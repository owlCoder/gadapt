"""Contracts for effective-continuous crossover, not optimizer benchmarks."""
import random
import unittest

import numpy as np

from gadapt.ga import GA
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.operations.crossover.differential_crossover import DifferentialCrossover


def decision_variable(low, high, step=None):
    variable = DecisionVariable(0)
    variable.min_value = low
    variable.max_value = high
    variable.step = step
    return variable


class DifferentialEffectiveContinuityTest(unittest.TestCase):
    def test_overflowing_grid_ratio_no_longer_crashes(self):
        variable = decision_variable(0.0, 1e200, 1e-150)
        self.assertFalse(variable.is_discrete)
        value = 4.321e199
        self.assertEqual(DifferentialCrossover._fit(variable, value), value)

    def test_ultrafine_finite_ratio_preserves_continuous_precision(self):
        variable = decision_variable(0.0, 1.0, 1e-12)
        self.assertFalse(variable.is_discrete)
        value = 0.12345678901234568
        self.assertEqual(DifferentialCrossover._fit(variable, value), value)

    def test_genuinely_discrete_step_still_snaps(self):
        variable = decision_variable(0.0, 1.0, 0.25)
        self.assertTrue(variable.is_discrete)
        self.assertEqual(DifferentialCrossover._fit(variable, 0.63), 0.75)

    def test_step_free_value_remains_continuous(self):
        variable = decision_variable(0.0, 1.0)
        self.assertEqual(DifferentialCrossover._fit(variable, 0.37), 0.37)

    def test_bounded_reliable_ga_survives_unrepresentably_dense_grid(self):
        random.seed(23)
        np.random.seed(23)
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 1.0

        ga = GA(cost_function=objective, population_size=6,
                reliability_mode=True, max_evaluations=12,
                acceptable_cost=0.0, probe_cost_function=False,
                crossover="differential",
                exit_check="generations", number_of_generations=6)
        ga.add(0.0, 1e200, step=1e-150)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertGreaterEqual(result.objective_evaluations, 6)
        self.assertLessEqual(result.objective_evaluations, 12)
        self.assertEqual(len(calls), result.objective_evaluations)
        self.assertEqual(result.valid_objective_evaluations, result.objective_evaluations)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertTrue(all(0.0 <= values[0] <= 1e200 for values in calls))


if __name__ == "__main__":
    unittest.main()
