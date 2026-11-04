#!/usr/bin/env python3
"""Fail-closed, read-only census of archived I55 A-process detector flags.

Requires a PASS from the *actual original 620-source full-clone attestation*.
Flag counts here are observations, never sensitivity/specificity estimates.
Does not execute optimizers, physical models or COCO tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import i55_npz_cross_archive_verifier as source

FLAGS = ("C1", "C2", "C3", "C4", "C5", "R1", "R2", "R3", "D2")
FUNCS = ("sphere", "rastrigin", "plateau")
DIMS = (2, 10)
SOURCE_SHA = "6b56fbc53ffc4d275ecef5e911ea4663474c9a08"
MANIFEST_SHA = "50ca2e96762447070a74309850cb1aa6586d3eb3"
SOURCE_TREE = "f88d221152fcb4157a8e1151a11b53cdfe8180b7"
PINNED_EVENT_TOTALS = {"C1": 2105, "C2": 18779, "C3": 8474,
                       "C4": 110, "C5": 1200, "R1": 0,
                       "R2": 25, "R3": 11, "D2": 0}
PINNED_FLAGGED_CELLS = {"C1": 109, "C2": 245, "C3": 60,
                        "C4": 10, "C5": 30, "R1": 0,
                        "R2": 25, "R3": 11, "D2": 0}


def require(condition: bool, description: str) -> None:
    if not condition:
        raise ValueError(description)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def empty_tally() -> dict:
    return {
        "valid_cells": 0, "original_calls": 0, "cells_with_any_flag": 0,
        "flag_occurrences": {key: 0 for key in FLAGS},
        "flagged_cells": {key: 0 for key in FLAGS},
    }


def add_cell(tally: dict, cell: dict) -> None:
    tally["valid_cells"] += 1
    tally["original_calls"] += cell["calls"]
    tally["cells_with_any_flag"] += int(any(cell["flags"][k] for k in FLAGS))
    for key in FLAGS:
        tally["flag_occurrences"][key] += cell["flags"][key]
        tally["flagged_cells"][key] += int(cell["flags"][key] > 0)


def check_attestation(att: dict) -> None:
    require(att.get("full_attestation_pass") is True and
            att.get("status") == "PASS", "Original 620 attestation is not PASS")
    require(att.get("manifest_git_blob") == MANIFEST_SHA,
            "Original manifest pin differs")
    git = att.get("original_git_tree", {})
    require(git.get("source_commit") == SOURCE_SHA and
            git.get("original_root_tree_sha1") == SOURCE_TREE and
            git.get("exact_tree_manifest_match") is True,
            "Original source Git tree provenance differs")
    b = att.get("npz_byte_gate", {})
    require(b.get("raw_bytes_verified") == 620 and
            b.get("full_git_blob_pass") is True and
            not b.get("missing") and not b.get("corrupt"),
            "Full original NPZ byte provenance absent")
    n = att.get("original_trace_replay", {}).get("npz", {})
    require(n.get("checked") == 620 and n.get("full_raw_trace_pass") is True and
            n.get("frozen_objective_values_pass") is True and
            n.get("frozen_objective_value_calls_checked") == 295445 and
            n.get("cells_with_flag_difference") == 0 and not n.get("errors"),
            "Full original numerical trace/oracle/flag gate absent")


def census(original_cells: dict[str, dict]) -> dict:
    require(set(original_cells) == set(source.I55_BLOBS),
            "Not all 21 original cell archives present")
    all_tally = empty_tally()
    by_library = {}
    by_function = {name: empty_tally() for name in FUNCS}
    by_dimension = {str(d): empty_tally() for d in DIMS}
    failed = []
    for lib in sorted(source.I55_BLOBS):
        document = original_cells[lib]
        rows = document.get("cells", [])
        require(document.get("library") == lib and len(rows) == 30,
                f"Wrong original library/30-cell roster: {lib}")
        seen = set()
        counter = empty_tally()
        for r in rows:
            fn, d, seed = r.get("function"), r.get("d"), r.get("seed")
            key = (fn, d, seed)
            require(fn in FUNCS and type(d) is int and d in DIMS and
                    type(seed) is int and seed in range(6000, 6005) and
                    key not in seen, f"Invalid/duplicate I55 cell: {lib}:{key}")
            seen.add(key)
            if r.get("error") is not None:
                failed.append({"library": lib, "function": fn, "d": d,
                               "seed": seed, "error": str(r["error"])})
                continue
            require(type(r.get("calls")) is int and r["calls"] > 0 and
                    re.fullmatch(r"[a-f0-9]{64}", str(r.get("hash"))) is not None,
                    f"Invalid physical-call or original trace hash: {lib}:{key}")
            flags = r.get("flags")
            require(isinstance(flags, dict) and set(flags) == set(FLAGS) and
                    all(type(flags[k]) is int and flags[k] >= 0 for k in FLAGS),
                    f"Invalid detector flag map: {lib}:{key}")
            for counter_ref in (all_tally, counter, by_function[fn], by_dimension[str(d)]):
                add_cell(counter_ref, r)
        require(len(seen) == 30, f"Original library roster incomplete: {lib}")
        by_library[lib] = counter

    require(all_tally["valid_cells"] == 620 and
            all_tally["original_calls"] == 295445 and len(failed) == 10,
            "620-source objective-call ledger mismatch")
    require(all(f["library"] == "nevergrad" and f["d"] == 10 and
                f["function"] in ("sphere", "rastrigin") for f in failed),
            "Historical unsuccessful cell population changed")
    require(all_tally["flag_occurrences"] == PINNED_EVENT_TOTALS and
            all_tally["flagged_cells"] == PINNED_FLAGGED_CELLS,
            "Frozen population flag totals mismatch")
    return {
        "schema": "I65_I55_ORIGINAL_A_PROCESS_620_FLAG_CENSUS_V1",
        "original_source_commit": SOURCE_SHA,
        "original_manifest_git_blob": MANIFEST_SHA,
        "original_git_tree": SOURCE_TREE,
        "original_cells_json_blobs": dict(sorted(source.I55_BLOBS.items())),
        "original_cells_total": 630,
        "original_cells_failed": len(failed),
        "historical_failed_cells": failed,
        "overall": all_tally, "by_library": by_library,
        "by_function": by_function, "by_dimension": by_dimension,
        "read_only": True, "new_optimizer_pf_coco_runs": 0,
        "limits": [
            "Counts summarize frozen A-process detector observations, not adjudicated defects",
            "Flag occurrence totals and counts of flagged cells have different denominators",
            "Flags overlap; do not sum them as independent events or use them to infer detector specificity",
            "Requires separately authenticated full original 620 raw NPZ replay; this tool reads original cell JSON",
            "A-prime/B raw arrays, I64-R off-Git source and M6/C1 originality signoff remain unresolved",
            "Scientific state DRAFT / NO-FREEZE / NOT_ESTABLISHED",
        ],
    }


def audit(repo: Path, full_attestation: Path) -> dict:
    data = full_attestation.read_bytes()
    check_attestation(json.loads(data))
    original = {}
    for lib, sha in source.I55_BLOBS.items():
        p = repo / "research" / "results" / "iteration55" / f"cells_{lib}.json"
        raw = p.read_bytes()
        require(git_blob(raw) == sha, f"Original cell JSON blob changed: {lib}")
        original[lib] = json.loads(raw)
    out = census(original)
    out["original_620_full_attestation_sha256"] = hashlib.sha256(data).hexdigest()
    out["original_620_full_attestation_gate_pass"] = True
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--full-attestation", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    out = audit(args.repo_root.resolve(), args.full_attestation)
    document = json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(document, encoding="utf-8")
    else:
        print(document, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
