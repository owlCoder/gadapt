"""I31 preregistered GA-only fitness-vs-evaluation-budget ablation.

The original GAdapt implementation and source AC physics are unchanged.
The `full_censored` arm is a deliberately expensive *control*: all three
physical scenarios are ALWAYS paid, but the selection score is the same
first-failure heuristic used by the first-failure early-stopping arm. This
allows us to separate score-landscape effects from screening benefits.
Same already-seen I30 spatial IEEE118 scenario suite; NOT a new holdout grid.
"""
import argparse
import csv
import json
import math
import platform
import random
import statistics
import time

import numpy as np
import pandas as pd
import scipy
from gadapt.ga import GA

from gadapt.operations.cost_finding.sequential_scenario_budget_cost import (
    SequentialScenarioBudgetCost, CENSORED_BASE_SCORE,
)
from research.iteration30_spatial_load_holdout import (
    IEEE118SourceParityLoadScenario, SPATIAL_SCENARIOS,
)
from research.iteration27_real_scenario_credit_benchmark import CONTROL_BUS_GEN


METHODS=("full_true","full_censored","stop_fixed","stop_adaptive")
SEEDS=tuple(range(2080,2092))
BUDGET=180
POPULATION=12
EXPECTED_MAX_NATIVE_AC=len(METHODS)*len(SEEDS)*BUDGET


class FullMeasuredCensoredReference(SequentialScenarioBudgetCost):
    """Paid full-source AC with *only* the selection score censored.

    Unlike stop_fixed this never elides any scenario, even when the first
    source limit is already proven violated. The first measured violation
    is remembered solely for the returned ranking score; true full-source
    costs and all observed physical diagnostics still come from the
    inherited full mode. On ANY numerical unknown, return unknown_score.
    A partial evaluation is never declared source-feasible.
    """
    def __init__(self, scenarios, scenario_evaluator, physical_counter,
                 budget, penalty=1e5):
        super().__init__(scenarios,scenario_evaluator,physical_counter,
                         budget,mode="full",penalty=penalty)
        original=self._evaluate
        self._first_violation_this_candidate=None
        self.full_cost_censored_selection_candidates=0

        def observe_first_failure(candidate,scenario):
            raw=original(candidate,scenario)
            if (isinstance(raw,dict) and
                raw.get("converged") is True and
                raw.get("feasible") is False and
                self._first_violation_this_candidate is None):
                self._first_violation_this_candidate=raw.get("normalized_violation")
            return raw
        self._evaluate=observe_first_failure

    def __call__(self,candidate):
        self._first_violation_this_candidate=None
        full_score=super().__call__(candidate)
        if self._last_status!="completely_evaluated":
            return full_score
        if self._first_violation_this_candidate is None:
            return full_score
        v=float(self._first_violation_this_candidate)
        if not math.isfinite(v) or v<=0:
            raise ValueError("First measured physical failure must have positive violation")
        censored=CENSORED_BASE_SCORE+self.penalty*v
        if not math.isfinite(censored) or censored>=self.unknown_score:
            raise ValueError("Censored reference score collides with unknown score")
        self.full_cost_censored_selection_candidates+=1
        self.best_censored_ranking_score=min(self.best_censored_ranking_score,censored)
        return float(censored)

    def summary(self):
        q=super().summary()
        q["mode"]="full_censored"
        q["fully_measured_physical_failures_returning_censored_fitness"]=(
            self.full_cost_censored_selection_candidates)
        q["true_full_source_score_is_not_censored_selection_score"]=True
        return q


def make_evaluator(mode, grid):
    if mode not in METHODS:
        raise ValueError("Unpreregistered I31 evaluator mode")
    options=dict(scenarios=SPATIAL_SCENARIOS,
                 scenario_evaluator=grid.evaluate_scenario,
                 physical_counter=lambda:grid.real_ac_calls,
                 budget=BUDGET,penalty=1e5)
    if mode=="full_censored":
        return FullMeasuredCensoredReference(**options)
    return SequentialScenarioBudgetCost(**options,mode=(
        "full" if mode=="full_true" else mode))


