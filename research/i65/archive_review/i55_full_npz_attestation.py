#!/usr/bin/env python3
"""Read-only, fail-closed original Git-tree -> NPZ-byte -> I55 trace/flag attestation.

Run only with a FULL Git checkout containing frozen I49/I50/I55 sources and
all archived I55 NPZ traces. Runs no optimizer, power flow or stochastic trial.

    python research/i65/archive_review/i55_full_npz_attestation.py \
      --repo-root . --output i55_full_npz_attestation.json

A report is written even when a provenance gate fails (exit code 2). Do not
claim full source or trace verification without full_attestation_pass=true.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import i55_npz_git_blob_manifest_gate as gate
import i55_npz_cross_archive_verifier as trace

# GitHub main committed this immutable provenance manifest on 2026-11-03.
# The independent *original* source anchor below predates all I65 review work.
PINNED_MANIFEST_GIT_BLOB = "50ca2e96762447070a74309850cb1aa6586d3eb3"
REPORT_SCHEMA = "I65_I55_ORIGINAL_GIT_TREE_TO_620_NPZ_V1"
LS_TREE_RE = re.compile(r"^(100644) blob ([a-f0-9]{40}) +([0-9]+)\t(.+)$")


class AttestationFailure(ValueError):
    """Do not continue to the next evidence level on a provenance failure."""


def _git(repo_root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(["git", "-C", str(repo_root), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, timeout=120)
        return proc.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise AttestationFailure(f"Git read-only query failed ({args[0]}): {exc}") from exc


def load_pinned_manifest(path: Path) -> dict:
    """Authenticate the manifest *itself*, not only the SHA values it declares."""
    raw = path.read_bytes()
    observed = gate.blob_id(raw)
    if observed != PINNED_MANIFEST_GIT_BLOB:
        raise AttestationFailure(f"Untrusted manifest Git blob: {observed}, want {PINNED_MANIFEST_GIT_BLOB}")
    try:
        manifest = json.loads(raw)
        gate.validate_manifest(manifest)
    except (json.JSONDecodeError, gate.ArchiveIndexError) as exc:
        raise AttestationFailure(f"Invalid pinned NPZ manifest: {exc}") from exc
    return manifest


def check_original_commit_tree(repo_root: Path, manifest: dict) -> dict:
    """Compare *all* 620 manifest records with immutable Git tree metadata.

    This catches a tampered manifest + matching tampered working-tree archives,
    even if someone retains the same source-commit SHA as a textual claim.
    No network, checkout, reset, branch move or write is performed.
    """
    gate.validate_manifest(manifest)
    root = Path(repo_root).resolve()
    actual_root = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
    if actual_root != root:
        raise AttestationFailure(f"Repository root mismatch: {actual_root} != {root}")
    tree = _git(root, "rev-parse", f"{gate.SOURCE_COMMIT}^{{tree}}")
    if tree != gate.SOURCE_TREE:
        raise AttestationFailure(f"Original commit root tree changed: {tree} != {gate.SOURCE_TREE}")
    raw = _git(root, "ls-tree", "--full-tree", "-r", "-l", gate.SOURCE_COMMIT,
               "--", gate.BASE)
    observed = {}
    for line in raw.splitlines():
        match = LS_TREE_RE.fullmatch(line)
        if not match:
            raise AttestationFailure(f"Unexpected Git tree record: {line[:150]}")
        _, sha, size, path = match.groups()
        if path in observed:
            raise AttestationFailure(f"Duplicate original Git entry: {path}")
        observed[path] = {"path": path, "git_blob_sha1": sha, "size": int(size)}
    expected = {r["path"]: r for r in manifest["entries"]}
    if set(expected) != set(observed):
        missing = sorted(set(expected) - set(observed))[:5]
        extra = sorted(set(observed) - set(expected))[:5]
        raise AttestationFailure(f"Original Git tree differs: missing={missing}, extra={extra}")
    for path, want in expected.items():
        if observed[path] != want:
            raise AttestationFailure(f"Original Git blob/size mismatch: {path}: "
                                     f"{observed[path]} != {want}")
    return {"source_commit": gate.SOURCE_COMMIT, "original_root_tree_sha1": tree,
            "original_npz_tree_entries": len(observed), "exact_tree_manifest_match": True,
            "method": "git rev-parse + git ls-tree (read-only)"}


def attest(repo_root: Path, manifest_file: Path) -> dict:
    """Never replay traces unless original Git tree and all local bytes pass."""
    result = {"schema": REPORT_SCHEMA, "date": str(date.today()), "read_only": True,
              "optimizer_or_power_flow_executed": False,
              "full_attestation_pass": False,
              "completed_levels": [], "status": "BLOCKED"}
    try:
        manifest = load_pinned_manifest(manifest_file)
        result["manifest_git_blob"] = PINNED_MANIFEST_GIT_BLOB
        result["completed_levels"].append("manifest_sha1_authenticated")
        result["original_git_tree"] = check_original_commit_tree(repo_root, manifest)
        result["completed_levels"].append("original_tree_620_entries_matched")
        local = gate.check_local_bytes(repo_root, manifest)
        result["npz_byte_gate"] = local
        if not local["full_git_blob_pass"]:
            raise AttestationFailure("620-source byte gate failed; NPZ trace replay NOT RUN")
        result["completed_levels"].append("620_local_npz_bytes_verified_against_original_git")
        rerun = trace.audit(repo_root, full_npz=True)
        result["original_trace_replay"] = rerun
        if not rerun["cross_i50_i55"]["matches_frozen_318_358"]:
            raise AttestationFailure("I50/I55 original SHA-256 pair comparison mismatch")
        if not rerun["posthoc_emukit_saved_digest_check"]["all_10_match_i50_and_differ_i55"]:
            raise AttestationFailure("Archived emukit VECLIB post hoc digest control mismatch")
        if not rerun["npz"]["full_raw_trace_pass"] or rerun["npz"]["checked"] != 620:
            raise AttestationFailure("Original 620 NPZ trace/flag replay FAILED or incomplete")
        if not rerun["npz"].get("frozen_objective_values_pass") or \
                rerun["npz"].get("frozen_objective_value_calls_checked", 0) <= 0:
            raise AttestationFailure("Frozen per-call objective-value oracle FAILED or incomplete")
        result["completed_levels"].append("620_trace_sha256_flags_and_objective_values_replayed")
        result["full_attestation_pass"] = True
        result["status"] = "PASS"
        result["limits"] = [
            "Recomputed only the archived A-process numerical traces and detector flags; no fresh runs",
            "Does not independently reproduce A-prime/B traces absent from the NPZ archive",
            "Does not prove general detector specificity, root-cause attribution, novelty or M6/C1 approval",
            "Frozen conclusions H55a-c supported, H55d not supported remain untouched",
        ]
    except Exception as exc:  # fail closed and persist a report for any ordinary audit error
        result["failure"] = {"type": type(exc).__name__, "description": str(exc)}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).with_name(gate.MANIFEST_NAME))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    outcome = attest(args.repo_root, args.manifest)
    document = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document, encoding="utf-8")
    else:
        sys.stdout.write(document)
    return 0 if outcome["full_attestation_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
