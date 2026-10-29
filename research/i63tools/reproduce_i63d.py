#!/usr/bin/env python3
"""
Nezavisna reprodukcija I63-D opisnih rezultata.

Ne importuje projektne module. Jedina nestandardna zavisnost je numpy.

Primeri:
  python3 reproduce_i63d.py

  # Eksplicitni parcijalni presek:
  python3 reproduce_i63d.py \
      research/results/iteration63d/run_part_case30_2.json.gz \
      research/results/iteration63d/run_part_case30_3.json.gz
"""

import argparse
import gzip
import glob
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np


NETWORKS = ("case30", "case39", "case24_ieee_rts")
ARMS = (
    ("FR", "AD-N"),
    ("FR", "FX-T"),
    ("SP", "AD-N"),
    ("SP", "FX-T"),
)
TIE = 0.001
BUDGET = 12000
SEED_BASE = 1_700_000_000
TEST_PURPOSE = 3


def read_gz(path):
    with gzip.open(path, "rt") as fh:
        return json.load(fh)


def win_fx_over_ad(f_fx, f_ad, normalizer):
    """Frozen W_c definition from ITERATION63_PROTOCOL.md §3."""
    if f_fx is None and f_ad is None:
        return 0.5
    if f_fx is None:
        return 0.0
    if f_ad is None:
        return 1.0

    delta = (float(f_ad) - float(f_fx)) / normalizer
    if delta > TIE:
        return 1.0
    if delta < -TIE:
        return 0.0
    return 0.5


def normalized_gap(value, normalizer):
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Non-finite best_feasible")
    return (value - normalizer) / normalizer


