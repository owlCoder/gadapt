"""I55 archive audit: verify exact I55 NPZ traces and I50↔I55 hashes, read only.

Use only on an existing full clone of owlCoder/gadapt, never runs optimizers:
    python i55_npz_cross_archive_verifier.py --repo-root /path/to/gadapt \
      > I65_I55_NPZ_COMPLETE_RECHECK.json

The 2026-11-02 external connector review established the *JSON pair* 318/358
and directly decompressed/rehashed FOUR original plateau NPZ files. The FULL
NPZ mode below is supplied for reproducibility but NOT run as part of that
review. Do not label its prospective checks as completed until actually run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import numpy as np

SNAPSHOT = "6b56fbc53ffc4d275ecef5e911ea4663474c9a08"
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
POSTHOC_BLOB = "2cac9ca8fefd9bb1029ac507ce5fd11624f80771"
NPZ_KEYS = {"x", "f", "phase", "x_star", "f_star", "reported_evals", "documented_max"}
BASE_DIR = Path("research/results")


def blob_sha(b: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(b)).encode("ascii") + b"\x00" + b).hexdigest()


def read_pinned_json(path: Path, want_sha: str) -> dict:
    raw = path.read_bytes()
    sha = blob_sha(raw)
    if sha != want_sha:
        raise ValueError(f"Git blob mismatch {path}: {sha} != {want_sha}")
    return json.loads(raw)


def key(r: dict) -> tuple[str, int, int]:
    return (r["function"], r["d"], r["seed"])


def sequence_hash(x: np.ndarray, f: np.ndarray, phase: np.ndarray) -> str:
    """Independently implement frozen i49.sequence_hash, no optimizer imports."""
    if not (len(x) == len(f) == len(phase)):
        raise ValueError("Inconsistent array lengths")
    h = hashlib.sha256()
    for xx, ff, pp in zip(x, f, phase):
        if int(pp) not in (0, 1):
            raise ValueError(f"Unsupported phase {pp}")
        h.update(np.ascontiguousarray(xx, dtype=np.float64).tobytes())
        h.update(repr(float(ff)).encode("ascii"))
        h.update(b"search" if pp == 0 else b"post")
    return h.hexdigest()


def classify_arrays(x: np.ndarray, f: np.ndarray, phase: np.ndarray,
                    x_star: np.ndarray, f_star: float | None,
                    reported_evals: int | None, documented_max: int | None) -> dict:
    """Independent reimplementation of original I49/I50 flag definitions."""
    n, d = x.shape
    lo, hi = np.full(d, -5.0), np.full(d, 5.0)
    flags = {s: 0 for s in ("C1", "C2", "C3", "C4", "C5", "R1", "R2", "R3", "D2")}
    seen = set()
    for row in x:
        if np.array_equal(row, lo) or np.array_equal(row, hi):
            flags["C1"] += 1
        raw = row.tobytes()
        if raw in seen:
            flags["C2"] += 1
        seen.add(raw)
        if np.any(row < lo) or np.any(row > hi):
            flags["C3"] += 1
    if documented_max is not None:
        flags["C4"] = max(0, n - documented_max)
    flags["C5"] = int(np.sum(phase != 0))
    if x_star.size:
        matches = [i for i in range(n) if np.all(np.abs(x[i] - x_star) <= 1e-12)]
        flags["R1"] = int(not matches)
        if f_star is not None and matches:
            recorded = float(f[matches[0]])
            flags["R2"] = int(abs(f_star - recorded) > 1e-9 * max(1.0, abs(recorded)))
        if f_star is not None and np.any(phase == 0):
            best = min(float(v) for v in f[phase == 0])
            flags["R3"] = int(f_star - best > 1e-9 * max(1.0, abs(best)))
    if reported_evals is not None:
        flags["D2"] = int(reported_evals != n)
    return flags


def evaluate_frozen_objective(x: np.ndarray, function: str) -> np.ndarray:
    """Independently re-evaluate frozen I49/50 original *objective only*.

    The frozen source ``Problem.base`` operates on untransformed z=x with
    LOWER=-5, UPPER=+5. This function never invokes an optimizer, power-flow,
    adapter or stochastic generator. It is deliberately independent of the
    historical ``research.iteration49_integrity_audit`` module.
    """
    if not isinstance(x, np.ndarray) or x.ndim != 2 or x.dtype != np.float64:
        raise ValueError("Objective oracle requires 2D float64 coordinates")
    if x.shape[1] not in (2, 10):
        raise ValueError("Unexpected I55 objective dimension")
    with np.errstate(invalid="ignore", over="ignore"):
        if function == "sphere":
            # c = -5 + 0.37*(5-(-5)) = -1.3 (frozen I49 formula)
            center = -5.0 + 0.37 * 10.0
            return np.sum((x - center) ** 2, axis=1)
        if function == "rastrigin":
            return 10.0 * x.shape[1] + np.sum(x*x - 10.0*np.cos(2.0*np.pi*x), axis=1)
        if function == "plateau":
            return np.sum(np.floor(x), axis=1)
    raise ValueError(f"Unknown frozen I55 objective: {function!r}")


def check_frozen_objective_values(x: np.ndarray, f: np.ndarray, function: str) -> dict:
    """Verify captured per-call objective values against an independent oracle.

    Cross-platform trig/reduction rounding is tolerated at 1e-10 absolute and
    relative; this is a post-hoc *data-integrity* check, not a proof of library
    bugs, independent physical validation, or a new experimental outcome.
    """
    expected = evaluate_frozen_objective(x, function)
    if f.dtype != np.float64 or f.shape != expected.shape:
        raise ValueError("Objective oracle input value dtype or shape mismatch")
    matches = np.isclose(f, expected, rtol=1e-10, atol=1e-10, equal_nan=True)
    if not bool(np.all(matches)):
        index = int(np.flatnonzero(~matches)[0])
        raise ValueError(f"Frozen objective value mismatch at call {index} "
                         f"for {function}: archived={f[index]!r} expected={expected[index]!r}")
    # This report records only sample count, not estimates of scientific efficacy.
    return {"function": function, "verified_calls": int(len(f)),
            "all_frozen_objective_values_match": True,
            "rtol": 1e-10, "atol": 1e-10}


def replay_npz(path: Path, cell: dict) -> dict[str, Any]:
    import zipfile
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size > 25_000_000:
        raise ValueError("Unexpectedly oversized NPZ")
    with zipfile.ZipFile(path) as z:
        actual = {name.removesuffix(".npy") for name in z.namelist()}
        if len(z.namelist()) != 7 or actual != NPZ_KEYS:
            raise ValueError(f"Unexpected NPZ members: {sorted(actual)}")
        if any(info.file_size > 12_000_000 for info in z.infolist()):
            raise ValueError("NPZ member exceeds safety limit")
    with np.load(path, allow_pickle=False) as z:
        x, f, phase = [np.asarray(z[t]) for t in ("x", "f", "phase")]
        x_star, fv = np.asarray(z["x_star"]), np.asarray(z["f_star"])
        reports = np.asarray(z["reported_evals"])
        documented = np.asarray(z["documented_max"])
    if x.ndim != 2 or x.shape[1] != cell["d"] or f.shape != (len(x),) or phase.shape != (len(x),):
        raise ValueError("NPZ coordinate/function/phase shapes mismatch")
    if x.dtype != np.dtype("float64") or f.dtype != np.dtype("float64") or phase.dtype != np.dtype("int8"):
        raise ValueError("NPZ dtype mismatch")
    if fv.size != 1 or reports.size != 1 or documented.size != 1:
        raise ValueError("NPZ result field dimensions mismatch")
    n = len(x)
    observed = sequence_hash(x, f, phase)
    if observed != cell["hash"]:
        raise ValueError("NPZ raw sequence hash disagrees with saved I55 hash")
    if cell["calls"] != n:
        raise ValueError("NPZ count disagrees with archived call count")
    # A correct archived trace digest authenticates the bytes but says nothing
    # about whether its recorded objective values follow the frozen objective.
    # The extra oracle is independent of the I49/50 classifier implementation.
    oracle = check_frozen_objective_values(x, f, cell["function"])
    fstar = None if np.isnan(float(fv[0])) else float(fv[0])
    rev = None if int(reports[0]) < 0 else int(reports[0])
    mx = None if int(documented[0]) < 0 else int(documented[0])
    derived = classify_arrays(x, f, phase, x_star.ravel(), fstar, rev, mx)
    diff = {k: [cell["flags"].get(k), v] for k, v in derived.items()
            if cell["flags"].get(k) != v}
    return {"calls": n, "npz_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "trace_hash": observed, "flag_mismatches": diff,
            "repeated_count": derived["C2"], "objective_oracle": oracle}


def paired_i50_i55(original: dict[str, dict], new: dict[str, dict]) -> dict:
    counts = {}
    skips, all_diffs = [], []
    for name in sorted(original):
        prior = {key(r): r for r in original[name]["cells"]}
        recent = {key(r): r for r in new[name]["cells"]}
        if len(prior) != 30 or len(recent) != 30 or prior.keys() != recent.keys():
            raise ValueError(f"Cell roster mismatch for {name}")
        same, different, skipped = 0, 0, 0
        for cell, before in sorted(prior.items()):
            after = recent[cell]
            if before.get("error") or after.get("error") or not before.get("hash") or not after.get("hash"):
                skipped += 1
                skips.append({"library": name, "cell": cell, "i50_error": before.get("error"),
                              "i55_error": after.get("error")})
            elif before["hash"] == after["hash"]:
                same += 1
            else:
                different += 1
                all_diffs.append({"library": name, "cell": cell})
        counts[name] = {"same": same, "different": different, "skipped": skipped,
                        "comparison_valid": same + different}
    s = {k: sum(x[k] for x in counts.values()) for k in ("same", "different", "skipped", "comparison_valid")}
    return {"totals": s, "by_library": counts, "skipped": skips,
            "different_by_library": {n: [list(x["cell"]) for x in all_diffs if x["library"] == n]
                                     for n in sorted(set(x["library"] for x in all_diffs))},
            "matches_frozen_318_358": s == {"same": 318, "different": 40, "skipped": 2, "comparison_valid": 358}}


def posthoc_diagnostic(original_emukit: dict, new_emukit: dict, posthoc: dict) -> dict:
    old = {key(c): c for c in original_emukit["cells"]}
    new = {key(c): c for c in new_emukit["cells"]}
    rows = []
    for c in posthoc["cells"]:
        k = key(c)
        rows.append({"cell": k, "matches_original_i50": c["hash"] == old[k]["hash"],
                     "differs_from_i55": c["hash"] != new[k]["hash"],
                     "reported_threads": c["veclib_threads"]})
    return {"count": len(rows), "all_10_match_i50_and_differ_i55": len(rows) == 10 and all(
        r["matches_original_i50"] and r["differs_from_i55"] and r["reported_threads"] == 1 for r in rows),
        "cases": rows}


def audit(repo_root: Path, full_npz: bool = True) -> dict:
    root = repo_root / BASE_DIR
    recent = {n: read_pinned_json(root / "iteration55" / f"cells_{n}.json", sha)
              for n, sha in I55_BLOBS.items()}
    original = {n: read_pinned_json(root / "iteration50" / f"cells_{n}.json", sha)
                for n, sha in I50_BLOBS.items()}
    post = read_pinned_json(root / "iteration55_posthoc" / "emukit_veclib.json", POSTHOC_BLOB)
    paired = paired_i50_i55(original, recent)
    diagnostic = posthoc_diagnostic(original["emukit"], recent["emukit"], post)
    errors, checked, npz_flags, objective_calls = [], 0, 0, 0
    if full_npz:
        for lib in sorted(recent):
            for c in recent[lib]["cells"]:
                path = root / "iteration55" / "traces" / lib / f"{c['function']}_{c['d']}_{c['seed']}.npz"
                if c.get("error") or not c.get("hash"):
                    continue
                try:
                    result = replay_npz(path, c)
                    checked += 1
                    objective_calls += result["objective_oracle"]["verified_calls"]
                    if result["flag_mismatches"]:
                        npz_flags += 1
                        errors.append({"library": lib, "cell": key(c), "problem": "flag mismatch",
                                       "details": result["flag_mismatches"]})
                except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
                    errors.append({"library": lib, "cell": key(c), "problem": str(exc)})
    return {"schema": "I65_I55_FULL_NPZ_AND_I50_CROSS_CHECK_V1",
            "pinned_head": SNAPSHOT,
            "read_only": True,
            "cross_i50_i55": paired,
            "posthoc_emukit_saved_digest_check": diagnostic,
            "npz": {"attempted": full_npz, "checked": checked,
                    "expected_evaluable": 620, "cells_with_flag_difference": npz_flags,
                    "frozen_objective_value_calls_checked": objective_calls,
                    "frozen_objective_values_pass": full_npz and checked == 620 and not errors and objective_calls > 0,
                    "errors": errors, "full_raw_trace_pass": full_npz and checked == 620 and not errors},
            "limits": ["Only archives at pinned Git source IDs", "NPZ replay is NOT an optimizer re-run",
                       "Archive digest agreement does not establish root-cause attribution",
                       "Post hoc VECLIB diagnostic is not preregistered validation",
                       "I64 stochastic bootstrap and independent I50 raw traces were not repeated"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--metadata-only", action="store_true", help="Skip raw NPZ arrays; still validate JSON identities")
    opt = parser.parse_args()
    print(json.dumps(audit(opt.repo_root, full_npz=not opt.metadata_only), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
