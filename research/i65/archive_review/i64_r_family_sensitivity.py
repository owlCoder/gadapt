#!/usr/bin/env python3
"""Read-only leave-one-function/dimension-out review of frozen I64-R.

The original I64-R registered verdict MUST remain unchanged. This tool only
calculates post hoc point-estimate sensitivity; it never reruns optimizers or
reinterprets the original bootstrap interval.

Usage:
  python i64_r_family_sensitivity.py --repo-root /path/to/gadapt > sensitivity.json
  python i64_r_family_sensitivity.py --analysis /path/to/analysis.json.gz
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

R_BLOB_SHA1 = "59025d6cc052baef76b14e5496962704bdb7604a"
ORIGINAL_CONTRASTS = ("c1", "c2", "c3", "c4")
FAMILIES = ("sphere", "rosenbrock", "rastrigin", "ackley", "griewank",
            "styblinski_tang", "beale", "himmelblau", "booth")
EXPECTED_PAIRS = frozenset(
    f"{family}|{d}"
    for family in FAMILIES
    for d in ((2,) if family in ("beale", "himmelblau", "booth") else (2, 7, 20))
)
RAW_FIELDS = ("shift|gadapt", "shift|ipop", "rot|gadapt", "rot|ipop", "rotm|gadapt", "rotm|ipop")


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def parse_frozen(path: Path, *, check_blob: bool = True) -> dict:
    raw = path.read_bytes()
    if check_blob and git_blob_sha1(raw) != R_BLOB_SHA1:
        raise ValueError(f"I64-R Git blob mismatch: {git_blob_sha1(raw)} != {R_BLOB_SHA1}")
    obj = json.loads(gzip.decompress(raw))
    if set(obj.get("per_pair", {})) != EXPECTED_PAIRS:
        raise ValueError("Frozen 21 function/dimension roster mismatch")
    if len(obj.get("estimates", [])) != 4:
        raise ValueError("Missing four registered contrasts")
    return obj


def rows_from_frozen(obj: dict) -> list[dict]:
    if set(obj.get("per_pair", {})) != EXPECTED_PAIRS:
        raise ValueError("Frozen 21 function/dimension roster mismatch")
    results = []
    for key, item in sorted(obj["per_pair"].items()):
        family, d = key.split("|")
        d = int(d)
        if set(item) != set(RAW_FIELDS):
            raise ValueError(f"Unexpected or missing variant/configuration: {key}")
        for field in RAW_FIELDS:
            value = item[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"Invalid ECDF A {key}/{field}: {value!r}")
        c1 = item["rotm|gadapt"] - item["rot|gadapt"]
        c2 = item["shift|gadapt"] - item["rotm|gadapt"]
        c3 = item["shift|ipop"] - item["rotm|ipop"]
        c4 = c2 - c3
        w = 1 / (9 * (1 if family in ("beale", "himmelblau", "booth") else 3))
        results.append(dict(cell=key, family=family, dimension=d, weight=w,
                            c1=c1, c2=c2, c3=c3, c4=c4, contribution_c4=w * c4))
    if not math.isclose(sum(row["weight"] for row in results), 1, abs_tol=1e-12):
        raise ValueError("Weights do not sum to 1")
    return results


def effect(rows: list[dict], contrast: str, *, renormalize: bool = True) -> float:
    numerator = sum(r["weight"] * r[contrast] for r in rows)
    denominator = sum(r["weight"] for r in rows) if renormalize else 1
    if not denominator:
        raise ValueError("Cannot estimate an empty study")
    return numerator / denominator


def evaluate(obj: dict) -> dict:
    rows = rows_from_frozen(obj)
    estimates = {c: effect(rows, c) for c in ORIGINAL_CONTRASTS}
    for i, c in enumerate(ORIGINAL_CONTRASTS):
        if not math.isclose(estimates[c], obj["estimates"][i], rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"Registered contrast mismatch {c}: {estimates[c]} vs {obj['estimates'][i]}")
    families = []
    for family in FAMILIES:
        removed = [r for r in rows if r["family"] == family]
        remain = [r for r in rows if r["family"] != family]
        families.append(dict(family=family, n_removed=len(removed), removed_c4_contribution=effect(removed, "c4", renormalize=False),
                             c2=effect(remain, "c2"), c4=effect(remain, "c4"),
                             point_c4_above_registered_threshold=effect(remain, "c4") > .05))
    dims = []
    for dimension in (2, 7, 20):
        remain = [r for r in rows if r["dimension"] != dimension]
        dims.append(dict(dimension_removed=dimension, remaining_weight=sum(r["weight"] for r in remain),
                         c2=effect(remain, "c2"), c4=effect(remain, "c4")))
    loo_cells = []
    for row in rows:
        rest = [r for r in rows if r["cell"] != row["cell"]]
        loo_cells.append(dict(cell_removed=row["cell"], c4=effect(rest, "c4")))
    return {
        "source_blob_sha1": R_BLOB_SHA1,
        "type": "POST_HOC_POINT_ESTIMATE_SENSITIVITY_ONLY",
        "original_inference": {"H64r1": obj.get("H64r1"), "H64r2": obj.get("H64r2"), "H64r3": obj.get("H64r3"),
                               "simultaneous_interval_c4": [obj["lower"][3], obj["upper"][3]],
                               "bootstrap": obj.get("boot"), "alpha": obj.get("alpha")},
        "reconstructed_contrasts": estimates,
        "family_leave_one_out": families,
        "dimension_leave_one_out": dims,
        "cell_leave_one_out": loo_cells,
        "pair_effect_signs": {"positive": sum(r["c4"] > 0 for r in rows), "negative": sum(r["c4"] < 0 for r in rows),
                              "zero": sum(r["c4"] == 0 for r in rows)},
        "pairs_sorted_by_c4_contribution": sorted(rows, key=lambda r: -r["contribution_c4"]),
        "limitations": [
            "Original preregistered I64-R inference is unchanged.",
            "Removing a family changes the target estimand and fixed benchmark composition.",
            "No leave-one-out bootstrap or multiple-comparison inference was run.",
            "Selection of 21 benchmark cells and Q matrices is not represented by seed bootstrap intervals.",
            "No generalization to all orthogonal transforms or objective families is warranted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--analysis", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if bool(args.repo_root) == bool(args.analysis):
        parser.error("provide exactly one of --repo-root or --analysis")
    p = args.analysis or (args.repo_root / "research/results/iteration64_r/analysis.json.gz")
    result = evaluate(parse_frozen(p))
    txt = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(txt, encoding="utf8")
    else:
        sys.stdout.write(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
