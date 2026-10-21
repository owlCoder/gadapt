"""Re-analyze persisted RTE1888 physical violation measurements, without MW imputation."""
import argparse
import csv
import math
import statistics

METHODS=("gadapt_legacy","slsqp_multistart","hybrid_adaptive","scipy_de")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("csv")
    args=parser.parse_args()
    with open(args.csv,newline="",encoding="utf8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=12:
        raise ValueError("Expected 12 measured RTE trials")
    keys={(r["method"],int(r["seed"])) for r in rows}
    if len(keys)!=12:
        raise ValueError("Duplicate RTE measurement keys")
    for method in METHODS:
        group=sorted([r for r in rows if r["method"]==method],
                     key=lambda r:int(r["seed"]))
        if [int(r["seed"]) for r in group]!=[300,301,302]:
            raise ValueError("Missing frozen paired RTE seeds")
        if any(int(r["actual_solver_calls"])!=72 for r in group):
            raise ValueError("Unequal true RTE AC solver budgets")
        feasible=[r for r in group if r["optimizer_success"]=="True" and
                  r["physically_feasible"]=="True"]
        bad=[r for r in group if r["optimizer_success"]!="True"]
        violations=[float(r["min_observed_violation"]) for r in group
                    if r["min_observed_violation"]]
        print("RTE",method,"actually_feasible",len(feasible),"/",len(group),
              "optimizer_errors",len(bad),
              "median_min_aggregated_violation",(
                statistics.median(violations) if violations else "NA"),
              "best_min_aggregated_violation",min(violations) if violations else "NA",
              "worst_min_aggregated_violation",max(violations) if violations else "NA",
              "AC_solver_failures",sum(int(r["converged_solver_failures"])
                                        for r in group),
              "real_NR_calls",72*len(group),flush=True)
    print("CAUTION: Nonzero aggregate violation means infeasible, regardless of its reduction. "
          "Only eight continuous generator-voltage controls were optimized. "
          "No claim of global or feasible RTE optimum.",flush=True)


if __name__=="__main__":
    main()
