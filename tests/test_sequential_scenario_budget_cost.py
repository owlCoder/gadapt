"""Fail-closed synthetic source-scenario unit tests. ZERO real AC PF calls."""
import math
import random
import unittest

from gadapt.ga import GA
from gadapt.operations.cost_finding.sequential_scenario_budget_cost import (
    SequentialScenarioBudgetCost, UNVERIFIED_SCORE,CENSORED_BASE_SCORE
)

SCENARIOS=(.98,1.0,1.02)


class MeteredSyntheticGrid:
    def __init__(self,fail_at=(),unknown_at=()):
        self.real_ac_calls=0
        self.fail_at=set(fail_at)
        self.unknown_at=set(unknown_at)
        self.trace=[]
    def evaluate(self,vector,scenario):
        self.real_ac_calls+=1
        self.trace.append(scenario)
        if scenario in self.unknown_at:
            return {"converged":False,"feasible":False,"error":"AC NR did not converge"}
        failed=scenario in self.fail_at
        return {
            "converged":True,"feasible":not failed,
            "normalized_violation":.5 if failed else 0.,
            "original_economic_cost":100.+scenario,
            "q_source_excess_mvar":50. if failed else 0.,
            "max_nodal_mismatch_mva":1e-11,
        }
    def meter(self,mode,cap=9):
        return SequentialScenarioBudgetCost(
           SCENARIOS,self.evaluate,lambda:self.real_ac_calls,cap,mode=mode)


