#!/usr/bin/env python3
"""Explicit opt-in, no-optimizer, two-PF-entrypoint PYPOWER dev smoke.

Run ONLY after real full-clone 341-path restore. No GA execution, no COCO,
no repeated seeds, no held-out instances, and no confirmation experiments.
An API entrypoint attempt is not the same as an internal numerical iteration.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESEARCH = REPO / "research"
if not (RESEARCH / "iteration58_validation.py").is_symlink():
    raise SystemExit("BLOCKED: restore historic research root symlinks first")
sys.path.insert(0, str(RESEARCH))
sys.path.insert(0, str(HERE))

import iteration56_cht_study as i56
import iteration58_validation as i58
from orpd_solver_entry_audit import SolverEntryAudit


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def main() -> int:
    # Scenario is deliberately a previous-development, non-held-out I58 case.
    network, scenario_index = "case30", 1
    audit = SolverEntryAudit()
    with audit.trace():
        with audit.phase("setup"):
            problem = i58.make_problem(network, scenario_index)
        x = problem.snap((problem.lo + problem.hi) / 2.0)
        with audit.phase("search"):
            evaluator = i56.Evaluator(problem, budget=2,
                                      target=lambda cost: False)
            evaluator(x)
        with audit.phase("witness"):
            # I58 independently reconstructs raw-case arrays and constraints,
            # but REUSES PYPOWER; it is NOT an independent AC solver model.
            witness = i58.independent_check(network, scenario_index, x)

    e = audit.evidence()
    expected = {"setup": {"runopf": 1, "runpf": 0},
                "search": {"runopf": 0, "runpf": 1},
                "witness": {"runopf": 1, "runpf": 1}}
    problems = []
    if e["phases"] != expected:
        problems.append("solver entrypoints != expected phase schedule")
    if evaluator.calls != 1:
        problems.append("admitted Python objective attempts != 1")
    if not isinstance(witness, dict) or not witness.get("valid", False):
        problems.append("I58 witness rejected the exact original candidate")
    # A valid candidate and actual PF attempt do not imply PF convergence or
    # feasible solution; those are separately reported rather than asserted.
    manifest = {"status": "PASS" if not problems else "FAIL",
                "scenario": {"network": network, "index": scenario_index,
                             "resolution": int(problem.resolution)},
                "python": platform.python_version(),
                "numpy": np.__version__,
                "source_git_blobs": {
                    "orpd": git_blob(RESEARCH / "legacy/flat/iteration56_orpd.py"),
                    "evaluator": git_blob(RESEARCH / "legacy/flat/iteration56_cht_study.py"),
                    "witness": git_blob(RESEARCH / "legacy/flat/iteration58_validation.py"),
                    "audit": git_blob(HERE / "orpd_solver_entry_audit.py")},
                "objective_admitted_calls": evaluator.calls,
                "witness_valid_vector": bool(witness.get("valid", False)) if isinstance(witness, dict) else False,
                "witness_converged": bool(witness.get("converged", False)) if isinstance(witness, dict) else False,
                "audited_api_entries": e,
                "errors": problems,
                "interpretation": "PYPOWER API entrypoint attempts only; not internal solver steps or independent physical oracle"}
    print(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
