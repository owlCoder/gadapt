"""Deterministic blending-crossover overflow contracts, not optimizer benchmarks."""
import math
import random
import unittest
from unittest.mock import patch

import numpy as np

from gadapt.ga import GA
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.variable_value import VariableValue
from gadapt.operations.crossover.blending_crossover import BlendingCrossover


def variable(low=0.0, high=1.0, step=None):
    decision = DecisionVariable(0)
    decision.min_value = low
    decision.max_value = high
    decision.step = step
    return decision


def crossover(decision, father, mother):
    operation = BlendingCrossover(None, None, None)
    operation._father_variable_value = VariableValue(decision, father)
    operation._mother_variable_value = VariableValue(decision, mother)
    return operation


class BlendingStepOverflowTests(unittest.TestCase):
    def test_infinite_step_count_uses_bounded_continuous_blending(self):
        decision = variable(0.0, 1e200, 1e-150)
        self.assertFalse(decision.is_discrete)
        operation = crossover(decision, 0.0, 1e200)
        with patch("gadapt.operations.crossover.blending_crossover.random.random",
                   return_value=0.25), patch(
                       "gadapt.operations.crossover.blending_crossover.random.randint",
                       side_effect=AssertionError("Do not sample an infinite step count")
                   ):
            offspring = operation._combine()
        self.assertEqual(offspring, (7.5e199, 2.5e199))
        self.assertTrue(all(math.isfinite(v) and 0.0 <= v <= 1e200
                            for v in offspring))

    def test_nonoverflowing_step_still_uses_discrete_blending(self):
        operation = crossover(variable(0.0, 1.0, 0.25), 0.25, 0.75)
        with patch("gadapt.operations.crossover.blending_crossover.random.randint",
                   return_value=1) as sample, patch(
                       "gadapt.operations.crossover.blending_crossover.random.random",
                       side_effect=AssertionError("Finite steps must use old discrete rule")
                   ):
            offspring = operation._combine()
        self.assertEqual(offspring, (0.5, 0.5))
        sample.assert_called_once_with(0, 2)

    def test_missing_step_preserves_continuous_blending(self):
        operation = crossover(variable(0.0, 1.0, None), 0.0, 1.0)
        with patch("gadapt.operations.crossover.blending_crossover.random.random",
                   return_value=0.25):
            self.assertEqual(operation._combine(), (0.75, 0.25))

    def test_bounded_reliability_ga_no_longer_crashes_blending_with_tiny_step(self):
        random.seed(29)
        np.random.seed(29)
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 1.0

        ga = GA(cost_function=objective, population_size=6,
                reliability_mode=True, max_evaluations=12,
                acceptable_cost=0.0, probe_cost_function=False,
                crossover="blending", crossover_probability=1.0,
                exit_check="generations", number_of_generations=5)
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
