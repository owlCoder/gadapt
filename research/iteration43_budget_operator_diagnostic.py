"""I43: budget-vs-operator diagnostic for GAdapt on binary route choice.

Previously frozen: research/ITERATION43_PROTOCOL.md (commit 9821ff1). Synthetic modular cost
over archived topohub topologies and static demands; NOT source SNDlib costs.
"""
import hashlib
import json
import math
import os
import platform
import random
import sys
import time
from multiprocessing import Pool

import networkx as nx
import numpy as np
import scipy
from scipy.stats import wilcoxon

from gadapt.ga import GA
from research.iteration42_phase0_vig import DATA_DIR, load_instance, two_paths

INSTANCES = ("polska", "nobel-germany", "atlanta", "france", "geant", "germany50")
METHODS = ("ga_i39", "ga_default", "one_plus_one_ea", "random_search")
SEEDS = tuple(range(4300, 4312))
BUDGET = 10_000
CHECKPOINTS = (360, 2000, 10_000)
PRICE_RATIO = 1.6
OVER_BUDGET = 1e15
ALPHA = 0.05


class RouteChoiceCost:
    """f(z) = sum_e dist_e * (n1 + 1.6 n2) with modules U, 2U covering the single-period load."""

    def __init__(self, graph, demands):
        edges = sorted(tuple(sorted(e)) for e in graph.edges)
        edge_ids = {frozenset(e): i for i, e in enumerate(edges)}
        self.dist = np.array([graph.edges[e]["dist"] for e in edges], dtype=float)
        values = np.array([q for _, _, q in demands], dtype=float)
        self.unit = 4.0 * float(values.mean())
        base = np.zeros(len(edges))
        rows = []
        for (a, b, q) in demands:
            paths = two_paths(graph, a, b)
            if paths is None:
                path = nx.shortest_path(graph, a, b)  # fixed demand: its single path
                for h in zip(path, path[1:]):
                    base[edge_ids[frozenset(h)]] += q
                continue
            incidence = np.zeros((2, len(edges)))
            for which, path in enumerate(paths):
                for h in zip(path, path[1:]):
                    incidence[which, edge_ids[frozenset(h)]] = 1.0
            base += q * incidence[0]
            rows.append(q * (incidence[1] - incidence[0]))
        self.base = base
        self.delta = np.array(rows).reshape(len(rows), len(edges))
        self.n = len(rows)

    def __call__(self, z):
        load = self.base + np.asarray(z, dtype=float) @ self.delta
        quanta = np.maximum(0, np.ceil(load / self.unit - 1e-10)).astype(int)
        return float(np.sum(self.dist * ((quanta % 2) + PRICE_RATIO * (quanta // 2))))


class Budgeted:
    def __init__(self, f, budget=BUDGET, checkpoints=CHECKPOINTS):
        self.f, self.budget, self.checkpoints = f, budget, checkpoints
        self.calls, self.over_budget, self.best = 0, 0, math.inf
        self.at = {}

    def __call__(self, values):
        if self.calls >= self.budget:
            self.over_budget += 1
            return OVER_BUDGET
        self.calls += 1
        z = np.rint(np.asarray(values, dtype=float)).astype(int)
        value = self.f(z)
        self.best = min(self.best, value)
        if self.calls in self.checkpoints:
            self.at[self.calls] = self.best
        return value

    @property
    def done(self):
        return self.calls >= self.budget


def build(name):
    graph, pairs = load_instance(os.path.join(DATA_DIR, name + ".json"))
    with open(os.path.join(DATA_DIR, name + ".json")) as handle:
        raw = json.load(handle)["graph"]["demands"]
    demands = [(a, b, float(raw[str(a)][str(b)])) for a, b in pairs]
    return RouteChoiceCost(graph, demands)


def run_ga(cost, n, i39):
    # Amendment A1 (pre-run): both arms exit only by budget, otherwise defaults.
    kwargs = dict(cost_function=cost, exit_function=lambda: cost.done,
                  exit_check="generations", number_of_generations=10**6, timeout=3600)
    if i39:
        kwargs.update(population_size=24, cost_diversity_metric="log_relative",
                      population_mutation="cost_diversity,parent_diversity")
    algo = GA(**kwargs)
    for _ in range(n):
        algo.add(0., 1., 1.)
    result = algo.execute()
    return str(result.messages)[:200]


def run_ea(cost, n):
    x = np.random.randint(0, 2, n)
    fx = cost(x)
    while not cost.done:
        flips = np.random.random(n) < 1.0 / n
        while not flips.any():
            flips = np.random.random(n) < 1.0 / n
        y = np.where(flips, 1 - x, x)
        fy = cost(y)
        if fy <= fx:
            x, fx = y, fy
    return "budget"


def run_random(cost, n):
    while not cost.done:
        cost(np.random.randint(0, 2, n))
    return "budget"


def one_run(task):
    name, method, seed = task
    random.seed(seed)
    np.random.seed(seed)
    f = build(name)
    cost = Budgeted(f)
    start = time.monotonic()
    if method == "ga_i39":
        stop = run_ga(cost, f.n, True)
    elif method == "ga_default":
        stop = run_ga(cost, f.n, False)
    elif method == "one_plus_one_ea":
        stop = run_ea(cost, f.n)
    else:
        stop = run_random(cost, f.n)
    return dict(instance=name, method=method, seed=seed, calls=cost.calls,
                over_budget_requests=cost.over_budget, stop=stop,
                best_at={str(b): cost.at.get(b) for b in CHECKPOINTS},
                seconds=round(time.monotonic() - start, 3))


def holm(pvalues):
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [None] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def analyse(runs, f0):
    def r(name, method, budget):
        return np.array([(x["best_at"][str(budget)] - f0[name]) / f0[name] for x in sorted(
            (x for x in runs if x["instance"] == name and x["method"] == method),
            key=lambda x: x["seed"])])

    tests = []
    for name in INSTANCES:
        for budget in (360, BUDGET):
            ga, ea = r(name, "ga_i39", budget), r(name, "one_plus_one_ea", budget)
            p = 1.0 if np.allclose(ga, ea) else float(wilcoxon(ga, ea).pvalue)
            tests.append(dict(instance=name, budget=budget, p=p,
                              median_r_ga_i39=float(np.median(ga)),
                              median_r_ea=float(np.median(ea))))
    for t, adj in zip(tests, holm([t["p"] for t in tests])):
        t["p_holm"] = adj
    summary = {}
    for name in INSTANCES:
        t = next(x for x in tests if x["instance"] == name and x["budget"] == BUDGET)
        ga_end, ga_360 = r(name, "ga_i39", BUDGET), r(name, "ga_i39", 360)
        significant = t["p_holm"] < ALPHA
        if significant and t["median_r_ea"] < t["median_r_ga_i39"]:
            label = "OPERATOR_DEFICIT"
        elif (not (significant and t["median_r_ea"] < t["median_r_ga_i39"])
              and np.sum(ga_end < 0) >= 10 and np.sum(ga_360 < 0) <= 2):
            label = "BUDGET_ARTIFACT"
        else:
            label = "MIXED"
        if significant and t["median_r_ga_i39"] < t["median_r_ea"]:
            label += "+GA_SIGNIFICANTLY_BETTER"
        summary[name] = dict(
            label=label,
            seeds_improving={m: {str(b): int(np.sum(r(name, m, b) < 0)) for b in CHECKPOINTS}
                             for m in METHODS},
            median_r={m: {str(b): float(np.median(r(name, m, b))) for b in CHECKPOINTS}
                      for m in METHODS})
    labels = [s["label"].split("+")[0] for s in summary.values()]
    overall = next((c for c in ("OPERATOR_DEFICIT", "BUDGET_ARTIFACT", "MIXED")
                    if labels.count(c) >= 4), "UNRESOLVED")
    return dict(tests=tests, per_instance=summary, overall=overall)


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main(output, processes=None):
    start = time.monotonic()
    f0, sizes = {}, {}
    for name in INSTANCES:
        f = build(name)
        f0[name], sizes[name] = f(np.zeros(f.n, dtype=int)), dict(genes=f.n, unit=f.unit)
    tasks = [(n, m, s) for n in INSTANCES for m in METHODS for s in SEEDS]
    with Pool(processes) as pool:
        runs = pool.map(one_run, tasks, chunksize=1)
    if any(x["calls"] != BUDGET for x in runs):
        raise RuntimeError("Evaluation accounting failed")
    here = os.path.abspath(__file__)
    phase0 = os.path.join(os.path.dirname(here), "iteration42_phase0_vig.py")
    result = dict(
        protocol="research/ITERATION43_PROTOCOL.md", protocol_commit="9821ff1",
        source_sha256={os.path.basename(p): sha256(p) for p in (here, phase0)},
        input_sha256={n: sha256(os.path.join(DATA_DIR, n + ".json")) for n in INSTANCES},
        environment=dict(python=sys.version.split()[0], platform=platform.platform(),
                         numpy=np.__version__, scipy=scipy.__version__, networkx=nx.__version__),
        synthetic_cost="modules U=4*mean demand and 2U at dist_e and 1.6*dist_e; NOT source SNDlib costs",
        f0=f0, sizes=sizes, runs=runs, analysis=analyse(runs, f0),
        total_seconds=round(time.monotonic() - start, 1))
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w") as handle:
        json.dump(result, handle, indent=1)
    return result


if __name__ == "__main__":
    out = main(sys.argv[1] if len(sys.argv) > 1 else "research/results/iteration43/diagnostic.json")
    print(json.dumps(dict(overall=out["analysis"]["overall"],
                          labels={k: v["label"] for k, v in out["analysis"]["per_instance"].items()},
                          seconds=out["total_seconds"]), indent=1))
