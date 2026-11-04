"""Frozen I64-R Budget.events strict-improvement record gate; synthetic only.

No original R seed-level source is available: these are contract tests
against original research/i64/e_common.py Budget.__call__ and r_study.py.
No optimizer, physics, PF/OPF or COCO call.
"""
from __future__ import annotations
import copy
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i64_r_off_git_raw_recovery_gate import PAIRS, validate_r_records


class I64ROriginalBudgetSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = []
        for k, (_, dimension) in enumerate(PAIRS):
            for s in range(1, 101):
                for cfg in ("gadapt", "ipop"):
                    cls.records.append({
                        "task": {"k": k, "config": cfg,
                                 "seed": 67_000_000 + 1000 * (63 + k) + s,
                                 "params": None},
                        "ok": True, "calls": 12000,
                        "events": [[1, 30.], [20, 20.], [12000, 1.]],
                        "best_f": 1.0,
                        "best_y": [0.0] * dimension,
                    })

    def tampered(self, change):
        rows = self.records.copy()
        rows[0] = copy.deepcopy(rows[0])
        change(rows[0])
        return rows

    def test_valid_complete_synthetic_original_budget_shape(self):
        x = validate_r_records(self.records)
        self.assertEqual(x["records_checked"], 4200)
        self.assertEqual(x["event_integrity"], "PASS")
        self.assertEqual(x["objective_calls_per_run"], 12000)
        self.assertNotIn("physical_calls_per_run", x)

    def test_rejects_equal_best_value_event(self):
        with self.assertRaisesRegex(ValueError, "not strictly improved"):
            validate_r_records(self.tampered(
                lambda r: r.update(events=[[1, 30.], [2, 30.], [12000, 1.]])))

    def test_rejects_tiny_best_value_increase(self):
        with self.assertRaisesRegex(ValueError, "not strictly improved"):
            validate_r_records(self.tampered(
                lambda r: r.update(events=[[1, 30.], [2, 30. + 1e-10],
                                            [12000, 1.]])))

    def test_rejects_wrong_saved_final_best_f(self):
        with self.assertRaisesRegex(ValueError, "original best_f"):
            validate_r_records(self.tampered(lambda r: r.update(best_f=0.99)))

    def test_rejects_missing_saved_final_best_f(self):
        with self.assertRaisesRegex(ValueError, "original best_f"):
            validate_r_records(self.tampered(lambda r: r.pop("best_f")))

    def test_rejects_wrong_saved_best_y_dimension(self):
        with self.assertRaisesRegex(ValueError, "best_y dimension"):
            validate_r_records(self.tampered(lambda r: r.update(best_y=[0.] * 3)))

    def test_rejects_nonfinite_saved_best_y(self):
        with self.assertRaisesRegex(ValueError, "best_y dimension"):
            validate_r_records(self.tampered(
                lambda r: r.update(best_y=[float("nan"), 1.])))

    def test_rejects_nonfinite_saved_best_f(self):
        with self.assertRaisesRegex(ValueError, "original best_f"):
            validate_r_records(self.tampered(lambda r: r.update(best_f=math.inf)))

    def test_rejects_bad_event_order(self):
        with self.assertRaisesRegex(ValueError, "event call count"):
            validate_r_records(self.tampered(
                lambda r: r.update(events=[[1, 30.], [1, 20.], [12000, 1.]])))

    def test_rejects_task_repetition(self):
        def duplicate(r):
            r["task"]["config"] = self.records[1]["task"]["config"]
        with self.assertRaisesRegex(ValueError, "Duplicate R task"):
            validate_r_records(self.tampered(duplicate))


if __name__ == "__main__":
    unittest.main()
