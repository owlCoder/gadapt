"""Iteration 17 guards: candidate source schema and REAL solver call accounting.

Unit tests use synthetic recorder stubs only: ZERO physical AC PF attempts.
"""
import copy
import unittest

import numpy as np

from research.iteration17_ieee14_gadapt_economic_pf import (
    IEEE14EconomicPFFeasibleSubset,PhysicalBudgetRecorder,
    original_economic_cost,measured_feasibility,FAILED_SCORE,TOLS,
)


class SyntheticPhysicalGrid:
    def __init__(self):
        self.evaluations=0
    def evaluate(self,vector):
        self.evaluations+=1
        if self.evaluations==1:
            return {"converged":False,"feasible":False,
                    "penalized_objective":FAILED_SCORE,
                    "actual_economic_cost":None,"solver_error":"failing real solver"}
        return {"converged":True,"feasible":True,
                "penalized_objective":20.+self.evaluations,
                "actual_economic_cost":20.+self.evaluations,
                "solver_error":""}


class GenuineIEEE14PilotTests(unittest.TestCase):
    def test_original_controllable_source_P_and_V_identity(self):
        p=IEEE14EconomicPFFeasibleSubset()
        self.assertEqual(p.n,9)
        self.assertEqual(p.non_slack_gen_ids,[1,2,3,4])
        self.assertEqual(p.slack_gen_ids,[0])
        self.assertEqual(p.all_gen_ids,[0,1,2,3,4])
        self.assertEqual(len(p.s["bus"]),14)
        self.assertEqual(len(p.s["branch"]),20)
        self.assertTrue(all(a<b for a,b in p.bounds))
        self.assertEqual(TOLS["generator_q_mvar"],1e-3)
        self.assertEqual(TOLS["ac_nodal_balance_mva"],1e-3)

    def test_real_source_cost_includes_slack_and_ignores_offline(self):
        source=IEEE14EconomicPFFeasibleSubset().source
        arr=source["gen"][:,1].copy()
        cost=original_economic_cost(arr,source["gen"][:,7]>0,
                 source["gencost"])
        self.assertGreater(cost,0)
        modified=arr.copy()
        modified[0]+=10
        result=original_economic_cost(modified,source["gen"][:,7]>0,
                     source["gencost"])
        self.assertNotEqual(cost,result)

    def test_exact_budget_never_calls_fake_ac(self):
        grid=SyntheticPhysicalGrid()
        a=PhysicalBudgetRecorder(grid,budget=2)
        self.assertEqual(a([.5]),FAILED_SCORE)
        self.assertEqual(a([.5]),22.)
        for _ in range(30):
            self.assertEqual(a([.5]),FAILED_SCORE)
        self.assertEqual(grid.evaluations,2)
        self.assertEqual(a.calls,2)
        self.assertEqual(a.post_budget_requests,30)
        self.assertEqual(a.feasible_candidates,1)
        self.assertEqual(a.first_feasible_call,2)
        self.assertEqual(a.ac_errors,1)
        self.assertEqual(a.summary()["best_feasible_economic_cost"],22.)

    def test_failed_solvers_never_become_feasible(self):
        a=PhysicalBudgetRecorder(SyntheticPhysicalGrid(),budget=1)
        a([.1])
        info=a.summary()
        self.assertIsNone(info["best_feasible_economic_cost"])
        self.assertEqual(info["solver_failed_calls"],1)
        self.assertIsNone(info["first_feasible_actual_ac_call"])

    def test_validator_rejects_synthetic_or_incomplete_ac_result(self):
        s=IEEE14EconomicPFFeasibleSubset().source
        with self.assertRaises((ValueError,KeyError,IndexError)):
            measured_feasibility(
               {"bus":s["bus"].copy(),"gen":s["gen"].copy(),
                "branch":s["branch"].copy()},s)

    def test_nonfinite_score_from_fake_grid_is_rejected(self):
        class Broken:
            def evaluate(self,_):
                return {"converged":True,"feasible":True,
                        "penalized_objective":float("nan"),
                        "actual_economic_cost":10}
        a=PhysicalBudgetRecorder(Broken(),budget=1)
        with self.assertRaises(ValueError):
            a([.1])

if __name__=="__main__":
    unittest.main()
