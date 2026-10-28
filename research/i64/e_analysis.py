"""I64-E analysis with the corrections from the independent mathematical review (D1-D6), written BEFORE any E result was viewed.
The data-producing code (e_study.py dev/freeze/run, e_algos.py, e_common.py) is unchanged; this module replaces e_study.stage_analyse only.
Provenance: the run manifest's hashes of e_algos.py / e_common.py and the e_study.py of the freezing commit are re-verified here.
"""
import hashlib
import json
import math
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e_study as es  # noqa: E402

FREEZE_COMMIT = os.environ.get("E_FREEZE_COMMIT", "")  # git commit that froze the spec/code (recorded in the output)


def verify():
    m = es.load("manifest_run")
    cur = es.manifest("analysis")
    for f in ("e_algos.py", "e_common.py"):
        if m["files"][f] != cur["files"][f]:
            raise SystemExit(f"STOP: {f} differs from the run build")
    for k in ("python", "pip_freeze", "gadapt_tree", "protocol", "mentor_head"):
        if json.loads(json.dumps(m[k])) != json.loads(json.dumps(cur[k])):
            raise SystemExit(f"STOP: {k} differs from the run build")
    if FREEZE_COMMIT:
        blob = subprocess.run(["git", "-C", es.REPO, "show", f"{FREEZE_COMMIT}:research/i64/e_study.py"], capture_output=True).stdout
        if hashlib.sha256(blob).hexdigest() != m["files"]["e_study.py"]:
            raise SystemExit("STOP: e_study.py at the freezing commit differs from the run manifest")
    return m


def gap_fn(cell, norm):
    n = norm[f"{es.CELLS[cell][0]}|{es.CELLS[cell][1]}"]

    def gp(f):
        if not math.isfinite(f):
            return math.inf
        if f < n["f_star"] - 1e-12 * n["s"]:
            raise SystemExit(f"STOP: value below f* in cell {cell}")
        return max(0.0, (f - n["f_star"]) / n["s"])
    return gp


def area(events, gp):
    total = 0.0
    for tau in es.TAUS:
        hit = next((c for c, f in events if gp(f) <= tau), None)
        if hit is not None:
            total += (es.B - hit + 1) / es.B
    return total / len(es.TAUS)


