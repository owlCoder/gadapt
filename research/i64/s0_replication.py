"""I64-S0: replication of the mentor's benchmark with real evaluation counting (frozen protocol: research/ITERATION64_PROTOCOL.md).

Runs the mentor's own `execute_gadapt_experiment`, `execute_pygad_experiment` and `execute_scipy_de_experiment` UNCHANGED
(num_runs=1 per seed) from the clone `gadapt_experiments@0e388356ba954d17a8d78941bd18a4580cc9d210`, with the mentor's GA/pygad.GA/DE
parameters copied verbatim. The only interventions: a call counter around the objective (GAdapt deep-copies the GA, hence
__deepcopy__ returns self), and a seed injected into SciPy DE (`rng=seed`; the mentor's call is unseeded).

  MBENCH=<clone> python research/i64/s0_replication.py gate|run|analyse        (interpreter: the mentor's pinned environment)
"""
import gzip
import hashlib
import json
import math
import os
import random
import subprocess
import sys

MBENCH = os.environ["MBENCH"]
sys.path.insert(0, MBENCH)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("S0_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_s0"))
COMMIT = "0e388356ba954d17a8d78941bd18a4580cc9d210"

import numpy as np  # noqa: E402
import pygad  # noqa: E402
import scipy.optimize  # noqa: E402
from gadapt.ga import GA  # noqa: E402
import research_experiments.runners.scipy_de_experiment as de_mod  # noqa: E402
from research_experiments.functions.ackley import ackley_func  # noqa: E402
from research_experiments.functions.beale import beale_func  # noqa: E402
from research_experiments.functions.booth import booth_func  # noqa: E402
from research_experiments.functions.griewank import griewank_func  # noqa: E402
from research_experiments.functions.himmelblau import himmelblau_func  # noqa: E402
from research_experiments.functions.rastrigin import rastrigin_func  # noqa: E402
from research_experiments.functions.rosenbrock import rosenbrock_func  # noqa: E402
from research_experiments.functions.sphere import sphere_func  # noqa: E402
from research_experiments.functions.styblinski_tang import styblinski_tang_func  # noqa: E402
from research_experiments.plugins.pygad.pygad_blending_crossover import blend_crossover_pygad  # noqa: E402
from research_experiments.plugins.pygad.pygad_roulette_wheel_selection import get_pygad_parent_selection  # noqa: E402
from research_experiments.runners.gadapt_experiment import execute_gadapt_experiment  # noqa: E402
from research_experiments.runners.pygad_experiment import execute_pygad_experiment  # noqa: E402
from research_experiments.runners.scipy_de_experiment import execute_scipy_de_experiment  # noqa: E402
from research_experiments.settings.experiment_ga_settings import ExperimentGASettings  # noqa: E402

POP, SAT, GENS, ELITE, MUT = 64, 20, 600, 50.0, 60
B_ANALYSIS = 12000
TAUS = (1e-2, 1e-4, 1e-6)
N_SEEDS = int(os.environ.get("S0_SEEDS", "20"))  # 20 in the study; smaller only for pipeline rehearsal in a temp directory
FUNCS = [  # (name, f, low, high, dims)
    ("sphere", sphere_func, -5.12, 5.12, (2, 7, 20)), ("rosenbrock", rosenbrock_func, 0.5, 1.5, (2, 7, 20)),
    ("rastrigin", rastrigin_func, -5.12, 5.12, (2, 7, 20)), ("ackley", ackley_func, -4, 4, (2, 7, 20)),
    ("griewank", griewank_func, -50, 50, (2, 7, 20)), ("styblinski_tang", styblinski_tang_func, -5, 5, (2, 7, 20)),
    ("beale", beale_func, -4.5, 4.5, (2,)), ("himmelblau", himmelblau_func, -6, 6, (2,)), ("booth", booth_func, -10, 10, (2,))]
CELLS = [(name, d) for name, _, _, _, dims in FUNCS for d in dims]  # 21 cells, sorted by function then dimension
CONFIGS = ("gadapt", "pygad_random", "pygad_adaptive", "de")
SEED_BASE_S0 = 64_000_000
NORMALIZER_SEED = 64001


