"""Pre-run checks for I48 (ITERATION48_PROTOCOL.md §5)."""
import os
import subprocess
import unittest

import numpy as np

import research.iteration48_valve_dispatch as m

DATA_DIR = os.path.dirname(m.DATA)


def published_vector(log_name):
    text = open(os.path.join(DATA_DIR, log_name)).read()
    line = text[text.rindex("prod levels:"):].splitlines()[1]
    return np.array(line.split("*")[0].split()[1:], dtype=float)


class ValveDispatchTest(unittest.TestCase):
    def test_published_optima_reproduce_certified_cost(self):
        for system, load, log in (("eld13", 1800.0, "eld13-1800.txt"), ("eld13", 2520.0, "eld13-2520.txt"),
                                  ("eld40", 10500.0, "eld40-10500.txt")):
            problem = m.ValveDispatch(system, load)
            p = published_vector(log)
            cost = float(np.sum(problem.unit_costs(p)))
            # published vectors have 3 decimals; valve-point slopes are ~10 $/MW
            self.assertLess(abs(cost - problem.optimum) / problem.optimum, 1e-5, (system, load, cost))

    def test_slack_unit_and_penalty(self):
        problem = m.ValveDispatch("eld13", 1800.0)
        self.assertEqual(problem.slack, 0)
        self.assertEqual(m.ValveDispatch("eld40", 10500.0).slack, 12)
        low = np.array(problem.p_max)[problem.free]  # others at max -> slack far below its minimum
        value, feasible = problem.evaluate(low)
        slack = 1800.0 - low.sum()
        p = problem.full_vector(low)
        p[0] = problem.p_min[0]
        self.assertFalse(feasible)
        self.assertAlmostEqual(value, float(np.sum(problem.unit_costs(p))) + 1000.0 * (problem.p_min[0] - slack))

    def test_budget_and_restarts(self):
        old = m.BUDGET
        m.BUDGET, m.CHECKPOINTS = 3000, (3000,)
        try:
            for method in m.METHODS:
                run = m.one_run(("eld13", 1800.0, method, 1))
                self.assertEqual((run["calls"], run["instance"]), (3000, "eld13@1800"), method)
            self.assertGreaterEqual(m.one_run(("eld13", 1800.0, "ipop_cma_es", 1))["restarts"], 1)
        finally:
            m.BUDGET, m.CHECKPOINTS = old, (5_000, 20_000, 50_000)

    def test_library_unchanged(self):
        diff = subprocess.run(["git", "diff", "--stat", "cc2f357", "--", "gadapt/"],
                              capture_output=True, text=True, check=True).stdout
        self.assertEqual(diff.strip(), "")


if __name__ == "__main__":
    unittest.main()
