use crate::model::{Candidate, ConstraintMethod};

pub(crate) struct Ranker {
    pub method: Option<ConstraintMethod>,
    pub weight: f64,
    initial_weight: f64,
    epsilon_initial: Option<f64>,
    pub epsilon: f64,
    infeasible_streak: usize,
    feasible_streak: usize,
    reference: f64,
}
impl Ranker {
    pub fn new(method: Option<ConstraintMethod>, weight: f64) -> Self {
        Self { method, weight, initial_weight: weight, epsilon_initial: None,
            epsilon: 0.0, infeasible_streak: 0, feasible_streak: 0, reference: 1.0 }
    }
    pub fn update(&mut self, population: &[Candidate], generation: usize, limit: Option<usize>) {
        if self.method.is_none() { return; }
        let mut vals: Vec<f64> = population.iter().filter(|c|c.valid).map(|c| c.objective.abs()).collect();
        if !vals.is_empty() {
            vals.sort_by(f64::total_cmp);
            self.reference = vals[vals.len()/2].max(1e-300);
        }
        if self.method == Some(ConstraintMethod::AdaptivePenalty) {
            let best = population.iter().filter(|c| c.valid).min_by(|a,b| self.compare(a,b));
            if let Some(c) = best {
                if c.feasible() { self.feasible_streak+=1; self.infeasible_streak=0; }
                else { self.infeasible_streak+=1; self.feasible_streak=0; }
                if self.infeasible_streak>=3 {
                    self.weight = (self.weight*2.0).min(self.initial_weight*1e6);
                    self.infeasible_streak=0;
                } else if self.feasible_streak>=3 {
                    self.weight = (self.weight/1.5).max(self.initial_weight/1e6);
                    self.feasible_streak=0;
                }
            }
        }
        if self.method == Some(ConstraintMethod::Epsilon) {
            if self.epsilon_initial.is_none() {
                let mut v:Vec<_>=population.iter().filter(|c|c.valid).map(|c| c.violation).collect();
                v.sort_by(f64::total_cmp);
                self.epsilon_initial=Some(if v.is_empty(){0.0}else{v[v.len()/5]});
            }
            let progress=limit.map(|l|generation as f64/l as f64).unwrap_or(0.0);
            self.epsilon=if progress < 0.5 { self.epsilon_initial.unwrap_or(0.0)*(1.0-2.0*progress).powi(5) }else{0.0};
        }
    }
    pub fn compare(&self, a: &Candidate, b: &Candidate) -> std::cmp::Ordering {
        if !a.valid { return if b.valid {std::cmp::Ordering::Greater} else {std::cmp::Ordering::Equal}; }
        if !b.valid { return std::cmp::Ordering::Less; }
        match self.method {
            None | Some(ConstraintMethod::Penalty) | Some(ConstraintMethod::AdaptivePenalty) => {
                self.raw_cost(a).total_cmp(&self.raw_cost(b))
            }
            Some(ConstraintMethod::FeasibilityRules) | Some(ConstraintMethod::Epsilon) => {
                let af = a.violation <= self.epsilon;
                let bf = b.violation <= self.epsilon;
                match (af, bf) {
                    (true, false)=>std::cmp::Ordering::Less,
                    (false, true)=>std::cmp::Ordering::Greater,
                    (true,true)=>a.objective.total_cmp(&b.objective),
                    (false,false)=>a.violation.total_cmp(&b.violation),
                }
            }
        }
    }
    fn raw_cost(&self,c:&Candidate)->f64 {
        match self.method {
            None => c.objective,
            _ => c.objective + self.weight*c.violation
        }
    }
    pub fn score(&self,c:&Candidate)->f64 {
        if !c.valid { return f64::MAX; }
        match self.method {
            None => c.objective,
            Some(ConstraintMethod::Penalty)|Some(ConstraintMethod::AdaptivePenalty) =>
                self.raw_cost(c).clamp(-1e12,1e12),
            Some(ConstraintMethod::FeasibilityRules)|Some(ConstraintMethod::Epsilon) =>
                if c.violation <= self.epsilon {
                    1.5 + (c.objective/self.reference).atan()/std::f64::consts::PI
                }else{2.0+c.violation/(1.0+c.violation)},
        }
    }
}
