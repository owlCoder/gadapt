"""Small direct-GAdapt AOS ablation with true IEEE14 AC feasibility signals.

NOT final dissertation validation. Input is a published reference grid,
not operational telemetry. Every true PF solve is budgeted. Evaluations
requested after budget are returned a sentinel and separately counted.
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np
from gadapt.ga import GA
from research.ieee14_voltage import IEEE14VoltageDispatch
from scipy.optimize import differential_evolution


METHODS = ("legacy", "affine", "uniform_objective", "ucb_objective",
           "ucb_feasibility", "scipy_de")


class AccountedObjective:
    def __init__(self, grid, budget):
        self.grid, self.budget = grid, budget
        self.evaluations = 0
        self.requests = 0
        self.cache = {}
        self.best_feasible = float("inf")
        self.best_penalized = float("inf")
        self.feasible_evaluations = 0
        self.pf_failures = 0
        self.feedback_reads = 0
        self.feedback_misses = 0

    def __call__(self, x):
        self.requests += 1
        if self.evaluations >= self.budget:
            return 1e8
        self.evaluations += 1
        values = tuple(float(t) for t in x)
        info = self.grid.evaluate(values)
        self.cache[values] = info
        self.best_penalized = min(self.best_penalized, info["score"])
        if not info["converged"]:
            self.pf_failures += 1
        if info["feasible"]:
            self.feasible_evaluations += 1
            self.best_feasible = min(self.best_feasible, info["loss"])
        return float(info["score"])

    def violation(self, x, cost):
        self.feedback_reads += 1
        info = self.cache.get(tuple(float(t) for t in x))
        if info is None:
            self.feedback_misses += 1
            return 1e12
        if not info["converged"]:
            return 1e12
        # Excess over the SAME declared feasibility tolerances, normalized
        # to dimensionless ratios, so zero means physical feasibility.
        return max(0.0,
                   info["v_max"] / 0.001 - 1.0,
                   info["q_max"] / 0.1 - 1.0,
                   info["branch_max"] / 0.1 - 1.0)


def run(grid, method, seed, budget, population):
    random.seed(seed)
    np.random.seed(seed)
    tracker = AccountedObjective(grid, budget)
    started = time.perf_counter()
    summary = []
    success = True
    error = ""
    if method == "scipy_de":
        factor = max(5, math.ceil(population / grid.n))
        try:
            differential_evolution(tracker, grid.bounds, popsize=factor,
                                   maxiter=math.ceil(budget / (factor * grid.n)),
                                   tol=0, atol=0, polish=False,
                                   rng=np.random.default_rng(seed))
        except Exception as exc:
            success, error = False, str(exc)
    else:
        extra = {
            "cost_diversity_metric": "log_relative" if method == "legacy"
                                     else "affine_invariant",
        }
        if method.startswith(("uniform_", "ucb_")):
            extra["mutation_operator_policy"] = (
                "uniform" if method.startswith("uniform_") else "ucb")
            extra["mutation_operator_credit"] = (
                "feasibility" if method.endswith("feasibility") else "objective")
            if method.endswith("feasibility"):
                extra["mutation_violation_function"] = tracker.violation
        ga = GA(cost_function=tracker, population_size=population,
                exit_check="generations",
                exit_function=lambda: tracker.evaluations >= budget,
                number_of_generations=math.ceil(3 * budget / population) + 10,
                timeout=240, population_mutation="cost_diversity,parent_diversity",
                **extra)
        for low, high in grid.bounds:
            ga.add(low, high)
        try:
            result = ga.execute()
            success = bool(result.success)
            error = result.message if not success else ""
            summary = getattr(result, "operator_credit_summary", [])
        except Exception as exc:
            success, error = False, str(exc)
    return dict(method=method, load_factor=grid.load_factor, seed=seed,
                feasible=bool(math.isfinite(tracker.best_feasible)),
                best_feasible_MW=(tracker.best_feasible if math.isfinite(tracker.best_feasible) else ""),
                best_penalized=tracker.best_penalized,
                objective_evaluations=tracker.evaluations,
                objective_requests=tracker.requests,
                feedback_reads=tracker.feedback_reads,
                feedback_misses=tracker.feedback_misses,
                feasible_evaluations=tracker.feasible_evaluations,
                pf_failures=tracker.pf_failures,
                seconds=round(time.perf_counter()-started, 4),
                operator_selections=sum(a["selections"] for a in summary),
                operator_observations=sum(a["observations"] for a in summary),
                success=success, error=error)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=8)
    parser.add_argument("--budget", type=int, default=240)
    parser.add_argument("--population", type=int, default=24)
    parser.add_argument("--loads", nargs="+", type=float, default=[1.0, 1.1])
    parser.add_argument("--output", default="aos_ieee14_pilot.csv")
    args = parser.parse_args()
    if args.runs < 1 or args.budget < args.population:
        parser.error("runs must be positive, budget >= population")
    rows = []
    for factor in args.loads:
        grid = IEEE14VoltageDispatch(factor)
        for seed in range(args.runs):
            for method in METHODS:
                row = run(grid, method, seed, args.budget, args.population)
                rows.append(row)
                print("RUN", row, flush=True)
        for method in METHODS:
            group = [r for r in rows if r["load_factor"] == factor and r["method"] == method]
            feas = [r["best_feasible_MW"] for r in group if r["feasible"]]
            print("SUMMARY", factor, method,
                  "successes", sum(r["feasible"] and r["success"] for r in group),
                  "/", len(group),
                  "median_feasible", statistics.median(feas) if feas else "NA",
                  "median_seconds", statistics.median(r["seconds"] for r in group),
                  flush=True)
    with open(args.output, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if any(r["objective_evaluations"] != args.budget for r in rows):
        print("WARNING: some runs did not expend all physical evaluations", flush=True)
    if any(r["feedback_misses"] for r in rows):
        print("WARNING: feedback was requested without a cached physical evaluation", flush=True)


if __name__ == "__main__":
    main()
