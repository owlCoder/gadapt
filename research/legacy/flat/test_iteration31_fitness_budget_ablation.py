"""I31 synthetic no-AC tests for scorer/budget identifiability and safety."""
import math
import unittest

from gadapt.operations.cost_finding.sequential_scenario_budget_cost import (
    SequentialScenarioBudgetCost, CENSORED_BASE_SCORE, UNVERIFIED_SCORE,
)
from research.iteration31_fitness_budget_ablation import (
    FullMeasuredCensoredReference, METHODS, SEEDS, BUDGET,
    POPULATION, EXPECTED_MAX_NATIVE_AC,
)
from research.iteration30_spatial_load_holdout import SPATIAL_SCENARIOS


class FakeSource:
    def __init__(self, fail=("nominal",), unknown=()):
        self.calls=0
        self.trace=[]
        self.fail=set(fail)
        self.unknown=set(unknown)

    def eval(self,x,scenario):
        self.calls+=1  # SYNTHETIC counter, NOT real AC
        self.trace.append(scenario)
        if scenario in self.unknown:
            return {"converged":False,"feasible":False,"error":"synthetic NR unknown"}
        failure=(scenario in self.fail and x[0]<0.5)
        return {"converged":True,
                "feasible":not failure,
                "normalized_violation":0.25 if failure else 0.0,
                "original_economic_cost":101.0,
                "max_nodal_mismatch_mva":0.}

    def evaluator(self, cls, mode=None, budget=9):
        args=dict(scenarios=SPATIAL_SCENARIOS,
                  scenario_evaluator=self.eval,
                  physical_counter=lambda:self.calls,
                  budget=budget,penalty=1e5)
        if cls is FullMeasuredCensoredReference:
            return cls(**args)
        return cls(**args,mode=mode)


class I31CensoredFitnessControlTests(unittest.TestCase):
    def test_preregistered_frozen_constants(self):
        self.assertEqual(METHODS,
            ("full_true","full_censored","stop_fixed","stop_adaptive"))
        self.assertEqual(SEEDS,tuple(range(2080,2092)))
        self.assertEqual(SPATIAL_SCENARIOS,
            ("nominal","odd_bus_heavier","even_bus_heavier"))
        self.assertEqual(BUDGET,180)
        self.assertEqual(POPULATION,12)
        self.assertEqual(EXPECTED_MAX_NATIVE_AC,8640)

    def test_same_failing_candidate_same_censored_score_but_more_paid_scenarios(self):
        full=FakeSource()
        ctrl=FakeSource()
        early=FakeSource()
        a=full.evaluator(SequentialScenarioBudgetCost,mode="full")
        b=ctrl.evaluator(FullMeasuredCensoredReference)
        c=early.evaluator(SequentialScenarioBudgetCost,mode="stop_fixed")
        x=[0.1]
        true=a(x)
        censored=b(x)
        stopped=c(x)
        self.assertAlmostEqual(true,101.+0.25*1e5)
        self.assertEqual(censored,stopped)
        self.assertEqual(censored,CENSORED_BASE_SCORE+0.25*1e5)
        self.assertEqual(full.trace,list(SPATIAL_SCENARIOS))
        self.assertEqual(ctrl.trace,list(SPATIAL_SCENARIOS))
        self.assertEqual(early.trace,["nominal"])
        self.assertEqual((a.calls,b.calls,c.calls),(3,3,1))
        q=b.summary()
        self.assertEqual(q["completely_evaluated_candidates"],1)
        self.assertEqual(q["fully_measured_physical_failures_returning_censored_fitness"],1)
        self.assertEqual(q["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],0)
        self.assertAlmostEqual(q["best_fully_measured_penalized_score_or_null"],true)
        self.assertIsNone(q["best_verified_robust_mean_economic_cost_or_null"])
        self.assertEqual(c.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],2)

    def test_feasible_full_score_is_unchanged_and_needs_three_real_observations(self):
        ctrl=FakeSource()
        a=ctrl.evaluator(FullMeasuredCensoredReference)
        x=[0.9]
        self.assertAlmostEqual(a(x),101.)
        q=a.summary()
        self.assertEqual(q["actual_native_AC_calls"],3)
        self.assertEqual(q["verified_all_scenario_feasible_candidates"],1)
        self.assertEqual(q["fully_measured_physical_failures_returning_censored_fitness"],0)
        self.assertAlmostEqual(q["best_verified_robust_mean_economic_cost_or_null"],101.)
        self.assertEqual(q["best_verified_robust_vector_or_null"],x)

    def test_first_failure_state_resets_at_each_candidate(self):
        ctrl=FakeSource()
        a=ctrl.evaluator(FullMeasuredCensoredReference,budget=9)
        self.assertEqual(a([0.1]),CENSORED_BASE_SCORE+25000.)
        self.assertAlmostEqual(a([0.8]),101.)
        self.assertEqual(a.calls,6)
        self.assertEqual(a.summary()["fully_measured_physical_failures_returning_censored_fitness"],1)
        self.assertEqual(a.summary()["verified_all_scenario_feasible_candidates"],1)

    def test_numerical_unknown_after_physical_failure_is_not_robust_feasible(self):
        ctrl=FakeSource(unknown=("even_bus_heavier",))
        a=ctrl.evaluator(FullMeasuredCensoredReference)
        self.assertEqual(a([0.1]),UNVERIFIED_SCORE)
        self.assertEqual(a.calls,3)
        self.assertEqual(a.summary()["verified_all_scenario_feasible_candidates"],0)
        self.assertEqual(a.summary()["fully_measured_physical_failures_returning_censored_fitness"],0)
        self.assertEqual(a.summary()["numerically_unknown_candidates"],1)

    def test_no_partial_native_budget_spend_for_full_censored(self):
        ctrl=FakeSource()
        a=ctrl.evaluator(FullMeasuredCensoredReference,budget=4)
        a([0.1])
        self.assertEqual(a([0.9]),UNVERIFIED_SCORE)
        self.assertEqual(a.calls,3)
        self.assertEqual(a.summary()["post_budget_requests_without_AC"],1)
        self.assertEqual(a.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],0)

    def test_counter_fails_closed_on_fake_unmetered_physics(self):
        n={"calls":0}
        def bogus(x,s):
            return {"converged":True,"feasible":True,
                    "normalized_violation":0.,"original_economic_cost":101.}
        a=FullMeasuredCensoredReference(
            SPATIAL_SCENARIOS,bogus,lambda:n["calls"],3)
        with self.assertRaises(RuntimeError):
            a([0.8])


if __name__=="__main__":
    unittest.main()
