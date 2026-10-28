"""I63-D: DESCRIPTIVE (non-confirmatory) extension of the I63 estimand after the I63 final STOP in `power`.

What it is: the frozen I63 test design (roster, normalisers, FX-T vectors, n = chosen_n from the I63 power screening, seeds p = 3, B = 12,000,
W / theta_63 estimand and bootstrap) executed in a NEW directory, results/iteration63d. The I63 directory and its STOP are not touched
(read only, hash-checked). It makes NO confirmatory claim about H56a/H63: the I63 calibration criterion that stopped the study is not met
and is not relaxed; this is reported as an estimate with intervals and a description.

  python research/i63tools/d_study.py gate|run [workers]|check [workers]|analyse
"""
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "research"))
import iteration63_replication as m  # noqa: E402  (module-level: I63 scenarios, seeds, estimand; OUT = the I63 directory = SOURCE here)

import numpy as np  # noqa: E402

SRC = m.OUT
D_OUT = os.environ.get("D_OUT", os.path.join(REPO, "research", "results", "iteration63d"))
m.i61.OUT = D_OUT  # everything the I61/I63 machinery saves from this process goes to D_OUT (workers read the roster from SRC)


def src_path(name):
    return os.path.join(SRC, name + ".json.gz")


def src_load(name):
    with gzip.open(src_path(name), "rt") as fh:
        return json.load(fh)


def d_path(name):
    os.makedirs(D_OUT, exist_ok=True)
    return os.path.join(D_OUT, name + ".json.gz")


def save(name, data):
    with gzip.open(d_path(name), "wt") as fh:
        json.dump(data, fh)


def load(name):
    with gzip.open(d_path(name), "rt") as fh:
        return json.load(fh)


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def source_state():
    n = src_load("power")["chosen_n"] if os.path.exists(src_path("power")) else int(os.environ.get("D_N", "0"))
    if n <= 0:
        raise SystemExit("STOP: no chosen_n in the I63 power artifact")
    fx = src_load("fxt")["chosen"]
    roster = src_load("roster")
    cells = [tuple(x) for x in roster["test"]]
    return n, fx, cells


def provenance():
    p = m.build_manifest("d")
    p["source_sha256"] = {f: sha(src_path(f)) for f in ("roster", "normalizers", "fxt", "rehearsal") if os.path.exists(src_path(f))}
    return p


def same(a, b):
    keys = ("python", "pip_freeze", "gadapt_tree_sha256", "library_root", "code_sha256", "settings", "source_sha256")
    return all(json.loads(json.dumps(a[k])) == json.loads(json.dumps(b[k])) for k in keys)


def stage_gate(workers):
    if os.path.exists(d_path("gate")):
        raise SystemExit("EXISTS: gate exists (create-once)")
    before = provenance()
    if not m.i61.gate_run("current", workers):
        raise SystemExit("STOP: the I56 instrument is not bit-identical on the current library")
    if not same(before, provenance()):
        raise SystemExit("STOP: provenance changed during the gate")
    save("gate", dict(passed=True, manifest=before))


def require_gate():
    g = load("gate")
    if not (g["passed"] and same(g["manifest"], provenance())):
        raise SystemExit("STOP: build differs from the gated one")


def stage_run(workers):
    from multiprocessing import Pool
    require_gate()
    n, fx, cells = source_state()
    tasks_all = lambda n_, j_: [m.task63(n_, j_, c, a, "test", s, fixed=fx[c] if a == "FX-T" else None)
                                for s in range(1, n + 1) for c, a in m.ARMS]
    m.check_archive_collisions([t for (n_, j_) in cells for t in tasks_all(n_, j_)])
    records = []
    for n_, j_ in cells:
        part = f"run_part_{n_}_{j_}"
        if os.path.exists(d_path(part)):
            records.extend(load(part)["records"])
            continue
        tasks = tasks_all(n_, j_)
        with Pool(workers, maxtasksperchild=1) as pool:
            recs = list(pool.imap(m.run63, tasks, chunksize=1))
        for i, r in enumerate(recs):
            if not r.get("ok"):
                with Pool(1, maxtasksperchild=1) as pool:
                    again = pool.apply(m.run63, (tasks[i],))
                again["rerun"], again["first_attempt"] = True, r
                recs[i] = again
        bad = [r for r in recs if not r.get("ok")]
        save(part, dict(records=recs))
        if bad:
            raise SystemExit(f"STOP: {len(bad)} runs failed technically twice in {n_} {j_}")
        records.extend(recs)
        print("cell", n_, j_, "done", flush=True)
    m.i61.assert_paired(records)
    save("run", dict(records=records, n=n, fx=fx, manifest=provenance()))


