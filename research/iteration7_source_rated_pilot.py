"""Iteration 7: preregistered tiny source-rated real AC GAdapt pilot (n=3).

This does NOT claim novelty for feasibility-first scalarization.
Five existing/experimental methods, 72 actual NR calls per paired method/seed,
full genuine GAdapt GA.execute() in a different source-rated RTE formulation.
See ITERATION7_PROTOCOL.md addendum C.
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np

from research.ieee118_allocation import (
    PhysicalGridRecorder, ga_stage, slsqp_stage,
    differential_evolution_stage, fill_actual_solver_budget
)
from research.iteration7_rte_source_physics import SourceRatedRTEGrid

METHODS=("gadapt_penalty","gadapt_feasibility_first",
         "slsqp_penalty","hybrid_fixed","scipy_de")


def run_one(method,seed,budget=72,population=12):
    if method not in METHODS:raise ValueError(method)
    if budget<4*population or population<8:
        raise ValueError("Need at least four GA population budgets")
    random.seed(seed)
    np.random.seed(seed)
    mode="feasibility_first" if method=="gadapt_feasibility_first" else "penalty"
    grid=SourceRatedRTEGrid(1.,scoring=mode)
    rec=PhysicalGridRecorder(grid,budget)
    started=time.perf_counter()
    controller=None
    ga_calls=0
    success=True
    error=""
    try:
        if method in ("gadapt_penalty","gadapt_feasibility_first"):
            success,error,controller=ga_stage(grid,rec,seed,population,"legacy")
            ga_calls=rec.calls
        elif method=="slsqp_penalty":
            slsqp_stage(grid,rec,seed,rec.local_start_point())
        elif method=="hybrid_fixed":
            success,error,controller=ga_stage(grid,rec,seed,population,"fixed")
            ga_calls=rec.calls
            rec.stage_cap=budget
            slsqp_stage(grid,rec,seed,rec.local_start_point())
        else:
            differential_evolution_stage(grid,rec,seed,population)
        fill_actual_solver_budget(grid,rec,seed)
    except Exception as exc:
        success=False
        error=(type(exc).__name__+": "+str(exc))[:300]
    physical=math.isfinite(rec.best_feasible)
    return {
        "case":"rte1888","formulation":"source_RATE_A_MVA_zero_unlimited",
        "load_factor":1.,"method":method,"seed":seed,
        "scoring":mode,"population":population,
        "dimension":grid.dimension,
        "budget":budget,"actual_ac_calls":rec.calls,
        "rejected_objective_requests":rec.requests-rec.calls,
        "nonconvergent_ac_calls":rec.failed_ac_calls,
        "physically_feasible":physical,
        "physically_feasible_evaluations":rec.physical_feasible_calls,
        "best_feasible_loss_mw":rec.best_feasible if physical else "",
        "min_observed_physical_violation":(
            rec.minimum_violation if math.isfinite(rec.minimum_violation) else ""),
        "best_objective_score":rec.best_penalized,
        "ga_physical_calls":ga_calls,
        "local_starts":rec.local_starts,
        "local_failed_terminations":rec.local_bad_exits,
        "random_filler_calls":rec.random_fills,
        "optimizer_completed":success,"error":error,
        "elapsed_sec":round(time.perf_counter()-started,3),
        "best_physical_feasible_voltages":(
            ";".join(f"{v:.10f}" for v in rec.best_feasible_vector)
            if rec.best_feasible_vector is not None else ""),
        "best_objective_candidate_voltages":(
            ";".join(f"{v:.10f}" for v in rec.best_penalized_vector)
            if rec.best_penalized_vector is not None else "")
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="rte1888_source_rated_pilot.csv")
    parser.add_argument("--seed-start",type=int,default=350)
    parser.add_argument("--seeds",type=int,default=3)
    parser.add_argument("--budget",type=int,default=72)
    parser.add_argument("--population",type=int,default=12)
    args=parser.parse_args()
    if (args.seeds<1 or args.budget<4*args.population or
        args.population<8):
        parser.error("Need at least one seed and at least four GA populations")
    rows=[]
    for seed in range(args.seed_start,args.seed_start+args.seeds):
        for method in METHODS:
            result=run_one(method,seed,args.budget,args.population)
            rows.append(result)
            print("PILOT_RUN",result,flush=True)
    with open(args.output,"w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for method in METHODS:
        group=[r for r in rows if r["method"]==method]
        vals=[r["min_observed_physical_violation"] for r in group
              if r["min_observed_physical_violation"] != ""]
        loss=[r["best_feasible_loss_mw"] for r in group
              if r["physically_feasible"]]
        print("PILOT_SUMMARY",method,
              "feasible_runs",len(loss),"of",len(group),
              "median_feasible_MW",statistics.median(loss) if loss else "NA",
              "median_min_violation",statistics.median(vals) if vals else "NA",
              "worst_min_violation",max(vals) if vals else "NA",
              "total_ac_calls",sum(r["actual_ac_calls"] for r in group),
              "total_nonconvergent",sum(r["nonconvergent_ac_calls"] for r in group),
              flush=True)
    expected=len(METHODS)*args.seeds
    if len(rows)!=expected or any(r["actual_ac_calls"]!=args.budget for r in rows):
        raise RuntimeError("Incomplete physical AC budget, preserve failure rows")
    if any(not r["optimizer_completed"] for r in rows):
        print("PILOT_WARNING: some algorithm stages did not complete; "
              "preserve all physical outcomes and investigate.",flush=True)
    print("PILOT_CAUTION: n=3 mechanistic pilot is not confirmatory inference.",flush=True)


if __name__=="__main__":
    main()
