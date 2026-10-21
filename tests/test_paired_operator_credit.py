"""Regression tests for physically-accounted pre/post mutation credit in real GA."""
import math
import random
import unittest

from gadapt.ga import GA


class PairedCreditTests(unittest.TestCase):
    def _optimize(self, credit="objective", limit=250, policy="ucb"):
        random.seed(17)
        scores = {}
        actual = {"count": 0, "requested": 0}

        def objective(x):
            actual["requested"] += 1
            if actual["count"] >= limit:
                return 1e8  # not a real evaluation
            actual["count"] += 1
            score = float(sum((v - 0.4) ** 2 for v in x))
            scores[tuple(x)] = score
            return score

        def physical_violation(x, score):
            # External physics/constraints would be read from a cached
            # solver result. Here the property is deterministic and cached.
            if tuple(x) not in scores:
                return None
            return max(0.0, 0.5 - sum(x))

        ga = GA(
            cost_function=objective, population_size=12,
            mutation_operator_policy=policy,
            mutation_operator_credit=credit,
            mutation_credit_assignment="paired",
            mutation_evaluation_counter=lambda: actual["count"],
            mutation_violation_function=physical_violation if credit == "feasibility" else None,
            ensure_unique_individuals=False,
            number_of_mutation_decision_variables=1,
            candidate_solution_mutation="random",
            exit_check="generations", number_of_generations=10,
            exit_function=lambda: actual["count"] >= limit,
            timeout=30,
        )
        for _ in range(4):
            ga.add(0.0, 1.0)
        result = ga.execute()
        self.assertTrue(result.success, result.messages)
        reports = result.operator_credit_summary
        self.assertEqual(len(reports), 2)
        self.assertTrue(all(a["credit_assignment"] == "paired" for a in reports))
        self.assertGreater(sum(a["paired_physical_baselines"] for a in reports), 0)
        self.assertGreater(sum(a["observations"] for a in reports), 0)
        self.assertLessEqual(sum(a["observations"] for a in reports), actual["count"])
        self.assertGreater(actual["count"], 12)
        return result, actual

    def test_paired_objective_through_full_ga(self):
        self._optimize("objective")

    def test_paired_feasibility_through_full_ga(self):
        self._optimize("feasibility")

    def test_paired_control_consumes_fixed_budget(self):
        _, actual = self._optimize("objective", limit=45)
        self.assertEqual(actual["count"], 45)
        self.assertGreaterEqual(actual["requested"], actual["count"])

    def test_reject_confounded_or_unaccounted_paired_modes(self):
        cases = [
            dict(mutation_credit_assignment="paired", mutation_operator_policy="legacy",
                 mutation_evaluation_counter=lambda: 0,
                 ensure_unique_individuals=False, number_of_mutation_decision_variables=1,
                 candidate_solution_mutation="random"),
            dict(mutation_credit_assignment="paired", mutation_operator_policy="ucb",
                 mutation_evaluation_counter=None,
                 ensure_unique_individuals=False, number_of_mutation_decision_variables=1,
                 candidate_solution_mutation="random"),
            dict(mutation_credit_assignment="paired", mutation_operator_policy="ucb",
                 mutation_evaluation_counter=lambda: 0,
                 ensure_unique_individuals=True, number_of_mutation_decision_variables=1,
                 candidate_solution_mutation="random"),
            dict(mutation_credit_assignment="paired", mutation_operator_policy="ucb",
                 mutation_evaluation_counter=lambda: 0,
                 ensure_unique_individuals=False, number_of_mutation_decision_variables=2,
                 candidate_solution_mutation="random"),
        ]
        for opts in cases:
            with self.subTest(opts=opts), self.assertRaises(ValueError):
                GA(cost_function=lambda x: float(sum(x)), **opts)


if __name__ == "__main__":
    unittest.main()
