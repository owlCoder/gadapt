//! Rust-native equivalent of GAdapt's extensible operator-factory concept.
//! The default methods return None to request the built-in implementation.
//! Hooks never bypass validation or the objective-evaluation budget.
use crate::model::Variable;
use crate::rng::Rng;

/// A borrowed, read-only snapshot of an evaluated or invalid population candidate.
#[derive(Clone,Copy,Debug)]
pub struct CandidateView<'a> {
    pub values:&'a[f64],
    pub objective:Option<f64>,
    pub violation:Option<f64>,
    pub score:Option<f64>,
    pub parent_distance:f64,
}
/// Override one or more phases of the genetic algorithm in native Rust.
///
/// \`crossover\` must return exactly one value per declared decision variable.
/// \`mutate\` returns true if it has handled the mutation, false to use the
/// built-in mutator; neither method may call the optimization objective.
pub trait GeneticHooks {
    /// Population is ranked from best to worst; index must be in range.
    fn select_parent(&mut self,_ranked:&[CandidateView<'_>],_rng:&mut Rng)->Option<usize>{
        None
    }
    fn crossover(
        &mut self,_first:&[f64],_second:&[f64],_third:&[f64],
        _variables:&[Variable],_probability:f64,_rng:&mut Rng,
    )->Option<Vec<f64>>{None}
    fn mutate(
        &mut self,_values:&mut[f64],_variables:&[Variable],
        _column_diversity:&[f64],_rng:&mut Rng,
    )->bool{false}
}
