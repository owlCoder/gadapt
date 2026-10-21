"""Opt-in, strictly metered sequential scenario fitness for actual GAdapt GA.

Safety-first policy:
* A declared *robust feasible* candidate was physically evaluated in ALL
  registered scenarios, and EVERY evaluated scenario satisfied its original
  source constraints and numerically converged.
* A single measured physical violation PROVES non-robustness on the finite
  registered suite, so later AC calls may be skipped for this candidate;
  they are UNOBSERVED and never counted as zero or simulated.
* A nonconvergent/exceptional solver result is NUMERICALLY UNKNOWN, not a
  mathematical proof of physical infeasibility.
* Real simulator call counts come ONLY from the caller-provided monotone
  counter. Every invoked scenario callback MUST advance it exactly once.
* No scenario is invoked unless >=N genuine AC calls remain available,
  reserving the possibility of a full validation in every new candidate.

The static first-fail and empirical-failure-order screening heuristics are
KNOWN families of early-stopping/racing ideas; no claim of new scientific
algorithm is made here. Default GA/cost-finding behavior is unchanged.
"""
import math
from numbers import Real

UNVERIFIED_SCORE=1e12
CENSORED_BASE_SCORE=1e9


class SequentialScenarioBudgetCost:
    """Drop-in cost_function for GA, DE, or any optimizer.

    scenario_evaluator(vector, scenario) performs exactly ONE true simulator
    solve (whether it converges or not) and returns source physical diagnostics.
    physical_counter() observes true attempted solves, not objective requests.

    Modes:
      full : N AC every trial; complete penalized source objective
      stop_fixed : stop after first measured physical constraint violation
      stop_adaptive : same, but empirically order prior measured failure rates

    Recorded partial observations NEVER claim that an untested scenario is
    feasible or infeasible. Returned censored scores are ranking surrogates
    and ARE NOT original fully evaluated penalized objective values.
    """
    def __init__(self, scenarios, scenario_evaluator, physical_counter,
                 budget, mode="full", penalty=1e5,
                 unknown_score=UNVERIFIED_SCORE):
        self.scenarios=tuple(scenarios)
        if (len(self.scenarios)<2 or
            len({str(s) for s in self.scenarios})!=len(self.scenarios)):
            raise ValueError("Require >=2 distinct predeclared physical scenarios")
        if mode not in ("full","stop_fixed","stop_adaptive"):
            raise ValueError("mode must be full/stop_fixed/stop_adaptive")
        if not callable(scenario_evaluator) or not callable(physical_counter):
            raise ValueError("Scenario callback and true physical AC counter required")
        if type(budget) is not int or budget<len(self.scenarios):
            raise ValueError("Budget must accommodate at least one full scenario batch")
        if (not isinstance(penalty,Real) or isinstance(penalty,bool) or
            not math.isfinite(penalty) or penalty<=0):
            raise ValueError("Positive finite physical violation penalty required")
        if (not isinstance(unknown_score,Real) or isinstance(unknown_score,bool) or
            not math.isfinite(unknown_score) or unknown_score<=CENSORED_BASE_SCORE):
            raise ValueError("unknown_score must dominate censored scores")
        self._evaluate=scenario_evaluator
        self._physical_counter=physical_counter
        self.budget=budget
        self.mode=mode
        self.penalty=float(penalty)
        self.unknown_score=float(unknown_score)
        self._origin=self._read_counter()
        self.requests=0
        self.post_budget_requests=0
        self.complete_candidates=0
        self.censored_physically_infeasible=0
        self.incomplete_numerically_unknown=0
        self.all_scenario_feasible=0
        self.first_robust_AC=None
        self.best_robust_cost=math.inf
        self.best_robust_vector=None
        self.best_robust_physics=None
        self.best_true_complete_penalized=math.inf
        self.best_censored_ranking_score=math.inf
        self.actual_scenario_attempts=[0]*len(self.scenarios)
        self.measured_converged_physical_failures=[0]*len(self.scenarios)
        self.measured_numerical_unknown=[0]*len(self.scenarios)
        self.measured_feasible=[0]*len(self.scenarios)
        self.total_unobserved_skipped_scenarios=0
        self.total_candidates_with_one_ac=0
        self.total_candidates_with_two_ac=0
        self._last_status=None

    def _read_counter(self):
        x=self._physical_counter()
        if type(x) is not int or x<0:
            raise ValueError("Physical simulator counter must be a nonnegative integer")
        return x

    @property
    def calls(self):
        return self._read_counter()-self._origin

    @property
    def remaining(self):
        return self.budget-self.calls

    def _order(self):
        n=len(self.scenarios)
        if self.mode!="stop_adaptive":
            return tuple(range(n))
        return tuple(sorted(range(n),key=lambda i:(
           -(self.measured_converged_physical_failures[i]+1)/
               (self.actual_scenario_attempts[i]+2),
           i)))

    def _one_verified_physical_call(self,candidate,index):
        before=self._read_counter()
        thrown=None
        try:
            raw=self._evaluate(candidate,self.scenarios[index])
        except Exception as err:
            thrown=err
            raw={"converged":False,"feasible":False,
                 "error":(type(err).__name__+": "+str(err))[:240]}
        after=self._read_counter()
        if after-before!=1:
            raise RuntimeError("Scenario evaluator must charge exactly ONE true physical solve")
        self.actual_scenario_attempts[index]+=1
        if not isinstance(raw,dict) or type(raw.get("converged")) is not bool:
            raise ValueError("Scenario callback must return explicit converged bool")
        if not raw["converged"]:
            self.measured_numerical_unknown[index]+=1
            return {"converged":False,"feasible":False,"error":str(raw.get("error",""))[:240]}
        if type(raw.get("feasible")) is not bool:
            raise ValueError("Scenario callback must distinguish source physical feasibility")
        viol=raw.get("normalized_violation")
        cost=raw.get("original_economic_cost")
        for name,value in (("normalized_violation",viol),("original_economic_cost",cost)):
            if not isinstance(value,Real) or isinstance(value,bool) or not math.isfinite(float(value)):
                raise ValueError("Measured %s must be finite real" % name)
        viol=float(viol)
        cost=float(cost)
        if viol<0 or (raw["feasible"] and viol!=0) or (not raw["feasible"] and viol<=0):
            raise ValueError("Measured source physical violation/feasible mismatch")
        if raw["feasible"]:
            self.measured_feasible[index]+=1
        else:
            self.measured_converged_physical_failures[index]+=1
        return {"converged":True,"feasible":raw["feasible"],
                "normalized_violation":viol,"original_economic_cost":cost,
                "q_source_excess_mvar":raw.get("q_source_excess_mvar"),
                "max_nodal_mismatch_mva":raw.get("max_nodal_mismatch_mva")}

    def __call__(self,candidate):
        self.requests+=1
        self._last_status=None
        if self.remaining<len(self.scenarios):
            self.post_budget_requests+=1
            self._last_status="no_real_ac_budget"
            return self.unknown_score
        order=self._order()
        observed={}
        start=self.calls
        verdict="complete"
        for index in order:
            observed[index]=self._one_verified_physical_call(candidate,index)
            z=observed[index]
            if not z["converged"] and self.mode!="full":
                verdict="numerically_unknown"
                break
            if z["converged"] and not z["feasible"] and self.mode!="full":
                verdict="screened_physically_infeasible"
                break
        used=self.calls-start
        if used!=len(observed) or self.calls>self.budget:
            raise RuntimeError("Physical scenario budget changed unexpectedly")
        self.total_unobserved_skipped_scenarios+=len(self.scenarios)-len(observed)
        if used==1:self.total_candidates_with_one_ac+=1
        if used==2:self.total_candidates_with_two_ac+=1
        all_converged=all(z["converged"] for z in observed.values())
        if verdict=="screened_physically_infeasible":
            self.censored_physically_infeasible+=1
            violation=float(observed[order[-1]]["normalized_violation"]) if order[-1] in observed else float(
                next(z["normalized_violation"] for z in observed.values() if z["converged"] and not z["feasible"]))
            # Use only measured information; not the unknown 3-scenario mean
            # and never pretend that skipped scenarios had zero violation.
            score=CENSORED_BASE_SCORE+self.penalty*violation
            self.best_censored_ranking_score=min(self.best_censored_ranking_score,score)
            self._last_status=verdict
            return float(score)
        if verdict=="numerically_unknown" or not all_converged:
            self.incomplete_numerically_unknown+=1
            self._last_status="numerically_unknown"
            return self.unknown_score
        if len(observed)!=len(self.scenarios):
            raise RuntimeError("Incomplete scenario vector cannot report full feasible result")
        self.complete_candidates+=1
        values=[observed[i] for i in range(len(self.scenarios))]
        cost=sum(v["original_economic_cost"] for v in values)/len(values)
        score=cost+self.penalty*sum(v["normalized_violation"] for v in values)
        if not math.isfinite(score):
            raise ValueError("Full physical score must be finite")
        self.best_true_complete_penalized=min(self.best_true_complete_penalized,score)
        if all(v["feasible"] for v in values):
            self.all_scenario_feasible+=1
            if self.first_robust_AC is None:
                self.first_robust_AC=self.calls
            if cost<self.best_robust_cost:
                self.best_robust_cost=cost
                self.best_robust_vector=[float(v) for v in candidate]
                self.best_robust_physics={
                  "per_scenario_original_cost":[v["original_economic_cost"] for v in values],
                  "per_scenario_real_source_normalized_violation":[v["normalized_violation"] for v in values],
                  "per_scenario_max_KCL_mva":[v["max_nodal_mismatch_mva"] for v in values]}
        self._last_status="completely_evaluated"
        return float(score)

    def summary(self):
        return {
           "mode":self.mode,
           "actual_native_AC_calls":self.calls,
           "max_native_AC_budget":self.budget,
           "unused_due_to_reserving_complete_validation":self.remaining,
           "objective_requests":self.requests,
           "post_budget_requests_without_AC":self.post_budget_requests,
           "completely_evaluated_candidates":self.complete_candidates,
           "early_screened_physically_infeasible_candidates":self.censored_physically_infeasible,
           "numerically_unknown_candidates":self.incomplete_numerically_unknown,
           "verified_all_scenario_feasible_candidates":self.all_scenario_feasible,
           "first_verified_robust_true_AC_number":self.first_robust_AC,
           "best_verified_robust_mean_economic_cost_or_null":(
               self.best_robust_cost if math.isfinite(self.best_robust_cost) else None),
           "best_verified_robust_vector_or_null":self.best_robust_vector,
           "best_verified_robust_source_physics_or_null":self.best_robust_physics,
           "best_fully_measured_penalized_score_or_null":(
               self.best_true_complete_penalized
               if math.isfinite(self.best_true_complete_penalized) else None),
           "best_censored_heuristic_score_not_true_objective_or_null":(
               self.best_censored_ranking_score
               if math.isfinite(self.best_censored_ranking_score) else None),
           "unobserved_scenarios_NOT_counted_as_feasible_or_infeasible":
               self.total_unobserved_skipped_scenarios,
           "candidates_stopped_after_1_real_AC":self.total_candidates_with_one_ac,
           "candidates_stopped_after_2_real_AC":self.total_candidates_with_two_ac,
           "source_scenarios":list(self.scenarios),
           "actual_AC_per_scenario":list(self.actual_scenario_attempts),
           "actually_observed_physical_source_failures_per_scenario":
               list(self.measured_converged_physical_failures),
           "actually_observed_numerical_unknown_per_scenario":
               list(self.measured_numerical_unknown),
           "actually_observed_source_feasible_per_scenario":list(self.measured_feasible),
           "unobserved_missing_results_are_never_source_feasible":True,
           "empirical_fail_probability_for_NEXT_sample":[
              (bad+1)/(tested+2)
              for bad,tested in zip(self.measured_converged_physical_failures,
                                  self.actual_scenario_attempts)],
        }
