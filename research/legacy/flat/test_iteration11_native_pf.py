"""Iteration 11 direct-original source and AC physical residual tests (NO PF runs)."""
import unittest

import numpy as np

from research.iteration11_original_matpower_native_pf import (
    load_original, summed_limit_violation, original_rate_a_violation,
    inspect_successful_pf,
)


class NativeOriginalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=load_original()

    def test_complete_2019_case_and_slack(self):
        x=self.source
        self.assertEqual(x["bus"].shape,(1888,13))
        self.assertEqual(x["gen"].shape,(298,21))
        self.assertEqual(x["branch"].shape,(2531,13))
        self.assertEqual(int(x["bus"][x["bus"][:,1]==3,0][0]),1320)
        self.assertEqual(int(x["gen"][-1,0]),1320)
        self.assertEqual(float(x["gen"][-1,3]),1.0)
        self.assertEqual(int(np.sum(x["gen"][:,7]>0)),291)
        self.assertEqual(int(np.sum(x["branch"][:,5]==0)),455)

    def test_inactive_limits_must_not_count(self):
        bounds=summed_limit_violation([2.,30.,-7.],
                     [0.,-10.,0.],[10.,20.,10.],[True,False,True])
        self.assertEqual(bounds["above_limit_count"],0)
        self.assertEqual(bounds["below_limit_count"],1)
        self.assertEqual(bounds["below_limit_total"],7.)

    def test_rate_a_zero_is_unbounded_and_both_terminals_checked(self):
        b=np.zeros((3,17))
        b[:,10]=[1,1,0]
        b[:,5]=[0,100,100]
        b[0,13:17]=[1000,1000,0,0]
        b[1,13:17]=[10.,0,120.,0]  # only TO end violates 100 MVA
        b[2,13:17]=[1100.,0,2000,0]  # offline
        result=original_rate_a_violation(b)
        self.assertEqual(result["rated_active_branches"],1)
        self.assertEqual(result["unrated_active_branches"],1)
        self.assertEqual(result["overloaded_branches"],1)
        self.assertAlmostEqual(result["sum_relative_rating_excess"],.2)

    def test_partial_ac_result_rejected(self):
        with self.assertRaises(ValueError):
            original_rate_a_violation(np.ones((2531,13)))

    def test_active_Q_enforcement_is_not_P_constraints(self):
        q=summed_limit_violation([10.,0.],[-1.,-1.],[1.,1.],[True,False])
        self.assertEqual(q["above_limit_total"],9.)
        p=summed_limit_violation([5.,6.],[4.,2.],[7.,10.],[True,True])
        self.assertEqual(p["above_limit_total"],0.)
        self.assertEqual(p["below_limit_total"],0.)

    def test_completed_pf_rejects_underspecified_arrays(self):
        with self.assertRaises(ValueError):
            inspect_successful_pf({"bus":np.zeros((5,13)),
                 "gen":np.zeros((298,21)),"branch":np.zeros((2531,17))},
                 self.source)


if __name__=="__main__":
    unittest.main()
