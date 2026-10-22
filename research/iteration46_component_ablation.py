"""I46: GAdapt component ablation on binary route choice (and its preregistered confirmation).

Previously frozen: research/ITERATION46_PROTOCOL.md (commit dcb54a1). Reuses the I43 model,
the I43 (1+1)-EA, the I45 textbook GA and the I44 validator-free accounting unchanged.
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
from research.iteration44_mutation_mechanism import VALIDATOR_CALLS, ValidatorFree
from research.iteration45_generic_vs_specific import run_textbook_ga

ABLATION_INSTANCES = ("polska", "nobel-germany", "atlanta", "france", "geant", "germany50")
CONFIRMATION_INSTANCES = ("dfn-gwin", "newyork", "norway", "pioro40", "zib54", "cost266")
ABLATION_SEEDS = tuple(range(4600, 4612))
CONFIRMATION_SEEDS = tuple(range(4700, 4712))
ALPHA = 0.05

GADAPT_I39 = dict(population_size=24, cost_diversity_metric="log_relative",
                  population_mutation="cost_diversity,parent_diversity")
TOURNAMENT = dict(parent_selection="tournament")
UNIFORM = dict(crossover="uniform")
ELITISM_ONE = dict(keep_elitism_percentage=4)
ONE_GENE = dict(candidate_solution_mutation="random", number_of_mutation_decision_variables=1)
ARMS = {
    "A0": {},
    "A1": TOURNAMENT,
    "A2": UNIFORM,
    "A3": ELITISM_ONE,
    "A4": {**TOURNAMENT, **UNIFORM, **ELITISM_ONE},
    "A5": {**TOURNAMENT, **UNIFORM, **ELITISM_ONE, **ONE_GENE},
}
REFERENCES = ("TB", "EA")


def make_ga(cost, n, arm):
    algo = GA(cost_function=cost, exit_function=lambda: cost.done, exit_check="generations",
              number_of_generations=10**6, timeout=3600, **GADAPT_I39, **ARMS[arm])
    for _ in range(n):
        algo.add(0., 1., 1.)
    return algo


def one_run(task):
    name, method, seed = task
    random.seed(seed)
    np.random.seed(seed)
    f = build(name)
    start = time.monotonic()
    skipped = 0
    if method in ARMS:
        cost = ValidatorFree(f, f.n)
        stop = str(make_ga(cost, f.n, method).execute().messages)[:200]
        skipped = cost.skipped
    elif method == "TB":
        cost = Budgeted(f)
        stop = run_textbook_ga(cost, f.n)
    else:
        cost = Budgeted(f)
        stop = run_ea(cost, f.n)
    return dict(instance=name, method=method, seed=seed, calls=cost.calls,
                validator_calls_excluded=skipped, over_budget_requests=cost.over_budget,
                stop=stop, best_at={str(b): cost.at.get(b) for b in CHECKPOINTS},
                seconds=round(time.monotonic() - start, 3))


def _r(runs, f0, name, method, budget=BUDGET):
    rows = sorted((x for x in runs if x["instance"] == name and x["method"] == method),
                  key=lambda x: x["seed"])
    return np.array([(x["best_at"][str(budget)] - f0[name]) / f0[name] for x in rows])


def family(runs, f0, instances, pairs):
    tests = []
    for a, b in pairs:
        for name in instances:
            x, y = _r(runs, f0, name, a), _r(runs, f0, name, b)
            p = 1.0 if np.allclose(x, y) else float(wilcoxon(x, y).pvalue)
            tests.append(dict(instance=name, a=a, b=b, p=p,
                              median_r_a=float(np.median(x)), median_r_b=float(np.median(y))))
    for t, adj in zip(tests, holm([t["p"] for t in tests])):
        t["p_holm"] = adj
        t["a_significantly_better"] = adj < ALPHA and t["median_r_a"] < t["median_r_b"]
        t["a_significantly_worse"] = adj < ALPHA and t["median_r_a"] > t["median_r_b"]
    return tests


def count(tests, a, key):
    return sum(t[key] for t in tests if t["a"] == a)


def analyse_ablation(runs, f0):
    primary = family(runs, f0, ABLATION_INSTANCES, [(a, "A0") for a in ("A1", "A2", "A3")])
    secondary = family(runs, f0, ABLATION_INSTANCES, [(a, "TB") for a in ("A4", "A5")])
    causal = [a for a in ("A1", "A2", "A3") if count(primary, a, "a_significantly_better") >= 4]
    explained = {a: ("EXPLAINED" if 6 - count(secondary, a, "a_significantly_worse") >= 4
                     else "NOT_EXPLAINED" if count(secondary, a, "a_significantly_worse") >= 4
                     else "UNCLEAR") for a in ("A4", "A5")}
    methods = list(ARMS) + list(REFERENCES)
    return dict(primary=primary, secondary=secondary, causal_single_components=causal,
                combination=explained,
                median_r={n: {m: {str(b): float(np.median(_r(runs, f0, n, m, b))) for b in CHECKPOINTS}
                              for m in methods} for n in ABLATION_INSTANCES})


def analyse_confirmation(runs, f0, arm):
    tests = family(runs, f0, CONFIRMATION_INSTANCES, [(arm, "A0")])
    wins = count(tests, arm, "a_significantly_better")
    return dict(arm=arm, tests=tests, wins=wins, confirmed=wins >= 4,
                vs_textbook=family(runs, f0, CONFIRMATION_INSTANCES, [(arm, "TB")]),
                median_r={n: {m: {str(b): float(np.median(_r(runs, f0, n, m, b))) for b in CHECKPOINTS}
                              for m in ("A0", arm, "TB")} for n in CONFIRMATION_INSTANCES})


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def execute(output, instances, methods, seeds, analyse, protocol_note):
    start = time.monotonic()
    f0, sizes = {}, {}
    for name in instances:
        f = build(name)
        f0[name], sizes[name] = f(np.zeros(f.n, dtype=int)), dict(genes=f.n, unit=f.unit)
    tasks = [(n, m, s) for n in reversed(instances) for m in methods for s in seeds]
    with Pool() as pool:
        runs = []
        for i, run in enumerate(pool.imap_unordered(one_run, tasks), 1):
            runs.append(run)
            if i % 24 == 0:
                print(f"{i}/{len(tasks)} runs, {time.monotonic() - start:.0f} s", flush=True)
    if any(x["calls"] != BUDGET for x in runs):
        raise RuntimeError("Evaluation accounting failed")
    if any(x["validator_calls_excluded"] != VALIDATOR_CALLS for x in runs if x["method"] in ARMS):
        raise RuntimeError("Validator exclusion failed")
    here = os.path.abspath(__file__)
    folder = os.path.dirname(here)
    deps = [os.path.join(folder, f) for f in (
        "iteration45_generic_vs_specific.py", "iteration44_mutation_mechanism.py",
        "iteration43_budget_operator_diagnostic.py", "iteration42_phase0_vig.py")]
    result = dict(
        protocol="research/ITERATION46_PROTOCOL.md", protocol_commit="dcb54a1", part=protocol_note,
        source_sha256={os.path.basename(p): sha256(p) for p in [here] + deps},
        input_sha256={n: sha256(os.path.join(DATA_DIR, n + ".json")) for n in instances},
        environment=dict(python=sys.version.split()[0], platform=platform.platform(),
                         numpy=np.__version__, scipy=scipy.__version__, networkx=nx.__version__),
        arms={k: v for k, v in ARMS.items() if k in methods}, base_config=GADAPT_I39,
        synthetic_cost="identical to I43; NOT source SNDlib costs",
        f0=f0, sizes=sizes, runs=sorted(runs, key=lambda x: (x["instance"], x["method"], x["seed"])),
        analysis=analyse(runs, f0), total_seconds=round(time.monotonic() - start, 1))
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w") as handle:
        json.dump(result, handle, indent=1)
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "confirm":
        arm = sys.argv[2]
        out = execute("research/results/iteration46/confirmation.json", CONFIRMATION_INSTANCES,
                      ("A0", arm, "TB"), CONFIRMATION_SEEDS,
                      lambda runs, f0: analyse_confirmation(runs, f0, arm), f"confirmation of {arm} (§6)")
        a = out["analysis"]
        print(json.dumps(dict(arm=arm, wins=a["wins"], confirmed=a["confirmed"]), indent=1))
    else:
        out = execute("research/results/iteration46/ablation.json", ABLATION_INSTANCES,
                      tuple(ARMS) + REFERENCES, ABLATION_SEEDS, analyse_ablation, "ablation (§2-§4)")
        a = out["analysis"]
        print(json.dumps(dict(causal=a["causal_single_components"], combination=a["combination"],
                              seconds=out["total_seconds"]), indent=1))
