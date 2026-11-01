"""I50: confirmatory replication of the I49 evaluation-integrity audit on a new, rule-based library sample.

Previously frozen: research/ITERATION50_PROTOCOL.md (commit c3598f6). Reuses the I49 problems, recorder and
classifier unchanged and adds D3x (cross-process reproducibility). Each library runs in its own venv; the cell
mode is executed by that venv's interpreter with `python -I`, the driver modes by the repository's .venv.

  python research/iteration50_integrity_audit.py validate
  python research/iteration50_integrity_audit.py smoke <library> <python>
  python research/iteration50_integrity_audit.py run <library> <python> [workers]
  python research/iteration50_integrity_audit.py aggregate
"""
import contextlib
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import warnings
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

import research.iteration49_integrity_audit as i49  # noqa: E402

warnings.filterwarnings("ignore")

BUDGET = 200
SMOKE_BUDGET = 20
RUN_TIMEOUT = 600
FUNCTIONS, DIMS, SEEDS = i49.FUNCTIONS, i49.DIMS, i49.SEEDS
INTEGRITY = ("C1", "C3", "C4", "C5", "R1", "R2", "R3", "D2", "D3", "D3x")
TORCH = ("evox", "evotorch")
OUT = os.path.join(HERE, "results", "iteration50")
MARK = "@@I50@@"
# one BLAS/OpenMP thread per run, so that parallel cells do not cause spurious timeouts (ELIGIBILITY §4)
THREADS = {k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}


def names(d):
    return [f"x{i:02d}" for i in range(d)]


