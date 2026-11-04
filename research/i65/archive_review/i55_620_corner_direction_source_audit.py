#!/usr/bin/env python3
"""Original I55 A-process full-corner direction and exact-byte repeat audit.

READ ONLY. Requires the already authenticated original 620 NPZ A sources,
their original Git commit/tree/blob manifest and independently pinned
full 620-source attestation. Never calls an optimizer, PF, OPF or COCO.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import i55_620_npz_phase_duplicate_context as phase_audit
import i55_620_flag_census as census
import i55_full_npz_attestation as full
import i55_npz_cross_archive_verifier as trace
import i55_npz_git_blob_manifest_gate as source_gate

SIDES = ("negative", "positive")
STAGES = ("search", "post")
FREQUENCIES = ("first", "repeat")
COLUMNS = tuple(f"{side}_{frequency}_{stage}"
                for side in SIDES for frequency in FREQUENCIES for stage in STAGES)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def zero() -> dict[str, int]:
    return {k: 0 for k in COLUMNS}


def add(into: dict[str, int], by: dict[str, int]) -> None:
    for key in COLUMNS:
        into[key] += by[key]


def count_signed_corners(x: np.ndarray, phases: np.ndarray) -> dict[str, int]:
    """Count original all-minus-five / all-plus-five corners separately.

    "Repeat" means identical original float64 coordinate bytes already
    appeared in this *same* ordered cell. Noncorner rows cannot be exact
    predecessors of a full corner. Phase counts use the CURRENT call.
    """
    require(isinstance(x, np.ndarray) and x.ndim == 2 and
            x.dtype == np.dtype("float64") and x.shape[1] in (2, 10),
            "Invalid original float64 coordinate shape/dimension")
    require(isinstance(phases, np.ndarray) and
            phases.dtype == np.dtype("int8") and phases.shape == (len(x),),
            "Invalid original binary phase dtype/shape")
    require(bool(np.all(np.isfinite(x))), "Original coordinates non-finite")
    require(bool(np.all((phases == 0) | (phases == 1))),
            "Original phase code invalid")
    observed = zero()
    seen_corners = set()
    for row, phase in zip(x, phases):
        negative = bool(np.all(row == -5.0))
        positive = bool(np.all(row == 5.0))
        if not (negative or positive):
            continue
        side = "negative" if negative else "positive"
        stage = "search" if phase == 0 else "post"
        raw = row.tobytes()
        freq = "repeat" if raw in seen_corners else "first"
        observed[f"{side}_{freq}_{stage}"] += 1
        seen_corners.add(raw)
    return observed


def total(part: dict[str, int], *, side=None, frequency=None, stage=None) -> int:
    return sum(v for k, v in part.items()
               if (side is None or k.startswith(side + "_")) and
               (frequency is None or "_" + frequency + "_" in k) and
               (stage is None or k.endswith("_" + stage)))


def analyze(original_repo: Path, attestation_path: Path) -> dict:
    repo = original_repo.resolve()
    frozen = census.audit(repo, attestation_path)
    manifest = full.load_pinned_manifest(
        repo / "research/i65/archive_review" / source_gate.MANIFEST_NAME)
    tree = full.check_original_commit_tree(repo, manifest)
    require(tree["original_root_tree_sha1"] == census.SOURCE_TREE,
            "Original I55 immutable Git tree does not match")
    original_sources = {v["path"]: v for v in manifest["entries"]}
    docs = {lib: trace.read_pinned_json(
        repo / f"research/results/iteration55/cells_{lib}.json", blob)
        for lib, blob in trace.I55_BLOBS.items()}
    overall = zero()
    libraries = {lib: zero() for lib in sorted(docs)}
    functions = {fn: zero() for fn in census.FUNCS}
    dimensions = {str(d): zero() for d in census.DIMS}
    visited = set()
    cells_negative = cells_positive = cells_both = 0
    for lib, doc in sorted(docs.items()):
        require(doc.get("library") == lib and len(doc["cells"]) == 30,
                "Original 30-cell library roster differs")
        for cell in doc["cells"]:
            if cell.get("error") is not None:
                continue
            fn, dim, seed = cell["function"], cell["d"], cell["seed"]
            rel = (f"research/results/iteration55/traces/{lib}/"
                   f"{fn}_{dim}_{seed}.npz")
            require(rel in original_sources and rel not in visited,
                    "Missing/duplicate original NPZ trace: " + rel)
            visited.add(rel)
            path = repo / rel
            raw = path.read_bytes()
            indexed = original_sources[rel]
            require(len(raw) == indexed["size"] and
                    source_gate.blob_id(raw) == indexed["git_blob_sha1"],
                    "Original source NPZ Git blob mismatch: " + rel)
            with np.load(path, allow_pickle=False) as archive:
                x = np.asarray(archive["x"])
                p = np.asarray(archive["phase"])
            corners = count_signed_corners(x, p)
            event = phase_audit.classify(x, p)
            require(total(corners) == cell["flags"]["C1"] and
                    total(corners, frequency="repeat") ==
                    event["C1_C2_search"] + event["C1_C2_post"] and
                    total(corners, stage="search") == event["C1_search"] and
                    total(corners, stage="post") == event["C1_post"],
                    "Signed corner / independently replayed C1/C2 mismatch: " + rel)
            require(event["C2_search"] + event["C2_post"] == cell["flags"]["C2"]
                    and event["calls"] == cell["calls"],
                    "Original frozen C2/call census mismatch: " + rel)
            for dst in (overall, libraries[lib], functions[fn], dimensions[str(dim)]):
                add(dst, corners)
            neg, pos = total(corners, side="negative"), total(corners, side="positive")
            cells_negative += int(neg > 0)
            cells_positive += int(pos > 0)
            cells_both += int(neg > 0 and pos > 0)

    require(len(visited) == 620 and visited == set(original_sources),
            "Original 620 source NPZ population incomplete")
    require(total(overall) == 2105 and
            total(overall, frequency="repeat") == 1956 and
            total(overall, frequency="first") == 149 and
            total(overall, stage="post") == 0,
            "Original 620 C1/sign/repeat census does not match prior source CI")
    expected = {"plateau": (1820, 1746),
                "sphere": (241, 201),
                "rastrigin": (44, 9)}
    for fn, (count, repeats) in expected.items():
        require(total(functions[fn]) == count and
                total(functions[fn], frequency="repeat") == repeats,
                "Original frozen function-context C1 counts differ: " + fn)
    require(sum(total(v) for v in libraries.values()) == total(overall) and
            sum(total(v) for v in functions.values()) == total(overall) and
            sum(total(v) for v in dimensions.values()) == total(overall),
            "Original source stratified C1 counts do not reconcile")
    return {
        "schema": "I65_I55_620_ORIGINAL_A_FULL_CORNER_SIGN_V1",
        "original_commit": census.SOURCE_SHA,
        "original_root_tree": census.SOURCE_TREE,
        "original_manifest_git_blob": census.MANIFEST_SHA,
        "full_original_attestation_sha256": frozen["original_620_full_attestation_sha256"],
        "original_npz_checked": 620,
        "historical_C1_corner_occurrences": total(overall),
        "historical_C1_first": total(overall, frequency="first"),
        "historical_C1_exact_repeats": total(overall, frequency="repeat"),
        "original_C1_post_calls": total(overall, stage="post"),
        "negative_corner_cells": cells_negative,
        "positive_corner_cells": cells_positive,
        "cells_with_both_signs": cells_both,
        "overall_by_sign_repeat_and_phase": overall,
        "by_function": functions,
        "by_dimension": dimensions,
        "by_library": libraries,
        "counting_rule": "All dimensions exactly -5 or exactly +5; exact coordinate byte repeats confined to the same ordered NPZ cell",
        "interpretation": "Descriptive original observed archive geometry, not software defect adjudication, physical validity, or causal attribution",
        "original_A_prime_B_raw_arrays": "NOT_AVAILABLE",
        "original_R_4200_raw_source": "NOT_AVAILABLE",
        "new_optimizer_PF_OPF_COCO_runs": 0,
        "research_status": "DRAFT / NO-FREEZE / NOT_ESTABLISHED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--full-attestation", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(analyze(args.repo_root, args.full_attestation),
                         sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
