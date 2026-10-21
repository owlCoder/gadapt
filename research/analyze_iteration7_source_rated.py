"""Independent iteration-7 source-RATE_A pilot audit from immutable raw CSV.

Uses actual physical outcomes, NOT incomparable optimizer objective values.
No reusing identical seeds as new independent observations.
Mechanistic n=3: all p-values exploratory and underpowered.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics

import numpy as np

METHODS=("gadapt_penalty","gadapt_feasibility_first",
         "slsqp_penalty","hybrid_fixed","scipy_de")
METHOD_LABELS=("GAdapt penalty","GAdapt feasibility-first",
               "SLSQP penalty","Fixed GAdapt + SLSQP","SciPy DE")


def sign_p(wins,losses):
    n=wins+losses
    if n==0:return 1.
    x=min(wins,losses)
    return min(1.,2*sum(math.comb(n,i) for i in range(x+1))/2**n)


def holm(raw):
    ordered=sorted(range(len(raw)),key=lambda i:raw[i])
    adjusted=[0.]*len(raw)
    running=0.
    for rank,i in enumerate(ordered):
        running=max(running,min(1.,raw[i]*(len(raw)-rank)))
        adjusted[i]=running
    return adjusted


def wilson(successes,n,z=1.959963984540054):
    if not n:return (0.,1.)
    p=successes/n
    center=(p+z*z/(2*n))/(1+z*z/n)
    radius=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return max(0.,center-radius),min(1.,center+radius)


def records(path):
    with open(path,newline="",encoding="utf8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=15:
        raise ValueError("Pilot must preserve all fifteen method/seed rows")
    result=[]
    pairs=set()
    for raw in rows:
        method=raw["method"]
        seed=int(raw["seed"])
        if method not in METHODS or seed not in (350,351,352):
            raise ValueError("Invalid preregistered method or seed")
        key=(method,seed)
        if key in pairs:raise ValueError("Duplicated paired run")
        pairs.add(key)
        if raw["formulation"]!="source_RATE_A_MVA_zero_unlimited":
            raise ValueError("Wrong constraint provenance/formulation")
        if int(raw["actual_ac_calls"])!=72 or int(raw["budget"])!=72:
            raise ValueError("Not 72 genuine AC solver calls")
        flag={"True":True,"False":False}[raw["physically_feasible"]]
        violation=(float(raw["min_observed_physical_violation"])
                   if raw["min_observed_physical_violation"]!="" else math.inf)
        loss=(float(raw["best_feasible_loss_mw"])
              if raw["best_feasible_loss_mw"]!="" else None)
        if flag and (loss is None or not math.isfinite(loss) or violation>1e-8):
            raise ValueError("Claimed feasible result fails direct recorder invariants")
        if not flag and loss is not None:
            raise ValueError("Infeasible loss must not be imputed")
        result.append({"method":method,"seed":seed,
             "feasible":flag,"violation":violation,"loss":loss,
             "failures":int(raw["nonconvergent_ac_calls"]),
             "calls":int(raw["actual_ac_calls"]),
             "runtime":float(raw["elapsed_sec"]),
             "optimizer_completed":raw["optimizer_completed"]=="True"})
    if len(pairs)!=15:raise ValueError("Incomplete paired observations")
    return result


def analyze(rows):
    summary=[]
    for method in METHODS:
        rr=sorted([r for r in rows if r["method"]==method],key=lambda r:r["seed"])
        values=[r["violation"] for r in rr if math.isfinite(r["violation"])]
        losses=[r["loss"] for r in rr if r["feasible"]]
        low,high=wilson(len(losses),3)
        summary.append({"method":method,"runs":len(rr),
          "physically_feasible_runs":len(losses),
          "wilson_95_low":low,"wilson_95_high":high,
          "median_best_feasible_loss_mw":statistics.median(losses) if losses else "",
          "median_min_violation":statistics.median(values) if values else "",
          "q90_min_violation":float(np.quantile(values,.9)) if values else "",
          "worst_min_violation":max(values) if values else "",
          "median_runtime_sec":statistics.median(r["runtime"] for r in rr),
          "total_solver_failures":sum(r["failures"] for r in rr),
          "total_true_ac_calls":sum(r["calls"] for r in rr),
          "optimizer_completed_runs":sum(r["optimizer_completed"] for r in rr)})
    base={r["seed"]:r for r in rows if r["method"]=="gadapt_penalty"}
    pairs=[]
    for method in METHODS[1:]:
        ours={r["seed"]:r for r in rows if r["method"]==method}
        wins=losses=ties=0
        paired_deltas=[]
        for seed in (350,351,352):
            a,b=ours[seed],base[seed]
            if a["feasible"]!=b["feasible"]:
                result=1 if a["feasible"] else -1
            elif a["feasible"]:
                delta=a["loss"]-b["loss"]
                paired_deltas.append(delta)
                result=1 if delta<0 else (-1 if delta>0 else 0)
            else:
                if math.isfinite(a["violation"]) and math.isfinite(b["violation"]):
                    delta=a["violation"]-b["violation"]
                    paired_deltas.append(delta)
                    result=1 if delta<-1e-9 else (-1 if delta>1e-9 else 0)
                else:
                    result=0
            if result>0:wins+=1
            elif result<0:losses+=1
            else:ties+=1
        pairs.append({"comparison":method+" vs gadapt_penalty",
           "wins":wins,"losses":losses,"ties":ties,
           "median_paired_numeric_delta":(
                statistics.median(paired_deltas) if paired_deltas else ""),
           "unadjusted_exact_sign_p":sign_p(wins,losses)})
    adj=holm([x["unadjusted_exact_sign_p"] for x in pairs])
    for item,p in zip(pairs,adj):item["holm_4_p"]=p
    return summary,pairs


def plot(rows,basename):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # Plot observed residuals only: no unobserved feasible MW values.
    fig,ax=plt.subplots(figsize=(10,5.5))
    for j,(m,label) in enumerate(zip(METHODS,METHOD_LABELS)):
        rr=sorted([v for v in rows if v["method"]==m],key=lambda v:v["seed"])
        for i,r in enumerate(rr):
            if math.isfinite(r["violation"]):
                ax.plot(j+(i-1)*.14,r["violation"],marker="o",markersize=7,
                        label=f"Seed {r['seed']}" if j==0 else None)
    ax.set_xticks(range(len(METHODS)),METHOD_LABELS,rotation=20,ha="right")
    ax.set_ylabel("Minimum measured physical constraint violation (not MW)")
    ax.set_title("RTE1888 source-MATPOWER RATE_A — exploratory n=3")
    ax.grid(axis="y",alpha=.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(str(basename)+".svg")
    fig.savefig(str(basename)+".png",dpi=160)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--summary",default="rte1888_iteration7_stats.json")
    parser.add_argument("--figure",default="rte1888_iteration7_violation")
    a=parser.parse_args()
    rows=records(a.csv_file)
    summaries,pairs=analyze(rows)
    document={"protocol":"research/ITERATION7_PROTOCOL.md addendum C",
             "raw_csv":a.csv_file,"n_independent_seeds":3,
             "n_method_seed_runs":len(rows),
             "total_actual_ac_calls":sum(r["calls"] for r in rows),
             "comparison_family":"4 explorative paired methods versus original GAdapt",
             "novelty_claim":False,"significance_claim":False,
             "summary":summaries,"comparisons":pairs}
    Path(a.summary).write_text(json.dumps(document,indent=2,sort_keys=True,
                                           allow_nan=False)+"\n",encoding="utf8")
    plot(rows,a.figure)
    print("INDEPENDENT_AUDIT",json.dumps(document,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
