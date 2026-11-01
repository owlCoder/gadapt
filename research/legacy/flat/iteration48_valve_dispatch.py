"""I48: GAdapt vs IPOP-CMA-ES and DE on valve-point economic dispatch with certified optima.

Previously frozen: research/ITERATION48_PROTOCOL.md (commit d61d796). Library at cc2f357.
"""
import hashlib
import json
import math
import os
import platform
import random
import sys
import time
import warnings
from multiprocessing import Pool

import numpy as np
import scipy
from scipy.optimize import differential_evolution
from scipy.stats import wilcoxon

from gadapt.ga import GA
from research.iteration43_budget_operator_diagnostic import holm

warnings.filterwarnings("ignore")

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pedroso_valve_2013",
                    "valve_point_dispatch.json")
INSTANCES = (("eld13", 1800.0), ("eld13", 2520.0), ("eld40", 10500.0))
METHODS = ("gadapt_default", "gadapt_documented", "ipop_cma_es", "scipy_de")
BUDGET = 50_000
CHECKPOINTS = (5_000, 20_000, 50_000)
SEEDS = tuple(range(5000, 5025))
PENALTY = 1000.0
ALPHA = 0.05
SUCCESS_GAP = 1e-4
OVER_BUDGET = 1e30


class BudgetEnded(Exception):
    pass


class ValveDispatch:
    def __init__(self, system, load):
        data = json.load(open(DATA))
        d = data[system]
        self.a, self.b, self.c, self.e, self.f = (np.array(d[k]) for k in "abcef")
        self.p_min, self.p_max = np.array(d["p_min"]), np.array(d["p_max"])
        self.load = load
        self.optimum = data["certified_optimum"][f"{system}@{load:g}"]
        self.slack = int(np.argmax(self.p_max - self.p_min))  # first unit with the largest range
        self.free = [i for i in range(len(self.a)) if i != self.slack]
        self.bounds = [(float(self.p_min[i]), float(self.p_max[i])) for i in self.free]

    def unit_costs(self, p):
        return (self.a + self.b * p + self.c * p * p
                + np.abs(self.e * np.sin(self.f * (self.p_min - p))))

    def full_vector(self, x):
        p = np.empty(len(self.a))
        p[self.free] = x
        p[self.slack] = self.load - float(np.sum(x))
        return p

    def evaluate(self, x):
        p = self.full_vector(np.asarray(x, dtype=float))
        s = p[self.slack]
        clipped = min(max(s, self.p_min[self.slack]), self.p_max[self.slack])
        violation = abs(s - clipped)
        p[self.slack] = clipped
        return float(np.sum(self.unit_costs(p)) + PENALTY * violation), violation <= 1e-6


class Counted:
    def __init__(self, problem, raise_at_budget=False):
        self.problem, self.raise_at_budget = problem, raise_at_budget
        self.calls, self.over_budget, self.best = 0, 0, math.inf
        self.best_feasible, self.at = math.inf, {}

    @property
    def done(self):
        return self.calls >= BUDGET

    def __call__(self, x):
        if self.done:
            self.over_budget += 1
            if self.raise_at_budget:
                raise BudgetEnded()
            return OVER_BUDGET
        self.calls += 1
        value, feasible = self.problem.evaluate(x)
        self.best = min(self.best, value)
        if feasible:
            self.best_feasible = min(self.best_feasible, value)
        if self.calls in CHECKPOINTS:
            self.at[self.calls] = self.best
        return value


def run_gadapt(counted, problem, seed, documented):
    random.seed(seed)
    np.random.seed(seed)
    extra = (dict(normal_distribution_mutation_min_std_dev=1e-4,
                  normal_distribution_mutation_min_std_dev_decay_generations=2.5) if documented else {})
    ga = GA(cost_function=counted, probe_cost_function=False, exit_check="generations",
            number_of_generations=10**7, exit_function=lambda: counted.done, timeout=7200, **extra)
    for lo, hi in problem.bounds:
        ga.add(lo, hi)
    ga.execute()


def run_ipop(counted, problem, seed):
    import cma
    lower, upper = np.array(problem.bounds).T
    rng = np.random.default_rng(seed)
    popsize, restart = None, 0
    while not counted.done:
        options = dict(bounds=[0, 1], seed=seed * 100 + restart + 1, verbose=-9, maxfevals=10**9)
        if popsize:
            options["popsize"] = popsize
        es = cma.CMAEvolutionStrategy(rng.uniform(0, 1, len(lower)), 0.3, options)
        while not counted.done and not es.stop():
            xs = es.ask()
            es.tell(xs, [counted(lower + np.asarray(x) * (upper - lower)) for x in xs])
        popsize = 2 * es.popsize
        restart += 1
    return restart


