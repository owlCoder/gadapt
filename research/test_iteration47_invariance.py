"""Checks for I47 (ITERATION47_PROTOCOL.md, "Kontrole pre pokretanja")."""
import subprocess
import unittest
import warnings

import numpy as np
from pypower.api import case30, ppoption, runpf
from pypower.idx_gen import PG

from research.iteration47_invariance import Counted, Dispatch, OVER_BUDGET, synthetic_value

warnings.filterwarnings("ignore")


class DispatchEvaluatorTest(unittest.TestCase):
    def test_original_dispatch_reproduces_runpf_and_gencost(self):
        d = Dispatch("case30")
        x = d.base["gen"][d.variables, PG]
        info = d.evaluate(x)
        solved, ok = runpf(case30(), ppoption(VERBOSE=0, OUT_ALL=0, ENFORCE_Q_LIMS=0, PF_TOL=1e-8, PF_MAX_IT=40))
        self.assertTrue(ok and info["converged"])
        c = d.base["gencost"][d.online, 4:7]
        pg = solved["gen"][d.online, PG]
        self.assertAlmostEqual(info["cost"], float(np.sum(c[:, 0] * pg ** 2 + c[:, 1] * pg + c[:, 2])), places=6)

    def test_mw_and_pu_give_identical_scores(self):
        d = Dispatch("case57")
        lower, upper = np.array(d.bounds_mw).T
        x = lower + 0.37 * (upper - lower)
        a, b = Counted(d, 5), Counted(d, 5)
        # (x / baseMVA) * baseMVA differs from x only in the last bit
        self.assertAlmostEqual(a.mw(x) / b.mw((x / d.base_mva) * d.base_mva), 1.0, places=12)

    def test_budget_accounting(self):
        d = Dispatch("case14")
        counted = Counted(d, 2)
        x = np.array(d.bounds_mw).mean(axis=1)
        counted.mw(x), counted.mw(x)
        self.assertEqual(counted.mw(x), OVER_BUDGET)
        self.assertEqual((counted.calls, counted.over_budget), (2, 1))

    def test_slack_is_not_a_variable(self):
        for name in ("case14", "case118"):
            d = Dispatch(name)
            self.assertEqual(len(d.slack), 1)
            self.assertNotIn(d.slack[0], d.variables)

    def test_synthetic_functions(self):
        self.assertEqual(synthetic_value("sphere", np.array([1.0, 2.0])), 5.0)
        self.assertAlmostEqual(synthetic_value("ellipsoid", np.array([1.0, 1.0])), 1001.0)

    def test_library_at_cc2f357_unchanged(self):
        diff = subprocess.run(["git", "diff", "--stat", "cc2f357", "--", "gadapt/"],
                              capture_output=True, text=True, check=True).stdout
        self.assertEqual(diff.strip(), "")


if __name__ == "__main__":
    unittest.main()
