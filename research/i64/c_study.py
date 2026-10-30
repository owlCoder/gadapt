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
    names = ("c_study.py", "r_study.py", "e_study.py", "e_common.py", "e_algos.py")
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
    return m


def same_build(a, b):
    keys = ("python", "pip_freeze", "gadapt_tree", "files", "protocol", "mentor_head", "settings", "c_files", "c_settings", "freeze_commit")
    return all(json.loads(json.dumps(a[k])) == json.loads(json.dumps(b[k])) for k in keys)


def inputs():
    return {"r_analysis": sha(os.path.join(R_OUT, "analysis.json.gz")), "normalizers": sha(os.path.join(es.OUT, "normalizers.json.gz")),
            "r_run": sha(os.path.join(R_OUT, "run.json.gz"))}


# ---- passive recording of the columnar-diversity coefficient vector ----
_LOG = []


def _install_recorder():
    from gadapt.operations.mutation.candidate_solution_mutation import variable_columnar_diversity_decision_variable_mutation_rate_determinator as m
    cls = m.VariableColumnarDiversityDecisionVariableMutationRateDeterminator
    if getattr(cls, "_c_recorded", False):
        return
    orig = cls._get_mutation_rate

    def rec(self, decision_variables):
        _LOG.append([float(g.columnar_diversity_coefficient) for g in decision_variables])
        return orig(self, decision_variables)
    cls._get_mutation_rate = rec
    cls._c_recorded = True


def run_short(k, variant, seed, record=True):
    """GAdapt-M (E configuration, native domain) on the shift / rotm objective of pair k for B_SHORT calls; returns (events, coefficient log)."""
    import e_algos
    _, name, d = PAIRS[k]
    lo_, hi_ = es.bounds_of(name)
    tf = es.cell_transform(3 * k + 1, "run")[0] if variant == "shift" else rs.rotm_transform(k)
    g = ec.make_objective(es.func_of(name), tf)
    budget = ec.Budget(g, B_SHORT)
    if record:
        _install_recorder()
    _LOG.clear()
    try:
        e_algos.RUNNERS["gadapt"](budget, d, seed, lo=float(lo_), hi=float(hi_))
    except ec.BudgetReached:
        pass
    return dict(calls=budget.n, events=budget.events, log=[list(v) for v in _LOG]) if record else dict(calls=budget.n, events=budget.events)


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
    """Passive-recording check on 3 synthetic pairs (non-confirmatory): same call sequence with and without the recorder."""
    reserve("preflight")
    res = []
    for k in (0, 6, 10):
        a = run_short(k, "shift", 987654 + k, record=False)
        b = run_short(k, "shift", 987654 + k, record=True)
        res.append(dict(k=k, identical=a["events"] == b["events"] and a["calls"] == b["calls"], n_log=len(b["log"])))
        print(res[-1], flush=True)
    if not all(r["identical"] and r["n_log"] > 0 for r in res):
        raise SystemExit("STOP: recording is not passive")
    save("preflight", dict(results=res, manifest=c_manifest(), inputs=inputs()))


def valid(records, k):
    exp = expected_tasks(k)
    got = {(r["task"]["variant"], r["task"]["seed"]): r for r in records}
    if len(records) != len(exp) or len(got) != len(exp):
        return False
    return all(((t["variant"], t["seed"]) in got and got[(t["variant"], t["seed"])]["ok"] and got[(t["variant"], t["seed"])]["task"] == t and got[(t["variant"], t["seed"])]["log"]) for t in exp)


def stage_run(workers):
    from multiprocessing import Pool
    if os.path.exists(path("run")):
        raise SystemExit("EXISTS: run exists (create-once)")
    pre = load("preflight")
    cur = c_manifest()
    if not same_build(pre["manifest"], cur) or pre["inputs"] != inputs():
        raise SystemExit("STOP: build or inputs differ from preflight")
    rs.env_check()
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
    cvs = []
    for v in rec["log"]:
        v = np.asarray(v, float)
        m = v.mean()
        if m > 0:
            cvs.append(float(v.std() / m))
    return float(np.median(cvs)) if cvs else math.nan


def spearman(x, y):
    from scipy.stats import spearmanr
    r = spearmanr(x, y).statistic
    return float(r)


