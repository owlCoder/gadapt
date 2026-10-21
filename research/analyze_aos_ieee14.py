"""Failure-aware exploratory analysis of direct GAdapt/IEEE14 AOS CSV.

Not a preregistered confirmatory test. No deletion or MW imputation of
failed runs. Feasibility has a Wilson CI; conditional MW statistics are
reported with an explicit denominator. Multiplicity corrected per load.
"""
import argparse
import csv
import math
import statistics

import numpy as np
from scipy.stats import binomtest, wilcoxon

METHODS = ("affine", "uniform_objective", "ucb_objective",
           "ucb_feasibility", "scipy_de")


def wilson(k, n, z=1.959963984540054):
    if not n:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    width = (z / denom) * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return (center-width, center+width)


def empirical_quantile(values, q):
    return float(np.quantile(np.asarray(values), q)) if values else float("nan")


def boot_median_ci(values, seed=20261021, n_resamples=3000):
    if not values:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, float)
    sampling = rng.integers(0, len(arr), (n_resamples, len(arr)))
    dist = np.median(arr[sampling], axis=1)
    return tuple(float(v) for v in np.quantile(dist, [0.025, 0.975]))


def rank(out_a, out_b):
    """-1: a is better; 1: b is better; 0 tie; failures included."""
    if out_a["feasible"] != out_b["feasible"]:
        return -1 if out_a["feasible"] else 1
    if out_a["feasible"]:
        return -1 if out_a["MW"] < out_b["MW"] else (
            1 if out_a["MW"] > out_b["MW"] else 0)
    return 0  # two physical failures: no fictitious ordered MW value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()
    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    data = {}
    for row in rows:
        key = (float(row["load_factor"]), row["method"], int(row["seed"]))
        if key in data:
            raise ValueError("Duplicate matched seed "+str(key))
        data[key] = dict(
            feasible=row["feasible"] == "True" and row["success"] == "True",
            MW=float(row["best_feasible_MW"]) if row["best_feasible_MW"] else float("nan"),
            seconds=float(row["seconds"]),
            calls=int(row["objective_evaluations"]),
            requests=int(row["objective_requests"]),
            feedback_misses=int(row["feedback_misses"]),
        )
    for load in sorted(set(k[0] for k in data)):
        seeds = sorted(set(k[2] for k in data if k[0] == load))
        print("LOAD", load, "paired_seeds", len(seeds))
        for method in ("legacy",)+METHODS:
            group = [data[(load, method, s)] for s in seeds]
            successes = [x["MW"] for x in group if x["feasible"]]
            k = len(successes)
            print("METHOD", method, "feasible", k, "/", len(group),
                  "wilson95", wilson(k,len(group)),
                  "conditional_median_MW", statistics.median(successes) if successes else "NA",
                  "conditional_q90_MW", empirical_quantile(successes, 0.90),
                  "worst_MW", max(successes) if successes else "NA",
                  "median_seconds", statistics.median(x["seconds"] for x in group),
                  "actual_pf_calls_range", (min(x["calls"] for x in group),
                                           max(x["calls"] for x in group)),
                  "excess_objective_requests", sum(x["requests"]-x["calls"] for x in group),
                  "callback_cache_misses", sum(x["feedback_misses"] for x in group))
        comparisons = []
        for method in METHODS:
            mine = [data[(load,method,s)] for s in seeds]
            orig = [data[(load,"legacy",s)] for s in seeds]
            outcomes = [rank(a,b) for a,b in zip(mine,orig)]
            wins, losses, ties = (outcomes.count(-1), outcomes.count(1), outcomes.count(0))
            sign_p = binomtest(wins, wins+losses, .5).pvalue if wins+losses else 1.0
            f_gain = sum(a["feasible"] and not b["feasible"] for a,b in zip(mine,orig))
            f_loss = sum(b["feasible"] and not a["feasible"] for a,b in zip(mine,orig))
            f_p = binomtest(f_gain, f_gain+f_loss, .5).pvalue if f_gain+f_loss else 1.0
            paired = [a["MW"]-b["MW"] for a,b in zip(mine,orig)
                      if a["feasible"] and b["feasible"]]
            pair_p = float(wilcoxon(paired).pvalue) if len(paired)>=6 and any(v!=0 for v in paired) else float("nan")
            comparisons.append((method, wins, losses, ties, sign_p, f_gain, f_loss,
                                f_p, paired, pair_p))
        # Pre-label all five comparisons as exploratory; Holm familywise control
        # is applied to composite paired wins/losses. A test on conditional MW
        # has selection bias when feasibility differs and is secondary.
        order = sorted(range(len(comparisons)), key=lambda i: comparisons[i][4])
        adjusted = [0.0]*len(comparisons)
        running = 0.0
        for pos, i in enumerate(order):
            running = max(running, min(1.0, (len(order)-pos)*comparisons[i][4]))
            adjusted[i] = running
        for i, (m,w,l,t,p,fg,fl,fp,pairs,pwp) in enumerate(comparisons):
            print("PAIRED",m,"wins",w,"losses",l,"ties",t,
                  "sign_p",p,"holm_p",adjusted[i],
                  "feasibility_gain_loss",f"{fg}/{fl}","mcnemar_exact_p",fp,
                  "both_feasible",len(pairs),
                  "median_difference_MW",statistics.median(pairs) if pairs else "NA",
                  "paired_boot95",boot_median_ci(pairs),
                  "conditional_wilcoxon_p",pwp)
    if any(row["error"] for row in rows):
        print("ALERT: optimiser errors recorded; do NOT discard")
    print("INTERPRETATION: exploratory small pilot; no novel-method or industrial claim")


if __name__ == "__main__":
    main()
