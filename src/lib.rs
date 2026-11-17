//! GAdapt: a native Rust self-adaptive genetic algorithm.
//!
//! # Example
//!
//! \`\`\`
//! use gadapt::{GA, Options};
//! let mut ga = GA::new(|xs: &[f64]| (xs[0] - 2.0).powi(2));
//! ga.add(-5.0, 5.0, None).unwrap();
//! ga.options.max_evaluations = Some(1000);
//! ga.options.acceptable_cost = Some(0.01);
//! let result = ga.execute().unwrap();
//! assert!(result.best_objective.is_some());
//! assert!(result.objective_evaluations <= 1000);
//! \`\`\`

mod constraints;
mod diversity;
mod engine;
mod model;
mod operators;
mod rng;

pub use model::{
    ConstraintMethod, Crossover, DiversityMetric, ExitCriterion, Fitness, GAError, Mutation,
    Options, ParentSelection, RunResult, Sampling, SolutionStatus, Termination, Variable,
};
pub use engine::GA;
