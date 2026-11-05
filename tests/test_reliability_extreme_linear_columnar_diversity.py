"""Opt-in linear columnar-diversity stability contracts, not optimizer benchmarks."""
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


def make_population(values, low=-1e308, high=1e308, monitored=True):
    variable = DecisionVariable(0)
    variable.min_value = low
    variable.max_value = high
    population = Population(
        [Candidate([VariableValue(variable, v)]) for v in values]
    )
    population.options = SimpleNamespace(
        reliability_monitor=object() if monitored else None
    )
    return variable, population


class ReliabilityExtremeLinearColumnarTests(unittest.TestCase):
    def test_opposite_signed_finite_endpoints_do_not_report_zero_diversity(self):
        variable, population = make_population([-1e308, 1e308])
        ColumnarDiversityDecisionVariableUpdater("linear").update_decision_variables(population)
        self.assertFalse(variable.stacked)
        self.assertAlmostEqual(variable.initial_st_dev, math.sqrt(0.5))
        self.assertTrue(math.isfinite(variable.initial_st_dev))
        self.assertEqual(variable.columnar_diversity_coefficient, 1.0)

    def test_scaled_extreme_coordinates_preserve_linear_metric(self):
        values = [-1e308, -5e307, 5e307, 1e308]
        variable, population = make_population(values)
        ColumnarDiversityDecisionVariableUpdater("linear").update_decision_variables(population)
        self.assertAlmostEqual(variable.initial_st_dev,
                               statistics.stdev([0.0, 0.25, 0.75, 1.0]), places=13)

    def test_finite_small_span_retains_standard_deviation_ratio(self):
        values = [-2.0, 0.0, 1.0, 2.0]
        variable, population = make_population(values, low=-2.0, high=2.0)
        ColumnarDiversityDecisionVariableUpdater("linear").update_decision_variables(population)
        self.assertAlmostEqual(variable.initial_st_dev,
                               statistics.stdev(values) / 4.0, places=13)

    def test_extreme_span_convergence_retains_initial_spread(self):
        variable, population = make_population([-1e308, 1e308] * 2)
        updater = ColumnarDiversityDecisionVariableUpdater("linear")
        updater.update_decision_variables(population)
        reference = variable.initial_st_dev
        self.assertGreater(reference, 0)
        population[:] = [Candidate([VariableValue(variable, -1e308)]) for _ in range(4)]
        updater.update_decision_variables(population)
        self.assertTrue(variable.stacked)
        self.assertEqual(variable.columnar_diversity_coefficient, 0.0)
        self.assertEqual(variable.initial_st_dev, reference)

    def test_bounded_reliability_ga_keeps_nonzero_extreme_linear_diversity(self):
        evaluated = []
        observed_coefficients = []

        def objective(values):
            evaluated.append(tuple(values))
            return -1.0 if values[0] < 0 else 1.0

        ga = GA(
            cost_function=objective, population_size=4,
            reliability_mode=True, max_evaluations=4,
            acceptable_cost=-2.0, probe_cost_function=False,
            ensure_unique_individuals=False,
            columnar_diversity_metric="linear",
            exit_check="generations", number_of_generations=1,
        )
        ga.add(-1e308, 1e308)
        original = ColumnarDiversityDecisionVariableUpdater._update_decision_variables

        def record_updated_coefficient(updater):
            original(updater)
            observed_coefficients.append(
                updater.population.options.decision_variables[0].columnar_diversity_coefficient
            )

        with patch(
            "gadapt.ga_model.decision_variable.DecisionVariable.make_random_value",
            side_effect=itertools.cycle([-1e308, 1e308]),
        ), patch.object(ColumnarDiversityDecisionVariableUpdater,
                       "_update_decision_variables", record_updated_coefficient):
            result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(evaluated), 4)
        self.assertEqual(set(evaluated), {(-1e308,), (1e308,)})
        self.assertEqual(observed_coefficients, [1.0])


if __name__ == "__main__":
    unittest.main()
