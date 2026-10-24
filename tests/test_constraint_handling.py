"""Opt-in constraint_handling: the cost function returns (objective, violation).

Toy problem: minimize (x - 2)^2 + (y - 1)^2 subject to x + y <= 2 (optimum x = 1.5, y = 0.5, objective 0.5).
The default (constraint_handling=None) is covered by a separate seeded call-sequence check.
"""
import math
import random
import unittest

import numpy as np

from gadapt.ga import GA
from gadapt.utils.constraint_handling import ConstraintHandler, parse_pair


def _pair(values):
    x, y = values
    return (x - 2) ** 2 + (y - 1) ** 2, max(0.0, x + y - 2)


def _run(technique, seed=1):
    random.seed(seed)
    np.random.seed(seed)
    ga = GA(cost_function=_pair, constraint_handling=technique, exit_check="generations", number_of_generations=80)
    ga.add(-3.0, 3.0, 0.01)
    ga.add(-3.0, 3.0, 0.01)
    return ga.execute()


class ConstraintHandlingTest(unittest.TestCase):
    def test_every_technique_reaches_the_constrained_optimum(self):
        for technique in ("penalty", "adaptive_penalty", "feasibility_rules", "epsilon"):
            result = _run(technique)
            self.assertTrue(result.success, (technique, result.messages))
            self.assertEqual(result.best_violation, 0.0, technique)
            self.assertLess(result.best_objective, 0.6, technique)

    def test_feasibility_rules_order(self):
        handler = ConstraintHandler("feasibility_rules")
        handler.start_generation(None, [(1.0, 0.0), (3.0, 0.5)], 0.0)
        feasible_bad, feasible_good = handler.cost(9.0, 0.0), handler.cost(1.0, 0.0)
        infeasible_small, infeasible_large = handler.cost(0.0, 0.1), handler.cost(0.0, 2.0)
        failed = handler.cost(None, float("inf"))
        self.assertTrue(feasible_good < feasible_bad < infeasible_small < infeasible_large < failed)

    def test_adaptive_penalty_weight(self):
        handler = ConstraintHandler("adaptive_penalty", 10.0)
        for _ in range(3):
            handler.start_generation((1.0, 0.5), [(1.0, 0.5)], 0.0)
        self.assertEqual(handler.weight, 20.0)
        for _ in range(3):
            handler.start_generation((1.0, 0.0), [(1.0, 0.0)], 0.0)
        self.assertAlmostEqual(handler.weight, 20.0 / 1.5)

    def test_epsilon_level_reaches_zero(self):
        handler = ConstraintHandler("epsilon")
        initial = [(1.0, v) for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)]
        handler.start_generation(None, initial, 0.0)
        self.assertAlmostEqual(handler.epsilon, 0.1)
        handler.start_generation(None, initial, 0.5)
        self.assertEqual(handler.epsilon, 0.0)

    def test_invalid_options(self):
        with self.assertRaises(ValueError):
            GA(cost_function=_pair, constraint_handling="unknown")
        with self.assertRaises(ValueError):
            GA(cost_function=_pair, constraint_handling="penalty", constraint_penalty_weight=0)

    def test_epsilon_needs_generations_also_when_set_after_construction(self):
        ga = GA(cost_function=_pair)
        ga.constraint_handling = "epsilon"
        ga.add(0.0, 1.0)
        ga.add(0.0, 1.0)
        with self.assertRaises(Exception) as raised:
            ga.execute()
        self.assertIn("number_of_generations", str(raised.exception))

    def test_keys_are_exact_for_extreme_values(self):
        handler = ConstraintHandler("feasibility_rules")
        handler.start_generation(None, [(1.0, 0.0)], 0.0)
        self.assertLess(handler.key(1e20, 0.0), handler.key(2e20, 0.0))
        self.assertLess(handler.key(2e20, 0.0), handler.key(0.0, 1e-20))
        self.assertLess(handler.key(0.0, 1e16), handler.key(0.0, 1e20))
        self.assertLess(handler.key(0.0, 1e300), handler.key(None, float("inf")))

    def test_penalty_never_becomes_nonfinite(self):
        handler = ConstraintHandler("adaptive_penalty", 1000.0)
        for _ in range(3000):
            handler.start_generation((1.0, 1.0), [(1.0, 1.0)], 0.0)
        self.assertEqual(handler.weight, 1000.0 * 1e6)
        for objective, violation in ((0.0, 1e150), (1.0, 0.0)):
            self.assertTrue(math.isfinite(handler.cost(objective, violation)))

    def test_overflowing_penalties_keep_their_order(self):
        handler = ConstraintHandler("penalty", 1000.0)
        handler.start_generation(None, [(1.0, 0.0)], 0.0)
        self.assertLess(handler.key(0.0, 1e149), handler.key(0.0, 1e150))
        self.assertLess(handler.key(-1e150, 1e146), handler.key(1e150, 9e145))
        with self.assertRaises(ValueError):
            parse_pair((1e151, 0.0))
        handler = ConstraintHandler("adaptive_penalty", 1e100)
        for _ in range(30):
            handler.start_generation((1.0, 1.0), [(1.0, 1.0)], 0.0)
        self.assertTrue(math.isfinite(handler.weight))
        self.assertTrue(math.isfinite(handler.cost(1.0, 0.0)) and math.isfinite(handler.cost(-1e150, 1e150)))

    def test_result_values_are_the_reported_feasible_solution(self):
        # a weak penalty makes an infeasible point the final scalar winner; the results report the best feasible one
        random.seed(3)
        np.random.seed(3)
        ga = GA(cost_function=_pair, constraint_handling="penalty", constraint_penalty_weight=1e-3,
                exit_check="generations", number_of_generations=60)
        ga.add(-3.0, 3.0, 0.01)
        ga.add(-3.0, 3.0, 0.01)
        result = ga.execute()
        self.assertTrue(result.feasible)
        objective, violation = _pair([result.result_values[0], result.result_values[1]])
        self.assertEqual(violation, 0.0)
        self.assertAlmostEqual(objective, result.best_objective)

    def test_pairs_are_validated(self):
        for bad in (("x", 0.0), (1.0, -1.0), (1.0, float("nan")), (True, 0.0), 1.0, (1.0, 2.0, 3.0)):
            with self.assertRaises(ValueError):
                parse_pair(bad)
        self.assertEqual(parse_pair((np.float64(1.5), 0)), (1.5, 0.0))

    def test_reports_the_best_feasible_solution(self):
        result = _run("penalty")
        self.assertTrue(result.feasible)
        x, y = result.result_values[0], result.result_values[1]
        self.assertAlmostEqual(_pair([x, y])[0], result.best_objective)
        self.assertLessEqual(x + y, 2 + 1e-12)

    def test_probe_requires_a_pair(self):
        ga = GA(cost_function=lambda v: 1.0, constraint_handling="penalty", exit_check="generations",
                number_of_generations=5)
        ga.add(0.0, 1.0)
        with self.assertRaises(Exception) as raised:
            ga.execute()
        self.assertIn("(objective, violation)", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
