"""Regression tests for experimental mutation credit in the real GA."""
import random
import unittest

from gadapt.ga import GA
from gadapt.operations.mutation.decision_variable_mutation.credit_based_decision_variable_mutator import (
    CreditBasedDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (
    RandomDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_decision_variable_mutator import (
    NormalDistributionDecisionVariableMutator,
)


class CreditTests(unittest.TestCase):
    def test_reject_invalid_configuration(self):
        with self.assertRaises(ValueError):
            GA(cost_function=lambda x: float(sum(x)), mutation_operator_policy="bad")
        with self.assertRaises(ValueError):
            GA(cost_function=lambda x: float(sum(x)),
               mutation_operator_policy="ucb", mutation_operator_credit="feasibility")
        with self.assertRaises(ValueError):
            CreditBasedDecisionVariableMutator(policy="ucb", credit="feasibility")

    def _run(self, policy="ucb", credit="objective", callback=None):
        random.seed(20261021)
        calls = {"fitness": 0, "feedback": 0}
        def objective(x):
            calls["fitness"] += 1
            return float(sum((float(v)-0.25)**2 for v in x))
        def violation(x, score):
            calls["feedback"] += 1
            return 0.0 if sum(x) >= 0 else abs(float(sum(x)))
        ga = GA(
            cost_function=objective,
            mutation_operator_policy=policy,
            mutation_operator_credit=credit,
            mutation_violation_function=callback if callback is not None else violation,
            population_size=12,
            ensure_unique_individuals=False,
            exit_check="generations",
            number_of_generations=6,
            timeout=30,
        )
        for _ in range(4):
            ga.add(-2.0, 2.0)
        out = ga.execute()
        self.assertTrue(out.success, out.messages)
        self.assertGreater(calls["fitness"], 12)
        self.assertTrue(out.operator_credit_summary)
        self.assertEqual(sum(a["observations"] for a in out.operator_credit_summary),
                         sum(a["rewarded"] + (a["observations"]-a["rewarded"])
                             for a in out.operator_credit_summary))
        self.assertGreater(sum(a["selections"] for a in out.operator_credit_summary), 0)
        return out, calls

    def test_uniform_credit_is_opt_in(self):
        out, _ = self._run(policy="uniform")
        self.assertEqual(len(out.operator_credit_summary), 2)

    def test_ucb_objective_credit(self):
        out, _ = self._run(policy="ucb")
        self.assertTrue(all(a["selections"] > 0 for a in out.operator_credit_summary))

    def test_feasibility_callback_on_evaluated_mutants(self):
        _, calls = self._run(policy="ucb", credit="feasibility")
        self.assertGreater(calls["feedback"], 0)
        self.assertLessEqual(calls["feedback"], calls["fitness"])

    def test_missing_physical_sample_cannot_receive_credit(self):
        """None marks a withheld evaluation, NOT a feasible observation."""
        random.seed(10)
        controller = CreditBasedDecisionVariableMutator(
            policy="ucb", credit="feasibility",
            violation_function=lambda x, cost: None)
        controller.append(RandomDecisionVariableMutator())
        var = type("Var", (), {
            "min_value": 0.0, "max_value": 1.0,
            "step": None, "decimal_places": -1,
            "make_random_value": lambda _: 0.3,
        })()
        entry = type("Entry", (), {})()
        entry.value = 0.2
        entry.decision_variable = var
        candidate = [entry]
        controller.begin_generation([type("Incumbent", (), {"cost_value": 2.0})()])
        controller.mutate(entry)
        evaluated = type("Evaluated", (list,), {"_succ": True, "cost_value": 1.0})
        controller.observe(evaluated(candidate))
        stats = controller.summary()
        self.assertEqual(sum(x["observations"] for x in stats), 0)
        self.assertEqual(sum(x["selections"] for x in stats), 1)

    def test_old_default_is_unchanged(self):
        ga = GA(cost_function=lambda v: float(sum(x*x for x in v)),
                population_size=10, number_of_generations=3,
                exit_check="generations", ensure_unique_individuals=False)
        ga.add(0.0, 1.0)
        ga.add(0.0, 1.0)
        out = ga.execute()
        self.assertTrue(out.success, out.messages)
        self.assertFalse(hasattr(out, "operator_credit_summary"))

    def test_no_trace_or_reward_leaks_across_generations(self):
        controller = CreditBasedDecisionVariableMutator(policy="ucb")
        controller.append(RandomDecisionVariableMutator())
        controller.append(NormalDistributionDecisionVariableMutator())
        class Value:
            def __init__(self):
                self.value = 0.2
                self.decision_variable = type("Var", (), {
                    "min_value": 0.0, "max_value": 1.0,
                    "step": None, "decimal_places": -1,
                    "make_random_value": lambda _: 0.3,
                })()
        class Candidate(list):
            cost_value = 1.0
            _succ = True
        c = Candidate([Value()])
        controller.begin_generation([type("P", (), {"cost_value": 2.0})()])
        controller.mutate(c[0])
        controller.begin_generation([type("P", (), {"cost_value": 2.0})()])
        controller.observe(c)
        self.assertEqual(sum(a["observations"] for a in controller.summary()), 0)


if __name__ == "__main__":
    unittest.main()