class ScenarioBudgetTests(unittest.TestCase):
    def test_full_mode_keeps_three_actual_solves_even_when_first_violates(self):
        g=MeteredSyntheticGrid(fail_at={.98})
        x=g.meter("full",3)
        value=x([.5])
        self.assertAlmostEqual(value,101.+.5*1e5)
        self.assertEqual(g.trace,list(SCENARIOS))
        self.assertEqual(x.calls,3)
        self.assertEqual(x.summary()["completely_evaluated_candidates"],1)
        self.assertIsNone(x.summary()["best_verified_robust_mean_economic_cost_or_null"])
        self.assertEqual(x.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],0)

    def test_early_stop_after_one_real_measured_violation_never_claims_other_scenarios(self):
        g=MeteredSyntheticGrid(fail_at={.98})
        x=g.meter("stop_fixed",9)
        value=x([.2])
        self.assertGreaterEqual(value,CENSORED_BASE_SCORE)
        self.assertEqual(g.trace,[.98])
        d=x.summary()
        self.assertEqual(d["actual_native_AC_calls"],1)
        self.assertEqual(d["early_screened_physically_infeasible_candidates"],1)
        self.assertEqual(d["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],2)
        self.assertEqual(d["actual_AC_per_scenario"],[1,0,0])
        self.assertIsNone(d["best_verified_robust_mean_economic_cost_or_null"])
        self.assertIsNone(d["best_fully_measured_penalized_score_or_null"])

    def test_second_scenario_failure_is_two_actual_solves_and_one_unseen(self):
        g=MeteredSyntheticGrid(fail_at={1.0})
        x=g.meter("stop_fixed",9)
        x([.2])
        self.assertEqual(g.trace,[.98,1.0])
        self.assertEqual(x.summary()["candidates_stopped_after_2_real_AC"],1)
        self.assertEqual(x.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],1)

    def test_all_source_scenarios_must_be_real_for_verified_feasible(self):
        g=MeteredSyntheticGrid()
        x=g.meter("stop_fixed",6)
        cost=x([.7])
        self.assertAlmostEqual(cost,101.)
        d=x.summary()
        self.assertEqual(d["actual_native_AC_calls"],3)
        self.assertEqual(d["verified_all_scenario_feasible_candidates"],1)
        self.assertEqual(d["first_verified_robust_true_AC_number"],3)
        self.assertAlmostEqual(d["best_verified_robust_mean_economic_cost_or_null"],101.)
        self.assertEqual(d["best_verified_robust_vector_or_null"],[.7])
        self.assertEqual(d["best_verified_robust_source_physics_or_null"]["per_scenario_real_source_normalized_violation"],[0.,0.,0.])

    def test_empirical_adaptive_order_only_uses_actually_observed_failures(self):
        g=MeteredSyntheticGrid(fail_at={1.02})
        x=g.meter("stop_adaptive",12)
        # Initially tie: 98,100,102, discovers 102 physically violated.
        first=x([.3])
        self.assertEqual(g.trace,list(SCENARIOS))
        self.assertEqual(x.summary()["actual_AC_per_scenario"],[1,1,1])
        # Observed fail(102)=1/1 -> posterior (2/3), others (1/3).
        second=x([.4])
        self.assertEqual(g.trace,[.98,1.0,1.02,1.02])
        self.assertEqual(x.summary()["actual_AC_per_scenario"],[1,1,2])
        self.assertEqual(x.summary()["early_screened_physically_infeasible_candidates"],2)
        self.assertEqual(x.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],2)
        self.assertAlmostEqual(second,first)

    def test_strict_remaining_budget_reserves_three_and_never_spends_two(self):
        g=MeteredSyntheticGrid(fail_at={.98})
        x=g.meter("stop_fixed",3)
        x([.1])
        self.assertEqual(x.calls,1)
        for _ in range(7):
            self.assertEqual(x([.2]),UNVERIFIED_SCORE)
        d=x.summary()
        self.assertEqual(d["post_budget_requests_without_AC"],7)
        self.assertEqual(d["actual_native_AC_calls"],1)
        self.assertEqual(d["unused_due_to_reserving_complete_validation"],2)
        self.assertEqual(g.trace,[.98])

    def test_nr_nonconverged_is_numerically_unknown_not_proved_physically_infeasible(self):
        g=MeteredSyntheticGrid(unknown_at={.98})
        x=g.meter("stop_fixed",9)
        self.assertEqual(x([.1]),UNVERIFIED_SCORE)
        d=x.summary()
        self.assertEqual(d["numerically_unknown_candidates"],1)
        self.assertEqual(d["early_screened_physically_infeasible_candidates"],0)
        self.assertEqual(d["actual_AC_per_scenario"],[1,0,0])
        self.assertEqual(d["verified_all_scenario_feasible_candidates"],0)

    def test_full_mode_counts_three_even_when_first_nr_nonconvergent(self):
        g=MeteredSyntheticGrid(unknown_at={.98})
        x=g.meter("full",3)
        self.assertEqual(x([.3]),UNVERIFIED_SCORE)
        self.assertEqual(x.calls,3)
        self.assertEqual(g.trace,list(SCENARIOS))
        self.assertEqual(x.summary()["numerically_unknown_candidates"],1)

    def test_false_physical_callback_counter_and_data_fail_closed(self):
        n={"calls":0}
        def no_solver(v,s):
            return {"converged":True,"feasible":True,
                   "normalized_violation":0.,"original_economic_cost":100.}
        x=SequentialScenarioBudgetCost(SCENARIOS,no_solver,lambda:n["calls"],3)
        with self.assertRaises(RuntimeError):
            x([.3])
        def bad_score(v,s):
            n["calls"]+=1
            return {"converged":True,"feasible":True,
                   "normalized_violation":.25,"original_economic_cost":100.}
        y=SequentialScenarioBudgetCost(SCENARIOS,bad_score,lambda:n["calls"],3)
        with self.assertRaises(ValueError):
            y([.3])

    def test_default_GA_accepts_new_optional_real_cost_without_new_GA_options(self):
        random.seed(410)
        class VariableMeter:
            def __init__(self):
                self.count=0
            def evaluate(self,vector,scenario):
                self.count+=1
                viol=max(0.,vector[0]-.8)
                return {"converged":True,"feasible":viol==0.,
                        "normalized_violation":viol,
                        "original_economic_cost":100.+scenario,
                        "max_nodal_mismatch_mva":0.}
        phy=VariableMeter()
        tracker=SequentialScenarioBudgetCost(
            SCENARIOS,phy.evaluate,lambda:phy.count,
            budget=90,mode="stop_fixed")
        ga=GA(cost_function=tracker,population_size=12,
              exit_check="generations",number_of_generations=30,
              exit_function=lambda:tracker.remaining<3,
              timeout=30)
        ga.add(0.,1.)
        outcome=ga.execute()
        self.assertTrue(outcome.success,outcome.messages)
        self.assertLessEqual(tracker.calls,90)
        self.assertGreater(tracker.requests,0)
        self.assertEqual(tracker.calls,sum(tracker.actual_scenario_attempts))
        self.assertGreater(tracker.summary()["verified_all_scenario_feasible_candidates"],0)

if __name__=="__main__":
    unittest.main()
