"""Deterministic reliability-only log-diversity contracts.

These tests are numerical correctness checks, not optimizer benchmarks.
"""
import itertools
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gadapt.ga import GA
from gadapt.operations.population_update.cost_diversity_population_updater import (
    CostDiversityPopulationUpdater,
)


def population(costs, monitored=True):
    return SimpleNamespace(
        options=SimpleNamespace(
            cost_diversity_metric="log_relative",
            reliability_monitor=object() if monitored else None,
        ),
        candidate_solutions=[SimpleNamespace(cost_value=x) for x in costs],
        relative_cost_diversity_in_first_population=float("nan"),
        absolute_cost_diversity_in_first_population=float("nan"),
        relative_cost_diversity_coefficient=float("nan"),
        absolute_cost_diversity=float("nan"),
    )


class ReliabilityExtremeCostDiversityTests(unittest.TestCase):
    def test_extreme_opposite_signs_do_not_cancel_shift_to_zero(self):
        pop = population([-1e308, 1e308])
        updater = CostDiversityPopulationUpdater()
        updater.update_population(pop)
        self.assertEqual(pop.relative_cost_diversity_coefficient, 1.0)
        self.assertTrue(math.isfinite(pop.relative_cost_diversity_in_first_population))
        self.assertGreater(pop.relative_cost_diversity_in_first_population, 700.0)

    def test_after_extreme_spread_converged_population_has_zero_diversity(self):
        pop = population([-1e308, 1e308, 0.0, 1e308])
        updater = CostDiversityPopulationUpdater()
        updater.update_population(pop)
        self.assertEqual(pop.relative_cost_diversity_coefficient, 1.0)
        initial = pop.relative_cost_diversity_in_first_population
        self.assertTrue(math.isfinite(initial))
        pop.candidate_solutions = [
            SimpleNamespace(cost_value=-1e308) for _ in range(4)
        ]
        updater.update_population(pop)
        self.assertEqual(pop.relative_cost_diversity_coefficient, 0.0)
        self.assertEqual(pop.relative_cost_diversity_in_first_population, initial)

    def test_regular_costs_keep_log_relative_formula(self):
        values = [-0.1, 0.0, 1.0, 3.0]
        pop = population(values)
        CostDiversityPopulationUpdater().update_population(pop)
        scale = 1.0 - min(values)
        expected_logs = sorted(math.log(x + scale) for x in values)
        expected = sum(b - a for a, b in zip(expected_logs, expected_logs[1:]))
        expected /= len(values) - 1
        self.assertAlmostEqual(pop.relative_cost_diversity_in_first_population,
                               expected, places=12)
        self.assertEqual(pop.relative_cost_diversity_coefficient, 1.0)

    def test_bounded_reliability_ga_handles_both_extreme_finite_cost_signs(self):
        attempts = []

        def objective(values):
            attempts.append(tuple(values))
            return -1e308 if values[0] == 0.0 else 1e308

        ga = GA(cost_function=objective, population_size=4,
                keep_elitism_percentage=100,
                reliability_mode=True, max_evaluations=4,
                acceptable_cost=-1.7e308,
                probe_cost_function=False, ensure_unique_individuals=False,
                exit_check="generations", number_of_generations=1)
        ga.add(0.0, 1.0)
        with patch("gadapt.ga_model.decision_variable.DecisionVariable.make_random_value",
                   side_effect=itertools.cycle([0.0, 1.0])):
            result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertTrue(result.feasible)
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(attempts), 4)
        self.assertEqual(set(attempts), {(0.0,), (1.0,)})
        self.assertEqual(result.best_objective, -1e308)


if __name__ == "__main__":
    unittest.main()
