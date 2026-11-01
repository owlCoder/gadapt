"""CMA-ES ask/tell independent baseline, equal 360 true IEEE14 AC-PF solves.

Public pycma package. Protocol preregistered in ITERATION5_PROTOCOL.md.
No global optimality claim and NO comparisons to nonidentical ORPD models.
"""
import argparse
import csv
import math
import statistics
import time
import numpy as np
from pypower.idx_gen import VG
from research.ieee14_voltage import IEEE14VoltageDispatch
from research.ieee14_local_refinement import PhysicalRecorder

def run(system,seed,budget=360):
    import cma
    recorder=PhysicalRecorder(system,budget)
    rng=np.random.default_rng(seed+71011)
    lo,hi=np.asarray(system.bounds,dtype=float).T
    initial=np.clip(np.array(system.base["gen"][:,VG]),lo+1e-6,hi-1e-6)
    t0=time.perf_counter()
    restart=0
    rounds=0
    errors=[]
    while recorder.evaluations<budget:
        if restart:
            initial=(recorder.best_penalized_vector if
                     recorder.best_penalized_vector is not None else
                     rng.uniform(lo,hi))
            initial=np.clip(np.asarray(initial),lo+1e-6,hi-1e-6)
        opts=dict(bounds=[lo.tolist(),hi.tolist()],seed=seed+17*restart,
                  popsize=8,verbose=-9,verb_log=0,verb_disp=0)
        try:
            es=cma.CMAEvolutionStrategy(initial.tolist(),0.035,opts)
        except Exception as exc:
            errors.append("initialization: "+str(exc))
            break
        while not es.stop() and recorder.evaluations<budget:
            solutions=es.ask()
            scores=[]
            evaluated=[]
            for x in solutions:
                if recorder.evaluations>=budget:break
                score=recorder(x)
                scores.append(float(score))
                evaluated.append(x)
            if len(evaluated)==len(solutions):
                try:
                    es.tell(evaluated,scores)
                except Exception as exc:
                    errors.append("tell: "+str(exc))
                    break
                rounds+=1
            else:
                # Partial terminal batch was genuinely evaluated, but cannot
                # be used in CMA ask/tell. No extra simulated objective calls.
                break
        restart+=1
        if restart>=20:break
    # If CMA early-terminated or errored, not hide unused physical budget.
    while recorder.evaluations<budget:
        recorder(rng.uniform(lo,hi))
        recorder.filler_evaluations+=1
    return dict(method="cma_es",load_factor=system.load_factor,seed=seed,
                optimizer_success=not bool(errors),error="; ".join(errors),
                physical_feasible=bool(math.isfinite(recorder.best_feasible)),
                feasible_loss_MW=(recorder.best_feasible if
                                  math.isfinite(recorder.best_feasible) else ""),
                best_penalized=recorder.best_penalized,
                true_pf_evaluations=recorder.evaluations,
                all_objective_requests=recorder.requests,
                feasible_physical_evaluations=recorder.feasible_count,
                pf_convergence_failures=recorder.pf_failures,
                cma_restarts=restart,cma_full_generations=rounds,
                random_budget_fill_evaluations=recorder.filler_evaluations,
                seconds=round(time.perf_counter()-t0,4),
                best_feasible_vector=("-".join(f"{v:.11g}" for v in
                    recorder.best_feasible_vector) if
                    recorder.best_feasible_vector is not None else ""))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seeds",type=int,default=12)
    p.add_argument("--seed-start",type=int,default=100)
    p.add_argument("--budget",type=int,default=360)
    p.add_argument("--output",default="ieee14_cma_es.csv")
    args=p.parse_args()
    rows=[]
    for factor in (1.,1.1):
        grid=IEEE14VoltageDispatch(factor)
        for seed in range(args.seed_start,args.seed_start+args.seeds):
            r=run(grid,seed,args.budget)
            rows.append(r)
            print("RUN",r,flush=True)
        vals=[r for r in rows if r["load_factor"]==factor]
        feas=[r["feasible_loss_MW"] for r in vals if r["physical_feasible"]]
        print("SUMMARY",factor,"feasible",len(feas),"/",len(vals),
              "median_loss_MW",statistics.median(feas) if feas else "NA",
              "worst_feasible_MW",max(feas) if feas else "NA",
              "median_seconds",statistics.median(r["seconds"] for r in vals),flush=True)
    with open(args.output,"w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if any(r["true_pf_evaluations"]!=args.budget for r in rows):
        raise ValueError("Unmatched physical PF solver budget")


if __name__=="__main__":
    main()
