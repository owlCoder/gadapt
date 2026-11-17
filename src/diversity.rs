//! Allocation-free diversity estimators, robust to finite extreme magnitudes.
use crate::model::{Candidate,DiversityMetric,Variable};

#[derive(Default)]
struct Moments {
    count:usize,
    mean:f64,
    m2:f64,
    min:f64,
    max:f64,
}
impl Moments {
    fn new()->Self{Self{count:0,mean:0.0,m2:0.0,min:f64::INFINITY,max:f64::NEG_INFINITY}}
    fn push(&mut self,x:f64){
        if !x.is_finite(){return;}
        self.min=self.min.min(x);
        self.max=self.max.max(x);
        self.count+=1;
        let delta=x-self.mean;
        self.mean+=delta/self.count as f64;
        self.m2+=delta*(x-self.mean);
    }
    fn deviation(&self)->f64{
        if self.count<2 || self.min==self.max {return 0.0;}
        let sample=(self.m2/(self.count-1) as f64).max(0.0).sqrt();
        // Preserve distinguishable-but-subnormal input signals.
        if sample==0.0 {f64::from_bits(1)} else {sample}
    }
}
fn scale_linear(x:f64,min:f64,max:f64)->f64{
    let span=max-min;
    if span.is_finite(){((x-min)/span).clamp(0.0,1.0)}
    else{((x*0.5-min*0.5)/(max*0.5-min*0.5)).clamp(0.0,1.0)}
}
fn log_from_lower(x:f64,low:f64)->f64{
    let gap=x-low;
    if gap.is_finite(){gap.max(0.0).ln_1p()}
    else{(-low).ln()+(x/-low).ln_1p()}
}
fn generic_spread<I>(values:I,metric:DiversityMetric)->f64
where I:Iterator<Item=f64>+Clone {
    let (mut min,mut max)=(f64::INFINITY,f64::NEG_INFINITY);
    for x in values.clone(){
        if x.is_finite(){min=min.min(x);max=max.max(x);}
    }
    if !min.is_finite() || min==max{return 0.0;}
    let mut stats=Moments::new();
    for x in values{
        if !x.is_finite(){continue;}
        let transformed=match metric {
            DiversityMetric::LogRelative=>log_from_lower(x,min),
            DiversityMetric::Linear | DiversityMetric::AffineInvariant=>scale_linear(x,min,max),
        };
        stats.push(transformed);
    }
    stats.deviation()
}
pub(crate) fn spread(values:&[f64],metric:DiversityMetric)->f64{
    generic_spread(values.iter().copied(),metric)
}
pub(crate) fn relative(current:f64,baseline:&mut Option<f64>)->f64{
    if !current.is_finite() || current<=0.0{return 0.0;}
    match baseline {
        None=>{*baseline=Some(current);1.0}
        Some(b) if *b>0.0=>(current/ *b).clamp(0.0,1.0),
        Some(_)=>1.0,
    }
}
pub(crate) fn cost(population:&[Candidate],metric:DiversityMetric,
    baseline:&mut Option<f64>)->f64{
    let values=population.iter().filter(|c|c.valid && c.score.is_finite()).map(|c|c.score);
    relative(generic_spread(values,metric),baseline)
}
pub(crate) fn columns(population:&[Candidate],vars:&[Variable],metric:DiversityMetric,
    baselines:&mut[Option<f64>])->Vec<f64>{
    let mut result=Vec::with_capacity(vars.len());
    for (i,variable) in vars.iter().enumerate(){
        let mut stats=Moments::new();
        for candidate in population {
            if !candidate.valid{continue;}
            let v=candidate.values[i];
            let scaled=match metric {
                DiversityMetric::LogRelative=>log_from_lower(v,variable.min),
                DiversityMetric::Linear | DiversityMetric::AffineInvariant=>
                    scale_linear(v,variable.min,variable.max),
            };
            stats.push(scaled);
        }
        result.push(relative(stats.deviation(),&mut baselines[i]));
    }
    result
}
pub(crate) fn parent_distance(a:&[f64],b:&[f64],vars:&[Variable])->f64{
    if vars.is_empty(){return 0.0;}
    let mut sum=0.0;
    for ((&x,&y),v) in a.iter().zip(b).zip(vars){
        let span=v.max-v.min;
        let delta=if span.is_finite(){(x-y)/span}
            else{(x*0.5-y*0.5)/(v.max*0.5-v.min*0.5)};
        sum+=delta.abs().min(1.0);
    }
    (sum/vars.len() as f64).clamp(0.0,1.0)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]fn constant_population_has_no_diversity(){
        assert_eq!(spread(&[1.0,1.0],DiversityMetric::LogRelative),0.0);
    }
    #[test]fn extremes_remain_finite(){
        let v=spread(&[-1e308,1e308],DiversityMetric::AffineInvariant);
        assert!(v.is_finite() && v>0.0);
        let v=spread(&[-1e308,1e308],DiversityMetric::LogRelative);
        assert!(v.is_finite() && v>0.0);
    }
    #[test]fn input_is_not_mutated(){
        let values=[0.0,10.0,-10.0];
        assert!(spread(&values,DiversityMetric::Linear)>0.0);
        assert_eq!(values,[0.0,10.0,-10.0]);
    }
    #[test]fn subnormal_values_do_not_create_false_ties(){
        let z=f64::from_bits(1);
        assert!(spread(&[0.0,z,z,0.0],DiversityMetric::LogRelative)>0.0);
    }
    #[test]fn columnar_extreme_span_survives(){
        let var=Variable::new(-1e308,1e308,None).unwrap();
        let mut a=Candidate::new(vec![-1e308]);a.valid=true;
        let mut b=Candidate::new(vec![1e308]);b.valid=true;
        let mut baselines=vec![None];
        let result=columns(&[a,b],&[var],DiversityMetric::Linear,&mut baselines);
        assert_eq!(result,vec![1.0]);
    }
}
