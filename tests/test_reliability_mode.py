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
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.population import Population
from gadapt.operations.cost_finding.constraint_handling_cost_finder import ConstraintHandlingCostFinder
from gadapt.operations.immigration.population_immigration.common_population_immigrator import CommonPopulationImmigrator
from gadapt.operations.immigration.candidate_solution_immigration.random_candidate_solution_immigrator import RandomCandidateSolutionImmigrator
from gadapt.utils.constraint_handling import ConstraintHandler


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

    def test_all_invalid_initial_generation_recovers_validated_probe(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 1.0 if len(calls) <= 2 else float("nan")

        ga = GA(cost_function=objective, population_size=4, reliability_mode=True,
                max_evaluations=6, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.objective_evaluations, 6)
        self.assertEqual(result.valid_objective_evaluations, 2)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertEqual(len(calls), 6)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.best_objective, 1.0)
        self.assertIn((result.result_values[0],), calls[:2])

    def test_constrained_all_invalid_generation_recovers_feasible_probe(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return (1.0, 0.0) if len(calls) <= 2 else (float("nan"), 0.0)

        ga = GA(cost_function=objective, population_size=4, reliability_mode=True,
                max_evaluations=6, acceptable_cost=0.0,
                constraint_handling="feasibility_rules")
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.objective_evaluations, 6)
        self.assertEqual(result.valid_objective_evaluations, 2)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertTrue(result.feasible)
        self.assertEqual(result.solution_status, "feasible_but_unacceptable")
        self.assertEqual(result.best_violation, 0.0)
        self.assertIn((result.result_values[0],), calls[:2])

    def test_all_invalid_with_no_valid_history_still_fails(self):
        seed()
        ga = GA(cost_function=lambda values: float("nan"),
                probe_cost_function=False, population_size=4, reliability_mode=True,
                max_evaluations=4, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertEqual(result.termination_reason, "evaluation_failure")
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.objective_evaluations, 4)

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

    def test_stateful_objective_is_not_deepcopied_into_initial_snapshot(self):
        seed()

        class ExternalSimulator:
            def __init__(self):
                self.calls = 0

            def __deepcopy__(self, memo):
                raise AssertionError("A stateful objective must never be cloned")

            def objective(self, values):
                self.calls += 1
                return float((values[0] - 0.1) ** 2)

        simulator = ExternalSimulator()
        ga = GA(cost_function=simulator.objective, population_size=4,
                reliability_mode=True, max_evaluations=8, acceptable_cost=-1.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.objective_evaluations, 8)
        self.assertEqual(simulator.calls, 8)

    def test_feasible_parent_survives_weak_penalty_and_immigration(self):
        # Fixed candidate evaluations, not an optimization-performance test.
        # Weak penalty favors every infeasible candidate over the feasible one.
        def objective(v):
            x = v[0]
            return (100.0, 0.0) if x >= 0 else (0.0, -x)

        def make_population(reliable):
            ga = GA(cost_function=objective, population_size=4,
                    keep_elitism_percentage=50, immigration_number=1,
                    constraint_handling="penalty", constraint_penalty_weight=0.001,
                    probe_cost_function=False)
            ga.add(-1.0, 1.0)
            options = GAOptions(ga)
            monitor = None
            if reliable:
                monitor = ReliabilityMonitor(objective, 20, -1.0, constrained=True)
                options.cost_function = monitor
                options.reliability_monitor = monitor
            population = Population(options)
            for c, x in zip(population, (-0.1, -0.2, -0.3, 0.5)):
                c[0].value = x
            finder = ConstraintHandlingCostFinder(ConstraintHandler("penalty", 0.001))
            finder.find_costs(population)
            return population, finder, monitor

        legacy, _, _ = make_population(False)
        self.assertTrue(all(c.violation_value > 0 for c in legacy))
        population, finder, monitor = make_population(True)
        feasible = [c for c in population if c.violation_value == 0.0]
        self.assertEqual(len(feasible), 1)
        self.assertEqual(feasible[0][0].value, 0.5)
        self.assertEqual(monitor.evaluations, 4)

        population.population_generation += 1
        immigrant = CommonPopulationImmigrator(RandomCandidateSolutionImmigrator())
        immigrant.immigrate(population)
        self.assertEqual(feasible[0][0].value, 0.5)
        self.assertFalse(feasible[0].is_immigrant)
        self.assertEqual(monitor.evaluations, 4)  # immigration itself evaluates nothing
        finder.find_costs(population)
        self.assertEqual(monitor.evaluations, 5)
        self.assertTrue(any(c is feasible[0] for c in population))

    def test_old_probe_feasible_incumbent_reenters_search_without_evaluation(self):
        def objective(v):
            return (100.0, 0.0) if v[0] >= 0 else (0.0, -v[0])

        ga = GA(cost_function=objective, population_size=4,
                keep_elitism_percentage=50,
                constraint_handling="penalty", constraint_penalty_weight=0.001,
                probe_cost_function=False)
        ga.add(-1.0, 1.0)
        options = GAOptions(ga)
        monitor = ReliabilityMonitor(objective, 20, -1.0, constrained=True)
        monitor([0.75])  # Already actually evaluated; not in the generated population.
        options.cost_function = monitor
        options.reliability_monitor = monitor
        population = Population(options)
        for c, x in zip(population, (-0.1, -0.2, -0.3, -0.4)):
            c[0].value = x
        finder = ConstraintHandlingCostFinder(ConstraintHandler("penalty", 0.001))
        finder.find_costs(population)
        self.assertEqual(monitor.evaluations, 5)  # 1 prior + 4 fresh; no re-evaluation
        feasible = [c for c in population if c.violation_value == 0]
        self.assertEqual(len(feasible), 1)
        self.assertEqual(feasible[0][0].value, 0.75)
        self.assertTrue(feasible[0].succ)

    def test_real_incumbent_progress_resets_stagnation(self):
        pairs = {
            0: (0.0, 3.0),
            1: (200.0, 2.0),  # worse objective but smaller violation
            2: (1000.0, 0.0),  # feasibility is always a strict improvement
            3: (900.0, 0.0),
        }
        monitor = ReliabilityMonitor(lambda v: pairs[int(v[0])], 12, -1.0, True)
        monitor([0])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 0)
        monitor([1])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 0)
        monitor([1])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 1)
        monitor([2])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 0)
        monitor([3])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 0)
        monitor([2])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 1)
        self.assertEqual(monitor.evaluations, 6)

    def test_refresh_cadence_preserves_incumbent_and_spends_no_calls(self):
        seed()
        ga = GA(cost_function=lambda v: float(v[0]),
                population_size=8, keep_elitism_percentage=50,
                reliability_mode=True, max_evaluations=30,
                acceptable_cost=-1.0, probe_cost_function=False,
                reliability_refresh_patience=2, reliability_refresh_percentage=50.0)
        ga.add(0.0, 10.0)
        options = GAOptions(ga)
        monitor = ReliabilityMonitor(ga.cost_function, 30, -1.0, False)
        options.reliability_monitor = monitor
        options.reliability_refresh_patience = ga.reliability_refresh_patience
        population = Population(options)
        for index, c in enumerate(population):
            c[0].value = float(index)
            c.cost_value = float(index)
        monitor([3.0])  # The candidate to preserve has actually been evaluated.
        elite = population[3]  # Largest cost among the four selectable survivors.
        elite._reliability_feasible_elite = True
        immigrant = CommonPopulationImmigrator(RandomCandidateSolutionImmigrator())
        population.population_generation = 1

        monitor.stagnant_generations = 1
        immigrant.immigrate(population)
        self.assertEqual(sum(c.is_immigrant for c in population), 0)

        monitor.stagnant_generations = 2
        immigrant.immigrate(population)
        self.assertEqual(sum(c.is_immigrant for c in population), 2)
        self.assertFalse(elite.is_immigrant)
        self.assertEqual(elite[0].value, 3.0)
        self.assertEqual(monitor.stagnation_refreshes, 1)
        self.assertEqual(monitor.evaluations, 1)

        monitor.stagnant_generations = 3
        immigrant.immigrate(population)
        self.assertEqual(monitor.stagnation_refreshes, 1)
        self.assertEqual(monitor.evaluations, 1)

    def test_refresh_runs_under_hard_budget_and_is_explicit_opt_in(self):
        def run(refresh):
            seed()
            ga = GA(cost_function=lambda v: 1.0, population_size=6,
                    reliability_mode=True, max_evaluations=30, acceptable_cost=0.0,
                    probe_cost_function=False, number_of_generations=8,
                    exit_check="generations", ensure_unique_individuals=False,
                    reliability_refresh_patience=(2 if refresh else None))
            ga.add(-1.0, 1.0)
            return ga.execute()

        off, on = run(False), run(True)
        for result in (off, on):
            self.assertTrue(result.success, result.messages)
            self.assertFalse(result.acceptable)
            self.assertLessEqual(result.objective_evaluations, 30)
        self.assertEqual(off.stagnation_refreshes, 0)
        self.assertGreater(on.stagnation_refreshes, 0)

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
