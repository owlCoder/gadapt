"""Synthetic-only source-contract tests for 620 original C1 signed corners.

No new optimizer, PF/OPF, COCO or objective-function evaluation.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i55_620_corner_direction_source_audit as corner
import i55_620_npz_phase_duplicate_context as original_phase


class FullCornerSignAndRepeatTests(unittest.TestCase):
    def test_negative_and_positive_first_and_repeat_search(self):
        x = np.array([[-5., -5.], [-5., -5.], [5., 5.],
                      [5., 5.], [-5., 5.], [0., 0.]], dtype=np.float64)
        p = np.zeros(len(x), dtype=np.int8)
        got = corner.count_signed_corners(x, p)
        self.assertEqual(got["negative_first_search"], 1)
        self.assertEqual(got["negative_repeat_search"], 1)
        self.assertEqual(got["positive_first_search"], 1)
        self.assertEqual(got["positive_repeat_search"], 1)
        self.assertEqual(corner.total(got), 4)
        self.assertEqual(corner.total(got, frequency="repeat"), 2)
        ref = original_phase.classify(x, p)
        self.assertEqual(ref["C1_C2_search"], 2)
        self.assertEqual(ref["C1_search"], 4)

    def test_first_search_to_post_and_post_to_search_distinct(self):
        x = np.array([[5., 5.], [5., 5.], [-5., -5.],
                      [-5., -5.], [-5., -5.]], dtype=np.float64)
        p = np.array([0, 1, 1, 0, 1], dtype=np.int8)
        got = corner.count_signed_corners(x, p)
        self.assertEqual(got["positive_first_search"], 1)
        self.assertEqual(got["positive_repeat_post"], 1)
        self.assertEqual(got["negative_first_post"], 1)
        self.assertEqual(got["negative_repeat_search"], 1)
        self.assertEqual(got["negative_repeat_post"], 1)
        self.assertEqual(corner.total(got, stage="post"), 3)

    def test_ten_dimensional_exact_full_corners(self):
        x = np.array([[-5.] * 10, [5.] * 10,
                      [-5.] * 10, [5.] * 10], dtype=np.float64)
        p = np.zeros(4, dtype=np.int8)
        got = corner.count_signed_corners(x, p)
        self.assertEqual(corner.total(got, frequency="first"), 2)
        self.assertEqual(corner.total(got, frequency="repeat"), 2)
        self.assertEqual(corner.total(got, side="negative"), 2)
        self.assertEqual(corner.total(got, side="positive"), 2)

    def test_mixed_coordinate_sign_not_a_full_corner(self):
        x = np.array([[-5., 5.], [5., -5.], [-5., -5. + 1e-12],
                      [5. - 1e-12, 5.]], dtype=np.float64)
        self.assertEqual(corner.total(corner.count_signed_corners(
            x, np.zeros(4, dtype=np.int8))), 0)

    def test_corner_after_any_number_of_noncorners_is_first(self):
        x = np.array([[0., 0.], [1., 2.], [0., 0.],
                      [-5., -5.], [0., 0.], [-5., -5.]], dtype=np.float64)
        got = corner.count_signed_corners(x, np.zeros(6, dtype=np.int8))
        self.assertEqual((got["negative_first_search"],
                          got["negative_repeat_search"]), (1, 1))

    def test_nonfinite_coordinate_rejected(self):
        x = np.array([[-5., float("nan")]], dtype=np.float64)
        with self.assertRaisesRegex(ValueError, "non-finite"):
            corner.count_signed_corners(x, np.array([0], dtype=np.int8))

    def test_wrong_dtype_or_dimension_rejected(self):
        p = np.zeros(1, dtype=np.int8)
        with self.assertRaisesRegex(ValueError, "coordinate"):
            corner.count_signed_corners(np.zeros((1, 3), dtype=np.float64), p)
        with self.assertRaisesRegex(ValueError, "coordinate"):
            corner.count_signed_corners(np.zeros((1, 2), dtype=np.float32), p)

    def test_malformed_phase_array_rejected(self):
        x = np.zeros((2, 2), dtype=np.float64)
        with self.assertRaisesRegex(ValueError, "phase"):
            corner.count_signed_corners(x, np.zeros(2, dtype=np.int64))
        with self.assertRaisesRegex(ValueError, "phase"):
            corner.count_signed_corners(x, np.zeros(1, dtype=np.int8))
        with self.assertRaisesRegex(ValueError, "phase"):
            corner.count_signed_corners(x, np.array([0, 3], dtype=np.int8))

    def test_accumulate_preserves_side_and_first_repeat(self):
        a = corner.zero()
        b = corner.count_signed_corners(np.array([
            [5., 5.], [-5., -5.], [5., 5.]], dtype=np.float64),
            np.array([0, 0, 1], dtype=np.int8))
        corner.add(a, b)
        corner.add(a, b)
        self.assertEqual(corner.total(a), 6)
        self.assertEqual(corner.total(a, side="negative"), 2)
        self.assertEqual(corner.total(a, side="positive"), 4)
        self.assertEqual(corner.total(a, frequency="repeat"), 2)
        self.assertEqual(corner.total(a, stage="post"), 2)


if __name__ == "__main__":
    unittest.main()
