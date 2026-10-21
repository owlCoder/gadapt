"""Failure-aware exact paired costs for previously-inspected chronological data."""
import argparse
import csv
import math
import statistics
import numpy as np
from scipy.stats import binomtest,wilcoxon
from research.analyze_aos_geant_temporal import median_bootstrap_ci
from research.geant_local_refinement import METHODS

def main():
    p=argparse.ArgumentParser()
    p.add_argument("csv")
    a=p.parse_args()
    with open(a.csv,newline="",encoding="utf8") as f:
        rows=list(csv.DictReader(f))
    data={}
    for r in rows:
        key=(r["method"],int(r["seed"]))
        if key in data:raise ValueError("duplicate "+str(key))
        cost=float(r["all_periods_cost"]) if r["all_periods_cost"] else math.nan
        valid=r["success"]=="True" and math.isfinite(cost)
        data[key]=dict(valid=valid,cost=cost,
                       test=float(r["reused_august_cost"]) if r["reused_august_cost"] else math.nan,
                       secs=float(r["seconds"]),
                       calls=int(r["physical_objective_evaluations"]),
                       extra=int(r["objective_requests"])-int(r["physical_objective_evaluations"]),
                       local=int(r["local_evaluations"]),
                       restarts=int(r["local_restarts"]),
                       filler=int(r["filler_evaluations"]),error=r["error"])
    seeds=sorted(s for m,s in data if m=="legacy_gadapt")
    for method in METHODS:
        group=[data[method,s] for s in seeds]
        good=[r for r in group if r["valid"]]
        vals=[r["cost"] for r in good]
        print("METHOD",method,"valid",len(good),"/",len(group),
              "median_44",statistics.median(vals) if vals else "NA",
              "q90_44",float(np.quantile(vals,.9)) if vals else "NA",
              "worst_44",max(vals) if vals else "NA",
              "median_reused_august",statistics.median(r["test"] for r in good) if good else "NA",
              "median_seconds",statistics.median(r["secs"] for r in group),
              "true_calls_minmax",(min(r["calls"] for r in group),max(r["calls"] for r in group)),
              "extra_requests",sum(r["extra"] for r in group),
              "local_calls",sum(r["local"] for r in group),
              "restart_count",sum(r["restarts"] for r in group),
              "filler_evaluations",sum(r["filler"] for r in group),flush=True)
    comparisons=[]
    for method in METHODS[1:]:
        pairs=[(data[method,s],data["legacy_gadapt",s]) for s in seeds]
        wins=sum(a["valid"] and (not b["valid"] or a["cost"]<b["cost"]) for a,b in pairs)
        losses=sum(b["valid"] and (not a["valid"] or b["cost"]<a["cost"]) for a,b in pairs)
        ties=len(pairs)-wins-losses
        pval=binomtest(wins,wins+losses,.5).pvalue if wins+losses else 1.
        diffs=[a["cost"]-b["cost"] for a,b in pairs if a["valid"] and b["valid"]]
        wp=float(wilcoxon(diffs).pvalue) if len(diffs)>=6 and any(x!=0 for x in diffs) else math.nan
        comparisons.append((method,wins,losses,ties,pval,diffs,wp))
    rank=sorted(range(len(comparisons)),key=lambda i:comparisons[i][4])
    holm=[1.]*len(comparisons)
    last=0.
    for pos,i in enumerate(rank):
        last=max(last,min(1.,(len(rank)-pos)*comparisons[i][4]))
        holm[i]=last
    for i,(method,w,l,t,pv,diffs,wp) in enumerate(comparisons):
        print("PAIRED",method,"wins/losses/ties",(w,l,t),
              "exact_sign_p",pv,"holm_p",holm[i],
              "median_paired_difference_44",statistics.median(diffs) if diffs else "NA",
              "bootstrap95",median_bootstrap_ci(diffs),
              "conditional_wilcoxon_p",wp,flush=True)
    failures=[(k,v["error"]) for k,v in data.items() if v["error"]]
    if failures:print("ALERT failures counted",failures[:12],flush=True)
    print("LIMITATIONS: same previously examined August samples, NOT independent; no hard feasibility signal.")


if __name__=="__main__":
    main()