def run_de(counted, problem, seed):
    try:
        differential_evolution(counted, problem.bounds, maxiter=10**7, tol=0, atol=0, polish=False,
                               rng=np.random.default_rng(seed))
    except BudgetEnded:
        pass


def one_run(task):
    system, load, method, seed = task
    problem = ValveDispatch(system, load)
    counted = Counted(problem, raise_at_budget=(method == "scipy_de"))
    start, restarts = time.monotonic(), None
    if method == "gadapt_default":
        run_gadapt(counted, problem, seed, False)
    elif method == "gadapt_documented":
        run_gadapt(counted, problem, seed, True)
    elif method == "ipop_cma_es":
        restarts = run_ipop(counted, problem, seed)
    else:
        run_de(counted, problem, seed)
    return dict(instance=f"{system}@{load:g}", method=method, seed=seed, calls=counted.calls,
                over_budget_requests=counted.over_budget, restarts=restarts,
                best_at={str(b): counted.at.get(b) for b in CHECKPOINTS},
                best_feasible=(counted.best_feasible if math.isfinite(counted.best_feasible) else None),
                seconds=round(time.monotonic() - start, 2))


def analyse(runs):
    optimum = {f"{s}@{l:g}": ValveDispatch(s, l).optimum for s, l in INSTANCES}
    names = list(optimum)

    def gap(name, method, budget=BUDGET):
        rows = sorted((x for x in runs if x["instance"] == name and x["method"] == method), key=lambda x: x["seed"])
        return np.array([(x["best_at"][str(budget)] - optimum[name]) / optimum[name] for x in rows])

    def family(a, b):
        tests = []
        for name in names:
            x, y = gap(name, a), gap(name, b)
            p = 1.0 if np.allclose(x, y) else float(wilcoxon(x, y).pvalue)
            tests.append(dict(instance=name, a=a, b=b, p=p, median_gap_a=float(np.median(x)),
                              median_gap_b=float(np.median(y))))
        for t, adj in zip(tests, holm([t["p"] for t in tests])):
            t["p_holm"] = adj
            t["a_better"] = adj < ALPHA and t["median_gap_a"] < t["median_gap_b"]
            t["a_worse"] = adj < ALPHA and t["median_gap_a"] > t["median_gap_b"]
        return tests

    primary = family("gadapt_default", "ipop_cma_es")
    better, worse = sum(t["a_better"] for t in primary), sum(t["a_worse"] for t in primary)
    verdict = "GADAPT_ADVANTAGE" if better >= 2 else "GADAPT_DEFICIT" if worse >= 2 else "INCONCLUSIVE"
    describe = {name: {m: {str(b): dict(median_gap=float(np.median(gap(name, m, b))),
                                        worst_gap=float(np.max(gap(name, m, b))),
                                        success_rate=float(np.mean(gap(name, m, b) <= SUCCESS_GAP)))
                           for b in CHECKPOINTS} for m in METHODS} for name in names}
    return dict(primary=primary, verdict=verdict,
                secondary=dict(documented_vs_ipop=family("gadapt_documented", "ipop_cma_es"),
                               default_vs_de=family("gadapt_default", "scipy_de")),
                describe=describe, certified_optimum=optimum)


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main(output="research/results/iteration48/valve_dispatch.json"):
    import cma
    start = time.monotonic()
    tasks = [(s, l, m, seed) for s, l in reversed(INSTANCES) for m in METHODS for seed in SEEDS]
    runs = []
    with Pool() as pool:
        for i, run in enumerate(pool.imap_unordered(one_run, tasks), 1):
            runs.append(run)
            if i % 25 == 0:
                print(f"{i}/{len(tasks)} runs, {time.monotonic() - start:.0f} s", flush=True)
    if any(x["calls"] != BUDGET for x in runs):
        raise RuntimeError("Evaluation accounting failed")
    here = os.path.abspath(__file__)
    result = dict(protocol="research/ITERATION48_PROTOCOL.md", protocol_commit="d61d796", library_commit="cc2f357",
                  source_sha256={os.path.basename(here): sha256(here)}, data_sha256=sha256(DATA),
                  environment=dict(python=sys.version.split()[0], platform=platform.platform(),
                                   numpy=np.__version__, scipy=scipy.__version__, cma=cma.__version__),
                  runs=sorted(runs, key=lambda x: (x["instance"], x["method"], x["seed"])),
                  analysis=analyse(runs), total_seconds=round(time.monotonic() - start, 1))
    os.makedirs(os.path.dirname(output), exist_ok=True)
    json.dump(result, open(output, "w"), indent=1)
    print(json.dumps(dict(verdict=result["analysis"]["verdict"], seconds=result["total_seconds"]), indent=1))


if __name__ == "__main__":
    main()
