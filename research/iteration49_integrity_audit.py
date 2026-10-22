"""I49: black-box evaluation-integrity audit of Python optimization libraries.

Previously frozen: research/ITERATION49_PROTOCOL.md (commit 92b307f). Run with the pinned audit
environment (research/h4_requirements_lock.txt) and the repository on PYTHONPATH (GAdapt control).
"""
import contextlib
import hashlib
import io
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

warnings.filterwarnings("ignore")

BUDGET = 1000
SEEDS = tuple(range(6000, 6005))
DIMS = (2, 10)
FUNCTIONS = ("sphere", "rastrigin", "plateau")
LOWER, UPPER = -5.0, 5.0
LIBRARIES = ("pymoo", "deap", "pygad", "geneticalgorithm", "nevergrad", "optuna", "pyswarms", "cma", "scipy_de")
CONTROLS = ("gadapt",)
INTEGRITY = ("C1", "C3", "C4", "C5", "R1", "R2", "R3", "D2")
REL = 1e-9


# ---------------------------------------------------------------- problems and recording

class Problem:
    def __init__(self, function, d, scale=None, shift=None):
        self.function, self.d = function, d
        self.a = np.ones(d) if scale is None else np.asarray(scale, float)
        self.b = np.zeros(d) if shift is None else np.asarray(shift, float)
        self.lo = LOWER * self.a + self.b
        self.hi = UPPER * self.a + self.b

    def base(self, z):
        if self.function == "sphere":
            c = LOWER + 0.37 * (UPPER - LOWER)
            return float(np.sum((z - c) ** 2))
        if self.function == "rastrigin":
            return float(10 * len(z) + np.sum(z * z - 10 * np.cos(2 * np.pi * z)))
        return float(np.sum(np.floor(z)))

    def __call__(self, x):
        return self.base((np.asarray(x, float) - self.b) / self.a)

    def normalized(self, x):
        return (np.asarray(x, float) - self.lo) / (self.hi - self.lo)


class Recorder:
    def __init__(self, problem):
        self.problem, self.phase, self.calls = problem, "search", []

    def __call__(self, x):
        x = np.array(x, dtype=float).ravel()
        f = self.problem(x)
        self.calls.append((x, f, self.phase))
        return f


# ---------------------------------------------------------------- adapters

def _seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)


def run_pymoo(rec, p, seed):
    from pymoo.algorithms.soo.nonconvex.ga import GA
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.optimize import minimize

    class P(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=p.d, n_obj=1, xl=p.lo, xu=p.hi)

        def _evaluate(self, x, out, *args, **kwargs):
            out["F"] = rec(x)

    res = minimize(P(), GA(), ("n_evals", BUDGET), seed=seed, verbose=False)
    rec.phase = "post"
    return dict(x=np.asarray(res.X, float), f=float(np.ravel(res.F)[0]),
                reported_evals=int(res.algorithm.evaluator.n_eval), documented_max=BUDGET)


