"""Synthetic fail-closed I55 620-source flag-census tests; not raw NPZ replays."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i55_620_flag_census as census


def full_attestation():
    return {
        "full_attestation_pass": True, "status": "PASS",
        "manifest_git_blob": census.MANIFEST_SHA,
        "original_git_tree": {
            "source_commit": census.SOURCE_SHA,
            "original_root_tree_sha1": census.SOURCE_TREE,
            "exact_tree_manifest_match": True,
        },
        "npz_byte_gate": {
            "raw_bytes_verified": 620, "full_git_blob_pass": True,
            "corrupt": [], "missing": [],
        },
        "original_trace_replay": {"npz": {
            "checked": 620, "frozen_objective_value_calls_checked": 295445,
            "full_raw_trace_pass": True, "frozen_objective_values_pass": True,
            "cells_with_flag_difference": 0, "errors": [],
        }},
    }


class FlagPopulationTests(unittest.TestCase):
    def test_valid_full_attestation_gate(self):
        census.check_attestation(full_attestation())

    def test_false_pass_rejected(self):
        a = full_attestation()
        a["full_attestation_pass"] = False
        with self.assertRaisesRegex(ValueError, "not PASS"):
            census.check_attestation(a)

    def test_missing_one_raw_npz_rejected(self):
        a = full_attestation()
        a["original_trace_replay"]["npz"]["checked"] = 619
        with self.assertRaisesRegex(ValueError, "numerical"):
            census.check_attestation(a)

    def test_missing_source_byte_rejected(self):
        a = full_attestation()
        a["npz_byte_gate"]["raw_bytes_verified"] = 619
        with self.assertRaisesRegex(ValueError, "byte provenance"):
            census.check_attestation(a)

    def test_modified_original_root_rejected(self):
        a = full_attestation()
        a["original_git_tree"]["original_root_tree_sha1"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "tree provenance"):
            census.check_attestation(a)

    def test_flag_mismatch_rejected(self):
        a = full_attestation()
        a["original_trace_replay"]["npz"]["cells_with_flag_difference"] = 1
        with self.assertRaisesRegex(ValueError, "numerical"):
            census.check_attestation(a)

    def test_per_cell_not_event_count(self):
        t = census.empty_tally()
        first = {"calls": 20, "flags": dict.fromkeys(census.FLAGS, 0)}
        first["flags"]["C1"] = 4
        second = {"calls": 30, "flags": dict.fromkeys(census.FLAGS, 0)}
        census.add_cell(t, first)
        census.add_cell(t, second)
        self.assertEqual(t["original_calls"], 50)
        self.assertEqual(t["valid_cells"], 2)
        self.assertEqual(t["flagged_cells"]["C1"], 1)
        self.assertEqual(t["flag_occurrences"]["C1"], 4)
        self.assertEqual(t["cells_with_any_flag"], 1)

    def test_missing_original_grid_rejected(self):
        raw = {lib: {"library": lib, "cells": []}
               for lib in census.source.I55_BLOBS}
        with self.assertRaisesRegex(ValueError, "30-cell roster"):
            census.census(raw)


if __name__ == "__main__":
    unittest.main()
