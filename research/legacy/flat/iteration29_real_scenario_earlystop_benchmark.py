"""I29: real original IEEE118 GA/DE benchmarking of metered scenario screening.

Pre-registered 5 methods x 4 new seeds; 180 true native PYPOWER AC PF max
per optimizer run. Full objective vs physically proven first-failure
screening, including adaptively ordered checks using ONLY prior PAID AC.
All variants share the existing unchanged 6D source generator VG physics.
This is an engineering feasibility-budget ablation, NOT algorithm novelty.
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
    SequentialScenarioBudgetCost,
)
from scipy.optimize import differential_evolution

from research.iteration27_real_scenario_credit_benchmark import (
    IEEE118SixSourcePVThreeScenarios,
    LOADS,CONTROL_BUS_GEN,
)

METHODS=(
    "gadapt_full",
    "gadapt_stop_fixed",
    "gadapt_stop_adaptive",
    "scipy_de_full",
    "scipy_de_stop_fixed",
)
SEEDS=(2060,2061,2062,2063)
BUDGET=180
POPULATION=12
EXPECTED_MAX_REAL_AC=len(METHODS)*len(SEEDS)*BUDGET


def method_mode(name):
    if name.endswith("_full"):
        return "full"
    if name.endswith("_stop_fixed"):
        return "stop_fixed"
    if name.endswith("_stop_adaptive"):
        return "stop_adaptive"
    raise ValueError("Unpreregistered simulator mode")


def one_run(method,seed,budget=BUDGET,population=POPULATION):
    if method not in METHODS or seed not in SEEDS or budget!=BUDGET or population!=POPULATION:
        raise ValueError("Preregistered I29 real physical simulator control drift")
    random.seed(seed)
    np.random.seed(seed)
    grid=IEEE118SixSourcePVThreeScenarios()
    fitness=SequentialScenarioBudgetCost(
        scenarios=LOADS,scenario_evaluator=grid.evaluate_scenario,
        physical_counter=lambda:grid.real_ac_calls,
        budget=budget,mode=method_mode(method),penalty=1e5)
    start=time.monotonic()
    optimizer_success=False
    error=""
    try:
        if method.startswith("gadapt_"):
            ga=GA(
                cost_function=fitness,
                population_size=population,
                cost_diversity_metric="log_relative",
                exit_check="generations",
                number_of_generations=128,
                exit_function=lambda:fitness.remaining<len(LOADS),
                population_mutation="cost_diversity,parent_diversity",
                timeout=240,
            )
            for lo,hi in grid.bounds:
                ga.add(float(lo),float(hi))
            result=ga.execute()
            optimizer_success=bool(result.success)
            error="" if optimizer_success else str(result.messages)[:250]
        else:
            result=differential_evolution(
                fitness,grid.bounds,popsize=5,
                maxiter=12,tol=0.,atol=0.,
                polish=False,seed=seed,updating="immediate")
            optimizer_success=bool(result.success)
            error="" if optimizer_success else str(result.message)[:250]
    except Exception as exc:
        optimizer_success=False
        error=(type(exc).__name__+": "+str(exc))[:350]
    info=fitness.summary()
    if info["actual_native_AC_calls"]!=grid.real_ac_calls:
        raise RuntimeError("Physical boundary and recorded AC diverged")
    if info["actual_native_AC_calls"]>budget or (
        sum(info["actual_AC_per_scenario"])!=info["actual_native_AC_calls"]):
        raise RuntimeError("Actual original IEEE source AC physical cap exceeded")
    if info["verified_all_scenario_feasible_candidates"]>info["completely_evaluated_candidates"]:
        raise RuntimeError("Physics false feasible inflation detected")
    return {
       "method":method,
       "seed":seed,
       "source_original_ieee118_synthetic_3load":True,
       "optimizer_reported_success":optimizer_success,
       "optimizer_error_or_stop_reason":error,
       "elapsed_seconds":round(time.monotonic()-start,5),
       **info,
    }


def run_preregistered():
    if (SEEDS!=(2060,2061,2062,2063) or len(METHODS)!=5 or
        LOADS!=(.98,1.,1.02) or EXPECTED_MAX_REAL_AC!=3600):
        raise RuntimeError("I29 fixed experiment mutated before physical evaluation")
    rows=[]
    for seed in SEEDS:
        for method in METHODS:
            x=one_run(method,seed)
            rows.append(x)
            print("I29_TRUE_AC",json.dumps(x,sort_keys=True,allow_nan=False),flush=True)
    if len(rows)!=20:
        raise RuntimeError("Missing a preregistered I29 optimizer run")
    summary={}
    for method in METHODS:
        matched=[x for x in rows if x["method"]==method]
        feasible=[x["best_verified_robust_mean_economic_cost_or_null"]
                 for x in matched
                 if x["best_verified_robust_mean_economic_cost_or_null"] is not None]
        summary[method]={
           "run_count":len(matched),
           "runs_with_proved_all_three_feasible":len(feasible),
           "true_native_AC_pf_calls":sum(x["actual_native_AC_calls"] for x in matched),
           "objective_requests":sum(x["objective_requests"] for x in matched),
           "fully_measured_three_scenario_candidates":sum(x["completely_evaluated_candidates"] for x in matched),
           "proven_physically_infeasible_censored_candidates":sum(x["early_screened_physically_infeasible_candidates"] for x in matched),
           "physically_unknown_nr_fail_candidates":sum(x["numerically_unknown_candidates"] for x in matched),
           "actually_verified_robust_feasible_candidates":sum(x["verified_all_scenario_feasible_candidates"] for x in matched),
           "total_source_scenarios_never_executed":sum(x["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"] for x in matched),
           "actual_AC_by_original_load_scenario":[sum(x["actual_AC_per_scenario"][i] for x in matched)
                  for i in range(3)],
           "best_truly_verified_robust_mean_original_cost_or_null":min(feasible) if feasible else None,
           "median_truly_verified_robust_cost_conditional_only":statistics.median(feasible) if feasible else None,
           "same_fixed_true_AC_cap_per_run_not_equal_number_of_genomes":True,
        }
    return {"metadata":{
       "protocol":"research/ITERATION29_PROTOCOL.md",
       "original_source_solver":"PYPOWER native case118, same source physics I27",
       "original_generator_control_buses":[bus for bus,_ in CONTROL_BUS_GEN],
       "synthetic_original_load_factors":list(LOADS),
       "same_physical_source_PG_QG_VM_positive_RATE_A_KCL":True,
       "new_seed_list":list(SEEDS),
       "methods":list(METHODS),
       "true_native_AC_budget_per_run":BUDGET,
       "predefined_max_native_AC":EXPECTED_MAX_REAL_AC,
       "true_actual_native_AC_total":sum(x["actual_native_AC_calls"] for x in rows),
       "numeric_GA_reward_model_UNCHANGED_from_I27":True,
       "early_screening_is_known_prior_art_not_a_novelty_claim":True,
       "scenarios_skipped_without_free_simulations":True,
       "is_in_sample_calibrated_public_grid_not_field_data":True,
       "new_ac_opf_calls":0,
       "environment":{"python":platform.python_version(),
                      "scipy":scipy.__version__,
                      "pandas":pd.__version__},
    },"runs":rows,"summary":summary}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",default="iteration29_budget_earlystop.json")
    p.add_argument("--csv",default="iteration29_budget_earlystop.csv")
    a=p.parse_args()
    out=run_preregistered()
    with open(a.json,"w",encoding="utf-8") as f:
        json.dump(out,f,indent=2,sort_keys=True,allow_nan=False)
    flat=[{k:(json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v)
           for k,v in rec.items()} for rec in out["runs"]]
    with open(a.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]))
        w.writeheader()
        w.writerows(flat)
    print("I29_SUMMARY",json.dumps(out["summary"],sort_keys=True,allow_nan=False),flush=True)
    print("I29_METADATA",json.dumps(out["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
