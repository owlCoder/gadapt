"""Synthetic checks for I43 (ITERATION43_PROTOCOL.md §6). No topohub data is used."""
import random
import subprocess
import unittest

import networkx as nx
import numpy as np

from research.iteration43_budget_operator_diagnostic import (
    Budgeted, OVER_BUDGET, RouteChoiceCost, holm, run_ea)


def triangle():
    graph = nx.Graph()
    graph.add_edge(0, 1, dist=10.0)
    graph.add_edge(1, 2, dist=20.0)
    graph.add_edge(0, 2, dist=100.0)
    return graph


class Iteration43Test(unittest.TestCase):
    def test_cost_formula_by_hand(self):
        # Demand 0->2 (q=8): path 0 = (0,2) direct, path 1 = (0,1,2). U = 4*8 = 32.
        f = RouteChoiceCost(triangle(), [(0, 2, 8.0)])
        self.assertEqual(f.n, 1)
        self.assertEqual(f.unit, 32.0)
        self.assertEqual(f(np.array([0])), 100.0)        # one U module on (0,2)
        self.assertEqual(f(np.array([1])), 30.0)         # one U module on (0,1) and (1,2)

    def test_two_modules_use_double_price(self):
        f = RouteChoiceCost(triangle(), [(0, 2, 8.0), (2, 0, 8.0)])
        f.unit = 8.0                                     # load 16 -> 2 quanta -> one 2U module
        self.assertAlmostEqual(f(np.array([0, 0])), 160.0)

    def test_budget_accounting(self):
        cost = Budgeted(lambda z: float(np.sum(z)), budget=5, checkpoints=(2, 5))
        for v in (3, 2, 4, 1, 5, 0):
            out = cost(np.array([v]))
        self.assertEqual(out, OVER_BUDGET)
        self.assertEqual((cost.calls, cost.over_budget), (5, 1))
        self.assertEqual(cost.at, {2: 2.0, 5: 1.0})

    def test_ea_solves_onemax(self):
        random.seed(1)
        np.random.seed(1)
        cost = Budgeted(lambda z: float(np.sum(z == 0)), budget=2000, checkpoints=(2000,))
        run_ea(cost, 30)
        self.assertEqual(cost.best, 0.0)

    def test_holm(self):
        self.assertEqual(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])

    def test_gadapt_library_untouched(self):
        diff = subprocess.run(["git", "diff", "--stat", "HEAD", "--", "gadapt/"],
                              capture_output=True, text=True, check=True).stdout
        self.assertEqual(diff.strip(), "")


if __name__ == "__main__":
    unittest.main()
