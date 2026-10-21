"""Exploratory chronological robustness statistics with multiplicity control.

Official SNDlib anonymized traffic, no claim of truly untouched holdout:
the later August timestamp was examined once for data quality.
All methods are compared at the same objective evaluation budget.
"""
import argparse
import csv
import statistics

import numpy as np
from scipy.stats import wilcoxon


def holm_adjust(p):
    order = sorted(range(len(p)), key=lambda k: p[k])
    adjusted = [None] * len(p)
    running = 0.0
    for position, i in enumerate(order):
        running = max(running, min(1.0, (len(p)-position)*p[i]))
        adjusted[i] = running
    return adjusted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    args = ap.parse_args()
    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    data = {}
    for row in rows:
        data.setdefault(row["method"], {})[int(row["seed"])] = row
    for method, candidates in sorted(data.items()):
        print("ALGORITHM",method,"seeds",len(candidates))
        for metric in ("train_cost","august_cost","all_four_cost"):
            vals = np.array([float(x[metric]) for x in candidates.values()])
            print("DESCRIPTIVE", method, metric,
                  "median",round(float(np.median(vals)),3),
                  "p90",round(float(np.quantile(vals,0.9)),3),
                  "worst",round(float(np.max(vals)),3),
                  "mean",round(float(np.mean(vals)),3),
                  "std",round(float(np.std(vals,ddof=1)),3))

    primary = data["log_relative"]
    tests = []
    for comparison in ("affine_invariant","affine_restart"):
        secondary = data[comparison]
        common = sorted(set(primary)&set(secondary))
        for metric in ("train_cost","august_cost","all_four_cost"):
            diff = np.array([float(secondary[seed][metric])-float(primary[seed][metric])
                             for seed in common])
            rng = np.random.default_rng(20261021)
            resampled = np.median(rng.choice(diff,size=(10000,len(diff)),replace=True),axis=1)
            ci = np.quantile(resampled,[0.025,0.975])
            pval = float(wilcoxon(diff,zero_method="wilcox").pvalue) if np.any(diff) else 1.0
            tests.append(dict(comparison=comparison, metric=metric, n=len(common),
                              paired_median_diff=float(np.median(diff)),
                              ci_low=float(ci[0]),ci_high=float(ci[1]),
                              wins=int(np.sum(diff<0)), losses=int(np.sum(diff>0)),
                              ties=int(np.sum(diff==0)),p=pval))
    corrected = holm_adjust([x["p"] for x in tests])
    for test, padj in zip(tests, corrected):
        print("PAIRED",test["comparison"],test["metric"],"n",test["n"],
              "median_diff_new_minus_legacy",round(test["paired_median_diff"],3),
              "bootstrap95", tuple(round(z,3) for z in (test["ci_low"],test["ci_high"])),
              "wins",test["wins"],"losses",test["losses"],"ties",test["ties"],
              "uncorrected_p",round(test["p"],6),
              "holm_six_comparisons_p",round(padj,6))
    print("LIMITATIONS: posthoc development dataset, 30 independent-seed target,"
          " traffic anonymized/scaled; no real deployment data.")


if __name__ == "__main__":
    main()
