"""Reproducible IEEE 14-bus AC voltage-control benchmark for actual GAdapt.

IEEE CDF 14-bus is a STANDARDIZED REFERENCE SYSTEM, not operational utility
measurements. Optimizes PV/slack generator voltage setpoints while evaluating
nonlinear AC load flow. Independent feasibility metrics check bus V, generator
Q, and branch apparent power (only where the reference dataset has RATE_A).
A finite penalty guides search but never establishes feasibility by itself.

pip install -e . scipy pypower
python research/ieee14_voltage.py --runs 20 --budget 640 --output ieee14.csv
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np
from gadapt.ga import GA
from pypower.api import case14, ppoption, runpf
from pypower.idx_bus import PD, QD, VM, VMIN, VMAX
from pypower.idx_gen import VG, QG, QMIN, QMAX, GEN_BUS
from pypower.idx_brch import RATE_A, PF, QF, PT, QT
from scipy.optimize import differential_evolution


class IEEE14VoltageDispatch:
    def __init__(self, load_factor=1.0):
        self.base = case14()
        self.base["bus"][:, PD] *= load_factor
        self.base["bus"][:, QD] *= load_factor
        self.load_factor = load_factor
        self.settings = ppoption(VERBOSE=0, OUT_ALL=0, ENFORCE_Q_LIMS=0,
                                 PF_TOL=1e-8, PF_MAX_IT=25)
        self.gen_bus_idx = self.base["gen"][:, GEN_BUS].astype(int) - 1
        self.bounds = [(float(self.base["bus"][bus, VMIN]),
                        float(self.base["bus"][bus, VMAX]))
                       for bus in self.gen_bus_idx]
        self.n = len(self.bounds)
        self.base_mva = float(self.base["baseMVA"])

    def evaluate(self, x):
        case = {k: (v.copy() if isinstance(v, np.ndarray) else v)
                for k, v in self.base.items()}
        case["gen"][:, VG] = np.asarray(x, dtype=float)
        try:
            solved, converged = runpf(case, self.settings)
        except (ValueError, ArithmeticError, RuntimeError, IndexError):
            converged = False
        if not converged:
            return dict(score=1e8, feasible=False, loss=float("nan"),
                        converged=False, v_max=float("inf"),
                        q_max=float("inf"), branch_max=float("inf"))
        bus, gen, branch = solved["bus"], solved["gen"], solved["branch"]
        if not all(np.isfinite(a).all() for a in (bus, gen, branch)):
            return dict(score=1e8, feasible=False, loss=float("nan"),
                        converged=False, v_max=float("inf"),
                        q_max=float("inf"), branch_max=float("inf"))
        v = np.maximum.reduce([bus[:, VM] - bus[:, VMAX],
                               bus[:, VMIN] - bus[:, VM], np.zeros(len(bus))])
        q = np.maximum.reduce([gen[:, QG] - gen[:, QMAX],
                               gen[:, QMIN] - gen[:, QG], np.zeros(len(gen))])
        ratings = branch[:, RATE_A]
        thermal = np.maximum(np.maximum(np.hypot(branch[:, PF], branch[:, QF]),
                                        np.hypot(branch[:, PT], branch[:, QT])) - ratings, 0)
        thermal[ratings <= 0] = 0  # missing thermal ratings are NOT inferred
        loss = float(np.sum(branch[:, PF] + branch[:, PT]))
        if not math.isfinite(loss):
            return dict(score=1e8, feasible=False, loss=float("nan"),
                        converged=False, v_max=float("inf"),
                        q_max=float("inf"), branch_max=float("inf"))
        score = loss + 5000 * float(np.sum(v*v)) + \
                1000 * float(np.sum((q/self.base_mva)**2)) + \
                1000 * float(np.sum((thermal/self.base_mva)**2))
        v_max, q_max, branch_max = map(float, (max(v), max(q), max(thermal)))
        feasible = v_max <= 1e-3 and q_max <= 0.1 and branch_max <= 0.1
        return dict(score=score, feasible=feasible, loss=loss, converged=True,
                    v_max=v_max, q_max=q_max, branch_max=branch_max)


class Recorder:
    def __init__(self, system, budget):
        self.system, self.budget = system, budget
        self.count, self.feasible_count, self.failures = 0, 0, 0
        self.best_feasible, self.best_score = float("inf"), float("inf")

    def __call__(self, x):
        if self.count >= self.budget:
            return 1e8
        self.count += 1
        info = self.system.evaluate(x)
        self.best_score = min(self.best_score, info["score"])
        if not info["converged"]:
            self.failures += 1
        if info["feasible"]:
            self.feasible_count += 1
            self.best_feasible = min(self.best_feasible, info["loss"])
        return float(info["score"])


def evaluate_method(system, method, seed, budget=480, pop=24):
    recorder = Recorder(system, budget)
    start = time.perf_counter()
    if method == "scipy_de":
        factor = max(5, math.ceil(pop / system.n))
        differential_evolution(
            recorder, system.bounds, popsize=factor,
            maxiter=math.ceil(budget / (factor * system.n)),
            tol=0, atol=0, polish=False, rng=np.random.default_rng(seed),
        )
        success = True
    else:
        random.seed(seed)
        np.random.seed(seed)
        extra = (dict(adaptive_immigration_patience=4,
                      adaptive_immigration_percentage=25.0,
                      adaptive_immigration_diversity_threshold=0.25)
                 if method == "affine_restart" else {})
        ga = GA(
            cost_function=lambda values: recorder([values[i] for i in range(system.n)]),
            population_size=pop, cost_diversity_metric=("affine_invariant" if method == "affine_restart" else method),
            exit_check="generations",
            number_of_generations=math.ceil(3 * budget / pop) + 10,
            population_mutation="cost_diversity,parent_diversity",
            timeout=240,
            **extra,
        )
        for lower, upper in system.bounds:
            ga.add(lower, upper)
        output = ga.execute()
        success = bool(output.success)
    return dict(load_factor=system.load_factor, algorithm=method, seed=seed,
                evaluations=recorder.count, seconds=round(time.perf_counter()-start, 3),
                feasible_loss_MW=recorder.best_feasible if math.isfinite(recorder.best_feasible) else "",
                best_penalized=recorder.best_score,
                feasible_evaluations=recorder.feasible_count,
                pf_failures=recorder.failures, success=success)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--budget", type=int, default=640)
    parser.add_argument("--population", type=int, default=24)
    parser.add_argument("--load-factors", nargs="+", type=float, default=[1., 1.1])
    parser.add_argument("--output", default="ieee14.csv")
    args = parser.parse_args()
    if args.runs <= 0 or args.budget < 25:
        parser.error("--runs must be >0 and --budget >=25")
    rows = []
    for factor in args.load_factors:
        system = IEEE14VoltageDispatch(factor)
        print("REFERENCE", factor,
              system.evaluate(system.base["gen"][:, VG]), flush=True)
        for seed in range(args.runs):
            for method in ("log_relative", "affine_invariant", "affine_restart", "scipy_de"):
                rows.append(evaluate_method(system, method, seed, args.budget, args.population))
        for method in ("log_relative", "affine_invariant", "affine_restart", "scipy_de"):
            selected = [r for r in rows if r["load_factor"] == factor and r["algorithm"] == method]
            feasible = [r["feasible_loss_MW"] for r in selected if r["feasible_loss_MW"] != ""]
            print("SUMMARY", "load=", factor, "method=", method,
                  "feasible_runs=", len(feasible), "/", len(selected),
                  "median_feasible_MW=", statistics.median(feasible) if feasible else "NA",
                  "median_evaluations=", statistics.median(r["evaluations"] for r in selected),
                  "median_seconds=", statistics.median(r["seconds"] for r in selected),
                  flush=True)
    with open(args.output, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if any(r["evaluations"] != args.budget for r in rows):
        print("WARNING: not every algorithm used its full evaluation budget", flush=True)


if __name__ == "__main__":
    main()
