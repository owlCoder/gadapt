//! Verified physical-call-cost bandit for multi-scenario optimizer studies.
//! Pure accounting: never calls a physical solver and never treats unknowns as success.
use crate::model::GAError;
use crate::rng::Rng;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PhysicalStatus { VerifiedFeasible, MeasuredInfeasible, NumericallyUnknown }
#[derive(Clone, Debug)]
pub struct PhysicalObservation {
    pub status: PhysicalStatus,
    pub actual_calls: usize,
    pub scenario_ids: Vec<String>,
    pub measured_violations: Vec<f64>,
}
impl PhysicalObservation {
    pub fn validate(&self, scenario_count:usize)->Result<(),GAError>{
        if self.actual_calls==0 || self.actual_calls>scenario_count
            || self.scenario_ids.len()!=self.actual_calls
            || self.measured_violations.len()!=self.actual_calls {
            return Err(GAError::Configuration("physical feedback count or length mismatch".into()));
        }
        let mut distinct=std::collections::HashSet::new();
        if self.scenario_ids.iter().any(|s|s.is_empty()||!distinct.insert(s.as_str())){
            return Err(GAError::Configuration("scenario identifiers must be nonempty and distinct".into()));
        }
        if self.measured_violations.iter().any(|x|!x.is_finite()||*x<0.0){
            return Err(GAError::Configuration("physical violations must be finite and nonnegative".into()));
        }
        match self.status {
            PhysicalStatus::VerifiedFeasible => {
                if self.actual_calls!=scenario_count ||
                    self.measured_violations.iter().any(|x|*x!=0.0) {
                    return Err(GAError::Configuration("verified feasibility requires every scenario with zero violation".into()));
                }
            }
            PhysicalStatus::MeasuredInfeasible=>{
                if self.measured_violations.iter().all(|x|*x==0.0){
                    return Err(GAError::Configuration("measured infeasibility needs a positive physical violation".into()));
                }
            }
            PhysicalStatus::NumericallyUnknown=>{}
        }
        Ok(())
    }
}
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct PhysicalArm {
    pub trials:u64,
    pub verified_successes:u64,
    pub unknown:u64,
    pub actual_calls:u64,
}
#[derive(Clone, Debug)]
pub struct PhysicalArmSummary {
    pub arm:usize,
    pub stats:PhysicalArm,
    pub certified_success_per_true_call:Option<f64>,
    pub optimistic_score:Option<f64>,
}
/// Optimistic verified-feasible successes per *paid* true scenario call.
///
/// These are heuristic arm-selection bounds for a nonstationary optimizer,
/// not a proof of superior search quality or a certificate of feasibility.
pub struct VerifiedCallRateBandit {
    scenario_count:usize,
    delta:f64,
    arms:Vec<PhysicalArm>,
}
impl VerifiedCallRateBandit {
    pub fn new(scenario_count:usize,delta:f64)->Result<Self,GAError>{
        if scenario_count<2 || !(0.0..1.0).contains(&delta) || delta==0.0 ||
            !delta.is_finite(){
            return Err(GAError::Configuration("scenario count must be >=2 and 0<delta<1".into()));
        }
        Ok(Self{scenario_count,delta,arms:Vec::new()})
    }
    pub fn add_operator(&mut self)->usize{
        let arm=self.arms.len();
        self.arms.push(PhysicalArm::default());
        arm
    }
    pub fn observe(&mut self,arm:usize,feedback:&PhysicalObservation)->Result<(),GAError>{
        feedback.validate(self.scenario_count)?;
        let stats=self.arms.get_mut(arm).ok_or_else(||GAError::Configuration("unknown physical operator arm".into()))?;
        let calls=feedback.actual_calls as u64;
        let trials=stats.trials.checked_add(1);
        let total_calls=stats.actual_calls.checked_add(calls);
        if trials.is_none()||total_calls.is_none(){
            return Err(GAError::Configuration("physical statistics overflow".into()));
        }
        stats.trials=trials.unwrap();
        stats.actual_calls=total_calls.unwrap();
        match feedback.status {
            PhysicalStatus::VerifiedFeasible=>stats.verified_successes+=1,
            PhysicalStatus::NumericallyUnknown=>stats.unknown+=1,
            PhysicalStatus::MeasuredInfeasible=>{}
        }
        Ok(())
    }
    pub fn arm(&self,index:usize)->Option<PhysicalArm>{self.arms.get(index).copied()}
    pub fn optimistic_score(&self,index:usize)->Option<f64>{
        let a=self.arms.get(index)?;
        if a.trials==0{return Some(f64::INFINITY);}
        let n=a.trials as f64;
        let t=self.arms.iter().map(|a|a.trials as f64).sum::<f64>();
        let k=self.arms.len() as f64;
        let radius=( (8.0*k*(t+1.0).powi(2)/self.delta).ln()/(2.0*n)).sqrt();
        let upper=((a.verified_successes+a.unknown) as f64/n+radius).min(1.0);
        let lower=((a.actual_calls as f64/n)-(self.scenario_count as f64-1.0)*radius).max(1.0);
        Some(upper/lower)
    }
    pub fn choose(&self,rng:&mut Rng)->Option<usize>{
        if self.arms.is_empty(){return None;}
        let cold:Vec<usize>=self.arms.iter().enumerate().filter(|(_,a)|a.trials==0)
            .map(|(i,_)|i).collect();
        if !cold.is_empty(){return Some(cold[rng.usize(cold.len())]);}
        let mut best=f64::NEG_INFINITY;
        let mut winners=Vec::new();
        for i in 0..self.arms.len(){
            let score=self.optimistic_score(i)?;
            if score>best{best=score;winners.clear();winners.push(i);}
            else if score==best{winners.push(i);}
        }
        Some(winners[rng.usize(winners.len())])
    }
    pub fn summary(&self)->Vec<PhysicalArmSummary>{
        self.arms.iter().enumerate().map(|(i,a)|PhysicalArmSummary{
            arm:i,stats:*a,
            certified_success_per_true_call:if a.actual_calls==0{None}
                else{Some(a.verified_successes as f64/a.actual_calls as f64)},
            optimistic_score:if a.trials==0{None}else{self.optimistic_score(i)},
        }).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn event(status:PhysicalStatus,n:usize,values:&[f64])->PhysicalObservation {
        PhysicalObservation {
            status,actual_calls:n,
            scenario_ids:(0..n).map(|i|format!("case{i}")).collect(),
            measured_violations:values.to_vec(),
        }
    }
    #[test]fn no_false_verified_success(){
        let mut bandit=VerifiedCallRateBandit::new(3,0.05).unwrap();
        let i=bandit.add_operator();
        bandit.observe(i,&event(PhysicalStatus::NumericallyUnknown,1,&[0.0])).unwrap();
        bandit.observe(i,&event(PhysicalStatus::MeasuredInfeasible,2,&[0.0,2.0])).unwrap();
        let a=bandit.arm(i).unwrap();
        assert_eq!(a.actual_calls,3);
        assert_eq!(a.verified_successes,0);
        assert_eq!(a.unknown,1);
        assert_eq!(bandit.summary()[0].certified_success_per_true_call,Some(0.0));
        assert!(bandit.observe(i,&event(PhysicalStatus::VerifiedFeasible,2,&[0.0,0.0])).is_err());
        assert_eq!(bandit.arm(i).unwrap(),a);
        bandit.observe(i,&event(PhysicalStatus::VerifiedFeasible,3,&[0.0,0.0,0.0])).unwrap();
        assert_eq!(bandit.summary()[0].certified_success_per_true_call,Some(1.0/6.0));
    }
    #[test]fn cold_arms_get_a_chance(){
        let mut bandit=VerifiedCallRateBandit::new(3,0.05).unwrap();
        let a=bandit.add_operator();let b=bandit.add_operator();
        bandit.observe(a,&event(PhysicalStatus::MeasuredInfeasible,1,&[1.0])).unwrap();
        assert_eq!(bandit.choose(&mut Rng::new(5)),Some(b));
    }
    #[test]fn invalid_feedback_is_rejected(){
        let mut b=VerifiedCallRateBandit::new(3,0.05).unwrap();
        let a=b.add_operator();
        let mut event=event(PhysicalStatus::VerifiedFeasible,3,&[0.0,0.0,0.0]);
        event.scenario_ids[1]=event.scenario_ids[0].clone();
        assert!(b.observe(a,&event).is_err());
    }
}