def stage_analyse():
    reserve("analysis")
    pre = load("preflight")
    run = load("run")
    if not same_build(pre["manifest"], c_manifest()) or run["inputs"] != inputs() or pre["inputs"] != inputs():
        raise SystemExit("STOP: build or inputs changed")
    ra = json.load(gzip.open(os.path.join(R_OUT, "analysis.json.gz"), "rt"))
    norm = es.load("normalizers")
    H = {}
    for k, _, _ in PAIRS:
        for v in ("shift", "rotm"):
            arr = [run_H(r) for r in run["records"] if r["task"]["k"] == k and r["task"]["variant"] == v]
            if len(arr) != SEEDS or not np.all(np.isfinite(arr)):
                raise SystemExit(f"STOP: invalid H for pair {k} {v}")
            H[(k, v)] = np.array(arr)
    # baseline E_k: log10 normalised gap at call B_SHORT (shift from E archive, rotm from R run), mean over 100 seeds
    def gap_at(events, nc):
        best = math.inf
        for c, f in events:
            if c <= B_SHORT:
                best = f
        return max(0.0, (best - nc["f_star"]) / nc["s"])
    Ebase = {}
    for k, name, d in PAIRS:
        nc = norm[f"{name}|{d}"]
        sh = [r for r in es.load(f"run_part_{3 * k + 1}")["records"] if r["task"]["config"] == "gadapt"]
        rm = [r for r in json.load(gzip.open(os.path.join(R_OUT, "run.json.gz"), "rt"))["records"] if r["task"]["k"] == k and r["task"]["config"] == "gadapt"]
        if len(sh) != 100 or len(rm) != 100:
            raise SystemExit("STOP: archived records incomplete")
        Ebase[k] = (np.mean([math.log10(gap_at(r["events"], nc) + 1e-12) for r in sh]), np.mean([math.log10(gap_at(r["events"], nc) + 1e-12) for r in rm]))
    dA = np.array([ra["per_pair"][f"{n}|{d}"]["shift|gadapt"] - ra["per_pair"][f"{n}|{d}"]["rotm|gadapt"] for _, n, d in PAIRS])
    ndims = {}
    for _, n, _ in PAIRS:
        ndims[n] = ndims.get(n, 0) + 1
    w = np.array([(1 / 9) / ndims[n] for _, n, _ in PAIRS])
    n_pairs = len(PAIRS)
    rng = np.random.default_rng(BOOT_SEED)

    def stats(idx_seed, idx_pair):
        # idx_seed[k] = (shift_idx, rotm_idx) seed resamples; idx_pair: pair resample for the rank statistics
        D = np.array([H[(k, "shift")][idx_seed[k][0]].mean() - H[(k, "rotm")][idx_seed[k][1]].mean() for k in range(n_pairs)])
        wmean = float(np.sum(w * D) / np.sum(w))
        Ek = np.array([Ebase[k][1] - Ebase[k][0] for k in range(n_pairs)])  # harder (larger gap) under rotm => positive
        p = idx_pair
        r_d = spearman(D[p], dA[p]) if np.std(D[p]) > 0 and np.std(dA[p]) > 0 else math.nan
        r_e = spearman(Ek[p], dA[p]) if np.std(Ek[p]) > 0 and np.std(dA[p]) > 0 else math.nan
        return D, wmean, r_d, r_e, r_d - r_e
    ident = {k: (np.arange(SEEDS), np.arange(SEEDS)) for k in range(n_pairs)}
    D0, wm0, rd0, re0, dd0 = stats(ident, np.arange(n_pairs))
    pos = int(np.sum(D0 > 0))
    from scipy.stats import binom
    p_binom = float(binom.sf(pos - 1, n_pairs, 0.5))
    boots = []
    for _ in range(BOOT):
        isd = {k: (rng.integers(0, SEEDS, SEEDS), rng.integers(0, SEEDS, SEEDS)) for k in range(n_pairs)}
        ip = rng.integers(0, n_pairs, n_pairs)
        _, wm, rd, re, dd = stats(isd, ip)
        boots.append((wm, rd, re, dd))
    boots = np.array(boots)
    valid_rows = np.all(np.isfinite(boots), axis=1)
    nv = int(valid_rows.sum())
    blocked = nv < 0.9 * BOOT or not all(np.isfinite([wm0, rd0, re0]))
    out = dict(blocked=blocked, n_pairs=n_pairs, delta_k=D0.tolist(), dA_k=dA.tolist(), wmean_delta=wm0, spearman_delta_dA=rd0, spearman_E_dA=re0, diff=dd0,
               positive_pairs=pos, p_binomial=p_binom, valid_boot=nv, inputs=run["inputs"], freeze_commit=pre["manifest"]["freeze_commit"],
               pairs=[f"{n}|{d}" for _, n, d in PAIRS])
    if not blocked:
        b = boots[valid_rows]
        lo_wm = float(np.quantile(b[:, 0], ALPHA / 3))   # Bonferroni over the three hypotheses (simultaneous bootstrap would need joint max; conservative)
        lo_rd = float(np.quantile(b[:, 1], ALPHA / 3))
        lo_dd = float(np.quantile(b[:, 3], ALPHA / 3))
        hi_rd = float(np.quantile(b[:, 1], 1 - ALPHA / 3))
        hi_dd = float(np.quantile(b[:, 3], 1 - ALPHA / 3))
        out.update(lo_wmean=lo_wm, lo_rd=lo_rd, hi_rd=hi_rd, lo_dd=lo_dd, hi_dd=hi_dd)
        out["H64c1"] = "supported" if (lo_wm > 0 and pos >= 15 and p_binom < 0.05) else ("opposite" if (float(np.quantile(b[:, 0], 1 - ALPHA / 3)) < 0) else "undecided")
        out["H64c2"] = "supported" if (rd0 >= 0.60 and lo_rd > 0.30) else ("opposite" if hi_rd < 0.30 else "undecided")
        out["H64c3"] = "supported" if lo_dd > 0 else ("opposite" if hi_dd < 0 else "undecided")
        out["mechanism_confirmed"] = bool(out["H64c1"] == "supported" and out["H64c2"] == "supported")
        out["diagnostic_value"] = bool(out["mechanism_confirmed"] and out["H64c3"] == "supported")
    save("analysis", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("delta_k", "dA_k", "pairs", "inputs")}, indent=1))


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    wk = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    {"preflight": stage_preflight, "run": lambda: stage_run(wk), "analyse": stage_analyse}.get(st, lambda: print(__doc__))()
