"""I64-R: rotation isolation (rotm = rot's Q with shift's o). Spec: research/ITERATION64_R_SPEC.md. Frozen E files are not modified.

  python research/i64/r_study.py check_repro | run [workers] | analyse
"""
import gzip
import hashlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MBENCH = os.environ["MBENCH"]
for p in (HERE, MBENCH, os.path.dirname(os.path.dirname(HERE))):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np  # noqa: E402

import e_algos  # noqa: E402
import e_common as ec  # noqa: E402
import e_study as es  # noqa: E402

OUT = os.environ.get("R_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_r"))
B = es.B
N_SEEDS = es.N_SEEDS
if N_SEEDS != 100 or es.B != 12000:
    raise SystemExit("STOP: E_SEEDS / budget differ from the frozen values (100 seeds, B = 12000)")
CONFIGS = ("gadapt", "ipop")
PAIRS = []  # (k, name, d)
for _n, *_rest in es.FUNCS:
    for _d in _rest[-1]:
        PAIRS.append((len(PAIRS), _n, _d))
assert len(PAIRS) == 21 and all(es.CELLS[3 * k + 1][:2] == (n, d) and es.CELLS[3 * k + 2][:2] == (n, d) for k, n, d in PAIRS)
BOUND_SHIFT, BOUND_THR = 0.03, 0.05
BOOT, BOOT_SEED, ALPHA = 20000, 70, 0.05


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name + ".json.gz")


def save(name, data):
    tmp = path(name) + ".tmp"
    with gzip.open(tmp, "wt") as fh:
        json.dump(data, fh)
    os.replace(tmp, path(name))


def load(name):
    with gzip.open(path(name), "rt") as fh:
        return json.load(fh)


def rotm_transform(k):
    tf_s = es.cell_transform(3 * k + 1, "run")[0]
    tf_r = es.cell_transform(3 * k + 2, "run")[0]
    Q, o, xs, w, lo, shift = tf_r[0], tf_s[1], tf_s[2], tf_s[3], tf_s[4], True
    assert np.array_equal(xs, tf_r[2]) and w == tf_r[3] and lo == tf_r[4]
    return (Q, o, xs, w, lo, shift)


def run_task(task):
    try:
        k = task["k"]
        _, name, d = PAIRS[k]
        lo_, hi_ = es.bounds_of(name)
        g = ec.make_objective(es.func_of(name), rotm_transform(k))
        budget = ec.Budget(g, B)
        kw = dict(task.get("params") or {})
        if task["config"] in es.NATIVE:
            kw["lo"], kw["hi"] = float(lo_), float(hi_)
        t0 = time.time()
        try:
            e_algos.RUNNERS[task["config"]](budget, d, task["seed"], **kw)
            return dict(task=task, ok=False, error="runner returned without exhausting the budget", calls=budget.n)
        except ec.BudgetReached:
            pass
        return dict(task=task, ok=budget.n == B, calls=budget.n, best_f=budget.best, best_y=budget.best_y, events=budget.events,
                    seconds=time.time() - t0)
    except Exception:  # noqa: BLE001
        import traceback
        return dict(task=task, ok=False, error=traceback.format_exc()[-1500:], calls=None)


