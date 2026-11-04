"""Source-faithful I64-R off-Git recovery gates; entirely synthetic tests.

This file was historically pytest-only and omitted from the I55 read-only CI.
It now uses standard-library unittest, with the original four-key R task schema
and the untouched historical E/R source Git blob identities. No raw R records,
objective evaluations, optimiser, AC/PF/OPF, or COCO experiment is executed.
"""
from __future__ import annotations

import copy
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i64_r_off_git_raw_recovery_gate import (
    BUILDS, PAIRS, blob_sha1, validate_r_records, verify_lineage,
)

SOURCE_GIT_BLOBS = {
    "research/i64/r_study.py": "4e8e33e07894ae1006c03cb0ada3566254fb9907",
    "research/i64/e_study.py": "b72a4bae65967c925a7f0a683a50f5144270ba34",
    "research/i64/e_common.py": "3aab99773a7e4a95b7972a3c8061c50bd471618d",
    "research/ITERATION64_R_SPEC.md": "ab2f8fb75d318a1e0f9663932912df7049cbc9a6",
}


class OriginalRRecoveryLegacyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Purely synthetic 21 x 2 x 100 task shell. The authentic E freeze
        # has no tuned GAdapt-M entry; R assigns params=None to GAdapt.
        cls.records = []
        for k, (_, d) in enumerate(PAIRS):
            for cfg in ("gadapt", "ipop"):
                for s in range(1, 101):
                    cls.records.append({
                        "task": {
                            "k": k, "config": cfg,
                            "seed": 67_000_000 + 1000 * (63 + k) + s,
                            "params": None if cfg == "gadapt" else {"sigma0": 0.3},
                        },
                        "calls": 12000, "ok": True,
                        "events": [[1, 30.0], [25, 20.0], [12000, 1.0]],
                        "best_f": 1.0,
                        "best_y": [0.0] * d,
                    })

    def tampered(self, idx, mutate):
        rows = self.records.copy()
        rows[idx] = copy.deepcopy(rows[idx])
        mutate(rows[idx])
        return rows

    def test_frozen_pair_roster(self):
        self.assertEqual(len(PAIRS), 21)
        self.assertEqual(PAIRS[0], ("sphere", 2))
        self.assertEqual(PAIRS[-1], ("booth", 2))

    def test_complete_source_shaped_synthetic_roster(self):
        report = validate_r_records(self.records)
        self.assertEqual(report["records_checked"], 4200)
        self.assertEqual(report["event_integrity"], "PASS")
        self.assertEqual(report["objective_calls_per_run"], 12000)

    def test_missing_original_row_rejected(self):
        with self.assertRaisesRegex(ValueError, "record count"):
            validate_r_records(self.records[:-1])

    def test_duplicate_seed_rejected(self):
        rows = self.tampered(1, lambda r: r["task"].update(
            seed=self.records[0]["task"]["seed"]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_r_records(rows)

    def test_wrong_seed_rejected(self):
        with self.assertRaisesRegex(ValueError, "seed"):
            validate_r_records(self.tampered(
                0, lambda r: r["task"].update(seed=1)))

    def test_non_increasing_event_calls_rejected(self):
        with self.assertRaisesRegex(ValueError, "event call"):
            validate_r_records(self.tampered(
                0, lambda r: r.update(events=[[5, 10.0], [5, 9.0]])))

    def test_nonfinite_event_rejected(self):
        with self.assertRaisesRegex(ValueError, "Non-finite"):
            validate_r_records(self.tampered(
                0, lambda r: r.update(events=[[1, math.nan]])))

    def test_failed_original_run_status_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsuccessful"):
            validate_r_records(self.tampered(
                0, lambda r: r.update(ok=False)))

    def test_worsening_best_so_far_rejected(self):
        with self.assertRaisesRegex(ValueError, "not strictly improved"):
            validate_r_records(self.tampered(
                0, lambda r: r.update(events=[[1, 1.0], [2, 100.0]])))

    def test_manifest_build_consensus_rejected_when_mismatched(self):
        manifest = {name: "synthetic:" + name for name in BUILDS}
        raw = {"e_inputs": {"part": "test-digest"}, "manifest": manifest}
        analysis = {"e_inputs": raw["e_inputs"]}
        check = {"e_inputs": raw["e_inputs"], "manifest": manifest,
                 "results": [{"identical": True} for _ in range(5)]}
        self.assertEqual(verify_lineage(raw, analysis, check)
                         ["check_repro_witnesses"], 5)
        changed = copy.deepcopy(check)
        changed["manifest"]["r_settings"] = "wrong-synthetic-settings"
        with self.assertRaisesRegex(ValueError, "build mismatch"):
            verify_lineage(raw, analysis, changed)

    def test_five_archived_repro_witnesses_cannot_contain_failure(self):
        manifest = {name: "synthetic:" + name for name in BUILDS}
        raw = {"e_inputs": {"part": "test-digest"}, "manifest": manifest}
        check = {"e_inputs": raw["e_inputs"], "manifest": manifest,
                 "results": [{"identical": True} for _ in range(5)]}
        check["results"][2]["identical"] = False
        with self.assertRaisesRegex(ValueError, "five E-R"):
            verify_lineage(raw, {"e_inputs": raw["e_inputs"]}, check)

    def test_git_blob_sha1_has_real_git_framing(self):
        self.assertEqual(blob_sha1(b"hello"),
                         "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_original_E_R_budget_and_protocol_files_remain_byte_identical(self):
        repo = Path(__file__).resolve().parents[3]
        for rel_path, expected_blob in SOURCE_GIT_BLOBS.items():
            with self.subTest(original=rel_path):
                self.assertEqual(blob_sha1((repo / rel_path).read_bytes()),
                                 expected_blob)


if __name__ == "__main__":
    unittest.main()
