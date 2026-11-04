"""Synthetic matched-flag accounting tests; no source simulation/optimization."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i55_paired_function_context_audit as method


def fixture():
    cells = []
    for dim in (2, 10):
        for seed in range(6000, 6005):
            for func in ("sphere", "rastrigin", "plateau"):
                flags = dict.fromkeys(method.base.FLAGS, 0)
                if func == "plateau":
                    flags["C1"] = 3
                if func == "sphere" and dim == 2 and seed == 6000:
                    flags["C1"] = 1
                    flags["C2"] = 1
                if func == "rastrigin" and dim == 10 and seed == 6000:
                    flags["C1"] = 2
                cells.append({
                    "function": func, "d": dim, "seed": seed,
                    "flags": flags, "calls": 10, "error": None,
                })
    return {"samplelib": {"library": "samplelib", "cells": cells}}


class MatchedContextTests(unittest.TestCase):
    def test_match_entire_library_and_count_overlap(self):
        r = method.paired_comparison(fixture())
        self.assertEqual(r["nominal_strata"], 10)
        self.assertEqual(r["complete_three_function_strata"], 10)
        c = r["overall_matched"]["C1"]["plateau_vs_sphere"]
        self.assertEqual(c["pairs"], 10)
        self.assertEqual((c["left_only"], c["right_only"],
                          c["both_present"], c["neither_present"]),
                         (9, 0, 1, 0))
        self.assertEqual((c["left_events"], c["right_events"]), (30, 1))
        self.assertEqual((c["left_original_calls"], c["right_original_calls"]),
                         (100, 100))
        self.assertEqual(r["library_direction_counts"]["C1"]["plateau_vs_sphere"]
                         ["more_left_flagged_cells"], ["samplelib"])

    def test_right_only_is_not_a_plateau_event(self):
        r = method.paired_comparison(fixture())
        t = r["overall_matched"]["C2"]["plateau_vs_sphere"]
        self.assertEqual((t["left_only"], t["right_only"],
                          t["neither_present"]), (0, 1, 9))
        self.assertEqual(r["library_direction_counts"]["C2"]["plateau_vs_sphere"]
                         ["more_right_flagged_cells"], ["samplelib"])

    def test_skip_incomplete_historical_stratum(self):
        data = fixture()
        for r in data["samplelib"]["cells"]:
            if r["d"] == 10 and r["seed"] == 6004 and r["function"] == "sphere":
                r["error"] = "historical failed source"
        result = method.paired_comparison(data)
        self.assertEqual(result["nominal_strata"], 10)
        self.assertEqual(result["complete_three_function_strata"], 9)
        self.assertEqual(len(result["incomplete_strata"]), 1)
        self.assertEqual(result["overall_matched"]["C1"]["plateau_vs_sphere"]["pairs"], 9)
        self.assertEqual(result["overall_matched"]["C1"]["plateau_vs_rastrigin"]["pairs"], 10)
        self.assertEqual(result["overall_matched"]["C1"]["sphere_vs_rastrigin"]["pairs"], 9)

    def test_duplicate_cell_is_rejected(self):
        data = fixture()
        data["samplelib"]["cells"].append(copy.deepcopy(data["samplelib"]["cells"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            method.paired_comparison(data)

    def test_missing_nominal_cell_is_rejected(self):
        data = fixture()
        data["samplelib"]["cells"].pop()
        with self.assertRaisesRegex(ValueError, "Missing nominal"):
            method.paired_comparison(data)

    def test_function_different_calls_preserved_not_silently_normalized(self):
        data = fixture()
        for r in data["samplelib"]["cells"]:
            if r["function"] == "plateau":
                r["calls"] = 20
        out = method.paired_comparison(data)
        c = out["overall_matched"]["C1"]["plateau_vs_sphere"]
        self.assertEqual((c["left_original_calls"], c["right_original_calls"]),
                         (200, 100))
        self.assertEqual((c["left_only"], c["both_present"]), (9, 1))


if __name__ == "__main__":
    unittest.main()
