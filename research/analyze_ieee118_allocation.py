"""Frozen IEEE118 exploratory six-method / two-load statistical report."""
import argparse
import csv
import math
import statistics

import numpy as np
from scipy.stats import binomtest, wilcoxon

from research.analyze_aos_ieee14 import wilson,boot_median_ci,rank
from research.ieee118_allocation import METHODS


def process(path, budget, seeds=6, start=200):
    with open(path,newline="",encoding="utf8") as f:
        rows=list(csv.DictReader(f))
    expected=len(METHODS)*2*seeds
    if len(rows)!=expected:
        raise ValueError(f"Expected {expected} measured rows, got {len(rows)}")
    data={}
    for row in rows:
        key=(float(row["load_factor"]),row["method"],int(row["seed"]))
        if key in data:
            raise ValueError("Duplicate measured key "+str(key))
        if int(row["actual_solver_calls"])!=budget:
            raise ValueError("Unequal physical calls "+str(key))
        has_physical=row["physically_feasible"]=="True"
        completed=row["optimizer_success"]=="True"
        val=float(row["feasible_loss_mw"]) if row["feasible_loss_mw"] else math.nan
        if has_physical and not math.isfinite(val):
            raise ValueError("Physical feasibility missing a valid loss "+str(key))
        data[key]=dict(feasible=has_physical and completed,MW=val,
                       raw_feasible=has_physical,completed=completed,
                       violation=(float(row["min_observed_violation"]) if
                                 row["min_observed_violation"] else math.nan),
                       time=float(row["elapsed_sec"]),
                       ga=int(row["ga_physical_calls"]),
                       local=int(row["local_physical_calls"]),
                       fill=int(row["random_filler_evaluations"]),
                       solver_failures=int(row["converged_solver_failures"]),
                       rejected=int(row["rejected_solver_requests"]),
                       decision=row["adaptive_decision"],error=row["error"])
    for load in (1.,1.1):
        seedlist=list(range(start,start+seeds))
        groups={m:[data[load,m,s] for s in seedlist] for m in METHODS}
        for method,items in groups.items():
            possible=[r["MW"] for r in items if r["feasible"]]
            violations=[r["violation"] for r in items if math.isfinite(r["violation"])]
            print("METHOD",load,method,"valid_feasible",len(possible),"/",len(items),
                  "wilson95",wilson(len(possible),len(items)),
                  "median_conditional_loss_mw",statistics.median(possible) if possible else "NA",
                  "conditional_q90_mw",float(np.quantile(possible,.90)) if possible else "NA",
                  "worst_conditional_mw",max(possible) if possible else "NA",
                  "median_min_violation",statistics.median(violations) if violations else "NA",
                  "physical_calls_total",budget*len(items),
                  "median_seconds",statistics.median(v["time"] for v in items),
                  "ga_calls_total",sum(v["ga"] for v in items),
                  "local_calls_total",sum(v["local"] for v in items),
                  "random_filler_calls",sum(v["fill"] for v in items),
                  "rejected_nonphysical_requests",sum(v["rejected"] for v in items),
                  "ac_failures",sum(v["solver_failures"] for v in items),
                  "adaptive_choices",dict((s,sum(r["decision"]==s for r in items))
                                          for s in ("feasible_stalled","feasible_improving",
                                                    "infeasible_explore"))
                  if method=="hybrid_adaptive" else {},
                  flush=True)
        tests=[]
        for method in METHODS[1:]:
            a,b=groups[method],groups["gadapt_legacy"]
            outcomes=[rank(x,y) for x,y in zip(a,b)]
            w,l,t=outcomes.count(-1),outcomes.count(1),outcomes.count(0)
            p=binomtest(w,w+l,.5).pvalue if w+l else 1.
            f_gain=sum(x["feasible"] and not y["feasible"] for x,y in zip(a,b))
            f_loss=sum(y["feasible"] and not x["feasible"] for x,y in zip(a,b))
            deltas=[x["MW"]-y["MW"] for x,y in zip(a,b)
                    if x["feasible"] and y["feasible"]]
            tests.append((method,w,l,t,p,f_gain,f_loss,deltas))
        order=sorted(range(len(tests)),key=lambda i:tests[i][4])
        corrected=[1.]*len(tests)
        running=0.
        for idx,i in enumerate(order):
            running=max(running,min(1.,tests[i][4]*(len(tests)-idx)))
            corrected[i]=running
        for i,(method,w,l,t,p,fg,fl,diffs) in enumerate(tests):
            print("PAIRED_PRIMARY",load,method,
                  "wins_losses_ties",(w,l,t),"sign_p",p,
                  "holm_5_p",corrected[i],
                  "feasibility_gain_loss",(fg,fl),
                  "exact_discordant_p",(binomtest(fg,fg+fl,.5).pvalue if fg+fl else 1.),
                  "both_feasible_n",len(diffs),
                  "median_delta_mw",statistics.median(diffs) if diffs else "NA",
                  "bootstrap95",boot_median_ci(diffs),
                  "wilcoxon_p",(float(wilcoxon(diffs).pvalue) if
                    len(diffs)>=6 and any(v!=0 for v in diffs) else math.nan),flush=True)
        for rival in ("hybrid_fixed_half","slsqp_multistart"):
            a,b=groups["hybrid_adaptive"],groups[rival]
            outcomes=[rank(x,y) for x,y in zip(a,b)]
            w,l,t=outcomes.count(-1),outcomes.count(1),outcomes.count(0)
            diffs=[x["MW"]-y["MW"] for x,y in zip(a,b)
                    if x["feasible"] and y["feasible"]]
            print("PAIRED_SECONDARY",load,"adaptive_vs",rival,
                  "wins_losses_ties",(w,l,t),
                  "exact_sign_p",binomtest(w,w+l,.5).pvalue if w+l else 1.,
                  "median_delta_mw",statistics.median(diffs) if diffs else "NA",
                  "bootstrap95",boot_median_ci(diffs),flush=True)
    print("CAVEAT: IEEE118 public model, n=6 and five corrected comparisons: an exploratory mechanism transfer, NOT proof of optimality, new theory or industrial reliability.")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--budget",type=int,default=180)
    a=parser.parse_args()
    process(a.csv,a.budget)
