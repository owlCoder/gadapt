"""Fast deterministic contracts for opt-in bounded reliability execution.

These are functional safety checks, NOT evidence of superior optimizer quality.
"""
import random
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import numpy as np

from gadapt.ga import GA
from gadapt.execution.reliability import ReliabilityMonitor, EvaluationBudgetExhausted


def seed():
    random.seed(11)
    np.random.seed(11)


class ReliabilityModeTest(unittest.TestCase):
    def test_hard_budget_including_validation_probes_and_best_ever(self):
        seed()
        seen = []

        def objective(values):
            value = float((values[0] - 0.3) ** 2)
            seen.append((tuple(values), value))
            return value

        ga = GA(cost_function=objective, population_size=6, reliability_mode=True,
                max_evaluations=14, acceptable_cost=-1.0,
                exit_check="avg_cost", max_attempt_no=2)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertFalse(result.acceptable)
        self.assertEqual(result.objective_evaluations, 14)
        self.assertEqual(result.valid_objective_evaluations, 14)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(len(seen), 14)
        best_values, best_cost = min(seen, key=lambda item: item[1])
        self.assertAlmostEqual(result.best_objective, best_cost)
        self.assertEqual(result.result_values, {0: best_values[0]})
        self.assertTrue(result.feasible)

    def test_acceptance_stops_without_spending_remaining_budget(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0

        ga = GA(cost_function=objective, population_size=4, reliability_mode=True,
                max_evaluations=50, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.objective_evaluations, 2)  # Both probes; no wasted search calls
        self.assertEqual(result.number_of_iterations, 0)
        self.assertEqual(len(calls), 2)

    def test_failed_generation_retains_validated_probe_incumbent(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 1.0 if len(calls) <= 2 else float("nan")

        ga = GA(cost_function=objective, population_size=4, reliability_mode=True,
                max_evaluations=10, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertEqual(result.termination_reason, "evaluation_failure")
        self.assertEqual(result.objective_evaluations, 6)
        self.assertEqual(result.valid_objective_evaluations, 2)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertEqual(len(calls), 6)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.best_objective, 1.0)
        self.assertIn((result.result_values[0],), calls[:2])

    def test_constraint_best_feasible_survives_selection_and_budget(self):
        seed()
        seen = []

        def objective(values):
            x = values[0]
            pair = (float((x + 0.5) ** 2), float(max(0.0, -x)))
            seen.append((tuple(values), pair))
            return pair

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=10,
                acceptable_cost=-1.0, constraint_handling="penalty",
                constraint_penalty_weight=0.001)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        feasible = [(v, obj) for v, (obj, violation) in seen if violation == 0]
        self.assertTrue(feasible)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.objective_evaluations, 10)
        self.assertTrue(result.feasible)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.best_violation, 0.0)
        best_values, best_obj = min(feasible, key=lambda item: item[1])
        self.assertEqual(result.best_objective, best_obj)
        self.assertEqual(result.result_values, {0: best_values[0]})

    def test_timeout_is_distinct_from_acceptance(self):
        seed()
        ga = GA(cost_function=lambda v: float(v[0] ** 2), population_size=4,
                reliability_mode=True, max_evaluations=20, acceptable_cost=-1.0,
                timeout=1)
        ga.add(-1.0, 1.0)
        # Move only the exit-check clock; keep population initialization and
        # the objective real and deterministic (no sleeps).
        with patch("gadapt.operations.exit_check.base_exit_checker.datetime") as clock:
            clock.now.return_value = datetime.now() + timedelta(seconds=10)
            result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.termination_reason, "timeout")
        self.assertEqual(result.objective_evaluations, 6)
        self.assertFalse(result.acceptable)

    def test_monitor_rejects_further_calls_after_a_failed_evaluation(self):
        calls = []

        def failing(values):
            calls.append(tuple(values))
            raise ValueError("invalid evaluation")

        monitor = ReliabilityMonitor(failing, 1, 0.0, constrained=False)
        with self.assertRaises(ValueError):
            monitor([1.0])
        with self.assertRaises(EvaluationBudgetExhausted):
            monitor([2.0])
        self.assertEqual(calls, [(1.0,)])
        self.assertEqual(monitor.evaluations, 1)
        self.assertEqual(monitor.invalid_evaluations, 1)
        self.assertEqual(monitor.valid_evaluations, 0)
        self.assertFalse(monitor.acceptable)

    def test_monitor_snapshots_values_before_mutating_objective(self):
        def objective(values):
            values[0] = 999.0
            return 0.0

        monitor = ReliabilityMonitor(objective, 1, 0.0, constrained=False)
        monitor([0.25])
        self.assertEqual(monitor.best[2], (0.25,))

    def test_no_feasible_solution_is_not_misreported(self):
        seed()
        def objective(values):
            return float(values[0] ** 2), 1.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=8, acceptable_cost=100.0,
                constraint_handling="feasibility_rules")
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.objective_evaluations, 8)
        self.assertFalse(result.feasible)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.best_violation, 1.0)

    def test_validation_probe_failure_returns_structured_status(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            if values[0] == -1.0:
                raise ValueError("domain excludes left endpoint")
            return 1.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=10, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.termination_reason, "validation_failed")
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.objective_evaluations, 1)
        self.assertEqual(result.invalid_objective_evaluations, 1)
        self.assertEqual(len(calls), 1)

    def test_budget_must_cover_initial_population_and_probes(self):
        calls = []
        ga = GA(cost_function=lambda v: calls.append(tuple(v)) or 1.0,
                reliability_mode=True, max_evaluations=5, acceptable_cost=0.0,
                population_size=4)
        ga.add(0.0, 1.0)
        with self.assertRaisesRegex(ValueError, "initial population"):
            ga.execute()
        self.assertEqual(calls, [])

    def test_legacy_does_not_gain_implicit_budget_or_quality_claims(self):
        seed()
        ga = GA(cost_function=lambda v: float(v[0] ** 2),
                exit_check="generations", number_of_generations=2, population_size=4)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertIsNone(result.objective_evaluations)
        self.assertIsNone(result.acceptable)
        self.assertIsNone(result.termination_reason)


if __name__ == "__main__":
    unittest.main()
