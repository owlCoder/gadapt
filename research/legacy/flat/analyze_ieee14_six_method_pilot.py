"""Final reproducible six-arm IEEE14 mechanistic pilot inference.

CMA-ES was preregistered as a separate supplemental baseline. This script
checks paired seeds, identical physical evaluation counts, and retains
all physical feasibility and optimizer failure outcomes. It never reports
a globally certified optimality gap.
"""
import argparse
import csv
import math
import statistics
import numpy as np
from scipy.stats import binomtest,wilcoxon
from research.analyze_aos_ieee14 import wilson,boot_median_ci,rank

NAMES=("legacy_gadapt","affine_gadapt","slsqp_multistart",
       "hybrid_gadapt_slsqp","scipy_de","cma_es")


def read_csv(path):
    with open(path,newline="",encoding="utf8") as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--main",default="research/results/ieee14_local_refinement_20261021.csv")
    ap.add_argument("--cma",default="research/results/ieee14_cma_es_20261021.csv")
    ap.add_argument("--reference",default="research/results/ieee14_reference_3600_20261021.csv")
    args=ap.parse_args()
    raw=read_csv(args.main)+read_csv(args.cma)
    ref={float(r["load_factor"]):float(r["independently_verified_MW"])
         for r in read_csv(args.reference) if r["feasible"]=="True"}
    if set(ref) != {1.0, 1.1}:
        raise ValueError("Missing two independently verified IEEE14 references")
    if len(raw) != 144:
        raise ValueError("Expected exactly 120 GA/SLSQP/DE rows and 24 CMA-ES rows")
    indexed={}
    for r in raw:
        key=(float(r["load_factor"]),r["method"],int(r["seed"]))
        if key in indexed:raise ValueError("duplicate "+str(key))
        count=int(r["true_pf_evaluations"])
        if count!=360:raise ValueError("unmatched solver count "+str(key))
        ok=r["optimizer_success"]=="True" and r["physical_feasible"]=="True"
        val=float(r["feasible_loss_MW"]) if r["feasible_loss_MW"] else math.nan
        indexed[key]=dict(feasible=ok,MW=val,
                          seconds=float(r["seconds"]),
                          requests=int(r["all_objective_requests"]),
                          calls=count,error=r["error"])
    if len(indexed) != 144:
        raise ValueError("Expected 144 unique paired observations")
    for load in sorted(ref):
        seeds=sorted(s for f,m,s in indexed if f==load and m=="legacy_gadapt")
        if seeds!=list(range(100,112)):raise ValueError("unmatched frozen seeds")
        groups={}
        for method in NAMES:
            group=[indexed[load,method,seed] for seed in seeds]
            groups[method]=group
            losses=[t["MW"] for t in group if t["feasible"]]
            print("METHOD",load,method,"valid",len(losses),"/",len(group),
                  "wilson95",wilson(len(losses),len(group)),
                  "median_MW",statistics.median(losses) if losses else "NA",
                  "q90_MW",float(np.quantile(losses,.9)) if losses else "NA",
                  "worst_conditional_MW",max(losses) if losses else "NA",
                  "median_seconds",statistics.median(t["seconds"] for t in group),
                  "true_calls_total",sum(t["calls"] for t in group),
                  "extra_wrapped_requests",sum(t["requests"]-t["calls"] for t in group),
                  "median_excess_vs_empirical_reference_MW",(
                      statistics.median(losses)-ref[load] if losses else "NA"),
                  flush=True)
        comparisons=[]
        for method in NAMES[1:]:
            other=groups[method]
            baseline=groups["legacy_gadapt"]
            ranks=[rank(a,b) for a,b in zip(other,baseline)]
            wins,losses,ties=ranks.count(-1),ranks.count(1),ranks.count(0)
            exact=float(binomtest(wins,wins+losses,.5).pvalue) if wins+losses else 1.
            delta=[a["MW"]-b["MW"] for a,b in zip(other,baseline)
                   if a["feasible"] and b["feasible"]]
            wp=(float(wilcoxon(delta).pvalue) if len(delta)>=6 and
                any(v!=0 for v in delta) else math.nan)
            comparisons.append((method,wins,losses,ties,exact,delta,wp))
        order=sorted(range(len(comparisons)),key=lambda i:comparisons[i][4])
        corrected=[0.]*len(comparisons)
        running=0.
        for position,i in enumerate(order):
            running=max(running,min(1.,(len(order)-position)*comparisons[i][4]))
            corrected[i]=running
        for i,(name,w,l,t,p,delta,wp) in enumerate(comparisons):
            print("PAIRED_PRIMARY",load,name,
                  "wins_losses_ties",(w,l,t),"exact_sign_p",p,
                  "holm_5_p",corrected[i],
                  "feasible_both",len(delta),
                  "median_difference_MW",statistics.median(delta) if delta else "NA",
                  "bootstrap95",boot_median_ci(delta),
                  "conditional_wilcoxon_p",wp,flush=True)
        # Secondary exploratory comparison within different method families.
        sl,cm=groups["slsqp_multistart"],groups["cma_es"]
        delta=[a["MW"]-b["MW"] for a,b in zip(sl,cm)
               if a["feasible"] and b["feasible"]]
        print("PAIRED_SECONDARY",load,"slsqp_minus_cma",
              "n",len(delta),"wins",sum(x<0 for x in delta),
              "losses",sum(x>0 for x in delta),
              "exact_sign_p",binomtest(sum(x<0 for x in delta),
                                      sum(x!=0 for x in delta),.5).pvalue,
              "median_difference_MW",statistics.median(delta),
              "bootstrap95",boot_median_ci(delta),flush=True)
        print("REFERENCE",load,"empirical_verified_best_MW",ref[load],
              "NOTE this is an achieved feasible upper bound, NEVER a proof of optimality")
    print("CONCLUSION: strong evidence standard local SLSQP is superior to plain GAdapt on this SMALL restricted case; NOT a new GA algorithm, NOT industrial evidence.")


if __name__=="__main__":
    main()