def analyse():
    if os.path.exists(es.path("analysis_v2")):
        raise SystemExit("EXISTS: analysis_v2 exists (create-once)")
    m = verify()
    norm, runs = es.load("normalizers"), es.load("run")["records"]
    N = es.N_SEEDS
    assert len(runs) == len(es.CELLS) * len(es.CONFIGS) * N, len(runs)
    assert all(r["ok"] and r["calls"] == es.B and all(e[0] <= es.B for e in r["events"]) for r in runs)
    w = {}
    for ci, (name, d, v) in enumerate(es.CELLS):
        dims = next(len(dd) for n_, _, _, _, dd in es.FUNCS if n_ == name)
        w[ci] = (1 / 9) / dims / len(es.VARIANTS)
    assert abs(sum(w.values()) - 1) < 1e-12
    raw = {}
    for r in runs:
        ci, c, s = r["task"]["cell"], r["task"]["config"], r["task"]["seed"]
        gp = gap_fn(ci, norm)
        g = gp(r["best_f"])
        L = 1.0 if math.isinf(g) else g / (1 + g)
        if (s in raw.setdefault((ci, c), {})):
            raise SystemExit(f"STOP: duplicate record {(ci, c, s)}")
        raw[(ci, c)][s] = (area(r["events"], gp), L, g)
    for (ci, c), v in raw.items():
        assert sorted(v) == [es.seed_of("run", ci, s) for s in range(1, N + 1)], (ci, c)
    arr = {k: np.array([v[s] for s in sorted(v)]) for k, v in raw.items()}
    comps = [c for c in es.CONFIGS if c != "gadapt"]
    cells = list(w)

    def stats(idx):
        dA = [sum(w[ci] * (arr[(ci, "gadapt")][idx[ci], 0].mean() - arr[(ci, c)][idx[ci], 0].mean()) for ci in cells) for c in comps]
        dM = [sum(w[ci] * (np.median(arr[(ci, c)][idx[ci], 2]) - np.median(arr[(ci, "gadapt")][idx[ci], 2])) for ci in cells) for c in comps]
        return np.array(dA + dM)

    def simultaneous(fn, R, seed, alpha):
        point = fn({ci: np.arange(N) for ci in cells})
        rng = np.random.default_rng(seed)
        boots = np.array([fn({ci: rng.integers(0, N, N) for ci in cells}) for _ in range(R)])
        finite = bool(np.all(np.isfinite(point)) and np.all(np.isfinite(boots)))
        se = boots.std(axis=0, ddof=1) if finite else np.full(len(point), np.nan)
        zero = bool(finite and np.any(se <= 0))
        ok = finite and not zero
        if ok:
            t = float(np.quantile(np.max(np.abs(boots - point) / se, axis=1), 1 - alpha))
            return point, point - t * se, point + t * se, t, dict(finite=finite, zero_variance=zero, blocked=False)
        return point, np.full(len(point), np.nan), np.full(len(point), np.nan), float("nan"), dict(finite=finite, zero_variance=zero, blocked=True)

    R = int(os.environ.get("E_BOOT", "20000"))
    point, lo, hi, tstar, flags_a = simultaneous(stats, R, 64, 0.02)
    names = [f"dA|{c}" for c in comps] + [f"dM|{c}" for c in comps]
    contrasts = {nm: dict(estimate=float(p), lower=float(a), upper=float(b)) for nm, p, a, b in zip(names, point, lo, hi)}
    if flags_a["blocked"]:
        verdict, supported, opposite = "blocked", False, False
    else:
        dA_lo = {c: contrasts[f"dA|{c}"]["lower"] for c in comps}
        dA_hi = {c: contrasts[f"dA|{c}"]["upper"] for c in comps}
        dM_lo = {c: contrasts[f"dM|{c}"]["lower"] for c in comps}
        dM_hi = {c: contrasts[f"dM|{c}"]["upper"] for c in comps}
        supported = all(dA_lo[c] > 0 for c in comps) or any(all(dA_lo[c] > 0 for c in comps if c != e) and dM_lo[e] > 0 for e in comps)
        opposite = len([c for c in comps if dA_hi[c] < 0]) >= 2 or any(dA_hi[c] < 0 and dM_hi[c] < 0 for c in comps)
        verdict = "supported" if supported else ("opposite" if opposite else "undecided")

    def cv(c, idx):
        return sum(w[ci] * es.cvar(list(arr[(ci, c)][idx[ci], 1])) for ci in cells)

    def rc(c, t, idx):
        return sum(w[ci] * np.mean(arr[(ci, c)][idx[ci], 2] <= t) for ci in cells)

    def b_stats(idx):
        return np.array([0.8 * cv("gadapt", idx) - cv("gadapt_preset", idx)] + [rc("gadapt_preset", t, idx) - rc("gadapt", t, idx) for t in es.TAUS])
    bp, blo, bhi, bt, flags_b = simultaneous(b_stats, R, 65, 0.01)
    full = {ci: np.arange(N) for ci in cells}
    r0 = cv("gadapt", full)
    h64b = dict(R0=float(r0), Rpreset=float(cv("gadapt_preset", full)), point=[float(x) for x in bp], lower=[float(x) for x in blo], tstar=bt,
                flags=flags_b, supported=bool((not flags_b["blocked"]) and r0 > 0 and blo[0] >= 0 and all(blo[1:] >= -0.05)))
    agg = {c: dict(A=float(sum(w[ci] * arr[(ci, c)][:, 0].mean() for ci in cells)), cvar90=float(cv(c, full)),
                   median_gap=float(sum(w[ci] * np.median(arr[(ci, c)][:, 2]) for ci in cells)),
                   reach=[float(rc(c, t, full)) for t in es.TAUS]) for c in es.CONFIGS}
    # descriptive disclosure for the CVaR bootstrap limitation (D5): runs per config with L > 0.5
    heavy = {c: int(sum((arr[(ci, c)][:, 1] > 0.5).sum() for ci in cells)) for c in es.CONFIGS}
    per_cell = {f"{es.CELLS[ci][0]}|{es.CELLS[ci][1]}|{es.CELLS[ci][2]}|{c}": dict(A=float(arr[(ci, c)][:, 0].mean()),
                                                                              median_gap=float(np.median(arr[(ci, c)][:, 2])),
                                                                              cvar90=es.cvar(list(arr[(ci, c)][:, 1])))
                for ci in cells for c in es.CONFIGS}
    out = dict(verdict=verdict, flags=flags_a, tstar=tstar, alpha=0.02, bootstrap=R, contrasts=contrasts, aggregate=agg, h64b=h64b,
               heavy_failures_L_gt_0_5=heavy, per_cell=per_cell, freeze_commit=FREEZE_COMMIT,
               artifact_sha256={f: es.sha(es.path(f)) for f in ("normalizers", "dev", "freeze", "run")})
    es.save("analysis_v2", out)
    es.save("manifest_analysis_v2", es.manifest("analysis_v2"))
    print(json.dumps({k: out[k] for k in ("verdict", "flags", "tstar", "contrasts", "aggregate", "h64b")}, indent=1)[:6000])


if __name__ == "__main__":
    analyse()
