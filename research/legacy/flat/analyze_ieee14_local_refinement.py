"""Preregistered IEEE14 local-refinement audit: paired, failure-aware statistics.

A feasible incumbent can be from any true solver call incl hybrid local stage;
post-budget sentinel requests are NOT evaluated and NEVER count as feasible.
"""
import argparse
import csv
import math
import statistics
import numpy as np
from scipy.stats import binomtest, wilcoxon
from research.analyze_aos_ieee14 import wilson,boot_median_ci,rank
from research.ieee14_local_refinement import METHODS


def analyze(file):
    with open(file,newline="",encoding="utf8") as fh:
        rows=list(csv.DictReader(fh))
    data={}
    for r in rows:
        key=(float(r["load_factor"]),r["method"],int(r["seed"]))
        if key in data: raise ValueError("Duplicate matched run "+str(key))
        valid=r["optimizer_success"]=="True" and r["physical_feasible"]=="True"
        data[key]=dict(feasible=valid,
                       MW=float(r["feasible_loss_MW"]) if r["feasible_loss_MW"] else float("nan"),
                       error=r["error"],
                       calls=int(r["true_pf_evaluations"]),
                       requests=int(r["all_objective_requests"]),
                       seconds=float(r["seconds"]),
                       filled=int(r["random_budget_fill_evaluations"]),
                       starts=int(r["local_restarts"]))
    if not data:raise ValueError("empty results")
    loads=sorted(set(x[0] for x in data))
    for load in loads:
        seeds=sorted(k[2] for k in data if k[0]==load and k[1]=="legacy_gadapt")
        print("LOAD",load,"paired_n",len(seeds),flush=True)
        for method in METHODS:
            sample=[data[load,method,s] for s in seeds]
            good=[v["MW"] for v in sample if v["feasible"]]
            print("METHOD",load,method,
                  "feasible",len(good),"/",len(sample),
                  "Wilson95",wilson(len(good),len(sample)),
                  "median_loss_MW",statistics.median(good) if good else "NA",
                  "conditional_q90_MW",float(np.quantile(good,.9)) if good else "NA",
                  "worst_feasible_MW",max(good) if good else "NA",
                  "median_seconds",statistics.median(s["seconds"] for s in sample),
                  "actual_pf_calls_range",(min(s["calls"] for s in sample),
                                          max(s["calls"] for s in sample)),
                  "objective_overhead_calls",sum(s["requests"]-s["calls"] for s in sample),
                  "budget_filler_evaluations",sum(s["filled"] for s in sample),
                  "local_restarts",sum(s["starts"] for s in sample),flush=True)
        comparisons=[]
        for method in METHODS[1:]:
            paired=[(data[load,method,s],data[load,"legacy_gadapt",s]) for s in seeds]
            outcomes=[rank(a,b) for a,b in paired]
            w,l,t=outcomes.count(-1),outcomes.count(1),outcomes.count(0)
            sign=binomtest(w,w+l,.5).pvalue if w+l else 1.
            improve=sum(a["feasible"] and not b["feasible"] for a,b in paired)
            regress=sum(b["feasible"] and not a["feasible"] for a,b in paired)
            mcnemar=binomtest(improve,improve+regress,.5).pvalue if improve+regress else 1.
            delta=[a["MW"]-b["MW"] for a,b in paired if a["feasible"] and b["feasible"]]
            wp=float(wilcoxon(delta).pvalue) if len(delta)>=6 and any(d!=0 for d in delta) else float("nan")
            comparisons.append((method,w,l,t,sign,improve,regress,mcnemar,delta,wp))
        ranks=sorted(range(len(comparisons)),key=lambda i:comparisons[i][4])
        adj=[0.]*len(comparisons)
        current=0.
        for pos,i in enumerate(ranks):
            current=max(current,min(1.,(len(ranks)-pos)*comparisons[i][4]))
            adj[i]=current
        for i,(method,w,l,t,p,improve,regress,mcnemar,delta,wp) in enumerate(comparisons):
            print("PAIRED",load,method,"wins/losses/ties",(w,l,t),
                  "exact_sign_p",p,"holm_p",adj[i],
                  "feasibility_gains_losses",(improve,regress),
                  "mcnemar_exact_p",mcnemar,
                  "paired_feasible_n",len(delta),
                  "median_paired_delta_MW",statistics.median(delta) if delta else "NA",
                  "bootstrap95",boot_median_ci(delta),
                  "conditional_wilcoxon_p",wp,flush=True)
    errs=[(k,v["error"]) for k,v in data.items() if v["error"]]
    if errs:print("ERRORS kept in reliability denominator",errs[:10],flush=True)
    print("CAUTION: 12-seed mechanistic pilot, NOT global optimum proof or industrial validation.")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("csv")
    args=parser.parse_args()
    analyze(args.csv)
