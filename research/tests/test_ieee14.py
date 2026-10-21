"""Physics and budget checks for IEEE14 reference-system research workflow."""
import math
import random
import unittest

import numpy as np
from pypower.idx_bus import PD, VM
from pypower.idx_gen import PG, VG
from pypower.api import runpf

from research.ieee14_voltage import IEEE14VoltageDispatch, Recorder, evaluate_method


class IEEE14Tests(unittest.TestCase):
    def test_standard_case_has_five_generator_controls(self):
        case = IEEE14VoltageDispatch()
        self.assertEqual(case.n, 5)
        self.assertEqual(len(case.base["bus"]), 14)

    def test_original_reference_has_ac_losses_and_finite_violation(self):
        case = IEEE14VoltageDispatch()
        result = case.evaluate(case.base["gen"][:, VG])
        self.assertTrue(result["converged"])
        self.assertTrue(math.isfinite(result["loss"]))
        self.assertGreater(result["loss"], 0)
        self.assertGreater(result["q_max"], 0)
        self.assertGreater(result["v_max"], 0)

    def test_physical_power_balance_from_ac_solver(self):
        case = IEEE14VoltageDispatch()
        solved, success = runpf(case.base, case.settings)
        self.assertTrue(success)
        branch_losses = float(np.sum(solved["branch"][:, 13] + solved["branch"][:, 15]))
        gen_minus_load = float(np.sum(solved["gen"][:, PG]) - np.sum(solved["bus"][:, PD]))
        self.assertAlmostEqual(branch_losses, gen_minus_load, places=5)

    def test_recorder_budget_is_bounded(self):
        case = IEEE14VoltageDispatch()
        recorder = Recorder(case, budget=2)
        value = case.base["gen"][:, VG]
        for _ in range(5):
            self.assertTrue(math.isfinite(recorder(value)))
        self.assertEqual(recorder.count, 2)

    def test_real_gadapt_execution_spends_budget(self):
        case = IEEE14VoltageDispatch()
        outcome = evaluate_method(case, "affine_invariant", 3, budget=40, pop=12)
        self.assertTrue(outcome["success"])
        self.assertEqual(outcome["evaluations"], 40)
        self.assertGreater(outcome["seconds"], 0)


if __name__ == "__main__":
    unittest.main()
