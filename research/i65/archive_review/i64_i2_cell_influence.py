#!/usr/bin/env python3
"""Archive-only I64-I / I64-I2 cell-contribution review; no optimizer/PF calls.

Run from a COMPLETE local clone of owlCoder/gadapt:
  python i64_i2_cell_influence.py --repo-root /path/to/gadapt > i64_i2_cell_influence.json

This script checks original Git blob SHA1 identifiers, matches (cell,seed),
recalculates per-cell feasibility and CVaR90 from archived run records and
checks all original I2 point estimates. The leave-one-cell-out calculations
are POST HOC descriptive estimates, not new simultaneous confidence bounds.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path

I_BLOBS = (
    "ffe95e937a9b1ca816e12119cafa788650a7f9e2", "74dec4b78827576d85f6779959db215172f2f1aa",
    "aa87c26e3f11af0775b5af10700945a52ee8477a", "359d448120fb95e47b53f51a669caa99165ed70a",
    "a98c087e37ea6cceab15a8e2d64e117fff1951e6", "772911f923101922abc57155a72652356e688e60",
    "b716f85173109c1f706e67223da32793fb116825", "55319da5b24284d308239b68f146b10dea5c07a0",
)
I2_BLOBS = (
    "73900a5ccaa733405fc0a3eb6df1133608116609", "4c08bf1941be512fcc4e8d49dcb9f8390873f844",
    "3fa08cd05e14c2cc826290a6ce66dc3a52753e3b", "2e31819b1226ac76c47773f5660d73976556af2b",
    "89abd8a3ebed095038224974a881b1548af1ddd0", "8f82e3790585c68ecf7f1a8a5c692684167caa7e",
    "66bb6005596ec83f6b0d8c48a796528e7557d3c0", "c0377da80ab2b397154a6a949055ab763513184b",
)
ANALYSIS_BLOB = "2b38375126a43128dba37aaf7966b92eb6df8691"
CONFIGS = ("gadapt", "gadapt_hyb", "ipop")
N_CELLS, N_SEEDS, BUDGET = 8, 30, 12000
CONTRASTS = ("CVaR(M)-CVaR(H)", "P(H)-P(M)", "CVaR(IPOP)-CVaR(H)", "P(H)-P(IPOP)")


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def read_pinned(path: Path, expected_blob_sha: str) -> dict:
    raw = path.read_bytes()
    actual = git_blob_sha1(raw)
    if actual != expected_blob_sha:
        raise ValueError(f"Source blob changed: {path}: {actual} != {expected_blob_sha}")
    return json.loads(gzip.decompress(raw))


def seed_of(ci: int, s: int) -> int:
    return 68_000_000 + 1000 * ci + s


def loss_and_feasible(row: dict) -> tuple[float, int]:
    """Same point-outcome mapping as original I64-I2, without importing I64."""
    if row["best_feasible"] is None:
        if row.get("witness_checked") is not False or row.get("best_x") is not None:
            raise ValueError("Missing feasible outcome nevertheless marked witnessed")
        return 1.0, 0
    r = float(row["r"])
    f = float(row["best_feasible"])
    if not (math.isfinite(r) and r > 0 and math.isfinite(f)):
        raise ValueError("Nonfinite reference or feasible objective")
    if row.get("witness_checked") is not True or row.get("best_x") is None:
        raise ValueError("Feasible outcome has no archived independent-witness check")
    g = max((f - r) / r, 0.0)
    return g / (1.0 + g), 1


def cv90(vals: list[float]) -> float:
    if not vals:
        raise ValueError("No outcomes")
    n = max(1, math.ceil(len(vals) * .10))
    return math.fsum(sorted(vals)[-n:]) / n


def by_cell(records: dict[str, list[dict]], ci: int) -> dict:
    items: dict[str, dict] = {}
    refs = set()
    for config in CONFIGS:
        arr = records[config]
        if len(arr) != N_SEEDS or len({r["task"]["s"] for r in arr}) != N_SEEDS:
            raise ValueError(f"Missing or duplicate seed in cell {ci}/{config}")
        arr = sorted(arr, key=lambda r: r["task"]["s"])
        for s, row in enumerate(arr, start=1):
            task = row["task"]
            if not (row["ok"] and row["calls"] == BUDGET and task["config"] == config
                    and task["ci"] == ci and task["s"] == s and task["seed"] == seed_of(ci, s)):
                raise ValueError(f"Cell {ci} failed frozen task / budget / seed check: {config} / {s}")
            refs.add(float(row["r"]))
        outcomes = [loss_and_feasible(r) for r in arr]
        losses = [v[0] for v in outcomes]
        feasible = sum(v[1] for v in outcomes)
        items[config] = {"feasible_count": feasible, "p_feasible": feasible / N_SEEDS,
                         "infeasible_seeds": [r["task"]["seed"] for r in arr if r["best_feasible"] is None],
                         "cvar90": cv90(losses), "worst_three_losses": sorted(losses, reverse=True)[:3]}
    if len(refs) != 1:
        raise ValueError(f"Unmatched I/I2 references in cell {ci}: {refs}")
    first = records["gadapt"][0]["task"]
    netj = {(r["task"]["net"], r["task"]["j"]) for a in records.values() for r in a}
    if len(netj) != 1:
        raise ValueError(f"Unmatched case/j labels in cell {ci}")
    m, h, i = (items[c] for c in CONFIGS)
    return {"cell_index": ci, "network": first["net"], "j": first["j"], "reference_r": next(iter(refs)),
            "configs": items,
            "contrasts": dict(zip(CONTRASTS, (m["cvar90"] - h["cvar90"], h["p_feasible"] - m["p_feasible"],
                                             i["cvar90"] - h["cvar90"], h["p_feasible"] - i["p_feasible"]))) }


def summarize(cells: list[dict], frozen_analysis: dict | None = None) -> dict:
    if len(cells) != N_CELLS or set(c["cell_index"] for c in cells) != set(range(N_CELLS)):
        raise ValueError("Not exactly eight unique ORPD cells")
    agg = {config: {"P": math.fsum(c["configs"][config]["p_feasible"] for c in cells) / N_CELLS,
                    "cvar90": math.fsum(c["configs"][config]["cvar90"] for c in cells) / N_CELLS}
           for config in CONFIGS}
    con = {key: math.fsum(c["contrasts"][key] for c in cells) / N_CELLS for key in CONTRASTS}
    if frozen_analysis is not None:
        for c in CONFIGS:
            for m in ("P", "cvar90"):
                if abs(agg[c][m] - frozen_analysis["aggregate"][c][m]) > 1e-12:
                    raise ValueError(f"Frozen aggregate changed: {c}/{m}")
        for name in CONTRASTS:
            if abs(con[name] - frozen_analysis["contrasts"][name]["estimate"]) > 1e-12:
                raise ValueError(f"Frozen contrast changed: {name}")
    influential = max(cells, key=lambda c: abs(c["contrasts"][CONTRASTS[2]]))
    removed = influential["cell_index"]
    keep = [c for c in cells if c["cell_index"] != removed]
    contribution = influential["contrasts"][CONTRASTS[2]] / N_CELLS
    leave_one_out = [{"cell_removed": c["cell_index"], "network": c["network"], "j": c["j"],
                      "point_cv_ipop_minus_hyb": math.fsum(x["contrasts"][CONTRASTS[2]] for x in cells
                                                       if x["cell_index"] != c["cell_index"]) / (N_CELLS - 1)}
                     for c in cells]
    return {
        "analysis_level": "ORIGINAL_RUN_RECORD_POINT_RECOMPUTATION_PLUS_POST_HOC_INFLUENCE",
        "original_preregistered_decisions": {k: frozen_analysis.get(k) for k in ("H64h1", "H64h2")} if frozen_analysis else None,
        "source_git_blobs": {"I": list(I_BLOBS), "I2": list(I2_BLOBS), "I2_analysis": ANALYSIS_BLOB},
        "aggregate_from_original_run_records": agg,
        "contrasts_from_original_run_records": con,
        "dominant_cell": {"index": removed, "network": influential["network"], "j": influential["j"],
                          "contrast": influential["contrasts"][CONTRASTS[2]],
                          "contribution_to_8_cell_mean": contribution,
                          "share_of_net_negative_point_estimate": (contribution / con[CONTRASTS[2]]
                                                                  if con[CONTRASTS[2]] != 0 else None),
                          "mean_without_this_cell": math.fsum(c["contrasts"][CONTRASTS[2]] for c in keep)/len(keep)},
        "posthoc_leave_one_cell_out": leave_one_out,
        "cells": sorted(cells, key=lambda c: c["cell_index"]),
        "limitations": [
            "Removing one cell changes the estimand; original H64h2 remains opposite for eight frozen cells.",
            "Leave-one-cell-out is exploratory point-estimate sensitivity, not a simultaneous interval.",
            "Original power-flow / optimization / independent physical-witness code not re-executed.",
            "The archived witness_checked flag is checked, not the original solver output independently revalidated.",
            "This script requires 16 original compressed files and runs no optimization.",
        ],
    }


def run(repo_root: Path) -> dict:
    src = repo_root / "research" / "results"
    cells = []
    for ci in range(N_CELLS):
        prior = read_pinned(src / f"iteration64_i/run_part_{ci}.json.gz", I_BLOBS[ci])["records"]
        hyb = read_pinned(src / f"iteration64_i2/run2_part_{ci}.json.gz", I2_BLOBS[ci])["records"]
        d = {"gadapt": [r for r in prior if r["task"]["config"] == "gadapt"],
             "ipop": [r for r in prior if r["task"]["config"] == "ipop"],
             "gadapt_hyb": hyb}
        cells.append(by_cell(d, ci))
    analysis = read_pinned(src / "iteration64_i2/analysis.json.gz", ANALYSIS_BLOB)
    return summarize(cells, analysis)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    res = run(args.repo_root)
    txt = json.dumps(res, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(txt, encoding="utf8")
    else:
        print(txt, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