def generations(pop, budget):
    """Generations after the initial population so that pop * (generations + 1) <= budget (protocol §3)."""
    return max(budget // pop - 1, 1)


class Recorder32(i49.Recorder):
    """Records (and returns) the float32 value a float32 library actually receives."""

    def __call__(self, x):
        x = np.array(x, dtype=float).ravel()
        f = float(np.float32(self.problem(x)))
        self.calls.append((x, f, self.phase))
        return f


def result(x=None, f=None, reported_evals=None, documented_max=None):
    return dict(x=None if x is None else np.asarray(x, float).ravel(), f=None if f is None else float(f),
                reported_evals=reported_evals, documented_max=documented_max)


# ---------------------------------------------------------------- adapters (ITERATION50_ELIGIBILITY.md)

def run_bayes_opt(rec, p, seed, budget):
    from bayes_opt import BayesianOptimization
    keys = names(p.d)
    opt = BayesianOptimization(f=lambda **kw: -rec([kw[k] for k in keys]),
                               pbounds={k: (float(l), float(h)) for k, l, h in zip(keys, p.lo, p.hi)},
                               random_state=seed, verbose=0)
    opt.maximize(init_points=5, n_iter=budget - 5)
    rec.phase = "post"
    best = opt.max
    return result([best["params"][k] for k in keys], -best["target"], documented_max=budget)


def run_cmaes(rec, p, seed, budget):
    from cmaes import CMA
    opt = CMA(mean=(p.lo + p.hi) / 2, sigma=0.3 * float(np.mean(p.hi - p.lo)),
              bounds=np.column_stack([p.lo, p.hi]), seed=seed)
    n = 0
    while n + opt.population_size <= budget:
        solutions = []
        for _ in range(opt.population_size):
            x = opt.ask()
            solutions.append((x, rec(x)))
        n += opt.population_size
        opt.tell(solutions)
    rec.phase = "post"
    return result()  # ask-and-tell: no reported result (R not applicable)


def run_scikit_opt(rec, p, seed, budget):
    from sko.DE import DE
    de = DE(func=lambda x: rec(x), n_dim=p.d, size_pop=50, max_iter=generations(50, budget),
            lb=list(p.lo), ub=list(p.hi))
    best_x, best_y = de.run()
    rec.phase = "post"
    return result(best_x, np.asarray(best_y).ravel()[0])


def run_gfo(rec, p, seed, budget):
    from gradient_free_optimizers import HillClimbingOptimizer
    keys = names(p.d)
    opt = HillClimbingOptimizer({k: (float(l), float(h)) for k, l, h in zip(keys, p.lo, p.hi)}, random_state=seed)
    opt.search(lambda para: rec([para[k] for k in keys]), n_iter=budget, verbosity=False, optimum="minimum")
    rec.phase = "post"
    return result([opt.best_para[k] for k in keys], opt.best_score, documented_max=budget)


def run_hyperactive(rec, p, seed, budget):
    from hyperactive.opt.gfo import HillClimbing
    keys = names(p.d)
    space = {k: np.arange(float(l), float(h), (float(h) - float(l)) / 100) for k, l, h in zip(keys, p.lo, p.hi)}
    opt = HillClimbing(search_space=space, n_iter=budget, random_state=seed,
                       experiment=lambda para: -rec([para[k] for k in keys]))
    best = opt.solve()
    rec.phase = "post"
    return result([best[k] for k in keys], documented_max=budget)


def run_niapy(rec, p, seed, budget):
    from niapy.algorithms.basic import ParticleSwarmAlgorithm
    from niapy.problems import Problem
    from niapy.task import Task

    class Box(Problem):
        def __init__(self):
            super().__init__(p.d, p.lo.copy(), p.hi.copy())

        def _evaluate(self, x):
            return rec(x)

    task = Task(problem=Box(), max_evals=budget)
    best_x, best_fit = ParticleSwarmAlgorithm(seed=seed).run(task)
    rec.phase = "post"
    return result(best_x, best_fit, reported_evals=int(task.evals), documented_max=budget)


def run_evolopy(rec, p, seed, budget):
    from EvoloPy.api import run_optimizer
    res = run_optimizer("PSO", lambda x: rec(x), lb=list(p.lo), ub=list(p.hi), dim=p.d, population_size=30,
                        iterations=generations(30, budget), num_runs=1, export_results=False,
                        export_details=False, export_convergence=False, export_boxplot=False,
                        display_plots=False, results_directory=os.path.join(os.getcwd(), "evolopy"))
    rec.phase = "post"
    return result(res["best_solution"], res["best_fitness"])


def run_smac(rec, p, seed, budget):
    from ConfigSpace import ConfigurationSpace
    from smac import HyperparameterOptimizationFacade, Scenario
    keys = names(p.d)
    space = ConfigurationSpace({k: (float(l), float(h)) for k, l, h in zip(keys, p.lo, p.hi)}, seed=seed)
    scenario = Scenario(space, deterministic=True, n_trials=budget, seed=seed,
                        output_directory=os.path.join(os.getcwd(), "smac"))
    smac = HyperparameterOptimizationFacade(scenario, lambda config, seed=0: rec([config[k] for k in keys]),
                                            overwrite=True, logging_level=40)
    incumbent = smac.optimize()
    rec.phase = "post"
    return result([incumbent[k] for k in keys], documented_max=budget)


def run_vizier(rec, p, seed, budget):
    from vizier.service import clients
    from vizier.service import pyvizier as vz
    keys = names(p.d)
    config = vz.StudyConfig(algorithm="DEFAULT")
    for k, l, h in zip(keys, p.lo, p.hi):
        config.search_space.root.add_float_param(k, float(l), float(h))
    config.metric_information.append(vz.MetricInformation("cost", goal=vz.ObjectiveMetricGoal.MINIMIZE))
    study = clients.Study.from_study_config(config, owner="i50", study_id=f"s{seed}_{time.time_ns()}")
    for _ in range(budget):
        for suggestion in study.suggest(count=1):
            suggestion.complete(vz.Measurement({"cost": rec([suggestion.parameters[k] for k in keys])}))
    rec.phase = "post"
    best = list(study.optimal_trials())[0].materialize()
    return result([best.parameters[k].value for k in keys], best.final_measurement.metrics["cost"].value)


def run_evox(rec, p, seed, budget):
    import torch
    from evox.algorithms import PSO
    from evox.core import Problem
    from evox.workflows import EvalMonitor, StdWorkflow

    class Box(Problem):
        def evaluate(self, pop):
            return torch.tensor([rec(x) for x in pop.detach().cpu().numpy()], dtype=pop.dtype)

    torch.manual_seed(seed)
    monitor = EvalMonitor()
    workflow = StdWorkflow(PSO(pop_size=100, lb=torch.tensor(p.lo, dtype=torch.float32),
                               ub=torch.tensor(p.hi, dtype=torch.float32)), Box(), monitor)
    workflow.init_step()
    for _ in range(generations(100, budget)):
        workflow.step()
    rec.phase = "post"
    return result(monitor.get_best_solution().detach().cpu().numpy(),
                  float(monitor.get_best_fitness().detach().cpu().numpy().ravel()[0]))


def run_evotorch(rec, p, seed, budget):
    import torch
    from evotorch import Problem
    from evotorch.algorithms import SNES
    problem = Problem("min", lambda x: torch.tensor(rec(x.detach().cpu().numpy()), dtype=torch.float32),
                      initial_bounds=(p.lo, p.hi), solution_length=p.d, seed=seed)  # SNES rejects hard bounds
    searcher = SNES(problem, stdev_init=0.3 * float(np.mean(p.hi - p.lo)))
    searcher.run(max(budget // searcher._popsize, 1))  # default popsize, chosen by SNES from the dimension
    rec.phase = "post"
    best = searcher.status["best"]
    return result(best.values.detach().cpu().numpy(), float(best.evals.detach().cpu().numpy().ravel()[0]))


def run_emukit(rec, p, seed, budget):
    from emukit.core import ContinuousParameter, ParameterSpace
    from emukit.core.initial_designs import RandomDesign
    from emukit.examples.gp_bayesian_optimization.single_objective_bayesian_optimization import (
        GPBayesianOptimization)
    keys = names(p.d)
    variables = [ContinuousParameter(k, float(l), float(h)) for k, l, h in zip(keys, p.lo, p.hi)]
    X = RandomDesign(ParameterSpace(variables)).get_samples(5)
    Y = np.array([[rec(x)] for x in X])
    bo = GPBayesianOptimization(variables_list=variables, X=X, Y=Y)
    bo.run_optimization(lambda X: np.array([[rec(x)] for x in X]), budget - 5)
    rec.phase = "post"
    return result()  # no documented result accessor in the quickstart (R not applicable)


def run_baybe(rec, p, seed, budget):
    import pandas as pd
    from baybe import Campaign
    from baybe.objectives import SingleTargetObjective
    from baybe.parameters import NumericalContinuousParameter
    from baybe.searchspace import SearchSpace
    from baybe.targets import NumericalTarget
    from baybe.utils.random import set_random_seed
    keys = names(p.d)
    set_random_seed(seed)
    campaign = Campaign(
        searchspace=SearchSpace.from_product([NumericalContinuousParameter(k, (float(l), float(h)))
                                              for k, l, h in zip(keys, p.lo, p.hi)]),
        objective=SingleTargetObjective(NumericalTarget(name="y", minimize=True)))
    for _ in range(budget):
        rec_df = campaign.recommend(batch_size=1)
        rec_df["y"] = [rec(row) for row in rec_df[keys].to_numpy()]
        campaign.add_measurements(pd.DataFrame(rec_df))
    rec.phase = "post"
    return result()  # ask-and-tell: no reported result (R not applicable)


def run_bofire(rec, p, seed, budget):
    from bofire.data_models.acquisition_functions.api import qLogEI
    from bofire.data_models.domain.api import Domain, Inputs, Outputs
    from bofire.data_models.features.api import ContinuousInput, ContinuousOutput
    from bofire.data_models.objectives.api import MinimizeObjective
    from bofire.strategies.api import SoboStrategy
    keys = names(p.d)
    domain = Domain(inputs=Inputs(features=[ContinuousInput(key=k, bounds=[float(l), float(h)])
                                            for k, l, h in zip(keys, p.lo, p.hi)]),
                    outputs=Outputs(features=[ContinuousOutput(key="y", objective=MinimizeObjective())]))
    experiments = domain.inputs.sample(10, seed=seed)
    experiments["y"] = [rec(row) for row in experiments[keys].to_numpy()]
    strategy = SoboStrategy.make(domain=domain, acquisition_function=qLogEI(), seed=seed)
    strategy.tell(experiments=experiments)
    for _ in range(budget - 10):
        new = strategy.ask(candidate_count=1)
        new["y"] = [rec(row) for row in new[keys].to_numpy()]
        strategy.tell(experiments=new)
    rec.phase = "post"
    return result()  # ask-and-tell: no reported result (R not applicable)


def run_gaft(rec, p, seed, budget):
    from gaft import GAEngine
    from gaft.components import BinaryIndividual, Population
    from gaft.operators import FlipBitMutation, RouletteWheelSelection, UniformCrossover
    template = BinaryIndividual(ranges=[(float(l), float(h)) for l, h in zip(p.lo, p.hi)], eps=0.001)
    population = Population(indv_template=template, size=50).init()
    engine = GAEngine(population=population, selection=RouletteWheelSelection(),
                      crossover=UniformCrossover(pc=0.8, pe=0.5), mutation=FlipBitMutation(pm=0.1))

    @engine.fitness_register
    @engine.minimize
    def fitness(indv):
        return rec(indv.solution)

    engine.run(ng=generations(50, budget))
    rec.phase = "post"
    best = population.best_indv(engine.fitness)  # the README's way to obtain the result
    return result(best.solution)


def run_solid(rec, p, seed, budget):
    from Solid.ParticleSwarm import ParticleSwarm

    class Swarm(ParticleSwarm):
        def _objective(self, member):
            return rec(member)

    best, value = Swarm(20, p.d, list(p.lo), list(p.hi), 0.5, 0.5, 0.5, generations(20, budget)).run(verbose=False)
    rec.phase = "post"
    return result(best, value)


# validation mutants for D3x (protocol §5): clean random search, hash- or time-seeded
def run_ref_seeded(rec, p, seed, budget, mode=None):
    if mode == "hash_seeded":
        s = abs(hash(f"seed{seed}")) % 2**32
    elif mode == "time_seeded":
        s = time.time_ns() % 2**32
    else:
        s = seed
    rng = np.random.default_rng(s)
    best_x, best_f = None, np.inf
    for _ in range(budget):
        x = rng.uniform(p.lo, p.hi)
        f = rec(x)
        if f < best_f:
            best_x, best_f = x.copy(), f
    rec.phase = "post"
    return result(best_x, best_f, reported_evals=len(rec.calls), documented_max=budget)


ADAPTERS = {name[4:]: fn for name, fn in globals().items() if name.startswith("run_")}
LIBRARIES = ("bayes_opt", "cmaes", "scikit_opt", "gfo", "hyperactive", "niapy", "evolopy", "smac", "vizier",
             "evox", "evotorch", "emukit", "baybe", "bofire", "gaft", "solid")


# ---------------------------------------------------------------- cell (runs inside the library's venv)

def execute(library, function, d, seed, budget, **kwargs):
    problem = i49.Problem(function, d)
    rec = (Recorder32 if library in TORCH else i49.Recorder)(problem)
    i49._seed_all(seed)
    with tempfile.TemporaryDirectory() as tmp:
        old = os.getcwd()
        os.chdir(tmp)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                res = ADAPTERS[library](rec, problem, seed, budget, **kwargs)
        finally:
            os.chdir(old)
    return problem, rec.calls, res


def classify(calls, res, problem):
    """The I49 classifier, unchanged; R1-R3 are not applicable when a library reports no result."""
    if res["x"] is None:
        flags, n = i49.classify(calls, dict(res, x=calls[0][0], f=None), problem)
        flags.update(R1=0, R2=0, R3=0)
        return flags, n, False
    flags, n = i49.classify(calls, res, problem)
    return flags, n, True


def cell(library, function, d, seed, budget, twice, mode=None):
    kwargs = {} if mode is None else dict(mode=mode)
    out = dict(library=library, function=function, d=int(d), seed=int(seed))
    start = time.monotonic()
    try:
        problem, calls, res = execute(library, function, int(d), int(seed), budget, **kwargs)
        flags, n, r_applicable = classify(calls, res, problem) if calls else ({}, 0, False)
        out.update(calls=n, flags=flags, r_applicable=r_applicable, hash=i49.sequence_hash(calls), error=None)
        if twice:
            _, calls2, _ = execute(library, function, int(d), int(seed), budget, **kwargs)
            out["hash_rerun"] = i49.sequence_hash(calls2)
    except BaseException as exc:  # recorded, never hidden
        out.update(calls=None, flags=None, error=f"{type(exc).__name__}: {str(exc)[:200]}")
    out["seconds"] = round(time.monotonic() - start, 2)
    print(MARK + json.dumps(out), flush=True)


# ---------------------------------------------------------------- driver (repository .venv)

def subprocess_cell(python, library, function, d, seed, budget, twice, hashseed, mode=None):
    args = [python, "-I", os.path.abspath(__file__), "cell", library, function, str(d), str(seed), str(budget),
            "1" if twice else "0"] + ([mode] if mode else [])
    env = dict(os.environ, PYTHONHASHSEED=str(hashseed), **THREADS)
    try:
        proc = subprocess.run(args, capture_output=True, text=True, env=env,
                              timeout=RUN_TIMEOUT * (2 if twice else 1))
    except subprocess.TimeoutExpired:
        return dict(library=library, function=function, d=d, seed=seed, calls=None, flags=None, error="timeout")
    lines = [line for line in proc.stdout.splitlines() if line.startswith(MARK)]
    if not lines:
        return dict(library=library, function=function, d=d, seed=seed, calls=None, flags=None,
                    error=f"no result (exit {proc.returncode}): {proc.stderr.strip()[-200:]}")
    return json.loads(lines[-1][len(MARK):])


def audit_cell(python, library, function, d, seed, budget=BUDGET, mode=None):
    a = subprocess_cell(python, library, function, d, seed, budget, True, 1, mode)
    b = subprocess_cell(python, library, function, d, seed, budget, False, 2, mode)
    if a.get("error") is None:
        a["flags"]["D3"] = int(a["hash"] != a["hash_rerun"])
        a["flags"]["D3x"] = None if b.get("error") is not None else int(a["hash"] != b["hash"])
        a["cross_process_error"] = b.get("error")
    return a


def smoke(library, python, d=2, budget=SMOKE_BUDGET):
    """Protocol §2 criterion 5: constant cost, N = 2, budget 20; only completion (and time) is inspected.

    With d=10 and budget=200 it is the pre-run full-size technical check (ITERATION50_ELIGIBILITY.md).
    """
    out = subprocess_cell(python, library, "constant", int(d), 0, int(budget), False, 1)
    print(json.dumps(dict(library=library, d=int(d), budget=int(budget), completed=out.get("error") is None,
                          error=out.get("error"), seconds=out.get("seconds"))))


def validate():
    report, passed = i49.validate()
    python = sys.executable
    for mode, want in ((None, (0, 0)), ("hash_seeded", (0, 1)), ("time_seeded", (1, 1))):
        c = audit_cell(python, "ref_seeded", "sphere", 2, 1, 50, mode)
        got = (c["flags"]["D3"], c["flags"]["D3x"]) if c.get("error") is None else None
        report[f"d3x_{mode}"] = dict(expected_D3_D3x=list(want), got=got, ok=got == want, error=c.get("error"))
    passed = all(v["ok"] for v in report.values())
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(validation=report, passed=passed), open(os.path.join(OUT, "validation.json"), "w"), indent=1)
    print(json.dumps(report, indent=1))
    return passed


def run(library, python, workers=4):
    if not json.load(open(os.path.join(OUT, "validation.json")))["passed"]:
        raise SystemExit("Tool validation has not passed (protocol §5): not running the audit")
    tasks = [(fn, d, s) for fn in FUNCTIONS for d in DIMS for s in SEEDS]
    start = time.monotonic()
    with ThreadPoolExecutor(int(workers)) as pool:
        cells = list(pool.map(lambda t: audit_cell(python, library, *t), tasks))
    freeze = subprocess.run([python, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    json.dump(dict(library=library, python=subprocess.run([python, "-c", "import sys;print(sys.version)"],
                                                          capture_output=True, text=True).stdout.strip(),
                   pip_freeze=freeze.splitlines(), threads=THREADS, workers=int(workers), cells=cells, seconds=round(time.monotonic() - start, 1)),
              open(os.path.join(OUT, f"cells_{library}.json"), "w"), indent=1)
    print(library, "done", round(time.monotonic() - start), "s")


def aggregate():
    from scipy.stats import beta
    eligibility = json.load(open(os.path.join(OUT, "eligible.json")))
    per, assessed = {}, []
    for lib in eligibility["sample"]:
        data = json.load(open(os.path.join(OUT, f"cells_{lib}.json")))
        ok = [c for c in data["cells"] if c.get("error") is None]
        classes = {k: sum(1 for c in ok if (c["flags"].get(k) or 0) > 0)
                   for k in ("C1", "C2", "C3", "C4", "C5", "R1", "R2", "R3", "D2", "D3", "D3x")}
        dup = [c["flags"]["C2"] / c["calls"] for c in ok if c["calls"]]
        per[lib] = dict(runs=len(data["cells"]), errors=len(data["cells"]) - len(ok), runs_with_class=classes,
                        assessable=bool(ok), integrity_finding=bool(ok) and any(classes[k] for k in INTEGRITY),
                        r_applicable=bool(ok) and ok[0]["r_applicable"],
                        d3x_unavailable=sum(1 for c in ok if c["flags"].get("D3x") is None),
                        median_duplicate_fraction=float(np.median(dup)) if dup else None,
                        error_examples=sorted({c["error"] for c in data["cells"] if c.get("error")})[:3])
        if ok:
            assessed.append(lib)

    def cp(k, n):
        lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
        hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
        return [lo, hi]

    k = sum(per[lib]["integrity_finding"] for lib in assessed)
    n = len(assessed)
    lo, hi = cp(k, n)
    verdict = "REPLICATED" if (k / n >= 1 / 3 and lo >= 0.10) else "REFUTED" if hi < 1 / 3 else "INCONCLUSIVE"
    i49_k, i49_n = 4, 9
    primary = dict(libraries_with_finding=k, of=n, proportion=k / n, clopper_pearson_95=[lo, hi], verdict=verdict,
                   pooled_with_i49=dict(k=k + i49_k, n=n + i49_n, clopper_pearson_95=cp(k + i49_k, n + i49_n)),
                   unassessable=[lib for lib in eligibility["sample"] if lib not in assessed])
    here = os.path.abspath(__file__)
    out = dict(protocol="research/ITERATION50_PROTOCOL.md", protocol_commit="c3598f6",
               source_sha256=hashlib.sha256(open(here, "rb").read()).hexdigest(),
               i49_source_sha256=hashlib.sha256(open(i49.__file__, "rb").read()).hexdigest(),
               driver=dict(python=sys.version.split()[0], platform=platform.platform()),
               per_library=per, primary=primary)
    json.dump(out, open(os.path.join(OUT, "integrity_audit.json"), "w"), indent=1)
    print(json.dumps(primary, indent=1))


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "cell":
        lib, fn, d, seed, budget, twice = args[:6]
        if fn == "constant":
            i49.Problem.base = lambda self, z: 1.0
            fn = "sphere"
        cell(lib, fn, d, seed, int(budget), twice == "1", args[6] if len(args) > 6 else None)
    elif cmd == "validate":
        raise SystemExit(0 if validate() else 1)
    elif cmd == "smoke":
        smoke(*args)
    elif cmd == "run":
        run(*args)
    elif cmd == "aggregate":
        aggregate()
