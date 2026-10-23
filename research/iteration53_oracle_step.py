"""I53: oracle step-size test on the I47 AC economic dispatch.

Frozen protocol: research/ITERATION53_PROTOCOL.md. The oracle patch replaces only the standard deviation of the
columnar-diversity Gaussian mutator, inside the worker process of an oracle run; the library is not modified.
Usage: python -m research.iteration53_oracle_step synthetic|reference|runs|analyse
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
from scipy.stats import wilcoxon

from gadapt.ga import GA
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_variable_columnar_diversity_decision_variable_mutator import (
    NormalDistributionVariableColumnarDiversityDecisionVariableMutator as ColumnarMutator,
)
from research.iteration43_budget_operator_diagnostic import holm
from research.iteration47_invariance import CASES, OVER_BUDGET, Dispatch

warnings.filterwarnings("ignore")

ALPHA = 0.05
BUDGET = 3000
SEEDS = tuple(range(5300, 5312))
REFERENCE_BUDGET = 60000
REFERENCE_SEEDS = (7001, 7002, 7003)
METHODS = ("g0", "gn", "or1", "orn", "orn01", "cma")
# method -> (oracle kappa or None, uniform reset component kept)
GADAPT_ARMS = {"g0": (None, True), "gn": (None, False), "or1": (1.0, True), "orn": (1.0, False),
               "orn01": (0.1, False)}
SYNTH_N = 10
SYNTH_SEEDS = tuple(range(5400, 5412))
SYNTH_PROBLEMS = ("sphere", "ellipsoid", "rotated_ellipsoid")
# arm -> (step: default / no floor / oracle, uniform reset component kept)
SYNTH_ARMS = {"DR": ("default", True), "DN": ("default", False), "FR": ("nofloor", True),
              "FN": ("nofloor", False), "OR": ("oracle", True), "ON": ("oracle", False)}
GAP_FLOOR = 1e-12
OUT = os.path.join("research", "results", "iteration53")


class Tracked:
    """Counts true evaluations (as I47 Counted) and keeps the best evaluated point."""

    def __init__(self, dispatch, budget):
        self.dispatch, self.budget = dispatch, budget
        self.calls, self.over_budget, self.failures = 0, 0, 0
        self.best_score, self.best_x = math.inf, None
        self.best_feasible = None

    @property
    def done(self):
        return self.calls >= self.budget

    def mw(self, pg_mw):
        if self.done:
            self.over_budget += 1
            return OVER_BUDGET
        self.calls += 1
        info = self.dispatch.evaluate(pg_mw)
        self.failures += not info["converged"]
        if info["score"] < self.best_score:
            self.best_score, self.best_x = info["score"], np.asarray(pg_mw, dtype=float).copy()
        if info.get("feasible") and (self.best_feasible is None or info["cost"] < self.best_feasible):
            self.best_feasible = info["cost"]
        return info["score"]


def oracle_std_dev(tracked, x_ref, lower, upper, kappa):
    """sigma_rel = clip(kappa * r / sqrt(N), 1e-12, 0.6); r = normalized distance of the best point to x_ref."""
    if tracked.best_x is None:
        return 0.6
    r = float(np.linalg.norm((tracked.best_x - x_ref) / (upper - lower)))
    return float(np.clip(kappa * r / math.sqrt(len(x_ref)), 1e-12, 0.6))


def gadapt_run(cost, bounds, seed, done, reset=True, min_std_dev=0.001):
    """I47 gadapt_minimize (log_relative) with the reset component and the sigma floor as factors."""
    random.seed(seed)
    np.random.seed(seed)
    ga = GA(cost_function=cost, probe_cost_function=False, exit_check="generations",
            number_of_generations=10**6, exit_function=done, timeout=3600,
            columnar_diversity_metric="log_relative", normal_distribution_mutation_min_std_dev=min_std_dev,
            decision_variable_mutation="variable_columnar_diversity,random" if reset else "variable_columnar_diversity")
    for lo, hi in bounds:
        ga.add(float(lo), float(hi))
    return str(ga.execute().messages)[:200]


def with_oracle(kappa, tracked, x_ref, lower, upper, function):
    """Runs function() with the oracle standard deviation patched in (kappa None: no patch); always restores."""
    original = ColumnarMutator._calculate_normal_distribution_standard_deviation
    if kappa is not None:
        x_ref = np.asarray(x_ref, dtype=float)
        ColumnarMutator._calculate_normal_distribution_standard_deviation = (
            lambda self: oracle_std_dev(tracked, x_ref, lower, upper, kappa))
    try:
        return function()
    finally:
        ColumnarMutator._calculate_normal_distribution_standard_deviation = original


def cma_minimize(tracked, lower, upper, seed):
    import cma
    es = cma.CMAEvolutionStrategy(np.full(len(lower), 0.5), 0.3,
                                  dict(bounds=[0, 1], seed=seed, verbose=-9, maxfevals=10**9))
    while not tracked.done:
        xs = es.ask()
        es.tell(xs, [tracked.mw(lower + np.asarray(x) * (upper - lower)) for x in xs])


def reference_run(task):
    case_name, seed = task
    dispatch = Dispatch(case_name)
    lower, upper = np.array(dispatch.bounds_mw).T
    tracked = Tracked(dispatch, REFERENCE_BUDGET)
    cma_minimize(tracked, lower, upper, seed)
    return dict(case=case_name, seed=seed, calls=tracked.calls, best_score=tracked.best_score,
                best_x=tracked.best_x.tolist())


def run(task):
    case_name, method, seed, x_ref = task
    dispatch = Dispatch(case_name)
    lower, upper = np.array(dispatch.bounds_mw).T
    tracked = Tracked(dispatch, BUDGET)
    start = time.monotonic()
    if method == "cma":
        cma_minimize(tracked, lower, upper, seed)
    else:
        kappa, reset = GADAPT_ARMS[method]
        with_oracle(kappa, tracked, x_ref, lower, upper,
                    lambda: gadapt_run(tracked.mw, dispatch.bounds_mw, seed, lambda: tracked.done, reset))
    return dict(case=case_name, method=method, seed=seed, calls=tracked.calls,
                over_budget_requests=tracked.over_budget, pf_failures=tracked.failures,
                best_score=tracked.best_score, best_feasible_cost=tracked.best_feasible,
                best_x=tracked.best_x.tolist(), variables=len(dispatch.variables),
                seconds=round(time.monotonic() - start, 2))


class Synthetic:
    """Quadratic with known optimum; same evaluate() contract as Dispatch."""

    def __init__(self, problem, seed):
        rng = np.random.default_rng(seed)
        self.x_star = rng.uniform(-3, 3, SYNTH_N)
        self.weights = (np.ones(SYNTH_N) if problem == "sphere"
                        else 10.0 ** (6.0 * np.arange(SYNTH_N) / (SYNTH_N - 1)))
        self.rotation = (np.linalg.qr(rng.standard_normal((SYNTH_N, SYNTH_N)))[0]
                         if problem == "rotated_ellipsoid" else np.eye(SYNTH_N))
        self.bounds_mw = [(-5.0, 5.0)] * SYNTH_N

    def evaluate(self, x):
        z = self.rotation @ (np.asarray(x, dtype=float) - self.x_star)
        return dict(score=float(np.dot(self.weights, z * z)), converged=True)


def synthetic_run(task):
    problem, arm, seed = task
    synthetic = Synthetic(problem, seed)
    lower, upper = np.array(synthetic.bounds_mw).T
    tracked = Tracked(synthetic, BUDGET)
    if arm == "CMA":
        cma_minimize(tracked, lower, upper, seed)
    else:
        step, reset = SYNTH_ARMS[arm]
        with_oracle(1.0 if step == "oracle" else None, tracked, synthetic.x_star, lower, upper,
                    lambda: gadapt_run(tracked.mw, synthetic.bounds_mw, seed, lambda: tracked.done, reset,
                                       1e-12 if step == "nofloor" else 0.001))
    return dict(problem=problem, arm=arm, seed=seed, calls=tracked.calls, over_budget_requests=tracked.over_budget,
                gap=tracked.best_score)


def _one_sided(better, worse):
    diff = [w - b for b, w in zip(better, worse)]
    return float(wilcoxon(diff, alternative="greater").pvalue) if any(diff) else 1.0


def analyse_synthetic(runs):
    log_gap = {(p, a): {r["seed"]: math.log10(max(r["gap"], GAP_FLOOR)) for r in runs
                        if r["problem"] == p and r["arm"] == a}
               for p in SYNTH_PROBLEMS for a in list(SYNTH_ARMS) + ["CMA"]}
    med = {f"{p}:{a}": float(np.median(list(v.values()))) for (p, a), v in log_gap.items()}
    a1 = holm([_one_sided([log_gap[(p, "ON")][s] for s in SYNTH_SEEDS], [log_gap[(p, "DR")][s] for s in SYNTH_SEEDS])
               for p in SYNTH_PROBLEMS])

    def closure(p):
        denominator = med[f"{p}:DR"] - med[f"{p}:CMA"]
        return (med[f"{p}:DR"] - med[f"{p}:ON"]) / denominator if denominator >= 0.5 else None

    contrasts = {}
    for name, better, worse in (("F_vs_D_reset", "FR", "DR"), ("F_vs_D_noreset", "FN", "DN"),
                                ("N_vs_R_default", "DN", "DR"), ("N_vs_R_oracle", "ON", "OR"),
                                ("O_vs_D_noreset", "ON", "DN")):
        contrasts[name] = dict(zip(SYNTH_PROBLEMS, holm(
            [_one_sided([log_gap[(p, better)][s] for s in SYNTH_SEEDS], [log_gap[(p, worse)][s] for s in SYNTH_SEEDS])
             for p in SYNTH_PROBLEMS])))
    c_diagonal, c_rotated = closure("ellipsoid"), closure("rotated_ellipsoid")
    return dict(median_log10_gap=med, A1_holm=dict(zip(SYNTH_PROBLEMS, a1)),
                A1=all(p < ALPHA for p in a1),
                closure_on={p: closure(p) for p in SYNTH_PROBLEMS},
                A2=(None if c_diagonal is None or c_rotated is None else (c_diagonal >= 0.9 and c_rotated < 0.5)),
                contrasts_holm=contrasts)


# test name -> (better arm, worse arm); "primary" decides H53, the others are the preregistered attributions
TESTS = {"primary": ("orn", "g0"), "S1_reset": ("gn", "g0"), "S2_step_no_reset": ("orn", "gn"),
         "S3_step_with_reset": ("or1", "g0")}


def analyse(runs, reference):
    out = {}
    decisive, closed, refuted = [], 0, 0
    p_values = {name: [] for name in TESTS}
    for case_name in CASES:
        best_known = reference[case_name]["best_score"]
        log_gap = {m: {r["seed"]: math.log10(max(r["best_score"] - best_known, GAP_FLOOR))
                       for r in runs if r["case"] == case_name and r["method"] == m} for m in METHODS}
        med = {m: float(np.median(list(log_gap[m].values()))) for m in METHODS}
        for name, (better, worse) in TESTS.items():
            p_values[name].append(_one_sided([log_gap[better][s] for s in SEEDS], [log_gap[worse][s] for s in SEEDS]))
        denominator = med["g0"] - med["cma"]
        out[case_name] = dict(
            best_known=best_known, median_log10_gap=med, gap_g0_minus_cma=denominator,
            below_reference={m: sum(r["best_score"] < best_known for r in runs
                                    if r["case"] == case_name and r["method"] == m) for m in METHODS},
            feasible_runs={m: sum(r["best_feasible_cost"] is not None for r in runs
                                  if r["case"] == case_name and r["method"] == m) for m in METHODS},
            closure={m: ((med["g0"] - med[m]) / denominator if denominator >= 0.5 else None)
                     for m in GADAPT_ARMS if m != "g0"},
            interaction=dict(s1_plus_s3=(med["g0"] - med["gn"]) + (med["g0"] - med["or1"]),
                             combined=med["g0"] - med["orn"]))
    adjusted = {name: holm(p) for name, p in p_values.items()}
    for i, case_name in enumerate(CASES):
        entry = out[case_name]
        entry["holm_p"] = {name: adjusted[name][i] for name in TESTS}
        if entry["closure"]["orn"] is None:
            continue
        decisive.append(case_name)
        closed += entry["closure"]["orn"] >= 0.9 and entry["holm_p"]["primary"] < ALPHA
        refuted += entry["closure"]["orn"] < 0.5
    if closed >= 4:
        verdict = "SUPPORTED"
    elif refuted >= 3:
        verdict = "REFUTED"
    else:
        verdict = "PARTIAL"
    out["decision"] = dict(verdict=verdict, decisive_cases=decisive, closed=closed, below_half=refuted)
    return out


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def provenance():
    import cma
    import pypower
    sources = ["research/iteration53_oracle_step.py", "research/iteration47_invariance.py",
               "research/ITERATION53_PROTOCOL.md"]
    return dict(python=sys.version, platform=platform.platform(), numpy=np.__version__, scipy=scipy.__version__,
                cma=cma.__version__, pypower=getattr(pypower, "__version__", "unknown"),
                sha256={s: sha256(s) for s in sources})


def main(part):
    os.makedirs(OUT, exist_ok=True)
    reference_path = os.path.join(OUT, "reference.json")
    start = time.monotonic()
    if part == "synthetic":
        tasks = [(p, a, s) for p in SYNTH_PROBLEMS for a in list(SYNTH_ARMS) + ["CMA"] for s in SYNTH_SEEDS]
        with Pool() as pool:
            results = pool.map(synthetic_run, tasks, chunksize=1)
        json.dump(dict(provenance=provenance(), runs=results, analysis=analyse_synthetic(results),
                       seconds=round(time.monotonic() - start, 1)),
                  open(os.path.join(OUT, "synthetic.json"), "w"), indent=1)
        print(json.dumps({k: v for k, v in analyse_synthetic(results).items() if k in ("A1", "A2", "closure_on")}))
    elif part == "reference":
        with Pool() as pool:
            results = pool.map(reference_run, [(c, s) for c in CASES for s in REFERENCE_SEEDS])
        reference = {c: min((r for r in results if r["case"] == c), key=lambda r: r["best_score"]) for c in CASES}
        json.dump(dict(provenance=provenance(), runs=results, reference=reference,
                       seconds=round(time.monotonic() - start, 1)), open(reference_path, "w"), indent=1)
    elif part == "runs":
        reference = json.load(open(reference_path))["reference"]
        tasks = [(c, m, s, reference[c]["best_x"]) for c in CASES for m in METHODS for s in SEEDS]
        with Pool() as pool:
            results = pool.map(run, tasks, chunksize=1)
        json.dump(dict(provenance=provenance(), runs=results, seconds=round(time.monotonic() - start, 1)),
                  open(os.path.join(OUT, "runs.json"), "w"), indent=1)
    elif part == "analyse":
        reference = json.load(open(reference_path))["reference"]
        runs = json.load(open(os.path.join(OUT, "runs.json")))["runs"]
        json.dump(analyse(runs, reference), open(os.path.join(OUT, "analysis.json"), "w"), indent=1)
        print(json.dumps(json.load(open(os.path.join(OUT, "analysis.json")))["decision"]))


if __name__ == "__main__":
    main(sys.argv[1])
