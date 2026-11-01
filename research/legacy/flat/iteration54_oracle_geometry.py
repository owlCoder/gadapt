"""I54: oracle geometry test on the I47/I53 AC economic dispatch.

Frozen protocol: research/ITERATION54_PROTOCOL.md. GAdapt runs unchanged; only its coordinates are changed:
u = 0.5 + A y, with A from the shape of the final CMA-ES covariance of the I53 reference run (no location information).
Usage: python -m research.iteration54_oracle_geometry geometry|runs|analyse
"""
import json
import math
import os
import sys
import time
import warnings
from multiprocessing import Pool

import numpy as np

from research.iteration43_budget_operator_diagnostic import holm
from research.iteration47_invariance import CASES, Dispatch
from research.iteration53_oracle_step import (
    ALPHA, BUDGET, GAP_FLOOR, REFERENCE_BUDGET, Tracked, _one_sided, cma_minimize, gadapt_run, provenance, sha256,
)

warnings.filterwarnings("ignore")

SEEDS = tuple(range(5500, 5512))
METHODS = ("g0", "w", "wd", "cma")
I53_REFERENCE = os.path.join("research", "results", "iteration53", "reference.json")
OUT = os.path.join("research", "results", "iteration54")
TESTS = {"primary": ("w", "g0"), "rotation_over_scales": ("w", "wd"), "scales_only": ("wd", "g0")}


def shape(covariance):
    """A = B diag(d), d = sqrt of the eigenvalues normalized to max 1 (only the shape of the covariance)."""
    eigenvalues, eigenvectors = np.linalg.eigh(np.asarray(covariance, dtype=float))
    d = np.sqrt(np.maximum(eigenvalues, 0.0))
    return eigenvectors * (d / d.max())


def diagonal_shape(covariance):
    d = np.sqrt(np.maximum(np.diag(np.asarray(covariance, dtype=float)), 0.0))
    return np.diag(d / d.max())


def y_half_widths(a):
    """Smallest box in y containing A^-1 applied to [0, 1]^N - 0.5."""
    return 0.5 * np.sum(np.abs(np.linalg.inv(a)), axis=1)


class Whitened:
    """Maps y to u = 0.5 + A y, clips u to [0, 1], evaluates x = lo + u (hi - lo) through a Tracked counter."""

    def __init__(self, tracked, a, lower, upper):
        self.tracked, self.a, self.lower, self.upper = tracked, np.asarray(a, dtype=float), lower, upper
        self.clipped = 0

    def to_x(self, y):
        u = 0.5 + self.a @ np.asarray(y, dtype=float)
        clipped = np.clip(u, 0.0, 1.0)
        return self.lower + clipped * (self.upper - self.lower), bool(np.any(clipped != u))

    def cost(self, y):
        x, was_clipped = self.to_x(y)
        if not self.tracked.done:
            self.clipped += was_clipped
        return self.tracked.mw(x)


def geometry_run(task):
    """Re-runs the best I53 reference run (same seed and budget) and returns its final covariance shape."""
    case_name, seed, expected = task
    dispatch = Dispatch(case_name)
    lower, upper = np.array(dispatch.bounds_mw).T
    tracked = Tracked(dispatch, REFERENCE_BUDGET)
    import cma
    es = cma.CMAEvolutionStrategy(np.full(len(lower), 0.5), 0.3,
                                  dict(bounds=[0, 1], seed=seed, verbose=-9, maxfevals=10**9))
    while not tracked.done:
        xs = es.ask()
        es.tell(xs, [tracked.mw(lower + np.asarray(x) * (upper - lower)) for x in xs])
    covariance = np.asarray(es.sm.C, dtype=float)
    return dict(case=case_name, seed=seed, reproduced=tracked.best_score == expected, best_score=tracked.best_score,
                expected=expected, covariance=covariance.tolist(),
                condition=float(np.linalg.cond(covariance)))


