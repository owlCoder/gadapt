"""Deterministic extreme-span initialization contracts, not optimizer benchmarks."""
import itertools
import math
import unittest
from unittest.mock import patch

from gadapt.ga import GA
from gadapt.ga_model.decision_variable import DecisionVariable


def variable(low, high, step=None, reliable=True):
    decision = DecisionVariable(0)
    decision.min_value = low
    decision.max_value = high
    decision.step = step
    if reliable:
        decision._reliability_safe_random = True
    return decision


class ExtremeFiniteRandomInitializationTests(unittest.TestCase):
    def test_safe_continuous_draws_cover_extreme_finite_span(self):
        decision = variable(-1e308, 1e308)
        for fraction, expected in [(0.0, -1e308), (0.25, -5e307),
                                   (0.5, 0.0), (0.75, 5e307)]:
            with self.subTest(fraction=fraction), patch(
                    "gadapt.ga_model.decision_variable.numpy.random.random",
                    return_value=fraction):
                value = decision.make_random_value()
            self.assertTrue(math.isfinite(value))
            self.assertGreaterEqual(value, decision.min_value)
            self.assertLessEqual(value, decision.max_value)
            self.assertAlmostEqual(value / 1e308, expected / 1e308)

    def test_effectively_continuous_tiny_step_uses_safe_draw(self):
        decision = variable(-1e308, 1e308, step=1e-150)
        self.assertFalse(decision.is_discrete)
        with patch("gadapt.ga_model.decision_variable.numpy.random.random",
                   return_value=0.5):
            self.assertEqual(decision.make_random_value(), 0.0)

    def test_ordinary_reliability_draw_uses_original_numpy_path(self):
        decision = variable(-1.0, 1.0)
        with patch("gadapt.ga_model.decision_variable.numpy.random.uniform",
                   return_value=0.25) as uniform, patch(
                "gadapt.ga_model.decision_variable.numpy.random.random"
        ) as random:
            self.assertEqual(decision.make_random_value(), 0.25)
        uniform.assert_called_once_with(low=-1.0, high=1.0)
        random.assert_not_called()

    def test_unmonitored_extreme_draw_keeps_legacy_path(self):
        decision = variable(-1e308, 1e308, reliable=False)
        with patch("gadapt.ga_model.decision_variable.numpy.random.uniform",
                   side_effect=OverflowError("legacy span")) as uniform:
            with self.assertRaises(OverflowError):
                decision.make_random_value()
        uniform.assert_called_once_with(low=-1e308, high=1e308)

    def test_reliable_ga_initializes_extreme_span_with_exact_budget(self):
        evaluated = []

        def objective(values):
            evaluated.append(tuple(values))
            return abs(values[0]) / 1e308

        ga = GA(
            cost_function=objective, population_size=4,
            keep_elitism_percentage=100, reliability_mode=True,
            max_evaluations=4, acceptable_cost=-1.0,
            probe_cost_function=False, ensure_unique_individuals=False,
            columnar_diversity_metric="linear",
            exit_check="generations", number_of_generations=1,
        )
        ga.add(-1e308, 1e308)
        with patch("gadapt.ga_model.decision_variable.numpy.random.random",
                   side_effect=itertools.cycle([0.0, 0.25, 0.5, 0.75])):
            result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(evaluated), 4)
        self.assertEqual(len(set(evaluated)), 4)
        for (value,) in evaluated:
            self.assertTrue(math.isfinite(value))
            self.assertGreaterEqual(value, -1e308)
            self.assertLessEqual(value, 1e308)


if __name__ == "__main__":
    unittest.main()
