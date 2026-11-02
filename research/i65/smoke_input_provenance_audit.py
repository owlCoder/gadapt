#!/usr/bin/env python3
"""I65 public case30 input lineage, one setup OPF, zero candidate PF.

No search and no COCO. Detects every unauthorized mutation among source,
scenario replay, OPF dispatch handoff and fixed midpoint control case.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path
import platform
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
if not (RESEARCH / "iteration58_validation.py").is_symlink():
    raise SystemExit("BLOCKED: full legacy-root alias restoration required")
sys.path.insert(0, str(RESEARCH))
sys.path.insert(0, str(HERE))

from pypower import api
import iteration56_cht_study as i56
import iteration58_validation as i58
from input_provenance_audit import audit_data_lineage, numeric_fingerprint
from orpd_solver_entry_audit import SolverEntryAudit


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git_blob(p):
    data = Path(p).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def clone_case(c):
    return {k: (v.copy() if isinstance(v, np.ndarray) else v)
            for k, v in c.items()}


def main():
    name, j = "case30", 1
    factor, seed = i58.SCENARIOS[j]
    raw = api.case30()
    # Reconstruction from the documented RandomState recipe: NOT a captured
    # independent pre-OPF snapshot, as frozen I56 does not expose that state.
    reconstructed_scaled = clone_case(raw)
    rng = np.random.RandomState(seed)
    scale = factor * (1 + i56.SPREAD * (2 * rng.random_sample(len(raw["bus"])) - 1))
    reconstructed_scaled["bus"][:, 2] *= scale
    reconstructed_scaled["bus"][:, 3] *= scale

    meter = SolverEntryAudit()
    with meter.trace():
        with meter.phase("setup"):
            problem = i58.make_problem(name, j)
    d = problem.delegate
    post_opf = clone_case(d.base)
    x = problem.snap((problem.lo + problem.hi) / 2)
    groups = len(problem.bus_groups)
    controls = d.snap(np.concatenate([x[:groups][problem.expand], x[groups:]]))
    ng, nt = len(d.gen_rows), len(d.tap_rows)
    controlled = clone_case(post_opf)
    controlled["gen"][d.gen_rows, 5] = controls[:ng]
    controlled["branch"][d.tap_rows, 8] = controls[ng:ng + nt]
    controlled["bus"][d.shunt_rows, 5] = controls[ng + nt:]
    lineage = audit_data_lineage(
        raw, reconstructed_scaled, post_opf, controlled,
        load_factor=factor, spread=i56.SPREAD, seed=seed,
        gen_rows=d.gen_rows, tap_rows=d.tap_rows,
        shunt_rows=d.shunt_rows, control_values=controls)
    case_source = inspect.getsourcefile(api.case30)
    if not case_source:
        raise RuntimeError("no exact installed PYPOWER case30 source filename")
    alternate = getattr(api, "case_ieee30", None)
    alt_hash = numeric_fingerprint(alternate()) if alternate else None
    if alt_hash is not None and alt_hash == lineage["stages"]["raw"]:
        raise RuntimeError("unexpected same raw case30/case_ieee30 numeric data")
    entries = meter.evidence()
    expected = {"setup":{"runopf":1,"runpf":0},
                "search":{"runopf":0,"runpf":0},
                "witness":{"runopf":0,"runpf":0}}
    problems = []
    if entries["phases"] != expected:
        problems.append("unplanned OPF/PF entrypoints")
    if tuple(raw["bus"].shape)[0] != 30 or tuple(raw["gen"].shape)[0] != 6:
        problems.append("case30 unexpected bus/gen count")
    if not np.array_equal(post_opf["bus"][:, 2:4],
                          reconstructed_scaled["bus"][:, 2:4]):
        problems.append("original scenario differs from explicit scale replay")
    model = {
        "source_name":"pypower.api.case30",
        "installed_pypower_version":importlib.metadata.version("PYPOWER"),
        "installed_case_source_basename":Path(case_source).name,
        "installed_case_source_sha256":sha_file(case_source),
        "case30_raw_fingerprint":lineage["stages"]["raw"],
        "case_ieee30_installed_fingerprint_if_available":alt_hash,
        "case30_is_not_identical_to_case_ieee30":(
            alt_hash != lineage["stages"]["raw"] if alt_hash else None),
        "licensing_note":"PYPOWER case data are excluded from PYPOWER BSD software license; do not relicense case contents",
        "physical_status":"transformed academic benchmark, not independent field measurement",
    }
    print(json.dumps({
        "status":"PASS" if not problems else "FAIL",
        "case":{"network":name,"j":j,"resolution":i58.RESOLUTION,
                "load_factor":factor,"spread":i56.SPREAD,"seed":seed},
        "runtime":{"python":platform.python_version(),"numpy":np.__version__},
        "model_provenance":model,
        "transformation":lineage,
        "api_entrypoints":entries,
        "source_git_blobs":{
            "original_i56":git_blob(RESEARCH/"legacy/flat/iteration56_orpd.py"),
            "original_i58":git_blob(RESEARCH/"legacy/flat/iteration58_validation.py"),
            "original_i56_study":git_blob(RESEARCH/"legacy/flat/iteration56_cht_study.py"),
            "audit":git_blob(HERE/"input_provenance_audit.py"),
        },
        "errors":problems,
        "scope":"single historical development case with one OPF setup; no candidate evaluation or independent physical source",
    }, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
