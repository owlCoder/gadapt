"""Reliability-first summary for IEEE14 AC benchmark CSV.

Success means at least one independently verified feasible AC solution, not
merely return of an optimizer object. Never impute missing feasible losses as
zero. Wilson confidence intervals are descriptive and assume independent seeds.
"""
import argparse
import csv
import math
import statistics
from collections import defaultdict


def wilson(success, total, z=1.959963984540054):
    if not total:
        return (float("nan"), float("nan"))
    p = success / total
    d = 1 + z*z/total
    c = (p + z*z/(2*total))/d
    h = z * math.sqrt((p*(1-p) + z*z/(4*total))/total)/d
    return (max(0., c-h), min(1., c+h))


def summarize(path):
    with open(path, newline="", encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    for row in rows:
        groups[(row["load_factor"], row["algorithm"])].append(row)
    print("SCENARIO,ALGORITHM,N,SUCCESS,WILSON95_LO,WILSON95_HI,"
          "MEDIAN_FEASIBLE_LOSS_MW,MAX_FEASIBLE_LOSS_MW,MEDIAN_EVALS,MEDIAN_SEC")
    for (load, algo), group in sorted(groups.items()):
        losses = [float(row["feasible_loss_MW"])
                  for row in group if row["feasible_loss_MW"] != ""]
        lo, hi = wilson(len(losses), len(group))
        print(",".join(map(str, [
            load, algo, len(group), len(losses),
            round(lo, 4), round(hi, 4),
            round(statistics.median(losses), 6) if losses else "NA",
            round(max(losses), 6) if losses else "NA",
            statistics.median(int(x["evaluations"]) for x in group),
            round(statistics.median(float(x["seconds"]) for x in group), 3),
        ])))
    # Unsuccessful runs count as explicit reliability failures. Paired SEED IDs
    # do NOT imply common initial populations across algorithms.
    for load in sorted(set(key[0] for key in groups)):
        by_algo = {algo: {r["seed"]: (r["feasible_loss_MW"] != "")
                          for r in group}
                   for (load_key, algo), group in groups.items() if load_key == load}
        if "log_relative" in by_algo and "affine_invariant" in by_algo:
            common = sorted(set(by_algo["log_relative"]) & set(by_algo["affine_invariant"]))
            a_only = sum(by_algo["affine_invariant"][seed] and
                         not by_algo["log_relative"][seed] for seed in common)
            legacy_only = sum(by_algo["log_relative"][seed] and
                              not by_algo["affine_invariant"][seed] for seed in common)
            print("DISCORDANT", load, "affine_only=", a_only,
                  "legacy_only=", legacy_only, "common_seeds=", len(common))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()
    summarize(args.csv)
