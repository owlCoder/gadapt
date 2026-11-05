"""Deterministic mutation contracts; no optimizer benchmark data."""
import random
import unittest
from unittest.mock import patch

import numpy as np

from gadapt.ga import GA
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.variable_value import VariableValue
from gadapt.operations.mutation.decision_variable_mutation.extreme_pointed_decision_variable_mutator import (
    ExtremePointedDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (
    RandomDecisionVariableMutator,
)


def variable_value(step=None, value=0.5):
    variable = DecisionVariable(0)
    variable.min_value = 0.0
    variable.max_value = 1.0
    variable.step = step
    return VariableValue(variable, value)


class ExtremePointedContinuousTest(unittest.TestCase):
    def test_no_step_uses_generator_instead_of_dividing_by_none(self):
        vv = variable_value()
        mutator = ExtremePointedDecisionVariableMutator()
        with patch.object(RandomDecisionVariableMutator, "_make_mutated_value",
                          return_value=0.75) as generator:
            mutator.mutate(vv)
        self.assertEqual(vv.value, 0.75)
        generator.assert_called_once_with()

    def test_tiny_step_uses_existing_continuous_fallback(self):
        vv = variable_value(step=1e-12)
        mutator = ExtremePointedDecisionVariableMutator()
        with patch.object(RandomDecisionVariableMutator, "_make_mutated_value",
                          return_value=0.23456789) as generator:
            mutator.mutate(vv)
        self.assertEqual(vv.value, 0.23456789)
        generator.assert_called_once_with()

    def test_discrete_step_preserves_extreme_step_operation(self):
        vv = variable_value(step=0.25)
        mutator = ExtremePointedDecisionVariableMutator()
        with patch.object(RandomDecisionVariableMutator, "_make_mutated_value",
                          side_effect=AssertionError("Discrete case should not fall back")), \
             patch("gadapt.operations.mutation.decision_variable_mutation."
                   "extreme_pointed_decision_variable_mutator.get_rand_bool_with_probability",
                   return_value=False), \
             patch("gadapt.operations.mutation.decision_variable_mutation."
                   "extreme_pointed_decision_variable_mutator.get_rand_bool",
                   return_value=True), \
             patch("gadapt.operations.mutation.decision_variable_mutation."
                   "extreme_pointed_decision_variable_mutator.random.randint",
                   return_value=1):
            mutator.mutate(vv)
        self.assertEqual(vv.value, 0.75)  # Forced "above" branch: 0.5 + 1 * 0.25.

    def test_bounded_reliability_ga_continuous_extreme_mutation_no_exception(self):
        random.seed(19)
        np.random.seed(19)
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 1.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=8, acceptable_cost=0.0,
                probe_cost_function=False,
                decision_variable_mutation="extreme_pointed",
                percentage_of_mutation_candidate_solutions=100.0,
                percentage_of_mutation_decision_variables=100.0,
                exit_check="generations", number_of_generations=5)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertGreaterEqual(result.objective_evaluations, 4)
        self.assertLessEqual(result.objective_evaluations, 8)
        self.assertEqual(len(calls), result.objective_evaluations)
        self.assertTrue(all(0.0 <= values[0] <= 1.0 for values in calls))


if __name__ == "__main__":
    unittest.main()
