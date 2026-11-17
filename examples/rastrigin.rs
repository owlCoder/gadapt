use std::f64::consts::PI;
use gadapt::{GA, ExitCriterion};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut ga=GA::new(|x: &[f64]| {
        10.0*x.len() as f64
            +x.iter().map(|v|v*v-10.0*(2.0*PI*v).cos()).sum::<f64>()
    });
    for _ in 0..10 {ga.add(-5.12,5.12,None)?;}
    ga.options.seed=20261117;
    ga.options.exit_criterion=ExitCriterion::Generations;
    ga.options.number_of_generations=Some(100);
    ga.options.max_evaluations=Some(4096);
    let result=ga.execute()?;
    println!("best objective: {:?}",result.best_objective);
    println!("best parameters: {:?}",result.result_values);
    println!("evaluations: {}",result.objective_evaluations);
    println!("status: {:?}",result.solution_status);
    Ok(())
}
