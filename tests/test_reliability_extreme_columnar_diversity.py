"""Deterministic log-columnar-diversity overflow checks; not GA benchmarks."""
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


def make_population(values, lower, upper, monitored=True):
    variable = DecisionVariable(0)
    variable.min_value = lower
    variable.max_value = upper
    candidates = [Candidate([VariableValue(variable, value)]) for value in values]
    population = Population(candidates)
    population.options = SimpleNamespace(
        reliability_monitor=object() if monitored else None
    )
    return variable, population


class ReliabilityExtremeColumnarDiversityTests(unittest.TestCase):
    def test_extreme_finite_bounds_have_finite_columnar_spread(self):
        variable, population = make_population(
            [-1e308, 1e308, -1e308, 1e308], -1e308, 1e308
        )
        ColumnarDiversityDecisionVariableUpdater().update_decision_variables(population)
        self.assertFalse(variable.stacked)
        self.assertTrue(math.isfinite(variable.initial_st_dev))
        self.assertGreater(variable.initial_st_dev, 350)
        self.assertEqual(variable.columnar_diversity_coefficient, 1.0)

    def test_extreme_spread_can_converge_to_stacked_without_losing_reference(self):
        variable, population = make_population([-1e308, 1e308], -1e308, 1e308)
        updater = ColumnarDiversityDecisionVariableUpdater()
        updater.update_decision_variables(population)
        initial = variable.initial_st_dev
        population[:] = [
            Candidate([VariableValue(variable, -1e308)]) for _ in range(4)
        ]
        updater.update_decision_variables(population)
        self.assertTrue(variable.stacked)
        self.assertEqual(variable.columnar_diversity_coefficient, 0.0)
        self.assertEqual(variable.initial_st_dev, initial)

    def test_regular_scale_uses_mathematically_same_log_transform(self):
        values = [-1.0, 0.0, 4.0, 2.5]
        variable, population = make_population(values, -1.0, 4.0)
        ColumnarDiversityDecisionVariableUpdater().update_decision_variables(population)
        expected = statistics.stdev(
            [math.log((value - variable.min_value) + 1.0) for value in values]
        )
        self.assertAlmostEqual(variable.initial_st_dev, expected, places=12)
        self.assertEqual(variable.columnar_diversity_coefficient, 1.0)

    def test_bounded_reliability_ga_can_complete_with_extreme_finite_bounds(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return -1.0 if values[0] < 0 else 1.0

        ga = GA(
            cost_function=objective, population_size=4,
            reliability_mode=True, max_evaluations=4,
            acceptable_cost=-2.0, probe_cost_function=False,
            ensure_unique_individuals=False,
            exit_check="generations", number_of_generations=1,
        )
        ga.add(-1e308, 1e308)
        with patch(
            "gadapt.ga_model.decision_variable.DecisionVariable.make_random_value",
            side_effect=itertools.cycle([-1e308, 1e308]),
        ):
            result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertTrue(result.feasible)
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(calls), 4)
        self.assertEqual(set(calls), {(-1e308,), (1e308,)})


if __name__ == "__main__":
    unittest.main()
