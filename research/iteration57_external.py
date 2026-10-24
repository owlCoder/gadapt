"""I57: GAdapt vs external methods (CMAwM, SciPy DE, random search) on the I56 discrete ORPD suite.

Frozen protocol: research/ITERATION57_PROTOCOL.md (frozen before any I56 test result). Reuses the I56 instrument,
evaluator, scalars, targets, T and bootstrap (research/iteration56_cht_study.py).

  python research/iteration57_external.py run [workers]     (after I56 test_ref exists)
  python research/iteration57_external.py analyse
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import iteration56_cht_study as i56  # noqa: E402
from iteration56_orpd import ORPD  # noqa: E402

PURPOSE = 5
SEEDS = range(1, 11)
CONFIGS = (("GAdapt", "SP"), ("GAdapt", "FR"), ("CMAwM", "SP"), ("CMAwM", "FR"), ("DE", "SP"), ("DE", "FR"),
           ("Random", "-"))
CONTRASTS = [(m, c) for m in ("CMAwM", "DE", "Random") for c in ("SP", "FR")]


class BudgetExhausted(Exception):
    pass


def seed_of(network, resolution, scenario_index, s):
    """The I56 formula with purpose 5."""
    return (10 ** 7 * PURPOSE + 10 ** 5 * i56.NETWORKS.index(network) + 10 ** 3 * resolution
            + 10 ** 2 * scenario_index + s)


class Scalar:
    """Index vector -> one actual runpf through the I56 evaluator -> the CHT scalar (FR applied explicitly)."""

    def __init__(self, problem, evaluator, cht_name):
        self.problem, self.evaluator = problem, evaluator
        self.cht = i56.CHT(cht_name, evaluator.f_ref) if cht_name in ("SP", "FR") else None

    def __call__(self, k):
        if self.evaluator.done:
            raise BudgetExhausted()
        k = np.clip(np.rint(np.asarray(k, float)), 0, self.problem.resolution - 1)
        values = list(self.problem.lo + k * self.problem.step)
        self.evaluator(values)
        raw = self.evaluator.cache[tuple(values)]
        return self.cht.merit(raw) if self.cht is not None else 0.0


def run_cmawm(problem, scalar, seed):
    from cmaes import CMAwM
    d, top = problem.d, problem.resolution - 1
    optimizer = CMAwM(mean=np.full(d, top / 2.0), sigma=top / 3.0, bounds=np.tile([0.0, float(top)], (d, 1)),
                      steps=np.ones(d), seed=seed)
    while not scalar.evaluator.done:
        solutions = []
        for _ in range(optimizer.population_size):
            if scalar.evaluator.done:
                return  # last generation: only the remaining candidates, no partial tell
            x_eval, x_tell = optimizer.ask()
            solutions.append((x_tell, scalar(x_eval)))
        optimizer.tell(solutions)


def run_de(problem, scalar, seed):
    from scipy.optimize import differential_evolution
    d, top = problem.d, problem.resolution - 1
    try:
        differential_evolution(scalar, [(0, top)] * d, strategy="best1bin", popsize=15, mutation=(0.5, 1),
                               recombination=0.7, init="latinhypercube", updating="immediate", workers=1,
                               vectorized=False, integrality=[True] * d, constraints=(), polish=False,
                               maxiter=10 ** 9, tol=0, atol=-1, rng=seed)
    except BudgetExhausted:
        pass


def run_random(problem, scalar, seed):
    rng = np.random.default_rng(seed)
    try:
        while True:
            scalar(rng.integers(0, problem.resolution, problem.d))
    except BudgetExhausted:
        pass


def run(task):
    import traceback
    try:
        return _run(task)
    except Exception:
        return dict(task=task, ok=False, complete=False, error=traceback.format_exc()[-2000:], T=None)


def _run(task):
    method, cht = task["method"], task["cht"]
    if method == "GAdapt":
        record = i56._run(dict(task, arm="AD-N", fixed=None, instrument=False))
        record["task"] = task
        return record
    load_factor, scenario_seed = task["scenario"]
    problem = ORPD(task["network"], task["resolution"], load_factor, i56.SPREAD, scenario_seed)
    evaluator = i56.Evaluator(problem, task["budget"], i56.make_target(task.get("reference")))
    scalar = Scalar(problem, evaluator, cht)
    dict(CMAwM=run_cmawm, DE=run_de, Random=run_random)[method](problem, scalar, task["seed"])
    complete = evaluator.calls == task["budget"]
    first = evaluator.first_target
    return dict(task=task, calls=evaluator.calls, complete=complete, errors=evaluator.errors,
                ok=complete and evaluator.errors == 0, T=(first / task["budget"]) if first is not None else 1.0,
                first_target=first, first_feasible=evaluator.first_feasible,
                best_feasible=evaluator.best_feasible if math.isfinite(evaluator.best_feasible) else None,
                min_violation=evaluator.min_violation, failures=evaluator.failures,
                sequence=evaluator.sequence.hexdigest())


def tasks():
    refs = i56.references("test_ref.json")
    valid, _ = i56.instances("test")
    out = []
    for n, R, j, sc in valid:
        for s in SEEDS:
            for method, cht in CONFIGS:
                out.append(dict(network=n, resolution=R, scenario_index=j, scenario=list(sc), method=method, cht=cht,
                                seed=seed_of(n, R, j, s), budget=i56.BUDGET, reference=refs[f"{n}|{R}|{j}"]))
    return out


def stage_run(workers):
    from multiprocessing import Pool
    work = tasks()
    with Pool(workers, maxtasksperchild=1) as pool:
        records = list(pool.imap(run, work))
    for i, r in enumerate(records):
        if not r["ok"]:
            with Pool(1, maxtasksperchild=1) as pool:
                again = pool.apply(run, (work[i],))
            again["rerun"], again["first_attempt"] = True, r
            records[i] = again
    import hashlib
    ref_hash = hashlib.sha256(open(i56.path("test_ref.json.gz"), "rb").read()).hexdigest()
    i56.save("i57.json", dict(test_ref_sha256=ref_hash, records=records))


def analyse():
    data = i56.load("i57.json")
    units = {}
    for r in data["records"]:
        t = r["task"]
        units.setdefault((t["network"], t["resolution"], t["scenario_index"], t["seed"]), {})[(t["method"], t["cht"])] = r
    complete = {k: u for k, u in units.items() if len(u) == len(CONFIGS) and all(r["ok"] for r in u.values())}
    cells = {}
    for (n, R, j, seed), u in complete.items():
        cells.setdefault((n, R, j), []).append(u)
    results = {}
    for method, cht in CONTRASTS:
        def contrast(u, method=method, cht=cht):
            other = u[(method, cht)] if method != "Random" else u[("Random", "-")]
            return other["T"] - u[("GAdapt", cht)]["T"]
        b = i56.bootstrap(cells, contrast, seed=57)
        results[f"{method}-{cht}"] = dict(estimate=b["estimate"], ci=b["ci"])  # no p-values (protocol)
    per_config = {f"{m}|{c}": dict(mean_T=float(np.mean([u[(m, c)]["T"] for u in complete.values()])),
                                   feasible=float(np.mean([u[(m, c)]["best_feasible"] is not None for u in complete.values()])),
                                   attained=float(np.mean([u[(m, c)]["first_target"] is not None for u in complete.values()])))
                  for m, c in CONFIGS}
    out = dict(units=len(units), complete_units=len(complete), results=results, per_config=per_config)
    i56.save("i57_analysis.json", out)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        stage_run(int(sys.argv[2]) if len(sys.argv) > 2 else 8)
    elif len(sys.argv) > 1 and sys.argv[1] == "analyse":
        analyse()
    else:
        print(__doc__)