def perform_one(method,seed):
    if method not in METHODS or seed not in SEEDS:
        raise ValueError("I31 method/seed must match preregistration")
    random.seed(seed)
    np.random.seed(seed)
    grid=IEEE118SourceParityLoadScenario()
    ev=make_evaluator(method,grid)
    start=time.monotonic()
    optimizer_success=False
    error=""
    try:
        ga=GA(cost_function=ev,
              population_size=POPULATION,
              cost_diversity_metric="log_relative",
              exit_check="generations",
              number_of_generations=128,
              exit_function=lambda:ev.remaining<len(SPATIAL_SCENARIOS),
              population_mutation="cost_diversity,parent_diversity",
              timeout=240)
        for lo,hi in grid.bounds:
            ga.add(float(lo),float(hi))
        result=ga.execute()
        optimizer_success=bool(result.success)
        error="" if optimizer_success else str(result.messages)[:300]
    except Exception as ex:
        error=(type(ex).__name__+": "+str(ex))[:350]

    q=ev.summary()
    if (q["actual_native_AC_calls"]!=grid.real_ac_calls or
        grid.real_ac_calls>BUDGET or
        sum(q["actual_AC_per_scenario"])!=grid.real_ac_calls or
        q["verified_all_scenario_feasible_candidates"]>
            q["completely_evaluated_candidates"]):
        raise RuntimeError("Invalid physical simulator boundary accounting")
    if method in ("full_true","full_censored"):
        if (q["actual_native_AC_calls"]%len(SPATIAL_SCENARIOS)!=0 or
            q["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"]!=0 or
            q["actual_AC_per_scenario"]!=[grid.real_ac_calls//3]*3):
            raise RuntimeError("Fully measured I31 arm skipped real source AC")
    return {
        "method":method,"seed":seed,
        "same_public_ieee118_spatial_load_profiles_as_I30":True,
        "optimizer_reported_success_not_equivalent_to_physical_feasibility":optimizer_success,
        "optimizer_message_or_exception":error,
        "wall_seconds":round(time.monotonic()-start,4),
        **q,
    }


def paired_success_contrast(rows, first, second):
    """Seed is the replicate; candidate counts are not independent samples."""
    a={r["seed"]:bool(r["verified_all_scenario_feasible_candidates"])
       for r in rows if r["method"]==first}
    b={r["seed"]:bool(r["verified_all_scenario_feasible_candidates"])
       for r in rows if r["method"]==second}
    if set(a)!=set(SEEDS) or set(b)!=set(SEEDS):
        raise RuntimeError("Missing paired seed in preregistered contrast")
    return {
        "first":first, "second":second,
        "both_succeed":sum(a[s] and b[s] for s in SEEDS),
        "first_only":sum(a[s] and not b[s] for s in SEEDS),
        "second_only":sum(b[s] and not a[s] for s in SEEDS),
        "neither_succeeds":sum(not a[s] and not b[s] for s in SEEDS),
    }


def run_preregistered():
    if (METHODS!=("full_true","full_censored","stop_fixed","stop_adaptive")
        or SEEDS!=tuple(range(2080,2092))
        or SPATIAL_SCENARIOS!=("nominal","odd_bus_heavier","even_bus_heavier")
        or BUDGET!=180 or POPULATION!=12 or EXPECTED_MAX_NATIVE_AC!=8640):
        raise RuntimeError("I31 predeclared protocol drift")
    rows=[]
    for seed in SEEDS:
        for method in METHODS:
            r=perform_one(method,seed)
            rows.append(r)
            print("I31_TRUE_AC",json.dumps(r,sort_keys=True,allow_nan=False),flush=True)
    summary={}
    for method in METHODS:
        sample=[r for r in rows if r["method"]==method]
        prices=[r["best_verified_robust_mean_economic_cost_or_null"]
                for r in sample if r["best_verified_robust_mean_economic_cost_or_null"] is not None]
        summary[method]={
            "runs":len(sample),
            "successful_seeds_with_truly_3AC_verified_feasible":len(prices),
            "truly_paid_native_AC":sum(r["actual_native_AC_calls"] for r in sample),
            "complete_three_scenario_candidates":sum(
                r["completely_evaluated_candidates"] for r in sample),
            "verified_all_three_feasible_candidates":sum(
                r["verified_all_scenario_feasible_candidates"] for r in sample),
            "early_screened_physically_infeasible":sum(
                r["early_screened_physically_infeasible_candidates"] for r in sample),
            "objective_requests":sum(r["objective_requests"] for r in sample),
            "unobserved_AC_never_executed":sum(
                r["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"]
                for r in sample),
            "best_true_verified_original_source_mean_cost_or_null":(
                min(prices) if prices else None),
            "median_original_cost_conditional_on_success_or_null":(
                statistics.median(prices) if prices else None),
        }
    return {"metadata":{
        "protocol":"research/ITERATION31_PROTOCOL.md",
        "methods":list(METHODS),"seeds":list(SEEDS),
        "source_scenarios":list(SPATIAL_SCENARIOS),
        "control_source_PV_buses":[bus for bus,_ in CONTROL_BUS_GEN],
        "same_spatial_ieee118_not_independent_network":True,
        "real_physical_AC_budget_per_run":BUDGET,
        "preregistered_upper_bound_true_AC":EXPECTED_MAX_NATIVE_AC,
        "total_real_AC":sum(r["actual_native_AC_calls"] for r in rows),
        "full_censored_is_experimental_control_not_new_science":True,
        "previous_GAdapt_default_and_sequential_evaluator_unmodified":True,
        "environment":{
            "python":platform.python_version(),
            "numpy":np.__version__,
            "scipy":scipy.__version__,"pandas":pd.__version__,
        },
    },"runs":rows,"summary":summary,
      "paired_seed_contrasts":[
          paired_success_contrast(rows,"full_true","full_censored"),
          paired_success_contrast(rows,"full_censored","stop_fixed"),
          paired_success_contrast(rows,"stop_fixed","stop_adaptive"),
      ]}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default="iteration31_ablation.json")
    parser.add_argument("--csv",default="iteration31_ablation.csv")
    args=parser.parse_args()
    out=run_preregistered()
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(out,f,indent=2,sort_keys=True,allow_nan=False)
    flat=[{k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v)
          for k,v in record.items()} for record in out["runs"]]
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]))
        w.writeheader()
        w.writerows(flat)
    print("I31_SUMMARY",json.dumps(out["summary"],sort_keys=True,allow_nan=False),flush=True)
    print("I31_PAIRED",json.dumps(out["paired_seed_contrasts"],sort_keys=True,allow_nan=False),flush=True)
    print("I31_METADATA",json.dumps(out["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
