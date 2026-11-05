"""Deterministic contracts for normal mutation on fixed decision variables.

These tests do not measure genetic-optimizer performance or make benchmark claims.
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
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_cost_diversity_decision_variable_mutator import (
    NormalDistributionCostDiversityDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_variable_columnar_diversity_decision_variable_mutator import (
    NormalDistributionVariableColumnarDiversityDecisionVariableMutator,
)


def fixed_value(value=2.5):
    variable = DecisionVariable(0)
    variable.min_value = value
    variable.max_value = value
    return VariableValue(variable, value)


class FixedVariableMutationTest(unittest.TestCase):
    def test_normal_mutator_keeps_valid_fixed_value_without_sampling(self):
        variable_value = fixed_value()
        mutator = NormalDistributionDecisionVariableMutator()
        with patch(
            "gadapt.operations.mutation.decision_variable_mutation."
            "normal_distribution_decision_variable_mutator.normally_distributed_random",
            side_effect=AssertionError("Fixed variable must not sample"),
        ):
            mutator.mutate(variable_value)
        self.assertEqual(variable_value.value, 2.5)

    def test_cost_diversity_normal_mutator_keeps_valid_fixed_value(self):
        variable_value = fixed_value(-1.5)
        mutator = NormalDistributionCostDiversityDecisionVariableMutator(
            get_cost_diversity_function=lambda: lambda: 0.7,
        )
        mutator.mutate(variable_value)
        self.assertEqual(variable_value.value, -1.5)

    def test_columnar_diversity_normal_mutator_keeps_valid_fixed_value(self):
        variable_value = fixed_value(0.75)
        variable_value.decision_variable.columnar_diversity_coefficient = 0.4
        mutator = NormalDistributionVariableColumnarDiversityDecisionVariableMutator()
        mutator.mutate(variable_value)
        self.assertEqual(variable_value.value, 0.75)

    def test_nonfixed_normal_mutation_still_samples(self):
        variable = DecisionVariable(0)
        variable.min_value = 0.0
        variable.max_value = 1.0
        variable_value = VariableValue(variable, 0.25)
        mutator = NormalDistributionDecisionVariableMutator()
        with patch(
            "gadapt.operations.mutation.decision_variable_mutation."
            "normal_distribution_decision_variable_mutator.normally_distributed_random",
            return_value=0.75,
        ) as sample:
            mutator.mutate(variable_value)
        self.assertEqual(variable_value.value, 0.75)
        self.assertTrue(sample.called)

    def test_reliability_ga_with_fixed_dimension_does_not_abort_normal_mutation(self):
        random.seed(17)
        np.random.seed(17)
        calls = []
        def objective(values):
            calls.append(tuple(values))
            return 1.0

        ga = GA(
            cost_function=objective,
            population_size=4,
            reliability_mode=True,
            max_evaluations=8,
            acceptable_cost=0.0,
            probe_cost_function=False,
            decision_variable_mutation="normal_distribution",
            percentage_of_mutation_candidate_solutions=100.0,
            percentage_of_mutation_decision_variables=100.0,
            exit_check="generations",
            number_of_generations=5,
        )
        ga.add(2.5, 2.5)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.feasible)
        self.assertFalse(result.acceptable)
        self.assertGreaterEqual(result.objective_evaluations, 4)
        self.assertLessEqual(result.objective_evaluations, 8)
        self.assertEqual(result.valid_objective_evaluations, result.objective_evaluations)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(calls), result.objective_evaluations)
        self.assertTrue(all(values == (2.5,) for values in calls))


if __name__ == "__main__":
    unittest.main()
