"""Exploratory paired GÉANT statistics, failure aware, 6 Holm comparisons."""
import argparse
import csv
import math
import statistics
import numpy as np
from scipy.stats import binomtest, wilcoxon
from research.paired_credit_geant import METHODS
from research.analyze_aos_geant_temporal import median_bootstrap_ci


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("csv")
    a=parser.parse_args()
    with open(a.csv,newline="",encoding="utf8") as f:
        rows=list(csv.DictReader(f))
    data={}
    for row in rows:
        key=(row["method"],int(row["seed"]))
        if key in data:
            raise ValueError("Duplicate result "+str(key))
        cost=float(row["all_44_cost"]) if row["all_44_cost"] else float("nan")
        ok=row["success"]=="True" and math.isfinite(cost)
        data[key]=dict(ok=ok,cost=cost,
                       aug=float(row["august_32_cost"]) if row["august_32_cost"] else float("nan"),
                       calls=int(row["objective_evaluations"]),
                       extra=int(row["objective_requests"])-int(row["objective_evaluations"]),
                       baselines=int(row["paired_physical_baselines"]),
                       incomplete=int(row["incomplete_pairs"]),
                       observations=int(row["operator_observations"]),
                       seconds=float(row["seconds"]),error=row["error"])
    seeds=sorted(s for m,s in data if m=="legacy_single")
    for method in METHODS:
        group=[data[method,s] for s in seeds]
        ok=[x for x in group if x["ok"]]
        print("METHOD",method,"successes",len(ok),"/",len(group),
              "median_44",statistics.median(x["cost"] for x in ok) if ok else "NA",
              "q90_44",float(np.quantile([x["cost"] for x in ok],.9)) if ok else "NA",
              "worst_44",max(x["cost"] for x in ok) if ok else "NA",
              "median_august_32",statistics.median(x["aug"] for x in ok) if ok else "NA",
              "median_seconds",statistics.median(x["seconds"] for x in group),
              "calls_range",(min(x["calls"] for x in group),max(x["calls"] for x in group)),
              "extra_requests",sum(x["extra"] for x in group),
              "physical_baselines",sum(x["baselines"] for x in group),
              "incomplete_pairs",sum(x["incomplete"] for x in group),
              "observations",sum(x["observations"] for x in group),flush=True)
    comparisons=[]
    for m in METHODS:
        if m=="legacy_single":
            continue
        pairs=[(data[m,s],data["legacy_single",s]) for s in seeds]
        wins=sum(x["ok"] and (not y["ok"] or x["cost"]<y["cost"]) for x,y in pairs)
        losses=sum(y["ok"] and (not x["ok"] or y["cost"]<x["cost"]) for x,y in pairs)
        ties=len(pairs)-wins-losses
        p=binomtest(wins,wins+losses,.5).pvalue if wins+losses else 1.
        diffs=[x["cost"]-y["cost"] for x,y in pairs if x["ok"] and y["ok"]]
        wp=float(wilcoxon(diffs).pvalue) if len(diffs)>=6 and any(d!=0 for d in diffs) else float("nan")
        comparisons.append((m,wins,losses,ties,p,diffs,wp))
    indices=sorted(range(len(comparisons)),key=lambda i:comparisons[i][4])
    holm=[1.]*len(comparisons)
    running=0.
    for i,index in enumerate(indices):
        running=max(running,min(1.,(len(indices)-i)*comparisons[index][4]))
        holm[index]=running
    for i,(m,w,l,t,p,diffs,wp) in enumerate(comparisons):
        print("PAIRED",m,"wins/losses/ties",(w,l,t),
              "exact_sign_p",p,"holm_p",holm[i],
              "median_difference_44",statistics.median(diffs) if diffs else "NA",
              "bootstrap95",median_bootstrap_ci(diffs),
              "conditional_wilcoxon_p",wp,flush=True)
    print("CAVEAT: same already inspected August timestamps, NOT a fresh holdout; n=8 exploratory only")


if __name__=="__main__":
    main()
