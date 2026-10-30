"""I64-C: mechanism pilot (coefficient homogenisation under an orthogonal transformation). Spec: research/ITERATION64_C_SPEC.md.

  python research/i64/c_study.py preflight | run [workers] | analyse
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

import e_common as ec  # noqa: E402
import e_study as es  # noqa: E402
import r_study as rs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.environ.get("C_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_c"))
R_OUT = rs.OUT
B_SHORT, SEEDS = 1200, 30
BOOT, BOOT_SEED, ALPHA = 20000, 72, 0.05
PAIRS = rs.PAIRS
if es.B != 12000 or es.N_SEEDS != 100:
    raise SystemExit("STOP: E settings differ from the frozen values")


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
        raise SystemExit(f"EXISTS: {name} is reserved (create-once)")


def save(name, data):
    tmp = path(name) + ".tmp"
    with gzip.open(tmp, "wt") as fh:
        json.dump(data, fh)
    os.replace(tmp, path(name))


def load(name):
    with gzip.open(path(name), "rt") as fh:
        return json.load(fh)


def c_manifest():
    m = es.manifest("c")
    names = ("c_study.py", "c_report.py", "run_c.sh", "r_study.py", "e_study.py", "e_common.py", "e_algos.py")
    m["c_files"] = {f: sha(os.path.join(HERE, f)) for f in names}
    m["c_files"]["ITERATION64_C_SPEC.md"] = sha(os.path.join(os.path.dirname(HERE), "ITERATION64_C_SPEC.md"))
    m["c_settings"] = dict(b=B_SHORT, seeds=SEEDS, boot=BOOT, boot_seed=BOOT_SEED, alpha=ALPHA)
    fc = os.environ.get("C_FREEZE_COMMIT", "")
    if not fc:
        raise SystemExit("STOP: set C_FREEZE_COMMIT")
    for rel, key in [("research/i64/" + f, f) for f in names] + [("research/ITERATION64_C_SPEC.md", "ITERATION64_C_SPEC.md")]:
        blob = subprocess.run(["git", "-C", REPO, "show", f"{fc}:{rel}"], capture_output=True).stdout
        if hashlib.sha256(blob).hexdigest() != m["c_files"][key]:
            raise SystemExit(f"STOP: {rel} differs from the freezing commit")
    m["freeze_commit"] = fc
    if subprocess.run(["git", "-C", MBENCH, "status", "--porcelain"], capture_output=True, text=True).stdout.strip():
        raise SystemExit("STOP: mentor clone has uncommitted changes")
    return m


def same_build(a, b):
    keys = ("python", "pip_freeze", "gadapt_tree", "files", "protocol", "mentor_head", "settings", "c_files", "c_settings", "freeze_commit")
    return all(json.loads(json.dumps(a[k])) == json.loads(json.dumps(b[k])) for k in keys)


def inputs():
    d = {"r_analysis": sha(os.path.join(R_OUT, "analysis.json.gz")), "r_run": sha(os.path.join(R_OUT, "run.json.gz")),
         "r_check_repro": sha(os.path.join(R_OUT, "check_repro.json.gz"))}
    for n in ("normalizers", "freeze", "manifest_run"):
        d["e_" + n] = sha(os.path.join(es.OUT, n + ".json.gz"))
    for k, _, _ in PAIRS:
        d[f"e_run_part_{3 * k + 1}"] = sha(os.path.join(es.OUT, f"run_part_{3 * k + 1}.json.gz"))
    return d


def same_gadapt_build_as_R():
    """The GAdapt tree, interpreter, dependencies, mentor head and E code/settings must equal the ones that produced the archived R records."""
    rm = json.load(gzip.open(os.path.join(R_OUT, "check_repro.json.gz"), "rt"))["manifest"]
    cur = es.manifest("c")
    for k in ("python", "pip_freeze", "gadapt_tree", "files", "mentor_head", "settings", "protocol"):
        if json.loads(json.dumps(rm[k])) != json.loads(json.dumps(cur[k])):
            raise SystemExit(f"STOP: {k} differs from the build that produced the archived R records")


# ---- passive recording of the columnar-diversity coefficient vector (once per generation, after the library's own update) ----
_LOG = []
_CUR = [None]


class record_coefficients:
    """Context manager: wraps ColumnarDiversityDecisionVariableUpdater._update_decision_variables; restores the original method on exit."""

    def __enter__(self):
        from gadapt.operations.decision_variable_update import variable_columnar_diversity_decision_variable_updater as m
        self.cls = m.ColumnarDiversityDecisionVariableUpdater
        self.orig = self.cls._update_decision_variables
        orig = self.orig

        def rec(updater):
            orig(updater)
            dv = updater.population.options.decision_variables
            v = [float(g.columnar_diversity_coefficient) for g in dv]
            if len(v) != len(dv) or not all(math.isfinite(x) and 0.0 <= x <= 1.0 for x in v):
                raise RuntimeError("invalid columnar-diversity coefficient vector")
            _LOG.append((_CUR[0].n if _CUR[0] is not None else -1, v))
        self.cls._update_decision_variables = rec
        return self

    def __exit__(self, *exc):
        self.cls._update_decision_variables = self.orig


def run_short(k, variant, seed, record=True, trace=False):
    """GAdapt-M (E configuration, native domain) on the shift / rotm objective of pair k for B_SHORT calls; returns events and (if record) the coefficient log."""
    import e_algos
    _, name, d = PAIRS[k]
    lo_, hi_ = es.bounds_of(name)
    tf = es.cell_transform(3 * k + 1, "run")[0] if variant == "shift" else rs.rotm_transform(k)
    g = ec.make_objective(es.func_of(name), tf)
    tr = []
    if trace:
        g0 = g

        def g(y):  # noqa: F811  (full evaluation trace: every argument vector and value)
            v = g0(y)
            tr.append((tuple(float(a) for a in y), float(v)))
            return v
    budget = ec.Budget(g, B_SHORT)
    _LOG.clear()
    _CUR[0] = budget

    def go():
        try:
            e_algos.RUNNERS["gadapt"](budget, d, seed, lo=float(lo_), hi=float(hi_))
        except ec.BudgetReached:
            pass
    if record:
        with record_coefficients():
            go()
    else:
        go()
    out = dict(calls=budget.n, events=budget.events)
    if trace:
        out["trace_sha256"] = hashlib.sha256(json.dumps(tr).encode()).hexdigest()
    if record:
        out["log"] = [[c, list(v)] for c, v in _LOG]
    return out


def run_task(task):
    try:
        r = run_short(task["k"], task["variant"], task["seed"])
        return dict(task=task, ok=r["calls"] == B_SHORT, **r)
    except Exception:  # noqa: BLE001
        import traceback
        return dict(task=task, ok=False, error=traceback.format_exc()[-1500:])


def seed_for(k, variant, s):
    return es.seed_of("run", (100 if variant == "shift" else 130) + k, s)


def expected_tasks(k):
    return [dict(k=k, variant=v, seed=seed_for(k, v, s)) for v in ("shift", "rotm") for s in range(1, SEEDS + 1)]


def stage_preflight():
    """Passive-recording check on 3 benchmark pairs with non-confirmatory seeds: same call sequence with and without the recorder."""
    reserve("preflight")
    same_gadapt_build_as_R()
    res = []
    for k in (0, 6, 10):
        a = run_short(k, "shift", 987654 + k, record=False, trace=True)
        b = run_short(k, "shift", 987654 + k, record=True, trace=True)
        res.append(dict(k=k, identical=a["events"] == b["events"] and a["calls"] == b["calls"] and a["trace_sha256"] == b["trace_sha256"], n_log=len(b["log"]), dim_ok=all(len(v) == PAIRS[k][2] for _, v in b["log"])))
        print(res[-1], flush=True)
    if not all(r["identical"] and r["n_log"] > 1 and r["dim_ok"] for r in res):
        raise SystemExit("STOP: recording is not passive")
    save("preflight", dict(results=res, manifest=c_manifest(), inputs=inputs()))


def valid_log(rec, d):
    log = rec["log"]
    if len(log) < 2:
        return False
    prev = -1
    for c, v in log:
        if not (0 <= c <= B_SHORT) or c < prev or len(v) != d or not all(math.isfinite(x) and 0.0 <= x <= 1.0 for x in v):
            return False
        prev = c
    return True


def valid(records, k):
    exp = expected_tasks(k)
    got = {(r["task"]["variant"], r["task"]["seed"]): r for r in records}
    if len(records) != len(exp) or len(got) != len(exp):
        return False
    for t in exp:
        r = got.get((t["variant"], t["seed"]))
        if r is None or not r.get("ok") or r["task"] != t or r["calls"] != B_SHORT or not valid_log(r, PAIRS[k][2]):
            return False
    return True


def stage_run(workers):
    from multiprocessing import Pool
    if os.path.exists(path("run")):
        raise SystemExit("EXISTS: run exists (create-once)")
    pre = load("preflight")
    cur = c_manifest()
    if not same_build(pre["manifest"], cur) or pre["inputs"] != inputs():
        raise SystemExit("STOP: build or inputs differ from preflight")
    rs.env_check()
    same_gadapt_build_as_R()
    import fcntl
    lock = open(path("run") + ".flock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        raise SystemExit("STOP: another process holds the run lock")
    allrecs = []
    for k, name, d in PAIRS:
        part = f"run_part_{k}"
        if os.path.exists(path(part)):
            p = load(part)
            if not same_build(p["manifest"], pre["manifest"]) or not valid(p["records"], k):
                raise SystemExit(f"STOP: existing {part} invalid")
            allrecs.extend(p["records"])
            continue
        tasks = expected_tasks(k)
        with Pool(workers, maxtasksperchild=20) as pool:
            records = list(pool.imap(run_task, tasks, chunksize=2))
        for i, r in enumerate(records):
            if not r.get("ok"):
                with Pool(1, maxtasksperchild=1) as pool:
                    again = pool.apply(run_task, (tasks[i],))
                again["rerun"], again["first_attempt"] = True, r
                records[i] = again
        if not valid(records, k):
            raise SystemExit(f"STOP: invalid records for pair {k}")
        save(part, dict(records=records, manifest=pre["manifest"]))
        allrecs.extend(records)
        print("pair", k, name, d, "done", flush=True)
    save("run", dict(records=allrecs, inputs=inputs(), manifest=pre["manifest"]))


def run_H(rec):
    """Median over generations (the initial generation, where every coefficient is 1 by construction, is excluded) of CV_j = std_j(d)/mean_j(d)."""
    cvs = []
    for _, v in rec["log"][1:]:
        v = np.asarray(v, float)
        m = v.mean()
        if m > 0:
            cvs.append(float(v.std() / m))
    return float(np.median(cvs)) if cvs else math.nan


def spearman(x, y):
    from scipy.stats import spearmanr
    r = spearmanr(x, y).statistic
    return float(r)


def archived_seed_arrays(norm):
    """Seed-level archived quantities: A and the log10 normalised gap at call B_SHORT for E `shift` (gadapt) and R `rotm` (gadapt) records."""
    def area_of(events, nc):
        tot = 0.0
        for tau in es.TAUS:
            hit = next((c for c, f in events if max(0.0, (f - nc["f_star"]) / nc["s"]) <= tau), None)
            if hit is not None:
                tot += (es.B - hit + 1) / es.B
        return tot / len(es.TAUS)

    def gap_at(events, nc):
        best = math.inf
        for c, f in events:
            if c <= B_SHORT:
                best = f
        return math.log10(max(0.0, (best - nc["f_star"]) / nc["s"]) + 1e-12)
    r_recs = json.load(gzip.open(os.path.join(R_OUT, "run.json.gz"), "rt"))["records"]
    out = {}
    for k, name, d in PAIRS:
        nc = norm[f"{name}|{d}"]
        sh = sorted((r for r in es.load(f"run_part_{3 * k + 1}")["records"] if r["task"]["config"] == "gadapt"), key=lambda r: r["task"]["seed"])
        rm = sorted((r for r in r_recs if r["task"]["k"] == k and r["task"]["config"] == "gadapt"), key=lambda r: r["task"]["seed"])
        if len(sh) != 100 or len(rm) != 100 or not all(r["ok"] and r["calls"] == es.B for r in sh + rm):
            raise SystemExit(f"STOP: archived records invalid for pair {k}")
        out[k] = dict(A_shift=np.array([area_of(r["events"], nc) for r in sh]), A_rotm=np.array([area_of(r["events"], nc) for r in rm]),
                      G_shift=np.array([gap_at(r["events"], nc) for r in sh]), G_rotm=np.array([gap_at(r["events"], nc) for r in rm]))
    return out


def stage_analyse():
    reserve("analysis")
    from scipy.stats import binom
    pre = load("preflight")
    run = load("run")
    cur = c_manifest()
    same_gadapt_build_as_R()
    if not same_build(pre["manifest"], cur) or not same_build(run["manifest"], cur) or run["inputs"] != inputs() or pre["inputs"] != inputs():
        raise SystemExit("STOP: build or inputs changed")
    allk = [r["task"] for r in run["records"]]
    if len(allk) != 2 * SEEDS * len(PAIRS) or len({(t["k"], t["variant"], t["seed"]) for t in allk}) != len(allk):
        raise SystemExit("STOP: C records are not exactly the planned unique tasks")
    for k, _, _ in PAIRS:
        if not valid([r for r in run["records"] if r["task"]["k"] == k], k):
            raise SystemExit(f"STOP: invalid C records for pair {k}")
    norm = es.load("normalizers")
    arr = archived_seed_arrays(norm)
    H = {}
    for k, _, _ in PAIRS:
        for v in ("shift", "rotm"):
            recs = sorted((r for r in run["records"] if r["task"]["k"] == k and r["task"]["variant"] == v), key=lambda r: r["task"]["seed"])
            h = np.array([run_H(r) for r in recs])
            if len(h) != SEEDS or not np.all(np.isfinite(h)):
                raise SystemExit(f"STOP: invalid H for pair {k} {v}")
            H[(k, v)] = h
    funcs = []
    for _, n, _ in PAIRS:
        if n not in funcs:
            funcs.append(n)
    pairs_of = {n: [k for k, nn, _ in PAIRS if nn == n] for n in funcs}
    wf = {n: (1 / 9) / len(pairs_of[n]) for n in funcs}  # w_{f,d} = (1/9)/m_f

    def one_pair(k, idx):
        ish, irm, iA, iB = idx
        D = H[(k, "shift")][ish].mean() - H[(k, "rotm")][irm].mean()
        dA = arr[k]["A_shift"][iA].mean() - arr[k]["A_rotm"][iB].mean()
        E = arr[k]["G_rotm"][iB].mean() - arr[k]["G_shift"][iA].mean()  # positive: rotm is harder at call B_SHORT
        return D, dA, E

    def draw(rng):
        return rng.integers(0, SEEDS, SEEDS), rng.integers(0, SEEDS, SEEDS), rng.integers(0, 100, 100), rng.integers(0, 100, 100)

    def stats(plan, rng=None):
        # plan: list of (function name, [pair ids]) copies; idx per (copy, pair)
        D, dA, E, W = [], [], [], []
        for n in plan:
            for k in pairs_of[n]:
                d_, a_, e_ = one_pair(k, draw(rng) if rng is not None else (np.arange(SEEDS), np.arange(SEEDS), np.arange(100), np.arange(100)))
                D.append(d_); dA.append(a_); E.append(e_); W.append(wf[n])
        D, dA, E, W = map(np.array, (D, dA, E, W))
        wm = float(np.sum(W * D) / np.sum(W))
        rd = spearman(D, dA) if np.std(D) > 0 and np.std(dA) > 0 else math.nan
        re_ = spearman(E, dA) if np.std(E) > 0 and np.std(dA) > 0 else math.nan
        return D, dA, E, wm, rd, re_, rd - re_
    D0, dA0, E0, wm0, rd0, re0, dd0 = stats(funcs)
    nz = int(np.sum(D0 != 0))
    pos = int(np.sum(D0 > 0))
    p_binom = float(binom.sf(pos - 1, nz, 0.5)) if nz else 1.0
    rng = np.random.default_rng(BOOT_SEED)
    boots = []
    for _ in range(BOOT):
        plan = [funcs[i] for i in rng.integers(0, len(funcs), len(funcs))]  # cluster bootstrap over the nine functions
        _, _, _, wm, rd, re_, dd = stats(plan, rng)
        boots.append((wm, rd, re_, dd))
    boots = np.array(boots)
    ok = np.all(np.isfinite(boots), axis=1)
    nv = int(ok.sum())
    blocked = nv < 0.9 * BOOT or not np.all(np.isfinite([wm0, rd0, re0]))
    # descriptive leave-one-function-out Spearman(D, dA)
    lofo = {}
    for n in funcs:
        keep = [i for i, (_, nn, _) in enumerate(PAIRS) if nn != n]
        lofo[n] = spearman(D0[keep], dA0[keep]) if np.std(D0[keep]) > 0 else math.nan
    out = dict(blocked=blocked, n_pairs=len(PAIRS), pairs=[f"{n}|{d}" for _, n, d in PAIRS], delta_k=D0.tolist(), dA_k=dA0.tolist(), E_k=E0.tolist(),
               wmean_delta=wm0, spearman_delta_dA=rd0, spearman_E_dA=re0, diff=dd0, positive_pairs=pos, nonzero_pairs=nz, p_binomial=p_binom,
               lofo_spearman=lofo, valid_boot=nv, boot=BOOT, boot_seed=BOOT_SEED, alpha=ALPHA, inputs=run["inputs"], freeze_commit=pre["manifest"]["freeze_commit"])
    if not blocked:
        bb = boots[ok]
        a3 = ALPHA / 3
        q = lambda col, p: float(np.quantile(bb[:, col], p))
        lo_wm, hi_wm, lo_rd, hi_rd, lo_dd, hi_dd = q(0, a3), q(0, 1 - a3), q(1, a3), q(1, 1 - a3), q(3, a3), q(3, 1 - a3)
        out.update(lo_wmean=lo_wm, hi_wmean=hi_wm, lo_rd=lo_rd, hi_rd=hi_rd, lo_dd=lo_dd, hi_dd=hi_dd)
        out["H64c1"] = "supported" if (lo_wm > 0 and pos >= 16) else ("below_zero" if hi_wm < 0 else "undecided")
        out["H64c2"] = "supported" if (rd0 >= 0.60 and lo_rd > 0.30) else ("below_threshold" if hi_rd < 0.30 else "undecided")
        out["H64c3"] = "supported" if lo_dd > 0 else ("opposite" if hi_dd < 0 else "undecided")
        out["signature_supported"] = bool(out["H64c1"] == "supported" and out["H64c2"] == "supported")
        out["stronger_marginal_than_baseline"] = bool(out["H64c3"] == "supported")
    save("analysis", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("delta_k", "dA_k", "E_k", "pairs", "inputs")}, indent=1))


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    wk = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    {"preflight": stage_preflight, "run": lambda: stage_run(wk), "analyse": stage_analyse}.get(st, lambda: print(__doc__))()
