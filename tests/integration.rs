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
    drop(ga);
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
    drop(ga);
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

#[test]
fn exhaustive_discrete_absence_only_after_valid_complete_coverage(){
    let mut ga=GA::new(|_|1.0);
    ga.add(-1.0,1.0,Some(1.0)).unwrap();
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(3);
    ga.options.acceptable_cost=Some(0.0);
    ga.options.discrete_certification=true;
    let r=ga.execute().unwrap();
    assert!(r.discrete_search_applied);
    assert_eq!(r.discrete_space_size,Some(3));
    assert_eq!(r.discrete_points_checked,Some(3));
    assert_eq!(r.discrete_absence_certified,Some(true));
    assert_eq!(r.termination_reason,Termination::DiscreteSpaceExhausted);
}
#[test]
fn invalid_discrete_response_never_certifies_absence(){
    let mut ga=GA::try_new(|_|Err("invalid".into()));
    ga.add(0.0,1.0,Some(1.0)).unwrap();
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(2);
    ga.options.acceptable_cost=Some(0.0);
    ga.options.discrete_certification=true;
    let r=ga.execute().unwrap();
    assert_eq!(r.discrete_space_exhausted,Some(true));
    assert_eq!(r.discrete_absence_certified,Some(false));
}

#[test]
fn grid_sampling_covers_all_indices_including_endpoints(){
    use std::collections::HashSet;
    let mut seen=HashSet::new();
    let mut ga=GA::new(|xs| {
        seen.insert(xs[0].to_bits());
        xs[0]
    });
    ga.add(0.0,1.0,Some(0.25)).unwrap();
    ga.options.max_evaluations=Some(250);
    ga.options.exit_criterion=ExitCriterion::Generations;
    ga.options.number_of_generations=Some(20);
    let r=ga.execute().unwrap();
    assert!(r.objective_evaluations<=250);
    drop(ga);
    assert!(seen.contains(&0.0f64.to_bits()));
    assert!(seen.contains(&1.0f64.to_bits()));
    assert!(seen.iter().all(|&bits| {
        let x=f64::from_bits(bits);
        let grid=(x/0.25).round();
        (x/0.25-grid).abs()<1e-9
    }));
}
#[test]
fn tiny_grid_step_does_not_accept_offgrid_values(){
    let v=gadapt::Variable::new(0.0,1e-10,Some(1e-15)).unwrap();
    assert!(v.contains(1e-15));
    assert!(!v.contains(5e-16));
}
#[test]
fn focus_and_mutation_caps_are_opt_in_and_budgeted(){
    let mut ga=GA::new(|xs| xs.iter().map(|x|x*x).sum());
    for _ in 0..7 {ga.add(-5.0,5.0,None).unwrap();}
    ga.options.mutation_focus_generations=Some(2.5);
    ga.options.max_mutated_variables=Some(1);
    ga.options.strict_mutation_decision_variable_limit=true;
    ga.options.max_evaluations=Some(100);
    ga.options.reliability_mode=true;
    ga.options.acceptable_cost=Some(-1.0);
    let r=ga.execute().unwrap();
    assert_eq!(r.objective_evaluations,100);
    assert!(r.best_objective.is_some());
}

#[test]
fn compensatory_mutation_preserves_hard_budget(){
    let mut ga=GA::new(|xs|xs.iter().sum());
    ga.add(-1.0,1.0,None).unwrap();
    ga.add(-1.0,1.0,None).unwrap();
    ga.options.compensatory_mutation=Some(gadapt::CompensatoryMode::Gated);
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(81);
    ga.options.acceptable_cost=Some(-100.0);
    let r=ga.execute().unwrap();
    assert_eq!(r.objective_evaluations,81);
}

#[test]
fn decimal_rounding_ambiguity_never_certifies_absence(){
    let mut ga=GA::new(|_|1.0);
    ga.add(0.15,0.45,Some(0.1)).unwrap();
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(5);
    ga.options.acceptable_cost=Some(0.0);
    ga.options.discrete_certification=true;
    let result=ga.execute().unwrap();
    assert!(!result.discrete_search_applied);
    assert_eq!(result.discrete_absence_certified,None);
}

#[test]
fn verified_stagnation_refresh_and_restarts_preserve_budget(){
    let mut ga=GA::new(|_|1.0);
    ga.add(-1.0,1.0,None).unwrap();
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(240);
    ga.options.acceptable_cost=Some(0.0);
    ga.options.reliability_refresh_patience=Some(2);
    ga.options.reliability_refresh_percentage=30.0;
    ga.options.reliability_restart_after_refreshes=Some(2);
    let r=ga.execute().unwrap();
    assert_eq!(r.objective_evaluations,240);
    assert!(r.stagnation_refreshes>0);
    assert!(r.reliability_restarts>0);
    assert_eq!(r.best_objective,Some(1.0));
}

