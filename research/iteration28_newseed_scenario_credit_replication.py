"""Iteration 28: STRICTLY pre-registered new-seed holdout, zero algorithm tuning.

Uses exact already-executed I27 IEEE118 6-VG, three real source-load AC
evaluator and GA UCB modes WITHOUT modification. Every actual physical
scenario is charged at the PYPOWER NR boundary by the imported recorder.

12 NEW seeds x 4 GA options x max 180 real AC = max 8640 real AC.
This checks stochastic replication on the SAME physical scenario task,
not transfer to an independent network, or proof of scientific novelty.
"""
import csv
import json
import math
import platform
import statistics

import pandas as pd
import scipy

from research.iteration27_real_scenario_credit_benchmark import (
    run_method,
    IEEE118SixSourcePVThreeScenarios,
    LOADS,
    PHYSICAL_SCENARIOS,
)

SEEDS=tuple(range(2040,2052))
METHODS=(
    "gadapt_legacy",
    "gadapt_ucb_objective",
    "gadapt_ucb_scalar_feasibility",
    "gadapt_ucb_scenario_feasibility",
)
BUDGET=180
POPULATION=12
EXPECTED_REAL_AC_UPPER_BOUND=len(SEEDS)*len(METHODS)*BUDGET
HISTORICAL_I27_SEEDS=(2026,2027,2028)


def wilson_95(success,n):
    """Descriptive marginal Wilson interval, NOT paired A-vs-B inference."""
    if not 0<=success<=n or n<1:
        raise ValueError("Invalid binomial success count")
    z=1.959963984540054
    z2=z*z
    denom=1.+z2/n
    p=success/n
    center=(p+z2/(2*n))/denom
    radius=z*math.sqrt(p*(1.-p)/n+z2/(4*n*n))/denom
    return [max(0.,center-radius),min(1.,center+radius)]


def summarize(rows):
    """Summarize every pair, including zero feasibility and negative results."""
    if len(rows)!=len(SEEDS)*len(METHODS):
        raise ValueError("Missing or duplicated preregistered run rows")
    pair={(int(r["seed"]),r["method"]):r for r in rows}
    if len(pair)!=len(SEEDS)*len(METHODS) or set(pair)!={
        (s,m) for s in SEEDS for m in METHODS}:
        raise ValueError("Missing, duplicate, or unpreregistered run")
    table={}
    success={}
    new="gadapt_ucb_scenario_feasibility"
    for method in METHODS:
        subset=[pair[s,method] for s in SEEDS]
        met=[r["best_all_three_feasible_mean_original_economic_cost"]
             for r in subset if r["best_all_three_feasible_mean_original_economic_cost"] is not None]
        k=sum(r["all_three_original_source_feasible_batches"]>0 for r in subset)
        success[method]={s:pair[s,method]["all_three_original_source_feasible_batches"]>0
                         for s in SEEDS}
        table[method]={
           "runs":len(subset),
           "runs_with_at_least_one_all_three_feasible":k,
           "run_success_fraction":k/len(SEEDS),
           "descriptive_marginal_wilson_95":wilson_95(k,len(SEEDS)),
           "all_three_feasible_complete_batches":sum(
               r["all_three_original_source_feasible_batches"] for r in subset),
           "sum_true_actual_native_AC_pf_calls":sum(r["true_real_ac_pf_calls"] for r in subset),
           "sum_true_three_scenario_complete_batches":sum(
               r["complete_three_source_scenario_batches"] for r in subset),
           "sum_numerically_failed_real_AC":sum(r["failed_real_ac_nr_calls"] for r in subset),
           "all_three_feasible_mean_cost_best_or_null":min(met) if met else None,
           "all_three_feasible_run_cost_median_conditional_only":statistics.median(met) if met else None,
           "per_scenario_feasible_completed_batches":[sum(
               r["per_load_source_feasible_batch_counts"][j] for r in subset)
               for j in range(PHYSICAL_SCENARIOS)],
           "not_independent_grid_problems":True,
        }
    discordance={}
    for control in METHODS:
        if control==new:continue
        yes_no=sum(success[new][s] and not success[control][s] for s in SEEDS)
        no_yes=sum(not success[new][s] and success[control][s] for s in SEEDS)
        both_yes=sum(success[new][s] and success[control][s] for s in SEEDS)
        both_no=sum(not success[new][s] and not success[control][s] for s in SEEDS)
        discordance[control]={
            "new_yes_control_no":yes_no,
            "new_no_control_yes":no_yes,
            "both_yes":both_yes,
            "both_no":both_no,
            "n_matched_seeds":len(SEEDS)
        }
        if sum(discordance[control][k] for k in ("new_yes_control_no","new_no_control_yes","both_yes","both_no"))!=len(SEEDS):
            raise RuntimeError("Invalid actual-paired 12-seed cross-tab")
    return table,discordance


