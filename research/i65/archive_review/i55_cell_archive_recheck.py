"""Read-only, cell-level I55 JSON replay; never executes an optimizer or reads NPZ.

Run at repository root:
    python research/i65/i55_cell_archive_recheck.py > /tmp/i55_cell_check.json

This audits the archived *cell metadata and digest comparisons*. It is NOT an
independent reconstruction of the byte-level objective-call traces. Historical
files are read as bytes, validated against recorded Git blob hashes and never
rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

# Frozen input identities verified on GitHub main at 6b56fbc53ffc4d275ecef5e911ea4663474c9a08.
CELL_BLOBS = {
    "baybe": "244296e9297e3aa1640673ee028aa1f2f784f0ff",
    "bayes_opt": "64ceed52bbc228296691721b4fc4672999c4e341",
    "bofire": "55a1f8e145f10466fae08f41d555447877769fcd",
    "cma": "99f0ebc95004f8f771a43accb8ebb4bbd887a862",
    "cmaes": "b0af13eb45fca4fdde2e47744452f40f1c63d8cb",
    "deap": "532f070501578d29d452be5f1a18cd1cf6883318",
    "emukit": "c712f0f10c33137f522967ffbc7136a6a16db40b",
    "evolopy": "63b1df3e2373869a44eebf365fc0a982e84cf4d1",
    "evotorch": "651bf5d1d782bc5afb26b6a648d2219ba1d89537",
    "evox": "debf2e9a880a70c4ac906ba2c15b728212b84074",
    "geneticalgorithm": "2a2b1360f6bb0be7644fca74decf0073160fbc40",
    "gfo": "3837984908a81e51213e5cc350273614eab461ac",
    "nevergrad": "f97f7e6ce48fc69ef1ff8c5177f5a7eec7fe3f76",
    "niapy": "c7bdcaa3c89dd8ec178f5d2620c5354a45fe4894",
    "optuna": "779c7cfd7dd79a48aa6edb8f637c194a1f5131aa",
    "pygad": "7b34d70482e952e4c229338a837f0171b5e83282",
    "pymoo": "2a5ac44e4c62f86ebb43dba6ccc3a2bd9db7e79e",
    "pyswarms": "72fffb230fd464834403a6de138e157aee0e6e27",
    "scikit_opt": "e5cf9ef291eed46b565a75ce80c9f3f6cee2aa19",
    "scipy_de": "68198ace7b3dc7185e31d92bea27dc7905ddae50",
    "smac": "aee6add993eaf400f4026a8a0448b66c87173b75",
}
RECOMPUTE_BLOB = "759de302c9678b2319cdd2603f35fa38a5196eb0"
DIGEST_FIELDS = ("hash", "hash_rerun", "hash_same", "hash_diff")
FLAG_TO_DIGEST = {"D3": "hash_rerun", "D3x_same": "hash_same", "D3x_diff": "hash_diff"}


class ArchiveMismatch(ValueError):
    """An archived claim or required source invariant is not satisfied."""


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise ArchiveMismatch(reason)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def read_pinned_json(path: Path, sha: str) -> dict:
    raw = path.read_bytes()
    observed = git_blob_sha(raw)
    check(observed == sha, f"Source changed: {path} blob={observed} expected={sha}")
    return json.loads(raw)


def is_hex_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(x in "0123456789abcdef" for x in value)


def audit_library(name: str, cells: list[dict]) -> dict:
    check(len(cells) == 30, f"{name}: expected 30 cells, found {len(cells)}")
    seen = set()
    counts = {"valid": 0, "invalid": 0, "manipulation_ok": 0,
              "D3": 0, "D3x_same": 0, "D3x_diff": 0}
    invalid_keys = []
    for c in cells:
        label = (c.get("function"), c.get("d"), c.get("seed"))
        check(label not in seen, f"{name}: duplicate cell {label}")
        seen.add(label)
        check(c.get("library") == name, f"{name}: cell library mismatch {label}")
        failed = bool(c.get("error") or c.get("errors"))
        if failed:
            counts["invalid"] += 1
            invalid_keys.append(list(label))
            check(c.get("manipulation_ok") is False, f"{name}: invalid cell marked manipulation success {label}")
            continue
        counts["valid"] += 1
        check(c.get("manipulation_ok") is True, f"{name}: valid cell lacks manipulation success {label}")
        counts["manipulation_ok"] += 1
        check(isinstance(c.get("hash_sentinel"), int) and isinstance(c.get("sentinel_same"), int)
              and isinstance(c.get("sentinel_diff"), int), f"{name}: missing integer sentinels {label}")
        check(c["hash_sentinel"] == c["sentinel_same"], f"{name}: A/A' control sentinel mismatch {label}")
        check(c["sentinel_same"] != c["sentinel_diff"], f"{name}: hash-seed manipulation ineffective {label}")
        for key in DIGEST_FIELDS:
            check(is_hex_digest(c.get(key)), f"{name}: invalid {key} digest {label}")
        for key, compared_to in FLAG_TO_DIGEST.items():
            reconstructed = int(c["hash"] != c[compared_to])
            check(c.get(key) == reconstructed, f"{name}: {key} flag disagrees with source hashes {label}")
            counts[key] += reconstructed
    counts["cells"] = len(cells)
    counts["invalid_keys"] = invalid_keys
    return counts


def audit_tree(repo_root: Path) -> dict:
    source = repo_root / "research" / "results" / "iteration55"
    by_library = {}
    for name, sha in sorted(CELL_BLOBS.items()):
        archive = read_pinned_json(source / f"cells_{name}.json", sha)
        check(archive.get("library") == name, f"{name}: file-level library mismatch")
        by_library[name] = audit_library(name, archive["cells"])
    expected = read_pinned_json(source / "recompute.json", RECOMPUTE_BLOB)
    check(set(expected.get("libraries", {})) == set(CELL_BLOBS), "recompute library roster mismatch")
    for name, values in by_library.items():
        published = expected["libraries"][name]
        for key, target in (("D3", "D3"), ("D3x_same", "D3x_same"),
                            ("D3x_diff", "D3x_diff"), ("valid", "comparison_valid"),
                            ("cells", "cells")):
            check(values[key] == published[target], f"{name}: {key} does not match recompute.json")
    summed = {key: sum(row[key] for row in by_library.values())
              for key in ("cells", "valid", "invalid", "manipulation_ok", "D3", "D3x_same", "D3x_diff")}
    check((len(by_library), summed["cells"], summed["valid"], summed["invalid"],
           summed["manipulation_ok"]) == (21, 630, 620, 10, 620), "I55 denominator mismatch")
    check(by_library["nevergrad"]["invalid"] == 10
          and all(x[1] == 10 for x in by_library["nevergrad"]["invalid_keys"]),
          "Unexpected Nevergrad failure pattern")
    check(all(v["invalid"] == 0 for k, v in by_library.items() if k != "nevergrad"),
          "Unexpected failures outside Nevergrad")
    differing = sorted(k for k, v in by_library.items() if v["D3x_diff"] > 0)
    same = sorted(k for k, v in by_library.items() if v["D3x_same"] > 0)
    check(differing == sorted(expected["summary"]["d3x_diff"]) == ["nevergrad", "smac"],
          "D3x_diff library identities changed")
    check(same == sorted(expected["summary"]["d3x_same"]) == ["nevergrad"],
          "D3x_same library identities changed")
    check((by_library["nevergrad"]["D3x_diff"], by_library["nevergrad"]["D3x_same"],
           by_library["smac"]["D3x_diff"], by_library["smac"]["D3x_same"]) == (5, 5, 30, 0),
          "I55 hash-seed contrast counts changed")
    return {
        "schema": "GADAPT_I55_CELL_JSON_RECHECK_V1",
        "kind": "read_only_archived_cell_metadata_check_not_npz_trace_replay",
        "input_git_blobs": {f"cells_{k}.json": v for k, v in sorted(CELL_BLOBS.items())} |
                           {"recompute.json": RECOMPUTE_BLOB},
        "totals": {"libraries": len(by_library), **summed},
        "d3x_diff_libraries": differing,
        "d3x_same_libraries": same,
        "by_library": by_library,
        "checks": {"source_blobs": True, "cell_uniqueness": True, "seed_sentinels": True,
                   "rederived_hash_flags": True, "recompute_aggregate_agreement": True,
                   "invalid_cells_explicit": True},
        "not_checked": ["NPZ objective-point arrays", "318/358 byte sequence replay versus I50",
                        "emukit C2 mismatch causal analysis", "I64 individual stochastic traces/bootstrap"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(audit_tree(args.repo_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
