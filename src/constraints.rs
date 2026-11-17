//! Constraint handlers with explicit feasibility ranking, penalty weights and epsilon schedule.
use crate::model::{Candidate,ConstraintMethod};

pub(crate) struct Ranker {
    pub method:Option<ConstraintMethod>,
    pub weight:f64,
    initial_weight:f64,
    epsilon_initial:Option<f64>,
    pub epsilon:f64,
    infeasible_streak:usize,
    feasible_streak:usize,
    reference:Option<f64>,
    previous_best:Option<(f64,f64)>,
}
fn percentile(sorted:&[f64],q:f64)->f64{
    let location=(sorted.len()-1) as f64*q/100.0;
    let lo=location.floor() as usize;
    let hi=(lo+1).min(sorted.len()-1);
    sorted[lo]+(sorted[hi]-sorted[lo])*(location-lo as f64)
}
impl Ranker {
    pub fn new(method:Option<ConstraintMethod>,weight:f64)->Self{
        Self {method,weight,initial_weight:weight,epsilon_initial:None,
            epsilon:0.0,infeasible_streak:0,feasible_streak:0,
            reference:None,previous_best:None}
    }
    pub fn update(&mut self,population:&[Candidate],generation:usize,limit:Option<usize>){
        if self.method.is_none(){return;}
        // Python's f_ref is frozen after its first successfully evaluated population.
        if self.reference.is_none(){
            let mut magnitudes:Vec<_>=population.iter().filter(|c|c.valid)
                .map(|c|c.objective.abs()).collect();
            if !magnitudes.is_empty(){
                magnitudes.sort_by(f64::total_cmp);
                let m=magnitudes.len()/2;
                let median=if magnitudes.len()%2==0{
                    0.5*magnitudes[m-1]+0.5*magnitudes[m]
                }else{magnitudes[m]};
                self.reference=Some(if median==0.0{1.0}else{median});
            }
        }
        if self.method==Some(ConstraintMethod::AdaptivePenalty){
            if let Some((_,violation))=self.previous_best {
                if violation==0.0{self.feasible_streak+=1;self.infeasible_streak=0;}
                else{self.infeasible_streak+=1;self.feasible_streak=0;}
                if self.infeasible_streak>=3{
                    self.weight=(self.weight*2.0).min(self.initial_weight*1e6);
                    self.infeasible_streak=0;
                    self.feasible_streak=0;
                }else if self.feasible_streak>=3{
                    self.weight=(self.weight/1.5).max(self.initial_weight/1e6);
                    self.infeasible_streak=0;
                    self.feasible_streak=0;
                }
            }
        }
        if self.method==Some(ConstraintMethod::Epsilon){
            if self.epsilon_initial.is_none(){
                let mut violations:Vec<_>=population.iter().filter(|c|c.valid)
                    .map(|c|c.violation).collect();
                if !violations.is_empty(){
                    violations.sort_by(f64::total_cmp);
                    self.epsilon_initial=Some(percentile(&violations,20.0));
                }
            }
            let progress=limit.map(|l|generation as f64/l as f64).unwrap_or(0.0);
            self.epsilon=if progress<0.5{
                self.epsilon_initial.unwrap_or(0.0)*(1.0-2.0*progress).powi(5)
            }else{0.0};
        }
        let best=population.iter().filter(|c|c.valid)
            .min_by(|a,b|self.compare(a,b));
        self.previous_best=best.map(|c|(c.objective,c.violation));
    }
    pub fn compare(&self,a:&Candidate,b:&Candidate)->std::cmp::Ordering{
        use std::cmp::Ordering;
        if !a.valid{return if b.valid{Ordering::Greater}else{Ordering::Equal};}
        if !b.valid{return Ordering::Less;}
        match self.method {
            None|Some(ConstraintMethod::Penalty)|Some(ConstraintMethod::AdaptivePenalty)=>
                self.raw_cost(a).total_cmp(&self.raw_cost(b)),
            Some(ConstraintMethod::FeasibilityRules)|Some(ConstraintMethod::Epsilon)=>{
                let af=a.violation<=self.epsilon;
                let bf=b.violation<=self.epsilon;
                match (af,bf){
                    (true,false)=>Ordering::Less,
                    (false,true)=>Ordering::Greater,
                    (true,true)=>a.objective.total_cmp(&b.objective),
                    (false,false)=>a.violation.total_cmp(&b.violation),
                }
            }
        }
    }
    fn raw_cost(&self,c:&Candidate)->f64{
        match self.method {
            None=>c.objective,
            _=>c.objective+self.weight*c.violation,
        }
    }
    pub fn score(&self,c:&Candidate)->f64{
        if !c.valid{return f64::MAX;}
        match self.method {
            None=>c.objective,
            Some(ConstraintMethod::Penalty)|Some(ConstraintMethod::AdaptivePenalty)=>
                self.raw_cost(c).clamp(-1e12,1e12),
            Some(ConstraintMethod::FeasibilityRules)|Some(ConstraintMethod::Epsilon)=>{
                if c.violation<=self.epsilon {
                    1.5+(c.objective/self.reference.unwrap_or(1.0)).atan()
                        /std::f64::consts::PI
                }else{2.0+c.violation/(1.0+c.violation)}
            }
        }
    }
}
#[cfg(test)]
mod tests{
    use super::*;
    fn candidate(objective:f64,violation:f64)->Candidate{
        let mut c=Candidate::new(vec![0.0]);
        c.valid=true;c.objective=objective;c.violation=violation;c
    }
    #[test]fn median_reference_stays_fixed(){
        let mut r=Ranker::new(Some(ConstraintMethod::FeasibilityRules),1000.0);
        r.update(&[candidate(2.0,0.0),candidate(4.0,0.0)],0,None);
        assert_eq!(r.reference,Some(3.0));
        r.update(&[candidate(50.0,0.0),candidate(80.0,0.0)],1,None);
        assert_eq!(r.reference,Some(3.0));
    }
    #[test]fn epsilon_percentile_interpolates(){
        let mut r=Ranker::new(Some(ConstraintMethod::Epsilon),1000.0);
        let values=[candidate(1.0,0.0),candidate(2.0,10.0)];
        r.update(&values,0,Some(10));
        assert_eq!(r.epsilon,2.0);
        r.update(&values,5,Some(10));
        assert_eq!(r.epsilon,0.0);
    }
    #[test]fn feasible_precedes_infeasible(){
        let r=Ranker::new(Some(ConstraintMethod::FeasibilityRules),1000.0);
        assert_eq!(r.compare(&candidate(10.0,0.0),&candidate(0.0,1.0)),std::cmp::Ordering::Less);
    }
}
