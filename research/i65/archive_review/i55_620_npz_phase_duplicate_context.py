#!/usr/bin/env python3
"""Read-only I55 original-620 NPZ C1/C2 event context by evaluation phase.

Unlike the frozen aggregate cells JSON, this inspects each *original* binary NPZ
coordinate and phase. The original 620-file Git tree/blob identities, trace
SHA256, frozen objective and detector flags are all verified first. No solver,
optimizer, RNG sampler, PF/OPF or COCO evaluation is executed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import i55_620_flag_census as census
import i55_full_npz_attestation as full
import i55_npz_git_blob_manifest_gate as source_gate
import i55_npz_cross_archive_verifier as trace

PHASE = {0: "search", 1: "post"}
KEYS = (
    "calls", "search_calls", "post_calls",
    "C1_search", "C1_post", "C2_search", "C2_post",
    "C1_C2_search", "C1_C2_post",
    "C2_first_search_current_search",
    "C2_first_search_current_post",
    "C2_first_post_current_search",
    "C2_first_post_current_post",
)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def zero() -> dict[str, int]:
    return {key: 0 for key in KEYS}


def accumulate(target: dict, item: dict) -> None:
    for key in KEYS:
        target[key] += item[key]


def classify(x: np.ndarray, phase: np.ndarray) -> dict[str, int]:
    """Reimplement frozen exact-row C1/C2 rules; partition by current phase.

    Duplicate transitions classify by the phase of the *first* occurrence,
    not the immediately previous occurrence. Signed zero remains byte-distinct
    in C2, as required by the original row.tobytes() detector definition.
    """
    require(isinstance(x, np.ndarray) and x.ndim == 2 and
            x.dtype == np.dtype("float64") and x.shape[1] in (2, 10),
            "Original coordinate dtype/dimension invalid")
    require(isinstance(phase, np.ndarray) and phase.dtype == np.dtype("int8")
            and phase.shape == (len(x),), "Original phase dtype/shape invalid")
    require(bool(np.all(np.isfinite(x))), "Original non-finite coordinates")
    require(bool(np.all((phase == 0) | (phase == 1))),
            "Original phase outside search/post binary")
    out = zero()
    seen = {}
    for row, stage in zip(x, phase):
        stage = int(stage)
        label = PHASE[stage]
        out["calls"] += 1
        out[f"{label}_calls"] += 1
        corner = bool(np.all(row == -5.0) or np.all(row == 5.0))
        raw = row.tobytes()
        duplicate = raw in seen
        if corner:
            out[f"C1_{label}"] += 1
        if duplicate:
            out[f"C2_{label}"] += 1
            first_stage = PHASE[seen[raw]]
            out[f"C2_first_{first_stage}_current_{label}"] += 1
        else:
            seen[raw] = stage
        if corner and duplicate:
            out[f"C1_C2_{label}"] += 1
    require(out["C2_search"] + out["C2_post"] ==
            sum(out[k] for k in KEYS if k.startswith("C2_first_")),
            "C2 first/current phase transition counts disagree")
    return out


def analyze(repo: Path, full_attestation: Path) -> dict:
    repo = repo.resolve()
    gate = census.audit(repo, full_attestation)
    manifest = full.load_pinned_manifest(
        repo / "research/i65/archive_review" / source_gate.MANIFEST_NAME
    )
    tree = full.check_original_commit_tree(repo, manifest)
    require(tree["original_root_tree_sha1"] == census.SOURCE_TREE,
            "Original source tree changed")
    original_manifest = {row["path"]: row for row in manifest["entries"]}
    docs = {
        library: trace.read_pinned_json(
            repo / f"research/results/iteration55/cells_{library}.json", sha
        ) for library, sha in trace.I55_BLOBS.items()
    }
    overall = zero()
    by_library = {lib: zero() for lib in sorted(docs)}
    by_function = {fn: zero() for fn in census.FUNCS}
    by_dimension = {str(d): zero() for d in census.DIMS}
    source_covered = set()
    cells_with_C1 = 0
    cells_with_C2 = 0

    for library, doc in sorted(docs.items()):
        require(doc.get("library") == library and len(doc["cells"]) == 30,
                f"Original 30-cell library roster mismatch: {library}")
        for cell in doc["cells"]:
            if cell.get("error") is not None:
                continue
            fn, dim, seed = cell["function"], cell["d"], cell["seed"]
            relative = (f"research/results/iteration55/traces/{library}/"
                        f"{fn}_{dim}_{seed}.npz")
            require(relative in original_manifest and relative not in source_covered,
                    f"Missing/duplicated original source: {relative}")
            source_covered.add(relative)
            path = repo / relative
            row = original_manifest[relative]
            raw = path.read_bytes()
            require(len(raw) == row["size"] and
                    source_gate.blob_id(raw) == row["git_blob_sha1"],
                    f"Original Git NPZ binary identity failed: {relative}")
            check = trace.replay_npz(path, cell)
            require(not check["flag_mismatches"] and
                    check["trace_hash"] == cell["hash"] and
                    check["objective_oracle"]["all_frozen_objective_values_match"],
                    f"Frozen original trace/objective/flag mismatch: {relative}")
            with np.load(path, allow_pickle=False) as npz:
                x = np.asarray(npz["x"])
                p = np.asarray(npz["phase"])
            events = classify(x, p)
            require(events["calls"] == cell["calls"] and
                    events["C1_search"] + events["C1_post"] == cell["flags"]["C1"] and
                    events["C2_search"] + events["C2_post"] == cell["flags"]["C2"] and
                    events["post_calls"] == cell["flags"]["C5"],
                    f"Original raw C1/C2/C5 count mismatch: {relative}")
            for tally in (overall, by_library[library],
                          by_function[fn], by_dimension[str(dim)]):
                accumulate(tally, events)
            cells_with_C1 += int(cell["flags"]["C1"] > 0)
            cells_with_C2 += int(cell["flags"]["C2"] > 0)

    require(source_covered == set(original_manifest) and len(source_covered) == 620,
            "Not every original valid NPZ was independently classified")
    require(overall["calls"] == 295445 and
            overall["C1_search"] + overall["C1_post"] == 2105 and
            overall["C2_search"] + overall["C2_post"] == 18779 and
            overall["post_calls"] == 1200 and
            cells_with_C1 == 109 and cells_with_C2 == 245,
            "Complete raw-source population differs from original cell census")
    require(sum(t["calls"] for t in by_library.values()) == overall["calls"] and
            sum(t["calls"] for t in by_function.values()) == overall["calls"],
            "Independent stratified exposure count mismatch")
    return {
        "schema": "I65_I55_620_ORIGINAL_NPZ_PHASE_C1_C2_CONTEXT_V1",
        "original_commit": census.SOURCE_SHA,
        "source_root_git_tree": census.SOURCE_TREE,
        "frozen_620_manifest_git_blob": census.MANIFEST_SHA,
        "full_attestation_json_sha256": gate["original_620_full_attestation_sha256"],
        "all_original_git_blobs_authenticated_again": True,
        "all_620_original_npz_replayed_again": True,
        "all_frozen_objectives_and_flags_matched_again": True,
        "source_npz_count": len(source_covered),
        "original_historical_valid_calls": overall["calls"],
        "cells_with_C1": cells_with_C1, "cells_with_C2": cells_with_C2,
        "overall": overall, "by_library": by_library,
        "by_function": by_function, "by_dimension": by_dimension,
        "duplicate_first_phase_semantics": "phase of first exact-byte occurrence",
        "C1_geometry": "all coordinates equal -5 OR all coordinates equal +5",
        "C2_equality": "exact NPZ float64 coordinate bytes, not tolerant distance",
        "limits": [
            "The flags are original observations, not adjudicated software defects",
            "Post events are archived evaluations, not new simulated experiments",
            "The phase label does not by itself establish why an optimizer repeated a point",
            "Original A-prime/B raw arrays are missing; I64-R off-Git 4200-run source unrecovered",
            "No causal, inferential, sensitivity, specificity, or novelty claim",
        ],
        "new_optimizer_PF_OPF_COCO_runs": 0,
        "scientific_state": "DRAFT / NO-FREEZE / NOT_ESTABLISHED",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--full-attestation", type=Path, required=True)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    report = analyze(a.repo_root, a.full_attestation)
    data = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if a.output:
        a.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
