"""I64-A: ablation of the GAdapt->CMA hybrid (random first phase). Spec: research/ITERATION64_A_SPEC.md. Frozen E/E3 files are not modified.

  python research/i64/a_study.py check_repro | run [workers] | analyse
"""
import gzip
import hashlib
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MBENCH = os.environ["MBENCH"]
for p in (HERE, MBENCH, os.path.dirname(os.path.dirname(HERE))):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np  # noqa: E402

import a_algo  # noqa: E402
import e3_algo  # noqa: E402
import e_algos  # noqa: E402
import e_study as es  # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.environ.get("A_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_a"))
E3_OUT = os.environ.get("A_E3_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_e3"))
B, N_SEEDS = es.B, es.N_SEEDS
if B != 12000 or N_SEEDS != 100:
    raise SystemExit("STOP: E_SEEDS / budget differ from the frozen values")
FRAC = 0.3
THR, BOOT, BOOT_SEED, ALPHA = 0.02, 20000, 71, 0.05


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name + ".json.gz")


def reserve(name):
    if os.path.exists(path(name)):
        raise SystemExit(f"EXISTS: {name} exists (create-once)")
    try:
        os.close(os.open(path(name) + ".lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        raise SystemExit(f"EXISTS: {name} is reserved or exists (create-once)")


_LOCKS = []


def process_lock(name):
    """Held for the life of the process (released by the OS on a crash, so `run` stays restartable) and race-free between processes."""
    import fcntl
    fh = open(path(name) + ".flock", "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        raise SystemExit(f"STOP: another process holds the {name} lock")
    _LOCKS.append(fh)


def save(name, data):
    tmp = path(name) + ".tmp"
    with gzip.open(tmp, "wt") as fh:
        json.dump(data, fh)
    os.replace(tmp, path(name))


def load(name):
    with gzip.open(path(name), "rt") as fh:
        return json.load(fh)


def e3_load(name):
    with gzip.open(os.path.join(E3_OUT, name + ".json.gz"), "rt") as fh:
        return json.load(fh)


def hyb_rand_runner(g, d, seed):
    a_algo.rand_cma_runner(g, d, seed, frac=FRAC, sigma0=0.05)


def run_task(task):
    e_algos.RUNNERS["hyb_rand"] = hyb_rand_runner  # also in spawned workers
    es.NATIVE = tuple(n for n in es.NATIVE if n != "hyb_rand")  # unit cube, no native domain
    return es.run_task(task)


def a_manifest():
    m = es.manifest("a")
    if e3_load("freeze")["frac"] != FRAC:
        raise SystemExit("STOP: E3 frac differs from the frozen 0.3")
    m["a_files"] = {f: sha(os.path.join(HERE, f)) for f in ("a_study.py", "a_algo.py", "e3_algo.py", "e3_study.py", "e_study.py", "e_common.py", "e_algos.py")}
    m["a_files"]["ITERATION64_A_SPEC.md"] = sha(os.path.join(os.path.dirname(HERE), "ITERATION64_A_SPEC.md"))
    m["a_settings"] = dict(thr=THR, boot=BOOT, boot_seed=BOOT_SEED, alpha=ALPHA, seeds=N_SEEDS, frac=FRAC)
    fc = os.environ.get("A_FREEZE_COMMIT", "")
    if not fc:
        raise SystemExit("STOP: set A_FREEZE_COMMIT to the commit that froze the A spec and code")
    for rel, key in [("research/i64/" + f, f) for f in ("a_study.py", "a_algo.py", "e3_algo.py", "e3_study.py", "e_study.py", "e_common.py", "e_algos.py")] + [("research/ITERATION64_A_SPEC.md", "ITERATION64_A_SPEC.md")]:
        blob = subprocess.run(["git", "-C", REPO, "show", f"{fc}:{rel}"], capture_output=True).stdout
        if hashlib.sha256(blob).hexdigest() != m["a_files"][key]:
            raise SystemExit(f"STOP: {rel} differs from the freezing commit {fc}")
    m["freeze_commit"] = fc
    if subprocess.run(["git", "-C", MBENCH, "status", "--porcelain"], capture_output=True, text=True).stdout.strip():
        raise SystemExit("STOP: mentor clone has uncommitted changes")
    return m


def same_build(a, b):
    keys = ("python", "pip_freeze", "gadapt_tree", "files", "protocol", "mentor_head", "settings", "a_files", "a_settings", "freeze_commit")
    return all(json.loads(json.dumps(a[k])) == json.loads(json.dumps(b[k])) for k in keys)


def inputs():
    d = {n: sha(os.path.join(E3_OUT, n + ".json.gz")) for n in ("run", "freeze")}
    d["normalizers"] = sha(os.path.join(es.OUT, "normalizers.json.gz"))
    d["manifest_run"] = sha(os.path.join(es.OUT, "manifest_run.json.gz"))
    return d


def env_check():
    em, cur = es.load("manifest_run"), es.manifest("a")
    if json.loads(json.dumps(em["pip_freeze"])) != json.loads(json.dumps(cur["pip_freeze"])) or em["python"] != cur["python"]:
        raise SystemExit("STOP: environment differs from the one that produced the archived records")


def preflight_synthetic():
    """Non-confirmatory preflight of the new random-phase runner on a synthetic objective (no archived or confirmatory cell is used)."""
    import e_common as ec
    runs = []
    for _ in range(2):
        ys = []

        def g(y):
            ys.append(np.array(y, float))
            return float(np.sum((np.asarray(y) - 0.3) ** 2))
        b = ec.Budget(g, B)
        try:
            a_algo.rand_cma_runner(b, 4, 12345, frac=FRAC, sigma0=0.05)
        except ec.BudgetReached:
            pass
        runs.append((b.n, b.events, ys))
    (n1, e1, y1), (n2, e2, y2) = runs
    rng = np.random.default_rng([12345, 5])
    n_rand = int(FRAC * B)
    ok = n1 == B == n2 and e1 == e2 and all(np.array_equal(a, b_) for a, b_ in zip(y1, y2))
    ok = ok and all(np.array_equal(y1[i], rng.uniform(0.0, 1.0, 4)) for i in range(n_rand))
    best = min(range(n_rand), key=lambda i: float(np.sum((y1[i] - 0.3) ** 2)))
    ok = ok and float(np.max(np.abs(y1[n_rand] - y1[best]))) < 0.5  # first CMA point lies near the best random point (sigma0 = 0.05)
    if not ok:
        raise SystemExit("STOP: synthetic preflight of the random-phase runner failed")
    return dict(calls=n1, random_calls=n_rand)


def stage_check_repro():
    reserve("check_repro")
    env_check()
    pre = preflight_synthetic()
    e3 = {(r["task"]["cell"], r["task"]["seed"]): r for r in e3_load("run")["records"]}
    res = []
    for cell in (2, 29, 28):
        old = e3[(cell, es.seed_of("run", cell, 1))]
        # re-run the E3 hybrid itself (not the ablation) on the current tree
        import e3_study
        new = e3_study.run_task2(dict(config="gadapt_hyb", params=None, cell=cell, seed=es.seed_of("run", cell, 1), purpose="run"))
        ok = bool(new.get("ok")) and all(json.dumps(new[x]) == json.dumps(old[x]) for x in ("calls", "best_f", "best_y", "events"))
        res.append(dict(cell=cell, cell_def=list(es.CELLS[cell]), old=old["best_f"], new=new.get("best_f"), identical=ok))
        print(res[-1], flush=True)
    if not all(r["identical"] for r in res):
        raise SystemExit("STOP: archived E3 hybrid records are not reproduced on the current tree")
    save("check_repro", dict(results=res, preflight=pre, manifest=a_manifest(), inputs=inputs()))


def require_build(stage):
    cr = load("check_repro")
    if not same_build(cr["manifest"], a_manifest()) or cr["inputs"] != inputs():
        raise SystemExit(f"STOP: build or archived inputs differ from check_repro (stage {stage})")
    return cr


def expected_tasks(ci):
    return [dict(config="hyb_rand", params=None, cell=ci, seed=es.seed_of("run", ci, s), purpose="run") for s in range(1, N_SEEDS + 1)]


def valid_records(records, ci):
    exp = expected_tasks(ci)
    got = {r["task"]["seed"]: r for r in records}
    if len(records) != len(exp) or len(got) != len(exp):
        return False
    for t in exp:
        r = got.get(t["seed"])
        if r is None or not r.get("ok") or r["calls"] != B or r["task"] != t:
            return False
        ev = r["events"]
        if not ev or any(not (1 <= c <= B) for c, _ in ev) or any(ev[i][0] >= ev[i + 1][0] for i in range(len(ev) - 1)):
            return False
    return True


def stage_run(workers):
    from multiprocessing import Pool
    if os.path.exists(path("run")):
        raise SystemExit("EXISTS: run exists (create-once)")
    process_lock("run")
    cr = require_build("run")
    env_check()
    allrecs = []
    for ci in range(len(es.CELLS)):
        part = f"run_part_{ci}"
        if os.path.exists(path(part)):
            p = load(part)
            if not same_build(p["manifest"], cr["manifest"]) or p["inputs"] != cr["inputs"] or not valid_records(p["records"], ci):
                raise SystemExit(f"STOP: existing {part} is not valid for this build")
            allrecs.extend(p["records"])
            continue
        tasks = expected_tasks(ci)
        with Pool(workers, maxtasksperchild=1) as pool:
            records = list(pool.imap(run_task, tasks, chunksize=1))
        for i, r in enumerate(records):
            if not r.get("ok"):
                with Pool(1, maxtasksperchild=1) as pool:
                    again = pool.apply(run_task, (tasks[i],))
                again["rerun"], again["first_attempt"] = True, r
                records[i] = again
        bad = [r for r in records if not r.get("ok")]
        if bad or not valid_records(records, ci):
            raise SystemExit(f"STOP: {len(bad)} runs failed technically twice or records invalid: {bad[0].get('error') if bad else ''}")
        save(part, dict(records=records, manifest=cr["manifest"], inputs=cr["inputs"]))
        allrecs.extend(records)
        print("cell", ci, es.CELLS[ci], "done", flush=True)
    save("run", dict(records=allrecs, inputs=inputs(), manifest=cr["manifest"]))


def cvar(values, share=0.1):
    k = max(1, int(math.ceil(share * len(values))))
    return float(np.mean(sorted(values)[-k:]))


def stage_analyse():
    reserve("analysis")
    cr = require_build("analyse")
    run = load("run")
    if run["inputs"] != inputs() or not same_build(run["manifest"], cr["manifest"]):
        raise SystemExit("STOP: run does not match the verified build / inputs")
    norm = es.load("normalizers")
    n_cells = len(es.CELLS)
    raw = {}

    def add(r, label):
        ci, s = r["task"]["cell"], r["task"]["seed"]
        n = norm[f"{es.CELLS[ci][0]}|{es.CELLS[ci][1]}"]

        def gp(f):
            if not math.isfinite(f):
                return math.inf
            if f < n["f_star"] - 1e-12 * n["s"]:
                raise SystemExit(f"STOP: value below f* in cell {ci}")
            return max(0.0, (f - n["f_star"]) / n["s"])
        g = gp(r["best_f"])
        area = 0.0
        for tau in es.TAUS:
            hit = next((c for c, f in r["events"] if gp(f) <= tau), None)
            if hit is not None:
                area += (B - hit + 1) / B
        raw.setdefault((ci, label), {})[s] = (area / len(es.TAUS), 1.0 if math.isinf(g) else g / (1 + g), g)
    h_recs = e3_load("run")["records"]
    if len(h_recs) != n_cells * N_SEEDS or len({(r["task"]["cell"], r["task"]["seed"]) for r in h_recs}) != len(h_recs):
        raise SystemExit("STOP: archived E3 records are not exactly 63 x 100 unique tasks")
    for ci in range(n_cells):
        exp = {es.seed_of("run", ci, s) for s in range(1, N_SEEDS + 1)}
        mine = [r for r in h_recs if r["task"]["cell"] == ci]
        if {r["task"]["seed"] for r in mine} != exp or any(r["task"]["config"] != "gadapt_hyb" or r["task"]["purpose"] != "run" or not r["ok"] or r["calls"] != B for r in mine):
            raise SystemExit(f"STOP: archived E3 records invalid for cell {ci}")
        if not valid_records([r for r in run["records"] if r["task"]["cell"] == ci], ci):
            raise SystemExit(f"STOP: invalid ablation records for cell {ci}")
    for r in h_recs:
        add(r, "H")
    for r in run["records"]:
        add(r, "R")
    arr = {}
    for k, v in raw.items():
        assert sorted(v) == [es.seed_of("run", k[0], s) for s in range(1, N_SEEDS + 1)], k
        arr[k] = np.array([v[s] for s in sorted(v)])
    w_all = {}
    for ci, (name, d, v) in enumerate(es.CELLS):
        dims = next(len(dd) for n_, _, _, _, dd in es.FUNCS if n_ == name)
        w_all[ci] = (1 / 9) / dims / len(es.VARIANTS)
    rot = [ci for ci in range(n_cells) if es.CELLS[ci][2] == "rot"]
    nonrot = [ci for ci in range(n_cells) if es.CELLS[ci][2] != "rot"]

    def wsum(cells, fn):
        tot = sum(w_all[ci] for ci in cells)
        return sum(w_all[ci] * fn(ci) for ci in cells) / tot

    def stats(idx):
        A = lambda c, ci: arr[(ci, c)][idx[ci], 0].mean()
        CV = lambda c, ci: cvar(list(arr[(ci, c)][idx[ci], 1]))
        return np.array([wsum(rot, lambda ci: A("H", ci) - A("R", ci)), wsum(nonrot, lambda ci: A("H", ci) - A("R", ci)),
                         wsum(rot, lambda ci: CV("R", ci) - CV("H", ci)), wsum(nonrot, lambda ci: CV("R", ci) - CV("H", ci))])
    names = ["c1 dA_rot(H-R)", "c2 dA_nonrot(H-R)", "c3 CVaR_rot(R)-CVaR_rot(H)", "c4 CVaR_nonrot(R)-CVaR_nonrot(H)"]
    point = stats({ci: np.arange(N_SEEDS) for ci in range(n_cells)})
    rng = np.random.default_rng(BOOT_SEED)
    boots = np.array([stats({ci: rng.integers(0, N_SEEDS, N_SEEDS) for ci in range(n_cells)}) for _ in range(BOOT)])  # one index per cell, shared by H and R (same seed = same task)
    finite = bool(np.all(np.isfinite(point)) and np.all(np.isfinite(boots)) and all(np.all(np.isfinite(v[:, 2])) for v in arr.values()))
    se = boots.std(axis=0, ddof=1) if finite else np.full(4, np.nan)
    blocked = (not finite) or bool(np.any(se <= 0))
    if blocked:
        out = dict(blocked=True, names=names, estimates=point.tolist(), se=se.tolist(), boot=BOOT, boot_seed=BOOT_SEED, alpha=ALPHA, inputs=run["inputs"],
                   freeze_commit=cr["manifest"]["freeze_commit"], H64a1="blocked", H64a2="blocked", contribution_supported=None)
        save("analysis", out)
        raise SystemExit("BLOCKED: non-finite values or degenerate standard error")
    t = float(np.quantile(np.max(np.abs(boots - point) / se, axis=1), 1 - ALPHA))
    lo, hi = point - t * se, point + t * se

    def verdict(l, h):
        return "supported" if l > THR else ("below_threshold" if h < THR else "undecided")
    h1, h2 = verdict(lo[0], hi[0]), verdict(lo[1], hi[1])
    agg = {}
    for var, cells in (("orig", [c for c in range(n_cells) if es.CELLS[c][2] == "orig"]), ("shift", [c for c in range(n_cells) if es.CELLS[c][2] == "shift"]), ("rot", rot)):
        agg[var] = {c: dict(A=wsum(cells, lambda ci: arr[(ci, c)][:, 0].mean()), cvar90=wsum(cells, lambda ci: cvar(list(arr[(ci, c)][:, 1]))),
                            median_gap=wsum(cells, lambda ci: float(np.median(arr[(ci, c)][:, 2])))) for c in ("H", "R")}
    out = dict(blocked=False, tstar=t, alpha=ALPHA, boot=BOOT, boot_seed=BOOT_SEED, names=names, estimates=point.tolist(), lower=lo.tolist(), upper=hi.tolist(),
               H64a1=h1, H64a2=h2, contribution_supported=bool(h1 == "supported" and h2 == "supported"), aggregate_by_variant=agg,
               inputs=run["inputs"], freeze_commit=cr["manifest"]["freeze_commit"])
    save("analysis", out)
    print(json.dumps({k: out[k] for k in ("estimates", "lower", "upper", "H64a1", "H64a2", "contribution_supported", "aggregate_by_variant")}, indent=1))


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    wk = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    {"check_repro": stage_check_repro, "run": lambda: stage_run(wk), "analyse": stage_analyse}.get(st, lambda: print(__doc__))()