def seed_of(p, cell_index, s):
    """64.000.000 + 10^6 p + 1000 c + s (protocol §6; c = sorted cell index)."""
    return SEED_BASE_S0 + 1_000_000 * p + 1000 * cell_index + s


def func_of(name):
    return next(f for n, f, *_ in FUNCS if n == name)


def bounds_of(name):
    return next((lo, hi) for n, _, lo, hi, _ in FUNCS if n == name)


def f_star(name, d):
    if name == "styblinski_tang":
        from numpy.polynomial import polynomial as P
        roots = np.roots([4, 0, -32, 5])
        a = min(r.real for r in roots if abs(r.imag) < 1e-12)
        return d * (a ** 4 - 16 * a ** 2 + 5 * a) / 2
    return 0.0


# ------------------------------------------------------------------ call counting

PHASE_FRAMES = {"best_solution": "best_solution", "find_fitness_for_first_generation": "init_manual",
                "__call__": None}


class Counter:
    """Counts every physical call; keeps improvement events (call index, f) and the best vector; phase by call stack."""

    def __init__(self, f):
        self.f, self.n, self.n_search, self.best, self.best_x, self.events, self.phases = f, 0, 0, math.inf, None, [], {}

    def __deepcopy__(self, memo):  # GA.execute() deep-copies the GA: keep one shared counter
        return self

    def phase(self):
        frame = sys._getframe(2)
        for _ in range(30):
            if frame is None:
                break
            name = frame.f_code.co_name
            if name == "best_solution":
                return "best_solution"
            if name == "find_fitness_for_first_generation":
                return "init_manual"
            if name == "_check_cost_function":
                return "gadapt_validation"
            if name == "__call__" and "NoImprovementStopper" in str(frame.f_locals.get("self", "").__class__):
                return "de_callback"
            frame = frame.f_back
        return "search"

    def __call__(self, x):
        v = float(self.f(x))
        self.n += 1
        ph = self.phase()
        self.phases[ph] = self.phases.get(ph, 0) + 1
        if ph == "search":
            self.n_search += 1
        if math.isfinite(v) and v < self.best:
            self.best, self.best_x = v, [float(t) for t in x]
            self.events.append((self.n, v, self.n_search))  # (physical call index, f, index among search calls only)
        return v


def configure(seed_setting=None):
    s = ExperimentGASettings()
    s.num_runs, s.saturation_criteria, s.number_of_generations, s.population_size = 1, SAT, GENS, POP
    s.keep_elitism_percentage, s.percentage_of_mutation_candidate_solutions = ELITE, MUT
    s.percentage_of_mutation_decision_variables = MUT
    s.logging_step = 10 ** 9
    return s