def run_deap(rec, p, seed):
    from deap import algorithms, base, creator, tools
    if not hasattr(creator, "FitMin"):
        creator.create("FitMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitMin)
    tb = base.Toolbox()
    tb.register("individual", lambda: creator.Individual([random.uniform(l, h) for l, h in zip(p.lo, p.hi)]))
    tb.register("population", tools.initRepeat, list, tb.individual)
    tb.register("evaluate", lambda ind: (rec(ind),))
    tb.register("mate", tools.cxBlend, alpha=0.5)
    tb.register("mutate", tools.mutGaussian, mu=0.0, sigma=list((p.hi - p.lo) / 10), indpb=0.1)
    tb.register("select", tools.selTournament, tournsize=3)
    hof = tools.HallOfFame(1)
    _, logbook = algorithms.eaSimple(tb.population(n=50), tb, cxpb=0.5, mutpb=0.2, ngen=19,
                                     halloffame=hof, verbose=False)
    rec.phase = "post"
    return dict(x=np.asarray(hof[0], float), f=float(hof[0].fitness.values[0]),
                reported_evals=int(sum(logbook.select("nevals"))), documented_max=None)


def run_pygad(rec, p, seed):
    import pygad
    ga = pygad.GA(num_generations=19, num_parents_mating=10, sol_per_pop=50, num_genes=p.d,
                  fitness_func=lambda g, s, i: -rec(s),
                  gene_space=[{"low": float(l), "high": float(h)} for l, h in zip(p.lo, p.hi)],
                  init_range_low=float(min(p.lo)), init_range_high=float(max(p.hi)),
                  random_seed=seed, suppress_warnings=True)
    ga.run()
    rec.phase = "post"
    solution, fitness, _ = ga.best_solution()
    return dict(x=np.asarray(solution, float), f=-float(fitness), reported_evals=None, documented_max=None)


def run_geneticalgorithm(rec, p, seed):
    from geneticalgorithm import geneticalgorithm as G
    model = G(function=rec, dimension=p.d, variable_type="real",
              variable_boundaries=np.column_stack([p.lo, p.hi]), convergence_curve=False, progress_bar=False,
              algorithm_parameters={"max_num_iteration": 19, "population_size": 50, "mutation_probability": 0.1,
                                    "elit_ratio": 0.01, "crossover_probability": 0.5, "parents_portion": 0.3,
                                    "crossover_type": "uniform", "max_iteration_without_improv": None})
    with contextlib.redirect_stdout(io.StringIO()):
        model.run()
    rec.phase = "post"
    out = model.output_dict
    return dict(x=np.asarray(out["variable"], float), f=float(out["function"]), reported_evals=None,
                documented_max=None)


def run_nevergrad(rec, p, seed):
    import nevergrad as ng
    param = ng.p.Array(shape=(p.d,), lower=p.lo, upper=p.hi)
    param.random_state = np.random.RandomState(seed)
    opt = ng.optimizers.NGOpt(parametrization=param, budget=BUDGET)
    recommendation = opt.minimize(rec)
    rec.phase = "post"
    loss = getattr(recommendation, "loss", None)
    return dict(x=np.asarray(recommendation.value, float), f=(None if loss is None else float(loss)),
                reported_evals=int(opt.num_tell), documented_max=BUDGET)


def run_optuna(rec, p, seed):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.ERROR)
    study = optuna.create_study(sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(lambda t: rec([t.suggest_float(f"x{i}", float(p.lo[i]), float(p.hi[i])) for i in range(p.d)]),
                   n_trials=BUDGET)
    rec.phase = "post"
    return dict(x=np.array([study.best_params[f"x{i}"] for i in range(p.d)], float), f=float(study.best_value),
                reported_evals=len(study.trials), documented_max=BUDGET)


def run_pyswarms(rec, p, seed):
    import pyswarms as ps
    opt = ps.single.GlobalBestPSO(n_particles=50, dimensions=p.d, options={"c1": 0.5, "c2": 0.3, "w": 0.9},
                                  bounds=(p.lo, p.hi))
    cost, pos = opt.optimize(lambda X: np.array([rec(x) for x in X]), iters=19, verbose=False)
    rec.phase = "post"
    return dict(x=np.asarray(pos, float), f=float(cost), reported_evals=None, documented_max=None)


def run_cma(rec, p, seed):
    import cma
    xbest, es = cma.fmin2(rec, list((p.lo + p.hi) / 2), 0.3 * float(np.mean(p.hi - p.lo)),
                          {"bounds": [list(p.lo), list(p.hi)], "maxfevals": BUDGET, "seed": seed, "verbose": -9})
    rec.phase = "post"
    return dict(x=np.asarray(xbest, float), f=float(es.result.fbest), reported_evals=int(es.result.evaluations),
                documented_max=BUDGET)


def run_scipy_de(rec, p, seed):
    from scipy.optimize import differential_evolution
    maxiter = BUDGET // (15 * p.d) - 1
    res = differential_evolution(rec, list(zip(p.lo, p.hi)), maxiter=maxiter, rng=seed)
    rec.phase = "post"
    return dict(x=np.asarray(res.x, float), f=float(res.fun), reported_evals=int(res.nfev), documented_max=None)


def run_gadapt(rec, p, seed, probe=True):
    from gadapt.ga import GA
    ga = GA(cost_function=rec, exit_check="generations", number_of_generations=40, probe_cost_function=probe)
    for l, h in zip(p.lo, p.hi):
        ga.add(float(l), float(h))
    res = ga.execute()
    rec.phase = "post"
    return dict(x=np.array([res.result_values[i] for i in sorted(res.result_values)], float), f=float(res.min_cost),
                reported_evals=None, documented_max=None)


# ---------------------------------------------------------------- validation optimizers (planted faults)

def run_reference(rec, p, seed, fault=None):
    rng = np.random.default_rng(seed)
    best_x, best_f = None, math.inf
    budget = BUDGET
    if fault == "probe":
        rec(p.lo.copy())
        budget -= 1
    if fault == "over":
        budget += 1
    seen = []
    for i in range(budget):
        x = rng.uniform(p.lo, p.hi) if not (fault == "duplicate" and i == 10) else seen[3].copy()
        seen.append(x)
        f = rec(x)
        if f < best_f:
            best_x, best_f = x.copy(), f
    rec.phase = "post"
    if fault == "unevaluated":
        best_x = best_x + 1e-6
    if fault == "wrong_value":
        best_f = best_f - 1.0
    # each mutant plants exactly one fault: the reported count is the true count
    return dict(x=best_x, f=best_f, reported_evals=len(rec.calls), documented_max=BUDGET)


ADAPTERS = {name: globals()[f"run_{name}"] for name in LIBRARIES + CONTROLS}


# ---------------------------------------------------------------- classification

def classify(calls, result, problem):
    xs = [c[0] for c in calls]
    search = [c for c in calls if c[2] == "search"]
    flags = {k: 0 for k in ("C1", "C2", "C3", "C4", "C5", "R1", "R2", "R3", "D2")}
    seen = set()
    for x, _, _ in calls:
        if np.array_equal(x, problem.lo) or np.array_equal(x, problem.hi):
            flags["C1"] += 1
        key = x.tobytes()
        if key in seen:
            flags["C2"] += 1
        seen.add(key)
        if np.any(x < problem.lo) or np.any(x > problem.hi):
            flags["C3"] += 1
    if result["documented_max"] is not None:
        flags["C4"] = max(0, len(calls) - result["documented_max"])
    flags["C5"] = len(calls) - len(search)
    x_star = np.asarray(result["x"], float).ravel()
    matches = [c for c in calls if c[0].shape == x_star.shape and np.all(np.abs(c[0] - x_star) <= 1e-12)]
    flags["R1"] = int(not matches)
    if result["f"] is not None and matches:
        recorded = matches[0][1]
        flags["R2"] = int(abs(result["f"] - recorded) > REL * max(1.0, abs(recorded)))
    if result["f"] is not None and search:
        best = min(c[1] for c in search)
        flags["R3"] = int(result["f"] - best > REL * max(1.0, abs(best)))
    if result["reported_evals"] is not None:
        flags["D2"] = int(result["reported_evals"] != len(calls))
    return flags, len(calls)


def sequence_hash(calls):
    h = hashlib.sha256()
    for x, f, phase in calls:
        h.update(x.tobytes())
        h.update(repr(f).encode())
        h.update(phase.encode())
    return h.hexdigest()


def execute(library, function, d, seed, transformed=False, **kwargs):
    if transformed:
        scale = 10.0 ** (2 * (np.arange(d) % 3))
        problem = Problem(function, d, scale=scale, shift=1000.0 * np.arange(d))
    else:
        problem = Problem(function, d)
    rec = Recorder(problem)
    _seed_all(seed)
    fn = ADAPTERS.get(library, run_reference)
    with contextlib.redirect_stdout(io.StringIO()):
        result = fn(rec, problem, seed, **kwargs) if library in ADAPTERS else run_reference(rec, problem, seed, **kwargs)
    return problem, rec.calls, result


def audit_cell(task):
    library, function, d, seed = task
    start = time.monotonic()
    try:
        problem, calls, result = execute(library, function, d, seed)
        flags, n = classify(calls, result, problem)
        _, calls2, _ = execute(library, function, d, seed)
        flags["D3"] = int(sequence_hash(calls) != sequence_hash(calls2))
        tproblem, tcalls, _ = execute(library, function, d, seed, transformed=True)
        same_len = len(tcalls) == len(calls)
        diff = (max(float(np.max(np.abs(problem.normalized(a[0]) - tproblem.normalized(b[0]))))
                    for a, b in zip(calls, tcalls)) if same_len and calls else math.inf)
        return dict(library=library, function=function, d=d, seed=seed, calls=n, flags=flags,
                    g1_invariant=bool(same_len and diff <= 1e-6), g1_max_normalized_diff=diff,
                    error=None, seconds=round(time.monotonic() - start, 2))
    except Exception as exc:  # recorded, never hidden
        return dict(library=library, function=function, d=d, seed=seed, calls=None, flags=None, g1_invariant=None,
                    g1_max_normalized_diff=None, error=f"{type(exc).__name__}: {str(exc)[:200]}",
                    seconds=round(time.monotonic() - start, 2))


def validate():
    expected = {None: set(), "probe": {"C1"}, "duplicate": {"C2"}, "over": {"C4"}, "unevaluated": {"R1"},
                "wrong_value": {"R2"}}
    report = {}
    for fault, want in expected.items():
        problem, calls, result = execute("reference", "sphere", 2, 1, fault=fault)
        flags, _ = classify(calls, result, problem)
        got = {k for k, v in flags.items() if v}
        report[str(fault)] = dict(expected=sorted(want), flagged=sorted(got), ok=got == want)
    for probe in (True, False):
        problem, calls, result = execute("gadapt", "sphere", 2, 1, probe=probe)
        got = classify(calls, result, problem)[0]["C1"] > 0
        report[f"gadapt_probe_{probe}"] = dict(expected_C1=probe, C1=got, ok=got == probe)
    return report, all(v["ok"] for v in report.values())


def summarize(cells):
    out = {}
    for lib in LIBRARIES + CONTROLS:
        rows = [c for c in cells if c["library"] == lib]
        ok = [c for c in rows if c["error"] is None]
        classes = {k: sum(1 for c in ok if c["flags"][k] > 0) for k in ("C1", "C2", "C3", "C4", "C5", "R1", "R2",
                                                                       "R3", "D2", "D3")}
        dup = [c["flags"]["C2"] / c["calls"] for c in ok if c["calls"]]
        out[lib] = dict(runs=len(rows), errors=len(rows) - len(ok), runs_with_class=classes,
                        integrity_finding=any(classes[k] for k in INTEGRITY + ("D3",)),
                        median_duplicate_fraction=float(np.median(dup)) if dup else None,
                        g1_invariant_runs=sum(1 for c in ok if c["g1_invariant"]),
                        calls_range=[min(c["calls"] for c in ok), max(c["calls"] for c in ok)] if ok else None)
    k = sum(out[lib]["integrity_finding"] for lib in LIBRARIES)
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, len(LIBRARIES) - k + 1))
    hi = 1.0 if k == len(LIBRARIES) else float(beta.ppf(0.975, k + 1, len(LIBRARIES) - k))
    verdict = "COMMON" if k >= 3 else "RARE" if k <= 1 else "BETWEEN"
    return out, dict(libraries_with_finding=k, of=len(LIBRARIES), clopper_pearson_95=[lo, hi], verdict=verdict)


