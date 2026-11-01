"""I45: is GAdapt's deficit on binary route choice GAdapt-specific or generic for population GAs?

Previously frozen: research/ITERATION45_PROTOCOL.md (commit 7061d7f). Reuses the I43 model,
(1+1)-EA and the I44 validator-free GAdapt arm unchanged.
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

from research.iteration42_phase0_vig import DATA_DIR
from research.iteration43_budget_operator_diagnostic import (
    BUDGET, CHECKPOINTS, Budgeted, build, holm, run_ea)
from research.iteration44_mutation_mechanism import VALIDATOR_CALLS, ValidatorFree, run_ga

INSTANCES = ("dfn-gwin", "newyork", "norway", "pioro40", "zib54", "cost266")
METHODS = ("gadapt_i39", "textbook_ga", "one_plus_one_ea")
SEEDS = tuple(range(4500, 4512))
ALPHA = 0.05
POPULATION = 24
CROSSOVER_PROBABILITY = 0.9


def run_textbook_ga(cost, n, on_generation=None):
    """Generational GA: elitism 1, binary tournament, uniform crossover (0.9), bit-flip 1/n."""
    population = np.random.randint(0, 2, (POPULATION, n))
    fitness = np.array([cost(x) for x in population])
    while not cost.done:
        def tournament():
            a, b = np.random.randint(0, POPULATION, 2)
            return population[a] if fitness[a] <= fitness[b] else population[b]

        elite = int(np.argmin(fitness))
        children, child_fitness = [population[elite]], [fitness[elite]]
        while len(children) < POPULATION and not cost.done:
            first, second = tournament(), tournament()
            if np.random.random() < CROSSOVER_PROBABILITY:
                child = np.where(np.random.random(n) < 0.5, first, second)
            else:
                child = first.copy()
            child = np.where(np.random.random(n) < 1.0 / n, 1 - child, child)
            children.append(child)
            child_fitness.append(cost(child))
        population, fitness = np.array(children), np.array(child_fitness)
        if on_generation is not None:
            on_generation(float(fitness.min()))
    return "budget"


def one_run(task):
    name, method, seed = task
    random.seed(seed)
    np.random.seed(seed)
    f = build(name)
    start = time.monotonic()
    skipped = 0
    if method == "gadapt_i39":
        cost = ValidatorFree(f, f.n)
        stop = run_ga(cost, f.n, False)
        skipped = cost.skipped
    elif method == "textbook_ga":
        cost = Budgeted(f)
        stop = run_textbook_ga(cost, f.n)
    else:
        cost = Budgeted(f)
        stop = run_ea(cost, f.n)
    return dict(instance=name, method=method, seed=seed, calls=cost.calls,
                validator_calls_excluded=skipped, over_budget_requests=cost.over_budget,
                stop=stop, best_at={str(b): cost.at.get(b) for b in CHECKPOINTS},
                seconds=round(time.monotonic() - start, 3))


def analyse(runs, f0):
    def r(name, method, budget):
        rows = sorted((x for x in runs if x["instance"] == name and x["method"] == method),
                      key=lambda x: x["seed"])
        return np.array([(x["best_at"][str(budget)] - f0[name]) / f0[name] for x in rows])

    def family(a, b):
        tests = []
        for name in INSTANCES:
            x, y = r(name, a, BUDGET), r(name, b, BUDGET)
            p = 1.0 if np.allclose(x, y) else float(wilcoxon(x, y).pvalue)
            tests.append(dict(instance=name, a=a, b=b, p=p,
                              median_r_a=float(np.median(x)), median_r_b=float(np.median(y))))
        for t, adj in zip(tests, holm([t["p"] for t in tests])):
            t["p_holm"] = adj
            t["a_significantly_better"] = adj < ALPHA and t["median_r_a"] < t["median_r_b"]
            t["a_significantly_worse"] = adj < ALPHA and t["median_r_a"] > t["median_r_b"]
        return tests

    f1 = family("textbook_ga", "gadapt_i39")
    f2 = family("one_plus_one_ea", "textbook_ga")
    textbook_wins = sum(t["a_significantly_better"] for t in f1)
    ea_wins = sum(t["a_significantly_better"] for t in f2)
    if textbook_wins >= 4:
        verdict = "GADAPT_SPECIFIC"
    elif 6 - textbook_wins >= 4 and ea_wins >= 4:
        verdict = "GENERIC"
    else:
        verdict = "MIXED"
    return dict(
        f1_textbook_vs_gadapt=f1, f2_ea_vs_textbook=f2, textbook_wins=textbook_wins,
        ea_wins=ea_wins, verdict=verdict,
        secondary_gadapt_vs_ea=family("gadapt_i39", "one_plus_one_ea"),
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
    # Longest runs first so the pool stays busy.
    tasks = [(n, m, s) for n in reversed(INSTANCES) for m in METHODS for s in SEEDS]
    with Pool(processes) as pool:
        runs = []
        for i, run in enumerate(pool.imap_unordered(one_run, tasks), 1):
            runs.append(run)
            if i % 12 == 0:
                print(f"{i}/{len(tasks)} runs, {time.monotonic() - start:.0f} s", flush=True)
    if any(x["calls"] != BUDGET for x in runs):
        raise RuntimeError("Evaluation accounting failed")
    if any(x["validator_calls_excluded"] != VALIDATOR_CALLS for x in runs if x["method"] == "gadapt_i39"):
        raise RuntimeError("Validator exclusion failed")
    here = os.path.abspath(__file__)
    folder = os.path.dirname(here)
    deps = [os.path.join(folder, f) for f in ("iteration44_mutation_mechanism.py",
                                              "iteration43_budget_operator_diagnostic.py",
                                              "iteration42_phase0_vig.py")]
    result = dict(
        protocol="research/ITERATION45_PROTOCOL.md", protocol_commit="7061d7f",
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
    out = main(sys.argv[1] if len(sys.argv) > 1 else "research/results/iteration45/generic_vs_specific.json")
    a = out["analysis"]
    print(json.dumps(dict(verdict=a["verdict"], textbook_wins=a["textbook_wins"],
                          ea_wins=a["ea_wins"], seconds=out["total_seconds"]), indent=1))
