"""I64 stage E (and R-compatible): 9 configurations x 63 cells (21 functions/dims x {orig, shift, rot}) under an exact 12,000-call budget.
Protocol: research/ITERATION64_PROTOCOL.md section 2-4 (estimands, weights, simultaneous bootstrap). Stages (each create-once, own process):

  python research/i64/e_study.py normalizers | dev | freeze | run [workers] | analyse
Environment: the `eenv` (mentor requirements + cma); GAdapt from the repository library (the opt-in preset exists only there);
MBENCH = mentor clone (PyGAD operators, functions).
"""
import gzip
import hashlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MBENCH = os.environ["MBENCH"]
OUT = os.environ.get("E_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_e"))
for p in (HERE, MBENCH, REPO):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np  # noqa: E402

import e_algos  # noqa: E402
import e_common as ec  # noqa: E402
from research_experiments.functions.ackley import ackley_func  # noqa: E402
from research_experiments.functions.beale import beale_func  # noqa: E402
from research_experiments.functions.booth import booth_func  # noqa: E402
from research_experiments.functions.griewank import griewank_func  # noqa: E402
from research_experiments.functions.himmelblau import himmelblau_func  # noqa: E402
from research_experiments.functions.rastrigin import rastrigin_func  # noqa: E402
from research_experiments.functions.rosenbrock import rosenbrock_func  # noqa: E402
from research_experiments.functions.sphere import sphere_func  # noqa: E402
from research_experiments.functions.styblinski_tang import styblinski_tang_func  # noqa: E402

B = int(os.environ.get("E_B", "12000"))  # 12,000 in the study; smaller only for pipeline rehearsal in a temp directory
TAUS = (1e-2, 1e-4, 1e-6)
FUNCS = [("sphere", sphere_func, -5.12, 5.12, (2, 7, 20)), ("rosenbrock", rosenbrock_func, 0.5, 1.5, (2, 7, 20)),
         ("rastrigin", rastrigin_func, -5.12, 5.12, (2, 7, 20)), ("ackley", ackley_func, -4, 4, (2, 7, 20)),
         ("griewank", griewank_func, -50, 50, (2, 7, 20)), ("styblinski_tang", styblinski_tang_func, -5, 5, (2, 7, 20)),
         ("beale", beale_func, -4.5, 4.5, (2,)), ("himmelblau", himmelblau_func, -6, 6, (2,)), ("booth", booth_func, -10, 10, (2,))]
VARIANTS = ("orig", "shift", "rot")
CELLS = [(n, d, v) for n, _, _, _, dims in FUNCS for d in dims for v in VARIANTS]  # 63 cells, c = 3 i + v
CONFIGS = ("gadapt", "gadapt_preset", "pygad_random", "pygad_adaptive", "de", "cma", "ipop", "bipop", "es11")
NATIVE = ('gadapt', 'gadapt_preset', 'pygad_random', 'pygad_adaptive', 'de')  # run on the mentor's native domain [lo, hi]
SEED_BASE = 64_000_000
PURPOSE = dict(dev=1, run=3)
N_SEEDS = int(os.environ.get("E_SEEDS", "100"))
DEV_SEEDS = int(os.environ.get("E_DEV_SEEDS", "5"))
# development candidates (listed in advance; chosen on development data only, then frozen)
CANDIDATES = {"cma": [dict(sigma0=s) for s in (0.2, 0.3, 0.5)], "ipop": [dict(sigma0=s) for s in (0.2, 0.3, 0.5)],
              "bipop": [dict(sigma0=s) for s in (0.2, 0.3, 0.5)],
              "es11": [dict(sigma0=s, up=u, stagnation=n) for s in (0.1, 0.3) for u in (1.2, 1.5) for n in (100, 1000)]}


def seed_of(purpose, cell_index, s):
    return SEED_BASE + 1_000_000 * PURPOSE[purpose] + 1000 * cell_index + s


def func_of(name):
    return next(f for n, f, *_ in FUNCS if n == name)


def bounds_of(name):
    return next((lo, hi) for n, _, lo, hi, _ in FUNCS if n == name)


def cell_transform(cell_index, purpose="run"):
    """Shift/rotation of a cell is generated once per cell (not per seed) from a public seed, shared by all configurations."""
    name, d, v = CELLS[cell_index]
    lo, hi = bounds_of(name)
    rng = np.random.default_rng([64, PURPOSE[purpose], cell_index])
    return ec.transform(name, d, lo, hi, v, rng)


