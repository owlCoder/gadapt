"""Paired exploratory inference for frozen 44-frame GÉANT AOS pilot.

Costs from trained static network-designs; all failed runs kept as failures.
No feasibility claim is derived from the unbounded capacity-module model.
"""
import argparse
import csv
import math
import statistics

import numpy as np
from scipy.stats import binomtest, wilcoxon


def median_bootstrap_ci(values, draws=3000):
    if not values:
        return (float("nan"), float("nan"))
    sample = np.asarray(values,float)
    rng = np.random.default_rng(20261021)
    picks = rng.integers(0,len(sample),(draws,len(sample)))
    return tuple(float(v) for v in np.quantile(np.median(sample[picks],axis=1),[.025,.975]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    args=p.parse_args()
    with open(args.file,newline="",encoding="utf-8") as src:
        rows=list(csv.DictReader(src))
    groups = {}
    for row in rows:
        method, seed = row["method"], int(row["seed"])
        if (method,seed) in groups:
            raise ValueError("duplicate seed")
        try:
            train = float(row["development_cost"])
            holdout = float(row["late_august_cost"])
            total = float(row["all_period_cost"])
        except ValueError:
            train = holdout = total = float("nan")
        groups[method,seed] = {
            "success": row["success"]=="True" and all(math.isfinite(x) for x in (train,holdout,total)),
            "train": train,"test":holdout,"all":total,
            "calls": int(row["objective_evaluations"]),
            "requests": int(row["objective_requests"]),
            "seconds":float(row["seconds"])
        }
    names = ("legacy","affine","uniform_objective","ucb_objective","scipy_de")
    seeds = sorted(seed for method,seed in groups if method=="legacy")
    for name in names:
        items=[groups[name,s] for s in seeds]
        ok=[i for i in items if i["success"]]
        test=sorted(i["test"] for i in ok)
        allperiod=sorted(i["all"] for i in ok)
        print("METHOD",name,"successes",len(ok),"/",len(items),
              "median_development",statistics.median(i["train"] for i in ok) if ok else "NA",
              "median_test",statistics.median(test) if test else "NA",
              "median_all",statistics.median(allperiod) if allperiod else "NA",
              "q90_test",float(np.quantile(test,.9)) if test else "NA",
              "worst_all",max(allperiod) if allperiod else "NA",
              "median_seconds",statistics.median(i["seconds"] for i in items),
              "true_calls_range",(min(i["calls"] for i in items),max(i["calls"] for i in items)),
              "extra_requests",sum(i["requests"]-i["calls"] for i in items))
    comparisons=[]
    for name in names[1:]:
        pairs=[(groups[name,s],groups["legacy",s]) for s in seeds]
        wins=sum(a["success"] and (not b["success"] or a["all"]<b["all"])
                 for a,b in pairs)
        losses=sum(b["success"] and (not a["success"] or b["all"]<a["all"])
                   for a,b in pairs)
        ties=len(seeds)-wins-losses
        signp=binomtest(wins,wins+losses,.5).pvalue if wins+losses else 1.
        diffs=[a["all"]-b["all"] for a,b in pairs if a["success"] and b["success"]]
        wilp=wilcoxon(diffs).pvalue if len(diffs)>=6 and any(d!=0 for d in diffs) else float("nan")
        comparisons.append((name,wins,losses,ties,signp,diffs,wilp))
    order=sorted(range(len(comparisons)),key=lambda i:comparisons[i][4])
    corrected=[0.]*len(comparisons)
    bound=0.
    for rank,i in enumerate(order):
        bound=max(bound,min(1.,(len(order)-rank)*comparisons[i][4]))
        corrected[i]=bound
    for i,(name,w,l,t,p,diffs,wp) in enumerate(comparisons):
        print("PAIRED",name,"wins/losses/ties",(w,l,t),
              "sign_p",p,"holm_p",corrected[i],
              "median_both_success_difference",statistics.median(diffs) if diffs else "NA",
              "bootstrap95",median_bootstrap_ci(diffs),
              "conditional_wilcoxon_p",wp)
    print("NOTICE: pilot 8 paired seeds; exploratory only; per-run failures not excluded from success fractions")


if __name__=="__main__":
    main()
