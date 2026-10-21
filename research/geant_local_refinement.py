"""Cross-domain strict budget GAdapt + discrete route-weight hill climbing.

The GÉANT block repeats previously inspected historical snapshots. It is
NOT an independent industrial validation. Frozen protocol ITERATION5_PROTOCOL.
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
from research.aos_geant_temporal import (
    GeantCapacity, ChronologicalCapacity, archived_traffic,
    TRAIN_STAMPS, TEST_STAMPS, SHA256,
)
from research.aos_geant_temporal import Recorder

METHODS=("legacy_gadapt","coordinate_multistart","hybrid_gadapt_coordinate","scipy_de")


class BudgetEnded(Exception):
    pass


class StageRecorder(Recorder):
    def __init__(self, problem, budget):
        super().__init__(problem,budget)
        self.stage_cap=budget
        self.postbudget=0
        self.local_calls=0
        self.local_restarts=0
        self.filler_calls=0

    def __call__(self,x):
        if self.evaluations >= min(self.stage_cap,self.budget):
            self.requests += 1
            self.postbudget += 1
            return 1e12
        return super().__call__(x)

    def strict(self,x):
        if self.evaluations >= min(self.stage_cap,self.budget):
            self.requests += 1
            self.postbudget += 1
            raise BudgetEnded()
        return self(x)


def ga_stage(train, recorder, seed, population):
    random.seed(seed)
    np.random.seed(seed)
    model=GA(cost_function=recorder,population_size=population,
             exit_check="generations",
             exit_function=lambda: recorder.evaluations>=recorder.stage_cap,
             number_of_generations=math.ceil(5*recorder.stage_cap/population)+12,
             population_mutation="cost_diversity,parent_diversity",
             timeout=240)
    for lo,hi in train.bounds:model.add(lo,hi,1.0)
    result=model.execute()
    return bool(result.success),str(result.message) if not result.success else ""


def local_stage(train,recorder,seed,warm_start):
    rng=np.random.default_rng(seed+137)
    lo,hi=np.array(train.bounds,dtype=int).T
    if warm_start is None:
        cur=rng.integers(lo,hi+1)
        current_cost=recorder.strict(cur)
    else:
        cur=np.clip(np.asarray(warm_start,dtype=int),lo,hi)
        if recorder.vector is None:
            current_cost=recorder.strict(cur)
        else:
            current_cost=float(recorder.best)
    fails=0
    while recorder.evaluations<recorder.stage_cap:
        idx=int(rng.integers(0,train.n))
        steps=(-8,-4,-2,-1,1,2,4,8)
        new=cur.copy()
        new[idx]=np.clip(new[idx]+int(rng.choice(steps)),lo[idx],hi[idx])
        if np.array_equal(new,cur):
            continue  # no physical evaluation, no credit
        cost=recorder.strict(new)
        recorder.local_calls+=1
        if cost<current_cost:
            cur=new
            current_cost=cost
            fails=0
        else:
            fails+=1
        if fails>=3*train.n:
            recorder.local_restarts+=1
            if recorder.vector is not None and recorder.local_restarts%2:
                cur=np.array(recorder.vector,dtype=int)
                pick=rng.choice(train.n,size=min(5,train.n),replace=False)
                for i in pick:
                    cur[i]=np.clip(cur[i]+int(rng.choice(steps)),lo[i],hi[i])
            else:
                cur=rng.integers(lo,hi+1)
            # Start new basin with a truly counted observation, not a
            # potentially optimistic score from an unrelated chromosome.
            if recorder.evaluations>=recorder.stage_cap:break
            current_cost=recorder.strict(cur)
            recorder.local_calls+=1
            fails=0


def run(train,heldout,all_periods,method,seed,budget,population):
    random.seed(seed)
    np.random.seed(seed)
    score=StageRecorder(train,budget)
    begin=time.perf_counter()
    success,error=True,""
    try:
        if method=="legacy_gadapt":
            success,error=ga_stage(train,score,seed,population)
        elif method=="coordinate_multistart":
            local_stage(train,score,seed,None)
        elif method=="hybrid_gadapt_coordinate":
            score.stage_cap=budget//2
            success,error=ga_stage(train,score,seed,population)
            first=score.vector
            score.stage_cap=budget
            local_stage(train,score,seed,first)
        elif method=="scipy_de":
            try:
                differential_evolution(
                    score.strict,train.bounds,popsize=1,
                    maxiter=math.ceil(budget/train.n)+3,
                    integrality=[True]*train.n,tol=0,atol=0,polish=False,
                    rng=np.random.default_rng(seed))
            except BudgetEnded:
                pass
        else:
            raise ValueError(method)
        # Charge any unused budget to explicit random samples (no fake calls).
        score.stage_cap=budget
        lo,hi=np.array(train.bounds,dtype=int).T
        filler_rng=np.random.default_rng(seed+33371)
        while score.evaluations<budget:
            score(filler_rng.integers(lo,hi+1))
            score.filler_calls+=1
    except Exception as exc:
        success,error=False,type(exc).__name__+": "+str(exc)
    if score.vector is None:
        success=False
        error=error or "No physically evaluated finite design"
        tcost=combined=float("nan")
    else:
        try:
            tcost=float(heldout.evaluate(score.vector)["cost"])
            combined=float(all_periods.evaluate(score.vector)["cost"])
            if not (math.isfinite(tcost) and math.isfinite(combined)):
                raise ValueError("nonfinite evaluation-period cost")
        except Exception as exc:
            success=False
            error=type(exc).__name__+": "+str(exc)
            tcost=combined=float("nan")
    return dict(method=method,seed=seed,success=success,error=error,
                training_cost=score.best,
                reused_august_cost=tcost,all_periods_cost=combined,
                physical_objective_evaluations=score.evaluations,
                objective_requests=score.requests,
                postbudget_calls=score.postbudget,
                local_evaluations=score.local_calls,
                local_restarts=score.local_restarts,
                filler_evaluations=score.filler_calls,
                seconds=round(time.perf_counter()-begin,4),
                final_vector=("-".join(map(str,score.vector)) if score.vector else ""))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seeds",type=int,default=8)
    p.add_argument("--seed-start",type=int,default=100)
    p.add_argument("--budget",type=int,default=360)
    p.add_argument("--population",type=int,default=36)
    p.add_argument("--output",default="geant_local_refinement.csv")
    args=p.parse_args()
    if args.seeds<1 or args.budget<2*args.population:p.error("invalid seed count or budget")
    base=GeantCapacity.download()
    snapshots=archived_traffic()
    peak_total=sum(x for _,_,x in base.demands)
    max_train=max(sum(d for _,_,d in snapshots[s]) for s in TRAIN_STAMPS)
    factor=peak_total/max_train
    scaled={s:[(i,j,w*factor) for i,j,w in d] for s,d in snapshots.items()}
    train=ChronologicalCapacity(base,{s:scaled[s] for s in TRAIN_STAMPS})
    heldout=ChronologicalCapacity(base,{s:scaled[s] for s in TEST_STAMPS})
    all_periods=ChronologicalCapacity(base,scaled)
    print("PROVENANCE",SHA256,"network_sha256",base.data_sha256,
          "factor_training_only",factor,"train",len(TRAIN_STAMPS),
          "reused_holdout",len(TEST_STAMPS),flush=True)
    rows=[]
    for seed in range(args.seed_start,args.seed_start+args.seeds):
        for method in METHODS:
            row=run(train,heldout,all_periods,method,seed,args.budget,args.population)
            rows.append(row)
            print("RUN",row,flush=True)
    with open(args.output,"w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for method in METHODS:
        subset=[r for r in rows if r["method"]==method]
        good=[r["all_periods_cost"] for r in subset if r["success"]]
        print("SUMMARY",method,"successes",len(good),"/",len(subset),
              "median_44",statistics.median(good) if good else "NA",
              "worst_44",max(good) if good else "NA",
              "median_seconds",statistics.median(r["seconds"] for r in subset),
              "physical_calls_range",(min(r["physical_objective_evaluations"] for r in subset),
                                       max(r["physical_objective_evaluations"] for r in subset)),
              flush=True)
    if any(r["physical_objective_evaluations"]!=args.budget for r in rows):
        print("WARNING unequal true evaluation budgets including failures",flush=True)


if __name__=="__main__":
    main()
