"""I27 true-AC accounting regression; these tests make NO PYPOWER runpf calls."""
import unittest
import numpy as np

from research.iteration27_real_scenario_credit_benchmark import (
    IEEE118SixSourcePVThreeScenarios,ThreeScenarioPhysicalBudget,
    LOADS,CONTROL_BUS_GEN,METHODS,SEEDS,BUDGET,
    FAILED_SCORE,
)


class SyntheticThreeRealPhysicalScenarios:
    def __init__(self):
        self.real_ac_calls=0
        self.failed_on=None
    def evaluate_scenario(self,vector,factor):
        self.real_ac_calls+=1
        if factor==self.failed_on:
            return {"converged":False,"feasible":False,"error":"Numerical failure"}
        # All signals are sourced directly from synthetic real-solver call mock.
        valid = factor == 1.0 or float(vector[0]) >= .5
        return {
            "converged":True,"feasible":valid,"error":"",
            "original_economic_cost":100.+factor,
            "normalized_violation":0. if valid else .2,
            "q_source_excess_mvar":0. if valid else 20.,
            "p_source_excess_mw":0.,
            "bus_v_excess_pu":0.,
            "positive_rate_a_mva_excess":0.,
            "max_source_q_excess_mvar":0. if valid else 20.,
            "max_nodal_mismatch_mva":1e-12,
        }


class OriginalIEEE118RobustScenarioTests(unittest.TestCase):
    def test_common_original_source_six_PV_controls_and_calibration_box(self):
        grid=IEEE118SixSourcePVThreeScenarios()
        self.assertEqual([b for b,_ in CONTROL_BUS_GEN],[103,32,34,92,19,74])
        self.assertEqual([i for _,i in CONTROL_BUS_GEN],[45,14,15,42,8,33])
        self.assertEqual(grid.n,6)
        self.assertEqual(grid.center.shape,(6,))
        self.assertAlmostEqual(grid.center[-1],.958)
        self.assertAlmostEqual(grid.bounds[-1][0],.948)
        self.assertAlmostEqual(grid.bounds[-1][1],.968)
        self.assertEqual(grid.real_ac_calls,0)
        self.assertEqual(len(grid.source["bus"]),118)
        self.assertEqual(len(grid.source["gen"]),54)
        self.assertEqual(len(grid.source["branch"]),186)

    def test_three_paid_simulations_per_candidate_with_no_sentinel_credit(self):
        dummy=SyntheticThreeRealPhysicalScenarios()
        monitor=ThreeScenarioPhysicalBudget(dummy,budget=6)
        first=[.3]+[.1]*5
        score=monitor(first)
        self.assertGreater(score,100.)
        self.assertEqual(monitor.calls,3)
        self.assertEqual(monitor.complete_batches,1)
        self.assertEqual(monitor.per_scenario_source_feasible,[0,1,0])
        self.assertEqual(monitor.cached_scenario_violation(first,score),(.2,0.,.2))
        self.assertEqual(monitor.cached_scalar_worst_violation(first,score),.2)
        robust=[.7]+[.1]*5
        score2=monitor(robust)
        self.assertEqual(monitor.calls,6)
        self.assertEqual(monitor.robust_feasible_batches,1)
        self.assertEqual(monitor.first_robust_real_AC_call,6)
        self.assertEqual(monitor.best_robust_economic_cost,101.)
        self.assertEqual(monitor.cached_scenario_violation(robust,score2),(0.,0.,0.))
        for _ in range(9):
            self.assertEqual(monitor(robust),FAILED_SCORE)
        self.assertIsNone(monitor.cached_scenario_violation(robust,FAILED_SCORE))
        self.assertEqual(dummy.real_ac_calls,6)
        self.assertEqual(monitor.requests,11)
        self.assertEqual(monitor.post_budget_requests,9)
        self.assertEqual(monitor.complete_batches,2)

    def test_partial_ac_batch_cap_never_simulates_partial_scenario(self):
        dummy=SyntheticThreeRealPhysicalScenarios()
        with self.assertRaises(ValueError):
            ThreeScenarioPhysicalBudget(dummy,budget=5)
        monitor=ThreeScenarioPhysicalBudget(dummy,budget=3)
        monitor([.7]+[.1]*5)
        self.assertEqual(dummy.real_ac_calls,3)
        monitor([.9]+[.1]*5)
        self.assertEqual(dummy.real_ac_calls,3)

    def test_failure_ac_is_charged_but_not_trusted_as_feasible(self):
        dummy=SyntheticThreeRealPhysicalScenarios()
        dummy.failed_on=1.02
        monitor=ThreeScenarioPhysicalBudget(dummy,budget=3)
        self.assertEqual(monitor([.7]+[.1]*5),FAILED_SCORE)
        self.assertEqual(dummy.real_ac_calls,3)
        self.assertEqual(monitor.numerically_failed_ac,1)
        self.assertIsNone(monitor.cached_scenario_violation([.7]+[.1]*5,FAILED_SCORE))
        self.assertEqual(monitor.robust_feasible_batches,0)
        self.assertIsNone(monitor.summary()["best_all_three_feasible_mean_original_economic_cost"])

    def test_preregistered_methods_seeds_and_physical_upper_bound(self):
        self.assertEqual(LOADS,(.98,1.0,1.02))
        self.assertEqual(len(METHODS),6)
        self.assertEqual(SEEDS,(2026,2027,2028))
        self.assertEqual(BUDGET,180)
        self.assertEqual(BUDGET*len(METHODS)*len(SEEDS),3240)
        self.assertEqual(BUDGET//len(LOADS),60)


if __name__=="__main__":
    unittest.main()