def stage_check(workers):
    from multiprocessing import Pool
    require_gate()
    recs = load("run")["records"]
    items = [((r["task"]["network"], r["task"]["j"], r["best_feasible_x"]), r["best_feasible"]) for r in recs if r.get("best_feasible") is not None]
    with Pool(workers) as pool:
        checks = pool.map(m.check_item, [x for x, _ in items], chunksize=64)
    fails = sum(1 for (_, v), c in zip(items, checks) if not (c.get("valid") and c.get("converged") and c.get("feasible")
                                                                and abs(c["losses"] - v) <= 1e-6 * max(1.0, v)))
    save("check", dict(expected=len(items), rows=len(checks), failures=fails))
    print("checked", len(checks), "failures", fails)
    if fails:
        raise SystemExit("STOP: independent check failed")


def stage_analyse():
    require_gate()
    chk = load("check")
    if chk["failures"] or chk["rows"] != chk["expected"]:
        raise SystemExit("STOP: independent check missing or failed")
    run = load("run")
    n, fx, cells = source_state()
    r = src_load("normalizers")["r"]
    units = m.units_of(run["records"])
    planned = [(n_, j_, s) for n_, j_ in cells for s in range(1, n + 1)]
    if sorted(units) != sorted(planned) or any(set(u) != set(m.ARMS) or not all(x["ok"] for x in u.values()) for u in units.values()):
        raise SystemExit("STOP: records are not exactly the planned complete units")
    cell_d = {}
    for (n_, j_, s), u in sorted(units.items()):
        cell_d.setdefault((n_, j_), []).append(m.d_of(u, r[f"{n_}|{j_}"]))
    prim = m.bootstrap(cell_d)
    nm = {k: float(np.mean([np.mean(v) for kk, v in cell_d.items() if kk[0] == k])) for k in m.NETWORKS}
    desc = {}
    for n_, j_ in cells:
        us = [u for (a, b, _), u in units.items() if (a, b) == (n_, j_)]
        rr = r[f"{n_}|{j_}"]
        row = {"d_mean": float(np.mean(cell_d[(n_, j_)])), "n": len(us)}
        for c in ("FR", "SP"):
            row[f"W|{c}"] = float(np.mean([m.win2(u[(c, "FX-T")]["best_feasible"], u[(c, "AD-N")]["best_feasible"], rr) / 2 for u in us]))
        for c, a in m.ARMS:
            g = [m.gap(u[(c, a)], rr) for u in us]
            fin = [x for x in g if x is not None]
            row[f"{c}|{a}"] = dict(feasible=len(fin) / len(g), median_gap=float(np.median(fin)) if fin else None)
        desc[f"{n_}|{j_}"] = row
    out = dict(label="DESCRIPTIVE; not confirmatory; I63 stopped in power and this does not replace it", H63_descriptive=prim, network_means=nm,
               leave_one_network_out={k: float(np.mean([v for kk, v in nm.items() if kk != k])) for k in nm}, n=n, descriptive=desc,
               source_sha256=run["manifest"]["source_sha256"])
    save("analysis", out)
    print(json.dumps({k: out[k] for k in ("label", "H63_descriptive", "network_means")}, indent=1))


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    wk = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    {"gate": lambda: stage_gate(wk), "run": lambda: stage_run(wk), "check": lambda: stage_check(wk), "analyse": stage_analyse}.get(st, lambda: print(__doc__))()
