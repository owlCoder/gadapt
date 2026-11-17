use std::collections::{HashMap, HashSet};
use std::time::Instant;

use crate::constraints::Ranker;
use crate::diversity;
use crate::hooks::{CandidateView,GeneticHooks};
use crate::linkage::Linkage;
use crate::discrete;
use crate::model::{
    Candidate, ConstraintMethod, CrossoverProbabilityPolicy, ExitCriterion, Fitness, GAError, Options, RunResult,
    SolutionStatus, Termination, Variable,
};
use crate::operators;
use crate::operator_credit::CreditBook;
use crate::rng::Rng;

type Objective<'a> = dyn FnMut(&[f64]) -> Result<Fitness, String> + 'a;

/// Complete native-Rust GA execution entry point. No Python runtime is needed.
///
/// The objective receives decision variables in registration order.
/// For fallible objectives use [GA::try_new]. For constrained objectives,
/// use [GA::constrained], or [GA::try_new] with Fitness::Constrained.
pub struct GA<'a> {
    pub options: Options,
    pub variables: Vec<Variable>,
    objective: Box<Objective<'a>>,
    operator_hooks:Option<Box<dyn GeneticHooks+'a>>,
    exit_callback:Option<Box<dyn FnMut()->bool+'a>>,
}
impl<'a> GA<'a> {
    pub fn new<F>(mut objective: F) -> Self
    where F: FnMut(&[f64]) -> f64 + 'a {
        Self::try_new(move |xs| Ok(Fitness::Scalar(objective(xs))))
    }
    pub fn constrained<F>(mut objective: F) -> Self
    where F: FnMut(&[f64]) -> (f64, f64) + 'a {
        let mut ga = Self::try_new(move |xs| {
            let (objective, violation) = objective(xs);
            Ok(Fitness::Constrained { objective, violation })
        });
        ga.options.constraint_handling = Some(ConstraintMethod::FeasibilityRules);
        ga
    }
    pub fn try_new<F>(objective: F) -> Self
    where F: FnMut(&[f64]) -> Result<Fitness, String> + 'a {
        Self { options: Options::default(), variables: Vec::new(), objective: Box::new(objective),
            operator_hooks:None,exit_callback:None }
    }
    /// Install a custom Rust operator factory, without altering the objective.
    pub fn set_hooks<H:GeneticHooks+'a>(&mut self,hooks:H)->&mut Self{
        self.operator_hooks=Some(Box::new(hooks));
        self
    }
    /// Register an external early-stop callback, checked between generations.
    pub fn set_exit_callback<F:FnMut()->bool+'a>(&mut self,callback:F)->&mut Self{
        self.exit_callback=Some(Box::new(callback));
        self
    }
    pub fn clear_exit_callback(&mut self)->&mut Self{
        self.exit_callback=None;
        self
    }
    /// Restore all built-in operators.
    pub fn clear_hooks(&mut self)->&mut Self{
        self.operator_hooks=None;
        self
    }
    pub fn add(&mut self, min: f64, max: f64, step: Option<f64>) -> Result<&mut Self, GAError> {
        self.variables.push(Variable::new(min, max, step)?);
        Ok(self)
    }
    pub fn execute(&mut self) -> Result<RunResult, GAError> {
        self.options.validate()?;
        if self.variables.is_empty() {
            return Err(GAError::Configuration("add at least one decision variable".into()));
        }
        let mut options = self.options.clone();
        let vars = self.variables.clone();
        if options.auto_unique_for_discrete && vars.iter().all(|v|v.grid_len().is_some()) {
            options.ensure_unique_individuals=true;
        }
        let start = Instant::now();
        let mut rng = Rng::new(options.seed);
        let mut record = Tracker::new(options.max_evaluations);
        let mut credit=if options.mutation_operator_policy==
            crate::model::MutationOperatorPolicy::Legacy{None}else{
                Some(CreditBook::new(options.mutation_operator_policy,options.mutation_credit_window))
            };
        if options.reliability_mode && options.discrete_certification {
            if let Some(axes) = discrete::axes(&vars, options.max_evaluations.unwrap_or(0)) {
                let size=axes.iter().map(Vec::len).product::<usize>();
                let mut checked=0usize;
                let mut reason=Termination::EvaluationBudget;
                for i in 0..size {
                    if options.timeout.is_some_and(|limit|start.elapsed()>=limit) {
                        reason=Termination::Timeout;
                        break;
                    }
                    let mut c=Candidate::new(discrete::point(&axes,i));
                    self.evaluate(&mut c, &mut record, &options, &vars);
                    checked+=1;
                    if record.accepted(options.acceptable_cost){
                        reason=Termination::AcceptableTarget;
                        break;
                    }
                }
                let exhausted=checked==size;
                if exhausted && reason != Termination::AcceptableTarget {
                    reason=Termination::DiscreteSpaceExhausted;
                }
                let certified=exhausted && !record.accepted(options.acceptable_cost)
                    && record.valid==size && record.invalid==0
                    && record.evaluations==size;
                let mut result=record.finish(reason,&[],0,vec![],0,0,0,options.seed,options.acceptable_cost);
                result.discrete_search_applied=true;
                result.discrete_space_size=Some(size);
                result.discrete_points_checked=Some(checked);
                result.discrete_space_exhausted=Some(exhausted);
                result.discrete_absence_certified=Some(certified);
                return Ok(result);
            }
        }
        if options.probe_cost_function {
            // As in the legacy API, probe both extreme decision vectors.
            // These are real objective callbacks and are charged against
            // the same hard evaluation budget; probes do not join the population.
            for values in [
                vars.iter().map(|v|v.min).collect(),
                vars.iter().map(|v|v.max).collect(),
            ] {
                if record.at_budget(){break;}
                let mut candidate=Candidate::new(values);
                self.evaluate(&mut candidate,&mut record,&options,&vars);
            }
        }
        let mut ranker = Ranker::new(options.constraint_handling, options.constraint_penalty_weight);
        let mut generations = 0usize;
        let mut diversity_initial: Option<f64> = None;
        let mut column_initial = vec![None;vars.len()];
        let mut history: Vec<f64> = Vec::new();
        let mut population = Vec::with_capacity(options.population_size);
        let mut global_seen: HashSet<Vec<u64>> = HashSet::new();

        while population.len() < options.population_size {
            if record.at_budget() { break; }
            let mut c = Candidate::new(vars.iter().map(|v| operators::sample(v, &mut rng)).collect());
            self.evaluate(&mut c, &mut record, &options, &vars);
            if options.ensure_unique_individuals {global_seen.insert(key(&c.values));}
            population.push(c);
            if record.accepted(options.acceptable_cost) { break; }
        }
        ranker.update(&population, 0, options.number_of_generations);
        prepare(&mut population, &ranker);
        if let Some(c) = population.first() {history.push(c.score);}
        let mut best_previous = population.first().map(|c|c.score).unwrap_or(f64::INFINITY);
        let mut average_previous = mean_best(&population, options.keep_count());
        let mut stalled = 0usize;
        let mut idle = 0usize;
        let mut restarts = 0usize;
        let mut refreshes = 0usize;
        let mut refreshes_since_improvement = 0usize;
        let mut verified_stagnant = 0usize;
        let mut immigration_events = 0usize;

        let reason = 'run: loop {
            if record.accepted(options.acceptable_cost) {
                break 'run Termination::AcceptableTarget;
            }
            if record.at_budget() { break 'run Termination::EvaluationBudget; }
            if let Some(limit) = options.timeout {
                if start.elapsed() >= limit { break 'run Termination::Timeout; }
            }
            if self.exit_callback.as_mut().is_some_and(|f|f()) {
                break 'run Termination::ExternalStop;
            }
            if options.number_of_generations.is_some_and(|n|generations >= n) {
                break 'run Termination::GenerationLimit;
            }
            if population.is_empty() { break 'run Termination::NoValidEvaluations; }

            if !options.reliability_mode {
                let stop = match options.exit_criterion {
                    ExitCriterion::AverageCost | ExitCriterion::MinimumCost =>
                        stalled >= options.max_attempt_no,
                    ExitCriterion::RequestedCost =>
                        record.best.as_ref().is_some_and(|c|c.feasible() && c.objective <= options.requested_cost),
                    ExitCriterion::Generations => false,
                };
                if stop {
                    break 'run if options.exit_criterion == ExitCriterion::RequestedCost {
                        Termination::RequestedCost
                    } else { Termination::Stagnation };
                }
            }
            if idle >= 20 { break 'run Termination::NoProgress; }

            generations += 1;
            let keep_count = options.keep_count().min(population.len());
            let elites: Vec<Candidate> = population.iter().take(keep_count).cloned().collect();
            // Assemble borrowed views only when a custom factory is installed.
            let views:Vec<CandidateView<'_>>=if self.operator_hooks.is_some(){
                elites.iter().map(|c|CandidateView{
                    values:&c.values,
                    objective:if c.valid{Some(c.objective)}else{None},
                    violation:if c.valid{Some(c.violation)}else{None},
                    score:if c.valid{Some(c.score)}else{None},
                    parent_distance:c.parent_distance,
                }).collect()
            }else{Vec::new()};
            let cost_diversity = diversity::cost(
                &population, options.cost_diversity_metric, &mut diversity_initial,
            );
            let column_diversity = diversity::columns(
                &population, &vars, options.columnar_diversity_metric,
                &mut column_initial,
            );
            let linkage=options.compensatory_mutation.and_then(|mode|Linkage::build(&elites,&vars,mode));
            let reference_score=if credit.is_some(){
                let mut values:Vec<_>=elites.iter().filter(|c|c.valid)
                    .map(|c|c.score).filter(|s|s.is_finite()).collect();
                values.sort_by(f64::total_cmp);
                values.get(values.len()/2).copied()
            }else{None};
            let mut mutated_candidates=0usize;
            let column_rate=if column_diversity.is_empty(){0.0}else{
                column_diversity.iter().sum::<f64>()/column_diversity.len() as f64
            }.clamp(0.0,1.0);
            let rate_span=options.crossover_max_probability-options.crossover_min_probability;
            let crossover_cost_probability=options.crossover_min_probability+
                rate_span*cost_diversity.clamp(0.0,1.0);
            let crossover_column_probability=options.crossover_min_probability+
                rate_span*column_rate;
            let refresh_due=options.reliability_mode
                && options.reliability_refresh_percentage>0.0
                && options.reliability_refresh_patience
                    .is_some_and(|n|n>0 && verified_stagnant>=n && verified_stagnant%n==0);
            let calls_remaining=options.max_evaluations.unwrap_or(usize::MAX)
                .saturating_sub(record.evaluations);
            let restart_due=refresh_due
                && options.reliability_restart_after_refreshes
                    .is_some_and(|n|refreshes_since_improvement>=n);
            let legacy_restart=options.reliability_mode
                && options.stagnation_restart_patience
                    .is_some_and(|n|n>0 && stalled>=n);
            // All replacement evaluations must fit before committing a restart.
            let restart=(restart_due || legacy_restart)
                && record.best.is_some()
                && calls_remaining>=options.population_size.saturating_sub(1);
            let adaptive_due=options.adaptive_immigration_patience
                .is_some_and(|n|n>0 && stalled>=n && stalled%n==0)
                && cost_diversity<options.adaptive_immigration_diversity_threshold;
            let extra_immigrants=if adaptive_due {
                ((keep_count as f64*options.adaptive_immigration_percentage/100.0).ceil() as usize).max(1)
            }else{0};
            let refresh_immigrants=if refresh_due {
                ((keep_count as f64*options.reliability_refresh_percentage/100.0).ceil() as usize).max(1)
            }else{0};
            let immigration=options.immigration_number.max(extra_immigrants)
                .max(refresh_immigrants).min(keep_count.saturating_sub(1));

            let verified_before=record.best.as_ref().map(|c|(c.objective,c.violation));
            let mut next = Vec::with_capacity(options.population_size);
            if restart {
                next.push(record.best.as_ref().unwrap().clone());
                restarts += 1;
                refreshes_since_improvement=0;
            } else {
                next.extend(elites.iter().take(keep_count.saturating_sub(immigration)).cloned());
                if options.reliability_mode {
                    if let Some(best)=record.best.as_ref() {
                        if !next.iter().any(|c|c.values==best.values && c.valid) && !next.is_empty(){
                            *next.last_mut().unwrap()=best.clone();
                        }
                    }
                }
                if refresh_due && immigration>0{
                    refreshes+=1;
                    refreshes_since_improvement+=1;
                }
            }
            let prev_evals = record.evaluations;
            let mut seen: HashSet<Vec<u64>> = if options.ensure_unique_individuals{
                next.iter().map(|c|key(&c.values)).collect()
            }else{HashSet::new()};
            // Keep live objective callbacks inside evaluate; never pre-score an unevaluated child.
            let offspring_target = if restart{1}else{
                options.population_size.saturating_sub(immigration)
            };
            let mut attempts_without_new_candidate = 0usize;
            let mut pending_child:Option<(Vec<f64>,usize,usize)>=None;
            while next.len() < offspring_target {
                if record.at_budget() { break; }
                if options.timeout.is_some_and(|limit|start.elapsed()>=limit) {break;}
                let (mut values,a,b)=if let Some(child)=pending_child.take(){
                    child
                } else {
                    let crossover_probability=match options.crossover_probability_policy{
                        CrossoverProbabilityPolicy::Fixed=>options.crossover_probability,
                        CrossoverProbabilityPolicy::CostDiversity=>crossover_cost_probability,
                        CrossoverProbabilityPolicy::ColumnarDiversity=>crossover_column_probability,
                        CrossoverProbabilityPolicy::Mixed=>
                            if rng.bool(0.5){crossover_cost_probability}
                            else{crossover_column_probability},
                    };
                    let has_custom_hooks=self.operator_hooks.is_some();
                    let mut choose=|rng:&mut Rng| -> Result<usize,GAError>{
                        let picked=self.operator_hooks.as_mut().and_then(|h|
                            h.select_parent(&views,rng));
                        if let Some(idx)=picked{
                            if idx>=elites.len(){return Err(GAError::Configuration(
                                "custom parent selector returned an out-of-range index".into()));}
                            Ok(idx)
                        }else{Ok(operators::parent_index(&elites,options.parent_selection,rng))}
                    };
                    let a=choose(&mut rng)?;
                    let b=choose(&mut rng)?;
                    let third_index=if has_custom_hooks{choose(&mut rng)?}else{a};
                    let first=&elites[a];
                    let second=&elites[b];
                    let third=&elites[third_index];
                    let mut pair=operators::cross_pair(
                        first,second,&elites,&vars,&options,crossover_probability,&mut rng);
                    if let Some(hooks)=self.operator_hooks.as_mut(){
                        if let Some(custom)=hooks.crossover(
                            &first.values,&second.values,&third.values,&vars,crossover_probability,&mut rng
                        ){pair.0=custom;}
                        if let Some(custom)=hooks.crossover(
                            &second.values,&first.values,&third.values,&vars,crossover_probability,&mut rng
                        ){pair.1=custom;}
                    }
                    if pair.0.len()!=vars.len() || pair.1.len()!=vars.len(){
                        return Err(GAError::Configuration(
                            "custom crossover returned wrong genome length".into()));
                    }
                    if next.len()+1<offspring_target {
                        pending_child=Some((pair.1,a,b));
                    }
                    (pair.0,a,b)
                };
                let first=&elites[a];
                let second=&elites[b];
                let mut trace:Vec<(usize,usize)>=Vec::new();
                let force=options.must_mutate_for_same_parents&&first.values==second.values;
                let mutation_probability = options.population_mutation_fraction
                    * (1.0 - cost_diversity).clamp(0.0,1.0);
                if force || (mutated_candidates<options.max_mutated_candidates.unwrap_or(usize::MAX)
                    && rng.bool(mutation_probability)) {
                    let before=linkage.as_ref().map(|_|values.clone());
                    let handled=self.operator_hooks.as_mut().is_some_and(|h|
                        h.mutate(&mut values,&vars,&column_diversity,&mut rng));
                    let count=if handled{
                        before.as_ref().map(|v|v.iter().zip(&values)
                            .filter(|(a,b)|*a!=*b).count()).unwrap_or(1)
                    }else{
                        operators::mutate(&mut values,&vars,&options,&column_diversity,
                            force,&mut rng,stalled,credit.as_mut(),&mut trace)
                    };
                    if count>0{mutated_candidates+=1;}
                    if let (Some(model),Some(original))=(&linkage,before) {
                        model.apply(&mut values,&original,&vars,&mut rng);
                    }
                }
                let mut current_key=if options.ensure_unique_individuals{key(&values)}
                    else{Vec::new()};
                if options.ensure_unique_individuals {
                    for attempt in 0..15 {
                        if !seen.contains(&current_key) && !global_seen.contains(&current_key) {break;}
                        if attempt < 5 {
                            let before=linkage.as_ref().map(|_|values.clone());
                            let handled=self.operator_hooks.as_mut().is_some_and(|h|
                                h.mutate(&mut values,&vars,&column_diversity,&mut rng));
                            if !handled {
                                operators::mutate(&mut values,&vars,&options,&column_diversity,
                                    true,&mut rng,stalled,credit.as_mut(),&mut trace);
                            }
                            if let (Some(model),Some(original))=(&linkage,before) {
                                model.apply(&mut values,&original,&vars,&mut rng);
                            }
                        }else{
                            values=vars.iter().map(|v|operators::sample(v,&mut rng)).collect();
                        }
                        current_key=key(&values);
                    }
                    if seen.contains(&current_key) || global_seen.contains(&current_key) {
                        attempts_without_new_candidate+=1;
                        // Finite discrete spaces cannot always furnish unseen offspring.
                        if attempts_without_new_candidate>options.population_size*3 {break;}
                        continue;
                    }
                }
                let mut child=Candidate::new(values);
                child.parent_distance=diversity::parent_distance(&first.values,&second.values,&vars);
                let before_calls=record.evaluations;
                self.evaluate(&mut child, &mut record, &options, &vars);
                if let Some(book)=credit.as_mut(){
                    let score=if record.evaluations>before_calls && child.valid {
                        Some(ranker.score(&child))
                    }else{None};
                    book.observe(&trace,score,reference_score);
                }
                if options.ensure_unique_individuals {
                    seen.insert(current_key.clone());
                    global_seen.insert(current_key);
                }
                next.push(child);
                if record.accepted(options.acceptable_cost) { break; }
            }
            // Periodic and diversity-triggered immigration are distinct from restart.
            while next.len() < options.population_size && !record.at_budget()
                && !record.accepted(options.acceptable_cost) {
                if options.timeout.is_some_and(|limit|start.elapsed()>=limit){break;}
                let vals:Vec<f64>=vars.iter().map(|v|operators::sample(v,&mut rng)).collect();
                let k=if options.ensure_unique_individuals{key(&vals)}else{Vec::new()};
                if options.ensure_unique_individuals
                    && (global_seen.contains(&k) || seen.contains(&k)) {break;}
                let mut immigrant=Candidate::new(vals);
                self.evaluate(&mut immigrant, &mut record, &options, &vars);
                if options.ensure_unique_individuals{global_seen.insert(k);}
                next.push(immigrant);
                immigration_events+=1;
            }
            if next.is_empty(){break 'run Termination::NoValidEvaluations;}
            if record.evaluations==prev_evals {idle+=1;}else{idle=0;}
            ranker.update(&next, generations, options.number_of_generations);
            prepare(&mut next, &ranker);
            population=next;

            let min = population.first().map(|c|c.score).unwrap_or(f64::INFINITY);
            history.push(min);
            let average=mean_best(&population, options.keep_count());
            let improved = match options.exit_criterion {
                ExitCriterion::AverageCost => average < average_previous,
                _ => min < best_previous,
            };
            if improved {stalled=0;} else {stalled+=1;}
            let verified_after=record.best.as_ref().map(|c|(c.objective,c.violation));
            if verified_after!=verified_before {
                verified_stagnant=0;
                refreshes_since_improvement=0;
            } else {
                verified_stagnant+=1;
            }
            best_previous=min;
            average_previous=average;
            // When no acceptable result exists, a restart preserves the exact
            // evaluated incumbent in Tracker, independent of scalar penalty ordering.
            if restart {stalled=0;}
        };
        let mut result=record.finish(reason, &population, generations, history, restarts,refreshes,
            immigration_events, options.seed, options.acceptable_cost);
        result.operator_credit_summary=credit.map(|book|book.summary());
        Ok(result)
    }

    fn evaluate(&mut self, candidate:&mut Candidate, record:&mut Tracker,
        options:&Options, vars:&[Variable]) {
        // Avoid per-callback key allocations and hash lookups when caching is off.
        let request=options.cache_evaluations.then(||key(&candidate.values));
        if let Some(request)=request.as_ref() {
            if let Some(&(objective, violation)) = record.cache.get(request) {
                record.cached += 1;
                candidate.objective=objective;
                candidate.violation=violation;
                candidate.valid=true;
                record.observe(candidate);
                return;
            }
        }
        if record.at_budget(){return;}
        // Count before entering the user callback, including every failure.
        record.evaluations+=1;
        let evaluation=(self.objective)(&candidate.values);
        let parsed=match evaluation {
            Ok(fitness)=>{
                let (objective, violation)=fitness.pair();
                if !objective.is_finite() || !violation.is_finite()
                    || violation < 0.0 || objective.abs()>1e150
                    || violation>1e150 {None}
                else if !matches!((options.constraint_handling,fitness),
                    (None,Fitness::Scalar(_)) | (Some(_),Fitness::Constrained{..})) {None}
                else if !candidate.values.iter().zip(vars).all(|(&x,var)|var.contains(x)){
                    None
                }else{Some((objective, violation))}
            }
            Err(_)=>None,
        };
        match parsed {
            None=>record.invalid+=1,
            Some((objective,violation))=>{
                record.valid+=1;
                candidate.valid=true;
                candidate.objective=objective;
                candidate.violation=violation;
                if let Some(request)=request {
                    record.cache.insert(request,(objective,violation));
                }
                record.observe(candidate);
            }
        }
    }
}

fn key(values:&[f64])->Vec<u64>{values.iter().map(|x|x.to_bits()).collect()}
fn prepare(population:&mut Vec<Candidate>,ranker:&Ranker) {
    for c in population.iter_mut() {c.score=ranker.score(c);}
    population.sort_by(|a,b|ranker.compare(a,b));
}
fn mean_best(population:&[Candidate], keep:usize)->f64 {
    let n=keep.min(population.len());
    if n==0 {return f64::INFINITY;}
    let values:Vec<f64>=population.iter().take(n).filter(|c|c.valid)
        .map(|c|c.score).collect();
    if values.is_empty(){return f64::INFINITY;}
    values.iter().sum::<f64>()/values.len() as f64
}
struct Tracker {
    max_evaluations:Option<usize>,
    evaluations:usize, valid:usize, invalid:usize, cached:usize,
    cache:HashMap<Vec<u64>,(f64,f64)>,
    best:Option<Candidate>,
}
impl Tracker {
    fn new(limit:Option<usize>)->Self {
        Self { max_evaluations:limit, evaluations:0,valid:0,invalid:0,cached:0,
            cache:HashMap::new(),best:None }
    }
    fn at_budget(&self)->bool{
        self.max_evaluations.is_some_and(|limit|self.evaluations>=limit)
    }
    fn observe(&mut self,c:&Candidate) {
        if !c.valid{return;}
        let better=match &self.best {
            None=>true,
            Some(prev)=>{
                match (c.feasible(),prev.feasible()) {
                    (true,false)=>true,
                    (false,true)=>false,
                    (true,true)=>c.objective<prev.objective,
                    (false,false)=>c.violation<prev.violation
                        || (c.violation==prev.violation&&c.objective<prev.objective),
                }
            }
        };
        if better {self.best=Some(c.clone());}
    }
    fn accepted(&self,target:Option<f64>)->bool{
        target.is_some_and(|t|self.best.as_ref().is_some_and(|c|c.feasible() && c.objective<=t))
    }
    fn finish(&self,reason:Termination,population:&[Candidate],generations:usize,
        history:Vec<f64>,restarts:usize,refreshes:usize,immigration_events:usize,
        seed:u64,target:Option<f64>)->RunResult{
        let accepted=self.accepted(target);
        let feasible=self.best.as_ref().is_some_and(Candidate::feasible);
        let solution_status=match (&self.best,feasible,accepted) {
            (None,_,_)=>SolutionStatus::NoValidEvaluation,
            (Some(_),_,true)=>SolutionStatus::Acceptable,
            (Some(_),true,false)=>SolutionStatus::Feasible,
            _=>SolutionStatus::Infeasible,
        };
        RunResult {
            result_values:self.best.as_ref().map(|c|c.values.clone()).unwrap_or_default(),
            min_cost:population.iter().find(|c|c.valid).map(|c|c.score),
            best_objective:self.best.as_ref().map(|c|c.objective),
            best_violation:self.best.as_ref().map(|c|c.violation),
            feasible,acceptable:accepted,solution_status,
            termination_reason:reason,
            number_of_iterations:generations,min_cost_per_generation:history,
            operator_credit_summary:None,
            objective_evaluations:self.evaluations,
            valid_objective_evaluations:self.valid,
            invalid_objective_evaluations:self.invalid,
            cached_objective_requests:self.cached,
            reliability_restarts:restarts,
            stagnation_refreshes:refreshes,
            discrete_search_applied:false,
            discrete_space_size:None,
            discrete_points_checked:None,
            discrete_space_exhausted:None,
            discrete_absence_certified:None,
            immigration_events,seed,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_fixed_budget(){
        let mut ga=GA::new(|v|v[0]*v[0]);ga.add(-1.0,1.0,None).unwrap();
        ga.options.max_evaluations=Some(7);
        let x=ga.execute().unwrap();
        assert_eq!(x.objective_evaluations,7);
        assert_eq!(x.valid_objective_evaluations,7);
        assert!(x.best_objective.is_some());
    }
    #[test]
    fn test_never_exceed_budget_on_error(){
        let mut ga=GA::try_new(|_|Err("simulated failure".to_owned()));
        ga.add(-1.0,1.0,None).unwrap();
        ga.options.reliability_mode=true;
        ga.options.max_evaluations=Some(9);
        ga.options.acceptable_cost=Some(0.0);
        let x=ga.execute().unwrap();
        assert!(x.objective_evaluations<=9);
        assert_eq!(x.valid_objective_evaluations,0);
        assert_eq!(x.solution_status,SolutionStatus::NoValidEvaluation);
    }
}