struct FixedCrossover;
impl gadapt::GeneticHooks for FixedCrossover {
    fn crossover(
        &mut self,_a:&[f64],_b:&[f64],_c:&[f64],
        _vars:&[gadapt::Variable],_p:f64,_rng:&mut gadapt::Rng
    )->Option<Vec<f64>>{
        Some(vec![0.25])
    }
}
#[test]
fn custom_rust_operator_respects_budget_and_exact_target(){
    let mut ga=GA::new(|x|(x[0]-0.25).powi(2));
    ga.add(-1.0,1.0,None).unwrap();
    ga.set_hooks(FixedCrossover);
    ga.options.must_mutate_for_same_parents=false;
    ga.options.population_mutation_fraction=0.0;
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(200);
    ga.options.acceptable_cost=Some(0.0);
    let r=ga.execute().unwrap();
    assert!(r.objective_evaluations<=200);
    assert_eq!(r.solution_status,SolutionStatus::Acceptable);
    assert_eq!(r.result_values,vec![0.25]);
}

#[test]
fn objective_ucb_operator_credit_is_budgeted_and_reported(){
    let mut ga=GA::new(|x|x.iter().map(|v|v*v).sum());
    for _ in 0..5{ga.add(-3.0,3.0,None).unwrap();}
    ga.options.mutation_operator_policy=gadapt::MutationOperatorPolicy::Ucb;
    ga.options.mutation_credit_window=10;
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(180);
    ga.options.acceptable_cost=Some(-1.0);
    let r=ga.execute().unwrap();
    let stats=r.operator_credit_summary.unwrap();
    assert_eq!(r.objective_evaluations,180);
    assert_eq!(stats.len(),2);
    assert!(stats.iter().map(|s|s.selections).sum::<usize>()>0);
    assert!(stats.iter().map(|s|s.observations).sum::<usize>()>0);
}

#[test]
fn scalar_fitness_cannot_falsely_certify_constrained_feasibility(){
    let mut ga=GA::new(|_|0.0);
    ga.add(-1.0,1.0,None).unwrap();
    ga.options.constraint_handling=Some(ConstraintMethod::FeasibilityRules);
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(13);
    ga.options.acceptable_cost=Some(0.0);
    let r=ga.execute().unwrap();
    assert_eq!(r.valid_objective_evaluations,0);
    assert_eq!(r.invalid_objective_evaluations,13);
    assert!(!r.feasible);
    assert_eq!(r.solution_status,SolutionStatus::NoValidEvaluation);
}
#[test]
fn epsilon_constraint_ranker_needs_generation_limit(){
    let mut ga=GA::constrained(|_|(1.0,1.0));
    ga.add(0.0,1.0,None).unwrap();
    ga.options.constraint_handling=Some(ConstraintMethod::Epsilon);
    assert!(ga.execute().is_err());
}

#[test]
fn opt_in_validation_probes_charge_actual_budget(){
    use std::cell::Cell;
    let called=Cell::new(0usize);
    let mut ga=GA::new(|x|{
        called.set(called.get()+1);
        x[0]*x[0]
    });
    ga.add(-1.0,1.0,None).unwrap();
    ga.options.probe_cost_function=true;
    ga.options.reliability_mode=true;
    ga.options.max_evaluations=Some(2);
    ga.options.acceptable_cost=Some(-1.0);
    let r=ga.execute().unwrap();
    assert_eq!(r.objective_evaluations,2);
    assert_eq!(r.valid_objective_evaluations,2);
    drop(ga);
    assert_eq!(called.get(),2);
}
#[test]
fn native_exit_callback_stops_between_generations(){
    use std::cell::Cell;
    let times=Cell::new(0usize);
    let mut ga=GA::new(|x|x[0]*x[0]);
    ga.add(-1.0,1.0,None).unwrap();
    ga.set_exit_callback(||{times.set(times.get()+1);times.get()>1});
    ga.options.exit_criterion=ExitCriterion::Generations;
    ga.options.number_of_generations=Some(200);
    let r=ga.execute().unwrap();
    assert_eq!(r.termination_reason,Termination::ExternalStop);
    drop(ga);
    assert!(times.get()>=2);
}

#[test]
fn legacy_crossover_probability_is_fixed_by_default(){
    let defaults=gadapt::Options::default();
    assert_eq!(defaults.crossover_probability_policy,
        gadapt::CrossoverProbabilityPolicy::Fixed);
    assert_eq!(defaults.crossover_probability,0.5);
}
#[test]
fn opt_in_crossover_probability_modes_respect_budget(){
    for mode in [
        gadapt::CrossoverProbabilityPolicy::CostDiversity,
        gadapt::CrossoverProbabilityPolicy::ColumnarDiversity,
        gadapt::CrossoverProbabilityPolicy::Mixed,
    ] {
        let mut ga=GA::new(|x|x[0]*x[0]+x[1]*x[1]);
        ga.add(-2.0,2.0,None).unwrap();
        ga.add(-2.0,2.0,None).unwrap();
        ga.options.crossover_probability_policy=mode;
        ga.options.reliability_mode=true;
        ga.options.max_evaluations=Some(64);
        ga.options.acceptable_cost=Some(-1.0);
        let r=ga.execute().unwrap();
        assert_eq!(r.objective_evaluations,64);
    }
}
