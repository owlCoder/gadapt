"""I47: GAdapt invariance to units / optimum position; AC economic dispatch on MATPOWER cases.

Previously frozen: research/ITERATION47_PROTOCOL.md (commit 6588731). Library at cc2f357
(opt-in columnar_diversity_metric="linear"); defaults untouched.
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

ALPHA = 0.05
SYNTH_BUDGET = 3000
SYNTH_SEEDS = tuple(range(4800, 4812))
DISPATCH_BUDGET = 3000
DISPATCH_SEEDS = tuple(range(4900, 4912))
CASES = ("case14", "case30", "case39", "case57", "case118")
METRICS = ("log_relative", "linear")
OVER_BUDGET = 1e30


class BudgetEnded(Exception):
    """Raised for optimizers that cannot be stopped by an exit function (DE)."""


def gadapt_minimize(cost, bounds, metric, seed, done):
    random.seed(seed)
    np.random.seed(seed)
    ga = GA(cost_function=cost, probe_cost_function=False, exit_check="generations",
            number_of_generations=10**6, exit_function=done, timeout=3600,
            columnar_diversity_metric=metric)
    for lo, hi in bounds:
        ga.add(float(lo), float(hi))
    return str(ga.execute().messages)[:200]


# ---------------------------------------------------------------- A. synthetic

def synthetic_value(function, z):
    d = len(z)
    if function == "sphere":
        return float(np.dot(z, z))
    weights = 10.0 ** (3.0 * np.arange(d) / (d - 1))
    return float(np.dot(weights, z * z))


def synthetic_run(task):
    function, d, r, p, metric, seed = task
    state = dict(calls=0, best=math.inf)
    centre = p * r

    def cost(values):
        if state["calls"] >= SYNTH_BUDGET:
            return OVER_BUDGET
        state["calls"] += 1
        v = synthetic_value(function, (np.asarray(values, dtype=float) - centre) / r)
        state["best"] = min(state["best"], v)
        return v

    gadapt_minimize(cost, [(0.0, r)] * d, metric, seed, lambda: state["calls"] >= SYNTH_BUDGET)
    return dict(function=function, d=d, r=r, p=p, metric=metric, seed=seed,
                calls=state["calls"], best=state["best"])


def synthetic_tasks():
    return [(f, d, r, p, m, s) for f in ("sphere", "ellipsoid") for d in (5, 20)
            for r in (1.0, 1000.0) for p in (0.5, 0.999) for m in METRICS for s in SYNTH_SEEDS]


def _paired(x, y):
    p = 1.0 if np.allclose(x, y) else float(wilcoxon(x, y).pvalue)
    return p, float(np.median(x)), float(np.median(y))


def analyse_synthetic(runs):
    def best(f, d, r, p, m):
        rows = sorted((x for x in runs if (x["function"], x["d"], x["r"], x["p"], x["metric"]) == (f, d, r, p, m)),
                      key=lambda x: x["seed"])
        return np.array([x["best"] for x in rows])

    cells = [(f, d) for f in ("sphere", "ellipsoid") for d in (5, 20)]
    a1 = []
    for f, d in cells:
        p, lin, log = _paired(best(f, d, 1000.0, 0.999, "linear"), best(f, d, 1000.0, 0.999, "log_relative"))
        a1.append(dict(function=f, d=d, p=p, median_linear=lin, median_log=log))
    for t, adj in zip(a1, holm([t["p"] for t in a1])):
        t["p_holm"] = adj
        t["linear_better"] = adj < ALPHA and t["median_linear"] < t["median_log"]
        t["linear_worse"] = adj < ALPHA and t["median_linear"] > t["median_log"]
    wins = sum(t["linear_better"] for t in a1)
    a1_verdict = "SUPPORTED" if wins >= 3 and not any(t["linear_worse"] for t in a1) else "NOT_SUPPORTED"
    a2 = []
    for m in METRICS:
        for f, d in cells:
            p, small, large = _paired(best(f, d, 1.0, 0.999, m), best(f, d, 1000.0, 0.999, m))
            a2.append(dict(metric=m, function=f, d=d, p=p, median_r1=small, median_r1000=large))
    for t, adj in zip(a2, holm([t["p"] for t in a2])):
        t["p_holm"] = adj
        t["unit_dependent"] = adj < ALPHA
    table = {f"{f}/D{d}/R{r:g}/p{p}": {m: float(np.median(best(f, d, r, p, m))) for m in METRICS}
             for f, d in cells for r in (1.0, 1000.0) for p in (0.5, 0.999)}
    return dict(a1=a1, a1_wins=wins, a1_verdict=a1_verdict, a2=a2, median_best=table)


# ---------------------------------------------------------------- B. dispatch

class Dispatch:
    """AC economic dispatch: PG of non-slack online generators, fixed VG, original loads."""

    def __init__(self, case_name):
        from pypower import api
        from pypower.idx_bus import BUS_TYPE
        from pypower.idx_gen import GEN_BUS, GEN_STATUS, PMAX, PMIN
        self.case_name = case_name
        self.base = getattr(api, case_name)()
        self.base_mva = float(self.base["baseMVA"])
        gen = self.base["gen"]
        ref_buses = set(np.flatnonzero(self.base["bus"][:, BUS_TYPE] == 3) + 1)
        online = gen[:, GEN_STATUS] > 0
        self.slack = [i for i in range(len(gen)) if online[i] and int(gen[i, GEN_BUS]) in ref_buses]
        self.variables = [i for i in range(len(gen)) if online[i] and i not in self.slack
                          and gen[i, PMAX] > gen[i, PMIN]]
        self.bounds_mw = [(float(gen[i, PMIN]), float(gen[i, PMAX])) for i in self.variables]
        self.online = np.flatnonzero(online)
        self.options = api.ppoption(VERBOSE=0, OUT_ALL=0, ENFORCE_Q_LIMS=0, PF_TOL=1e-8, PF_MAX_IT=40)

    def evaluate(self, pg_mw):
        from pypower.api import runpf
        from pypower.idx_brch import PF, PT, QF, QT, RATE_A
        from pypower.idx_bus import VM, VMAX, VMIN
        from pypower.idx_gen import PG, PMAX, PMIN, QG, QMAX, QMIN
        case = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in self.base.items()}
        case["gen"][self.variables, PG] = np.asarray(pg_mw, dtype=float)
        try:
            solved, converged = runpf(case, self.options)
        except (ValueError, ArithmeticError, RuntimeError, IndexError, np.linalg.LinAlgError):
            converged = False
        if not converged:
            return dict(score=1e12, feasible=False, cost=None, converged=False)
        bus, gen, branch = solved["bus"], solved["gen"], solved["branch"]
        if not all(np.isfinite(a).all() for a in (bus, gen, branch)):
            return dict(score=1e12, feasible=False, cost=None, converged=False)
        g = gen[self.online]
        coefficients = self.base["gencost"][self.online, 4:7]
        cost = float(np.sum(coefficients[:, 0] * g[:, PG] ** 2 + coefficients[:, 1] * g[:, PG]
                            + coefficients[:, 2]))
        v = float(np.sum(np.maximum(bus[:, VM] - bus[:, VMAX], 0) + np.maximum(bus[:, VMIN] - bus[:, VM], 0)))
        s = gen[self.slack]
        p = float(np.sum(np.maximum(s[:, PG] - s[:, PMAX], 0) + np.maximum(s[:, PMIN] - s[:, PG], 0)))
        q = float(np.sum(np.maximum(g[:, QG] - g[:, QMAX], 0) + np.maximum(g[:, QMIN] - g[:, QG], 0)))
        rating = branch[:, RATE_A]
        flow = np.maximum(np.hypot(branch[:, PF], branch[:, QF]), np.hypot(branch[:, PT], branch[:, QT]))
        mva = float(np.sum(np.where(rating > 0, np.maximum(flow - rating, 0), 0)))
        score = cost + 1e5 * (v + p / 100 + q / 100 + mva / 100)
        feasible = v <= 1e-5 and p <= 1e-3 and q <= 1e-3 and mva <= 1e-3
        return dict(score=float(score), feasible=bool(feasible), cost=cost, converged=True)


class Counted:
    def __init__(self, dispatch, budget, raise_at_budget=False):
        self.dispatch, self.budget, self.raise_at_budget = dispatch, budget, raise_at_budget
        self.calls, self.over_budget, self.failures = 0, 0, 0
        self.best_score, self.best_feasible_cost = math.inf, math.inf

    @property
    def done(self):
        return self.calls >= self.budget

    def mw(self, pg_mw):
        if self.done:
            self.over_budget += 1
            if self.raise_at_budget:
                raise BudgetEnded()
            return OVER_BUDGET
        self.calls += 1
        info = self.dispatch.evaluate(pg_mw)
        self.failures += not info["converged"]
        self.best_score = min(self.best_score, info["score"])
        if info["feasible"]:
            self.best_feasible_cost = min(self.best_feasible_cost, info["cost"])
        return info["score"]


def dispatch_run(task):
    case_name, method, seed = task
    dispatch = Dispatch(case_name)
    lower, upper = np.array(dispatch.bounds_mw).T
    start = time.monotonic()
    if method.startswith("gadapt"):
        _, metric, unit = method.split(":")
        counted = Counted(dispatch, DISPATCH_BUDGET)
        if unit == "mw":
            gadapt_minimize(counted.mw, dispatch.bounds_mw, metric, seed, lambda: counted.done)
        else:
            scale = dispatch.base_mva
            gadapt_minimize(lambda x: counted.mw(np.asarray(x, dtype=float) * scale),
                            [(lo / scale, hi / scale) for lo, hi in dispatch.bounds_mw],
                            metric, seed, lambda: counted.done)
    elif method == "cma_es":
        import cma
        counted = Counted(dispatch, DISPATCH_BUDGET)
        es = cma.CMAEvolutionStrategy(np.full(len(lower), 0.5), 0.3,
                                      dict(bounds=[0, 1], seed=seed, verbose=-9, maxfevals=10**9))
        while not counted.done:
            xs = es.ask()
            values = [counted.mw(lower + np.asarray(x) * (upper - lower)) for x in xs]
            es.tell(xs, values)
    else:
        counted = Counted(dispatch, DISPATCH_BUDGET, raise_at_budget=True)
        try:
            differential_evolution(counted.mw, dispatch.bounds_mw, maxiter=10**6, tol=0, atol=0,
                                   polish=False, rng=np.random.default_rng(seed))
        except BudgetEnded:
            pass
    return dict(case=case_name, method=method, seed=seed, calls=counted.calls,
                over_budget_requests=counted.over_budget, pf_failures=counted.failures,
                best_score=counted.best_score,
                best_feasible_cost=(counted.best_feasible_cost if math.isfinite(counted.best_feasible_cost) else None),
                variables=len(dispatch.variables), seconds=round(time.monotonic() - start, 2))


DISPATCH_METHODS = ("gadapt:log_relative:mw", "gadapt:linear:mw", "gadapt:log_relative:pu",
                    "gadapt:linear:pu", "cma_es", "scipy_de")


def analyse_dispatch(runs):
    def scores(c, m):
        rows = sorted((x for x in runs if x["case"] == c and x["method"] == m), key=lambda x: x["seed"])
        return np.array([x["best_score"] for x in rows])

    def family(pairs):
        tests = []
        for a, b in pairs:
            for c in CASES:
                p, ma, mb = _paired(scores(c, a), scores(c, b))
                tests.append(dict(case=c, a=a, b=b, p=p, median_a=ma, median_b=mb))
        for t, adj in zip(tests, holm([t["p"] for t in tests])):
            t["p_holm"] = adj
            t["a_better"] = adj < ALPHA and t["median_a"] < t["median_b"]
            t["a_worse"] = adj < ALPHA and t["median_a"] > t["median_b"]
        return tests

    b1 = family([("gadapt:linear:mw", "gadapt:log_relative:mw")])
    wins, losses = sum(t["a_better"] for t in b1), sum(t["a_worse"] for t in b1)
    verdict = "SUPPORTED" if wins >= 3 and losses == 0 else "REFUTED" if wins <= 1 else "PARTIAL"
    b2 = family([("gadapt:log_relative:mw", "gadapt:log_relative:pu"), ("gadapt:linear:mw", "gadapt:linear:pu")])
    best_known = {c: float(min(x["best_score"] for x in runs if x["case"] == c)) for c in CASES}
    describe = {c: {m: dict(median_score=float(np.median(scores(c, m))),
                            median_rel_gap=float(np.median((scores(c, m) - best_known[c]) / abs(best_known[c]))),
                            seeds_feasible=int(sum(x["best_feasible_cost"] is not None for x in runs
                                                   if x["case"] == c and x["method"] == m)))
                    for m in DISPATCH_METHODS} for c in CASES}
    return dict(b1=b1, b1_wins=wins, b1_losses=losses, b1_verdict=verdict, b2=b2,
                best_known_score=best_known, describe=describe)


# ---------------------------------------------------------------- driver

def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def run_pool(function, tasks, label):
    start, runs = time.monotonic(), []
    with Pool() as pool:
        for i, run in enumerate(pool.imap_unordered(function, tasks), 1):
            runs.append(run)
            if i % 24 == 0:
                print(f"{label}: {i}/{len(tasks)} runs, {time.monotonic() - start:.0f} s", flush=True)
    return runs, round(time.monotonic() - start, 1)


def provenance():
    import cma
    import pypower
    here = os.path.abspath(__file__)
    return dict(protocol="research/ITERATION47_PROTOCOL.md", protocol_commit="6588731", library_commit="cc2f357",
                source_sha256={os.path.basename(here): sha256(here)},
                environment=dict(python=sys.version.split()[0], platform=platform.platform(),
                                 numpy=np.__version__, scipy=scipy.__version__, cma=cma.__version__,
                                 pypower=getattr(pypower, "__version__", "5.1.19")))


def main(part):
    os.makedirs("research/results/iteration47", exist_ok=True)
    if part in ("synthetic", "all"):
        runs, seconds = run_pool(synthetic_run, synthetic_tasks(), "synthetic")
        if any(x["calls"] != SYNTH_BUDGET for x in runs):
            raise RuntimeError("Synthetic evaluation accounting failed")
        out = dict(provenance(), runs=sorted(runs, key=lambda x: tuple(map(str, x.values()))),
                   analysis=analyse_synthetic(runs), total_seconds=seconds)
        json.dump(out, open("research/results/iteration47/synthetic.json", "w"), indent=1)
        print(json.dumps(dict(a1=out["analysis"]["a1_verdict"], wins=out["analysis"]["a1_wins"]), indent=1))
    if part in ("dispatch", "all"):
        tasks = [(c, m, s) for c in reversed(CASES) for m in DISPATCH_METHODS for s in DISPATCH_SEEDS]
        runs, seconds = run_pool(dispatch_run, tasks, "dispatch")
        if any(x["calls"] != DISPATCH_BUDGET for x in runs):
            raise RuntimeError("Dispatch evaluation accounting failed")
        out = dict(provenance(), runs=sorted(runs, key=lambda x: (x["case"], x["method"], x["seed"])),
                   analysis=analyse_dispatch(runs), total_seconds=seconds)
        json.dump(out, open("research/results/iteration47/dispatch.json", "w"), indent=1)
        print(json.dumps(dict(b1=out["analysis"]["b1_verdict"], wins=out["analysis"]["b1_wins"],
                              losses=out["analysis"]["b1_losses"]), indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
