use gadapt::{ConstraintMethod, ExitCriterion, Fitness, GA, SolutionStatus, Termination};

#[test]
fn zero_budget_overshoot_and_invalid_results() {
    let mut count=0usize;
    let mut ga=GA::try_new(|_| {
        count+=1;
        Err("a deliberately invalid evaluation".to_owned())
    });
    ga.add(-1.0,1.0,None).unwrap();
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(11);
    ga.options.acceptable_cost=Some(0.0);
    let result=ga.execute().unwrap();
    assert_eq!(result.objective_evaluations,11);
    assert_eq!(result.invalid_objective_evaluations,11);
    assert_eq!(result.valid_objective_evaluations,0);
    assert_eq!(result.solution_status,SolutionStatus::NoValidEvaluation);
    assert_eq!(count,11);
}
#[test]
fn returns_genuinely_evaluated_incumbent(){
    let mut seen=Vec::new();
    let mut ga=GA::new(|x|{seen.push(x[0]);(x[0]-1.0).powi(2)});
    ga.add(-2.0,2.0,None).unwrap();
    ga.options.max_evaluations=Some(150);
    ga.options.reliability_mode=true;
    ga.options.acceptable_cost=Some(-1.0);
    let r=ga.execute().unwrap();
    assert_eq!(r.objective_evaluations,150);
    let found=r.result_values[0];
    assert!(seen.contains(&found));
    assert_eq!(r.best_objective,Some((found-1.0).powi(2)));
}
#[test]
fn simple_constrained_problem(){
    let mut ga=GA::constrained(|x| {
        ((x[0]-1.0).powi(2), (x[0]-0.5).max(0.0))
    });
    ga.add(-1.0,1.0,None).unwrap();
    ga.options.constraint_handling=Some(ConstraintMethod::FeasibilityRules);
    ga.options.max_evaluations=Some(400);
    ga.options.reliability_mode=true;
    ga.options.acceptable_cost=Some(0.5);
    let r=ga.execute().unwrap();
    assert!(r.objective_evaluations<=400);
    assert!(r.best_violation.unwrap_or(f64::INFINITY)>=0.0);
    if r.feasible {assert!(r.result_values[0]<=0.5);}
}
#[test]
fn discrete_grid_does_not_escape_bounds(){
    let mut ga=GA::new(|x|x[0]);
    ga.add(-1.0,1.0,Some(0.25)).unwrap();
    ga.options.max_evaluations=Some(100);
    let r=ga.execute().unwrap();
    assert!(r.result_values[0]>=-1.0 && r.result_values[0]<=1.0);
    let steps=(r.result_values[0]+1.0)/0.25;
    assert!((steps-steps.round()).abs()<1e-8);
}
#[test]
fn deterministic_runs_given_seed(){
    fn make()->gadapt::RunResult {
        let mut ga=GA::new(|x|x[0]*x[0]+x[1]*x[1]);
        ga.add(-2.0,2.0,None).unwrap();
        ga.add(-2.0,2.0,None).unwrap();
        ga.options.seed=109;
        ga.options.exit_criterion=ExitCriterion::Generations;
        ga.options.number_of_generations=Some(25);
        ga.execute().unwrap()
    }
    let a=make();let b=make();
    assert_eq!(a.result_values,b.result_values);
    assert_eq!(a.min_cost_per_generation,b.min_cost_per_generation);
}
#[test]
fn accepted_target_stops_before_spending_budget(){
    let mut ga=GA::new(|_|0.0);
    ga.add(-1.0,1.0,None).unwrap();
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(200);
    ga.options.acceptable_cost=Some(0.0);
    let r=ga.execute().unwrap();
    assert_eq!(r.objective_evaluations,1);
    assert_eq!(r.solution_status,SolutionStatus::Acceptable);
    assert_eq!(r.termination_reason,Termination::AcceptableTarget);
}
#[test]
fn callback_constraint_contract_checked(){
    let mut ga=GA::try_new(|_|Ok(Fitness::Constrained{objective:1.0,violation:-1.0}));
    ga.add(-1.0,1.0,None).unwrap();
    ga.options.constraint_handling=Some(ConstraintMethod::Penalty);
    ga.options.max_evaluations=Some(5);
    let r=ga.execute().unwrap();
    assert_eq!(r.invalid_objective_evaluations,5);
    assert_eq!(r.solution_status,SolutionStatus::NoValidEvaluation);
}