def r_manifest():
    """E build manifest (python, pip freeze, gadapt tree, mentor head) + hashes of the R spec/code; the freezing commit is recorded by `git rev-parse HEAD`."""
    import subprocess
    m = es.manifest("r")
    m["r_files"] = {"r_study.py": sha(os.path.join(HERE, "r_study.py")), "ITERATION64_R_SPEC.md": sha(os.path.join(os.path.dirname(HERE), "ITERATION64_R_SPEC.md"))}
    m["r_settings"] = dict(configs=CONFIGS, pairs=PAIRS, seeds=N_SEEDS, boot=BOOT, boot_seed=BOOT_SEED, alpha=ALPHA, bounds=[BOUND_SHIFT, BOUND_THR])
    m["git_head"] = subprocess.run(["git", "-C", os.path.dirname(os.path.dirname(HERE)), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return m


def same_build(a, b):
    keys = ("python", "pip_freeze", "gadapt_tree", "files", "protocol", "mentor_head", "settings", "r_files", "r_settings")
    return all(json.loads(json.dumps(a[k])) == json.loads(json.dumps(b[k])) for k in keys)


def e_inputs():
    """SHA-256 of every archived E input the analysis reads (recorded in check_repro BEFORE the run; re-verified later)."""
    d = {f"run_part_{ci}": sha(os.path.join(es.OUT, f"run_part_{ci}.json.gz")) for ci in range(len(es.CELLS))}
    for n in ("run", "freeze", "normalizers", "manifest_run"):
        d[n] = sha(os.path.join(es.OUT, n + ".json.gz"))
    return d


def e_parts():
    return {f"run_part_{ci}": sha(os.path.join(es.OUT, f"run_part_{ci}.json.gz")) for ci in range(len(es.CELLS))}


def env_check():
    em, cur = es.load("manifest_run"), es.manifest("r")
    if json.loads(json.dumps(em["pip_freeze"])) != json.loads(json.dumps(cur["pip_freeze"])) or em["python"] != cur["python"]:
        raise SystemExit("STOP: environment differs from the one that produced the archived E records")
    return cur


def e_record(cell, config, seed_index):
    part = es.load(f"run_part_{cell}")["records"]
    return next(r for r in part if r["task"]["config"] == config and r["task"]["seed"] == es.seed_of("run", cell, seed_index))


def stage_check_repro():
    if os.path.exists(path("check_repro")):
        raise SystemExit("EXISTS: check_repro exists (create-once)")
    env_check()
    params = es.load("freeze")["params"]
    res = []
    # cells 1 and 2 are sphere d=2 shift / rot; cell 40 and 41 are mid-list shift / rot (rastrigin or similar, see CELLS)
    for cell, cfg in ((1, "gadapt"), (2, "gadapt"), (2, "ipop"), (3 * 9 + 1, "gadapt"), (3 * 9 + 2, "ipop")):
        old = e_record(cell, cfg, 1)
        new = es.run_task(dict(config=cfg, params=params.get(cfg), cell=cell, seed=es.seed_of("run", cell, 1), purpose="run"))
        ok = bool(new.get("ok")) and all(json.dumps(new[x]) == json.dumps(old[x]) for x in ("calls", "best_f", "best_y", "events"))
        res.append(dict(cell=cell, cell_def=list(es.CELLS[cell]), config=cfg, old=old["best_f"], new=new.get("best_f"), identical=ok))
        print(res[-1], flush=True)
    if not all(r["identical"] for r in res):
        raise SystemExit("STOP: archived E records are not reproduced on the current tree")
    save("check_repro", dict(results=res, manifest=r_manifest(), e_inputs=e_inputs()))


def require_build(stage):
    cr = load("check_repro")
    cur = r_manifest()
    if not same_build(cr["manifest"], cur):
        raise SystemExit(f"STOP: build differs from the one that passed check_repro (stage {stage})")
    if cr["e_inputs"] != e_inputs():
        raise SystemExit(f"STOP: archived E inputs differ from the ones recorded in check_repro (stage {stage})")
    return cr


def expected_tasks(k, params):
    return [dict(config=c, params=params.get(c), k=k, seed=es.seed_of("run", 63 + k, s)) for s in range(1, N_SEEDS + 1) for c in CONFIGS]


def valid_records(records, k, params):
    exp = expected_tasks(k, params)
    got = {(r["task"]["config"], r["task"]["seed"]): r for r in records}
    if len(records) != len(exp) or len(got) != len(exp):
        return False
    for t in exp:
        r = got.get((t["config"], t["seed"]))
        if r is None or not r.get("ok") or r["calls"] != B or r["task"] != t:
            return False
        ev = r["events"]
        if not ev or ev[-1][0] > B or any(not (1 <= c <= B) for c, _ in ev) or any(ev[i][0] >= ev[i + 1][0] for i in range(len(ev) - 1)):
            return False
    return True


def stage_run(workers):
    if os.path.exists(path("run")):
        raise SystemExit("EXISTS: run exists (create-once)")
    from multiprocessing import Pool
    cr = require_build("run")
    env_check()
    params = es.load("freeze")["params"]
    allrecs = []
    for k, name, d in PAIRS:
        part = f"run_part_{k}"
        if os.path.exists(path(part)):
            p = load(part)
            if not same_build(p["manifest"], cr["manifest"]) or not valid_records(p["records"], k, params):
                raise SystemExit(f"STOP: existing {part} is not valid for this build")
            allrecs.extend(p["records"])
            continue
        tasks = expected_tasks(k, params)
        assert len({(t["k"], t["seed"], t["config"]) for t in tasks}) == len(tasks)
        with Pool(workers, maxtasksperchild=50) as pool:
            records = list(pool.imap(run_task, tasks, chunksize=4))
        for i, r in enumerate(records):
            if not r.get("ok"):
                with Pool(1, maxtasksperchild=1) as pool:
                    again = pool.apply(run_task, (tasks[i],))
                again["rerun"], again["first_attempt"] = True, r
                records[i] = again
        bad = [r for r in records if not r.get("ok")]
        if bad or not valid_records(records, k, params):
            raise SystemExit(f"STOP: {len(bad)} runs failed technically twice or the records are invalid: {bad[0].get('error') if bad else ''}")
        save(part, dict(records=records, manifest=cr["manifest"]))
        allrecs.extend(records)
        print("pair", k, name, d, "done", flush=True)
    save("run", dict(records=allrecs, e_inputs=e_inputs(), manifest=cr["manifest"]))


def gap_fn(nc):
    def gp(f):
        if not math.isfinite(f):
            return math.inf
        if f < nc["f_star"] - 1e-12 * nc["s"]:
            raise SystemExit("STOP: value below f*")
        return max(0.0, (f - nc["f_star"]) / nc["s"])
    return gp


def area_of(events, nc):
    gp = gap_fn(nc)
    total = 0.0
    for tau in es.TAUS:
        hit = next((c for c, f in events if gp(f) <= tau), None)
        if hit is not None:
            total += (B - hit + 1) / B
    return total / len(es.TAUS)


def stage_analyse():
    if os.path.exists(path("analysis")):
        raise SystemExit("EXISTS: analysis exists (create-once)")
    cr = require_build("analyse")
    run = load("run")
    if run["e_inputs"] != e_inputs() or not same_build(run["manifest"], cr["manifest"]):
        raise SystemExit("STOP: run does not match the verified build / E inputs")
    norm = es.load("normalizers")
    params = es.load("freeze")["params"]
    A = {}  # (k, variant, config) -> array over seeds (index s-1)
    for k, name, d in PAIRS:
        nc = norm[f"{name}|{d}"]
        for variant, cell in (("shift", 3 * k + 1), ("rot", 3 * k + 2)):
            part = es.load(f"run_part_{cell}")["records"]
            for cfg in CONFIGS:
                recs = {r["task"]["seed"]: r for r in part if r["task"]["config"] == cfg}
                seeds = [es.seed_of("run", cell, s) for s in range(1, N_SEEDS + 1)]
                if sorted(recs) != sorted(seeds) or not all(r["ok"] and r["calls"] == B for r in recs.values()):
                    raise SystemExit(f"STOP: archived E records invalid for {name}|{d} {variant} {cfg}")
                A[(k, variant, cfg)] = np.array([area_of(recs[s]["events"], nc) for s in seeds])
        recs_k = [r for r in run["records"] if r["task"]["k"] == k]
        if not valid_records(recs_k, k, params):
            raise SystemExit(f"STOP: invalid R records for pair {k}")
        for cfg in CONFIGS:
            recs = {r["task"]["seed"]: r for r in recs_k if r["task"]["config"] == cfg}
            A[(k, "rotm", cfg)] = np.array([area_of(recs[es.seed_of("run", 63 + k, s)]["events"], nc) for s in range(1, N_SEEDS + 1)])
    if not all(np.all(np.isfinite(v)) for v in A.values()):
        raise SystemExit("STOP: non-finite ECDF areas")
    ndims = {}
    for _, name, d in PAIRS:
        ndims[name] = ndims.get(name, 0) + 1
    wts = {k: (1 / 9) / ndims[name] for k, name, d in PAIRS}  # d=2 cells carry 5/9 of the total weight, d=7 and d=20 carry 2/9 each

    def agg(get):
        def f(variant, cfg):
            return sum(wts[k] * get(k, variant, cfg) for k, _, _ in PAIRS)
        return f

    def contrasts(a):
        c1 = a("rotm", "gadapt") - a("rot", "gadapt")
        c2 = a("shift", "gadapt") - a("rotm", "gadapt")
        c3 = a("shift", "ipop") - a("rotm", "ipop")
        return np.array([c1, c2, c3, c2 - c3])
    est = contrasts(agg(lambda k, v, c: A[(k, v, c)].mean()))
    rng = np.random.default_rng(BOOT_SEED)
    boots = np.empty((BOOT, 4))
    for b in range(BOOT):
        means = {}
        for k, _, _ in PAIRS:
            for v in ("shift", "rot", "rotm"):
                idx = rng.integers(0, N_SEEDS, N_SEEDS)  # one resample per (pair, variant), shared by both configurations (same seeds = same task)
                for c in CONFIGS:
                    means[(k, v, c)] = A[(k, v, c)][idx].mean()
        boots[b] = contrasts(agg(lambda k, v, c: means[(k, v, c)]))
    se = boots.std(axis=0, ddof=1)
    blocked = bool(np.any(~np.isfinite(se)) or np.any(se <= 0))
    if blocked:
        out = dict(blocked=True, estimates=est.tolist(), se=se.tolist())
        save("analysis", out)
        raise SystemExit("BLOCKED: degenerate bootstrap standard error")
    tmax = np.quantile(np.max(np.abs(boots - est) / se, axis=1), 1 - ALPHA)
    lo, hi = est - tmax * se, est + tmax * se

    def thr_verdict(l, h, thr):
        return "supported" if l > thr else ("below_threshold" if h < thr else "undecided")
    h1 = "supported" if (lo[0] >= -BOUND_SHIFT and hi[0] <= BOUND_SHIFT) else ("outside_bound" if (lo[0] > BOUND_SHIFT or hi[0] < -BOUND_SHIFT) else "undecided")
    h2 = thr_verdict(lo[1], hi[1], BOUND_THR)
    h3 = thr_verdict(lo[3], hi[3], BOUND_THR)
    if h3 == "supported" and h2 != "supported":
        h3 = "undecided"  # H64r3 requires H64r2 (spec section 7)
    out = dict(blocked=False, estimates=est.tolist(), lower=lo.tolist(), upper=hi.tolist(), tstar=float(tmax), se=se.tolist(),
               names=["c1 A_G(rotm)-A_G(rot)", "c2 A_G(shift)-A_G(rotm)", "c3 A_I(shift)-A_I(rotm)", "c4 c2-c3"],
               H64r1=h1, H64r2=h2, H64r3=h3,
               aggregates={f"{v}|{c}": float(agg(lambda k, vv, cc: A[(k, vv, cc)].mean())(v, c)) for v in ("shift", "rot", "rotm") for c in CONFIGS},
               per_pair={f"{PAIRS[k][1]}|{PAIRS[k][2]}": {f"{v}|{c}": float(A[(k, v, c)].mean()) for v in ("shift", "rot", "rotm") for c in CONFIGS} for k, _, _ in PAIRS},
               e_inputs=run["e_inputs"], boot=BOOT, boot_seed=BOOT_SEED, alpha=ALPHA, git_head=r_manifest()["git_head"])
    save("analysis", out)
    print(json.dumps({k: out[k] for k in ("estimates", "lower", "upper", "H64r1", "H64r2", "H64r3", "aggregates")}, indent=1))


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    wk = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    {"check_repro": stage_check_repro, "run": lambda: stage_run(wk), "analyse": stage_analyse}.get(st, lambda: print(__doc__))()
