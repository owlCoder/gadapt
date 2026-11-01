"""Paired statistics on genuine SNDlib GÉANT routing-design experiment.

Compare legacy and experimental GAdapt on the same seed/initialization,
report effect magnitude and negative findings. Treat other optimizers
descriptively (same numeric seed does not imply paired RNG samples).
"""
import argparse
import csv
import statistics

import numpy as np
from scipy.stats import wilcoxon


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()
    with open(args.csv, newline="", encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    by_method = {}
    for row in rows:
        by_method.setdefault(row["method"], {})[int(row["seed"])] = float(row["cost"])
    for method, scores in sorted(by_method.items()):
        values = list(scores.values())
        print("GROUP", method, "n=",len(values),
              "median=",statistics.median(values),
              "mean=",round(statistics.mean(values), 3),
              "stddev=",round(statistics.stdev(values), 3) if len(values)>1 else "NA",
              "worst=",max(values), "best=",min(values))
    a, b = by_method["log_relative"], by_method["affine_invariant"]
    seeds = sorted(set(a) & set(b))
    differences = np.array([b[i] - a[i] for i in seeds], dtype=float)
    rng = np.random.default_rng(20261021)
    bootstrap = np.median(rng.choice(differences, size=(10000, len(differences)),
                                     replace=True), axis=1)
    low, high = np.quantile(bootstrap, [0.025, 0.975])
    pvalue = float(wilcoxon(differences, zero_method="wilcox").pvalue) if any(differences) else 1.0
    print("PAIRING", "common_seeds=",len(seeds),
          "affine_minus_legacy_median=",statistics.median(differences),
          "mean=",round(statistics.mean(differences),3),
          "wins_affine=",int(np.sum(differences < 0)),
          "wins_legacy=",int(np.sum(differences > 0)),
          "ties=",int(np.sum(differences == 0)),
          "bootstrap_95_ci_median_diff=", (round(float(low),3),round(float(high),3)),
          "wilcoxon_two_sided_exploratory_p=",round(pvalue,6),
          "NOTE=uncorrected exploratory inference")


if __name__ == "__main__":
    main()
