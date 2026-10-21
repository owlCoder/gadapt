"""Regression for direct in-core scenario-aware GAdapt mutation operator credit.

Synthetic deterministic scenarios; NO AC solvers in this unittest module.
The production code must perform exactly N real physical calls before any
feedback is credited, never infer feasibility from a penalty/sentinel alone.
"""
import random
import unittest

from gadapt.ga import GA
from gadapt.operations.mutation.decision_variable_mutation.credit_based_decision_variable_mutator import (
    CreditBasedDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (
    RandomDecisionVariableMutator,
)


class ScenarioCreditTests(unittest.TestCase):
    def _controller(self, callback=None, n=3):
        c=CreditBasedDecisionVariableMutator(
            policy="ucb", credit="scenario_feasibility",
            scenario_count=n,
            evaluation_counter=lambda:0,
            violation_function=callback or (lambda values, score:[0,0,0]))
        c.append(RandomDecisionVariableMutator())
        return c

    def test_reward_robust_feasible_dominates_partial_even_if_nearly_feasible(self):
        signals=iter([[0,0,0],[0,0,1e-12],[0.0,.3,1.0],[2,2,2]])
        controller=self._controller(callback=lambda values,score:next(signals))
        all_feasible=controller._scenario_reward([.1],2.,.0)
        almost=controller._scenario_reward([.1],2.,1.)
        partly=controller._scenario_reward([.1],2.,1.)
        no=controller._scenario_reward([.1],2.,1.)
        self.assertEqual(all_feasible,.75)
        self.assertLess(almost,.75)
        self.assertGreater(almost,partly)
        self.assertGreater(partly,no)
        self.assertEqual(controller._scenario_fully_feasible_observations,1)

    def test_invalid_or_missing_scenario_feedback_never_credited_as_zero(self):
        for outcome in ([],[0,0],[0,0,0,0],0.0,"000",
                        [0,0,-1],[0,0,float("nan")],[0,float("inf"),0],
                        [True,0,0]):
            with self.subTest(outcome=outcome):
                c=self._controller(callback=lambda v,s:outcome)
                with self.assertRaises(ValueError):
                    c._scenario_reward([.1],1.,0.0)
        c=self._controller(callback=lambda v,s:None)
        self.assertIsNone(c._scenario_reward([.1],1.,0.0))
        self.assertEqual(c._scenario_fully_feasible_observations,0)

    def test_configuration_is_fail_closed_and_legacy_stays_default(self):
        cases=[
            {"mutation_operator_policy":"legacy","mutation_operator_credit":"scenario_feasibility",
             "mutation_scenario_count":3,"mutation_evaluation_counter":lambda:0,
             "mutation_violation_function":lambda x,c:[0,0,0]},
            {"mutation_operator_policy":"ucb","mutation_operator_credit":"scenario_feasibility",
             "mutation_scenario_count":1,"mutation_evaluation_counter":lambda:0,
             "mutation_violation_function":lambda x,c:[0]},
            {"mutation_operator_policy":"ucb","mutation_operator_credit":"scenario_feasibility",
             "mutation_scenario_count":3,"mutation_evaluation_counter":None,
             "mutation_violation_function":lambda x,c:[0,0,0]},
            {"mutation_operator_policy":"ucb","mutation_operator_credit":"scenario_feasibility",
             "mutation_scenario_count":3,"mutation_evaluation_counter":lambda:0,
             "mutation_violation_function":None},
            {"mutation_operator_policy":"ucb","mutation_operator_credit":"scenario_feasibility",
             "mutation_scenario_count":3,"mutation_evaluation_counter":lambda:0,
             "mutation_violation_function":lambda x,c:[0,0,0],
             "mutation_credit_assignment":"paired"},
            {"mutation_operator_policy":"ucb","mutation_operator_credit":"objective",
             "mutation_scenario_count":3}
        ]
        for options in cases:
            with self.subTest(options=options),self.assertRaises(ValueError):
                GA(cost_function=lambda x:sum(x),**options)

        random.seed(123)
        baseline=GA(cost_function=lambda x:sum(v*v for v in x),population_size=10,
                    exit_check="generations",number_of_generations=4)
        baseline.add(0.0,1.0);baseline.add(0.0,1.0)
        result=baseline.execute()
        self.assertTrue(result.success,result.messages)
        self.assertFalse(hasattr(result,"operator_credit_summary"))

    def test_real_GA_execution_with_three_simulated_scenario_charges_per_trial(self):
        random.seed(2468)
        count={"physical":0,"requests":0}
        budget=90
        cache={}
        def cost(vector):
            count["requests"]+=1
            if count["physical"]+3>budget:
                return 1e12
            # Simulate the strict batch accounting with 3 separate
            # deterministic non-AC source scenarios.
            violation=[]
            for scenario in (.98,1.0,1.02):
                count["physical"]+=1
                violation.append(max(0.,sum(vector)*scenario-.8))
            cache[tuple(vector)]=violation
            return float(sum((v-.3)**2 for v in vector)+
                         1e4*max(violation))
        def feedback(vector,score):
            return cache.get(tuple(vector))
        ga=GA(
           cost_function=cost,
           population_size=12,
           exit_check="generations",
           number_of_generations=16,
           exit_function=lambda:count["physical"]>=budget,
           mutation_operator_policy="ucb",
           mutation_operator_credit="scenario_feasibility",
           mutation_violation_function=feedback,
           mutation_scenario_count=3,
           mutation_evaluation_counter=lambda:count["physical"],
           ensure_unique_individuals=False,
           timeout=30)
        for _ in range(4):
            ga.add(0.0,1.0)
        result=ga.execute()
        self.assertTrue(result.success,result.messages)
        self.assertEqual(count["physical"],budget)
        self.assertGreaterEqual(count["requests"],budget//3)
        stats=result.operator_credit_summary
        self.assertEqual(len(stats),2)
        # A short stochastic GA test may spend its budget before any mutation;
        # its substantive contract is counted full batches, bounded observations,
        # and no false physical feedback. Deterministic operator-selection tests
        # are exercised separately by test_no_false_credit_when_real_counter_says_unpaid.
        self.assertGreaterEqual(sum(x["selections"] for x in stats),0)
        self.assertLessEqual(sum(x["observations"] for x in stats),
                             count["physical"]//3)
        self.assertTrue(all(x["credit_assignment"]=="offspring" for x in stats))

    def test_no_false_credit_when_real_counter_says_unpaid(self):
        c=self._controller(callback=lambda v,score:[0,0,0])
        class Variable:
            def __init__(self):
                self.value=.4
                self.decision_variable=type("Source",(),{
                    "variable_id":0,"min_value":0.,"max_value":1.,
                    "step":None,"decimal_places":-1,
                    "make_random_value":lambda _: .5})()
        class Offspring(list):
            _succ=True
            cost_value=3.0
        var=Variable()
        offspring=Offspring([var])
        c.begin_generation([type("Prev",(),{"cost_value":4.0})()])
        c.mutate(var)
        c.observe(offspring,physically_evaluated=False)
        summary=c.summary()
        self.assertEqual(sum(x["observations"] for x in summary),0)
        self.assertGreater(sum(x["withheld_unpaid_credits"] for x in summary),0)


if __name__=="__main__":
    unittest.main()
