"""I36 frozen independent IEEE14 topology transfer of censor-safe operator credit.

Four same-score fixed-screen GAdapt arms, different ORIGINAL network from I35.
Synthetic IEEE14 three-load test already studied I32; NOT blind utility grid.
"""
import argparse
import csv
import json
import math
import platform
import random
import time
import numpy as np
import pandas as pd
import scipy
from gadapt.ga import GA
from gadapt.operations.cost_finding.sequential_scenario_budget_cost import SequentialScenarioBudgetCost
from research.iteration32_ieee14_topology_transfer import IEEE14OriginalSpatialLoad, SCENARIOS
from research.iteration34_censor_credit_geant import ObservedSequentialCost
from research.iteration33_geant_routing_budget import holm_adjust

METHODS=("legacy_fixed","ucb_objective_fixed",
         "uniform_censor_safe_fixed","ucb_censor_safe_fixed")
SEEDS=tuple(range(2500,2512))
BUDGET=180
POPULATION=12
MAX_REAL_AC=4*12*180

class IEEE14ActualNativeACBoundary:
    def __init__(self):
        self.grid=IEEE14OriginalSpatialLoad()
        self.bounds=self.grid.bounds
        self.n=self.grid.n
        if self.n!=9 or len(self.bounds)!=9:
            raise RuntimeError("I36 original IEEE14 9D controls drift")

    @property
    def real_routing_calls(self):
        # Compatibility alias for shared observation cache, THIS IS REAL PYPOWER AC.
        return self.grid.real_ac_calls

    def evaluate_scenario(self,x,scenario):
        return self.grid.evaluate_scenario(x,scenario)

class IEEE14SourceACObserved(ObservedSequentialCost):
    def __init__(self,source):
        self.route=source
        self._current=[]
        self.last=None
        SequentialScenarioBudgetCost.__init__(
            self,SCENARIOS,source.evaluate_scenario,
            physical_counter=lambda:source.real_routing_calls,
            budget=BUDGET,mode="stop_fixed",penalty=1e5)

def run_one(method,seed):
    if method not in METHODS or seed not in SEEDS:
        raise ValueError("I36 method/seed outside preregistration")
    random.seed(seed)
    np.random.seed(seed)
    source=IEEE14ActualNativeACBoundary()
    ev=IEEE14SourceACObserved(source)
    opt={}
    if method=="ucb_objective_fixed":
        opt=dict(mutation_operator_policy="ucb",mutation_operator_credit="objective")
    elif method in ("uniform_censor_safe_fixed","ucb_censor_safe_fixed"):
        opt=dict(
            mutation_operator_policy="uniform" if method.startswith("uniform") else "ucb",
            mutation_operator_credit="censored_verified_per_cost",
            mutation_scenario_count=3,
            mutation_evaluation_counter=lambda:source.real_routing_calls,
            mutation_violation_function=ev.censor_safe_cached_feedback)
    ga=GA(cost_function=ev,population_size=POPULATION,
          cost_diversity_metric="log_relative",
          population_mutation="cost_diversity,parent_diversity",
          exit_check="generations",number_of_generations=128,
          exit_function=lambda:ev.remaining<3,
          timeout=240,**opt)
    for lo,hi in source.bounds:
        ga.add(float(lo),float(hi))
    t=time.monotonic()
    success=False
    error=""
    result=None
    try:
        result=ga.execute()
        success=bool(result.success)
        if not success:error=str(result.messages)[:250]
    except Exception as exc:
        error=(type(exc).__name__+": "+str(exc))[:250]
    stats=getattr(result,"operator_credit_summary",[]) if result is not None else []
    q=ev.summary()
    physical=source.grid.real_ac_calls
    if (physical!=q["actual_native_AC_calls"] or physical>BUDGET
            or sum(q["actual_AC_per_scenario"])!=physical
            or q["verified_all_scenario_feasible_candidates"]>q["completely_evaluated_candidates"]):
        raise RuntimeError("I36 actual original IEEE14 AC and feasible count discrepancy")
    return dict(method=method,seed=seed,
        original_case="IEEE14 case14 14 bus, 5 generators; 4PG+5VG controlled",
        actual_evaluation_kind="genuine source PYPOWER NR AC (not GÉANT)",
        optimizer_success_not_source_feasible=success,
        error_or_stop_reason=error,elapsed_seconds=round(time.monotonic()-t,5),
        operator_credit_summary=stats,
        operator_selections=sum(a["selections"] for a in stats),
        operator_observations=sum(a["observations"] for a in stats),
        rewarded_operator_trials=sum(a["rewarded"] for a in stats),
        **q)

