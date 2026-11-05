"""Fast deterministic contracts for opt-in bounded reliability execution.

These are functional safety checks, NOT evidence of superior optimizer quality.
"""
import math
import random
import unittest
from datetime import datetime, timedelta
from fractions import Fraction
from unittest.mock import patch

import numpy as np

from gadapt.ga import GA
from gadapt.execution.ga_executor import GAExecutor
from gadapt.execution.reliability import ReliabilityMonitor, EvaluationBudgetExhausted, AcceptableTargetReached
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.population import Population
from gadapt.operations.cost_finding.constraint_handling_cost_finder import ConstraintHandlingCostFinder
from gadapt.operations.cost_finding.elitism_cost_finder import ElitismCostFinder
from gadapt.operations.immigration.population_immigration.common_population_immigrator import CommonPopulationImmigrator
from gadapt.operations.immigration.candidate_solution_immigration.random_candidate_solution_immigrator import RandomCandidateSolutionImmigrator
from gadapt.utils.constraint_handling import ConstraintHandler


def seed():
    random.seed(11)
    np.random.seed(11)


class ReliabilityModeTest(unittest.TestCase):
    def test_precise_scalar_incumbent_improves_without_float_difference(self):
        worse = Fraction(1) + Fraction(3, 2**56)
        better = Fraction(1) + Fraction(1, 2**56)
        self.assertEqual(float(worse), float(better))
        values = [worse, better]
        monitor = ReliabilityMonitor(lambda v: values[int(v[0])], 2,
                                     0.0, False, cache_evaluations=True)
        self.assertEqual(monitor([0]), worse)
        self.assertEqual(monitor([1]), better)
        self.assertEqual(monitor.best, (1.0, 0.0, (1,)))
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.valid_evaluations, 2)
        self.assertEqual(monitor([0]), 1.0)
        self.assertEqual(monitor.best[2], (1,))
        self.assertEqual(monitor.cached_objective_requests, 1)

    def test_precise_constrained_violation_orders_infeasible_incumbent(self):
        worse = Fraction(1) + Fraction(3, 2**56)
        better = Fraction(1) + Fraction(1, 2**56)
        self.assertEqual(float(worse), float(better))
        values = [worse, better]
        monitor = ReliabilityMonitor(lambda v: (10.0, values[int(v[0])]),
                                     2, 0.0, True)
        self.assertEqual(monitor([0]), (10.0, worse))
        self.assertEqual(monitor([1]), (10.0, better))
        self.assertEqual(monitor.best, (10.0, 1.0, (1,)))
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor.evaluations, 2)

    def test_precise_constrained_objective_orders_feasible_incumbent(self):
        worse = Fraction(1) + Fraction(3, 2**56)
        better = Fraction(1) + Fraction(1, 2**56)
        monitor = ReliabilityMonitor(lambda v: (worse if v[0] == 0 else better, 0.0),
                                     2, 0.0, True)
        self.assertEqual(monitor([0]), (worse, 0.0))
        self.assertEqual(monitor([1]), (better, 0.0))
        self.assertEqual(monitor.best, (1.0, 0.0, (1,)))
        self.assertEqual(monitor.valid_evaluations, 2)

    def test_precise_objective_cannot_false_accept_binary64_rounding(self):
        above = Fraction(1) + Fraction(1, 2**55)
        below = Fraction(1) - Fraction(1, 2**55)
        self.assertEqual(float(above), 1.0)
        self.assertEqual(float(below), 1.0)
        calls = []

        def objective(values):
            calls.append(values[0])
            return above if values[0] == 0 else below

        monitor = ReliabilityMonitor(objective, 2, 1.0, False,
                                     cache_evaluations=True)
        self.assertEqual(monitor([0]), above)
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor.best, (1.0, 0.0, (0,)))
        # Cache hits must never convert a falsely rounded objective to
        # an actual acceptance, even when no new physical calls remain.
        monitor.stop_on_acceptance = True
        self.assertEqual(monitor([0]), 1.0)
        self.assertFalse(monitor.acceptable)
        with self.assertRaises(AcceptableTargetReached):
            monitor([1])
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor.best, (1.0, 0.0, (1,)))
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.cached_objective_requests, 1)
        self.assertEqual(calls, [0, 1])

    def test_constrained_precise_objective_and_exact_threshold(self):
        above = Fraction(1) + Fraction(1, 2**55)
        below = Fraction(1) - Fraction(1, 2**55)
        values = [above, below]
        monitor = ReliabilityMonitor(lambda v: (values[int(v[0])], 0.0),
                                     2, 1.0, True)
        self.assertEqual(monitor([0]), (above, 0.0))
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor([1]), (below, 0.0))
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor.best, (1.0, 0.0, (1,)))
        # A non-binary64 threshold is also compared at its original
        # precision, rather than being rounded down on construction.
        threshold = Fraction(1) + Fraction(1, 2**55)
        m2 = ReliabilityMonitor(lambda _: 1.0, 1, threshold, False)
        self.assertEqual(m2([0]), 1.0)
        self.assertTrue(m2.acceptable)

    def test_rounded_above_threshold_never_stops_real_ga(self):
        seed()
        above = Fraction(1) + Fraction(1, 2**55)
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return above

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=4,
                acceptable_cost=1.0, probe_cost_function=False)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.solution_status, "feasible_but_unacceptable")
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(len(calls), 4)

    def test_negative_scalar_underflow_cannot_fabricate_zero_incumbent(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return Fraction(-1, 10**400) if len(calls) == 1 else 1.0

        monitor = ReliabilityMonitor(objective, 2, 0.0, False,
                                     cache_evaluations=True,
                                     decision_bounds=((0.0, 1.0),))
        self.assertTrue(math.isnan(monitor([0.5])))
        self.assertFalse(monitor.acceptable)
        self.assertIsNone(monitor.best)
        self.assertEqual(monitor([0.5]), 1.0)
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.invalid_evaluations, 1)
        self.assertEqual(monitor.valid_evaluations, 1)
        self.assertEqual(monitor.cached_objective_requests, 0)
        self.assertEqual(calls, [(0.5,), (0.5,)])
        self.assertEqual(monitor.best, (1.0, 0.0, (0.5,)))

    def test_negative_constrained_objective_underflow_cannot_fabricate_zero(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return (Fraction(-1, 10**400), 0.0) if len(calls) == 1 else (1.0, 0.0)

        monitor = ReliabilityMonitor(objective, 2, 0.0, True,
                                     cache_evaluations=True,
                                     decision_bounds=((0.0, 1.0),))
        self.assertTrue(math.isnan(monitor([0.5])))
        self.assertFalse(monitor.acceptable)
        self.assertIsNone(monitor.best)
        self.assertEqual(monitor([0.5]), (1.0, 0.0))
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.invalid_evaluations, 1)
        self.assertEqual(monitor.valid_evaluations, 1)
        self.assertEqual(monitor.cached_objective_requests, 0)
        self.assertEqual(calls, [(0.5,), (0.5,)])
        self.assertEqual(monitor.best, (1.0, 0.0, (0.5,)))

    def test_negative_underflow_population_recovery_uses_real_budget(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return Fraction(-1, 10**400) if len(calls) <= 4 else 1.0

        ga = GA(cost_function=objective, population_size=4,
                probe_cost_function=False, reliability_mode=True,
                max_evaluations=8, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.acceptable)
        self.assertEqual(result.objective_evaluations, 8)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(len(calls), 8)
        self.assertEqual(result.best_objective, 1.0)

    def test_positive_scalar_underflow_never_falsely_reaches_zero_target(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return Fraction(1, 10**400) if len(calls) == 1 else 1.0

        monitor = ReliabilityMonitor(objective, 2, 0.0, False,
                                     cache_evaluations=True,
                                     decision_bounds=((0.0, 1.0),))
        self.assertTrue(math.isnan(monitor([0.5])))
        self.assertFalse(monitor.acceptable)
        self.assertIsNone(monitor.best)
        self.assertEqual(monitor([0.5]), 1.0)
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.valid_evaluations, 1)
        self.assertEqual(monitor.invalid_evaluations, 1)
        self.assertEqual(monitor.cached_objective_requests, 0)
        self.assertFalse(monitor.acceptable)

    def test_positive_constrained_objective_underflow_never_falsely_acceptable(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            if len(calls) == 1:
                return Fraction(1, 10**400), 0.0
            return 1.0, 0.0

        monitor = ReliabilityMonitor(objective, 2, 0.0, True,
                                     cache_evaluations=True,
                                     decision_bounds=((0.0, 1.0),))
        self.assertTrue(math.isnan(monitor([0.5])))
        self.assertIsNone(monitor.best)
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor([0.5]), (1.0, 0.0))
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.invalid_evaluations, 1)
        self.assertEqual(monitor.valid_evaluations, 1)
        self.assertEqual(monitor.cached_objective_requests, 0)
        self.assertFalse(monitor.acceptable)

    def test_positive_underflow_population_recovery_uses_real_evaluation_budget(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return Fraction(1, 10**400) if len(calls) <= 4 else 1.0

        ga = GA(cost_function=objective, population_size=4,
                probe_cost_function=False, reliability_mode=True,
                max_evaluations=8, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.acceptable)
        self.assertEqual(result.objective_evaluations, 8)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(len(calls), 8)
        self.assertEqual(result.best_objective, 1.0)

    def test_small_discrete_grid_is_exhaustive_without_ga_population_floor(self):
        # The only acceptable point is last in grid order; cover all 3x2
        # points even though GA's default population_size is 32.
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0 if tuple(values) == (2.0, 1.0) else 1.0

        ga = GA(cost_function=objective, reliability_mode=True,
                reliability_discrete_certify=True, max_evaluations=6,
                acceptable_cost=0.0)
        ga.add(0.0, 2.0, step=1.0)
        ga.add(0.0, 1.0, step=1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertTrue(result.discrete_search_applied)
        self.assertTrue(result.discrete_space_exhausted)
        self.assertFalse(result.discrete_absence_certified)
        self.assertEqual(result.discrete_space_size, 6)
        self.assertEqual(result.discrete_points_checked, 6)
        self.assertEqual(result.objective_evaluations, 6)
        self.assertEqual(len(set(calls)), 6)
        self.assertEqual(result.best_objective, 0.0)
        self.assertEqual(result.result_values, {0: 2.0, 1: 1.0})
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.number_of_iterations, 0)

    def test_full_grid_with_no_target_can_certify_absence_under_valid_outputs(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return float(values[0] + values[1] + 1)

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, reliability_discrete_certify=True,
                max_evaluations=4, acceptable_cost=0.0)
        ga.add(0.0, 1.0, step=1.0)
        ga.add(0.0, 1.0, step=1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.termination_reason, "discrete_space_exhausted")
        self.assertEqual(result.discrete_points_checked, 4)
        self.assertTrue(result.discrete_space_exhausted)
        self.assertTrue(result.discrete_absence_certified)
        self.assertEqual(len(set(calls)), 4)

    def test_invalid_grid_point_invalidates_absence_certificate(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return float("nan") if tuple(values) == (0.0, 1.0) else 2.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, reliability_discrete_certify=True,
                max_evaluations=4, acceptable_cost=0.0)
        ga.add(0.0, 1.0, step=1.0)
        ga.add(0.0, 1.0, step=1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.invalid_objective_evaluations, 1)
        self.assertTrue(result.discrete_space_exhausted)
        self.assertFalse(result.discrete_absence_certified)
        self.assertEqual(len(calls), 4)

    def test_constrained_grid_ignores_infeasible_too_good_points(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return (0.2, 0.0) if tuple(values) == (1.0, 1.0) else (-100.0, 0.5)

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, reliability_discrete_certify=True,
                max_evaluations=4, acceptable_cost=0.2, constraint_handling="penalty",
                constraint_penalty_weight=0.001)
        ga.add(0.0, 1.0, step=1.0)
        ga.add(0.0, 1.0, step=1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertTrue(result.feasible)
        self.assertEqual(result.best_objective, 0.2)
        self.assertEqual(result.best_violation, 0.0)
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.result_values, {0: 1.0, 1: 1.0})
        self.assertEqual(len(calls), 4)

    def test_full_grid_with_no_valid_evaluations_fails_closed(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            raise ValueError("Simulation failed")

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, reliability_discrete_certify=True,
                max_evaluations=4, acceptable_cost=0.0)
        ga.add(0.0, 1.0, step=1.0)
        ga.add(0.0, 1.0, step=1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertFalse(result.discrete_absence_certified)
        self.assertEqual(len(calls), 4)

    def test_larger_grid_falls_back_to_ga_without_false_certificate(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return float(values[0] ** 2)

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, reliability_discrete_certify=True,
                max_evaluations=10, acceptable_cost=-1.0)
        ga.add(0.0, 100.0, step=1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.discrete_search_applied)
        self.assertFalse(result.discrete_absence_certified)
        self.assertLessEqual(result.objective_evaluations, 10)
        self.assertEqual(len(calls), result.objective_evaluations)

    def test_floating_step_grid_matches_discrete_generator_including_endpoint(self):
        from gadapt.execution.discrete_certification import discrete_grid_axes
        from gadapt.ga_model.decision_variable import DecisionVariable

        variable = DecisionVariable(0)
        variable.min_value = 0.0
        variable.max_value = 10.2
        variable.step = 0.1
        axes = discrete_grid_axes([variable], max_points=103)
        self.assertIsNotNone(axes)
        self.assertEqual(len(axes[0]), 103)
        self.assertEqual(axes[0][-1], 10.2)
        self.assertEqual(len(set(axes[0])), 103)
        self.assertIsNone(discrete_grid_axes([variable], max_points=102))

    def test_discrete_certification_requires_opt_in_reliability_mode(self):
        with self.assertRaisesRegex(ValueError, "requires reliability_mode"):
            GA(cost_function=lambda values: 0.0, reliability_discrete_certify=True)

    def test_cache_does_not_collapse_large_distinct_integers(self):
        # float(2**53) == float(2**53 + 1): previous key collided.
        calls = []

        def objective(values):
            calls.append(values[0])
            return float(len(calls))

        monitor = ReliabilityMonitor(objective, 3, -1.0, False,
                                     cache_evaluations=True)
        self.assertEqual(monitor([2**53]), 1.0)
        self.assertEqual(monitor([2**53 + 1]), 2.0)
        self.assertEqual(monitor([2**53]), 1.0)
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.cached_objective_requests, 1)
        self.assertEqual(calls, [2**53, 2**53 + 1])

    def test_cache_bypasses_extended_precision_numpy_scalars(self):
        # np.longdouble may have more precision than float; cache must not
        # silently merge different inputs on such platforms.
        calls = []

        def objective(values):
            calls.append(values[0])
            return float(len(calls))

        monitor = ReliabilityMonitor(objective, 3, -1.0, False,
                                     cache_evaluations=True)
        x = np.longdouble(1)
        y = np.nextafter(x, np.longdouble(2))
        self.assertEqual(monitor([x]), 1.0)
        self.assertEqual(monitor([y]), 2.0)
        self.assertEqual(monitor([x]), 3.0)
        self.assertEqual(monitor.evaluations, 3)
        self.assertEqual(monitor.cached_objective_requests, 0)
        self.assertEqual(len(calls), 3)

    def test_cache_reuses_valid_identical_vector_without_spending_budget(self):
        seen = []

        def objective(values):
            seen.append(tuple(values))
            return 2.0

        monitor = ReliabilityMonitor(objective, 1, -1.0, False,
                                     cache_evaluations=True)
        self.assertEqual(monitor([0.0]), 2.0)
        self.assertEqual(monitor([0.0]), 2.0)
        self.assertEqual(monitor.evaluations, 1)
        self.assertEqual(monitor.valid_evaluations, 1)
        self.assertEqual(monitor.cached_objective_requests, 1)
        self.assertEqual(seen, [(0.0,)])
        with self.assertRaises(EvaluationBudgetExhausted):
            monitor([-0.0])  # Signed zeros are distinct numeric inputs.
        self.assertEqual(seen, [(0.0,)])
        self.assertEqual(monitor.best, (2.0, 0.0, (0.0,)))

    def test_invalid_callback_outcomes_are_not_cached(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            if len(calls) == 1:
                raise ValueError("intermittent failure")
            return 3.0

        monitor = ReliabilityMonitor(objective, 3, -1.0, False,
                                     cache_evaluations=True)
        with self.assertRaisesRegex(ValueError, "intermittent failure"):
            monitor([1.0])
        self.assertEqual(monitor([1.0]), 3.0)
        self.assertEqual(monitor([1.0]), 3.0)
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.invalid_evaluations, 1)
        self.assertEqual(monitor.valid_evaluations, 1)
        self.assertEqual(monitor.cached_objective_requests, 1)
        self.assertEqual(len(calls), 2)

    def test_cached_constrained_pair_uses_immutable_validated_snapshot(self):
        calls = []
        output = [8.0, 0.25]

        def objective(values):
            calls.append(tuple(values))
            return output

        monitor = ReliabilityMonitor(objective, 2, -1.0, True,
                                     cache_evaluations=True)
        self.assertEqual(monitor([0.5]), output)
        output[0] = -999.0
        self.assertEqual(monitor([0.5]), (8.0, 0.25))
        self.assertEqual(monitor.best, (8.0, 0.25, (0.5,)))
        self.assertEqual(monitor.evaluations, 1)
        self.assertEqual(monitor.cached_objective_requests, 1)
        self.assertEqual(len(calls), 1)

    def test_deterministic_discrete_duplicates_do_not_use_physical_budget(self):
        def run(cache):
            seed()
            calls = []

            def objective(values):
                calls.append(tuple(values))
                return 1.0

            ga = GA(cost_function=objective, population_size=6,
                    reliability_mode=True, max_evaluations=12,
                    acceptable_cost=0.0, probe_cost_function=False,
                    exit_check="generations", number_of_generations=1,
                    ensure_unique_individuals=False,
                    reliability_cache_evaluations=cache)
            ga.add(0.0, 1.0, step=1.0)
            result = ga.execute()
            self.assertTrue(result.success, result.messages)
            self.assertEqual(result.objective_evaluations, len(calls))
            self.assertEqual(result.best_objective, 1.0)
            return result, calls

        original, original_calls = run(False)
        cached, cached_calls = run(True)
        self.assertGreaterEqual(len(original_calls), 6)
        self.assertLessEqual(len(cached_calls), 2)
        self.assertEqual(cached.cached_objective_requests,
                         len(original_calls) - len(cached_calls))
        self.assertEqual(original.cached_objective_requests, 0)
        self.assertLess(cached.objective_evaluations, original.objective_evaluations)
        self.assertFalse(cached.acceptable)

    def test_cache_is_rejected_outside_reliability_mode(self):
        with self.assertRaisesRegex(ValueError, "requires reliability_mode"):
            GA(cost_function=lambda values: 1.0,
               reliability_cache_evaluations=True)
        with self.assertRaisesRegex(ValueError, "must be boolean"):
            GA(cost_function=lambda values: 1.0,
               reliability_mode=True, reliability_cache_evaluations=1)

    def test_exact_integer_bounds_do_not_round_illegal_points_into_domain(self):
        # Adjacent integers above binary64 precision have identical floats.
        # The original input must be checked without converting to float.
        limit = 2 ** 54
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0

        monitor = ReliabilityMonitor(objective, 5, 0.0, False,
                                     cache_evaluations=True,
                                     decision_bounds=((limit, limit),))
        for outside in (limit + 1, limit - 1):
            self.assertEqual(float(outside), float(limit))
            self.assertTrue(math.isnan(monitor([outside])))
            self.assertFalse(monitor.acceptable)
            self.assertIsNone(monitor.best)
        self.assertEqual(monitor.invalid_evaluations, 2)
        self.assertEqual(monitor.cached_objective_requests, 0)
        self.assertEqual(monitor([limit]), 0.0)
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor.best, (0.0, 0.0, (limit,)))
        self.assertEqual(monitor.evaluations, 3)
        self.assertEqual(calls, [(limit + 1,), (limit - 1,), (limit,)])

    def test_exact_integer_bounds_constrained_objective_cannot_fake_feasibility(self):
        limit = 2 ** 54
        monitor = ReliabilityMonitor(lambda values: (0.0, 0.0),
                                     2, 0.0, True,
                                     decision_bounds=((limit, limit),))
        self.assertTrue(math.isnan(monitor([limit + 1])))
        self.assertEqual(monitor.invalid_evaluations, 1)
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor((limit,)), (0.0, 0.0))
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor.valid_evaluations, 1)

    def test_reliability_rejects_in_bounds_but_off_grid_candidates(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0

        monitor = ReliabilityMonitor(objective, 5, 0.0, False,
                                     cache_evaluations=True,
                                     decision_bounds=((0.0, 1.0),),
                                     decision_grids=((0.0, 1.0, 0.5, 1),))
        for value in (0.25, 0.75, 0.25):
            self.assertTrue(math.isnan(monitor([value])))
            self.assertFalse(monitor.acceptable)
            self.assertIsNone(monitor.best)
        self.assertEqual(monitor.cached_objective_requests, 0)
        self.assertEqual(monitor.invalid_evaluations, 3)
        self.assertEqual(monitor([0.5]), 0.0)
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor([0.5]), 0.0)
        self.assertEqual(monitor.evaluations, 4)
        self.assertEqual(monitor.cached_objective_requests, 1)
        self.assertEqual(calls, [(0.25,), (0.75,), (0.25,), (0.5,)])

    def test_off_grid_constrained_population_cannot_claim_feasibility(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0, 0.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=4, acceptable_cost=0.0,
                probe_cost_function=False, constraint_handling="feasibility_rules")
        ga.add(0.0, 1.0, step=0.5)
        with patch("gadapt.ga_model.decision_variable.DecisionVariable.make_random_value",
                   return_value=0.25):
            result = ga.execute()
        self.assertFalse(result.success)
        self.assertFalse(result.acceptable)
        self.assertFalse(result.feasible)
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.termination_reason, "evaluation_failure")
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 0)
        self.assertEqual(calls, [(0.25,)] * 4)

    def test_non_dividing_discrete_step_rejects_ungenerated_upper_endpoint(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0

        monitor = ReliabilityMonitor(objective, 5, 0.0, False,
                                     decision_bounds=((0.0, 1.0),),
                                     decision_grids=((0.0, 1.0, 0.3, 1),))
        self.assertTrue(math.isnan(monitor([1.0])))
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor([0.9]), 0.0)
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor.best[2], (0.9,))
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(calls, [(1.0,), (0.9,)])

    def test_step_too_fine_for_grid_remains_continuous(self):
        monitor = ReliabilityMonitor(lambda values: 0.0, 1, 0.0, False,
                                     decision_bounds=((0.0, 1.0),),
                                     decision_grids=((0.0, 1.0, 1e-12, 12),))
        self.assertEqual(monitor([0.1234567891234]), 0.0)
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor.evaluations, 1)

    def test_large_exact_integer_grid_does_not_lose_index_precision(self):
        low = 2**54
        calls = []
        monitor = ReliabilityMonitor(lambda values: calls.append(values[0]) or 0.0,
                                     2, 0.0, False,
                                     decision_bounds=((low, low + 2),),
                                     decision_grids=((low, low + 2, 1, 0),))
        self.assertEqual(monitor([low + 1]), 0.0)
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor.best[2], (low + 1,))
        self.assertEqual(calls, [low + 1])

    def test_out_of_bounds_inputs_can_never_become_acceptable(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0

        monitor = ReliabilityMonitor(objective, 8, 0.0, False,
                                     decision_bounds=((0.0, 1.0),))
        invalid = [[-0.01], [1.01], [float("nan")], [float("inf")],
                   [True], ["0.5"], []]
        for values in invalid:
            self.assertTrue(math.isnan(monitor(values)))
            self.assertFalse(monitor.acceptable)
            self.assertIsNone(monitor.best)
        self.assertEqual(monitor.evaluations, len(invalid))
        self.assertEqual(monitor.invalid_evaluations, len(invalid))
        self.assertEqual(monitor.valid_evaluations, 0)
        self.assertEqual(len(calls), len(invalid))
        self.assertEqual(monitor([0.5]), 0.0)
        self.assertTrue(monitor.acceptable)
        self.assertEqual(monitor.best, (0.0, 0.0, (0.5,)))
        self.assertEqual(monitor.evaluations, 8)

    def test_constrained_cost_finder_never_accepts_outside_domain(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0, 0.0  # Claimed feasible even for an illegal vector.

        ga = GA(cost_function=objective, population_size=4,
                probe_cost_function=False, constraint_handling="feasibility_rules")
        ga.add(0.0, 1.0)
        options = GAOptions(ga)
        monitor = ReliabilityMonitor(objective, 8, 0.0, True,
                                     decision_bounds=((0.0, 1.0),))
        options.cost_function = monitor
        options.reliability_monitor = monitor
        population = Population(options)
        for candidate in population:
            candidate[0].value = 2.0
        finder = ConstraintHandlingCostFinder(ConstraintHandler("feasibility_rules"))
        with self.assertRaisesRegex(ValueError, "All evaluated candidate costs were invalid"):
            finder.find_costs(population)
        self.assertEqual(monitor.evaluations, 4)
        self.assertEqual(monitor.invalid_evaluations, 4)
        self.assertFalse(monitor.acceptable)
        self.assertIsNone(monitor.best)
        self.assertEqual(len(calls), 4)

    def test_invalid_domain_points_never_enter_deterministic_cache(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0

        monitor = ReliabilityMonitor(objective, 4, 0.0, False,
                                     cache_evaluations=True,
                                     decision_bounds=((0.0, 1.0),))
        self.assertTrue(math.isnan(monitor([3.0])))
        self.assertTrue(math.isnan(monitor([3.0])))
        self.assertEqual(monitor.cached_objective_requests, 0)
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor([0.5]), 0.0)
        self.assertEqual(monitor([0.5]), 0.0)
        self.assertEqual(monitor.evaluations, 3)
        self.assertEqual(monitor.invalid_evaluations, 2)
        self.assertEqual(monitor.valid_evaluations, 1)
        self.assertEqual(monitor.cached_objective_requests, 1)
        self.assertEqual(calls, [(3.0,), (3.0,), (0.5,)])

    def test_reliability_rejects_nonfinite_bounds_before_objective(self):
        for lower, upper, step in (
                (float("nan"), 1.0, None),
                (0.0, float("inf"), None),
                (0.0, 1.0, float("nan"))):
            with self.subTest(lower=lower, upper=upper, step=step):
                calls = []

                def objective(values):
                    calls.append(tuple(values))
                    return 0.0

                ga = GA(cost_function=objective, population_size=4,
                        reliability_mode=True, max_evaluations=8,
                        acceptable_cost=0.0, probe_cost_function=True)
                ga.add(lower, upper, step=step)
                result = ga.execute()
                self.assertFalse(result.success)
                self.assertEqual(result.termination_reason, "validation_failed")
                self.assertEqual(result.objective_evaluations, 0)
                self.assertEqual(result.solution_status, "no_valid_evaluation")
                self.assertIn("finite variable bounds", str(result.messages))
                self.assertEqual(calls, [])

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
        self.assertEqual(result.objective_evaluations, 1)  # First probe already met target.
        self.assertEqual(result.number_of_iterations, 0)
        self.assertEqual(len(calls), 1)

    def test_first_acceptable_probe_never_calls_opposite_boundary(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            if values[0] == 1.0:
                raise AssertionError("No need to evaluate this boundary")
            return 0.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=12, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.objective_evaluations, 1)
        self.assertEqual(result.valid_objective_evaluations, 1)
        self.assertEqual(result.invalid_objective_evaluations, 0)
        self.assertEqual(result.result_values, {0: 0.0})
        self.assertEqual(calls, [(0.0,)])

    def test_constrained_acceptable_first_probe_avoids_second_call(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            if values[0] == 1.0:
                raise AssertionError("No need to evaluate this boundary")
            return 0.0, 0.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=12,
                acceptable_cost=0.0, constraint_handling="feasibility_rules")
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertTrue(result.feasible)
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.objective_evaluations, 1)
        self.assertEqual(result.result_values, {0: 0.0})
        self.assertEqual(calls, [(0.0,)])

    def test_first_unacceptable_probe_still_checks_opposite_boundary(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 1.0 if values[0] == 0.0 else 0.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=12, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertEqual(result.objective_evaluations, 2)
        self.assertEqual(result.result_values, {0: 1.0})
        self.assertEqual(calls, [(0.0,), (1.0,)])

    def test_first_probe_target_cannot_override_invalid_structural_options(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 0.0

        ga = GA(cost_function=objective, population_size=3,
                reliability_mode=True, max_evaluations=10, acceptable_cost=0.0)
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertFalse(result.termination_reason == "acceptable_target")
        self.assertEqual(result.termination_reason, "validation_failed")
        self.assertEqual(result.objective_evaluations, 0)
        self.assertEqual(calls, [])  # Invalid structure is rejected before any probe.

    def test_first_acceptable_candidate_stops_initial_generation_immediately(self):
        seed()
        seen = []

        def objective(values):
            seen.append(tuple(values))
            return 0.0

        ga = GA(cost_function=objective, population_size=6,
                reliability_mode=True, max_evaluations=6,
                acceptable_cost=0.0, probe_cost_function=False)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertEqual(result.solution_status, "acceptable")
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.objective_evaluations, 1)
        self.assertEqual(result.valid_objective_evaluations, 1)
        self.assertEqual(result.number_of_iterations, 0)
        self.assertEqual(result.result_values, {0: seen[0][0]})
        self.assertEqual(len(seen), 1)

    def test_third_candidate_target_does_not_evaluate_rest_of_population(self):
        seed()
        seen = []

        def objective(values):
            seen.append(tuple(values))
            return 0.0 if len(seen) == 3 else 1.0

        ga = GA(cost_function=objective, population_size=8,
                reliability_mode=True, max_evaluations=8,
                acceptable_cost=0.0, probe_cost_function=False)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.objective_evaluations, 3)
        self.assertEqual(result.best_objective, 0.0)
        self.assertEqual(result.result_values, {0: seen[2][0]})
        self.assertEqual(len(seen), 3)

    def test_last_budgeted_call_that_reaches_target_reports_acceptance(self):
        seed()
        seen = []

        def objective(values):
            seen.append(tuple(values))
            return 0.0 if len(seen) == 4 else 1.0

        ga = GA(cost_function=objective, population_size=4,
                reliability_mode=True, max_evaluations=4,
                acceptable_cost=0.0, probe_cost_function=False)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.best_objective, 0.0)
        self.assertEqual(len(seen), 4)

    def test_early_target_requires_both_feasibility_and_quality(self):
        seed()
        seen = []

        def objective(values):
            seen.append(tuple(values))
            if len(seen) <= 2:
                return (-100.0, 0.5)  # Never accept infeasible low cost.
            if len(seen) == 3:
                return (1.0, 0.0)  # Feasible but fails the threshold.
            return (0.2, 0.0)

        ga = GA(cost_function=objective, population_size=8,
                reliability_mode=True, max_evaluations=8,
                acceptable_cost=0.2, probe_cost_function=False,
                constraint_handling="penalty", constraint_penalty_weight=0.001)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertTrue(result.feasible)
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(result.best_objective, 0.2)
        self.assertEqual(result.best_violation, 0.0)
        self.assertEqual(result.result_values, {0: seen[3][0]})
        self.assertEqual(len(seen), 4)

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

    def test_positive_fraction_violation_cannot_underflow_to_feasible(self):
        tiny = Fraction(1, 10 ** 400)
        self.assertGreater(tiny, 0)
        self.assertEqual(float(tiny), 0.0)
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return (0.0, tiny)

        monitor = ReliabilityMonitor(objective, 2, 0.0, True,
                                     decision_bounds=((0.0, 1.0),))
        for value in (0.25, 0.75):
            self.assertTrue(math.isnan(monitor([value])))
            self.assertFalse(monitor.acceptable)
            self.assertIsNone(monitor.best)
        self.assertEqual(monitor.evaluations, 2)
        self.assertEqual(monitor.invalid_evaluations, 2)
        self.assertEqual(monitor.valid_evaluations, 0)
        self.assertEqual(calls, [(0.25,), (0.75,)])

    def test_underflowed_violation_never_creates_feasible_ga_result(self):
        seed()
        tiny = Fraction(1, 10 ** 400)
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return (0.0, tiny)

        ga = GA(cost_function=objective, population_size=4,
                probe_cost_function=False, reliability_mode=True,
                max_evaluations=8, acceptable_cost=0.0,
                constraint_handling="feasibility_rules")
        ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.acceptable)
        self.assertFalse(result.feasible)
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.objective_evaluations, 8)
        self.assertEqual(result.invalid_objective_evaluations, 8)
        self.assertEqual(result.valid_objective_evaluations, 0)
        self.assertEqual(len(calls), 8)

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

    def test_boolean_callback_is_invalid_at_scalar_cost_finder_boundary(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return True if len(calls) <= 4 else 2.0

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, reliability_mode=True,
                max_evaluations=8, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.invalid_population_resamples, 1)
        self.assertEqual(result.objective_evaluations, 8)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(result.best_objective, 2.0)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(len(calls), 8)

    def test_boolean_only_callback_never_becomes_a_valid_incumbent(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return False

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, reliability_mode=True,
                max_evaluations=9, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertFalse(result.acceptable)
        self.assertFalse(result.feasible)
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.objective_evaluations, 9)
        self.assertEqual(result.invalid_objective_evaluations, 9)
        self.assertEqual(result.valid_objective_evaluations, 0)
        self.assertEqual(len(calls), 9)

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

    def test_overflowing_real_is_charged_invalid_and_recovery_continues(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return 10**400 if len(calls) <= 4 else 1.0

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, reliability_mode=True,
                max_evaluations=8, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.invalid_population_resamples, 1)
        self.assertEqual(result.objective_evaluations, 8)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(result.best_objective, 1.0)
        self.assertFalse(result.acceptable)
        self.assertEqual(len(calls), 8)

    def test_overflowing_real_monitor_never_records_false_incumbent(self):
        monitor = ReliabilityMonitor(lambda values: 10**400,
                                     max_evaluations=1, acceptable_cost=0.0,
                                     constrained=False)
        self.assertEqual(monitor([0.0]), 10**400)
        self.assertEqual(monitor.evaluations, 1)
        self.assertEqual(monitor.invalid_evaluations, 1)
        self.assertEqual(monitor.valid_evaluations, 0)
        self.assertIsNone(monitor.best)
        self.assertFalse(monitor.acceptable)
        with self.assertRaises(EvaluationBudgetExhausted):
            monitor([0.0])
        self.assertEqual(monitor.evaluations, 1)

    def test_recovery_discovers_first_valid_after_two_invalid_cohorts(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return float("nan") if len(calls) <= 8 else 1.0

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, reliability_mode=True,
                max_evaluations=12, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.invalid_population_resamples, 2)
        self.assertEqual(result.objective_evaluations, 12)
        self.assertEqual(result.invalid_objective_evaluations, 8)
        self.assertEqual(result.valid_objective_evaluations, 4)
        self.assertEqual(result.best_objective, 1.0)
        self.assertTrue(result.feasible)
        self.assertFalse(result.acceptable)
        self.assertEqual(len(calls), 12)

    def test_recovery_constrained_accepts_first_valid_feasible_candidate(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return (float("nan"), 0.0) if len(calls) <= 4 else (0.0, 0.0)

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, constraint_handling="feasibility_rules",
                reliability_mode=True, max_evaluations=14, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertTrue(result.acceptable)
        self.assertEqual(result.termination_reason, "acceptable_target")
        self.assertEqual(result.invalid_population_resamples, 1)
        self.assertEqual(result.objective_evaluations, 5)
        self.assertEqual(result.valid_objective_evaluations, 1)
        self.assertEqual(result.invalid_objective_evaluations, 4)
        self.assertEqual(result.best_violation, 0.0)
        self.assertEqual(result.result_values, {0: calls[4][0]})
        self.assertEqual(len(calls), 5)

    def test_recovery_exhausts_partial_last_cohort_without_extra_calls(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return float("nan")

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, reliability_mode=True,
                max_evaluations=10, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.invalid_population_resamples, 2)
        self.assertEqual(result.objective_evaluations, 10)
        self.assertEqual(result.invalid_objective_evaluations, 10)
        self.assertEqual(len(calls), 10)

    def test_recovery_honors_timeout_before_resampling(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return float("nan")

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, reliability_mode=True,
                max_evaluations=20, acceptable_cost=0.0, timeout=1)
        ga.add(-1.0, 1.0)
        with patch("gadapt.execution.ga_executor.datetime") as clock:
            clock.now.return_value = datetime.now() + timedelta(seconds=1000)
            result = ga.execute()
        self.assertFalse(result.success)
        self.assertEqual(result.termination_reason, "timeout")
        self.assertEqual(result.invalid_population_resamples, 0)
        self.assertEqual(result.objective_evaluations, 4)
        self.assertEqual(len(calls), 4)

    def test_legacy_all_invalid_still_stops_without_retries(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            return float("nan")

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, exit_check="generations",
                number_of_generations=1)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertEqual(len(calls), 4)
        self.assertIsNone(result.invalid_population_resamples)

    def test_callback_cannot_spoof_acceptable_target(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            raise AcceptableTargetReached("user callback is not the monitor")

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, reliability_mode=True,
                max_evaluations=9, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.objective_evaluations, 9)
        self.assertEqual(result.invalid_objective_evaluations, 9)
        self.assertEqual(len(calls), 9)

    def test_callback_cannot_spoof_budget_exhaustion_in_constrained_mode(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            raise EvaluationBudgetExhausted("user callback is not the monitor")

        ga = GA(cost_function=objective, probe_cost_function=False,
                population_size=4, reliability_mode=True,
                constraint_handling="feasibility_rules",
                max_evaluations=9, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.solution_status, "no_valid_evaluation")
        self.assertEqual(result.objective_evaluations, 9)
        self.assertEqual(result.invalid_objective_evaluations, 9)
        self.assertEqual(len(calls), 9)

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

    def test_invalid_boundary_probe_no_longer_aborts_valid_interior(self):
        seed()
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
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertEqual(result.termination_reason, "budget_exhausted")
        self.assertEqual(result.solution_status, "feasible_but_unacceptable")
        self.assertEqual(result.objective_evaluations, 10)
        self.assertEqual(result.invalid_objective_evaluations, 1)
        self.assertEqual(result.valid_objective_evaluations, 9)
        self.assertEqual(len(calls), 10)
        self.assertTrue(any("Boundary objective probe failed" in msg
                            for level, msg in result.messages))
        self.assertGreaterEqual(result.result_values[0], -1.0)

    def test_invalid_constrained_probe_pair_no_longer_aborts(self):
        seed()
        calls = []

        def objective(values):
            calls.append(tuple(values))
            if values[0] == -1.0:
                return float("nan"), 0.0
            return 1.0, 0.0

        ga = GA(cost_function=objective, population_size=4, reliability_mode=True,
                max_evaluations=6, acceptable_cost=0.0,
                constraint_handling="feasibility_rules")
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertFalse(result.acceptable)
        self.assertTrue(result.feasible)
        self.assertEqual(result.best_objective, 1.0)
        self.assertEqual(result.objective_evaluations, 6)
        self.assertEqual(result.invalid_objective_evaluations, 1)
        self.assertEqual(len(calls), 6)

    def test_boundary_probe_recovery_never_masks_structural_errors(self):
        calls = []

        def objective(values):
            calls.append(tuple(values))
            raise ValueError("boundary undefined")

        ga = GA(cost_function=objective, population_size=3, reliability_mode=True,
                max_evaluations=5, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertEqual(result.termination_reason, "validation_failed")
        self.assertEqual(result.objective_evaluations, 0)
        self.assertEqual(len(calls), 0)  # Structural validation rejects this before probing.
        self.assertTrue(any("Population size" in str(message) for message in result.messages))

    def test_noncallable_objective_still_fails_validation_without_charges(self):
        ga = GA(cost_function=42, population_size=4, reliability_mode=True,
                max_evaluations=6, acceptable_cost=0.0)
        ga.add(-1.0, 1.0)
        result = ga.execute()
        self.assertFalse(result.success)
        self.assertEqual(result.termination_reason, "validation_failed")
        self.assertEqual(result.objective_evaluations, 0)
        self.assertEqual(result.solution_status, "no_valid_evaluation")

    def test_legacy_boundary_failure_stays_strict(self):
        def objective(values):
            if values[0] == -1.0:
                raise ValueError("domain excludes left endpoint")
            return 1.0

        ga = GA(cost_function=objective, population_size=4,
                exit_check="generations", number_of_generations=2)
        ga.add(-1.0, 1.0)
        with self.assertRaisesRegex(Exception, "domain excludes left endpoint"):
            ga.execute()  # Preserve legacy validator's raised exception.

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

    def test_least_violation_survives_weak_penalty_and_immigration(self):
        # All four candidates are infeasible. Weak penalty ranks the
        # most promising (smallest violation) as the worst by scalar cost.
        def objective(values):
            x = values[0]
            return (100.0 if x > -0.2 else 0.0, -x)

        def prepare(reliable):
            ga = GA(cost_function=objective, population_size=4,
                    keep_elitism_percentage=50, immigration_number=1,
                    constraint_handling="penalty", constraint_penalty_weight=0.001,
                    probe_cost_function=False)
            ga.add(-1.0, 0.0)
            options = GAOptions(ga)
            monitor = None
            if reliable:
                monitor = ReliabilityMonitor(objective, 20, -1.0, constrained=True)
                options.cost_function = monitor
                options.reliability_monitor = monitor
            population = Population(options)
            for c, x in zip(population, (-0.1, -0.6, -0.7, -0.8)):
                c[0].value = x
            finder = ConstraintHandlingCostFinder(ConstraintHandler("penalty", 0.001))
            finder.find_costs(population)
            return population, monitor

        legacy, _ = prepare(False)
        self.assertTrue(all(c.violation_value >= 0.6 for c in legacy))
        population, monitor = prepare(True)
        self.assertEqual(monitor.best[1], 0.1)
        elite = next(c for c in population if c.get_values_tuple() == (-0.1,))
        self.assertEqual(elite.objective_value, 100.0)
        self.assertTrue(elite.succ)
        self.assertTrue(elite._reliability_incumbent_elite)
        self.assertEqual(monitor.evaluations, 4)

        population.population_generation += 1
        CommonPopulationImmigrator(RandomCandidateSolutionImmigrator()).immigrate(population)
        self.assertFalse(elite.is_immigrant)
        self.assertEqual(elite.get_values_tuple(), (-0.1,))
        self.assertEqual(monitor.evaluations, 4)  # No re-evaluation during immigration.

    def test_prior_infeasible_probe_reenters_search_without_extra_call(self):
        def objective(values):
            x = values[0]
            return (100.0 if x > -0.2 else 0.0, -x)

        ga = GA(cost_function=objective, population_size=4,
                keep_elitism_percentage=50, constraint_handling="penalty",
                constraint_penalty_weight=0.001, probe_cost_function=False)
        ga.add(-1.0, 0.0)
        options = GAOptions(ga)
        monitor = ReliabilityMonitor(objective, 20, -1.0, constrained=True)
        monitor([-0.05])
        options.cost_function = monitor
        options.reliability_monitor = monitor
        population = Population(options)
        for c, x in zip(population, (-0.5, -0.6, -0.7, -0.8)):
            c[0].value = x
        finder = ConstraintHandlingCostFinder(ConstraintHandler("penalty", 0.001))
        finder.find_costs(population)
        self.assertEqual(monitor.evaluations, 5)  # One probe + exactly four candidates.
        elite = next(c for c in population if c.get_values_tuple() == (-0.05,))
        self.assertTrue(elite.succ)
        self.assertEqual(elite.violation_value, 0.05)
        self.assertEqual(elite.objective_value, 100.0)
        self.assertTrue(elite._reliability_incumbent_elite)

    def test_first_feasible_point_supersedes_least_violation_protection(self):
        def objective(values):
            x = values[0]
            if x >= 0.0:
                return 110.0, 0.0
            return (100.0 if x > -0.2 else 0.0, -x)

        ga = GA(cost_function=objective, population_size=4,
                keep_elitism_percentage=50, immigration_number=1,
                constraint_handling="penalty", constraint_penalty_weight=0.001,
                probe_cost_function=False)
        ga.add(-1.0, 1.0)
        options = GAOptions(ga)
        monitor = ReliabilityMonitor(objective, 20, -1.0, constrained=True)
        options.cost_function = monitor
        options.reliability_monitor = monitor
        population = Population(options)
        for c, x in zip(population, (-0.1, -0.6, -0.7, -0.8)):
            c[0].value = x
        finder = ConstraintHandlingCostFinder(ConstraintHandler("penalty", 0.001))
        finder.find_costs(population)
        old = next(c for c in population if c.get_values_tuple() == (-0.1,))
        population.population_generation += 1
        candidate = next(c for c in population if c is not old)
        candidate[0].value = 0.5
        candidate.is_immigrant = True
        candidate.population_generation = population.population_generation
        finder.find_costs(population)
        self.assertEqual(monitor.best, (110.0, 0.0, (0.5,)))
        feasible = next(c for c in population if c.get_values_tuple() == (0.5,))
        self.assertTrue(feasible._reliability_incumbent_elite)
        self.assertTrue(feasible._reliability_feasible_elite)

        population.population_generation += 1
        before = monitor.evaluations
        CommonPopulationImmigrator(RandomCandidateSolutionImmigrator()).immigrate(population)
        self.assertFalse(feasible.is_immigrant)
        self.assertEqual(feasible.get_values_tuple(), (0.5,))
        self.assertEqual(monitor.evaluations, before)

    def test_precise_feasible_improvement_resets_stagnation_and_refresh_debt(self):
        # Three strictly improving objectives collapse to float 1.0.
        high = Fraction(1) + Fraction(3, 2**55)
        middle = Fraction(1) + Fraction(2, 2**55)
        low = Fraction(1) + Fraction(1, 2**55)
        self.assertEqual([float(x) for x in (high, middle, low)],
                         [1.0, 1.0, 1.0])
        values = (high, middle, low)
        monitor = ReliabilityMonitor(lambda v: values[int(v[0])],
                                     6, 0.0, False)
        monitor([0])
        monitor.completed_generation()
        monitor([0])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 1)
        monitor.refreshes_since_improvement = 2
        monitor([1])
        monitor.completed_generation()
        self.assertEqual(monitor.best, (1.0, 0.0, (1,)))
        self.assertEqual(monitor.stagnant_generations, 0)
        self.assertEqual(monitor.refreshes_since_improvement, 0)
        monitor([2])
        monitor.completed_generation()
        self.assertEqual(monitor.best, (1.0, 0.0, (2,)))
        self.assertEqual(monitor.stagnant_generations, 0)
        monitor([1])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 1)
        self.assertEqual(monitor.evaluations, 5)
        self.assertEqual(monitor.valid_evaluations, 5)

    def test_precise_violation_improvement_resets_stagnation_before_feasibility(self):
        # The scalar ranker rounds these to equal violation, but a feasible
        # point is not yet found. A real violation reduction still matters.
        high = Fraction(1) + Fraction(3, 2**55)
        middle = Fraction(1) + Fraction(2, 2**55)
        low = Fraction(1) + Fraction(1, 2**55)
        values = (high, middle, low)
        monitor = ReliabilityMonitor(lambda v: (8.0, values[int(v[0])]),
                                     6, -1.0, True)
        monitor([0])
        monitor.completed_generation()
        monitor([0])
        monitor.completed_generation()
        self.assertEqual(monitor.stagnant_generations, 1)
        monitor([1])
        monitor.completed_generation()
        self.assertEqual(monitor.best, (8.0, 1.0, (1,)))
        self.assertEqual(monitor.stagnant_generations, 0)
        monitor([2])
        monitor.completed_generation()
        self.assertEqual(monitor.best, (8.0, 1.0, (2,)))
        self.assertEqual(monitor.stagnant_generations, 0)
        self.assertFalse(monitor.acceptable)
        self.assertEqual(monitor.evaluations, 4)

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

    def test_restart_restores_exact_cached_constrained_incumbent_without_evaluation(self):
        seed()
        actual_calls = []

        def objective(values):
            actual_calls.append(tuple(values))
            return (100.0, 0.0) if values[0] >= 0 else (0.0, -values[0])

        ga = GA(cost_function=objective, population_size=6, reliability_mode=True,
                max_evaluations=20, acceptable_cost=-1.0, probe_cost_function=False,
                constraint_handling="penalty", constraint_penalty_weight=0.001,
                reliability_refresh_patience=2, reliability_restart_after_refreshes=2)
        ga.add(-1.0, 1.0)
        monitor = ReliabilityMonitor(objective, 20, -1.0, constrained=True)
        monitor([0.75])  # A real prior evaluation absent from the population.
        ga._reliability_monitor = monitor
        options = GAOptions(ga)
        options.cost_function = monitor
        population = Population(options)
        for c in population:
            c[0].value = -0.5
        executor = GAExecutor.__new__(GAExecutor)
        executor.population = population
        executor.ga_options = options
        executor.reliability_monitor = monitor
        executor.cost_finder = ConstraintHandlingCostFinder(ConstraintHandler("penalty", 0.001))

        monitor.stagnant_generations = 6
        monitor.refreshes_since_improvement = 1
        self.assertFalse(executor.restart_if_stagnant())
        monitor.refreshes_since_improvement = 2
        self.assertTrue(executor.restart_if_stagnant())
        self.assertEqual(len(population), 6)
        self.assertEqual(population[0].get_values_tuple(), (0.75,))
        self.assertEqual(population[0].objective_value, 100.0)
        self.assertEqual(population[0].violation_value, 0.0)
        self.assertEqual(population[0].cost_value, 100.0)
        self.assertTrue(population[0].succ)
        self.assertTrue(all(math.isnan(c.cost_value) for c in population.candidate_solutions[1:]))
        self.assertEqual(monitor.evaluations, 1)
        self.assertEqual(actual_calls, [(0.75,)])
        self.assertEqual(monitor.restarts, 1)
        self.assertEqual(monitor.refreshes_since_improvement, 0)
        self.assertFalse(executor.restart_if_stagnant())

    def test_restart_requires_budget_for_entire_reseed(self):
        seed()
        ga = GA(cost_function=lambda values: float(values[0]), population_size=6,
                reliability_mode=True, max_evaluations=5, acceptable_cost=-1.0,
                probe_cost_function=False, reliability_refresh_patience=2,
                reliability_restart_after_refreshes=1)
        ga.add(0.0, 1.0)
        monitor = ReliabilityMonitor(ga.cost_function, 5, -1.0, False)
        monitor([0.5])  # Only four calls remain, but five new points are required.
        ga._reliability_monitor = monitor
        options = GAOptions(ga)
        population = Population(options)
        executor = GAExecutor.__new__(GAExecutor)
        executor.population = population
        executor.ga_options = options
        executor.reliability_monitor = monitor
        executor.cost_finder = ElitismCostFinder()
        monitor.stagnant_generations = 2
        monitor.refreshes_since_improvement = 1
        before = [c.get_values_tuple() for c in population]
        self.assertFalse(executor.restart_if_stagnant())
        self.assertEqual([c.get_values_tuple() for c in population], before)
        self.assertEqual(monitor.evaluations, 1)
        self.assertEqual(monitor.restarts, 0)

    def test_restart_after_two_failed_refreshes_stays_under_total_budget(self):
        def run(restart):
            seed()
            calls = []

            def objective(values):
                calls.append(tuple(values))
                return 1.0

            ga = GA(cost_function=objective, population_size=8,
                    reliability_mode=True, max_evaluations=70, acceptable_cost=0.0,
                    probe_cost_function=False, exit_check="generations",
                    number_of_generations=9, ensure_unique_individuals=False,
                    reliability_refresh_patience=2,
                    reliability_refresh_percentage=25.0,
                    reliability_restart_after_refreshes=(2 if restart else None))
            ga.add(-1.0, 1.0)
            result = ga.execute()
            self.assertTrue(result.success, result.messages)
            self.assertEqual(result.objective_evaluations, len(calls))
            self.assertLessEqual(result.objective_evaluations, 70)
            self.assertEqual(result.best_objective, 1.0)
            self.assertEqual(result.solution_status, "feasible_but_unacceptable")
            return result

        baseline = run(False)
        restarted = run(True)
        self.assertEqual(baseline.reliability_restarts, 0)
        self.assertEqual(restarted.reliability_restarts, 1)
        self.assertEqual(restarted.stagnation_refreshes, 2)

    def test_incumbent_improvement_clears_restart_debt(self):
        monitor = ReliabilityMonitor(lambda values: float(values[0]), 5, -1.0, False)
        monitor([2.0])
        monitor.completed_generation()
        monitor.refreshes_since_improvement = 2
        monitor([1.0])
        monitor.completed_generation()
        self.assertEqual(monitor.refreshes_since_improvement, 0)
        self.assertEqual(monitor.stagnant_generations, 0)

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