def expected_seed(network, j, s):
    i = NETWORKS.index(network)
    return (
        SEED_BASE
        + 10**7 * TEST_PURPOSE
        + 10**6 * i
        + 10**4 * j
        + s
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "parts",
        nargs="*",
        help="Explicit run_part_*.json.gz files; default is every part in --parts-dir",
    )
    parser.add_argument(
        "--source",
        default="research/results/iteration63",
        help="Directory containing frozen roster, normalizers, fxt and power",
    )
    parser.add_argument(
        "--parts-dir",
        default="research/results/iteration63d",
    )
    args = parser.parse_args()

    source = args.source
    normalizers = read_gz(
        os.path.join(source, "normalizers.json.gz")
    )["r"]
    roster = read_gz(os.path.join(source, "roster.json.gz"))
    expected_cells = {tuple(x) for x in roster["test"]}
    chosen_n = int(
        read_gz(os.path.join(source, "power.json.gz"))["chosen_n"]
    )
    chosen_fxt = read_gz(
        os.path.join(source, "fxt.json.gz")
    )["chosen"]

    paths = args.parts or sorted(
        glob.glob(os.path.join(args.parts_dir, "run_part_*.json.gz"))
    )
    if not paths:
        raise SystemExit("No run_part_*.json.gz files found")

    units = {}
    seen_cells = set()

    for path in paths:
        part = read_gz(path)
        records = part.get("records")
        if not isinstance(records, list):
            raise ValueError(f"{path}: missing records list")

        for rec in records:
            task = rec["task"]
            network = task["network"]
            j = int(task["j"])
            s = int(task["s"])
            arm = (task["cht"], task["arm"])
            cell = (network, j)
            key = (network, j, s)

            if cell not in expected_cells:
                raise ValueError(f"Unexpected cell: {cell}")
            if arm not in ARMS:
                raise ValueError(f"Unexpected arm: {key}, {arm}")
            if rec.get("ok") is not True:
                raise ValueError(f"Technical failure: {key}, {arm}")
            if rec.get("calls") != BUDGET:
                raise ValueError(f"Wrong call count: {key}, {arm}")
            if task.get("budget") != BUDGET:
                raise ValueError(f"Wrong task budget: {key}, {arm}")
            if task.get("purpose") != "test":
                raise ValueError(f"Wrong purpose: {key}, {arm}")
            if task.get("seed") != expected_seed(network, j, s):
                raise ValueError(f"Wrong seed: {key}, {arm}")
            if task.get("reference") is not None:
                raise ValueError(f"Unexpected reference: {key}, {arm}")
            if task.get("stop") is not False:
                raise ValueError(f"Unexpected early stop: {key}, {arm}")

            expected_fixed = (
                chosen_fxt[task["cht"]]
                if task["arm"] == "FX-T"
                else None
            )
            if task.get("fixed") != expected_fixed:
                raise ValueError(f"Wrong fixed vector: {key}, {arm}")

            unit = units.setdefault(key, {})
            if arm in unit:
                raise ValueError(f"Duplicate record: {key}, {arm}")
            unit[arm] = rec
            seen_cells.add(cell)

    by_cell = defaultdict(list)
    for key, unit in units.items():
        if set(unit) != set(ARMS):
            missing = set(ARMS) - set(unit)
            raise ValueError(f"Incomplete four-vector {key}: {missing}")
        by_cell[key[:2]].append((key[2], unit))

    expected_seeds = set(range(1, chosen_n + 1))
    for cell, rows in by_cell.items():
        seeds = {s for s, _ in rows}
        if seeds != expected_seeds:
            raise ValueError(
                f"{cell}: expected seeds 1..{chosen_n}; "
                f"missing={sorted(expected_seeds - seeds)[:10]}, "
                f"extra={sorted(seeds - expected_seeds)[:10]}"
            )

    cell_d = {}
    cell_output = {}

    for cell in sorted(by_cell):
        network, j = cell
        normalizer = float(normalizers[f"{network}|{j}"])
        if not math.isfinite(normalizer) or normalizer <= 0:
            raise ValueError(f"Invalid normalizer for {cell}")

        d_values = []
        w_fr_values = []
        w_sp_values = []
        gaps = {arm: [] for arm in ARMS}

        for _, unit in sorted(by_cell[cell]):
            w_fr = win_fx_over_ad(
                unit[("FR", "FX-T")]["best_feasible"],
                unit[("FR", "AD-N")]["best_feasible"],
                normalizer,
            )
            w_sp = win_fx_over_ad(
                unit[("SP", "FX-T")]["best_feasible"],
                unit[("SP", "AD-N")]["best_feasible"],
                normalizer,
            )

            w_fr_values.append(w_fr)
            w_sp_values.append(w_sp)
            d_values.append(w_fr - w_sp)

            for arm in ARMS:
                gaps[arm].append(
                    normalized_gap(
                        unit[arm]["best_feasible"],
                        normalizer,
                    )
                )

        d_array = np.asarray(d_values, dtype=float)
        cell_d[cell] = d_array

        unique, counts = np.unique(d_array, return_counts=True)
        row = {
            "n": int(d_array.size),
            "d_mean": float(np.mean(d_array)),
            "d_counts": {
                f"{value:g}": int(count)
                for value, count in zip(unique, counts)
            },
            "W_FR_mean": float(np.mean(w_fr_values)),
            "W_SP_mean": float(np.mean(w_sp_values)),
            "arms": {},
        }

        for arm in ARMS:
            values = gaps[arm]
            finite = [x for x in values if x is not None]
            row["arms"][f"{arm[0]}|{arm[1]}"] = {
                "feasible": len(finite) / len(values),
                "median_gap": (
                    float(np.median(np.asarray(finite, dtype=float)))
                    if finite
                    else None
                ),
            }

        cell_output[f"{network}|{j}"] = row

    missing_cells = sorted(expected_cells - seen_cells)
    unexpected_cells = sorted(seen_cells - expected_cells)
    if unexpected_cells:
        raise ValueError(f"Unexpected cells: {unexpected_cells}")

    output = {
        "status": "complete" if not missing_cells else "partial",
        "chosen_n": chosen_n,
        "cells": cell_output,
        "missing_cells": [list(x) for x in missing_cells],
    }

    # Global quantities are forbidden for an incomplete roster.
    if not missing_cells:
        network_means = {}
        for network in NETWORKS:
            means = [
                float(np.mean(values))
                for cell, values in cell_d.items()
                if cell[0] == network
            ]
            if not means:
                raise ValueError(f"No cells for network {network}")
            network_means[network] = float(np.mean(means))

        theta_63 = float(
            np.mean([network_means[n] for n in NETWORKS])
        )
        leave_one_out = {
            network: float(
                np.mean([
                    network_means[other]
                    for other in NETWORKS
                    if other != network
                ])
            )
            for network in NETWORKS
        }

        output["theta_63"] = theta_63
        output["network_means"] = network_means
        output["leave_one_network_out"] = leave_one_out
    else:
        output["global_estimates"] = None
        output["note"] = (
            "theta_63, network means and leave-one-network-out "
            "are intentionally omitted for an incomplete roster"
        )

    json.dump(
        output,
        sys.stdout,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
