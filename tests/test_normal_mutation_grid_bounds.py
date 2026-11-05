"""Regression checks for normal mutation on non-dividing finite grids.

These deterministic contracts are not optimization-performance experiments.
"""
import random
import unittest
from unittest.mock import patch

import numpy as np

from gadapt.ga import GA
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.variable_value import VariableValue
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_decision_variable_mutator import (
    NormalDistributionDecisionVariableMutator,
)


NORMAL_SAMPLE = (
    "gadapt.operations.mutation.decision_variable_mutation."
    "normal_distribution_decision_variable_mutator.normally_distributed_random"
)


def normal_mutate(low, high, step, current, sample=1.0):
    variable = DecisionVariable(0)
    variable.min_value = low
    variable.max_value = high
    variable.step = step
    value = VariableValue(variable, current)
    with patch(NORMAL_SAMPLE, return_value=sample):
        NormalDistributionDecisionVariableMutator().mutate(value)
    return value.value


class NormalMutationGridBoundsTest(unittest.TestCase):
    def test_nondividing_grid_cannot_round_beyond_declared_upper_bound(self):
        # Previously normalizing to 1 and round(1 / 0.6) produced 1.2.
        self.assertEqual(normal_mutate(0.0, 1.0, 0.6, 0.0), 0.6)

    def test_nondividing_three_step_grid_uses_last_real_grid_point(self):
        self.assertEqual(normal_mutate(0.0, 1.0, 0.3, 0.0), 0.9)

    def test_nearly_integer_floating_ratio_preserves_valid_upper_endpoint(self):
        self.assertEqual(normal_mutate(0.0, 10.2, 0.1, 0.0), 10.2)

    def test_exact_dividing_grid_keeps_upper_endpoint(self):
        self.assertEqual(normal_mutate(0.0, 1.0, 0.5, 0.0), 1.0)

    def test_same_last_grid_value_nudges_within_grid(self):
        variable = DecisionVariable(0)
        variable.min_value = 0.0
        variable.max_value = 1.0
        variable.step = 0.6
        value = VariableValue(variable, 0.6)
        with patch(NORMAL_SAMPLE, return_value=1.0), patch(
            "gadapt.operations.mutation.decision_variable_mutation."
            "normal_distribution_decision_variable_mutator.random.choice",
            return_value=1,
        ):
            NormalDistributionDecisionVariableMutator().mutate(value)
        self.assertEqual(value.value, 0.0)

    def test_bounded_reliability_ga_never_evaluates_off_grid_normal_mutation(self):
        random.seed(31)
        np.random.seed(31)
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 1.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=12, acceptable_cost=0.0,
                ensure_unique_individuals=False, probe_cost_function=False,
                decision_variable_mutation="normal_distribution",
                percentage_of_mutation_candidate_solutions=100.0,
                percentage_of_mutation_decision_variables=100.0,
                exit_check="generations", number_of_generations=6)
        ga.add(0.0, 1.0, step=0.6)
        with patch(NORMAL_SAMPLE, return_value=1.0) as sample:
            result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertGreater(result.objective_evaluations, 4)
        self.assertLessEqual(result.objective_evaluations, 12)
        self.assertEqual(result.valid_objective_evaluations, result.objective_evaluations)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(calls), result.objective_evaluations)
        self.assertTrue(sample.called)
        self.assertTrue(all(values[0] in (0.0, 0.6) for values in calls))


if __name__ == "__main__":
    unittest.main()
