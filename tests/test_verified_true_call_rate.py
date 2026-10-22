"""I37 ZERO-PHYSICS structural regression tests; not IEEE, Dijkstra or evidence of superiority."""
import math
import random
import unittest

from gadapt.ga import GA
from gadapt.operations.mutation.decision_variable_mutation.verified_call_rate_bandit import (
    VerifiedCallRateBandit,
)
from gadapt.operations.mutation.decision_variable_mutation.credit_based_decision_variable_mutator import (
    CreditBasedDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (
    RandomDecisionVariableMutator,
)


class TrueCallRateUnitTests(unittest.TestCase):
    def test_legacy_credit_equal_despite_fifty_percent_throughput_gap(self):
        b = VerifiedCallRateBandit(3)
        b.add_operator()
        b.add_operator()
        # Same 50% verified success, but operator 0 fails after one paid call
        # while operator 1 fails after three paid calls.
        for _ in range(500):
            b.observe(0, "verified_feasible", 3)
            b.observe(0, "measured_infeasible", 1)
            b.observe(1, "verified_feasible", 3)
            b.observe(1, "measured_infeasible", 3)
        a, c = b.summary()
        old_credit_a = a["verified_successes"] / (3 * a["trials"])
        old_credit_b = c["verified_successes"] / (3 * c["trials"])
        self.assertEqual(old_credit_a, old_credit_b)
        self.assertAlmostEqual(a["certified_success_per_true_call"], .25)
        self.assertAlmostEqual(c["certified_success_per_true_call"], 1 / 6)
        self.assertAlmostEqual(a["certified_success_per_true_call"] /
                               c["certified_success_per_true_call"], 1.5)
        self.assertGreater(b.optimistic_score(0), b.optimistic_score(1))
        self.assertEqual(b.choose(), 0)

    def test_unknown_is_paid_not_verified_and_stays_optimistically_unresolved(self):
        b = VerifiedCallRateBandit(3)
        b.add_operator()
        b.observe(0, "numerically_unknown", 2)
        row = b.summary()[0]
        self.assertEqual(row["actual_calls"], 2)
        self.assertEqual(row["verified_successes"], 0)
        self.assertEqual(row["unknown"], 1)
        self.assertEqual(row["certified_success_per_true_call"], 0)
        self.assertGreater(row["optimistic_score"], 0)

    def test_no_unpaid_credit_and_strict_actual_call_check(self):
        b = VerifiedCallRateBandit(3)
        b.add_operator()
        with self.assertRaises(ValueError):
            b.observe(0, "verified_feasible", 1)
        with self.assertRaises(ValueError):
            b.observe(0, "measured_infeasible", 0)
        with self.assertRaises(ValueError):
            b.observe(0, "some_made_up_status", 3)
        with self.assertRaises(ValueError):
            b.observe(0, "numerically_unknown", True)
        self.assertEqual(b.summary()[0]["actual_calls"], 0)
        self.assertIsNone(b.summary()[0]["optimistic_score"])

    def test_opt_in_and_legacy_compatibility(self):
        params = dict(mutation_operator_policy="ucb_true_call_rate",
                      mutation_operator_credit="censored_verified_per_cost",
                      mutation_evaluation_counter=lambda: 0,
                      mutation_scenario_count=3,
                      mutation_violation_function=lambda x, score: None)
        ga = GA(cost_function=lambda x: sum(x), **params)
        self.assertEqual(ga.mutation_operator_policy, "ucb_true_call_rate")
        with self.assertRaises(ValueError):
            GA(cost_function=lambda x: sum(x),
               mutation_operator_policy="ucb_true_call_rate")
        legacy = GA(cost_function=lambda x: sum(x))
        self.assertEqual(legacy.mutation_operator_policy, "legacy")
        self.assertEqual(legacy.mutation_operator_credit, "objective")

    def test_core_observation_single_operator_verified_and_failure(self):
        feedback = {"status": "verified_feasible", "actual_calls": 3,
                    "observed_scenarios": ["a", "b", "c"],
                    "observed_violations": [0., 0., 0.]}
        controller = CreditBasedDecisionVariableMutator(
            policy="ucb_true_call_rate", credit="censored_verified_per_cost",
            evaluation_counter=lambda: 0, scenario_count=3,
            violation_function=lambda x, score: feedback)
        controller.append(RandomDecisionVariableMutator())
        class Gene:
            value = 0.4
            decision_variable = type("Decision", (), {"variable_id": 0})()
        class Offspring(list):
            _succ = True
            cost_value = 0.0
        gene = Gene()
        candidate = Offspring([gene])
        controller._traces[id(gene)] = 0
        controller.observe(candidate, physically_evaluated=True, measured_scenarios=3)
        self.assertEqual(controller.summary()[0]["verified_true_call_rate"]["actual_calls"], 3)
        self.assertEqual(controller.summary()[0]["verified_true_call_rate"]["verified_successes"], 1)
        feedback = {"status": "measured_infeasible", "actual_calls": 1,
                    "observed_scenarios": ["a"], "observed_violations": [.2]}
        controller._traces[id(gene)] = 0
        controller.observe(candidate, physically_evaluated=True, measured_scenarios=1)
        record = controller.summary()[0]["verified_true_call_rate"]
        self.assertEqual(record["actual_calls"], 4)
        self.assertEqual(record["verified_successes"], 1)
        self.assertAlmostEqual(record["certified_success_per_true_call"], .25)

    def test_actual_synthetic_core_ga_trace(self):
        # Artificial toy evaluator only. Physical budget counter is a mock.
        random.seed(376)
        costs = {"true_calls": 0, "requests": 0, "last": None}
        budget = 90
        def mock_objective(x):
            costs["requests"] += 1
            costs["last"] = None
            if costs["true_calls"] + 3 > budget:
                return 1e12
            observed = []
            for j in range(3):
                costs["true_calls"] += 1
                violation = max(0., sum(x) - 1.1) if j == 0 else 0.
                observed.append(violation)
                if violation > 0:
                    break
            costs["last"] = (tuple(x), costs["true_calls"], {
                "status": "measured_infeasible" if any(v > 0 for v in observed)
                          else "verified_feasible",
                "actual_calls": len(observed),
                "observed_scenarios": ["a", "b", "c"][:len(observed)],
                "observed_violations": observed})
            return 1e9 + sum(x) if observed[-1] else sum((v - .4)**2 for v in x)
        def cached_feedback(x, score):
            v = costs["last"]
            if v is None or tuple(x) != v[0] or costs["true_calls"] != v[1]:
                return None
            return v[2]
        ga = GA(cost_function=mock_objective, population_size=12,
                exit_check="generations", number_of_generations=20,
                exit_function=lambda: costs["true_calls"] >= budget - 2,
                mutation_operator_policy="ucb_true_call_rate",
                mutation_operator_credit="censored_verified_per_cost",
                mutation_evaluation_counter=lambda: costs["true_calls"],
                mutation_violation_function=cached_feedback,
                mutation_scenario_count=3,
                number_of_mutation_decision_variables=1,
                candidate_solution_mutation="random",
                ensure_unique_individuals=False, timeout=30)
        for _ in range(3):
            ga.add(0., 1.)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        self.assertLessEqual(costs["true_calls"], budget)
        self.assertTrue(result.operator_credit_summary)
        paid = sum(r["verified_true_call_rate"]["actual_calls"]
                   for r in result.operator_credit_summary)
        # Only mutated offspring are attributed; all first-generation AC
        # still paid globally and not fictitiously attributed to a mutator.
        self.assertLessEqual(paid, costs["true_calls"])
        self.assertTrue(all(r["verified_true_call_rate"]["actual_calls"] >= 0
                            for r in result.operator_credit_summary))


if __name__ == "__main__":
    unittest.main()
