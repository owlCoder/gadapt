#!/usr/bin/env python3
"""Read-only Git-blob completeness and byte-integrity gate for 620 I55 NPZ traces.

This gate does not parse the NPZ members or rerun I55 detectors. Pair it with
`i55_npz_cross_archive_verifier.py` for full trace/flag replay AFTER this gate
passes on a full local clone. No optimiser or PF simulation is invoked.

Usage:
 python research/i65/archive_review/i55_npz_git_blob_manifest_gate.py --index-only
 python research/i65/archive_review/i55_npz_git_blob_manifest_gate.py --repo-root . --output i55_npz_gate.json
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BASE = "research/results/iteration55/traces"
SOURCE_COMMIT = "6b56fbc53ffc4d275ecef5e911ea4663474c9a08"
SOURCE_TREE = "f88d221152fcb4157a8e1151a11b53cdfe8180b7"
FUNCTIONS = ("sphere", "rastrigin", "plateau")
DIMENSIONS = (2, 10)
SEEDS = range(6000, 6005)
LIBRARIES = (
    "baybe", "bayes_opt", "bofire", "cma", "cmaes", "deap", "emukit", "evolopy",
    "evotorch", "evox", "geneticalgorithm", "gfo", "nevergrad", "niapy",
    "optuna", "pygad", "pymoo", "pyswarms", "scikit_opt", "scipy_de", "smac",
)
MANIFEST_NAME = "I65_I55_ORIGINAL_620_NPZ_GIT_BLOB_MANIFEST_2026-11-03.json"
SHA40 = re.compile(r"^[a-f0-9]{40}$")


class ArchiveIndexError(ValueError):
    """The manifest does not represent the frozen NPZ experiment."""


def blob_id(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\x00" + content).hexdigest()


def wanted_paths() -> set[str]:
    return {
        f"{BASE}/{library}/{function}_{d}_{seed}.npz"
        for library in LIBRARIES
        for function in FUNCTIONS
        for d in DIMENSIONS
        for seed in SEEDS
        if not (library == "nevergrad" and function in ("sphere", "rastrigin") and d == 10)
    }


def validate_manifest(manifest: dict) -> dict:
    if not isinstance(manifest, dict):
        raise ArchiveIndexError("Manifest root must be object")
    if manifest.get("schema") != "I65_I55_ORIGINAL_NPZ_GIT_TREE_V1":
        raise ArchiveIndexError("Unexpected manifest schema")
    if manifest.get("original_source_commit") != SOURCE_COMMIT or manifest.get("original_source_tree_sha1") != SOURCE_TREE:
        raise ArchiveIndexError("Manifest points to another source commit/tree")
    if manifest.get("original_npz_count") != 620 or manifest.get("total_bytes") != 12319037:
        raise ArchiveIndexError("Original file count or byte total disagrees")
    rows = manifest.get("entries")
    if not isinstance(rows, list) or len(rows) != 620:
        raise ArchiveIndexError("Manifest must enumerate exactly 620 files")
    seen, by_lib, total = set(), Counter(), 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "git_blob_sha1", "size"}:
            raise ArchiveIndexError("Bad entry shape")
        path, sha, size = row["path"], row["git_blob_sha1"], row["size"]
        if not isinstance(path, str) or path in seen:
            raise ArchiveIndexError("Non-string or duplicate path")
        if not isinstance(sha, str) or not SHA40.fullmatch(sha):
            raise ArchiveIndexError("Malformed Git blob SHA-1")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0 or size > 25_000_000:
            raise ArchiveIndexError("Invalid NPZ compressed size")
        seen.add(path)
        by_lib[path.split("/")[4]] += 1
        total += size
    expected = wanted_paths()
    if seen != expected:
        raise ArchiveIndexError(f"Filename roster mismatch: missing={sorted(expected - seen)[:4]} extras={sorted(seen - expected)[:4]}")
    if total != manifest["total_bytes"]:
        raise ArchiveIndexError("NPZ byte total mismatch")
    if len(by_lib) != 21 or by_lib["nevergrad"] != 20 or any(
        v != 30 for lib, v in by_lib.items() if lib != "nevergrad"
    ):
        raise ArchiveIndexError("Per-library source coverage mismatch")
    return {"source_commit": SOURCE_COMMIT, "source_tree": SOURCE_TREE,
            "manifest_files": len(rows), "manifest_bytes": total,
            "library_counts": dict(sorted(by_lib.items())),
            "expected_unavailable_failed_cells": 630 - len(rows)}


def check_local_bytes(repo_root: Path, manifest: dict) -> dict:
    validate_manifest(manifest)
    repo_root = Path(repo_root)
    base = repo_root / BASE
    expected = {item["path"]: item for item in manifest["entries"]}
    observed_paths = {
        x.relative_to(repo_root).as_posix() for x in base.glob("*/*.npz")
    }
    missing = sorted(set(expected) - observed_paths)
    unexpected = sorted(observed_paths - set(expected))
    corrupt = []
    checked = 0
    for path, row in sorted(expected.items()):
        full = repo_root / path
        if path not in observed_paths:
            continue
        content = full.read_bytes()
        actual = blob_id(content)
        if len(content) != row["size"] or actual != row["git_blob_sha1"]:
            corrupt.append({"path": path, "expected_blob": row["git_blob_sha1"],
                            "actual_blob": actual, "expected_bytes": row["size"],
                            "actual_bytes": len(content)})
        checked += 1
    return {"read_only": True, "raw_bytes_verified": checked,
            "expected_npz_files": len(expected), "missing": missing,
            "unexpected": unexpected, "corrupt": corrupt,
            "full_git_blob_pass": checked == 620 and not (missing or unexpected or corrupt),
            "npz_trace_arrays_replayed": False, "detector_flags_recomputed": False}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--manifest", type=Path, default=Path(__file__).with_name(MANIFEST_NAME))
    ap.add_argument("--index-only", action="store_true", help="Validate manifest structure without reading any NPZ bytes")
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    metadata = validate_manifest(manifest)
    if args.index_only:
        outcome = {"manifest_index_validated": True, "local_npz_byte_replay_run": False,
                   "npz_trace_arrays_replayed": False, **metadata}
    else:
        outcome = {"manifest_index_validated": True, "local_npz_byte_replay_run": True,
                   **metadata, **check_local_bytes(args.repo_root, manifest)}
    raw = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(raw, encoding="utf-8")
    else:
        print(raw, end="")
    if not args.index_only and not outcome["full_git_blob_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
