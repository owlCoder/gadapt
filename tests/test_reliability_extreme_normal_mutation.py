"""Opt-in extreme finite normal-mutation stability contracts, not optimizer benchmarks."""
import itertools
import math
import unittest
from unittest.mock import patch

from gadapt.ga import GA
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.variable_value import VariableValue
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_decision_variable_mutator import (
    NormalDistributionDecisionVariableMutator,
)


SAMPLE = (
    "gadapt.operations.mutation.decision_variable_mutation."
    "normal_distribution_decision_variable_mutator.normally_distributed_random"
)


def mutate(current, sample, low=-1e308, high=1e308, step=None, monitored=True):
    variable = DecisionVariable(0)
    variable.min_value = low
    variable.max_value = high
    variable.step = step
    if monitored:
        variable._reliability_safe_random = True
    value = VariableValue(variable, current)
    with patch(SAMPLE, return_value=sample) as sampled:
        NormalDistributionDecisionVariableMutator().mutate(value)
    return value.value, sampled


class ExtremeFiniteNormalMutationTests(unittest.TestCase):
    def test_both_extreme_endpoints_have_finite_mutation(self):
        # Both endpoint parents used to produce 0/inf or inf/inf arithmetic.
        for current in (-1e308, 0.0, 1e308):
            for fraction, expected in (
                (0.0, -1.0), (0.25, -0.5),
                (0.75, 0.5), (1.0, 1.0)
            ):
                with self.subTest(current=current, fraction=fraction):
                    value, sampled = mutate(current, fraction)
                    self.assertTrue(sampled.called)
                    self.assertTrue(math.isfinite(value))
                    self.assertGreaterEqual(value, -1e308)
                    self.assertLessEqual(value, 1e308)
                    self.assertAlmostEqual(value / 1e308, expected)

    def test_extreme_endpoints_produce_finite_normalized_means(self):
        for current, expected_mean in (
            (-1e308, 0.0), (0.0, 0.5), (1e308, 1.0)
        ):
            with self.subTest(current=current):
                _, sampled = mutate(current, 0.75)
                arguments = sampled.call_args.args
                self.assertTrue(math.isfinite(arguments[0]))
                self.assertAlmostEqual(arguments[0], expected_mean)
                self.assertEqual(arguments[2:], (0, 1))

    def test_extreme_span_with_tiny_step_is_effectively_continuous(self):
        value, _ = mutate(-1e308, 0.75, step=1e-150)
        self.assertTrue(math.isfinite(value))
        self.assertAlmostEqual(value / 1e308, 0.5)

    def test_normal_scale_keeps_legacy_interpolation(self):
        value, sampled = mutate(-2.0, 0.75, low=-2.0, high=2.0)
        self.assertEqual(value, 1.0)
        self.assertAlmostEqual(sampled.call_args.args[0], 0.0)

    def test_unmonitored_extreme_span_keeps_original_behavior(self):
        value, _ = mutate(-1e308, 0.75, monitored=False)
        self.assertTrue(math.isinf(value))
        value_at_zero, _ = mutate(-1e308, 0.0, monitored=False)
        self.assertTrue(math.isnan(value_at_zero))

    def test_bounded_ga_mutations_remain_in_bounds_and_counted(self):
        observed = []

        def objective(values):
            observed.append(tuple(values))
            return values[0] / 1e308

        ga = GA(
            cost_function=objective, population_size=4,
            reliability_mode=True, max_evaluations=12,
            acceptable_cost=-2.0, probe_cost_function=False,
            ensure_unique_individuals=False,
            decision_variable_mutation="normal_distribution",
            percentage_of_mutation_candidate_solutions=100.0,
            percentage_of_mutation_decision_variables=100.0,
            exit_check="generations", number_of_generations=6,
        )
        ga.add(-1e308, 1e308)
        with patch(
            "gadapt.ga_model.decision_variable.DecisionVariable.make_random_value",
            side_effect=itertools.cycle([-1e308, -5e307, 0.0, 5e307])
        ), patch(SAMPLE, return_value=0.75) as sample:
            result = ga.execute()

        self.assertTrue(result.success, result.messages)
        self.assertTrue(sample.called, "Normal mutation must run during the GA")
        self.assertGreater(result.objective_evaluations, 4)
        self.assertLessEqual(result.objective_evaluations, 12)
        self.assertEqual(result.valid_objective_evaluations,
                         result.objective_evaluations)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(observed), result.objective_evaluations)
        self.assertTrue(all(
            len(values) == 1 and math.isfinite(values[0]) and
            -1e308 <= values[0] <= 1e308 for values in observed
        ))


if __name__ == "__main__":
    unittest.main()
