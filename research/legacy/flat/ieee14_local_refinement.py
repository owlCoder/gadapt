"""Direct actual GAdapt + PYPOWER experiment: strict physical-cost-matched memetic audit.

Not a globally optimal AC-OPF solver; 5 voltage setpoints with unchanged
active dispatch, transformer taps and shunts. Protocol frozen in
research/ITERATION5_PROTOCOL.md BEFORE implementation and execution.
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np
from scipy.optimize import differential_evolution, minimize
from pypower.idx_gen import VG
from gadapt.ga import GA
from research.ieee14_voltage import IEEE14VoltageDispatch

METHODS = ("legacy_gadapt", "affine_gadapt", "slsqp_multistart",
           "hybrid_gadapt_slsqp", "scipy_de")


class PhysicalBudgetEnded(Exception):
    """Intentional strict stop: optimizer asked for another physical evaluation."""


class PhysicalRecorder:
    def __init__(self, system, budget):
        self.system = system
        self.budget = int(budget)
        self.stage_cap = self.budget
        self.evaluations = 0
        self.requests = 0
        self.best_feasible = math.inf
        self.best_feasible_vector = None
        self.best_penalized = math.inf
        self.best_penalized_vector = None
        self.feasible_count = 0
        self.pf_failures = 0
        self.filler_evaluations = 0
        self.slsqp_starts = 0
        self.slsqp_failed_starts = 0

    def __call__(self, x):
        self.requests += 1
        if self.evaluations >= min(self.budget, self.stage_cap):
            return 1e8  # not a physical solve, never recorded as an incumbent
        self.evaluations += 1
        values = tuple(float(v) for v in x)
        info = self.system.evaluate(values)
        if not info["converged"]:
            self.pf_failures += 1
        score = float(info["score"])
        if not math.isfinite(score):
            raise ValueError("AC penalized objective not finite")
        if score < self.best_penalized:
            self.best_penalized = score
            self.best_penalized_vector = values
        if info["feasible"]:
            self.feasible_count += 1
            if float(info["loss"]) < self.best_feasible:
                self.best_feasible = float(info["loss"])
                self.best_feasible_vector = values
        return score

    def strict(self, x):
        if self.evaluations >= min(self.budget, self.stage_cap):
            self.requests += 1
            raise PhysicalBudgetEnded()
        return self(x)

    def start_point(self):
        if self.best_feasible_vector is not None:
            return np.array(self.best_feasible_vector)
        if self.best_penalized_vector is not None:
            return np.array(self.best_penalized_vector)
        return np.array(self.system.base["gen"][:, VG], dtype=float)


def run_ga(system, recorder, seed, population, metric):
    random.seed(seed)
    np.random.seed(seed)
    ga = GA(cost_function=recorder, population_size=population,
            cost_diversity_metric=metric,
            exit_check="generations", exit_function=lambda: (
                recorder.evaluations >= recorder.stage_cap),
            number_of_generations=math.ceil(
                5 * recorder.stage_cap / population) + 12,
            timeout=240, population_mutation="cost_diversity,parent_diversity")
    for lo, hi in system.bounds:
        ga.add(lo, hi)
    res = ga.execute()
    return bool(res.success), str(res.message) if not res.success else ""


def run_slsqp(system, recorder, seed, initial, prioritize_incumbent=True):
    rng = np.random.default_rng(seed+919)
    lower, upper = np.array(system.bounds, dtype=float).T
    first = np.clip(np.asarray(initial, float), lower, upper)
    failures = []
    while recorder.evaluations < recorder.stage_cap:
        # The first local descent starts at the best physically VERIFIED GA
        # control, not at a postbudget sentinel or GA reported result.
        if recorder.slsqp_starts == 0 and prioritize_incumbent:
            x0 = first
        elif recorder.slsqp_starts == 0:
            x0 = np.clip(system.base["gen"][:, VG],lower,upper)
        elif recorder.slsqp_starts % 3 == 0 and recorder.best_feasible_vector is not None:
            x0 = np.clip(np.asarray(recorder.best_feasible_vector) +
                         rng.normal(0, 0.025, system.n), lower, upper)
        else:
            x0 = rng.uniform(lower, upper)
        before = recorder.evaluations
        recorder.slsqp_starts += 1
        try:
            opt = minimize(recorder.strict, x0, method="SLSQP",
                           bounds=system.bounds,
                           options=dict(maxiter=100, ftol=1e-11,
                                        disp=False))
            if not opt.success:
                recorder.slsqp_failed_starts += 1
                failures.append(str(opt.message))
        except PhysicalBudgetEnded:
            break
        except (ValueError, ArithmeticError, FloatingPointError) as exc:
            recorder.slsqp_failed_starts += 1
            failures.append(type(exc).__name__+": "+str(exc))
        if recorder.evaluations == before:
            # No solver progress; a genuine random point is still charged.
            recorder.strict(rng.uniform(lower,upper))
    return failures


def run_de(system, recorder, seed, population):
    factor = max(5,math.ceil(population/system.n))
    try:
        differential_evolution(
            recorder.strict, system.bounds, popsize=factor,
            maxiter=math.ceil(recorder.budget/(factor*system.n))+3,
            tol=0,atol=0,polish=False,
            rng=np.random.default_rng(seed))
    except PhysicalBudgetEnded:
        return


def fill_remaining(system, recorder, seed):
    """Equalize genuine evaluation budgets, without hiding abandoned budgets."""
    rng=np.random.default_rng(seed+131071)
    lower,upper=np.asarray(system.bounds).T
    recorder.stage_cap=recorder.budget
    while recorder.evaluations < recorder.budget:
        recorder(rng.uniform(lower,upper))
        recorder.filler_evaluations += 1


def run(system, method, seed, budget, population):
    random.seed(seed)
    np.random.seed(seed)
    monitor=PhysicalRecorder(system,budget)
    started=time.perf_counter()
    optimizer_success=True
    error=""
    try:
        if method in ("legacy_gadapt","affine_gadapt"):
            optimizer_success,error=run_ga(
                system,monitor,seed,population,
                "log_relative" if method=="legacy_gadapt" else "affine_invariant")
        elif method=="hybrid_gadapt_slsqp":
            monitor.stage_cap=budget//2
            optimizer_success,error=run_ga(
                system,monitor,seed,population,"log_relative")
            initial=monitor.start_point()
            monitor.stage_cap=budget
            run_slsqp(system,monitor,seed,initial)
        elif method=="slsqp_multistart":
            run_slsqp(system,monitor,seed,monitor.start_point(),
                      prioritize_incumbent=False)
        elif method=="scipy_de":
            run_de(system,monitor,seed,population)
        else:
            raise ValueError(method)
        fill_remaining(system,monitor,seed)
    except Exception as exc:
        optimizer_success=False
        error=type(exc).__name__+": "+str(exc)
    return dict(method=method,load_factor=system.load_factor,seed=seed,
                optimizer_success=optimizer_success,error=error,
                physical_feasible=(math.isfinite(monitor.best_feasible)
                                   and optimizer_success),
                feasible_loss_MW=(monitor.best_feasible if
                    math.isfinite(monitor.best_feasible) else ""),
                best_penalized=monitor.best_penalized,
                true_pf_evaluations=monitor.evaluations,
                all_objective_requests=monitor.requests,
                feasible_physical_evaluations=monitor.feasible_count,
                pf_convergence_failures=monitor.pf_failures,
                local_restarts=monitor.slsqp_starts,
                local_nonconverged_terminations=monitor.slsqp_failed_starts,
                random_budget_fill_evaluations=monitor.filler_evaluations,
                seconds=round(time.perf_counter()-started,4),
                best_feasible_vector=("-".join(
                    f"{v:.11g}" for v in monitor.best_feasible_vector) if
                    monitor.best_feasible_vector is not None else ""))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--seeds",type=int,default=12)
    parser.add_argument("--seed-start",type=int,default=100)
    parser.add_argument("--budget",type=int,default=360)
    parser.add_argument("--population",type=int,default=24)
    parser.add_argument("--loads",type=float,nargs="+",default=[1.0,1.1])
    parser.add_argument("--output",default="ieee14_local_refinement.csv")
    args=parser.parse_args()
    if args.seeds<1 or args.budget < 2*args.population:
        parser.error("positive seeds and budget >= twice population required")
    rows=[]
    for factor in args.loads:
        grid=IEEE14VoltageDispatch(factor)
        for seed in range(args.seed_start,args.seed_start+args.seeds):
            for method in METHODS:
                r=run(grid,method,seed,args.budget,args.population)
                rows.append(r)
                print("RUN",r,flush=True)
        for method in METHODS:
            sample=[r for r in rows if r["load_factor"]==factor and r["method"]==method]
            feasible=[r["feasible_loss_MW"] for r in sample if r["physical_feasible"]]
            print("SUMMARY",factor,method,
                  "feasible",len(feasible),"/",len(sample),
                  "median_loss_MW",statistics.median(feasible) if feasible else "NA",
                  "worst_loss_MW",max(feasible) if feasible else "NA",
                  "median_seconds",statistics.median(r["seconds"] for r in sample),
                  "physical_calls",(min(r["true_pf_evaluations"] for r in sample),
                                    max(r["true_pf_evaluations"] for r in sample)),flush=True)
    with open(args.output,"w",newline="",encoding="utf8") as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if any(r["true_pf_evaluations"]!=args.budget for r in rows):
        print("WARNING: missing genuine physical evaluations, includes failed runs",flush=True)
    if any(not r["optimizer_success"] for r in rows):
        print("WARNING: optimizer failures included in success denominator",flush=True)


if __name__=="__main__":
    main()
