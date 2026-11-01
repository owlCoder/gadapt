"""Predeclared repeat-use GÉANT chronological paired mutation-credit pilot.

The 32 August evaluation matrices have ALREADY been inspected in iteration 3.
They are not pristine or independent; all conclusions here are exploratory.
Run: python -m research.paired_credit_geant --runs 8 --budget 240
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np
from scipy.optimize import differential_evolution
from gadapt.ga import GA
from research.aos_geant_temporal import (
    GeantCapacity, ChronologicalCapacity, archived_traffic,
    TRAIN_STAMPS, TEST_STAMPS, SHA256
)
from research.aos_geant_temporal import Recorder

METHODS = ("legacy","legacy_single","uniform_offspring","ucb_offspring",
           "uniform_paired","ucb_paired","scipy_de")


def run(train, test, combined, method, seed, budget=240, population=36):
    random.seed(seed)
    np.random.seed(seed)
    recorder=Recorder(train,budget)
    started=time.perf_counter()
    success=True
    error=""
    telemetry=[]
    if method=="scipy_de":
        try:
            differential_evolution(recorder,train.bounds,
                                   popsize=1,maxiter=math.ceil(budget/train.n)+2,
                                   integrality=[True]*train.n,tol=0,atol=0,polish=False,
                                   rng=np.random.default_rng(seed))
        except Exception as exc:
            success,error=False,str(exc)
    else:
        paired="paired" in method
        options={"cost_diversity_metric":("log_relative" if method=="legacy"
                                           else "affine_invariant")}
        if method!="legacy":
            options.update(ensure_unique_individuals=False,
                           number_of_mutation_decision_variables=1,
                           candidate_solution_mutation="random")
        if method not in ("legacy","legacy_single"):
            options.update(mutation_operator_policy=(
                               "uniform" if method.startswith("uniform") else "ucb"),
                           mutation_operator_credit="objective",
                           mutation_credit_assignment=("paired" if paired else "offspring"))
            if paired:
                options["mutation_evaluation_counter"]=lambda:recorder.evaluations
        ga=GA(cost_function=recorder,population_size=population,
              number_of_generations=math.ceil(4*budget/population)+12,
              exit_check="generations",
              exit_function=lambda: recorder.evaluations>=budget,
              population_mutation="cost_diversity,parent_diversity",
              timeout=240,**options)
        for low,high in train.bounds:
            ga.add(low,high,1.0)
        try:
            result=ga.execute()
            success=bool(result.success)
            error=result.message if not success else ""
            telemetry=getattr(result,"operator_credit_summary",[])
        except Exception as exc:
            success,error=False,str(exc)
    if recorder.vector is None:
        success=False
        error=error or "No physical design evaluated"
        test_score=all_score=float("nan")
    else:
        try:
            test_score=float(test.evaluate(recorder.vector)["cost"])
            all_score=float(combined.evaluate(recorder.vector)["cost"])
        except Exception as exc:
            success,error=False,str(exc)
            test_score=all_score=float("nan")
    return dict(method=method,seed=seed,success=success,error=error,
                development_cost=recorder.best,
                august_32_cost=test_score,all_44_cost=all_score,
                objective_evaluations=recorder.evaluations,
                objective_requests=recorder.requests,
                paired_physical_baselines=(telemetry[0].get("paired_physical_baselines",0)
                                            if telemetry else 0),
                incomplete_pairs=(telemetry[0].get("paired_incomplete_trials",0)
                                    if telemetry else 0),
                operator_observations=sum(o["observations"] for o in telemetry),
                seconds=round(time.perf_counter()-started,4),
                chosen_weights=("-".join(map(str,recorder.vector))
                                 if recorder.vector is not None else ""))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--runs",type=int,default=8)
    parser.add_argument("--budget",type=int,default=240)
    parser.add_argument("--population",type=int,default=36)
    parser.add_argument("--output",default="paired_geant.csv")
    args=parser.parse_args()
    if args.runs<1 or args.budget<args.population:
        parser.error("runs>=1 and budget>=population required")
    base=GeantCapacity.download()
    snapshots=archived_traffic()
    peak=sum(d for _,_,d in base.demands)
    training_max=max(sum(d for _,_,d in snapshots[t]) for t in TRAIN_STAMPS)
    factor=peak/training_max
    scaled={t:[(a,b,d*factor) for a,b,d in raw]
            for t,raw in snapshots.items()}
    training=ChronologicalCapacity(base,{t:scaled[t] for t in TRAIN_STAMPS})
    testing=ChronologicalCapacity(base,{t:scaled[t] for t in TEST_STAMPS})
    all_periods=ChronologicalCapacity(base,scaled)
    print("PROVENANCE",SHA256,"network",base.data_sha256,
          "scaling_training_only",factor,
          "train",len(TRAIN_STAMPS),"reused_august_test",len(TEST_STAMPS),flush=True)
    rows=[]
    for seed in range(args.runs):
        for method in METHODS:
            row=run(training,testing,all_periods,method,seed,args.budget,args.population)
            rows.append(row)
            print("RUN",row,flush=True)
    with open(args.output,"w",newline="",encoding="utf-8") as dest:
        writer=csv.DictWriter(dest,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for method in METHODS:
        group=[r for r in rows if r["method"]==method]
        ok=[r for r in group if r["success"]]
        print("SUMMARY",method,"successful",len(ok),"/",len(group),
              "median_all_44",statistics.median(r["all_44_cost"] for r in ok) if ok else "NA",
              "median_aug_32",statistics.median(r["august_32_cost"] for r in ok) if ok else "NA",
              "worst_all_44",max(r["all_44_cost"] for r in ok) if ok else "NA",
              "median_seconds",statistics.median(r["seconds"] for r in group),
              flush=True)
    if any(r["objective_evaluations"]!=args.budget for r in rows):
        print("WARNING: unequal PHYSICAL training budgets",flush=True)
    if any(not r["success"] for r in rows):
        print("WARNING: failure rows counted in success",flush=True)


if __name__=="__main__":
    main()
