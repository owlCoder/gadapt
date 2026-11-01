"""Tool validation for I49 (ITERATION49_PROTOCOL.md §6): planted faults and the GAdapt control.

Run in the pinned audit environment with the repository on PYTHONPATH.
"""
import unittest

import numpy as np

import research.iteration49_integrity_audit as m


class IntegrityAuditValidationTest(unittest.TestCase):
    def test_planted_faults_detected_exactly_and_clean_reference_passes(self):
        report, passed = m.validate()
        for name, row in report.items():
            self.assertTrue(row["ok"], (name, row))
        self.assertTrue(passed)

    def test_transformed_problem_is_the_same_problem(self):
        p = m.Problem("rastrigin", 4)
        t = m.Problem("rastrigin", 4, scale=[1, 100, 1e4, 1], shift=[0, 1000, 2000, 3000])
        u = np.array([0.1, 0.5, 0.9, 0.3])
        x = p.lo + u * (p.hi - p.lo)
        y = t.lo + u * (t.hi - t.lo)
        self.assertAlmostEqual(p(x), t(y), places=9)

    def test_classifier_counts_out_of_bounds_and_post_calls(self):
        p = m.Problem("sphere", 2)
        rec = m.Recorder(p)
        rec(np.array([6.0, 0.0]))
        rec(np.array([1.0, 1.0]))
        rec.phase = "post"
        rec(np.array([1.0, 1.0]))
        flags, n = m.classify(rec.calls, dict(x=[1.0, 1.0], f=p([1.0, 1.0]), reported_evals=2, documented_max=2), p)
        self.assertEqual((n, flags["C3"], flags["C2"], flags["C4"], flags["C5"], flags["D2"]), (3, 1, 1, 1, 1, 1))


if __name__ == "__main__":
    unittest.main()
