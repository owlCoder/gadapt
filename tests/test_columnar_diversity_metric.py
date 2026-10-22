"""Opt-in columnar_diversity_metric="linear": invariant to the units and to the position in the range."""
import unittest

import numpy as np

from gadapt.ga import GA
from gadapt.ga_model.candidate_solution import CandidateSolution
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.variable_value import VariableValue
from gadapt.operations.decision_variable_update.variable_columnar_diversity_decision_variable_updater import (
    ColumnarDiversityDecisionVariableUpdater)


class _Population(list):
    pass


def _coefficients(metric, lower, upper, initial, current):
    """Coefficient of one decision variable after an initial and a current population."""
    variable = DecisionVariable(0)
    variable.min_value, variable.max_value = lower, upper
    updater = ColumnarDiversityDecisionVariableUpdater(metric)
    for values in (initial, current):
        population = _Population()
        for value in values:
            c = CandidateSolution(0)
            c.append(VariableValue(variable, value))
            population.append(c)
        updater.update_decision_variables(population)
    return variable.columnar_diversity_coefficient


class ColumnarDiversityMetricTest(unittest.TestCase):
    rng = np.random.RandomState(0)
    initial = rng.uniform(0, 1, 24)
    near_top = 0.999 - 0.002 * rng.uniform(0, 1, 24)

    def _both(self, metric, scale):
        return (_coefficients(metric, 0., scale, self.initial * scale, self.near_top * scale),
                _coefficients(metric, 0., scale, self.initial * scale, (self.near_top - 0.5) * scale))

    def test_linear_is_invariant_to_units_and_position(self):
        top_1, middle_1 = self._both("linear", 1.0)
        top_1000, middle_1000 = self._both("linear", 1000.0)
        self.assertAlmostEqual(top_1, top_1000, places=12)
        self.assertAlmostEqual(top_1, middle_1, places=12)
        self.assertAlmostEqual(middle_1, middle_1000, places=12)

    def test_default_log_depends_on_units(self):
        top_1, _ = self._both("log_relative", 1.0)
        top_1000, _ = self._both("log_relative", 1000.0)
        self.assertGreater(top_1 / top_1000, 2)  # same population, different units

    def test_parameter_is_validated(self):
        with self.assertRaises(ValueError):
            GA(cost_function=lambda a: 0.0, columnar_diversity_metric="relative")
        self.assertEqual(GA(cost_function=lambda a: 0.0).columnar_diversity_metric, "log_relative")


if __name__ == "__main__":
    unittest.main()
