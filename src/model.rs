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
    /// Number of canonical points in a safe, finite discrete grid.
    /// Like the Python implementation, tiny steps (>1e9 intervals)
    /// are treated as continuous rather than allocating an enormous grid.
    pub fn grid_len(&self) -> Option<usize> {
        let step=self.step?;
        let ratio=(self.max-self.min)/step;
        if !ratio.is_finite() || !(0.0..=1e9).contains(&ratio) {return None;}
        let nearest=ratio.round();
        let count=if (ratio-nearest).abs()<=1e-9f64.max(ratio.abs()*1e-9) {
            nearest
        }else{ratio.floor()};
        Some(count as usize+1)
    }
    /// The i-th grid point, if a finite safe grid is declared.
    pub fn grid_point(&self,i:usize)->Option<f64> {
        let n=self.grid_len()?;
        if i>=n {return None;}
        let raw=(self.min+i as f64*self.step?).min(self.max);
        if !raw.is_finite() {return None;}
        Some(raw)
    }
    pub fn contains(&self, x: f64) -> bool {
        if !x.is_finite() || x < self.min || x > self.max { return false; }
        let Some(n)=self.grid_len() else {return true;};
        let step=self.step.unwrap();
        let i=((x-self.min)/step).round();
        if !i.is_finite() || i<0.0 || i >= n as f64 {return false;}
        let expected=match self.grid_point(i as usize) {
            Some(x)=>x, None=>return false
        };
        // Scale tolerance with actual ULP and a fraction of grid step;
        // never allow a tolerance wider than the inter-point gap.
        let scale=x.abs().max(expected.abs()).max(step).max(f64::MIN_POSITIVE);
        let tolerance=(8.0*f64::EPSILON*scale).min(step/16.0);
        (expected-x).abs() <= tolerance
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
pub enum CompensatoryMode { Gated, Ungated, Permuted, Resample }
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
    pub max_mutated_candidates: Option<usize>,
    pub max_mutated_variables: Option<usize>,
    pub strict_mutation_decision_variable_limit: bool,
    pub compensatory_mutation: Option<CompensatoryMode>,
    pub mutation_focus_generations: Option<f64>,
    pub mutation_focus_exploration_probability: f64,
    pub must_mutate_for_same_parents: bool,
    pub ensure_unique_individuals: bool,
    /// If enabled, treat a fully discrete variable set as unique-by-default.
    /// Set false to disable auto uniqueness while preserving explicit `ensure_unique_individuals`.
    pub auto_unique_for_discrete: bool,
    pub columnar_diversity_metric: DiversityMetric,
    pub cost_diversity_metric: DiversityMetric,
    pub normal_mutation_min_std_dev: f64,
    pub normal_mutation_max_std_dev: f64,
    pub min_std_dev_decay_generations: Option<usize>,
    pub immigration_number: usize,
    pub adaptive_immigration_patience: Option<usize>,
    pub adaptive_immigration_percentage: f64,
    pub adaptive_immigration_diversity_threshold: f64,
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
    pub discrete_certification: bool,
    pub reliability_refresh_patience: Option<usize>,
    pub reliability_refresh_percentage: f64,
    pub reliability_restart_after_refreshes: Option<usize>,
    /// Legacy native-Rust alternate restart trigger. Disabled by default.
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
            max_mutated_candidates: None,
            max_mutated_variables: None,
            strict_mutation_decision_variable_limit: false,
            compensatory_mutation: None,
            mutation_focus_generations: None,
            mutation_focus_exploration_probability: 0.1,
            must_mutate_for_same_parents: true,
            ensure_unique_individuals: false,
            auto_unique_for_discrete: true,
            columnar_diversity_metric: DiversityMetric::LogRelative,
            cost_diversity_metric: DiversityMetric::LogRelative,
            normal_mutation_min_std_dev: 0.001,
            normal_mutation_max_std_dev: 0.6,
            min_std_dev_decay_generations: None,
            immigration_number: 0,
            adaptive_immigration_patience: None,
            adaptive_immigration_percentage: 20.0,
            adaptive_immigration_diversity_threshold: 0.25,
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
            discrete_certification: false,
            reliability_refresh_patience: None,
            reliability_refresh_percentage: 20.0,
            reliability_restart_after_refreshes: None,
            stagnation_restart_patience: None,
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
            ("mutation_focus_exploration_probability", self.mutation_focus_exploration_probability),
            ("adaptive_immigration_diversity_threshold", self.adaptive_immigration_diversity_threshold),
        ] {
            if !p.is_finite() || !(0.0..=1.0).contains(&p) {
                return Err(GAError::Configuration(format!("{name} must be in [0, 1]")));
            }
        }
        if self.crossover_min_probability > self.crossover_max_probability {
            return Err(GAError::Configuration("crossover probability interval is reversed".into()));
        }
        if self.max_attempt_no == 0 { return Err(GAError::Configuration("max_attempt_no must be > 0".into())); }
        if self.mutation_focus_generations.is_some_and(|x|!x.is_finite() || x<=0.0) {
            return Err(GAError::Configuration("mutation_focus_generations must be positive".into()));
        }
        if !(0.0..=100.0).contains(&self.adaptive_immigration_percentage)
            || !self.adaptive_immigration_percentage.is_finite() {
            return Err(GAError::Configuration("adaptive immigration percentage must be 0..100".into()));
        }
        if self.max_mutated_variables == Some(0) || self.max_mutated_candidates == Some(0) {
            return Err(GAError::Configuration("mutation count limits must be positive".into()));
        }
        if self.reliability_refresh_patience==Some(0) ||
            self.reliability_restart_after_refreshes==Some(0) {
            return Err(GAError::Configuration("reliability refresh/restart intervals must be positive".into()));
        }
        if !self.reliability_refresh_percentage.is_finite() ||
            !(0.0..=100.0).contains(&self.reliability_refresh_percentage) {
            return Err(GAError::Configuration("reliability refresh percentage must be 0..100".into()));
        }
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
    DiscreteSpaceExhausted,
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
    pub stagnation_refreshes: usize,
    pub discrete_search_applied: bool,
    pub discrete_space_size: Option<usize>,
    pub discrete_points_checked: Option<usize>,
    pub discrete_space_exhausted: Option<bool>,
    pub discrete_absence_certified: Option<bool>,
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
