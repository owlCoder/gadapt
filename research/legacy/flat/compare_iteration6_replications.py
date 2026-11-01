"""Audit sensitivity of matched IEEE118 experiments to runner environment.

Does NOT use the repeated results as independent seeds. Requires two
72-run records, same method-load-seed keys and true physical budgets.
Never averages duplicated runs as though they were independent trials.
"""
import argparse
import csv
import math
import statistics


def load(path):
    with open(path,newline="",encoding="utf8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=72:raise ValueError(f"Expected 72 rows in {path}")
    indexed={}
    for r in rows:
        key=(float(r["load_factor"]),r["method"],int(r["seed"]))
        if key in indexed:raise ValueError("duplicate key "+str(key))
        if int(r["actual_solver_calls"])!=180:
            raise ValueError("Nonmatching actual physics budget "+str(key))
        indexed[key]=r
    return indexed


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("first")
    ap.add_argument("second")
    a=ap.parse_args()
    before,after=load(a.first),load(a.second)
    if set(before)!=set(after):raise ValueError("Matched keys differ")
    methods=sorted(set(k[1] for k in before))
    for method in methods:
        keys=sorted(k for k in before if k[1]==method)
        delta=[]
        agree=0
        samevectors=0
        samefeas=0
        decisionagree=0
        for key in keys:
            r,s=before[key],after[key]
            x=float(r["feasible_loss_mw"]) if r["feasible_loss_mw"] else math.nan
            y=float(s["feasible_loss_mw"]) if s["feasible_loss_mw"] else math.nan
            if math.isfinite(x) and math.isfinite(y):
                delta.append(abs(y-x))
                if x==y:agree+=1
            if r["best_physical_feasible_voltages"]==s["best_physical_feasible_voltages"]:
                samevectors+=1
            if r["physically_feasible"]==s["physically_feasible"]:
                samefeas+=1
            if r["adaptive_decision"]==s["adaptive_decision"]:
                decisionagree+=1
        print("REPLAY",method,"n",len(keys),
              "feasibility_agreement",samefeas,
              "decision_agreement",decisionagree,
              "same_incumbent_vector",samevectors,
              "exact_same_feasible_loss",agree,
              "median_absolute_loss_MW",statistics.median(delta) if delta else "NA",
              "max_absolute_loss_MW",max(delta) if delta else "NA",flush=True)
    print("CAVEAT: second run is SAME public task with SAME paired seeds. "
          "It measures repeatability, not independent statistical replication.")


if __name__=="__main__":
    main()
