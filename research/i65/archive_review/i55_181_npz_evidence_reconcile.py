#!/usr/bin/env python3
"""Fail-closed, read-only audit of the 181 original I55 NPZ replay witnesses.

This reconciles previously archived 55 replay sources with 126 additional
original NPZ replay reports, across 21 original libraries, and independently
cross-checks the declared source Git identities, original frozen cell metadata,
call counts, SHA-256 transcript digests and every C/R/D2 detector flag.

It does NOT load all 620 raw NPZs. It verifies the *archived replay witnesses*,
not an independent second execution of the original raw objective computation.
No optimizer, PF, AC OPF or held-out COCO is executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path("research/i65/archive_review")
BASE = "research/results/iteration55/traces/"
INDEX = "I65_I55_FIFTY_ORIGINAL_NPZ_REPLAY_INDEX_2026-11-03.json"
INDEX_SHA = "1418207f25a3745c4caacdd2fdb63359dc227b04"
MANIFEST = "I65_I55_ORIGINAL_620_NPZ_GIT_BLOB_MANIFEST_2026-11-03.json"
MANIFEST_SHA = "50ca2e96762447070a74309850cb1aa6586d3eb3"
SOURCE_SHA = "6b56fbc53ffc4d275ecef5e911ea4663474c9a08"
ENGINE_SHA = "076ac19beef2514eef9985c86eac071ca9975b8d"
BATCH_PATTERN = "I65_I55_NEXT_126_NPZ_BATCH_{:02d}_2026-11-04.json"
NEXT_INDEX = "I65_I55_NEXT_126_SOURCE_REPLAY_INDEX_2026-11-04.json"
NEXT_INDEX_SHA = "63d02f2e03483babe67f95adc9414dc886c5b12f"
CELL_PATTERN = re.compile(r"^research/results/iteration55/traces/([a-z0-9_]+)/(sphere|rastrigin|plateau)_(2|10)_(600[0-4])\.npz$")
EXPECTED_LIBRARIES = frozenset((
    "baybe", "bayes_opt", "bofire", "cma", "cmaes", "deap", "emukit",
    "evolopy", "evotorch", "evox", "geneticalgorithm", "gfo", "nevergrad",
    "niapy", "optuna", "pygad", "pymoo", "pyswarms", "scikit_opt",
    "scipy_de", "smac",
))


class ReconciliationError(ValueError):
    """Any failure prevents a PASS declaration."""


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ReconciliationError(reason)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def read_pinned_json(path: Path, git_sha: str) -> Any:
    raw = path.read_bytes()
    require(git_blob(raw) == git_sha, f"Frozen Git JSON identity changed: {path}")
    return json.loads(raw)


def reconcile(
    manifest: dict,
    earlier: dict,
    batches: list[dict],
    original_cells: dict[str, dict],
    *,
    expected_libraries: frozenset[str] = EXPECTED_LIBRARIES,
    per_library: int = 6,
    original_total: int = 620,
    expected_prior_count: int = 55,
    expected_prior_calls: int = 24298,
) -> dict:
    """Check all provenance and scientific invariants against frozen metadata.

    Synthetic fixtures can vary counts; the CLI uses the strictly pinned real
    source identities, 21 libraries, 55+126 archival replays, 620 original NPZ.
    """
    require(manifest.get("original_source_commit") == SOURCE_SHA, "Wrong original source commit")
    require(manifest.get("schema") == "I65_I55_ORIGINAL_NPZ_GIT_TREE_V1", "Wrong original manifest schema")
    entries = manifest.get("entries", [])
    require(len(entries) == original_total, "Original NPZ roster count changed")
    original = {e["path"]: e for e in entries}
    require(len(original) == len(entries), "Original manifest has duplicated paths")
    require(earlier.get("new_valid_npz") == 50 and earlier.get("prior_original_npz_replayed") == 5,
            "Frozen preceding replay count not 5+50")
    require(earlier.get("cumulative_original_evaluations_recomputed") == expected_prior_calls,
            "Original prior objective-evaluation total changed")
    before = earlier.get("prior_five_source_paths", []) + earlier.get("new_fifty_source_paths", [])
    require(len(before) == expected_prior_count and len(set(before)) == expected_prior_count,
            "Original 55 replay sources have duplicate or missing paths")
    require(all(p in original for p in before), "Preexisting replay source outside original frozen manifest")
    require(len(batches) == len(expected_libraries), "Missing or extra 126-source batch")
    require(set(original_cells) == set(expected_libraries), "Original library metadata roster mismatch")
    require(set(b["batch_library"] for b in batches) == expected_libraries,
            "Wrong or duplicate original library batch")

    lookup = {}
    for library in expected_libraries:
        cells = original_cells[library].get("cells", [])
        rows = {(r["function"], int(r["d"]), int(r["seed"])): r for r in cells}
        require(len(rows) == len(cells) == 30, f"Frozen 30-cell library roster broken: {library}")
        lookup[library] = rows

    seen = set(before)
    new_paths = []
    new_calls = new_bytes = new_float32_calls = raw_wrong_float64_rejections = 0
    by_library = {}
    batch_ids = set()
    flag_totals = {key: 0 for key in ("C1", "C2", "C3", "C4", "C5", "R1", "R2", "R3", "D2")}
    for batch in batches:
        library = batch["batch_library"]
        batch_id = batch.get("iteration_batch")
        require(isinstance(batch_id, int) and 1 <= batch_id <= len(expected_libraries) and batch_id not in batch_ids,
                f"Wrong duplicate / missing batch ID: {batch_id}")
        batch_ids.add(batch_id)
        require(batch.get("original_commit") == SOURCE_SHA, f"Batch {batch_id} source commit changed")
        require(batch.get("manifest_blob") == MANIFEST_SHA, f"Batch {batch_id} source manifest changed")
        require(batch.get("engine_git_blob") == ENGINE_SHA, f"Batch {batch_id} replay engine changed")
        require(batch.get("replayed") == per_library and batch.get("failed") == 0 and
                batch.get("files_requested") == per_library, f"Batch {batch_id} not completely reproduced")
        require(batch.get("no_new_optimizers") is True and batch.get("full_original_620_replayed") is False,
                f"Batch {batch_id} experimental-scope field changed")
        records = batch["results"]
        require(len(records) == per_library, f"Batch {batch_id} result count changed")
        calls = size = float32_calls = 0
        funcs = {"sphere": 0, "rastrigin": 0, "plateau": 0}
        for record in records:
            path = record["path"]
            match = CELL_PATTERN.fullmatch(path)
            require(match is not None, f"Illegal frozen-source path: {path}")
            lib, fn, d, seed = match.groups()
            require(lib == library and path not in seen and path in original,
                    f"Duplicate, wrong library or non-original source: {path}")
            seen.add(path)
            new_paths.append(path)
            funcs[fn] += 1
            old_blob = original[path]
            require(record["source_git_blob_sha1"] == old_blob["git_blob_sha1"] and
                    record["source_binary_size"] == old_blob["size"], f"NPZ original blob mismatch: {path}")
            frozen = lookup[library][(fn, int(d), int(seed))]
            require(frozen["error"] is None, f"Falsely passing an original failed cell: {path}")
            require(record["pass"] is True and record["trace_sha256_match"] is True and
                    record["recomputed_flags_match"] is True and record["objective_mismatches"] == 0,
                    f"A numerical or detector replay failed: {path}")
            require(record["archived_trace_sha256"] == record["recomputed_trace_sha256"] == frozen["hash"],
                    f"Raw sequence SHA256 does not match original cell JSON: {path}")
            require(record["original_flag_counts"] == frozen["flags"],
                    f"Original C/R/D2 detector flag counts changed: {path}")
            n = record["objective_calls_rechecked"]
            require(type(n) is int and n > 0 and n == frozen["calls"],
                    f"Physical objective call count changed: {path}")
            require(record["float32_recorder"] is (library in {"evox", "evotorch"}),
                    f"Incorrect recorded numeric precision: {path}")
            require(record["float64_wrong_policy_rejections"] >= 0,
                    f"Invalid counter of incorrectly rejected values: {path}")
            calls += n
            size += record["source_binary_size"]
            if record["float32_recorder"]:
                float32_calls += n
            raw_wrong_float64_rejections += record["float64_wrong_policy_rejections"]
            for key in flag_totals:
                flag_totals[key] += record["original_flag_counts"][key]
        require(batch.get("objective_calls") == calls, f"Incorrect original call aggregate in batch {batch_id}")
        require(batch.get("float32_calls") == float32_calls, f"Wrong float32 sum in batch {batch_id}")
        require(batch.get("float64_wrong_policy_rejections") ==
                sum(r["float64_wrong_policy_rejections"] for r in records),
                f"Wrong float32-vs-float64 policy summary in batch {batch_id}")
        require(all(funcs[fn] >= 1 for fn in funcs), f"Missing source test function: {library}")
        by_library[library] = {"new_npz": len(records), "source_objective_calls": calls,
                               "compressed_bytes": size, "functions": funcs}
        new_calls += calls
        new_bytes += size
        new_float32_calls += float32_calls
    require(batch_ids == set(range(1, len(batches) + 1)), "Batch identifier roster has a gap")
    require(len(new_paths) == len(expected_libraries) * per_library and len(seen) ==
            expected_prior_count + len(new_paths), "New NPZ sources are not all distinct")
    require(len(seen) <= original_total, "More source witnesses than original successful NPZ")
    return {
        "schema": "I65_I55_181_ARCHIVED_ORIGINAL_NPZ_WITNESS_RECONCILIATION_V1",
        "source_original_commit": SOURCE_SHA,
        "manifest_git_blob": MANIFEST_SHA,
        "prior_index_git_blob": INDEX_SHA,
        "replay_engine_git_blob": ENGINE_SHA,
        "read_only": True, "new_optimization_or_pf_or_coco_runs": 0,
        "reconciliation_pass": True,
        "new_library_batches": len(batches),
        "libraries_covered": len(expected_libraries),
        "prior_replays": expected_prior_count,
        "new_replays": len(new_paths),
        "original_replayed_cumulative": len(seen),
        "original_evaluable_total": original_total,
        "original_unreplayed": original_total-len(seen),
        "prior_original_calls": expected_prior_calls,
        "new_original_calls": new_calls,
        "original_calls_cumulative": expected_prior_calls + new_calls,
        "new_npz_binary_bytes": new_bytes,
        "new_float32_objective_calls": new_float32_calls,
        "wrong_float64_policy_false_rejections": raw_wrong_float64_rejections,
        "flag_occurrences_in_new_replays": flag_totals,
        "by_library": dict(sorted(by_library.items())),
        "new_source_paths": sorted(new_paths),
        "full_original_620_attestation": False,
        "limits": [
            "This reconciles archived raw replay WITNESSES; it does not re-read all NPZ bytes a second time",
            "Only A-process NPZ raw arrays were archived, not the A-prime or B raw arrays",
            "Remaining original raw traces and independent detector specificity are not closed",
            "I64-R off-Git 4200-run raw source and signed M6/C1 remain pending",
            "No novelty, full freeze or held-out COCO result is implied",
        ],
    }



def load_pinned_batches(
    archive: Path,
    earlier: dict,
    *,
    index_sha: str = NEXT_INDEX_SHA,
    expected_libraries: frozenset[str] = EXPECTED_LIBRARIES,
    per_library: int = 6,
) -> tuple[dict, list[dict]]:
    """Authenticate all 21 published evidence JSON blobs BEFORE reconciliation.

    The previous reconciler authenticated its manifest, prior index and original
    cell metadata but parsed new batch JSON without comparing its raw Git identity
    with the immutable 126-source index. That left unchecked fields in a modified
    batch outside the integrity gate. Index pinning closes that gap.
    """
    index = read_pinned_json(archive / NEXT_INDEX, index_sha)
    require(index.get("schema") == "I65_I55_NEXT_126_SOURCE_REPLAY_INDEX_V1",
            "Wrong 126-source index schema")
    require(index.get("original_source_commit") == SOURCE_SHA and
            index.get("frozen_620_manifest_blob") == MANIFEST_SHA and
            index.get("prior_55_index_blob") == INDEX_SHA and
            index.get("replay_engine_blob") == ENGINE_SHA,
            "126-source index provenance mismatch")
    witnesses = index.get("per_library_witnesses")
    require(isinstance(witnesses, list) and len(witnesses) == len(expected_libraries),
            "Missing or extra indexed batch identities")
    require(index.get("new_replay_witnesses") == len(expected_libraries) * per_library and
            index.get("new_original_eligible_libraries") == len(expected_libraries),
            "126-source index count mismatch")

    prior = earlier.get("prior_five_source_paths", []) + earlier.get("new_fifty_source_paths", [])
    require(len(prior) == len(set(prior)) and
            len(index.get("old_55_source_paths", [])) == len(prior) and
            set(index["old_55_source_paths"]) == set(prior),
            "Indexed prior-55 source roster mismatch")
    require(index.get("prior_original_raw_replay_witnesses") == len(prior) and
            index.get("prior_objective_evaluations") ==
            earlier.get("cumulative_original_evaluations_recomputed"),
            "126-source index prior numerical ledger mismatch")

    batches = []
    observed_paths = []
    total_calls = total_bytes = 0
    observed_libraries = set()
    for ordinal, evidence in enumerate(witnesses, 1):
        library = evidence.get("library")
        path = str(ROOT / BATCH_PATTERN.format(ordinal))
        require(evidence.get("batch_id") == ordinal and evidence.get("path") == path and
                library in expected_libraries and library not in observed_libraries,
                f"Indexed batch order, path or ownership mismatch: {ordinal}")
        observed_libraries.add(library)
        sha = evidence.get("git_blob_sha1")
        require(isinstance(sha, str) and re.fullmatch(r"[a-f0-9]{40}", sha) is not None,
                f"Missing indexed Git blob identity: {ordinal}")
        batch = read_pinned_json(archive / BATCH_PATTERN.format(ordinal), sha)
        require(batch.get("iteration_batch") == ordinal and
                batch.get("batch_library") == library,
                f"Batch ownership differs from indexed identity: {ordinal}")
        rows = batch.get("results")
        require(isinstance(rows, list) and len(rows) == per_library and
                evidence.get("source_npz") == len(rows), f"Indexed row count mismatch: {ordinal}")
        calls = sum(r["objective_calls_rechecked"] for r in rows)
        size = sum(r["source_binary_size"] for r in rows)
        require(calls == evidence.get("objective_calls") == batch.get("objective_calls") and
                size == evidence.get("compressed_source_bytes"),
                f"Indexed batch numerical totals differ: {ordinal}")
        observed_paths.extend(r["path"] for r in rows)
        total_calls += calls
        total_bytes += size
        batches.append(batch)
    require(observed_libraries == expected_libraries, "Indexed library roster mismatch")
    require(len(observed_paths) == len(set(observed_paths)) and
            len(index.get("new_npz_source_paths", [])) == len(observed_paths) and
            set(index["new_npz_source_paths"]) == set(observed_paths) and
            not set(observed_paths).intersection(prior),
            "Indexed NPZ path roster mismatch")
    require(index.get("new_original_evaluations") == total_calls and
            index.get("new_compressed_binary_bytes") == total_bytes and
            index.get("total_original_evaluations_recomputed") ==
            index["prior_objective_evaluations"] + total_calls and
            index.get("total_raw_replay_witnesses") == len(prior) + len(observed_paths) and
            index.get("remaining_raw_npz_unreplayed") ==
            index.get("original_total_valid_npz", 0) - len(prior) - len(observed_paths) and
            index.get("number_new_failed_raw_replays") == 0,
            "126-source index aggregate or coverage mismatch")
    return index, batches


def audit_full_checkout(repo_root: Path) -> dict:
    archive = repo_root / ROOT
    manifest = read_pinned_json(archive / MANIFEST, MANIFEST_SHA)
    earlier = read_pinned_json(archive / INDEX, INDEX_SHA)
    # Pinned 21 original cell metadata blobs are frozen in the pre-existing
    # independent cross-archive reader, not inferred from current reports.
    import i55_npz_cross_archive_verifier as frozen
    original_cells = {
        lib: read_pinned_json(repo_root / "research" / "results" / "iteration55" / f"cells_{lib}.json", sha)
        for lib, sha in frozen.I55_BLOBS.items()
    }
    new_index, batches = load_pinned_batches(archive, earlier)
    out = reconcile(manifest, earlier, batches, original_cells)
    out["new_126_index_git_blob"] = NEXT_INDEX_SHA
    out["all_21_new_batch_git_blobs_authenticated"] = True
    require(out["original_replayed_cumulative"] == 181 and out["original_unreplayed"] == 439,
            "Unexpected total replay coverage")
    require(out["new_original_calls"] == 61152 and out["original_calls_cumulative"] == 85450,
            "Unexpected objective-call ledger aggregate")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--output", type=Path)
    a = p.parse_args(argv)
    try:
        result = audit_full_checkout(a.repo_root.resolve())
        exit_code = 0
    except Exception as exc:
        result = {"schema": "I65_I55_181_ARCHIVED_ORIGINAL_NPZ_WITNESS_RECONCILIATION_V1",
                  "reconciliation_pass": False,
                  "failure": {"type": type(exc).__name__, "description": str(exc)}}
        exit_code = 2
    document = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(document, encoding="utf-8")
    else:
        sys.stdout.write(document)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