def main(output="research/results/iteration49/integrity_audit.json"):
    start = time.monotonic()
    validation, passed = validate()
    print(json.dumps(validation, indent=1), flush=True)
    if not passed:
        raise SystemExit("Tool validation failed (protocol §6): not running the audit")
    tasks = [(lib, fn, d, s) for lib in LIBRARIES + CONTROLS for fn in FUNCTIONS for d in DIMS for s in SEEDS]
    cells = []
    with Pool() as pool:
        for i, cell in enumerate(pool.imap_unordered(audit_cell, tasks), 1):
            cells.append(cell)
            if i % 30 == 0:
                print(f"{i}/{len(tasks)} cells, {time.monotonic() - start:.0f} s", flush=True)
    per_library, primary = summarize(cells)
    here = os.path.abspath(__file__)
    versions = {}
    for mod in ("pymoo", "deap", "pygad", "nevergrad", "optuna", "pyswarms", "cma", "scipy", "numpy"):
        try:
            versions[mod] = __import__(mod).__version__
        except Exception:
            versions[mod] = None
    result = dict(protocol="research/ITERATION49_PROTOCOL.md", protocol_commit="92b307f",
                  source_sha256=hashlib.sha256(open(here, "rb").read()).hexdigest(),
                  environment=dict(python=sys.version.split()[0], platform=platform.platform(), versions=versions),
                  validation=validation, cells=sorted(cells, key=lambda c: (c["library"], c["function"], c["d"],
                                                                           c["seed"])),
                  per_library=per_library, primary=primary, total_seconds=round(time.monotonic() - start, 1))
    os.makedirs(os.path.dirname(output), exist_ok=True)
    json.dump(result, open(output, "w"), indent=1)
    print(json.dumps(primary, indent=1))


if __name__ == "__main__":
    main()
