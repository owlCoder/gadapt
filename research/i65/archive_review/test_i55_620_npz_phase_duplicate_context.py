"""Synthetic, no-optimizer, adversarial I55 raw phase/C1/C2 tests."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i55_620_npz_phase_duplicate_context as method
import i55_npz_cross_archive_verifier as frozen


class I55PhaseContextTests(unittest.TestCase):
    def test_original_corner_and_duplicate_semantics_by_phase(self):
        x = np.array([[-5., -5.], [-5., -5.], [5., 5.],
                      [5., 5.], [0., 0.], [0., 0.]], dtype=np.float64)
        phase = np.array([0, 1, 0, 1, 0, 1], dtype=np.int8)
        got = method.classify(x, phase)
        self.assertEqual((got["search_calls"], got["post_calls"]), (3, 3))
        self.assertEqual((got["C1_search"], got["C1_post"]), (2, 2))
        self.assertEqual((got["C2_search"], got["C2_post"]), (0, 3))
        self.assertEqual((got["C1_C2_search"], got["C1_C2_post"]), (0, 2))
        self.assertEqual(got["C2_first_search_current_post"], 3)
        orig = frozen.classify_arrays(x, np.zeros(6), phase,
                                      np.array([]), None, None, None)
        self.assertEqual(orig["C1"], got["C1_search"] + got["C1_post"])
        self.assertEqual(orig["C2"], got["C2_search"] + got["C2_post"])
        self.assertEqual(orig["C5"], got["post_calls"])

    def test_first_post_can_be_revisited_during_search_and_post(self):
        x = np.array([[2., 2.], [2., 2.], [2., 2.]], dtype=np.float64)
        phase = np.array([1, 0, 1], dtype=np.int8)
        out = method.classify(x, phase)
        self.assertEqual(out["C2_first_post_current_search"], 1)
        self.assertEqual(out["C2_first_post_current_post"], 1)
        self.assertEqual(out["C2_first_search_current_search"], 0)

    def test_first_phase_not_most_recent_phase(self):
        x = np.array([[1., 1.], [1., 1.], [1., 1.]], dtype=np.float64)
        phase = np.array([0, 1, 1], dtype=np.int8)
        out = method.classify(x, phase)
        self.assertEqual(out["C2_first_search_current_post"], 2)
        self.assertEqual(out["C2_first_post_current_post"], 0)

    def test_signed_zero_binary_exactness(self):
        x = np.array([[0., 0.], [-0., 0.], [0., 0.]], dtype=np.float64)
        phase = np.zeros(3, dtype=np.int8)
        out = method.classify(x, phase)
        self.assertEqual(out["C2_search"], 1)
        self.assertEqual(out["C1_search"], 0)

    def test_mixed_and_near_corner_not_c1(self):
        x = np.array([[-5., 5.], [-5., -5. + 1e-12],
                      [5., 5.], [-5., -5.]], dtype=np.float64)
        p = np.zeros(4, dtype=np.int8)
        out = method.classify(x, p)
        self.assertEqual(out["C1_search"], 2)
        self.assertEqual(out["C2_search"], 0)

    def test_nonbinary_phase_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            method.classify(np.zeros((2, 2), dtype=np.float64),
                            np.array([0, 2], dtype=np.int8))

    def test_nans_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "non-finite"):
            method.classify(np.array([[0., float("nan")]], dtype=np.float64),
                            np.array([0], dtype=np.int8))

    def test_wrong_dtype_dim_and_phase_shape_fail(self):
        x = np.zeros((3, 2), dtype=np.float64)
        p = np.zeros(3, dtype=np.int8)
        with self.assertRaisesRegex(ValueError, "dtype/dimension"):
            method.classify(x.astype(np.float32), p)
        with self.assertRaisesRegex(ValueError, "dtype/dimension"):
            method.classify(np.zeros((3, 3), dtype=np.float64), p)
        with self.assertRaisesRegex(ValueError, "dtype/shape"):
            method.classify(x, np.zeros(2, dtype=np.int8))

    def test_accumulate_does_not_confuse_event_and_call_counts(self):
        a = method.zero()
        b = method.classify(np.array([[5., 5.], [5., 5.]], dtype=np.float64),
                            np.array([0, 1], dtype=np.int8))
        method.accumulate(a, b)
        method.accumulate(a, b)
        self.assertEqual(a["calls"], 4)
        self.assertEqual(a["C1_search"], 2)
        self.assertEqual(a["C1_post"], 2)
        self.assertEqual(a["C2_post"], 2)
        self.assertEqual(a["C1_C2_post"], 2)


if __name__ == "__main__":
    unittest.main()