def run(task):
    case_name, method, seed, covariance = task
    dispatch = Dispatch(case_name)
    lower, upper = np.array(dispatch.bounds_mw).T
    tracked = Tracked(dispatch, BUDGET)
    clipped = 0
    start = time.monotonic()
    if method == "cma":
        cma_minimize(tracked, lower, upper, seed)
    elif method == "g0":
        gadapt_run(tracked.mw, dispatch.bounds_mw, seed, lambda: tracked.done)
    else:
        a = shape(covariance) if method == "w" else diagonal_shape(covariance)
        whitened = Whitened(tracked, a, lower, upper)
        h = y_half_widths(a)
        gadapt_run(whitened.cost, list(zip(-h, h)), seed, lambda: tracked.done)
        clipped = whitened.clipped
    return dict(case=case_name, method=method, seed=seed, calls=tracked.calls, over_budget_requests=tracked.over_budget,
                pf_failures=tracked.failures, best_score=tracked.best_score, best_feasible_cost=tracked.best_feasible,
                best_x=tracked.best_x.tolist(), clipped_evaluations=clipped, variables=len(dispatch.variables),
                seconds=round(time.monotonic() - start, 2))


def analyse(runs, reference):
    out, decisive, supported, refuted = {}, [], 0, 0
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
            closure={m: ((med["g0"] - med[m]) / denominator if denominator >= 0.5 else None) for m in ("w", "wd")},
            below_reference={m: sum(r["best_score"] < best_known for r in runs
                                    if r["case"] == case_name and r["method"] == m) for m in METHODS},
            feasible_runs={m: sum(r["best_feasible_cost"] is not None for r in runs
                                  if r["case"] == case_name and r["method"] == m) for m in METHODS},
            clipped_fraction={m: float(np.mean([r["clipped_evaluations"] / r["calls"] for r in runs
                                                if r["case"] == case_name and r["method"] == m])) for m in ("w", "wd")})
    adjusted = {name: holm(p) for name, p in p_values.items()}
    for i, case_name in enumerate(CASES):
        entry = out[case_name]
        entry["holm_p"] = {name: adjusted[name][i] for name in TESTS}
        if entry["closure"]["w"] is None:
            continue
        decisive.append(case_name)
        supported += entry["closure"]["w"] >= 0.5 and entry["holm_p"]["primary"] < ALPHA
        refuted += entry["closure"]["w"] < 0.2
    needed = math.ceil(0.75 * len(decisive)) if decisive else 0
    if decisive and supported >= needed:
        verdict = "SUPPORTED"
    elif decisive and refuted >= needed:
        verdict = "REFUTED"
    else:
        verdict = "PARTIAL"
    out["decision"] = dict(verdict=verdict, decisive_cases=decisive, needed=needed, supported=supported,
                           below_0_2=refuted)
    return out


def main(part):
    os.makedirs(OUT, exist_ok=True)
    reference = json.load(open(I53_REFERENCE))["reference"]
    geometry_path = os.path.join(OUT, "geometry.json")
    start = time.monotonic()
    if part == "geometry":
        with Pool() as pool:
            results = pool.map(geometry_run, [(c, reference[c]["seed"], reference[c]["best_score"]) for c in CASES])
        json.dump(dict(provenance=provenance(), i54_sha256=sha256("research/iteration54_oracle_geometry.py"), i53_reference_sha256=sha256(I53_REFERENCE), runs=results,
                       seconds=round(time.monotonic() - start, 1)), open(geometry_path, "w"), indent=1)
        print(json.dumps({r["case"]: dict(reproduced=r["reproduced"], condition=r["condition"]) for r in results}))
    elif part == "runs":
        geometry = {r["case"]: r for r in json.load(open(geometry_path))["runs"]}
        if not all(g["reproduced"] for g in geometry.values()):
            raise SystemExit("reference not reproduced; stop (protocol)")
        tasks = [(c, m, s, geometry[c]["covariance"]) for c in CASES for m in METHODS for s in SEEDS]
        with Pool() as pool:
            results = pool.map(run, tasks, chunksize=1)
        json.dump(dict(provenance=provenance(), i54_sha256=sha256("research/iteration54_oracle_geometry.py"), runs=results, seconds=round(time.monotonic() - start, 1)),
                  open(os.path.join(OUT, "runs.json"), "w"), indent=1)
    elif part == "analyse":
        runs = json.load(open(os.path.join(OUT, "runs.json")))["runs"]
        result = analyse(runs, reference)
        json.dump(result, open(os.path.join(OUT, "analysis.json"), "w"), indent=1)
        print(json.dumps(result["decision"]))


if __name__ == "__main__":
    main(sys.argv[1])
