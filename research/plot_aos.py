"""Publication-supporting exploratory plots for the AOS pilots.

Graphics show *conditional* feasible costs with feasibility denominators
annotated; do not silently discard unsuccessful optimization runs.
"""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


IEEE_METHODS = ("legacy", "affine", "uniform_objective", "ucb_objective",
                "ucb_feasibility", "scipy_de")
GEANT_METHODS = ("legacy", "affine", "uniform_objective", "ucb_objective",
                 "scipy_de")


def name(method):
    return method.replace("_", " ").title()


def ieee_plot(rows, prefix):
    for factor in sorted({float(r["load_factor"]) for r in rows}):
        subset = [r for r in rows if float(r["load_factor"]) == factor]
        data, labels, failures = [], [], []
        for method in IEEE_METHODS:
            selected = [r for r in subset if r["method"] == method]
            feasible = [
                float(r["best_feasible_MW"]) for r in selected
                if r["success"] == "True" and r["feasible"] == "True"
                and r["best_feasible_MW"]
            ]
            # Mark no feasible runs as a missing distribution, never impute a MW.
            data.append(feasible if feasible else [float("nan")])
            labels.append(name(method))
            failures.append((len(feasible),len(selected)))
        fig, ax = plt.subplots(figsize=(11, 5.6))
        ax.boxplot(data, showfliers=True)
        ax.set_xticks(range(1, len(labels) + 1), labels)
        ax.set_ylabel("Loss (MW), ONLY feasible optimization runs")
        ax.set_title(f"IEEE14 PYPOWER AC, load={factor:.2f}, 240 actual PF calls per run")
        ax.tick_params(axis="x",rotation=22)
        bottom, top = ax.get_ylim()
        height = top - bottom
        ax.set_ylim(bottom, top + .16*height)
        for i,(good,n) in enumerate(failures,1):
            ax.text(i, top + .03*height, f"{good}/{n} feasible",
                    ha="center",va="bottom",fontsize=8)
        fig.text(.02,.012,
                 "Exploratory pilot. Feasibility checked independently of penalized cost. "
                 "Failures counted in n; boxes show conditional feasible losses only.",
                 fontsize=8)
        fig.tight_layout(rect=(0,.05,1,.99))
        output=f"{prefix}_load_{str(factor).replace('.','p')}.png"
        fig.savefig(output,dpi=160)
        plt.close(fig)
        print("PLOT",output)


def geant_plot(rows,prefix):
    for metric,title in (
        ("all_period_cost","One static plan covering all 44 periods"),
        ("late_august_cost","One static plan covering 32 held-out August periods"),
    ):
        fig,ax=plt.subplots(figsize=(10,5.4))
        data,labels,denoms=[],[],[]
        for method in GEANT_METHODS:
            trials=[r for r in rows if r["method"]==method]
            valid=[float(r[metric]) for r in trials if r["success"]=="True"
                   and r[metric] and r[metric].lower()!="nan"]
            data.append(valid if valid else [float("nan")])
            labels.append(name(method))
            denoms.append((len(valid),len(trials)))
        ax.boxplot(data,showfliers=True)
        ax.set_xticks(range(1,len(labels)+1),labels)
        ax.set_ylabel("Capacity module cost (SNDlib model units)")
        ax.set_title("GÉANT chronological planning: "+title)
        ax.tick_params(axis="x",rotation=20)
        bottom,top=ax.get_ylim()
        gap=top-bottom
        ax.set_ylim(bottom,top+.14*gap)
        for i,(successful,total) in enumerate(denoms,1):
            ax.text(i,top+.02*gap,f"{successful}/{total}",ha="center",fontsize=8)
        fig.text(.015,.013,
                 "Exploratory pilot (8 paired seeds, 240 training evaluations). "
                 "Anonymized/scaled traffic. August is NOT a pristine independent industry holdout.",
                 fontsize=8)
        fig.tight_layout(rect=(0,.06,1,.99))
        suffix=("all_44" if metric=="all_period_cost" else "heldout_32")
        filename=f"{prefix}_{suffix}.png"
        fig.savefig(filename,dpi=160)
        plt.close(fig)
        print("PLOT",filename)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--kind",choices=("ieee14","geant"),required=True)
    p.add_argument("--csv",required=True)
    p.add_argument("--prefix",required=True)
    a=p.parse_args()
    with open(a.csv,newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if not rows:
        raise ValueError("Empty raw CSV")
    Path(a.prefix).parent.mkdir(parents=True,exist_ok=True)
    if a.kind=="ieee14":
        ieee_plot(rows,a.prefix)
    else:
        geant_plot(rows,a.prefix)


if __name__=="__main__":
    main()