def paired(rows,a,b):
    aa={r["seed"]:bool(r["verified_all_scenario_feasible_candidates"])
        for r in rows if r["method"]==a}
    bb={r["seed"]:bool(r["verified_all_scenario_feasible_candidates"])
        for r in rows if r["method"]==b}
    if set(aa)!=set(SEEDS) or set(bb)!=set(SEEDS):
        raise RuntimeError("Incomplete I36 paired seeds")
    both=sum(aa[s] and bb[s] for s in SEEDS)
    aonly=sum(aa[s] and not bb[s] for s in SEEDS)
    bonly=sum(not aa[s] and bb[s] for s in SEEDS)
    neither=sum(not aa[s] and not bb[s] for s in SEEDS)
    n=aonly+bonly
    p=(min(1.,2*sum(math.comb(n,k) for k in range(min(aonly,bonly)+1))/2**n)
       if n else 1.)
    return dict(first=a,second=b,both=both,first_only=aonly,second_only=bonly,
                neither=neither,exact_two_sided_p_unadjusted=p)

def experiment():
    if (METHODS!=("legacy_fixed","ucb_objective_fixed",
                  "uniform_censor_safe_fixed","ucb_censor_safe_fixed")
            or SEEDS!=tuple(range(2500,2512))
            or SCENARIOS!=("nominal","odd_bus_plus1pct","even_bus_plus1pct")
            or BUDGET!=180 or POPULATION!=12 or MAX_REAL_AC!=8640):
        raise RuntimeError("I36 original frozen protocol drift")
    rows=[]
    for seed in SEEDS:
        for method in METHODS:
            r=run_one(method,seed)
            rows.append(r)
            print("I36_TRUE_AC",json.dumps(r,sort_keys=True,allow_nan=False),flush=True)
    if len(rows)!=48:raise RuntimeError("Missing I36 physical run")
    summary={}
    for method in METHODS:
        r=[v for v in rows if v["method"]==method]
        prices=[v["best_verified_robust_mean_economic_cost_or_null"] for v in r
                if v["best_verified_robust_mean_economic_cost_or_null"] is not None]
        summary[method]=dict(
            runs=len(r),true_source_robust_seed_success=len(prices),
            actual_original_native_AC=sum(v["actual_native_AC_calls"] for v in r),
            source_verified_all_three_candidates=sum(v["verified_all_scenario_feasible_candidates"] for v in r),
            truly_completed_three_source_scenarios=sum(v["completely_evaluated_candidates"] for v in r),
            physically_measured_early_failures=sum(v["early_screened_physically_infeasible_candidates"] for v in r),
            numerically_unknown_candidates=sum(v["numerically_unknown_candidates"] for v in r),
            unobserved_skipped_source_scenarios=sum(v["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"] for v in r),
            operator_selections=sum(v["operator_selections"] for v in r),
            operator_feedback_observations=sum(v["operator_observations"] for v in r),
            positive_operator_rewards=sum(v["rewarded_operator_trials"] for v in r),
            best_source_verified_mean_economic_cost_or_null=min(prices) if prices else None,
            median_cost_conditional_on_seed_success_or_null=float(np.median(prices)) if prices else None)
    comps=[("ucb_censor_safe_fixed","legacy_fixed"),
           ("ucb_censor_safe_fixed","ucb_objective_fixed"),
           ("ucb_censor_safe_fixed","uniform_censor_safe_fixed")]
    pvals=[paired(rows,*x) for x in comps]
    for row,adj in zip(pvals,holm_adjust([v["exact_two_sided_p_unadjusted"] for v in pvals])):
        row["holm_three_p_adjusted"]=adj
    return dict(metadata=dict(
        preregistration="research/ITERATION36_PROTOCOL.md",
        original_source="pypower.case14() original native source NR AC",
        source_limit_verification="all generator source PG/QG, BUS VMIN/VMAX, positive original RATE_A both ends and complex KCL",
        original_spatial_synthetic_load_profiles=list(SCENARIOS),
        already_known_IEEE14_topology_NOT_blind_test=True,
        methods=list(METHODS),seeds=list(SEEDS),
        true_AC_budget_per_run=BUDGET,max_registered_actual_AC=MAX_REAL_AC,
        actually_executed_native_PYPOWER_AC=sum(r["actual_native_AC_calls"] for r in rows),
        python=platform.python_version(),numpy=np.__version__,
        scipy=scipy.__version__,pandas=pd.__version__),
        runs=rows,summary=summary,paired_seed_contrasts=pvals)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",default="iteration36_ieee14_real_AC.json")
    p.add_argument("--csv",default="iteration36_ieee14_real_AC.csv")
    args=p.parse_args()
    out=experiment()
    with open(args.json,"w",encoding="utf8") as f:json.dump(out,f,sort_keys=True,indent=2,allow_nan=False)
    flat=[{k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v
           for k,v in row.items()} for row in out["runs"]]
    keys=list(dict.fromkeys(k for row in flat for k in row))
    with open(args.csv,"w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader();writer.writerows(flat)
    print("I36_SUMMARY",json.dumps(out["summary"],sort_keys=True,allow_nan=False),flush=True)
    print("I36_PAIRED",json.dumps(out["paired_seed_contrasts"],sort_keys=True,allow_nan=False),flush=True)
    print("I36_METADATA",json.dumps(out["metadata"],sort_keys=True,allow_nan=False),flush=True)

if __name__=="__main__":main()
