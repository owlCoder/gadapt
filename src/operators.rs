use crate::model::{Candidate, Crossover, Mutation, Options, ParentSelection, Variable};
use crate::rng::Rng;
use crate::operator_credit::CreditBook;

pub(crate) fn sample(variable: &Variable, rng: &mut Rng) -> f64 {
    // Sampling by a uniform grid index avoids the half-weighted endpoints
    // created by sampling a continuous value and snapping to the nearest point.
    if let Some(n)=variable.grid_len(){
        return variable.grid_point(rng.usize(n)).unwrap_or(variable.min);
    }
    let u=rng.unit();
    (variable.min*(1.0-u)+variable.max*u).clamp(variable.min,variable.max)
}
pub(crate) fn snap(value:f64, variable:&Variable)->f64 {
    let x=value.clamp(variable.min,variable.max);
    let Some(n)=variable.grid_len() else{return x;};
    let step=variable.step.unwrap();
    let i=((x-variable.min)/step).round().clamp(0.0,(n-1) as f64) as usize;
    variable.grid_point(i).unwrap_or(x)
}
pub(crate) fn parent_index(elites:&[Candidate], method:ParentSelection,rng:&mut Rng)->usize {
    let n=elites.len();
    match method {
        ParentSelection::Random=>rng.usize(n),
        ParentSelection::TopToBottom=>{
            // A bias toward top-ranked candidates, without making lower ranks unreachable.
            let x=rng.unit();
            ((x*x*n as f64).floor() as usize).min(n-1)
        }
        ParentSelection::Tournament(k)=>{
            let mut best=rng.usize(n);
            for _ in 1..k.max(1) {
                let j=rng.usize(n);
                if j<best{best=j;}
            }
            best
        }
        ParentSelection::Roulette=>{
            let total=(n*(n+1)/2) as f64;
            let draw=rng.unit()*total;
            let mut acc=0.0;
            for idx in 0..n {
                acc+=(n-idx) as f64;
                if draw<acc{return idx;}
            }
            n-1
        }
    }
}
fn lerp(a:f64,b:f64,t:f64)->f64 {
    let v = a*(1.0-t)+b*t;
    if v.is_finite(){v}else{a*0.5+b*0.5}
}
fn reflect_snap(x:f64,v:&Variable)->f64{
    if !x.is_finite(){
        return snap(if x.is_sign_negative(){v.min}else{v.max},v);
    }
    let span=v.max-v.min;
    let period=2.0*span;
    if span.is_finite() && period.is_finite() {
        let offset=x-v.min;
        if offset.is_finite(){
            let folded=offset.rem_euclid(period);
            return snap(v.min+if folded<=span{folded}else{period-folded},v);
        }
    }
    snap(x.clamp(v.min,v.max),v)
}
/// Generate the first member of a pair. Probability and donor rules follow
/// the native-Python operators, but pair bookkeeping is not yet identical.
pub(crate) fn cross(
    first:&Candidate,second:&Candidate,_third:&Candidate,pool:&[Candidate],
    vars:&[Variable],options:&Options,prob:f64,rng:&mut Rng
)->Vec<f64>{
    if options.crossover==Crossover::Differential {
        // Python's differential operator chooses one shared F for the
        // whole genome and one Bernoulli trial for the entire parent pair.
        if !rng.bool(prob){return first.values.clone();}
        let eligible=pool.iter().filter(|c|
            !std::ptr::eq(*c,first) && !std::ptr::eq(*c,second)).count();
        let f=0.5+0.5*rng.unit();
        let donors=if eligible>=4 {
            let pick=|rng:&mut Rng,other:Option<usize>|->usize{
                loop{
                    let index=rng.usize(pool.len());
                    if other==Some(index) || std::ptr::eq(&pool[index],first)
                        || std::ptr::eq(&pool[index],second){continue;}
                    return index;
                }
            };
            let a=pick(rng,None);
            let b=pick(rng,Some(a));
            Some((a,b))
        }else{None};
        return vars.iter().enumerate().map(|(i,v)|{
            let a=first.values[i];
            let shifted=if let Some((left,right))=donors{
                let lhs=pool[left].values[i];let rhs=pool[right].values[i];
                a+f*(lhs*0.5-rhs*0.5)*2.0
            }else{
                lerp(a,second.values[i],f)
            };
            reflect_snap(shifted,v)
        }).collect();
    }
    // Legacy blending/uniform crossover retries until at least one
    // decision variable was crossed, raising the probability as needed.
    let mut p=prob;
    loop {
        let mut crossed=false;
        let values:Vec<_>=vars.iter().enumerate().map(|(i,var)|{
            let a=first.values[i];
            let b=second.values[i];
            if !rng.bool(p){return a;}
            crossed=true;
            let value=match options.crossover {
                Crossover::Uniform=>{
                    // Python first-offspring uniform uses father in two
                    // of three choices; mother in the remaining one.
                    if rng.usize(3)<2{b}else{a}
                }
                Crossover::Blending=>{
                    if let Some(n)=var.grid_len(){
                        let step=var.step.unwrap();
                        let left=((a-var.min)/step).round().clamp(0.0,(n-1) as f64) as usize;
                        let right=((b-var.min)/step).round().clamp(0.0,(n-1) as f64) as usize;
                        let low=left.min(right);let high=left.max(right);
                        var.grid_point(low+rng.usize(high-low+1)).unwrap_or(a)
                    }else{
                        // No extrapolation: Python blending uses alpha in [0,1].
                        lerp(a,b,rng.unit())
                    }
                }
                Crossover::Differential=>unreachable!(),
            };
            snap(if value.is_finite(){value}else{a},var)
        }).collect();
        if crossed{return values;}
        p=(p+0.1).min(1.0);
    }
}
pub(crate) fn mutate(
    values:&mut [f64], vars:&[Variable], options:&Options, columns:&[f64],
    force:bool, rng:&mut Rng, stagnant_generations:usize,
    mut credit:Option<&mut CreditBook>, trace:&mut Vec<(usize,usize)>
)->usize {
    let dims=values.len();
    if dims==0{return 0;}
    let avg=columns.iter().sum::<f64>()/dims as f64;
    let mut cap=options.max_mutated_variables.unwrap_or_else(||{
        (dims as f64*options.decision_variable_mutation_fraction).round() as usize
    }).clamp(1,dims);
    if !options.strict_mutation_decision_variable_limit {
        cap=cap.max((dims+4)/5).min(dims);
    }
    let focused=options.mutation_focus_generations.is_some()
        && !rng.bool(options.mutation_focus_exploration_probability);
    let focus=if focused {
        0.5f64.powf(stagnant_generations as f64/options.mutation_focus_generations.unwrap())
    }else{1.0};
    let mut desired=if force {1+rng.usize(cap)}else{
        (1.0+rng.unit()*(cap as f64)*(0.25+0.75*avg)).floor() as usize
    }.clamp(1,cap);
    desired=((desired as f64*focus).ceil() as usize).clamp(1,cap);
    let mut candidates:Vec<usize>=(0..dims).collect();
    let mut changed=0;
    for _ in 0..desired {
        if candidates.is_empty(){break;}
        // Two passes over candidate indices; avoid allocating a new weights
        // vector for every mutated gene.
        let sum=candidates.iter().map(|&i|(1.0-columns[i]).max(0.001)).sum::<f64>();
        let mut target=rng.unit()*sum;
        let mut pick=candidates.len()-1;
        for (pos,&index) in candidates.iter().enumerate(){
            target-=(1.0-columns[index]).max(0.001);
            if target<=0.0{pick=pos;break;}
        }
        let i=candidates.swap_remove(pick);
        let old=values[i];
        let var=&vars[i];
        let (selected,arm)=match options.mutation {
            Mutation::Mixed=>{
                if let Some(book)=credit.as_deref_mut(){
                    let (idx,op)=book.choose(rng);
                    (op,Some(idx))
                }else if rng.bool(0.5*focus){(Mutation::Random,None)}
                else{(Mutation::Normal,None)}
            },
            other=>(other,None),
        };
        if let Some(arm)=arm {
            if let Some(item)=trace.iter_mut().find(|(variable,_)|*variable==i){
                *item=(i,arm);
            }else{trace.push((i,arm));}
        }
        let next=match selected {
            Mutation::Random=>sample(var,rng),
            Mutation::ExtremePointed=>if rng.bool(0.5){var.min}else{var.max},
            Mutation::Normal | Mutation::Mixed => {
                let decay=options.min_std_dev_decay_generations.map(|n|{
                    0.1f64.powf(stagnant_generations as f64/n.max(1) as f64)
                }).unwrap_or(1.0);
                let step_floor=var.step.and_then(|s|{
                    let span=var.max-var.min;
                    if span.is_finite() && span>0.0 {Some(s/span)}else{None}
                }).unwrap_or(0.0);
                let min_std=(options.normal_mutation_min_std_dev*decay)
                    .max(1e-9).max(step_floor);
                let std=min_std+
                    (options.normal_mutation_max_std_dev-min_std)*columns[i].clamp(0.0,1.0);
                // Calculate in normalized space to avoid infinite ranges.
                let normalized=if (var.max-var.min).is_finite(){
                    (old-var.min)/(var.max-var.min)
                }else{
                    (old*0.5-var.min*0.5)/(var.max*0.5-var.min*0.5)
                };
                let u=(normalized+rng.normal()*std).clamp(0.0,1.0);
                let raw=lerp(var.min,var.max,u);
                snap(raw,var)
            }
        };
        if next!=old {values[i]=next; changed+=1;}
    }
    // An explicitly forced mutation must try to escape identical parents.
    if force && changed==0 {
        let i=rng.usize(dims);
        for _ in 0..8 {
            let candidate=sample(&vars[i],rng);
            if candidate!=values[i] {values[i]=candidate;changed+=1;break;}
        }
    }
    changed
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn uniform_respects_bounds(){
        let var=Variable::new(-1e308,1e308,None).unwrap();
        let mut rng=Rng::new(3);
        for _ in 0..1000 {let x=sample(&var,&mut rng);assert!(x>=var.min&&x<=var.max&&x.is_finite());}
    }
}

#[cfg(test)]
mod crossover_contract_tests{
    use super::*;
    #[test]fn blend_never_extrapolates_continuous_values(){
        let var=Variable::new(-1.0,1.0,None).unwrap();
        let a=Candidate::new(vec![-0.5]);
        let b=Candidate::new(vec![0.8]);
        let mut options=Options::default();
        options.crossover=Crossover::Blending;
        let mut rng=Rng::new(42);
        for _ in 0..500{
            let next=cross(&a,&b,&a,&[],&[var],&options,1.0,&mut rng);
            assert!(next[0]>=-0.5 && next[0]<=0.8);
        }
    }
    #[test]fn differential_rate_is_whole_candidate(){
        let var=Variable::new(-1.0,1.0,None).unwrap();
        let a=Candidate::new(vec![0.1,0.2]);
        let b=Candidate::new(vec![-0.1,-0.2]);
        let mut options=Options::default();
        options.crossover=Crossover::Differential;
        let out=cross(&a,&b,&a,&[],&[var,var],&options,0.0,&mut Rng::new(3));
        assert_eq!(out,a.values);
    }
}
