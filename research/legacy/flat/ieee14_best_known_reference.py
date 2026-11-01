"""Empirical IEEE14 best-known feasible control at higher solver budget.

No proof of global optimality. Different published reactive dispatch models
cannot be compared to this 5-voltage-only control setting.
"""
import argparse
import csv
import math
import random
import time
import numpy as np
from research.ieee14_voltage import IEEE14VoltageDispatch
from research.ieee14_local_refinement import PhysicalRecorder,run_slsqp,fill_remaining,PhysicalBudgetEnded
from scipy.optimize import differential_evolution


def run_one(load, budget=3600, first_stage=2000, seed=20261021):
    system=IEEE14VoltageDispatch(load)
    recorder=PhysicalRecorder(system,budget)
    random.seed(seed)
    np.random.seed(seed)
    started=time.perf_counter()
    recorder.stage_cap=first_stage
    stage_error=""
    try:
        differential_evolution(recorder.strict,system.bounds,
                               popsize=8,maxiter=math.ceil(first_stage/(8*system.n))+3,
                               tol=0,atol=0,polish=False,
                               rng=np.random.default_rng(seed))
    except PhysicalBudgetEnded:
        pass
    except Exception as exc:
        stage_error=str(exc)
    recorder.stage_cap=budget
    if recorder.best_feasible_vector is not None:
        start_vector=recorder.best_feasible_vector
    else:
        start_vector=recorder.start_point()
    warnings=run_slsqp(system,recorder,seed+1,start_vector)
    fill_remaining(system,recorder,seed+2)
    verified=None
    vector=recorder.best_feasible_vector
    if vector is not None:
        # ONE additional out-of-budget independent physical verification.
        verified=system.evaluate(vector)
        if not verified["converged"] or not verified["feasible"]:
            raise RuntimeError("Best-recorded feasible vector failed independent repeat solve")
        if not math.isclose(verified["loss"],recorder.best_feasible,
                            rel_tol=1e-8,abs_tol=1e-8):
            raise RuntimeError("Recheck loss inconsistent with recorded best")
    return dict(load_factor=load,seed=seed,search_evaluations=recorder.evaluations,
                extra_validation_pf_calls=1 if verified else 0,
                feasible=bool(verified is not None),
                independently_verified_MW=(verified["loss"] if verified else ""),
                best_penalized=recorder.best_penalized,
                verified_voltage_excess=verified["v_max"] if verified else "",
                verified_reactive_excess_MVAr=verified["q_max"] if verified else "",
                verified_branch_excess_MVA=verified["branch_max"] if verified else "",
                chosen_gen_VG_vector=(";".join(f"{v:.12f}" for v in vector) if vector else ""),
                attempts_after_budget=recorder.requests-recorder.evaluations,
                local_starts=recorder.slsqp_starts,
                local_termination_warnings=len(warnings),
                random_filler_evaluations=recorder.filler_evaluations,
                first_stage_error=stage_error,
                seconds=round(time.perf_counter()-started,4))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--budget",type=int,default=3600)
    p.add_argument("--de-stage",type=int,default=2000)
    p.add_argument("--seed",type=int,default=20261021)
    p.add_argument("--output",default="ieee14_best_known_reference.csv")
    args=p.parse_args()
    if not (args.budget>args.de_stage>=100):
        p.error("budget>de-stage>=100 required")
    results=[run_one(load,args.budget,args.de_stage,args.seed)
             for load in (1.0,1.1)]
    for r in results:print("AUDITED",r,flush=True)
    with open(args.output,"w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    if any(r["search_evaluations"]!=args.budget for r in results):
        raise RuntimeError("Physical reference search did not spend frozen budget")
    if any(not r["feasible"] for r in results):
        print("WARNING: no independently verified feasible control for some load",flush=True)
    print("DISCLAIMER: best-achieved upper bound for min loss, NOT an optimum certificate",flush=True)


if __name__=="__main__":
    main()