def run_task(task):
    """task: dict(config, params, cell, seed, purpose). Returns the record (events of the best-so-far trace by call)."""
    try:
        name, d, v = CELLS[task["cell"]]
        lo_, hi_ = bounds_of(name)
        tf, info = cell_transform(task["cell"], task["purpose"])
        g = ec.make_objective(func_of(name), tf)
        budget = ec.Budget(g, B)
        kw = dict(task.get("params") or {})
        if task["config"].startswith("pygad"):
            kw["mentor_dir"] = MBENCH
        if task["config"] in NATIVE:
            kw["lo"], kw["hi"] = float(lo_), float(hi_)
        t0 = time.time()
        try:
            e_algos.RUNNERS[task["config"]](budget, d, task["seed"], **kw)
            return dict(task=task, ok=False, error="runner returned without exhausting the budget", calls=budget.n)
        except ec.BudgetReached:
            pass
        return dict(task=task, ok=budget.n == B, calls=budget.n, best_f=budget.best, best_y=budget.best_y, events=budget.events,
                    seconds=time.time() - t0)
    except Exception as exc:  # noqa: BLE001
        import traceback
        return dict(task=task, ok=False, error=traceback.format_exc()[-1500:], calls=None)


def execute(tasks, workers):
    from multiprocessing import Pool
    with Pool(workers, maxtasksperchild=50) as pool:
        records = list(pool.imap(run_task, tasks, chunksize=4))
    for i, r in enumerate(records):
        if not r.get("ok"):
            with Pool(1, maxtasksperchild=1) as pool:
                again = pool.apply(run_task, (tasks[i],))
            again["rerun"], again["first_attempt"] = True, r
            records[i] = again
    bad = [r for r in records if not r.get("ok")]
    if bad:
        raise SystemExit(f"STOP: {len(bad)} runs failed technically twice (first {bad[0]['task']}): {bad[0].get('error')}")
    return records


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name + ".json.gz")


def save(name, data):
    with gzip.open(path(name), "wt") as fh:
        json.dump(data, fh)


def load(name):
    with gzip.open(path(name), "rt") as fh:
        return json.load(fh)


