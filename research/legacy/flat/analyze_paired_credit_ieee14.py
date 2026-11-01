"""Failure-aware exploratory inference for physically counted paired-credit AOS.

All 8 methods evaluated for 8 paired seeds at two load factors.
N=8 is insufficient for claims of broad reliability or superiority.
"""
import argparse
import csv
import math
import statistics

import numpy as np
from scipy.stats import binomtest, wilcoxon
from research.analyze_aos_ieee14 import wilson, boot_median_ci, rank
from research.paired_credit_ieee14 import METHODS


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("csv")
    args=parser.parse_args()
    with open(args.csv,newline="",encoding="utf-8") as src:
        rows=list(csv.DictReader(src))
    data={}
    for row in rows:
        key=(float(row["load_factor"]),row["method"],int(row["seed"]))
        if key in data:
            raise ValueError("duplicate matched key "+str(key))
        data[key]=dict(
            feasible=row["feasible"]=="True" and row["success"]=="True",
            MW=(float(row["best_feasible_MW"]) if row["best_feasible_MW"] else float("nan")),
            seconds=float(row["seconds"]),
            calls=int(row["objective_evaluations"]),
            requests=int(row["objective_requests"]),
            baselines=int(row["paired_baseline_evaluations"]),
            incomplete=int(row["paired_incomplete_trials"]),
            observations=int(row["operator_observations"]),
            error=row["error"],
        )
    if not data:
        raise ValueError("empty pilot")
    for load in sorted(set(k[0] for k in data)):
        seeds=sorted(k[2] for k in data if k[0]==load and k[1]=="legacy_single")
        if len(seeds)!=len(set(seeds)):
            raise ValueError("duplicate reference seeds")
        for method in METHODS:
            values=[data[load,method,s] for s in seeds]
            feasible=[x["MW"] for x in values if x["feasible"]]
            print("METHOD",load,method,
                  "feasible",len(feasible),"/",len(values),
                  "Wilson95",wilson(len(feasible),len(values)),
                  "median_feasible_MW",statistics.median(feasible) if feasible else "NA",
                  "conditional_q90_MW",float(np.quantile(feasible,.9)) if feasible else "NA",
                  "worst_conditional_MW",max(feasible) if feasible else "NA",
                  "median_seconds",statistics.median(x["seconds"] for x in values),
                  "true_PF_calls_range",(min(x["calls"] for x in values),
                                         max(x["calls"] for x in values)),
                  "extra_objective_requests",sum(x["requests"]-x["calls"] for x in values),
                  "physical_baselines_total",sum(x["baselines"] for x in values),
                  "paired_incomplete_total",sum(x["incomplete"] for x in values),
                  "operator_observations_total",sum(x["observations"] for x in values),
                  flush=True)
        comparisons=[]
        for method in METHODS:
            if method=="legacy_single":
                continue
            theirs=[data[load,method,s] for s in seeds]
            controls=[data[load,"legacy_single",s] for s in seeds]
            outcomes=[rank(a,b) for a,b in zip(theirs,controls)]
            wins=outcomes.count(-1)
            losses=outcomes.count(1)
            ties=outcomes.count(0)
            p=binomtest(wins,wins+losses,.5).pvalue if wins+losses else 1.0
            diffs=[a["MW"]-b["MW"] for a,b in zip(theirs,controls)
                   if a["feasible"] and b["feasible"]]
            wp=float(wilcoxon(diffs).pvalue) if len(diffs)>=6 and any(d!=0 for d in diffs) else float("nan")
            comparisons.append(dict(method=method,wins=wins,losses=losses,ties=ties,p=p,diffs=diffs,wp=wp))
        order=sorted(range(len(comparisons)),key=lambda i:comparisons[i]["p"])
        corrected=[0.0]*len(comparisons)
        best=0.0
        for place,i in enumerate(order):
            best=max(best,min(1.0,(len(order)-place)*comparisons[i]["p"]))
            corrected[i]=best
        for i,c in enumerate(comparisons):
            print("PAIRED",load,c["method"],
                  "wins/losses/ties",(c["wins"],c["losses"],c["ties"]),
                  "sign_p",c["p"],"holm_p",corrected[i],
                  "both_feasible_n",len(c["diffs"]),
                  "median_paired_difference_MW",statistics.median(c["diffs"]) if c["diffs"] else "NA",
                  "bootstrap95_paired",boot_median_ci(c["diffs"]),
                  "conditional_wilcoxon_p",c["wp"],
                  flush=True)
    failures=[(k,v["error"]) for k,v in data.items() if v["error"]]
    if failures:
        print("ALERT optimization errors retained",failures[:10],flush=True)
    print("INTERPRETATION: descriptive exploratory pilot only. Paired local controls consume genuine solver evaluations.")


if __name__=="__main__":
    main()
