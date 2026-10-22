"""I44: does mutation intensity explain GAdapt's deficit on binary route choice?

Previously frozen: research/ITERATION44_PROTOCOL.md (commit a39e599). Reuses the I43 model and
(1+1)-EA unchanged. GAdapt validator calls (all-min, all-max) are excluded from budget and best.
"""
import hashlib
import json
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
from research.iteration42_phase0_vig import DATA_DIR
from research.iteration43_budget_operator_diagnostic import (
    BUDGET, CHECKPOINTS, Budgeted, build, holm, run_ea)

INSTANCES = ("nobel-us", "abilene", "ta1", "nobel-eu", "india35", "janos-us")
METHODS = ("ga_i39", "ga_i39_m1", "one_plus_one_ea")
SEEDS = tuple(range(4400, 4412))
ALPHA = 0.05
VALIDATOR_CALLS = 2


class ValidatorFree(Budgeted):
    """Budgeted cost that checks and ignores GAdapt's two validator calls (all-min, all-max)."""

    def __init__(self, f, n):
        super().__init__(f)
        self.n, self.skipped = n, 0

    def __call__(self, values):
        if self.skipped < VALIDATOR_CALLS:
            z = np.rint(np.asarray(values, dtype=float)).astype(int)
            expected = 0 if self.skipped == 0 else 1
            if z.shape != (self.n,) or not np.all(z == expected):
                raise RuntimeError("Unexpected GAdapt validator call order")
            self.skipped += 1
            return float(self.f(z))
        return super().__call__(values)


def run_ga(cost, n, one_gene):
    kwargs = dict(cost_function=cost, exit_function=lambda: cost.done,
                  exit_check="generations", number_of_generations=10**6, timeout=3600,
                  population_size=24, cost_diversity_metric="log_relative",
                  population_mutation="cost_diversity,parent_diversity")
    if one_gene:
        # Amendment A1 (pre-run): the columnar-diversity rate determinator overrides the
        # user limit with max(round(N/5), ...); only the random branch honours it.
        kwargs.update(number_of_mutation_decision_variables=1, candidate_solution_mutation="random")
    algo = GA(**kwargs)
    for _ in range(n):
        algo.add(0., 1., 1.)
    return str(algo.execute().messages)[:200]


def one_run(task):
    name, method, seed = task
    random.seed(seed)
    np.random.seed(seed)
    f = build(name)
    start = time.monotonic()
    if method == "one_plus_one_ea":
        cost = Budgeted(f)
        stop = run_ea(cost, f.n)
        skipped = 0
    else:
        cost = ValidatorFree(f, f.n)
        stop = run_ga(cost, f.n, method == "ga_i39_m1")
        skipped = cost.skipped
    return dict(instance=name, method=method, seed=seed, calls=cost.calls,
                validator_calls_excluded=skipped, over_budget_requests=cost.over_budget,
                stop=stop, best_at={str(b): cost.at.get(b) for b in CHECKPOINTS},
                seconds=round(time.monotonic() - start, 3))


def analyse(runs, f0):
    def r(name, method, budget):
        rows = sorted((x for x in runs if x["instance"] == name and x["method"] == method),
                      key=lambda x: x["seed"])
        return np.array([(x["best_at"][str(budget)] - f0[name]) / f0[name] for x in rows])

    def family(a, b, budget):
        tests = []
        for name in INSTANCES:
            x, y = r(name, a, budget), r(name, b, budget)
            p = 1.0 if np.allclose(x, y) else float(wilcoxon(x, y).pvalue)
            tests.append(dict(instance=name, budget=budget, a=a, b=b, p=p,
                              median_r_a=float(np.median(x)), median_r_b=float(np.median(y))))
        for t, adj in zip(tests, holm([t["p"] for t in tests])):
            t["p_holm"] = adj
            t["a_significantly_better"] = adj < ALPHA and t["median_r_a"] < t["median_r_b"]
            t["a_significantly_worse"] = adj < ALPHA and t["median_r_a"] > t["median_r_b"]
        return tests

    primary = family("ga_i39_m1", "ga_i39", BUDGET)
    wins = sum(t["a_significantly_better"] for t in primary)
    verdict = "SUPPORTED" if wins >= 4 else "REFUTED" if wins <= 1 else "PARTIAL"
    return dict(
        primary=primary, primary_wins=wins, h_mut=verdict,
        secondary=dict(ga_i39_vs_ea=family("ga_i39", "one_plus_one_ea", BUDGET),
                       ga_i39_m1_vs_ea=family("ga_i39_m1", "one_plus_one_ea", BUDGET)),
        median_r={name: {m: {str(b): float(np.median(r(name, m, b))) for b in CHECKPOINTS}
                         for m in METHODS} for name in INSTANCES})


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
        runs = []
        for i, run in enumerate(pool.imap_unordered(one_run, tasks), 1):
            runs.append(run)
            if i % 12 == 0:
                print(f"{i}/{len(tasks)} runs, {time.monotonic() - start:.0f} s", flush=True)
    if any(x["calls"] != BUDGET for x in runs):
        raise RuntimeError("Evaluation accounting failed")
    if any(x["validator_calls_excluded"] != VALIDATOR_CALLS for x in runs if x["method"] != "one_plus_one_ea"):
        raise RuntimeError("Validator exclusion failed")
    here = os.path.abspath(__file__)
    deps = [os.path.join(os.path.dirname(here), f) for f in
            ("iteration43_budget_operator_diagnostic.py", "iteration42_phase0_vig.py")]
    result = dict(
        protocol="research/ITERATION44_PROTOCOL.md", protocol_commit="a39e599",
        source_sha256={os.path.basename(p): sha256(p) for p in [here] + deps},
        input_sha256={n: sha256(os.path.join(DATA_DIR, n + ".json")) for n in INSTANCES},
        environment=dict(python=sys.version.split()[0], platform=platform.platform(),
                         numpy=np.__version__, scipy=scipy.__version__, networkx=nx.__version__),
        synthetic_cost="identical to I43; NOT source SNDlib costs",
        f0=f0, sizes=sizes, runs=sorted(runs, key=lambda x: (x["instance"], x["method"], x["seed"])),
        analysis=analyse(runs, f0), total_seconds=round(time.monotonic() - start, 1))
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w") as handle:
        json.dump(result, handle, indent=1)
    return result


if __name__ == "__main__":
    out = main(sys.argv[1] if len(sys.argv) > 1 else "research/results/iteration44/mechanism.json")
    print(json.dumps(dict(h_mut=out["analysis"]["h_mut"], wins=out["analysis"]["primary_wins"],
                          seconds=out["total_seconds"]), indent=1))
