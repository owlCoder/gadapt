"""French RTE1888 case: predeclared NEGATIVE feasibility stress-test.

The reference case is already infeasible (nonzero physical overload) with
only eight generator-voltage controls. Never call a smaller penalty
'feasible'. 12 method-runs, 72 genuine pandapower NR solves each.
"""
import argparse
import csv
import math
import statistics
from research.ieee118_allocation import run

METHODS=("gadapt_legacy","slsqp_multistart","hybrid_adaptive","scipy_de")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="rte1888_iteration6.csv")
    args=p.parse_args()
    rows=[]
    for seed in (300,301,302):
        for method in METHODS:
            row=run("rte1888",1.0,method,seed,72,12)
            rows.append(row)
            print("RUN",row,flush=True)
    for method in METHODS:
        sample=[r for r in rows if r["method"]==method]
        feasible=[r["feasible_loss_mw"] for r in sample
                  if r["physically_feasible"] and r["optimizer_success"]]
        violations=[r["min_observed_violation"] for r in sample
                    if r["min_observed_violation"] != ""]
        print("SUMMARY",method,
              "independently_feasible",len(feasible),"/",len(sample),
              "median_feasible_mw",statistics.median(feasible) if feasible else "NA",
              "median_min_violation",statistics.median(violations) if violations else "NA",
              "worst_min_violation",max(violations) if violations else "NA",
              "solver_calls_range",(min(r["actual_solver_calls"] for r in sample),
                                     max(r["actual_solver_calls"] for r in sample)),
              "nonconvergent_solver_calls",sum(r["converged_solver_failures"] for r in sample),
              flush=True)
    with open(args.output,"w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if len(rows)!=12 or any(r["actual_solver_calls"]!=72 for r in rows):
        raise ValueError("Missing RTE stress rows or mismatched true AC solver budget")
    if all(not r["physically_feasible"] for r in rows):
        print("NEGATIVE: no physically feasible solution to this 8-voltage-control RTE subset, "
              "compare violation magnitude only; do NOT report a feasible loss optimum.",flush=True)


if __name__=="__main__":main()
