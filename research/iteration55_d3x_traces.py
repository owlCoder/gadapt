"""I55 (paper Study 5): corrected D3x with effective hash seeds, and full call-trace archive.

Frozen protocol: research/ITERATION55_PROTOCOL.md. Adapters, configurations and the classifier are the unchanged
I49/I50 ones. Each cell runs in three fresh processes of the library's interpreter, launched with -s and
PYTHONSAFEPATH=1 (python -I implies -E and would ignore PYTHONHASHSEED); every process reports a sentinel hash.
Usage:
  python -m research.iteration55_d3x_traces run <sample i49|i50> <library> <python> [workers]   (repository .venv)
  python -m research.iteration55_d3x_traces cell <sample> <library> <function> <d> <seed> <twice> <trace|-> [mode]
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

import research.iteration49_integrity_audit as i49

MARK = "@@I55@@"
SENTINEL = "integrity-audit-sentinel"
OUT = os.path.join("research", "results", "iteration55")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMEOUT = 3600
PHASES = ("search", "post")


# ---------------------------------------------------------------- cell (runs inside the library's environment)

def execute(sample, library, function, d, seed, mode="-"):
    if sample == "i49":
        problem, calls, res = i49.execute(library, function, d, seed)
    else:
        import research.iteration50_integrity_audit as i50
        kwargs = {} if mode == "-" else dict(mode=mode)  # mode: the I50 D3x validation mutants (ref_seeded)
        problem, calls, res = i50.execute(library, function, d, seed, i50.BUDGET, **kwargs)
    return problem, calls, res


def save_trace(path, calls, res):
    x = np.array([c[0] for c in calls], dtype=float) if calls else np.zeros((0, 0))
    f = np.array([c[1] for c in calls], dtype=float)
    phase = np.array([PHASES.index(c[2]) for c in calls], dtype=np.int8)
    x_star = np.asarray(res["x"], dtype=float).ravel() if res.get("x") is not None else np.zeros(0)
    np.savez_compressed(path, x=x, f=f, phase=phase, x_star=x_star,
                        f_star=np.array([np.nan if res.get("f") is None else float(res["f"])]),
                        reported_evals=np.array([-1 if res.get("reported_evals") is None else res["reported_evals"]]),
                        documented_max=np.array([-1 if res.get("documented_max") is None else res["documented_max"]]))


def cell(sample, library, function, d, seed, twice, trace, mode="-"):
    import research.iteration50_integrity_audit as i50
    out = dict(library=library, function=function, d=int(d), seed=int(seed), hash_sentinel=hash(SENTINEL))
    start = time.monotonic()
    try:
        problem, calls, res = execute(sample, library, function, int(d), int(seed), mode)
        flags, n, r_applicable = i50.classify(calls, res, problem) if calls else ({}, 0, False)
        out.update(calls=n, flags=flags, r_applicable=r_applicable, hash=i49.sequence_hash(calls), error=None)
        if trace != "-":
            save_trace(trace, calls, res)
        if twice:
            out["hash_rerun"] = i49.sequence_hash(execute(sample, library, function, int(d), int(seed), mode)[1])
    except BaseException as exc:  # recorded, never hidden
        out.update(calls=None, flags=None, error=f"{type(exc).__name__}: {str(exc)[:200]}")
    out["seconds"] = round(time.monotonic() - start, 2)
    print(MARK + json.dumps(out, default=int), flush=True)


# ---------------------------------------------------------------- driver (repository .venv)

def fresh(python, sample, library, function, d, seed, twice, hashseed, trace, mode="-"):
    args = [python, "-s", "-m", "research.iteration55_d3x_traces", "cell", sample, library, function, str(d),
            str(seed), "1" if twice else "0", trace, mode]
    env = dict(os.environ, PYTHONHASHSEED=str(hashseed), PYTHONSAFEPATH="1", PYTHONPATH=REPO,
               OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    try:
        proc = subprocess.run(args, capture_output=True, text=True, env=env, cwd=REPO, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return dict(error="timeout")
    lines = [line for line in proc.stdout.splitlines() if line.startswith(MARK)]
    if not lines:
        return dict(error=f"exit {proc.returncode}: {proc.stderr[-300:]}")
    return json.loads(lines[-1][len(MARK):])


def audit_cell(python, sample, library, function, d, seed, trace_dir, mode="-"):
    trace = os.path.join(trace_dir, f"{function}_{d}_{seed}.npz")
    a = fresh(python, sample, library, function, d, seed, True, 1, trace, mode)
    a_same = fresh(python, sample, library, function, d, seed, False, 1, "-", mode)
    b = fresh(python, sample, library, function, d, seed, False, 2, "-", mode)
    out = dict(a, sample=sample, hash_same=a_same.get("hash"), hash_diff=b.get("hash"),
               sentinel_same=a_same.get("hash_sentinel"), sentinel_diff=b.get("hash_sentinel"),
               errors=[x.get("error") for x in (a, a_same, b) if x.get("error")])
    valid = (not out["errors"] and a["hash_sentinel"] == a_same["hash_sentinel"]
             and a["hash_sentinel"] != b["hash_sentinel"])
    out["manipulation_ok"] = valid
    if valid:
        out["D3"] = int(a["hash"] != a["hash_rerun"])
        out["D3x_same"] = int(a["hash"] != a_same["hash"])
        out["D3x_diff"] = int(a["hash"] != b["hash"])
    return out


def run(sample, library, python, workers=4):
    os.makedirs(OUT, exist_ok=True)
    trace_dir = os.path.join(OUT, "traces", library)
    os.makedirs(trace_dir, exist_ok=True)
    tasks = [(f, d, s) for f in i49.FUNCTIONS for d in i49.DIMS for s in i49.SEEDS]
    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=int(workers)) as pool:
        cells = list(pool.map(lambda t: audit_cell(python, sample, library, *t, trace_dir), tasks))
    freeze = subprocess.run([python, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines()
    version = subprocess.run([python, "-c", "import sys; print(sys.version)"], capture_output=True, text=True).stdout
    json.dump(dict(sample=sample, library=library, python=version.strip(), pip_freeze=freeze, workers=int(workers),
                   cells=cells, seconds=round(time.monotonic() - start, 1)),
              open(os.path.join(OUT, f"cells_{library}.json"), "w"), indent=1)
    ok = [c for c in cells if c["manipulation_ok"]]
    print(json.dumps(dict(library=library, cells=len(cells), valid=len(ok),
                          D3=sum(c["D3"] for c in ok), D3x_same=sum(c["D3x_same"] for c in ok),
                          D3x_diff=sum(c["D3x_diff"] for c in ok))))


if __name__ == "__main__":
    command, rest = sys.argv[1], sys.argv[2:]
    if command == "cell":
        cell(*rest)
    elif command == "run":
        run(*rest)
