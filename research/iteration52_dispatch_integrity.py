"""I52: do integrity findings transfer to a real infrastructure cost function (AC economic dispatch)?

Previously frozen: research/ITERATION52_PROTOCOL.md (commit 32bac01). Adapters and classifier are the unchanged
I49/I50 ones; only the cost function changes (I47 `Dispatch.evaluate(...)["score"]`).

  python research/iteration52_dispatch_integrity.py validate                  (repository .venv)
  python research/iteration52_dispatch_integrity.py run <library> <python> [workers]
  python research/iteration52_dispatch_integrity.py aggregate                 (repository .venv)
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
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

import research.iteration49_integrity_audit as i49  # noqa: E402
import research.iteration50_integrity_audit as i50  # noqa: E402

OUT = os.path.join(HERE, "results", "iteration52")
CASES = ("case14", "case39", "case118")
SEEDS = i49.SEEDS
MARK = "@@I52@@"
TIMEOUT = 600
STUDY1 = i49.LIBRARIES
STUDY2 = tuple(json.load(open(os.path.join(HERE, "results", "iteration50", "eligible.json")))["sample"])
INTEGRITY = ("C3", "C4", "C5", "R1", "R2", "R3", "D2", "D3", "D3x")  # C1 not counted (protocol)


class DispatchProblem:
    """The I47 dispatch score with the attribute interface the I49/I50 adapters use (d, lo, hi, call)."""

    def __init__(self, case):
        from research.iteration47_invariance import Dispatch
        self.dispatch = Dispatch(case)
        bounds = np.array(self.dispatch.bounds_mw, dtype=float)
        self.d, self.lo, self.hi = len(bounds), bounds[:, 0].copy(), bounds[:, 1].copy()

    def __call__(self, x):
        return float(self.dispatch.evaluate(np.asarray(x, float))["score"])


def execute(library, case, seed):
    problem = DispatchProblem(case)
    rec = (i50.Recorder32 if library in i50.TORCH else i49.Recorder)(problem)
    i49._seed_all(seed)
    with tempfile.TemporaryDirectory() as tmp:
        old = os.getcwd()
        os.chdir(tmp)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                if library in STUDY1 or library == "gadapt":
                    res = i49.ADAPTERS[library](rec, problem, seed)
                else:
                    res = i50.ADAPTERS[library](rec, problem, seed, i50.BUDGET)
        finally:
            os.chdir(old)
    if res.get("x") is not None:
        res = dict(res, x=np.asarray(res["x"], float).ravel())
    return problem, rec.calls, res


def cell(library, case, seed, twice):
    out = dict(library=library, case=case, seed=seed)
    start = time.monotonic()
    try:
        problem, calls, res = execute(library, case, seed)
        flags, n, r_applicable = i50.classify(calls, res, problem) if calls else ({}, 0, False)
        out.update(calls=n, flags=flags, r_applicable=r_applicable, hash=i49.sequence_hash(calls), error=None)
        if twice:
            out["hash_rerun"] = i49.sequence_hash(execute(library, case, seed)[1])
    except BaseException as exc:  # recorded, never hidden
        out.update(calls=None, flags=None, error=f"{type(exc).__name__}: {str(exc)[:200]}")
    out["seconds"] = round(time.monotonic() - start, 2)
    print(MARK + json.dumps(out), flush=True)


def fresh(python, library, case, seed, twice, hashseed):
    args = [python, "-I", os.path.abspath(__file__), "cell", library, case, str(seed), "1" if twice else "0"]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT * (2 if twice else 1),
                              env=dict(os.environ, PYTHONHASHSEED=str(hashseed), **i50.THREADS))
    except subprocess.TimeoutExpired:
        return dict(library=library, case=case, seed=seed, calls=None, flags=None, error="timeout")
    lines = [line for line in proc.stdout.splitlines() if line.startswith(MARK)]
    if not lines:
        return dict(library=library, case=case, seed=seed, calls=None, flags=None,
                    error=f"no result (exit {proc.returncode}): {proc.stderr.strip()[-200:]}")
    return json.loads(lines[-1][len(MARK):])


def audit_cell(python, library, case, seed):
    a = fresh(python, library, case, seed, True, 1)
    b = fresh(python, library, case, seed, False, 2)
    if a.get("error") is None:
        a["flags"]["D3"] = int(a["hash"] != a["hash_rerun"])
        a["flags"]["D3x"] = None if b.get("error") is not None else int(a["hash"] != b["hash"])
        a["cross_process_error"] = b.get("error")
    return a


def validate():
    report = {}
    for mode, want in ((None, (0, 0)), ("hash_seeded", (0, 1)), ("time_seeded", (1, 1))):
        c = i50.audit_cell(sys.executable, "ref_seeded", "sphere", 2, 1, 50, mode)
        got = (c["flags"]["D3"], c["flags"]["D3x"]) if c.get("error") is None else None
        report[f"d3x_{mode}"] = dict(expected=list(want), got=got, ok=got == want)
    timing = {}
    for case in CASES:
        p = DispatchProblem(case)
        rng = np.random.default_rng(0)
        start = time.perf_counter()
        for _ in range(50):
            p(rng.uniform(p.lo, p.hi))
        timing[case] = dict(d=p.d, ms_per_evaluation=round((time.perf_counter() - start) / 50 * 1000, 2))
    passed = all(v["ok"] for v in report.values())
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(validation=report, passed=passed, timing=timing), open(os.path.join(OUT, "validation.json"), "w"),
              indent=1)
    print(json.dumps(report), json.dumps(timing), passed)
    return passed


def run(library, python, workers=5):
    if not json.load(open(os.path.join(OUT, "validation.json")))["passed"]:
        raise SystemExit("validation has not passed: not running")
    tasks = [(case, s) for case in CASES for s in SEEDS]
    start = time.monotonic()
    with ThreadPoolExecutor(int(workers)) as pool:
        cells = list(pool.map(lambda t: audit_cell(python, library, *t), tasks))
    freeze = subprocess.run([python, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines()
    json.dump(dict(library=library, pip_freeze=freeze, threads=i50.THREADS, cells=cells,
                   seconds=round(time.monotonic() - start, 1)),
              open(os.path.join(OUT, f"cells_{library}.json"), "w"), indent=1)
    print(library, "done", round(time.monotonic() - start), "s")


def synthetic_status():
    """Library-level synthetic finding status without C1: I49 + I51 D3x (study 1), I50 (study 2)."""
    i49r = json.load(open(os.path.join(HERE, "results", "iteration49", "integrity_audit.json")))["per_library"]
    i51r = json.load(open(os.path.join(HERE, "results", "iteration51", "d3x.json")))["per_library"]
    i50r = json.load(open(os.path.join(HERE, "results", "iteration50", "integrity_audit.json")))["per_library"]
    out = {}
    for lib in STUDY1:
        classes = {k for k in INTEGRITY if (i49r[lib]["runs_with_class"].get(k) or 0) > 0}
        if i51r[lib]["d3x_runs"]:
            classes.add("D3x")
        out[lib] = sorted(classes)
    for lib in STUDY2:
        out[lib] = sorted(k for k in INTEGRITY if (i50r[lib]["runs_with_class"].get(k) or 0) > 0)
    return out


def aggregate():
    from scipy.stats import beta
    timing = json.load(open(os.path.join(OUT, "validation.json")))["timing"]
    synthetic = synthetic_status()
    per, agree, assessed = {}, 0, 0
    for lib in STUDY1 + STUDY2 + ("gadapt",):
        data = json.load(open(os.path.join(OUT, f"cells_{lib}.json")))
        ok = [c for c in data["cells"] if c.get("error") is None]
        runs = {k: sum(1 for c in ok if (c["flags"].get(k) or 0) > 0) for k in ("C1", "C2") + INTEGRITY}
        real = sorted(k for k in INTEGRITY if runs[k])
        dup = [c["flags"]["C2"] / c["calls"] for c in ok if c["calls"]]
        wasted = sum(c["flags"]["C2"] * timing[c["case"]]["ms_per_evaluation"] / 1000 for c in ok)
        row = dict(runs=len(data["cells"]), errors=len(data["cells"]) - len(ok), runs_with_class=runs,
                   real_classes=real, synthetic_classes=synthetic.get(lib),
                   median_duplicate_fraction=float(np.median(dup)) if dup else None,
                   estimated_seconds_on_duplicates=round(wasted, 2),
                   error_examples=sorted({c["error"] for c in data["cells"] if c.get("error")})[:2])
        if lib != "gadapt" and ok:
            assessed += 1
            row["status_agrees"] = bool(real) == bool(synthetic[lib])
            agree += row["status_agrees"]
        per[lib] = row
    lo = 0.0 if agree == 0 else float(beta.ppf(0.025, agree, assessed - agree + 1))
    hi = 1.0 if agree == assessed else float(beta.ppf(0.975, agree + 1, assessed - agree))
    primary = dict(agree=agree, of=assessed, clopper_pearson_95=[lo, hi],
                   verdict="H52 SUPPORTED" if agree >= 17 else "H52 REFUTED",
                   unassessable=[lib for lib in STUDY1 + STUDY2 if not per[lib]["runs"] - per[lib]["errors"]])
    out = dict(protocol="research/ITERATION52_PROTOCOL.md", protocol_commit="32bac01",
               source_sha256=hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
               driver=dict(python=sys.version.split()[0], platform=platform.platform()), timing=timing,
               per_library=per, primary=primary)
    json.dump(out, open(os.path.join(OUT, "integrity_dispatch.json"), "w"), indent=1)
    print(json.dumps(primary, indent=1))


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "cell":
        cell(args[0], args[1], int(args[2]), args[3] == "1")
    elif cmd == "validate":
        raise SystemExit(0 if validate() else 1)
    elif cmd == "run":
        run(*args)
    elif cmd == "aggregate":
        aggregate()
