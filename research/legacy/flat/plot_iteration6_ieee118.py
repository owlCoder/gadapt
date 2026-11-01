"""Regenerate IEEE118 physical losses and budget-split plots from raw CSV.

Requires 72 unique 6-method, 2-load, 6-seed trials and 180 actual PF
evaluations per run. No plot treats an infeasible run as having a valid MW
loss. IEEE118 is a public benchmark, not a global optimality certificate.
"""
import argparse
import csv
from pathlib import Path
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

METHODS=("gadapt_legacy","slsqp_multistart","hybrid_fixed_half",
         "hybrid_adaptive","scipy_de","cma_es")
LABELS=("GAdapt","SLSQP","GA + SLSQP 50/50","Adaptive GA + SLSQP","SciPy DE","CMA-ES")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--output-dir",default="iteration6_figures")
    args=ap.parse_args()
    with open(args.csv,newline="",encoding="utf8") as f:rows=list(csv.DictReader(f))
    if len(rows)!=72:raise ValueError("Expected 72 physical IEEE118 trial records")
    uniq={(float(r["load_factor"]),r["method"],int(r["seed"])) for r in rows}
    if len(uniq)!=72:raise ValueError("Not 72 unique method-load-seed keys")
    if any(int(r["actual_solver_calls"])!=180 for r in rows):
        raise ValueError("Unequal true physical AC solver calls")
    out=Path(args.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    for load in (1.,1.1):
        groups=[[r for r in rows if float(r["load_factor"])==load and
                 r["method"]==method] for method in METHODS]
        if any(len(g)!=6 for g in groups):raise ValueError("Missing frozen paired methods")
        subsets=[[float(r["feasible_loss_mw"]) for r in group if
                  r["optimizer_success"]=="True" and
                  r["physically_feasible"]=="True"
                  and r["feasible_loss_mw"]] for group in groups]
        fig,ax=plt.subplots(figsize=(12,6.5))
        valid=[(i+1,a) for i,a in enumerate(subsets) if a]
        if valid:
            xs,vals=zip(*valid)
            ax.boxplot(vals,positions=xs,widths=.4)
        else:
            ax.text(.5,.5,"No physically feasible solutions found",
                    transform=ax.transAxes,ha="center",va="center")
        ax.set_xticks(range(1,7),LABELS,rotation=25,ha="right")
        ax.set_title(f"IEEE118 – {load:.0%} load / 180 true AC powerflows per run")
        ax.set_ylabel("Physically feasible active-power loss (MW)")
        ax.grid(axis="y",alpha=.25)
        for i,g in enumerate(subsets):
            ax.text(i+1,1.02,f"{len(g)}/6 feasible",ha="center",
                    transform=ax.get_xaxis_transform(),fontsize=9)
        fig.text(.03,.01,"6 paired seeds 200–205. Loss distributions condition on real physical feasibility; failures remain in 6-run denominator.",fontsize=9)
        fig.tight_layout(rect=(0,.05,1,.93))
        for ext in ("svg","png"):
            target=out/f"ieee118_load{int(load*100)}.{ext}"
            fig.savefig(target,dpi=160)
            print("FIGURE",target,flush=True)
        plt.close(fig)

        fig,ax=plt.subplots(figsize=(9,5))
        adaptive=sorted(groups[METHODS.index("hybrid_adaptive")],
                        key=lambda r:int(r["seed"]))
        seeds=[int(r["seed"]) for r in adaptive]
        shares=[int(r["ga_physical_calls"])/180 for r in adaptive]
        ax.bar([str(s) for s in seeds],shares)
        ax.axhline(.5,linestyle="--",linewidth=1.2,label="Fixed hybrid GA half-budget")
        ax.set_ylim(0,1)
        ax.set_ylabel("Share of real evaluations consumed by GAdapt")
        ax.set_xlabel("Paired seed")
        ax.set_title(f"Frozen adaptive GA→SLSQP split — IEEE118, {load:.0%} load")
        ax.legend()
        fig.tight_layout()
        for ext in ("svg","png"):
            target=out/f"ieee118_allocation_load{int(load*100)}.{ext}"
            fig.savefig(target,dpi=160)
            print("FIGURE",target,flush=True)
        plt.close(fig)


if __name__=="__main__":main()