def manifest(stage):
    import platform
    import subprocess
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.split()
    tree = {}
    for root, _, files in os.walk(os.path.join(REPO, "gadapt")):
        for f in sorted(files):
            if f.endswith(".py"):
                tree[os.path.relpath(os.path.join(root, f), REPO)] = sha(os.path.join(root, f))
    return dict(stage=stage, python=platform.python_version(), pip_freeze=freeze, gadapt_tree=tree,
                files={f: sha(os.path.join(HERE, f)) for f in ("e_study.py", "e_algos.py", "e_common.py")},
                protocol=sha(os.path.join(os.path.dirname(HERE), "ITERATION64_PROTOCOL.md")),
                mentor_head=subprocess.run(["git", "-C", MBENCH, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
                settings=dict(B=B, taus=TAUS, cells=CELLS, configs=CONFIGS, n_seeds=N_SEEDS, dev_seeds=DEV_SEEDS, candidates=CANDIDATES))


def require(stage, deps=()):
    if os.path.exists(path(stage)):
        raise SystemExit(f"EXISTS: {stage} exists (create-once)")
    m = manifest(stage)
    for d in deps:
        prev = load("manifest_" + d)
        if any(json.loads(json.dumps(prev[k])) != json.loads(json.dumps(m[k])) for k in ("python", "pip_freeze", "gadapt_tree", "files", "protocol", "mentor_head", "settings")):
            raise SystemExit(f"STOP: build differs from the one that produced {d}")
    return m


def normalised_gap(rec, norm):
    n = norm[f"{CELLS[rec['task']['cell']][0]}|{CELLS[rec['task']['cell']][1]}"]
    return lambda f: max(0.0, (f - n["f_star"]) / n["s"])


def ecdf_area(rec, norm):
    gp = normalised_gap(rec, norm)
    total = 0.0
    for tau in TAUS:
        hit = next((c for c, f in rec["events"] if gp(f) <= tau), None)
        if hit is not None:
            total += (B - hit + 1) / B
    return total / len(TAUS)


def stage_normalizers():
    m = require("normalizers")
    s0 = os.path.join(os.path.dirname(HERE), "results", "iteration64_s0", "normalizers.json.gz")
    with gzip.open(s0, "rt") as fh:
        norm = json.load(fh)
    # protocol: the same s_i for all algorithms/transformations, computed once (S0 normalizers, seed 64001) and archived
    save("normalizers", norm)
    save("manifest_normalizers", m)


def stage_dev(workers):
    m = require("dev", ("normalizers",))
    norm = load("normalizers")
    tasks = []
    for ci in range(len(CELLS)):
        if CELLS[ci][2] != "rot":
            continue
        for algo, cands in CANDIDATES.items():
            for k, params in enumerate(cands):
                for s in range(1, DEV_SEEDS + 1):
                    tasks.append(dict(config=algo, params=params, cand=k, cell=ci, seed=seed_of("dev", ci, s), purpose="dev"))
    records = execute(tasks, workers)
    score = {}
    for r in records:
        score.setdefault((r["task"]["config"], r["task"]["cand"]), []).append(ecdf_area(r, norm))
    chosen = {}
    for algo, cands in CANDIDATES.items():
        means = [float(np.mean(score[(algo, k)])) for k in range(len(cands))]
        chosen[algo] = dict(index=int(np.argmax(means)), params=cands[int(np.argmax(means))], means=means)
    save("dev", dict(chosen=chosen, records=[{k: v for k, v in r.items() if k != "events"} for r in records]))
    save("manifest_dev", m)


def stage_freeze():
    m = require("freeze", ("normalizers", "dev"))
    dev = load("dev")
    save("freeze", dict(params={a: v["params"] for a, v in dev["chosen"].items()}, manifest=m, dev_sha=sha(path("dev"))))
    save("manifest_freeze", m)


def stage_run(workers):
    """Resumable by cell: each cell's records are stored in run_part_<c>.json.gz (deterministic tasks); `run` is assembled at the end."""
    m = require("run", ("normalizers", "dev", "freeze"))
    fr = load("freeze")
    params = fr["params"]
    allrecs = []
    for ci in range(len(CELLS)):
        part = f"run_part_{ci}"
        if os.path.exists(path(part)):
            allrecs.extend(load(part)["records"])
            continue
        tasks = [dict(config=c, params=params.get(c), cell=ci, seed=seed_of("run", ci, s), purpose="run")
                 for s in range(1, N_SEEDS + 1) for c in CONFIGS]
        assert len({(t["cell"], t["seed"], t["config"]) for t in tasks}) == len(tasks)
        records = execute(tasks, workers)
        save(part, dict(records=records))
        allrecs.extend(records)
        print("cell", ci, CELLS[ci], "done", flush=True)
    save("run", dict(records=allrecs))
    save("manifest_run", m)


def cvar(values, share=0.1):
    k = max(1, int(math.ceil(share * len(values))))
    return float(np.mean(sorted(values)[-k:]))


def stage_analyse():
    require("analysis", ("normalizers", "dev", "freeze", "run"))
    norm, runs = load("normalizers"), load("run")["records"]
    n_funcs = 9
    w = {}
    for ci, (name, d, v) in enumerate(CELLS):
        dims = next(len(dd) for n, _, _, _, dd in FUNCS if n == name)
        w[ci] = (1 / n_funcs) / dims / len(VARIANTS)
    arr = {}
    for r in runs:
        gp = normalised_gap(r, norm)
        g = gp(r["best_f"])
        arr.setdefault((r["task"]["cell"], r["task"]["config"]), {})[r["task"]["seed"]] = (ecdf_area(r, norm), g / (1 + g), g)
    arr = {k: np.array([v[s] for s in sorted(v)]) for k, v in arr.items()}
    comps = [c for c in CONFIGS if c != "gadapt"]
    cells = list(w)

    def stats(idx):
        dA = [sum(w[ci] * (arr[(ci, "gadapt")][idx[ci], 0].mean() - arr[(ci, c)][idx[ci], 0].mean()) for ci in cells) for c in comps]
        dM = [sum(w[ci] * (np.median(arr[(ci, c)][idx[ci], 2]) - np.median(arr[(ci, "gadapt")][idx[ci], 2])) for ci in cells) for c in comps]
        return np.array(dA + dM)
    n = N_SEEDS
    point = stats({ci: np.arange(n) for ci in cells})
    rng = np.random.default_rng(64)
    R = int(os.environ.get("E_BOOT", "20000"))
    boots = np.array([stats({ci: rng.integers(0, n, n) for ci in cells}) for _ in range(R)])
    se = boots.std(axis=0, ddof=1)
    if np.any(se <= 0):
        raise SystemExit("STOP: zero bootstrap variance blocks confirmation (protocol 3)")
    alpha = 0.02
    tstar = float(np.quantile(np.max(np.abs(boots - point) / se, axis=1), 1 - alpha))
    lo, hi = point - tstar * se, point + tstar * se
    names = [f"dA|{c}" for c in comps] + [f"dM|{c}" for c in comps]
    contrasts = {nm: dict(estimate=float(p), lower=float(a), upper=float(b)) for nm, p, a, b in zip(names, point, lo, hi)}
    dA_lo = {c: contrasts[f"dA|{c}"]["lower"] for c in comps}
    dA_hi = {c: contrasts[f"dA|{c}"]["upper"] for c in comps}
    dM_lo = {c: contrasts[f"dM|{c}"]["lower"] for c in comps}
    dM_hi = {c: contrasts[f"dM|{c}"]["upper"] for c in comps}
    supported = all(dA_lo[c] > 0 for c in comps) or any(all(dA_lo[c] > 0 for c in comps if c != e) and dM_lo[e] > 0 for e in comps)
    opposite = len([c for c in comps if dA_hi[c] < 0]) >= 2 or any(dA_hi[c] < 0 and dM_hi[c] < 0 for c in comps)
    agg = {c: dict(A=float(sum(w[ci] * arr[(ci, c)][:, 0].mean() for ci in cells)),
                   cvar90=float(sum(w[ci] * cvar(list(arr[(ci, c)][:, 1])) for ci in cells)),
                   median_gap=float(sum(w[ci] * np.median(arr[(ci, c)][:, 2]) for ci in cells)),
                   reach=[float(sum(w[ci] * np.mean(arr[(ci, c)][:, 2] <= t) for ci in cells)) for t in TAUS]) for c in CONFIGS}
    # H64b: preset vs default GAdapt, four contrasts with their own simultaneous bootstrap (alpha 0.01, protocol 3):
    #   (1) 0.8*R0 - R_preset >= 0 (lower bound), (2..4) reach_preset - reach_default >= -0.05 for each target (lower bound)
    def b_stats(idx):
        def cv(c):
            return sum(w[ci] * cvar(list(arr[(ci, c)][idx[ci], 1])) for ci in cells)

        def rc(c, t):
            return sum(w[ci] * np.mean(arr[(ci, c)][idx[ci], 2] <= t) for ci in cells)
        return np.array([0.8 * cv("gadapt") - cv("gadapt_preset")] + [rc("gadapt_preset", t) - rc("gadapt", t) for t in TAUS])
    full = {ci: np.arange(n) for ci in cells}
    bp = b_stats(full)
    rng_b = np.random.default_rng(65)
    bb = np.array([b_stats({ci: rng_b.integers(0, n, n) for ci in cells}) for _ in range(R)])
    bse = bb.std(axis=0, ddof=1)
    if np.any(bse <= 0):
        raise SystemExit("STOP: zero bootstrap variance in H64b blocks confirmation (protocol 3)")
    bt = float(np.quantile(np.max(np.abs(bb - bp) / bse, axis=1), 1 - 0.01))
    blo = bp - bt * bse
    r0 = sum(w[ci] * cvar(list(arr[(ci, "gadapt")][:, 1])) for ci in cells)
    h64b = dict(R0=float(r0), Rpreset=float(sum(w[ci] * cvar(list(arr[(ci, "gadapt_preset")][:, 1])) for ci in cells)),
                point=[float(x) for x in bp], lower=[float(x) for x in blo], tstar=bt,
                supported=bool(r0 > 0 and blo[0] >= 0 and all(blo[1:] >= -0.05)))
    out = dict(verdict="supported" if supported else ("opposite" if opposite else "undecided"), tstar=tstar, alpha=alpha, bootstrap=R,
               contrasts=contrasts, aggregate=agg, h64b=h64b)
    save("analysis", out)
    print(json.dumps(out, indent=1)[:4000])


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    wk = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    {"normalizers": stage_normalizers, "dev": lambda: stage_dev(wk), "freeze": stage_freeze, "run": lambda: stage_run(wk),
     "analyse": stage_analyse}.get(st, lambda: print(__doc__))()
