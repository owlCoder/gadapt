"""Evaluation-integrity audit for any black-box optimizer: a practitioner's front end to the I49/I50 classifier.

Wrap your optimizer in a function

    def run(f, lower, upper, budget, seed):
        ...                      # your optimizer calls f(x) for x in the box, at most `budget` times
        f.search_done()          # optional: mark that the optimizer's main call has returned (enables C5)
        ...                      # extract the result the way your code does
        return x_best, f_best    # what your code reports (or None if it reports nothing)

and run

    python research/integrity_audit_tool.py path/to/my_module.py:run --budget 200

The tool runs your optimizer on three test functions (shifted sphere, Rastrigin, floor plateau) in 2-D and 10-D with
several seeds, records every call and reports, per class, in how many runs it occurred:

  integrity   C3 out of the box, C4 over the budget, C5 calls after `run` returned, R1 reported x never evaluated,
              R2 reported f differs from the recorded f(x), R3 reported f worse than the best evaluated,
              D3 same seed differs within one process, D3x same seed differs between two fresh processes
  waste       C2 share of repeated evaluations
  info        C1 evaluations exactly at the all-lower or all-upper corner (a validation probe, or a legitimate point
              of an algorithm that clips to the bounds: inspect before concluding, research I50 §3)

Validated on planted faults (research/test_integrity_audit_tool.py) and used in research I49/I50.
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

import research.iteration49_integrity_audit as i49  # noqa: E402

INTEGRITY = ("C3", "C4", "C5", "R1", "R2", "R3", "D3", "D3x")
MARK = "@@AUDIT@@"
EXPLAIN = {
    "C3": "evaluates points outside the box",
    "C4": "evaluates more often than the budget",
    "C5": "evaluates after the optimizer returned (e.g. while extracting the result)",
    "R1": "reports a solution that was never evaluated",
    "R2": "reports a cost that differs from the recorded cost of the reported solution",
    "R3": "reports a solution worse than the best one it evaluated",
    "D3": "same seed, different call sequence within one process",
    "D3x": "same seed, different call sequence between processes (e.g. depends on PYTHONHASHSEED)",
}


def load(target):
    path, name = target.rsplit(":", 1)
    spec = importlib.util.spec_from_file_location("audited_module", os.path.abspath(path))
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec.loader.exec_module(module)
    return getattr(module, name)


class Recorder(i49.Recorder):
    def search_done(self):
        self.phase = "post"


def execute(run, function, d, seed, budget):
    problem = i49.Problem(function, d)
    rec = Recorder(problem)
    i49._seed_all(seed)
    with contextlib.redirect_stdout(io.StringIO()):
        out = run(rec, problem.lo.copy(), problem.hi.copy(), budget, seed)
    rec.phase = "post"
    x, f = (None, None) if out is None else out
    result = dict(x=None if x is None else np.asarray(x, float).ravel(), f=None if f is None else float(f),
                  reported_evals=None, documented_max=budget)
    return problem, rec.calls, result


def classify(calls, result, problem):
    if not calls:
        return {}
    if result["x"] is None:
        flags, _ = i49.classify(calls, dict(result, x=calls[0][0], f=None), problem)
        flags.update(R1=0, R2=0, R3=0)
    else:
        flags, _ = i49.classify(calls, result, problem)
    flags.pop("D2", None)
    return flags


def cell(target, function, d, seed, budget, twice):
    run = load(target)
    out = dict(function=function, d=d, seed=seed)
    try:
        problem, calls, result = execute(run, function, d, seed, budget)
        out.update(calls=len(calls), flags=classify(calls, result, problem), hash=i49.sequence_hash(calls),
                   reports_result=result["x"] is not None, error=None)
        if twice:
            out["hash_rerun"] = i49.sequence_hash(execute(run, function, d, seed, budget)[1])
    except Exception as exc:
        out.update(error=f"{type(exc).__name__}: {str(exc)[:200]}")
    print(MARK + json.dumps(out), flush=True)


def fresh_process(target, function, d, seed, budget, twice, hashseed, python, timeout):
    args = [python, "-I", os.path.abspath(__file__), "--cell", target, function, str(d), str(seed), str(budget),
            "1" if twice else "0"]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                              env=dict(os.environ, PYTHONHASHSEED=str(hashseed)))
    except subprocess.TimeoutExpired:
        return dict(function=function, d=d, seed=seed, error="timeout")
    lines = [line for line in proc.stdout.splitlines() if line.startswith(MARK)]
    if not lines:
        return dict(function=function, d=d, seed=seed, error=f"exit {proc.returncode}: {proc.stderr[-300:]}")
    return json.loads(lines[-1][len(MARK):])


def audit(target, budget=200, dims=(2, 10), seeds=3, python=sys.executable, timeout=600):
    cells = []
    for function in i49.FUNCTIONS:
        for d in dims:
            for seed in range(seeds):
                a = fresh_process(target, function, d, seed, budget, True, 1, python, timeout)
                b = fresh_process(target, function, d, seed, budget, False, 2, python, timeout)
                if a.get("error") is None:
                    a["flags"]["D3"] = int(a["hash"] != a["hash_rerun"])
                    a["flags"]["D3x"] = int(b.get("error") is None and a["hash"] != b["hash"])
                cells.append(a)
    ok = [c for c in cells if c.get("error") is None]
    runs = {k: sum(1 for c in ok if c["flags"].get(k)) for k in INTEGRITY + ("C1",)}
    waste = [c["flags"]["C2"] / c["calls"] for c in ok if c["calls"]]
    return dict(target=target, budget=budget, runs=len(cells), errors=[c["error"] for c in cells if c.get("error")],
                integrity={k: runs[k] for k in INTEGRITY if runs[k]}, corner_calls_runs=runs["C1"],
                median_repeated_share=float(np.median(waste)) if waste else None,
                reports_result=bool(ok) and ok[0]["reports_result"], cells=cells)


def report(summary):
    lines = [f"Audited {summary['target']}: {summary['runs']} runs, budget {summary['budget']}."]
    if summary["errors"]:
        lines.append(f"  {len(summary['errors'])} runs failed, e.g. {summary['errors'][0]}")
    if not summary["reports_result"]:
        lines.append("  The optimizer reports no result: R1-R3 not checked.")
    if summary["integrity"]:
        for k, n in summary["integrity"].items():
            lines.append(f"  PROBLEM {k} in {n} runs: {EXPLAIN[k]}")
    else:
        lines.append("  No integrity problem found.")
    if summary["median_repeated_share"]:
        lines.append(f"  Waste: median {100 * summary['median_repeated_share']:.1f}% of evaluations repeat a point.")
    if summary["corner_calls_runs"]:
        lines.append(f"  Info: corner evaluations in {summary['corner_calls_runs']} runs (probe, or legitimate "
                     "clipping: inspect).")
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--cell":
        target, function, d, seed, budget, twice = argv[1:7]
        cell(target, function, int(d), int(seed), int(budget), twice == "1")
        return 0
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("target", help="path/to/module.py:function with signature run(f, lower, upper, budget, seed)")
    parser.add_argument("--budget", type=int, default=200)
    parser.add_argument("--dims", type=int, nargs="+", default=[2, 10])
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--python", default=sys.executable, help="interpreter of the optimizer's environment")
    parser.add_argument("--json", help="also write the full result to this file")
    args = parser.parse_args(argv)
    start = time.monotonic()
    summary = audit(args.target, args.budget, tuple(args.dims), args.seeds, args.python)
    print(report(summary))
    print(f"({time.monotonic() - start:.0f} s)")
    if args.json:
        json.dump(summary, open(args.json, "w"), indent=1)
    return 1 if summary["integrity"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
