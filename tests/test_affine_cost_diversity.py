"""Regression tests for opt-in affine-invariant cost diversity."""
import math
import random
import unittest
from types import SimpleNamespace

import numpy as np

from gadapt.ga import GA
from gadapt.ga_model.ga_options import GAOptions
from gadapt.utils.affine_cost_diversity import affine_cost_diversity
from gadapt.operations.population_update.cost_diversity_population_updater import CostDiversityPopulationUpdater


class AffineCostDiversityTest(unittest.TestCase):
    def test_shift_and_positive_scale_invariance(self):
        initial = [-2.0, 0.0, 5.0, 8.0]
        current = [0.0, 1.0, 3.0, 4.0]
        baseline, reference = affine_cost_diversity(initial)
        self.assertEqual(baseline, 1.0)
        expected, _ = affine_cost_diversity(current, reference)
        for multiplier, shift in [(1.0, 10.0), (1.0, 1000.0),
                                  (0.001, 0.0), (100.0, -300.0)]:
            x = [multiplier * c + shift for c in initial]
            y = [multiplier * c + shift for c in current]
            _, transformed_reference = affine_cost_diversity(x)
            actual, _ = affine_cost_diversity(y, transformed_reference)
            self.assertAlmostEqual(expected, actual, places=10)

    def test_degenerate_initial_population_recovers(self):
        initial, initial_reference = affine_cost_diversity([1.0] * 4)
        self.assertEqual((initial, initial_reference), (0.0, 0.0))
        after, reference = affine_cost_diversity([1.0, 2.0, 3.0, 4.0], initial_reference)
        self.assertEqual(after, 1.0)
        self.assertEqual(reference, 0.0)
        converged, _ = affine_cost_diversity([8.0] * 4, reference)
        self.assertEqual(converged, 0.0)

    def test_large_finite_range(self):
        score, reference = affine_cost_diversity([-1e308, 1e308])
        self.assertEqual(score, 1.0)
        self.assertTrue(math.isfinite(reference))

    def test_invalid_costs(self):
        for values in [[], [1.0, math.nan], [1.0, math.inf], [1.0, -math.inf]]:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    affine_cost_diversity(values)

    def test_configuration_default_and_validation(self):
        ga = GA(cost_function=lambda x: float(sum(v * v for v in x)))
        ga.add(-5.0, 5.0)
        self.assertEqual(ga.cost_diversity_metric, "log_relative")
        ga.cost_diversity_metric = "affine_invariant"
        self.assertEqual(GAOptions(ga.clone()).cost_diversity_metric, "affine_invariant")
        with self.assertRaises(ValueError):
            ga.cost_diversity_metric = "unknown"

    def test_real_population_updater_recovers_from_initial_tie(self):
        population = SimpleNamespace(
            options=SimpleNamespace(cost_diversity_metric="affine_invariant"),
            candidate_solutions=[],
            relative_cost_diversity_in_first_population=float("nan"),
            absolute_cost_diversity_in_first_population=float("nan"),
            relative_cost_diversity_coefficient=float("nan"),
            absolute_cost_diversity=float("nan"),
        )
        updater = CostDiversityPopulationUpdater()
        population.candidate_solutions = [
            SimpleNamespace(cost_value=1.0) for _ in range(4)
        ]
        updater.update_population(population)
        self.assertEqual(population.relative_cost_diversity_coefficient, 0.0)
        population.candidate_solutions = [
            SimpleNamespace(cost_value=float(v)) for v in (1, 2, 3, 4)
        ]
        updater.update_population(population)
        self.assertEqual(population.relative_cost_diversity_coefficient, 1.0)

    def test_full_optimizer_affine_translation_invariance(self):
        def run(shift):
            random.seed(21)
            np.random.seed(21)
            ga = GA(
                cost_function=lambda x: float(sum(v * v for v in x) + shift),
                cost_diversity_metric="affine_invariant",
                population_size=12,
                exit_check="generations",
                number_of_generations=8,
                population_mutation="cost_diversity,parent_diversity",
            )
            for _ in range(3):
                ga.add(-5.0, 5.0)
            result = ga.execute()
            self.assertTrue(result.success, result.message)
            return result
        original = run(0.0)
        shifted = run(1000.0)
        self.assertAlmostEqual(
            original.min_cost, shifted.min_cost - 1000.0, places=7
        )
        self.assertEqual(original.result_values, shifted.result_values)

    def test_stateful_bound_objective_is_not_deep_copied(self):
        class ExternalSimulator:
            def __init__(self):
                self.evaluations = 0

            def objective(self, variables):
                self.evaluations += 1
                return float(sum(float(x) ** 2 for x in variables))

        simulator = ExternalSimulator()
        ga = GA(cost_function=simulator.objective,
                population_size=12, exit_check="generations",
                number_of_generations=8)
        ga.add(-3.0, 3.0)
        ga.add(-3.0, 3.0)
        cloned = ga.clone()
        self.assertIs(cloned.cost_function.__self__, simulator)
        self.assertIsNot(cloned._decision_variables, ga._decision_variables)
        result = ga.execute()
        self.assertTrue(result.success, result.message)
        # Validation alone invokes two boundary-point evaluations.
        # This must count ALL executions, not just those two calls.
        self.assertGreater(simulator.evaluations, 12)

    def test_nonfinite_industry_objective_fails_closed(self):
        for invalid in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(invalid=invalid):
                ga = GA(
                    cost_function=lambda x, value=invalid: float(value),
                    population_size=12, exit_check="generations",
                    number_of_generations=6,
                )
                ga.add(-2.0, 2.0)
                ga.add(-2.0, 2.0)
                result = ga.execute()
                self.assertFalse(result.success)
                self.assertIn("All evaluated candidate costs", repr(result.messages))

    def test_end_to_end_both_modes(self):
        for metric in ("log_relative", "affine_invariant"):
            with self.subTest(metric=metric):
                random.seed(123)
                np.random.seed(123)
                ga = GA(
                    cost_function=lambda x: float(sum(v * v for v in x)),
                    population_size=12,
                    exit_check="generations",
                    number_of_generations=6,
                    cost_diversity_metric=metric,
                )
                ga.add(-5.0, 5.0)
                ga.add(-5.0, 5.0)
                result = ga.execute()
                self.assertTrue(result.success, result.message)
                self.assertTrue(math.isfinite(result.min_cost))


if __name__ == "__main__":
    unittest.main()
