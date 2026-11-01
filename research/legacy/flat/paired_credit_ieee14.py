"""Physically counted paired-vs-unpaired AOS on the ACTUAL GAdapt package.

Run as: python -m research.paired_credit_ieee14 --runs 8 --budget 240
Protocol MUST be read before inspecting outcomes: PAIRED_CREDIT_PROTOCOL.md.
This is a public reference AC case, not production utility measurements.
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np
from gadapt.ga import GA
from scipy.optimize import differential_evolution
from research.aos_ieee14_pilot import IEEE14VoltageDispatch, AccountedObjective


METHODS = ("legacy", "legacy_single", "uniform_offspring", "ucb_offspring",
           "uniform_paired", "ucb_paired", "ucb_paired_feasibility", "scipy_de")


def run(system, method, seed, budget=240, population=24):
    random.seed(seed)
    np.random.seed(seed)
    monitor = AccountedObjective(system, budget)
    started = time.perf_counter()
    success, error, stats = True, "", []
    if method == "scipy_de":
        factor = max(5, math.ceil(population / system.n))
        try:
            differential_evolution(
                monitor, system.bounds, popsize=factor,
                maxiter=math.ceil(budget/(factor*system.n)) + 2,
                tol=0, atol=0, polish=False, rng=np.random.default_rng(seed))
        except Exception as exc:
            success, error = False, str(exc)
    else:
        paired = "paired" in method
        constrained_mutation = method != "legacy"
        options = {
            "cost_diversity_metric": ("log_relative" if method == "legacy"
                                      else "affine_invariant"),
        }
        if constrained_mutation:
            options.update(ensure_unique_individuals=False,
                           number_of_mutation_decision_variables=1,
                           candidate_solution_mutation="random")
        if method not in ("legacy", "legacy_single"):
            options.update(
                mutation_operator_policy=(
                    "uniform" if method.startswith("uniform") else "ucb"
                ),
                mutation_operator_credit=(
                    "feasibility" if method.endswith("feasibility") else "objective"
                ),
                mutation_credit_assignment=("paired" if paired else "offspring"),
            )
            if paired:
                options["mutation_evaluation_counter"] = lambda: monitor.evaluations
            if method.endswith("feasibility"):
                options["mutation_violation_function"] = monitor.violation
        optimizer = GA(
            cost_function=monitor,
            population_size=population,
            exit_check="generations",
            exit_function=lambda: monitor.evaluations >= budget,
            number_of_generations=math.ceil(4*budget/population)+12,
            population_mutation="cost_diversity,parent_diversity",
            timeout=240,
            **options,
        )
        for lower, upper in system.bounds:
            optimizer.add(lower, upper)
        try:
            result = optimizer.execute()
            success = bool(result.success)
            error = result.message if not success else ""
            stats = getattr(result, "operator_credit_summary", [])
        except Exception as exc:
            success, error = False, str(exc)
    return {
        "method":method,
        "load_factor":system.load_factor,
        "seed":seed,
        "success":success,
        "error":error,
        "feasible":bool(math.isfinite(monitor.best_feasible)),
        "best_feasible_MW":(monitor.best_feasible if math.isfinite(monitor.best_feasible) else ""),
        "best_penalized":monitor.best_penalized,
        "objective_evaluations":monitor.evaluations,
        "objective_requests":monitor.requests,
        "physical_violation_reads":monitor.feedback_reads,
        "unmatched_violation_reads":monitor.feedback_misses,
        "feasible_evaluations":monitor.feasible_evaluations,
        "pf_failures":monitor.pf_failures,
        "operator_selections":sum(x["selections"] for x in stats),
        "operator_observations":sum(x["observations"] for x in stats),
        "paired_baseline_evaluations":(
            stats[0].get("paired_physical_baselines",0) if stats else 0
        ),
        "paired_incomplete_trials":(
            stats[0].get("paired_incomplete_trials",0) if stats else 0
        ),
        "seconds":round(time.perf_counter()-started,4),
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--runs",type=int,default=8)
    parser.add_argument("--budget",type=int,default=240)
    parser.add_argument("--population",type=int,default=24)
    parser.add_argument("--loads",nargs="+",type=float,default=[1.,1.1])
    parser.add_argument("--output",default="paired_ieee14.csv")
    args=parser.parse_args()
    if args.runs<1 or args.budget<args.population:
        parser.error("runs>=1, budget>=population required")
    rows=[]
    for factor in args.loads:
        system=IEEE14VoltageDispatch(factor)
        for seed in range(args.runs):
            for method in METHODS:
                row=run(system,method,seed,args.budget,args.population)
                rows.append(row)
                print("RUN",row,flush=True)
        for method in METHODS:
            group=[r for r in rows if r["load_factor"]==factor and r["method"]==method]
            feasible=[r["best_feasible_MW"] for r in group if r["feasible"] and r["success"]]
            print("SUMMARY",factor,method,"feasible",len(feasible),"/",len(group),
                  "median_feasible_MW",statistics.median(feasible) if feasible else "NA",
                  "median_seconds",statistics.median(r["seconds"] for r in group),
                  "median_pair_probes",statistics.median(r["paired_baseline_evaluations"] for r in group),
                  flush=True)
    with open(args.output,"w",newline="",encoding="utf-8") as src:
        writer=csv.DictWriter(src,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if any(r["objective_evaluations"]!=args.budget for r in rows):
        print("WARNING: physical evaluation budgets differ",flush=True)
    if any(not r["success"] for r in rows):
        print("WARNING: optimizer errors retained in raw CSV; no success-only inference",flush=True)


if __name__=="__main__":
    main()
