"""Rebuild iteration-5 IEEE14 six-method distribution figures from raw CSV.

Reference dashed line is an independently achieved feasible value, NOT a
mathematical lower bound. Failed optimizer runs are never silently imputed
with a loss in MW; each box annotates the feasibility denominator.
"""
import argparse
import csv
from pathlib import Path
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

METHODS=("legacy_gadapt","affine_gadapt","slsqp_multistart",
         "hybrid_gadapt_slsqp","scipy_de","cma_es")
LABELS=("Original GAdapt","Affine GAdapt","Multi-start SLSQP",
        "GAdapt + SLSQP","SciPy DE","CMA-ES")


def load_rows(path):
    with open(path,newline="",encoding="utf8") as file:
        return list(csv.DictReader(file))


def plot(load,rows,reference,out_dir):
    groups=[[r for r in rows if r["method"]==method and
             float(r["load_factor"])==load] for method in METHODS]
    if any(len(g)!=12 for g in groups):
        raise ValueError("Requires exactly 12 matched seeds for every algorithm")
    arrays=[]
    counts=[]
    for group in groups:
        values=[float(r["feasible_loss_MW"]) for r in group if
                r["optimizer_success"]=="True" and r["physical_feasible"]=="True"
                and r["feasible_loss_MW"]]
        arrays.append(np.array(values,float))
        counts.append(len(values))
    fig,ax=plt.subplots(figsize=(12,6.5))
    has_data=[(i+1,arr) for i,arr in enumerate(arrays) if len(arr)]
    if has_data:
        positions,datasets=zip(*has_data)
        ax.boxplot(datasets,positions=positions,widths=.45,showfliers=True)
    ax.axhline(reference,color="tab:red",linestyle="--",linewidth=1.2,
               label="Best independently rechecked feasible control (NOT proven optimum)")
    ax.set_xticks(range(1,len(METHODS)+1),LABELS,rotation=20,ha="right")
    ax.set_title(f"IEEE14 AC physical solver — {load:.0%} demand, 360 calls/run")
    ax.set_ylabel("Real-power losses (MW) among physically feasible runs only")
    ax.grid(axis="y",alpha=.25)
    ax.legend(loc="upper right",fontsize=9)
    for i,n in enumerate(counts):
        ax.text(i+1,1.02,f"{n}/12 feasible",ha="center",
                transform=ax.get_xaxis_transform(),fontsize=9)
    fig.text(.04,.01,
             "12 paired seeds (100–111). Constraint violations and failed runs are "
             "included in feasibility denominators; loss boxes are conditional.",
             fontsize=9)
    fig.tight_layout(rect=(0,.045,1,.94))
    tag="load100" if load==1 else "load110"
    for ext in ("svg","png"):
        file=out_dir/f"ieee14_local_refinement_{tag}.{ext}"
        fig.savefig(file,dpi=160)
        print("PLOT",file,flush=True)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--main",default="research/results/ieee14_local_refinement_20261021.csv")
    p.add_argument("--cma",default="research/results/ieee14_cma_es_20261021.csv")
    p.add_argument("--reference",default="research/results/ieee14_reference_3600_20261021.csv")
    p.add_argument("--output-dir",default="iteration5_figures")
    args=p.parse_args()
    rows=load_rows(args.main)+load_rows(args.cma)
    ref={float(r["load_factor"]):float(r["independently_verified_MW"])
         for r in load_rows(args.reference) if r["feasible"]=="True"}
    if set(ref)!={1.,1.1}:raise ValueError("Missing both physical reference audits")
    output=Path(args.output_dir)
    output.mkdir(parents=True,exist_ok=True)
    for load in (1.,1.1):
        plot(load,rows,ref[load],output)


if __name__=="__main__":
    main()