def run_one(config, name, d, seed):
    """One run of the mentor's configuration on cell (name, d) with this seed. Returns the record."""
    s = configure()
    f = func_of(name)
    lo, hi = bounds_of(name)
    counter = Counter(f)
    random.seed(seed)
    np.random.seed(seed)
    result_list, info = [], {}
    if config == "gadapt":
        ga = GA(cost_function=counter, population_size=s.population_size,
                population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                candidate_solution_mutation="variable_columnar_diversity, random",
                decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
                percentage_of_mutation_candidate_solutions=s.percentage_of_mutation_candidate_solutions,
                percentage_of_mutation_decision_variables=s.percentage_of_mutation_decision_variables,
                exit_check="min_cost", keep_elitism_percentage=s.keep_elitism_percentage,
                max_attempt_no=s.saturation_criteria, number_of_generations=s.number_of_generations,
                parent_selection="roulette_wheel", crossover_probability=0.5, immigration_number=0, crossover="blending",
                ensure_unique_individuals=False, logging=False)
        for _ in range(d):
            ga.add(min_value=lo, max_value=hi, step=None)
        traces, final, _, gens = execute_gadapt_experiment(ga, f"{name}{d}", result_list)
    elif config in ("pygad_random", "pygad_adaptive"):
        sel = get_pygad_parent_selection(s.pygad_parent_selection)
        mut = dict(mutation_type="random", mutation_probability=s.pygad_random_mutation_probability) if config == "pygad_random" \
            else dict(mutation_type="adaptive", mutation_probability=list(s.pygad_adaptive_mutation_probabilities))
        elite = round((s.keep_elitism_percentage / 100) * s.population_size)

        def get_ga_instance():
            return pygad.GA(num_generations=1000, num_parents_mating=elite, parent_selection_type=sel,
                            sol_per_pop=s.population_size, num_genes=d, gene_type=float,
                            gene_space=[{"low": lo, "high": hi}] * d, fitness_func=lambda inst, sol, idx: 0 - counter(sol),
                            suppress_warnings=True, keep_elitism=elite, stop_criteria=f"saturate_{s.saturation_criteria}",
                            crossover_type=blend_crossover_pygad, **mut)
        traces, final, _, gens = execute_pygad_experiment(get_ga_instance, f"{name}{d}", result_list, s.number_of_generations)
    elif config == "de":
        real = scipy.optimize.differential_evolution
        de_mod.differential_evolution = lambda *a, **k: real(*a, rng=seed, **k)  # seed injection only
        try:
            traces, final, _, gens = execute_scipy_de_experiment(counter, [(lo, hi)] * d, f"{name}{d}", result_list)
        finally:
            de_mod.differential_evolution = real
    else:
        raise ValueError(config)
    return dict(config=config, function=name, d=d, seed=seed, calls=counter.n, phases=counter.phases, generations=float(gens),
                mentor_final_rounded=float(final), best_f=counter.best, best_x=counter.best_x, events=counter.events)


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def manifest(stage):
    import platform
    head = subprocess.run(["git", "-C", MBENCH, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.split()
    return dict(stage=stage, python=platform.python_version(), pip_freeze=freeze, mentor_commit=head, expected_commit=COMMIT,
                driver_sha256=sha(os.path.abspath(__file__)),
                protocol_sha256=sha(os.path.join(os.path.dirname(HERE), "ITERATION64_PROTOCOL.md")),
                settings=dict(pop=POP, sat=SAT, gens=GENS, elite=ELITE, mut=MUT, b_analysis=B_ANALYSIS, taus=TAUS, cells=CELLS,
                              configs=CONFIGS, seeds=N_SEEDS, seed_base=SEED_BASE_S0))


def save(name, data):
    os.makedirs(OUT, exist_ok=True)
    with gzip.open(os.path.join(OUT, name + ".json.gz"), "wt") as fh:
        json.dump(data, fh)


def load(name):
    with gzip.open(os.path.join(OUT, name + ".json.gz"), "rt") as fh:
        return json.load(fh)


def exists(name):
    return os.path.exists(os.path.join(OUT, name + ".json.gz"))


def require_commit():
    m = manifest("check")
    if m["mentor_commit"] != COMMIT:
        raise SystemExit(f"STOP: mentor repository is at {m['mentor_commit']}, expected {COMMIT}")
    return m


# ------------------------------------------------------------------ normalizers and gates

def normalizers():
    rng = np.random.RandomState(NORMALIZER_SEED)
    out = {}
    for name, f, lo, hi, dims in FUNCS:
        for d in dims:
            u = rng.uniform(lo, hi, size=(4096, d))
            vals = np.array([f(x) for x in u]) - f_star(name, d)
            s = float(np.median(vals))
            if not s > 0:
                raise SystemExit(f"STOP: non-positive normalizer for {name} d={d}")
            out[f"{name}|{d}"] = dict(s=s, f_star=f_star(name, d), min_sample=float(vals.min()))
    return out


def stage_gate():
    if exists("gate"):
        raise SystemExit("EXISTS: gate artifacts exist; controlled recovery required (create-once)")
    m = require_commit()
    norm = normalizers()
    for key, v in norm.items():
        if v["min_sample"] < -1e-12 * v["s"]:
            raise SystemExit(f"STOP: sampled value below f* for {key}")
    # gates (1) counting, (2) determinism, (3) witness; cells: sphere 2, rastrigin 7, booth 2; seeds p = 9
    cells = [("sphere", 2), ("rastrigin", 7), ("booth", 2)]
    report, mismatches = [], []
    for name, d in cells:
        ci = CELLS.index((name, d))
        for config in CONFIGS:
            seed = seed_of(9, ci, 1)
            a, b = run_one(config, name, d, seed), run_one(config, name, d, seed)
            same = a["calls"] == b["calls"] and a["events"] == b["events"] and a["best_f"] == b["best_f"]
            counted = sum(a["phases"].values()) == a["calls"]
            witness = abs(func_of(name)(np.array(a["best_x"])) - a["best_f"]) <= 1e-12 * max(1.0, abs(a["best_f"]))
            report.append(dict(cell=[name, d], config=config, calls=a["calls"], phases=a["phases"], deterministic=same,
                               counted=counted, witness=bool(witness)))
            if not (same and counted and witness and a["calls"] > 0):
                mismatches.append(report[-1])
    save("normalizers", norm)
    save("gate", dict(passed=not mismatches, report=report, mismatches=mismatches, manifest=m))
    print(json.dumps(dict(passed=not mismatches, mismatches=len(mismatches)), indent=1))
    if mismatches:
        raise SystemExit("STOP: S0 gate failed (counting, determinism or witness)")


def stage_run():
    if exists("runs"):
        raise SystemExit("EXISTS: runs exist; controlled recovery required (create-once)")
    if not (exists("gate") and load("gate")["passed"]):
        raise SystemExit("STOP: the gate did not pass")
    m = require_commit()
    g = load("gate")["manifest"]
    for k in ("python", "pip_freeze", "mentor_commit", "driver_sha256", "protocol_sha256"):
        if g[k] != m[k]:
            raise SystemExit(f"STOP: {k} differs from the gated build")
    records = []
    for ci, (name, d) in enumerate(CELLS):
        for s in range(1, N_SEEDS + 1):
            for config in CONFIGS:
                for attempt in (1, 2):  # a technical failure is repeated once with the same seed (§7)
                    try:
                        r = run_one(config, name, d, seed_of(0, ci, s))
                        r["attempt"], r["s"] = attempt, s
                        records.append(r)
                        break
                    except Exception as exc:  # noqa: BLE001
                        if attempt == 2:
                            save("runs_partial", dict(records=records, failed=[name, d, config, s, repr(exc)]))
                            raise SystemExit(f"STOP: repeated technical failure {name} {d} {config} seed {s}: {exc!r}")
        print("cell", name, d, "done", flush=True)
    save("runs", dict(records=records, manifest=m))


# ------------------------------------------------------------------ analysis (protocol §2-§3)

def gap(rec, norm):
    n = norm[f"{rec['function']}|{rec['d']}"]
    return max(0.0, (rec["best_f"] - n["f_star"]) / n["s"])


def ecdf_area(rec, norm, search_only=False):
    n = norm[f"{rec['function']}|{rec['d']}"]
    total = 0.0
    for tau in TAUS:
        hit = next((e[2] if search_only else e[0] for e in rec["events"] if max(0.0, (e[1] - n["f_star"]) / n["s"]) <= tau), None)
        if hit is not None and hit <= B_ANALYSIS:
            total += (B_ANALYSIS - hit + 1) / B_ANALYSIS
    return total / len(TAUS)


def weights():
    w = {}
    for name, _, _, _, dims in FUNCS:
        for d in dims:
            w[(name, d)] = (1 / 9) / len(dims)
    return w


def cvar(values, share=0.1):
    k = max(1, int(math.ceil(share * len(values))))
    return float(np.mean(sorted(values)[-k:]))


def stage_analyse():
    if exists("analysis"):
        raise SystemExit("EXISTS: analysis exists (create-once)")
    runs = load("runs")["records"]
    norm = load("normalizers")
    w = weights()
    data = {}  # (cell, config) -> list over seeds s of (A, L, g, calls, gens)
    for r in sorted(runs, key=lambda r: (r["function"], r["d"], r["config"], r["s"])):
        L = gap(r, norm) / (1 + gap(r, norm))
        data.setdefault(((r["function"], r["d"]), r["config"]), []).append((ecdf_area(r, norm), L, gap(r, norm), r["calls"], r["generations"], ecdf_area(r, norm, True), r["phases"].get("search", 0)))
    cells = list(w)
    arr = {k: np.array(v) for k, v in data.items()}
    for k, v in arr.items():
        if len(v) != N_SEEDS:
            raise SystemExit(f"STOP: {k} has {len(v)} runs, expected {N_SEEDS}")
    comps = [c for c in CONFIGS if c != "gadapt"]

    def stats(idx):  # idx: per-cell index arrays (paired across configs)
        dA, dM = {}, {}
        for c in comps:
            a = sum(w[cell] * (arr[(cell, "gadapt")][idx[cell], 0].mean() - arr[(cell, c)][idx[cell], 0].mean()) for cell in cells)
            m = sum(w[cell] * (np.median(arr[(cell, c)][idx[cell], 2]) - np.median(arr[(cell, "gadapt")][idx[cell], 2])) for cell in cells)
            dA[c], dM[c] = a, m
        return np.array([dA[c] for c in comps] + [dM[c] for c in comps])
    full = {cell: np.arange(N_SEEDS) for cell in cells}
    point = stats(full)
    rng = np.random.default_rng(64)
    B = 20000 if os.environ.get("S0_FULL_BOOT", "1") == "1" else 2000
    boots = np.empty((B, len(point)))
    for b in range(B):
        boots[b] = stats({cell: rng.integers(0, N_SEEDS, N_SEEDS) for cell in cells})
    se = boots.std(axis=0, ddof=1)
    alpha = 0.01
    if np.any(se <= 0):
        raise SystemExit("STOP: zero bootstrap variance blocks confirmation (§3)")
    tstar = float(np.quantile(np.max(np.abs(boots - point) / se, axis=1), 1 - alpha))
    lo, hi = point - tstar * se, point + tstar * se
    names = [f"dA|{c}" for c in comps] + [f"dM|{c}" for c in comps]
    contrasts = {n: dict(estimate=float(p), lower=float(l), upper=float(h)) for n, p, l, h in zip(names, point, lo, hi)}
    dA_lo = {c: contrasts[f"dA|{c}"]["lower"] for c in comps}
    dA_hi = {c: contrasts[f"dA|{c}"]["upper"] for c in comps}
    dM_lo = {c: contrasts[f"dM|{c}"]["lower"] for c in comps}
    dM_hi = {c: contrasts[f"dM|{c}"]["upper"] for c in comps}
    all_win = all(dA_lo[c] > 0 for c in comps)
    exception = [e for e in comps if all(dA_lo[c] > 0 for c in comps if c != e) and dM_lo[e] > 0]
    supported = bool(all_win or exception)
    worse_eff = [c for c in comps if dA_hi[c] < 0]
    opposite = bool(len(worse_eff) >= 2 or any(dA_hi[c] < 0 and dM_hi[c] < 0 for c in comps))
    verdict = "supported" if supported else ("opposite" if opposite else "undecided")
    descriptive = {}
    for (cell, c), v in arr.items():
        descriptive[f"{cell[0]}|{cell[1]}|{c}"] = dict(calls_mean=float(v[:, 3].mean()), gens_mean=float(v[:, 4].mean()),
                                                      A_mean=float(v[:, 0].mean()), gap_median=float(np.median(v[:, 2])),
                                                      cvar90=cvar(list(v[:, 1])),
                                                      reach=[float(np.mean(v[:, 2] <= t)) for t in TAUS])
    agg = {c: dict(calls_mean=float(sum(w[cell] * arr[(cell, c)][:, 3].mean() for cell in cells)),
                   gens_mean=float(sum(w[cell] * arr[(cell, c)][:, 4].mean() for cell in cells)),
                   A=float(sum(w[cell] * arr[(cell, c)][:, 0].mean() for cell in cells)),
                   A_search_only=float(sum(w[cell] * arr[(cell, c)][:, 5].mean() for cell in cells)),
                   search_calls_mean=float(sum(w[cell] * arr[(cell, c)][:, 6].mean() for cell in cells)),
                   cvar90=float(sum(w[cell] * cvar(list(arr[(cell, c)][:, 1])) for cell in cells)),
                   median_gap=float(sum(w[cell] * np.median(arr[(cell, c)][:, 2]) for cell in cells)))
           for c in CONFIGS}
    out = dict(verdict=verdict, supported=supported, opposite=opposite, exception_candidates=exception, tstar=tstar, alpha=alpha,
               bootstrap=B, contrasts=contrasts, aggregate=agg, descriptive=descriptive)
    save("analysis", out)
    print(json.dumps(dict(verdict=verdict, contrasts=contrasts, aggregate=agg), indent=1))


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    {"gate": stage_gate, "run": stage_run, "analyse": stage_analyse}.get(stage, lambda: print(__doc__))()