def execute_fixed_replication():
    if SEEDS!=(2040,2041,2042,2043,2044,2045,2046,2047,2048,2049,2050,2051):
        raise RuntimeError("Seed holdout set must not be tuned after preregistration")
    if set(SEEDS).intersection(HISTORICAL_I27_SEEDS):
        raise RuntimeError("I28 seeds overlap pilot I27")
    if PHYSICAL_SCENARIOS!=3 or LOADS!=(.98,1.0,1.02):
        raise RuntimeError("Frozen underlying original IEEE118 load physics changed")
    rows=[]
    for seed in SEEDS:
        for method in METHODS:
            row=run_method(method,seed,BUDGET,POPULATION)
            if row["method"]!=method or row["seed"]!=seed:
                raise RuntimeError("Wrong source GA method/seed identity")
            if (row["true_real_ac_pf_calls"]>BUDGET or
                row["true_real_ac_pf_calls"]%PHYSICAL_SCENARIOS!=0 or
                row["true_real_ac_pf_calls"]!=PHYSICAL_SCENARIOS*
                   row["complete_three_source_scenario_batches"]):
                raise RuntimeError("GAdapt original IEEE source real AC counter corrupted")
            rows.append(row)
            print("I28_NEWSEED_REAL_AC",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    table,paired=summarize(rows)
    physical_probe=IEEE118SixSourcePVThreeScenarios()
    output={"metadata":{
       "protocol":"research/ITERATION28_PROTOCOL.md",
       "unmodified_i27_physical_implementation":"research/iteration27_real_scenario_credit_benchmark.py",
       "strictly_new_seed_holdout_not_new_scenario_holdout":True,
       "original_public_ieee118_in_sample_physical_problem":True,
       "synthetic_source_load_factors":list(LOADS),
       "original_source_generator_bus_ids":[103,32,34,92,19,74],
       "same_frozen_original_source_PQ_V_RateA_KCL_constraints":True,
       "preregistered_new_seed_list":list(SEEDS),
       "historical_i27_seed_list":list(HISTORICAL_I27_SEEDS),
       "preregistered_method_list":list(METHODS),
       "max_real_native_ac_pf_per_seed_method":BUDGET,
       "real_native_ac_per_full_fitness":PHYSICAL_SCENARIOS,
       "max_total_preregistered_real_AC":EXPECTED_REAL_AC_UPPER_BOUND,
       "actual_total_real_AC":sum(r["true_real_ac_pf_calls"] for r in rows),
       "total_optimizers_executed":len(rows),
       "new_source_AC_OPF_calls":0,
       "source_chosen_by_earlier_IEEE_Q_diagnostics":True,
       "operator_selection_causal_effect_not_established":True,
       "scientific_novelty_not_established":True,
       "environment":{"python":platform.python_version(),
                      "scipy":scipy.__version__,
                      "pandas":pd.__version__},
       "preflight_0_real_AC":physical_probe.real_ac_calls,
    },"runs":rows,"summary":table,"new_vs_old_paired_binary":paired}
    print("I28_SUMMARY",json.dumps(table,sort_keys=True,allow_nan=False),flush=True)
    print("I28_PAIRED",json.dumps(paired,sort_keys=True,allow_nan=False),flush=True)
    print("I28_METADATA",json.dumps(output["metadata"],sort_keys=True,allow_nan=False),flush=True)
    return output


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default="iteration28_seed_holdout.json")
    parser.add_argument("--csv",default="iteration28_seed_holdout.csv")
    args=parser.parse_args()
    out=execute_fixed_replication()
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(out,f,indent=2,sort_keys=True,allow_nan=False)
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        flat=[{k:(json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v)
             for k,v in row.items()} for row in out["runs"]]
        w=csv.DictWriter(f,fieldnames=list(flat[0]))
        w.writeheader()
        w.writerows(flat)


if __name__=="__main__":
    main()
