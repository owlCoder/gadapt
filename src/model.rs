use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Variable {
    pub min: f64,
    pub max: f64,
    pub step: Option<f64>,
}
impl Variable {
    pub fn new(min: f64, max: f64, step: Option<f64>) -> Result<Self, GAError> {
        if !min.is_finite() || !max.is_finite() || min >= max {
            return Err(GAError::Configuration("variable bounds must be finite and min < max".into()));
        }
        if step.is_some_and(|s| !s.is_finite() || s <= 0.0) {
            return Err(GAError::Configuration("step must be finite and positive".into()));
        }
        Ok(Self { min, max, step })
    }
    pub fn contains(&self, x: f64) -> bool {
        if !x.is_finite() || x < self.min || x > self.max { return false; }
        match self.step {
            None => true,
            Some(s) => {
                let i = ((x-self.min)/s).round();
                if !i.is_finite() || i < 0.0 { return false; }
                let expected = self.min + i*s;
                (expected-x).abs() <= 8.0*f64::EPSILON * x.abs().max(expected.abs()).max(1.0)
            }
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Fitness {
    Scalar(f64),
    Constrained { objective: f64, violation: f64 },
}
impl Fitness {
    pub fn pair(self) -> (f64, f64) {
        match self {
            Self::Scalar(x) => (x, 0.0),
            Self::Constrained { objective, violation } => (objective, violation),
        }
    }
}
impl From<f64> for Fitness {
    fn from(value: f64) -> Self { Self::Scalar(value) }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ParentSelection { Roulette, Tournament(usize), Random, TopToBottom }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Sampling { Roulette, Tournament(usize), Random, TopToBottom }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Crossover { Blending, Uniform, Differential }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mutation { Random, Normal, Mixed, ExtremePointed }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DiversityMetric { LogRelative, Linear, AffineInvariant }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ExitCriterion { AverageCost, MinimumCost, RequestedCost, Generations }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ConstraintMethod { Penalty, AdaptivePenalty, FeasibilityRules, Epsilon }

#[derive(Clone, Debug)]
pub struct Options {
    pub population_size: usize,
    pub keep_elitism_percentage: f64,
    pub number_of_crossover_parents: Option<usize>,
    pub parent_selection: ParentSelection,
    pub crossover: Crossover,
    pub crossover_probability: f64,
    pub crossover_min_probability: f64,
    pub crossover_max_probability: f64,
    pub mutation: Mutation,
    pub population_mutation_fraction: f64,
    pub decision_variable_mutation_fraction: f64,
    pub must_mutate_for_same_parents: bool,
    pub ensure_unique_individuals: bool,
    pub columnar_diversity_metric: DiversityMetric,
    pub cost_diversity_metric: DiversityMetric,
    pub normal_mutation_min_std_dev: f64,
    pub normal_mutation_max_std_dev: f64,
    pub min_std_dev_decay_generations: Option<usize>,
    pub immigration_number: usize,
    pub adaptive_immigration_patience: Option<usize>,
    pub adaptive_immigration_percentage: f64,
    pub exit_criterion: ExitCriterion,
    pub max_attempt_no: usize,
    pub number_of_generations: Option<usize>,
    pub requested_cost: f64,
    pub timeout: Option<std::time::Duration>,
    pub constraint_handling: Option<ConstraintMethod>,
    pub constraint_penalty_weight: f64,
    pub reliability_mode: bool,
    pub max_evaluations: Option<usize>,
    pub acceptable_cost: Option<f64>,
    pub cache_evaluations: bool,
    pub stagnation_restart_patience: Option<usize>,
    pub seed: u64,
}
impl Default for Options {
    fn default() -> Self {
        Self {
            population_size: 32,
            keep_elitism_percentage: 50.0,
            number_of_crossover_parents: None,
            parent_selection: ParentSelection::Roulette,
            crossover: Crossover::Blending,
            crossover_probability: 0.5,
            crossover_min_probability: 0.5,
            crossover_max_probability: 1.0,
            mutation: Mutation::Mixed,
            population_mutation_fraction: 0.5,
            decision_variable_mutation_fraction: 0.2,
            must_mutate_for_same_parents: true,
            ensure_unique_individuals: false,
            columnar_diversity_metric: DiversityMetric::LogRelative,
            cost_diversity_metric: DiversityMetric::LogRelative,
            normal_mutation_min_std_dev: 0.01,
            normal_mutation_max_std_dev: 0.5,
            min_std_dev_decay_generations: None,
            immigration_number: 0,
            adaptive_immigration_patience: None,
            adaptive_immigration_percentage: 20.0,
            exit_criterion: ExitCriterion::AverageCost,
            max_attempt_no: 2,
            number_of_generations: None,
            requested_cost: f64::MAX,
            timeout: Some(std::time::Duration::from_secs(600)),
            constraint_handling: None,
            constraint_penalty_weight: 1000.0,
            reliability_mode: false,
            max_evaluations: None,
            acceptable_cost: None,
            cache_evaluations: false,
            stagnation_restart_patience: Some(5),
            seed: 42,
        }
    }
}
impl Options {
    pub(crate) fn validate(&self) -> Result<(), GAError> {
        if self.population_size < 4 { return Err(GAError::Configuration("population_size must be >= 4".into())); }
        if !(0.0..100.0).contains(&self.keep_elitism_percentage) {
            return Err(GAError::Configuration("keep_elitism_percentage must be in [0, 100)".into()));
        }
        if self.keep_count() < 2 {
            return Err(GAError::Configuration("elitism must retain at least two candidates".into()));
        }
        for (name, p) in [
            ("crossover_probability", self.crossover_probability),
            ("crossover_min_probability", self.crossover_min_probability),
            ("crossover_max_probability", self.crossover_max_probability),
            ("population_mutation_fraction", self.population_mutation_fraction),
            ("decision_variable_mutation_fraction", self.decision_variable_mutation_fraction),
        ] {
            if !p.is_finite() || !(0.0..=1.0).contains(&p) {
                return Err(GAError::Configuration(format!("{name} must be in [0, 1]")));
            }
        }
        if self.crossover_min_probability > self.crossover_max_probability {
            return Err(GAError::Configuration("crossover probability interval is reversed".into()));
        }
        if self.max_attempt_no == 0 { return Err(GAError::Configuration("max_attempt_no must be > 0".into())); }
        if self.max_evaluations == Some(0) { return Err(GAError::Configuration("evaluation budget must be > 0".into())); }
        if self.number_of_generations == Some(0) { return Err(GAError::Configuration("number_of_generations must be > 0".into())); }
        if self.immigration_number >= self.population_size - self.keep_count() {
            if self.immigration_number != 0 {
                return Err(GAError::Configuration("immigration_number must leave room for offspring".into()));
            }
        }
        if !self.constraint_penalty_weight.is_finite() || self.constraint_penalty_weight <= 0.0 {
            return Err(GAError::Configuration("constraint penalty weight must be positive".into()));
        }
        if !self.normal_mutation_min_std_dev.is_finite()
            || !self.normal_mutation_max_std_dev.is_finite()
            || self.normal_mutation_min_std_dev < 0.0
            || self.normal_mutation_max_std_dev < self.normal_mutation_min_std_dev {
            return Err(GAError::Configuration("invalid normal mutation deviations".into()));
        }
        if self.acceptable_cost.is_some_and(|x| !x.is_finite()) {
            return Err(GAError::Configuration("acceptable_cost must be finite".into()));
        }
        if self.reliability_mode && self.max_evaluations.is_none() {
            return Err(GAError::Configuration("reliability_mode requires max_evaluations".into()));
        }
        if self.reliability_mode && self.acceptable_cost.is_none() {
            return Err(GAError::Configuration("reliability_mode requires acceptable_cost".into()));
        }
        Ok(())
    }
    pub(crate) fn keep_count(&self) -> usize {
        ((self.population_size as f64 * self.keep_elitism_percentage / 100.0).round() as usize)
            .clamp(1, self.population_size - 1)
    }
}

#[derive(Clone, Debug)]
pub(crate) struct Candidate {
    pub values: Vec<f64>,
    pub objective: f64,
    pub violation: f64,
    pub score: f64,
    pub valid: bool,
    pub parent_distance: f64,
}
impl Candidate {
    pub fn new(values: Vec<f64>) -> Self {
        Self { values, objective: f64::NAN, violation: f64::INFINITY, score: f64::INFINITY,
            valid: false, parent_distance: 1.0 }
    }
    pub fn feasible(&self) -> bool { self.valid && self.violation == 0.0 }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SolutionStatus { Acceptable, Feasible, Infeasible, NoValidEvaluation }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Termination {
    AcceptableTarget,
    EvaluationBudget,
    GenerationLimit,
    Stagnation,
    RequestedCost,
    Timeout,
    NoValidEvaluations,
    NoProgress,
}
#[derive(Clone, Debug)]
pub struct RunResult {
    pub result_values: Vec<f64>,
    pub min_cost: Option<f64>,
    pub best_objective: Option<f64>,
    pub best_violation: Option<f64>,
    pub feasible: bool,
    pub acceptable: bool,
    pub solution_status: SolutionStatus,
    pub termination_reason: Termination,
    pub number_of_iterations: usize,
    pub min_cost_per_generation: Vec<f64>,
    pub objective_evaluations: usize,
    pub valid_objective_evaluations: usize,
    pub invalid_objective_evaluations: usize,
    pub cached_objective_requests: usize,
    pub reliability_restarts: usize,
    pub immigration_events: usize,
    pub seed: u64,
}

#[derive(Debug)]
pub enum GAError { Configuration(String) }
impl fmt::Display for GAError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self { Self::Configuration(x) => write!(f, "invalid GAdapt configuration: {x}") }
    }
}
impl std::error::Error for GAError {}
