"""I35 preregistered genuine IEEE118 source AC transfer of in-core I34 credit.

Four SAME early-fail GA selection-score conditions. 12 entirely new paired
seeds; original PYPOWER case118 source Q/P/V/positive RATE_A/KCL verification.
Not a new topology or real utility operation.
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
from research.iteration34_censor_credit_geant import ObservedSequentialCost
from research.iteration30_spatial_load_holdout import IEEE118SourceParityLoadScenario, SPATIAL_SCENARIOS
from research.iteration33_geant_routing_budget import holm_adjust

METHODS=("legacy_fixed","ucb_objective_fixed",
         "uniform_censor_safe_fixed","ucb_censor_safe_fixed")
SEEDS=tuple(range(2400,2412))
BUDGET=180
POPULATION=12
MAX_REAL_AC=len(METHODS)*len(SEEDS)*BUDGET


class IEEE118TrueACCounter:
    """Compatibility with read-only I34 event recorder. Calls are PYPOWER AC."""
    def __init__(self):
        self.grid=IEEE118SourceParityLoadScenario()
        self.bounds=self.grid.bounds
        self.n=self.grid.n
        if self.n!=6 or len(self.bounds)!=6:
            raise RuntimeError("Original IEEE118 six source generator-voltage controls changed")

    @property
    def real_routing_calls(self):
        # Name required by shared generic I34 cache; actually NATIVE AC CALLS.
        return self.grid.real_ac_calls

    def evaluate_scenario(self,vector,scenario):
        return self.grid.evaluate_scenario(vector,scenario)


class IEEE118ObservedSourceAC(ObservedSequentialCost):
    def __init__(self, true_source):
        self.route=true_source
        self._current=[]
        self.last=None
        SequentialScenarioBudgetCost.__init__(
            self,SPATIAL_SCENARIOS,true_source.evaluate_scenario,
            physical_counter=lambda:true_source.real_routing_calls,
            budget=BUDGET,mode="stop_fixed",penalty=1e5)


def run_one(method,seed):
    if method not in METHODS or seed not in SEEDS:
        raise ValueError("Unregistered I35 method/seed")
    random.seed(seed)
    np.random.seed(seed)
    source=IEEE118TrueACCounter()
    ev=IEEE118ObservedSourceAC(source)
    options={}
    if method=="ucb_objective_fixed":
        options=dict(mutation_operator_policy="ucb",mutation_operator_credit="objective")
    elif method in ("uniform_censor_safe_fixed","ucb_censor_safe_fixed"):
        options=dict(
            mutation_operator_policy="uniform" if method.startswith("uniform") else "ucb",
            mutation_operator_credit="censored_verified_per_cost",
            mutation_scenario_count=3,
            mutation_evaluation_counter=lambda:source.real_routing_calls,
            mutation_violation_function=ev.censor_safe_cached_feedback)
    ga=GA(cost_function=ev,population_size=POPULATION,
          cost_diversity_metric="log_relative",
          population_mutation="cost_diversity,parent_diversity",
          exit_check="generations",number_of_generations=128,
          exit_function=lambda:ev.remaining<3,timeout=240,**options)
    for lo,hi in source.bounds:
        ga.add(float(lo),float(hi))
    t=time.monotonic()
    optimizer_success=False
    exception=""
    result=None
    try:
        result=ga.execute()
        optimizer_success=bool(result.success)
        if not optimizer_success:
            exception=str(result.messages)[:250]
    except Exception as error:
        exception=(type(error).__name__+": "+str(error))[:250]
    stats=getattr(result,"operator_credit_summary",[]) if result is not None else []
    q=ev.summary()
    actual=source.grid.real_ac_calls
    if (actual!=q["actual_native_AC_calls"] or actual>BUDGET
            or sum(q["actual_AC_per_scenario"])!=actual
            or q["verified_all_scenario_feasible_candidates"]>q["completely_evaluated_candidates"]):
        raise RuntimeError("Native original source AC physics counter or feasibility invariant")
    return dict(method=method,seed=seed,
        source_case="Original IEEE118 case118, 54 source generators, six PV VG controls",
        true_solver="PYPOWER real Newton-Raphson AC, NOT networkx or GÉANT",
        optimizer_success_not_source_physical_feasibility=optimizer_success,
        optimizer_exception_or_stop=exception,
        wall_seconds=round(time.monotonic()-t,5),
        operator_credit_summary=stats,
        operator_selections=sum(a["selections"] for a in stats),
        operator_observations=sum(a["observations"] for a in stats),
        positively_rewarded_operator_trials=sum(a["rewarded"] for a in stats),
        **q)


def paired(rows,a,b):
    aa={r["seed"]:bool(r["verified_all_scenario_feasible_candidates"])
        for r in rows if r["method"]==a}
    bb={r["seed"]:bool(r["verified_all_scenario_feasible_candidates"])
        for r in rows if r["method"]==b}
    if set(aa)!=set(SEEDS) or set(bb)!=set(SEEDS):
        raise RuntimeError("Missing paired seed")
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
            or SEEDS!=tuple(range(2400,2412))
            or SPATIAL_SCENARIOS!=("nominal","odd_bus_heavier","even_bus_heavier")
            or BUDGET!=180 or POPULATION!=12 or MAX_REAL_AC!=8640):
        raise RuntimeError("I35 protocol changed")
    rows=[]
    for seed in SEEDS:
        for method in METHODS:
            r=run_one(method,seed)
            rows.append(r)
            print("I35_TRUE_AC",json.dumps(r,sort_keys=True,allow_nan=False),flush=True)
    if len(rows)!=48:
        raise RuntimeError("I35 missing source AC run")
    summary={}
    for method in METHODS:
        rr=[r for r in rows if r["method"]==method]
        costs=[r["best_verified_robust_mean_economic_cost_or_null"] for r in rr
               if r["best_verified_robust_mean_economic_cost_or_null"] is not None]
        summary[method]=dict(
            runs=len(rr),source_robust_seed_success=len(costs),
            actual_native_PYPOWER_AC=sum(r["actual_native_AC_calls"] for r in rr),
            verified_three_source_feasible_candidates=sum(
                r["verified_all_scenario_feasible_candidates"] for r in rr),
            complete_three_source_scenarios=sum(r["completely_evaluated_candidates"] for r in rr),
            measured_early_physical_source_failures=sum(
                r["early_screened_physically_infeasible_candidates"] for r in rr),
            numerically_unknown_candidates=sum(r["numerically_unknown_candidates"] for r in rr),
            never_run_source_scenarios=sum(
                r["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"] for r in rr),
            operator_selections=sum(r["operator_selections"] for r in rr),
            operator_feedback_observations=sum(r["operator_observations"] for r in rr),
            positive_operator_credits=sum(r["positively_rewarded_operator_trials"] for r in rr),
            best_truly_source_verified_original_mean_economic_cost_or_null=min(costs) if costs else None,
            median_source_economic_cost_conditional_success_or_null=(
                float(np.median(costs)) if costs else None))
    comparisons=[
        ("ucb_censor_safe_fixed","legacy_fixed"),
        ("ucb_censor_safe_fixed","ucb_objective_fixed"),
        ("ucb_censor_safe_fixed","uniform_censor_safe_fixed"),
    ]
    tests=[paired(rows,*names) for names in comparisons]
    adjusted=holm_adjust([x["exact_two_sided_p_unadjusted"] for x in tests])
    for item,p in zip(tests,adjusted):
        item["holm_three_p_adjusted"]=p
    return dict(metadata=dict(
            preregistration="research/ITERATION35_PROTOCOL.md",
            original_source="pypower.case118() original 54 generator 118 bus",
            original_source_constraints="individual PG,QG; bus VMIN/VMAX; positive RATE_A both ends; complex nodal KCL",
            source_scenarios=list(SPATIAL_SCENARIOS),
            previously_explored_original_IEEE118_NOT_independent_topology=True,
            methods=list(METHODS),seeds=list(SEEDS),
            true_AC_per_run_max=BUDGET,max_actual_native_AC=MAX_REAL_AC,
            total_actual_original_PYPOWER_native_AC=sum(r["actual_native_AC_calls"] for r in rows),
            Python=platform.python_version(),numpy=np.__version__,
            scipy=scipy.__version__,pandas=pd.__version__),
        runs=rows,summary=summary,paired_seed_contrasts=tests)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default="iteration35_ieee118_real_ac.json")
    parser.add_argument("--csv",default="iteration35_ieee118_real_ac.csv")
    args=parser.parse_args()
    result=experiment()
    with open(args.json,"w",encoding="utf8") as f:
        json.dump(result,f,sort_keys=True,indent=2,allow_nan=False)
    flat=[{k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v
           for k,v in row.items()} for row in result["runs"]]
    keys=list(dict.fromkeys(k for row in flat for k in row))
    with open(args.csv,"w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader()
        writer.writerows(flat)
    print("I35_SUMMARY",json.dumps(result["summary"],sort_keys=True,allow_nan=False),flush=True)
    print("I35_PAIRED",json.dumps(result["paired_seed_contrasts"],sort_keys=True,allow_nan=False),flush=True)
    print("I35_METADATA",json.dumps(result["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
