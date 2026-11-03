#!/usr/bin/env python3
"""Read-only I50/I55 JSON flag-count vs flag-presence comparison.

The frozen I55 recompute.py checks bool(old[k]) != bool(recomputed[k]),
not exact numeric counts. This independent verifier compares BOTH concepts.
No NPZ, optimizer or power-flow execution is performed.

Run: python i55_i50_numeric_vs_boolean_audit.py --repo-root /path/to/gadapt
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

I50_BLOBS = {
    "baybe": "98b843c3fa4ddccf8661570986ff13ed291fb088",
    "bayes_opt": "566df77fe0d149879a63c7174aa05f38d0237537",
    "bofire": "e91746e2149ed38ee9cec2fecdef08ea8994a9b6",
    "cmaes": "13888f5275674ba64dc0a233753cdfac222c4aed",
    "emukit": "90fc870b617f18c549936146320237e8a53e9e7a",
    "evolopy": "75e0465c35f0ae8391e4d9286ccd6aa9ad2090f1",
    "evotorch": "bb57a45015cee13b2812eec52b3d510cdcf04237",
    "evox": "f4174bdaa13491cac66db34da61e58e0c9da650e",
    "gfo": "4840620af763e5b1eaa6e89d9ce710534c191b81",
    "niapy": "3d9f00c3482d8385541be21e491e45b1ce7070a3",
    "scikit_opt": "0b8c17d8d5ad4b02a915808dfd4ccd578d92a82b",
    "smac": "4df33c2c93d3ebd6b2c3f2ebc58f043ddd000f3a",
}
I55_BLOBS = {
    "baybe": "244296e9297e3aa1640673ee028aa1f2f784f0ff",
    "bayes_opt": "64ceed52bbc228296691721b4fc4672999c4e341",
    "bofire": "55a1f8e145f10466fae08f41d555447877769fcd",
    "cmaes": "b0af13eb45fca4fdde2e47744452f40f1c63d8cb",
    "emukit": "c712f0f10c33137f522967ffbc7136a6a16db40b",
    "evolopy": "63b1df3e2373869a44eebf365fc0a982e84cf4d1",
    "evotorch": "651bf5d1d782bc5afb26b6a648d2219ba1d89537",
    "evox": "debf2e9a880a70c4ac906ba2c15b728212b84074",
    "gfo": "3837984908a81e51213e5cc350273614eab461ac",
    "niapy": "c7bdcaa3c89dd8ec178f5d2620c5354a45fe4894",
    "scikit_opt": "e5cf9ef291eed46b565a75ce80c9f3f6cee2aa19",
    "smac": "aee6add993eaf400f4026a8a0448b66c87173b75",
}
FLAGS = ("C1", "C2", "C3", "C4", "C5", "R1", "R2", "R3", "D2")


def git_sha(b: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\x00" + b).hexdigest()


def read_checked(p: Path, expected: str) -> dict:
    raw = p.read_bytes()
    if git_sha(raw) != expected:
        raise ValueError(f"Git blob mismatch: {p}")
    return json.loads(raw)


def key(c: dict) -> tuple[str, int, int]:
    return (c["function"], c["d"], c["seed"])


def compare_pair(old: dict, new: dict) -> dict[str, Any]:
    o = {key(c): c for c in old["cells"]}
    n = {key(c): c for c in new["cells"]}
    if len(o) != 30 or len(n) != 30 or o.keys() != n.keys():
        raise ValueError("The 30-cell roster does not match")
    evaluated, skips, differences = 0, [], []
    for k in sorted(o):
        before, after = o[k], n[k]
        if before.get("error") or after.get("error") or before.get("flags") is None or after.get("flags") is None:
            skips.append({"cell": k, "I50_error": before.get("error"), "I55_error": after.get("error")})
            continue
        evaluated += 1
        numeric, boolean = {}, {}
        for flag in FLAGS:
            if flag not in before["flags"] or flag not in after["flags"]:
                raise ValueError(f"Missing comparable flag {flag} for {k}")
            old_value, new_value = before["flags"][flag], after["flags"][flag]
            if not isinstance(old_value, int) or not isinstance(new_value, int):
                raise ValueError(f"Invalid flag counter {flag}")
            if old_value != new_value:
                numeric[flag] = [old_value, new_value]
            if bool(old_value) != bool(new_value):
                boolean[flag] = [int(bool(old_value)), int(bool(new_value))]
        if numeric or boolean:
            differences.append({"cell": k, "numeric_differences": numeric,
                                "presence_differences": boolean})
    return {"compared": evaluated, "skipped": skips,
            "numeric_change_cells": sum(bool(x["numeric_differences"]) for x in differences),
            "presence_change_cells": sum(bool(x["presence_differences"]) for x in differences),
            "differences": differences}


def audit(repo: Path) -> dict:
    base = repo / "research" / "results"
    names = sorted(I50_BLOBS)
    out = {}
    for name in names:
        old = read_checked(base / "iteration50" / f"cells_{name}.json", I50_BLOBS[name])
        new = read_checked(base / "iteration55" / f"cells_{name}.json", I55_BLOBS[name])
        out[name] = compare_pair(old, new)
    numeric = [(name, item) for name, sub in out.items() for item in sub["differences"]
               if item["numeric_differences"]]
    presence = [(name, item) for name, sub in out.items() for item in sub["differences"]
                if item["presence_differences"]]
    total = sum(x["compared"] for x in out.values())
    expected = (total == 358 and len(numeric) == 1 and len(presence) == 1 and
                numeric[0][0] == "emukit" and numeric[0][1]["cell"] == ("plateau", 2, 6001) and
                numeric[0][1]["numeric_differences"] == {"C1": [2, 3], "C2": [0, 1]} and
                presence[0][1]["presence_differences"] == {"C2": [0, 1]})
    return {"schema": "I65_I55_EXACT_NUMERIC_VS_BINARY_FLAGS_V1",
            "source_git_blobs": {k: {"I50": I50_BLOBS[k], "I55": I55_BLOBS[k]} for k in names},
            "compared_cells": total,
            "skipped": [dict(library=n, **s) for n, x in out.items() for s in x["skipped"]],
            "numeric_counter_changed_cells": len(numeric),
            "binary_presence_changed_cells": len(presence),
            "only_counter_discrepancy": [{"library": n, **v} for n, v in numeric],
            "matches_exact_frozen_expectation": expected,
            "scope": "Saved I50/I55 JSON cell-level counters. No independent raw NPZ replay.",
            "notes": ["C1 count 2 to 3 does not change its binary flag presence",
                      "C2 count 0 to 1 changes binary flag presence",
                      "Historical I55 recompute.py compares bool(old flag) versus bool(new flag); not exact numeric count"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", required=True, type=Path)
    args = p.parse_args()
    r = audit(args.repo_root)
    print(json.dumps(r, indent=2, sort_keys=True))
    if not r["matches_exact_frozen_expectation"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
