"""Deterministic opt-in log columnar subnormal contracts; no optimizer benchmarks."""
import itertools
import math
import statistics
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gadapt.ga import GA
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.variable_value import VariableValue
from gadapt.operations.decision_variable_update.variable_columnar_diversity_decision_variable_updater import (
    ColumnarDiversityDecisionVariableUpdater,
)


class Candidate(list):
    is_immigrant = False


class Population(list):
    pass


def population(values, high, monitored=True):
    decision = DecisionVariable(0)
    decision.min_value = 0.0
    decision.max_value = high
    members = Population(
        Candidate([VariableValue(decision, value)]) for value in values
    )
    members.options = SimpleNamespace(
        reliability_monitor=object() if monitored else None
    )
    return decision, members


class SubnormalLogColumnarDiversityTests(unittest.TestCase):
    def test_distinct_subnormal_column_has_positive_initial_spread(self):
        ulp = math.ulp(0.0)
        values = [0.0, ulp, ulp, ulp]
        self.assertEqual(statistics.stdev([math.log1p(v) for v in values]), 0.0)
        decision, members = population(values, 2 * ulp)
        ColumnarDiversityDecisionVariableUpdater("log_relative").update_decision_variables(members)
        self.assertFalse(decision.stacked)
        self.assertEqual(decision.initial_st_dev, ulp)
        self.assertEqual(decision.columnar_diversity_coefficient, 1.0)

    def test_convergence_and_recovery_preserve_reference(self):
        ulp = math.ulp(0.0)
        decision, members = population([0.0, ulp, ulp, ulp], 2 * ulp)
        updater = ColumnarDiversityDecisionVariableUpdater("log_relative")
        updater.update_decision_variables(members)
        original = decision.initial_st_dev
        members[:] = [Candidate([VariableValue(decision, ulp)]) for _ in range(4)]
        updater.update_decision_variables(members)
        self.assertTrue(decision.stacked)
        self.assertEqual(decision.columnar_diversity_coefficient, 0.0)
        self.assertEqual(decision.initial_st_dev, original)
        members[:] = [Candidate([VariableValue(decision, value)])
                      for value in (0.0, 2 * ulp, 2 * ulp, 2 * ulp)]
        updater.update_decision_variables(members)
        self.assertFalse(decision.stacked)
        self.assertEqual(decision.initial_st_dev, original)
        self.assertGreater(decision.columnar_diversity_coefficient, 0.0)

    def test_default_mode_retains_historical_zero_log_spread(self):
        ulp = math.ulp(0.0)
        decision, members = population([0.0, ulp, ulp, ulp], 2 * ulp,
                                       monitored=False)
        ColumnarDiversityDecisionVariableUpdater("log_relative").update_decision_variables(members)
        self.assertFalse(decision.stacked)
        self.assertEqual(decision.initial_st_dev, 0.0)
        self.assertEqual(decision.columnar_diversity_coefficient, 0.0)

    def test_representable_log_spread_is_unchanged(self):
        values = [0.0, 1.0, 1.0, 1.0]
        expected = statistics.stdev([math.log1p(v) for v in values])
        decision, members = population(values, 2.0)
        ColumnarDiversityDecisionVariableUpdater("log_relative").update_decision_variables(members)
        self.assertEqual(decision.initial_st_dev, expected)
        self.assertEqual(decision.columnar_diversity_coefficient, 1.0)

    def test_bounded_ga_preserves_initial_subnormal_diversity(self):
        ulp = math.ulp(0.0)
        calls, coefficients = [], []

        def objective(values):
            calls.append(tuple(values))
            return 1.0

        ga = GA(
            cost_function=objective, population_size=4,
            keep_elitism_percentage=100,
            reliability_mode=True, max_evaluations=4,
            acceptable_cost=0.0, probe_cost_function=False,
            ensure_unique_individuals=False,
            columnar_diversity_metric="log_relative",
            exit_check="generations", number_of_generations=1,
        )
        ga.add(0.0, 2 * ulp)
        original_update = ColumnarDiversityDecisionVariableUpdater._update_decision_variables

        def record(updater):
            original_update(updater)
            coefficients.append(
                updater.population.options.decision_variables[0].columnar_diversity_coefficient
            )

        with patch(
            "gadapt.ga_model.decision_variable.DecisionVariable.make_random_value",
            side_effect=itertools.cycle([0.0, ulp, ulp, ulp]),
        ), patch.object(
            ColumnarDiversityDecisionVariableUpdater,
            "_update_decision_variables", record,
        ):
            result = ga.execute()

        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(calls), 4)
        self.assertEqual(coefficients, [1.0])


if __name__ == "__main__":
    unittest.main()
