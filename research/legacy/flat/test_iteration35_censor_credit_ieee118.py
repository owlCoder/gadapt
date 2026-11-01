"""I35 tests make ZERO physical PYPOWER AC calls: protocol and event integrity."""
import unittest
import numpy as np
from research.iteration35_censor_credit_ieee118 import (
    METHODS,SEEDS,BUDGET,POPULATION,MAX_REAL_AC,
    IEEE118TrueACCounter,IEEE118ObservedSourceAC,paired)
from research.iteration30_spatial_load_holdout import SPATIAL_SCENARIOS
from pypower.idx_bus import BUS_I,PD,QD
from pypower.idx_gen import PG

class SyntheticIEEE118EventBoundary:
    def __init__(self,unknown=None,first_fail=None):
        self.real_routing_calls=0
        self.unknown=unknown
        self.fail=first_fail
    def evaluate_scenario(self,vector,profile):
        self.real_routing_calls+=1
        if profile==self.unknown:
            return dict(converged=False,feasible=False,error="synthetic numerical failure")
        bad=(profile==self.fail)
        return dict(converged=True,feasible=not bad,
                    normalized_violation=.2 if bad else 0.,
                    original_economic_cost=129000.,
                    max_nodal_mismatch_mva=0.)

class I35NoAC(unittest.TestCase):
    def test_frozen_pre_registered_IEEE118_procedures(self):
        self.assertEqual(METHODS,("legacy_fixed","ucb_objective_fixed",
            "uniform_censor_safe_fixed","ucb_censor_safe_fixed"))
        self.assertEqual(SEEDS,tuple(range(2400,2412)))
        self.assertEqual(BUDGET,180)
        self.assertEqual(POPULATION,12)
        self.assertEqual(MAX_REAL_AC,8640)
        self.assertEqual(SPATIAL_SCENARIOS,
                         ("nominal","odd_bus_heavier","even_bus_heavier"))

    def test_source_original_case_invariance_before_real_ac(self):
        b=IEEE118TrueACCounter()
        g=b.grid
        self.assertEqual(g.real_ac_calls,0)
        x=[(lo+hi)/2 for lo,hi in b.bounds]
        nominal=g.new_source_case_no_ac(x,"nominal")
        odd=g.new_source_case_no_ac(x,"odd_bus_heavier")
        even=g.new_source_case_no_ac(x,"even_bus_heavier")
        self.assertEqual(g.real_ac_calls,0)
        self.assertEqual(len(g.source["bus"]),118)
        self.assertEqual(len(g.source["gen"]),54)
        ids=nominal["bus"][:,BUS_I].astype(int)
        oddids=ids%2==1
        np.testing.assert_allclose(nominal["bus"][:,PD],g.source["bus"][:,PD])
        np.testing.assert_allclose(odd["bus"][:,PD],
            g.source["bus"][:,PD]*np.where(oddids,1.02,.98))
        np.testing.assert_allclose(even["bus"][:,QD],
            g.source["bus"][:,QD]*np.where(oddids,.98,1.02))
        np.testing.assert_array_equal(odd["gen"][:,PG],g.source["gen"][:,PG])
        np.testing.assert_array_equal(odd["branch"],g.source["branch"])

    def test_first_fail_no_unobserved_source_imputation(self):
        b=SyntheticIEEE118EventBoundary(first_fail="nominal")
        ev=IEEE118ObservedSourceAC(b)
        score=ev([.5]*6)
        self.assertGreater(score,1e9)
        self.assertEqual(ev.calls,1)
        out=ev.censor_safe_cached_feedback([.5]*6,score)
        self.assertEqual(out["actual_calls"],1)
        self.assertEqual(out["observed_scenarios"],["nominal"])
        self.assertEqual(out["observed_violations"],[.2])
        self.assertEqual(ev.summary()["verified_all_scenario_feasible_candidates"],0)
        self.assertEqual(ev.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],2)

    def test_three_real_calls_needed_for_source_robustness(self):
        b=SyntheticIEEE118EventBoundary()
        ev=IEEE118ObservedSourceAC(b)
        score=ev([.5]*6)
        self.assertEqual(score,129000.)
        self.assertEqual(ev.calls,3)
        self.assertEqual(ev.summary()["verified_all_scenario_feasible_candidates"],1)
        self.assertEqual(ev.censor_safe_cached_feedback([.5]*6,score)["actual_calls"],3)
        self.assertIsNone(ev.censor_safe_cached_feedback([.6]*6,score))

    def test_unknown_versus_physical_false(self):
        b=SyntheticIEEE118EventBoundary(unknown="nominal")
        ev=IEEE118ObservedSourceAC(b)
        score=ev([.5]*6)
        self.assertEqual(ev.calls,1)
        self.assertIsNone(ev.censor_safe_cached_feedback([.5]*6,score))
        self.assertEqual(ev.summary()["numerically_unknown_candidates"],1)
        self.assertEqual(ev.summary()["early_screened_physically_infeasible_candidates"],0)

    def test_paired_preregistered_exact_p(self):
        rows=[]
        for s in SEEDS:
            rows.extend([{"seed":s,"method":"new","verified_all_scenario_feasible_candidates":1},
                {"seed":s,"method":"old",
                 "verified_all_scenario_feasible_candidates":int(s not in SEEDS[:4])}])
        d=paired(rows,"new","old")
        self.assertEqual(d["first_only"],4)
        self.assertAlmostEqual(d["exact_two_sided_p_unadjusted"],.125)

if __name__=="__main__":
    unittest.main()
