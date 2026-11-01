"""Synthetic checks for I45 (ITERATION45_PROTOCOL.md §5). No topohub data is used."""
import random
import unittest

import numpy as np

from research.iteration43_budget_operator_diagnostic import Budgeted
from research.iteration45_generic_vs_specific import run_textbook_ga


class TextbookGaTest(unittest.TestCase):
    def test_solves_onemax(self):
        random.seed(1)
        np.random.seed(1)
        cost = Budgeted(lambda z: float(np.sum(z == 0)), budget=10_000, checkpoints=(10_000,))
        run_textbook_ga(cost, 30)
        self.assertEqual(cost.best, 0.0)

    def test_exact_budget_and_elitism(self):
        weights = np.random.RandomState(3).rand(50)
        population_minima = []
        np.random.seed(4)
        cost = Budgeted(lambda z: float(weights @ z), budget=1234, checkpoints=(1234,))
        run_textbook_ga(cost, 50, population_minima.append)
        self.assertEqual((cost.calls, cost.over_budget), (1234, 0))
        self.assertGreater(len(population_minima), 40)
        self.assertTrue(all(a >= b for a, b in zip(population_minima, population_minima[1:])))


if __name__ == "__main__":
    unittest.main()
