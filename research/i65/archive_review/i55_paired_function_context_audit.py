#!/usr/bin/env python3
"""Read-only matched FUNCTION comparison of archived I55 original A-process flags.

Pair within library × dimension × seed, never treat calls or seeds as IID.
Requires already completed full 620-original raw NPZ attestation and pinned
original 21 JSON cell blobs; produces descriptive evidence, NOT diagnosis,
confidence intervals, hypothesis tests, or new optimization evaluations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import i55_620_flag_census as base

FLAGS = ("C1", "C2")
CONTRASTS = (("plateau", "sphere"), ("plateau", "rastrigin"),
             ("sphere", "rastrigin"))


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def empty():
    return {
        "pairs": 0, "left_present": 0, "right_present": 0,
        "left_only": 0, "right_only": 0, "both_present": 0,
        "neither_present": 0, "left_events": 0, "right_events": 0,
        "left_original_calls": 0, "right_original_calls": 0,
    }


def update(tally, left, right, flag):
    a, b = left["flags"][flag] > 0, right["flags"][flag] > 0
    tally["pairs"] += 1
    tally["left_present"] += int(a)
    tally["right_present"] += int(b)
    tally["left_only"] += int(a and not b)
    tally["right_only"] += int(b and not a)
    tally["both_present"] += int(a and b)
    tally["neither_present"] += int(not a and not b)
    tally["left_events"] += left["flags"][flag]
    tally["right_events"] += right["flags"][flag]
    tally["left_original_calls"] += left["calls"]
    tally["right_original_calls"] += right["calls"]


def paired_comparison(documents):
    """Pure deterministic comparison, with named strata and no inferential test."""
    overall = {flag: {f"{a}_vs_{b}": empty() for a, b in CONTRASTS}
               for flag in FLAGS}
    by_library = {}
    by_dimension = {str(d): {flag: {f"{a}_vs_{b}": empty() for a,b in CONTRASTS}
                             for flag in FLAGS} for d in base.DIMS}
    skipped = []
    complete = 0
    for library, doc in sorted(documents.items()):
        index = {}
        for r in doc["cells"]:
            k = (r["function"], r["d"], r["seed"])
            require(k not in index, f"Duplicate library/function/dimension/seed: {library}:{k}")
            index[k] = r
        local = {flag: {f"{a}_vs_{b}": empty() for a, b in CONTRASTS}
                 for flag in FLAGS}
        for dim in base.DIMS:
            for seed in range(6000, 6005):
                rows = {f: index.get((f, dim, seed)) for f in base.FUNCS}
                require(all(x is not None for x in rows.values()),
                        f"Missing nominal source cell for {library}/{dim}/{seed}")
                complete += int(all(x.get("error") is None for x in rows.values()))
                if any(x.get("error") is not None for x in rows.values()):
                    skipped.append({
                        "library": library, "dimension": dim, "seed": seed,
                        "failed_functions": [f for f, x in rows.items()
                                             if x.get("error") is not None],
                    })
                for a, b in CONTRASTS:
                    left, right = rows[a], rows[b]
                    if left.get("error") is not None or right.get("error") is not None:
                        continue
                    key = f"{a}_vs_{b}"
                    for flag in FLAGS:
                        update(local[flag][key], left, right, flag)
                        update(overall[flag][key], left, right, flag)
                        update(by_dimension[str(dim)][flag][key], left, right, flag)
        by_library[library] = local
    library_directions = {}
    for flag in FLAGS:
        library_directions[flag] = {}
        for a,b in CONTRASTS:
            key = f"{a}_vs_{b}"
            pos = []; neg = []; tied = []
            for library, results in sorted(by_library.items()):
                tally = results[flag][key]
                balance = tally["left_only"] - tally["right_only"]
                (pos if balance > 0 else neg if balance < 0 else tied).append(library)
            library_directions[flag][key] = {
                "more_left_flagged_cells": pos,
                "more_right_flagged_cells": neg,
                "equal_flagged_cell_counts": tied,
            }
    for group in [*overall.values(), *(by_dimension[d][f] for d in by_dimension
                                             for f in FLAGS),
                  *(by_library[lib][f] for lib in by_library for f in FLAGS)]:
        for tally in group.values():
            require(tally["pairs"] == (tally["left_only"]+tally["right_only"]+
                        tally["both_present"]+tally["neither_present"]),
                    "Internal paired 2x2 tally mismatch")
            require(tally["left_present"] == tally["left_only"]+tally["both_present"] and
                    tally["right_present"] == tally["right_only"]+tally["both_present"],
                    "Internal paired prevalence mismatch")
    return {
        "complete_three_function_strata": complete,
        "nominal_strata": len(documents)*len(base.DIMS)*5,
        "incomplete_strata": skipped,
        "overall_matched": overall,
        "matched_by_library": by_library,
        "matched_by_dimension": by_dimension,
        "library_direction_counts": library_directions,
    }


def audit(repo: Path, attestation: Path):
    # Authenticate original raw 620 A-process attestation first, then each
    # 21 frozen source JSON blob, then original 620/295445 flag census totals.
    gate = base.audit(repo, attestation)
    docs = {}
    for library, sha in base.source.I55_BLOBS.items():
        raw = (repo / "research/results/iteration55" /
               f"cells_{library}.json").read_bytes()
        require(base.git_blob(raw) == sha, f"Original source cell blob mismatch: {library}")
        docs[library] = json.loads(raw)
    matched = paired_comparison(docs)
    require(len(docs) == 21 and matched["nominal_strata"] == 210 and
            matched["complete_three_function_strata"] == 205 and
            len(matched["incomplete_strata"]) == 5,
            "Original 21-library × 2-dimension × 5-seed matched roster differs")
    for flag in FLAGS:
        for a,b in CONTRASTS:
            t = matched["overall_matched"][flag][f"{a}_vs_{b}"]
            require(t["pairs"] == 205, f"Unmatched or missing {flag}/{a}/{b} count")
    return {
        "schema": "I65_I55_A_PROCESS_PAIRED_FUNCTION_CONTEXT_V1",
        "original_source_commit": base.SOURCE_SHA,
        "source_620_manifest_git_blob": base.MANIFEST_SHA,
        "attestation_json_sha256": gate["original_620_full_attestation_sha256"],
        "full_620_original_A_trace_attestation_prerequisite": True,
        "source_21_original_cells_sha1": dict(sorted(base.source.I55_BLOBS.items())),
        "source_620_census_regression_pass": True,
        "flags": list(FLAGS),
        "pairs": [f"{a}_vs_{b}" for a,b in CONTRASTS],
        **matched,
        "interpretation": [
            "Post-hoc descriptive paired comparison of flag presence, not causal effect of objective family.",
            "Match library, dimension, original seed; 10 historical failed cells occupy only 5 shared 10D Nevergrad strata (sphere and Rastrigin both failed).",
            "Flag events are neither independent samples nor adjudicated software failures.",
            "Library-level signs describe heterogeneous library evidence; NO p-values, CIs or accuracy estimates.",
            "Function and library characteristics and unequal original evaluation budgets can confound interpretation.",
            "No A-prime/B raw replay, I64-R raw seed-level bootstrap, M6/C1 signoff or new COCO.",
        ],
        "new_optimizer_or_physical_experiments": 0,
        "scientific_status": "DRAFT / NO-FREEZE / NOT_ESTABLISHED",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--full-attestation", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = audit(args.repo_root.resolve(), args.full_attestation)
    raw = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(raw, encoding="utf-8")
    else:
        print(raw, end="")


if __name__ == "__main__":
    main()
