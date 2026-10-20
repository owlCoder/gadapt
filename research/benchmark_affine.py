"""Reproducible exploratory GAdapt benchmark for cost-diversity transforms.

Uses the ACTUAL gadapt.GA, not a stand-in optimizer. Not a full dissertation
validation or a fair comparison against an independent solver.
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np

from gadapt.ga import GA


def sphere(x):
    return float(sum(v * v for v in x))


def rastrigin(x):
    return float(10 * len(x) + sum(v * v - 10 * math.cos(2 * math.pi * v) for v in x))


FUNCTIONS = {"sphere": (sphere, -5.0, 5.0), "rastrigin": (rastrigin, -5.12, 5.12)}


def run_once(name, dimensions, metric, shift, seed, population, generations):
    fun, low, high = FUNCTIONS[name]
    nfev = [0]

    def objective(x):
        nfev[0] += 1
        return float(fun(x) + shift)

    # Legacy GAdapt uses global random / NumPy RNGs. Reset both per run
    # for comparable starts. This is not thread-safe.
    random.seed(seed)
    np.random.seed(seed)
    ga = GA(
        cost_function=objective, cost_diversity_metric=metric,
        population_size=population, exit_check="generations",
        number_of_generations=generations, timeout=120,
        population_mutation="cost_diversity,parent_diversity",
    )
    for _ in range(dimensions):
        ga.add(low, high)
    start = time.perf_counter()
    result = ga.execute()
    seconds = time.perf_counter() - start
    if not result.success:
        raise RuntimeError(result.message)
    return dict(
        function=name, dimensions=dimensions, metric=metric, shift=shift,
        seed=seed, minimum=float(result.min_cost - shift),
        evaluations=nfev[0], seconds=seconds, generations=result.number_of_iterations,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--generations", type=int, default=150)
    parser.add_argument("--population", type=int, default=32)
    parser.add_argument("--dimensions", type=int, nargs="+", default=[2, 7])
    parser.add_argument("--output", default="affine_results.csv")
    args = parser.parse_args()
    rows = []
    for name in FUNCTIONS:
        for dim in args.dimensions:
            for seed in range(args.runs):
                for metric in ("log_relative", "affine_invariant"):
                    for shift in (0.0, 1000.0):
                        rows.append(run_once(name, dim, metric, shift, seed,
                                             args.population, args.generations))
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    for name in FUNCTIONS:
        for dim in args.dimensions:
            for metric in ("log_relative", "affine_invariant"):
                base = {(r["seed"]): r["minimum"] for r in rows if
                        r["function"] == name and r["dimensions"] == dim and
                        r["metric"] == metric and r["shift"] == 0.0}
                shifted = {(r["seed"]): r["minimum"] for r in rows if
                           r["function"] == name and r["dimensions"] == dim and
                           r["metric"] == metric and r["shift"] == 1000.0}
                diffs = [abs(base[s] - shifted[s]) for s in base]
                print(name, dim, metric,
                      "median_best=", statistics.median(base.values()),
                      "median_shift_invariance_error=", statistics.median(diffs),
                      "max_shift_invariance_error=", max(diffs))


if __name__ == "__main__":
    main()
