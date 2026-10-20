"""AC power-grid benchmark on public IEEE test networks (real pandapower solver).

This evaluates unchanged GAdapt, the opt-in affine diversity variant, and
SciPy Differential Evolution on the same active-loss minimization task.
All candidates undergo AC power flow; voltage/thermal limits are independently
rechecked at the final solution. This is a public NETWORK BENCHMARK, not
measured live utility telemetry and not evidence of field deployment.

Install: pip install -e . 'pandapower==2.14.11' 'scipy==1.13.1'
Run: python research/ieee_grid_benchmark.py --runs 5
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np
from scipy.optimize import differential_evolution
import pandapower as pp
import pandapower.networks as pn

from gadapt.ga import GA

GRIDS = {"ieee14": pn.case14, "ieee118": pn.case118, "rte1888": pn.case1888rte}
LOW_VOLTAGE = 0.94
HIGH_VOLTAGE = 1.08
LINE_LIMIT_PERCENT = 100.0
GEN_VOLTAGE_BOUNDS = (0.95, 1.08)
PENALTY_WEIGHT = 1e5


class GridProblem:
    """Stateful AC evaluator with explicit final feasibility checks."""

    def __init__(self, case, load_factor):
        if case not in GRIDS:
            raise ValueError(case)
        self.case = case
        self.load_factor = load_factor
        self.net = GRIDS[case]()
        self.net.load["p_mw"] *= load_factor
        self.net.load["q_mvar"] *= load_factor
        self.gen_ids = list(self.net.gen.index[:min(len(self.net.gen), 8)])
        if not self.gen_ids:
            raise ValueError("No generators for voltage control")
        self.reference = self.net.gen.loc[self.gen_ids, "vm_pu"].to_numpy(copy=True)
        self.calls = 0

    @property
    def dimension(self):
        return len(self.gen_ids)

    def evaluate(self, x, count=True):
        if count:
            self.calls += 1
        for idx, value in zip(self.gen_ids, x):
            self.net.gen.at[idx, "vm_pu"] = float(value)
        try:
            pp.runpp(
                self.net, init="flat", algorithm="nr",
                calculate_voltage_angles=True, numba=False,
                enforce_q_lims=True, max_iteration=40, tolerance_mva=1e-8,
            )
            v = self.net.res_bus.vm_pu.to_numpy(dtype=float)
            l = self.net.res_line.loading_percent.to_numpy(dtype=float)
            t = self.net.res_trafo.loading_percent.to_numpy(dtype=float)
            ploss = float(self.net.res_line.pl_mw.sum() +
                          self.net.res_trafo.pl_mw.sum())
            if (not np.isfinite(ploss) or
                not np.all(np.isfinite(v)) or
                not np.all(np.isfinite(l)) or
                not np.all(np.isfinite(t))):
                raise ArithmeticError("Non-finite grid output")
            voltage_violation = (
                np.maximum(LOW_VOLTAGE-v, 0.0).sum() +
                np.maximum(v-HIGH_VOLTAGE, 0.0).sum()
            )
            overload = (
                np.maximum(l-LINE_LIMIT_PERCENT, 0.0).sum() +
                np.maximum(t-LINE_LIMIT_PERCENT, 0.0).sum()
            ) / 100.0
            violation = float(voltage_violation + overload)
            return {
                "loss": ploss,
                "violation": violation,
                "feasible": bool(violation <= 1e-8),
                "minimum_voltage": float(np.min(v)),
                "maximum_voltage": float(np.max(v)),
                "maximum_loading": float(max(np.max(l, initial=0.0),
                                              np.max(t, initial=0.0))),
                "objective": ploss + PENALTY_WEIGHT * violation,
                "solver_failed": False,
            }
        except (Exception, ArithmeticError):
            # Do not invent an apparently feasible grid state on solver failure.
            return dict(loss=math.nan, violation=math.inf, feasible=False,
                        minimum_voltage=math.nan, maximum_voltage=math.nan,
                        maximum_loading=math.nan, objective=1e12,
                        solver_failed=True)

    def objective(self, values):
        return float(self.evaluate(values)["objective"])


def run_one(case, load_factor, algorithm, seed, population, ga_generations):
    grid = GridProblem(case, load_factor)
    baseline = grid.evaluate(grid.reference, count=False)
    random.seed(seed)
    np.random.seed(seed)
    start = time.perf_counter()
    if algorithm == "de":
        multiplier = max(1, math.ceil(population / grid.dimension))
        de_generations = max(1, math.ceil((population * 0.5 *
                                          ga_generations) /
                                         (multiplier * grid.dimension)))
        result = differential_evolution(
            grid.objective,
            [GEN_VOLTAGE_BOUNDS] * grid.dimension,
            strategy="best1bin", popsize=multiplier,
            maxiter=de_generations, seed=seed, polish=False,
            tol=0.0, atol=0.0, updating="immediate",
        )
        values = result.x
        success = bool(np.isfinite(result.fun))
    else:
        metric = ("log_relative" if algorithm == "gadapt_original"
                  else "affine_invariant")
        ga = GA(
            cost_function=grid.objective,
            cost_diversity_metric=metric,
            population_size=population,
            exit_check="generations", number_of_generations=ga_generations,
            population_mutation="cost_diversity,parent_diversity",
            timeout=240,
        )
        for _ in grid.gen_ids:
            ga.add(*GEN_VOLTAGE_BOUNDS)
        result = ga.execute()
        success = bool(result.success)
        values = [result.result_values[i] for i in range(grid.dimension)] if success else grid.reference
    runtime = time.perf_counter()-start
    # Independent final AC power flow, not based on the algorithm's penalty value.
    checked = grid.evaluate(values, count=False)
    return dict(
        case=case, load_factor=load_factor, algorithm=algorithm, seed=seed,
        dimension=grid.dimension, evaluations=grid.calls, runtime_sec=round(runtime, 4),
        converged=success, solver_failed=checked["solver_failed"],
        feasible=checked["feasible"], loss_mw=checked["loss"],
        violation=checked["violation"], minimum_voltage=checked["minimum_voltage"],
        maximum_voltage=checked["maximum_voltage"],
        maximum_loading_percent=checked["maximum_loading"],
        baseline_loss_mw=baseline["loss"], baseline_feasible=baseline["feasible"],
        baseline_violation=baseline["violation"],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", nargs="+", choices=list(GRIDS), default=["ieee14", "ieee118"])
    parser.add_argument("--loads", nargs="+", type=float, default=[1.0, 1.15])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--population", type=int, default=16)
    parser.add_argument("--ga-generations", type=int, default=28)
    parser.add_argument("--output", default="ieee_grid_results.csv")
    args = parser.parse_args()
    if args.runs < 1 or args.population < 8:
        parser.error("runs >= 1 and population >= 8 are required")
    if any(load <= 0 for load in args.loads):
        parser.error("Load multipliers must be positive")
    rows = []
    for case in args.cases:
        for load_factor in args.loads:
            for seed in range(args.runs):
                for algorithm in ("gadapt_original", "gadapt_affine", "de"):
                    row = run_one(
                        case, load_factor, algorithm, seed,
                        args.population, args.ga_generations,
                    )
                    rows.append(row)
                    print("RUN", case, load_factor, seed, algorithm,
                          "feasible", row["feasible"], "loss", row["loss_mw"],
                          "evaluations", row["evaluations"], flush=True)
    with open(args.output, "w", encoding="utf-8", newline="") as file:
        w = csv.DictWriter(file, rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    for case in args.cases:
        for load_factor in args.loads:
            for algorithm in ("gadapt_original", "gadapt_affine", "de"):
                selected = [r for r in rows if
                            r["case"] == case and
                            r["load_factor"] == load_factor and
                            r["algorithm"] == algorithm]
                good = [r["loss_mw"] for r in selected if r["feasible"]]
                print("SUMMARY", case, load_factor, algorithm,
                      "feasible_rate", len(good)/len(selected),
                      "median_feasible_loss_mw",
                      statistics.median(good) if good else "none",
                      "median_eval", statistics.median(
                          [r["evaluations"] for r in selected]),
                      flush=True)


if __name__ == "__main__":
    main()
