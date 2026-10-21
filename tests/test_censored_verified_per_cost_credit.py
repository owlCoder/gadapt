"""I34 synthetic core-GAdapt counter/credit tests: zero GÉANT routing, zero AC.

These tests prove safe accounting, NOT optimizer effectiveness or originality.
"""
import unittest
import random
from gadapt.ga import GA
from gadapt.operations.mutation.decision_variable_mutation.credit_based_decision_variable_mutator import (
    CreditBasedDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (
    RandomDecisionVariableMutator,
)


class I34CensoredVerifiedPerCost(unittest.TestCase):
    def _controller(self, feedback, n=3):
        c=CreditBasedDecisionVariableMutator(
            policy="ucb",credit="censored_verified_per_cost",
            evaluation_counter=lambda:0,
            scenario_count=n,violation_function=lambda x,s:feedback)
        c.append(RandomDecisionVariableMutator())
        return c

    def test_strict_reward_only_true_complete_verified_and_cost_normalized(self):
        good=dict(status="verified_feasible",actual_calls=3,
                  observed_scenarios=["nominal","odd","even"],observed_violations=[0.,0.,0.])
        c=self._controller(good)
        self.assertAlmostEqual(c._censored_verified_reward([1],1e9,3),1/3)
        self.assertEqual(c._censor_safe_verified_feedback,1)
        # A fast reject is observed for learning, but NOT rewarded as cheap success.
        bad=dict(status="measured_infeasible",actual_calls=1,
                 observed_scenarios=["nominal"],observed_violations=[.5])
        c=self._controller(bad)
        self.assertEqual(c._censored_verified_reward([1],1e9,1),0.)
        self.assertEqual(c._censor_safe_measured_failures,1)
        self.assertEqual(c._censor_safe_verified_feedback,0)

    def test_missing_unknown_never_credits(self):
        c=self._controller(None)
        self.assertIsNone(c._censored_verified_reward([1],1e12,1))
        c=self._controller({"status":"numerically_unknown","actual_calls":2,
                            "observed_scenarios":["nominal","even"],
                            "observed_violations":[0.,0.]})
        self.assertIsNone(c._censored_verified_reward([1],1e12,2))
        self.assertEqual(c._censor_safe_withheld_unknown,1)

    def test_stale_mismatched_duplicate_and_fabricated_feedback_rejected(self):
        valid={"status":"verified_feasible","actual_calls":3,
               "observed_scenarios":["a","b","c"],"observed_violations":[0.,0.,0.]}
        invalid=[
            {**valid,"actual_calls":2},
            {**valid,"observed_scenarios":["a","a","c"]},
            {**valid,"observed_violations":[0.,0.,1e-12]},
            {**valid,"observed_violations":[0.,0.,float("nan")]},
            {**valid,"observed_violations":[0.,False,0.]},
            {**valid,"status":"measured_infeasible"},
            {**valid,"status":"unknown_bad_status"},
            {**valid,"unexpected":"surplus"},
            {**valid,"observed_scenarios":["a","b"]},
            {**valid,"observed_violations":[0.,0.]},
            {**valid,"actual_calls":True},
            {**valid,"observed_scenarios":[1,"b","c"]},
        ]
        for feedback in invalid:
            with self.subTest(feedback=feedback):
                with self.assertRaises(ValueError):
                    self._controller(feedback)._censored_verified_reward([1],1e9,3)
        for num in (0,4,True):
            with self.subTest(measured_calls=num),self.assertRaises(ValueError):
                self._controller(valid)._censored_verified_reward([1],1e9,num)

    def test_ga_configuration_opt_in_and_fail_closed(self):
        invalid=[
            {},
            {"mutation_operator_policy":"legacy"},
            {"mutation_scenario_count":1},
            {"mutation_scenario_count":None},
            {"mutation_evaluation_counter":None},
            {"mutation_violation_function":None},
            {"mutation_credit_assignment":"paired"},
        ]
        setup=dict(mutation_operator_policy="ucb",
                   mutation_operator_credit="censored_verified_per_cost",
                   mutation_scenario_count=3,
                   mutation_evaluation_counter=lambda:0,
                   mutation_violation_function=lambda x,s:None,
                   mutation_credit_assignment="offspring")
        for change in invalid:
            kw=setup.copy()
            if not change:kw.pop("mutation_violation_function")
            else:kw.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):
                GA(cost_function=lambda x:sum(x),**kw)
        g=GA(cost_function=lambda x:sum(x),**setup)
        self.assertEqual(g.mutation_operator_credit,"censored_verified_per_cost")
        # GA default still exact legacy options.
        plain=GA(cost_function=lambda x:sum(x))
        self.assertEqual(plain.mutation_operator_policy,"legacy")
        self.assertEqual(plain.mutation_operator_credit,"objective")

    def test_actual_gadapt_partial_one_two_three_real_charges_and_withholding(self):
        random.seed(2344)
        calls={"physical":0,"requests":0}
        budget=90
        cache={"last":None}
        traces=[]
        profiles=("nominal","odd","even")
        def physical_cost(x):
            calls["requests"]+=1
            budget_before=calls["physical"]
            cache["last"]=None
            if budget_before+3>budget:return 1e12
            observations=[]
            scenario_names=[]
            for i,s in enumerate(profiles):
                calls["physical"]+=1
                scenario_names.append(s)
                violation=(float(max(0.,sum(x)-2.)) if i == 0 else 0.)
                observations.append(violation)
                if violation>0:break
            # Stored as exactly the last paid trial, not historic genome cache.
            cache["last"]=(tuple(x),calls["physical"],{
                "status":"measured_infeasible" if any(v>0 for v in observations) else "verified_feasible",
                "actual_calls":len(observations),
                "observed_scenarios":scenario_names,
                "observed_violations":observations})
            traces.append(len(observations))
            return (1e9+1e5*observations[-1] if observations[-1]>0 else
                    sum((v-.5)**2 for v in x))
        def observed(x,score):
            r=cache["last"]
            if r is None or tuple(x)!=r[0] or calls["physical"]!=r[1]:return None
            return r[2]
        ga=GA(cost_function=physical_cost,population_size=12,
              exit_check="generations",number_of_generations=15,
              exit_function=lambda:calls["physical"]>=budget-2,
              mutation_operator_policy="ucb",mutation_operator_credit="censored_verified_per_cost",
              mutation_violation_function=observed,mutation_scenario_count=3,
              mutation_evaluation_counter=lambda:calls["physical"],
              ensure_unique_individuals=False,timeout=30)
        for _ in range(4):ga.add(0.,1.)
        result=ga.execute()
        self.assertTrue(result.success,result.messages)
        self.assertLessEqual(calls["physical"],budget)
        self.assertEqual(sum(traces),calls["physical"])
        self.assertTrue(all(1<=v<=3 for v in traces))
        summary=result.operator_credit_summary
        self.assertEqual(len(summary),2)
        self.assertLessEqual(sum(o["observations"] for o in summary),len(traces)*4)
        self.assertEqual(sum(o["censor_safe_withheld_unknown"] for o in summary)%2,0)
        # This is synthetic accounting only: NOT GÉANT, NOT AC.
        self.assertTrue(any(v==3 for v in traces))


if __name__=="__main__":
    unittest.main()
