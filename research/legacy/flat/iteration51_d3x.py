"""I51: cross-process reproducibility (D3x) on the I49 sample, with the unchanged I49 adapters.

Previously frozen: research/ITERATION51_PROTOCOL.md (commit 6a22aad).

  python research/iteration51_d3x.py validate            (repository .venv)
  python research/iteration51_d3x.py run <python> [workers]  (driver; cells run in <python>, the I49 environment)
"""
import contextlib
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import research.iteration49_integrity_audit as i49  # noqa: E402

OUT = os.path.join(HERE, "results", "iteration51")
MARK = "@@I51@@"
TIMEOUT = 600
THREADS = {k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}


def cell(library, function, d, seed, twice):
    out = dict(library=library, function=function, d=d, seed=seed)
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            _, calls, _ = i49.execute(library, function, d, seed)
            out.update(calls=len(calls), hash=i49.sequence_hash(calls), error=None)
            if twice:
                out["hash_rerun"] = i49.sequence_hash(i49.execute(library, function, d, seed)[1])
    except BaseException as exc:  # recorded, never hidden
        out.update(error=f"{type(exc).__name__}: {str(exc)[:200]}")
    print(MARK + json.dumps(out), flush=True)


def fresh(python, library, function, d, seed, twice, hashseed):
    args = [python, "-I", os.path.abspath(__file__), "cell", library, function, str(d), str(seed),
            "1" if twice else "0"]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT * (2 if twice else 1),
                              env=dict(os.environ, PYTHONHASHSEED=str(hashseed), **THREADS))
    except subprocess.TimeoutExpired:
        return dict(error="timeout")
    lines = [line for line in proc.stdout.splitlines() if line.startswith(MARK)]
    return json.loads(lines[-1][len(MARK):]) if lines else dict(error=f"exit {proc.returncode}: {proc.stderr[-200:]}")


def audit_cell(python, library, function, d, seed):
    a = fresh(python, library, function, d, seed, True, 1)
    b = fresh(python, library, function, d, seed, False, 2)
    row = dict(library=library, function=function, d=d, seed=seed, calls=a.get("calls"),
               error=a.get("error") or b.get("error"))
    if a.get("error") is None:
        row["D3"] = int(a["hash"] != a["hash_rerun"])
        row["D3x"] = None if b.get("error") else int(a["hash"] != b["hash"])
    return row


def validate():
    import research.iteration50_integrity_audit as i50
    report = {}
    for mode, want in ((None, (0, 0)), ("hash_seeded", (0, 1)), ("time_seeded", (1, 1))):
        c = i50.audit_cell(sys.executable, "ref_seeded", "sphere", 2, 1, 50, mode)
        got = (c["flags"]["D3"], c["flags"]["D3x"]) if c.get("error") is None else None
        report[f"d3x_{mode}"] = dict(expected=list(want), got=got, ok=got == want)
    passed = all(v["ok"] for v in report.values())
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(validation=report, passed=passed), open(os.path.join(OUT, "validation.json"), "w"), indent=1)
    print(json.dumps(report), passed)
    return passed


def run(python, workers=8):
    if not json.load(open(os.path.join(OUT, "validation.json")))["passed"]:
        raise SystemExit("D3x validation has not passed: not running")
    tasks = [(lib, fn, d, s) for lib in i49.LIBRARIES + i49.CONTROLS for fn in i49.FUNCTIONS for d in i49.DIMS
             for s in i49.SEEDS]
    start = time.monotonic()
    with ThreadPoolExecutor(int(workers)) as pool:
        cells = list(pool.map(lambda t: audit_cell(python, *t), tasks))
    per = {}
    for lib in i49.LIBRARIES + i49.CONTROLS:
        rows = [c for c in cells if c["library"] == lib]
        ok = [c for c in rows if c["error"] is None]
        per[lib] = dict(runs=len(rows), errors=len(rows) - len(ok), d3_runs=sum(c["D3"] for c in ok),
                        d3x_runs=sum(1 for c in ok if c["D3x"]), d3x_unavailable=sum(1 for c in ok if c["D3x"] is None),
                        error_examples=sorted({c["error"] for c in rows if c["error"]})[:2])
    freeze = subprocess.run([python, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines()
    result = dict(protocol="research/ITERATION51_PROTOCOL.md", protocol_commit="6a22aad",
                  source_sha256=hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
                  i49_source_sha256=hashlib.sha256(open(i49.__file__, "rb").read()).hexdigest(),
                  driver=dict(python=sys.version.split()[0], platform=platform.platform()), pip_freeze=freeze,
                  threads=THREADS, per_library=per,
                  libraries_with_d3x=[lib for lib in i49.LIBRARIES if per[lib]["d3x_runs"]],
                  cells=cells, seconds=round(time.monotonic() - start, 1))
    json.dump(result, open(os.path.join(OUT, "d3x.json"), "w"), indent=1)
    print(json.dumps({lib: {k: v for k, v in r.items() if k != "error_examples"} for lib, r in per.items()}, indent=1))
    print("libraries with D3x:", result["libraries_with_d3x"], result["seconds"], "s")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "cell":
        cell(args[0], args[1], int(args[2]), int(args[3]), args[4] == "1")
    elif cmd == "validate":
        raise SystemExit(0 if validate() else 1)
    elif cmd == "run":
        run(*args)
