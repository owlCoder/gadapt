//! Opt-in objective-reward UCB selection of mutation operators.
//! Offspring attribution is heuristic, not a causal effect of a single mutation.
use std::collections::VecDeque;
use crate::model::{Mutation,MutationOperatorPolicy,OperatorCreditSummary};
use crate::rng::Rng;

struct Arm {
    kind:Mutation,
    selections:usize,
    observations:usize,
    rewarded:usize,
    withheld:usize,
    history:VecDeque<f64>,
}
pub(crate) struct CreditBook {
    policy:MutationOperatorPolicy,
    arms:Vec<Arm>,
    window:usize,
}
impl CreditBook {
    pub(crate) fn new(policy:MutationOperatorPolicy,window:usize)->Self{
        Self {policy,window,arms:[Mutation::Random,Mutation::Normal]
            .into_iter().map(|kind|Arm{
                kind,selections:0,observations:0,rewarded:0,withheld:0,
                history:VecDeque::with_capacity(window.min(1024)),
            }).collect()}
    }
    pub(crate) fn choose(&mut self,rng:&mut Rng)->(usize,Mutation){
        let picked=match self.policy {
            MutationOperatorPolicy::Legacy|MutationOperatorPolicy::Uniform=>rng.usize(self.arms.len()),
            MutationOperatorPolicy::Ucb=>{
                let mut cold:Vec<_>=self.arms.iter().enumerate()
                    .filter(|(_,a)|a.selections==0).map(|(i,_)|i).collect();
                if !cold.is_empty(){cold.swap_remove(rng.usize(cold.len()))}
                else {
                    let total=self.arms.iter().map(|a|a.selections).sum::<usize>();
                    let mut top=f64::NEG_INFINITY;
                    let mut winners=Vec::new();
                    for (i,a) in self.arms.iter().enumerate(){
                        let mean=if a.history.is_empty(){0.0}else{
                            a.history.iter().sum::<f64>()/a.history.len() as f64};
                        let value=mean+(2.0*((total+1) as f64).ln()/a.selections as f64).sqrt();
                        if value>top{top=value;winners.clear();winners.push(i);}
                        else if value==top{winners.push(i);}
                    }
                    winners[rng.usize(winners.len())]
                }
            }
        };
        self.arms[picked].selections+=1;
        (picked,self.arms[picked].kind)
    }
    /// Each mutated variable attributes its latest operator, and the reward
    /// is split equally to avoid inflation when many genes are mutated.
    pub(crate) fn observe(&mut self,trace:&[(usize,usize)],
        actual_score:Option<f64>,reference_score:Option<f64>){
        if trace.is_empty(){return;}
        let reward=if let (Some(actual),Some(reference))=(actual_score,reference_score){
            if !actual.is_finite()||!reference.is_finite(){None}
            else{Some(((reference-actual)/(1.0+reference.abs())).clamp(0.0,1.0))}
        } else {None};
        for &(_,arm) in trace {
            let a=&mut self.arms[arm];
            if let Some(value)=reward {
                let share=value/trace.len() as f64;
                if a.history.len()==self.window{a.history.pop_front();}
                a.history.push_back(share);
                a.observations+=1;
                if share>0.0{a.rewarded+=1;}
            }else{a.withheld+=1;}
        }
    }
    pub(crate) fn summary(&self)->Vec<OperatorCreditSummary>{
        self.arms.iter().map(|a|OperatorCreditSummary{
            operator:a.kind,selections:a.selections,
            observations:a.observations,rewarded:a.rewarded,
            withheld:a.withheld,
            recent_mean_reward:if a.history.is_empty(){0.0}else{
                a.history.iter().sum::<f64>()/a.history.len() as f64
            }
        }).collect()
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]fn rewards_are_not_multiplied_by_gene_count(){
        let mut book=CreditBook::new(MutationOperatorPolicy::Uniform,5);
        let (a,_)=book.choose(&mut Rng::new(9));
        book.observe(&[(0,a),(1,a)],Some(0.0),Some(1.0));
        let s=book.summary()[a].clone();
        assert_eq!(s.observations,2);
        assert!((s.recent_mean_reward-0.25).abs()<1e-12);
    }
    #[test]fn unpaid_or_invalid_returns_are_withheld(){
        let mut book=CreditBook::new(MutationOperatorPolicy::Ucb,64);
        let (a,_)=book.choose(&mut Rng::new(17));
        book.observe(&[(0,a)],None,Some(1.0));
        let s=book.summary()[a].clone();
        assert_eq!(s.withheld,1);
        assert_eq!(s.observations,0);
    }
}
