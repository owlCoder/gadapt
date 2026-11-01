"""I36 zero-native-AC synthetic regression for independently preregistered IEEE14 transfer."""
import unittest
import numpy as np
from pypower.idx_bus import BUS_I,PD,QD
from pypower.idx_gen import PG
from research.iteration36_censor_credit_ieee14 import (
    METHODS, SEEDS, BUDGET, POPULATION, MAX_REAL_AC,
    IEEE14ActualNativeACBoundary, IEEE14SourceACObserved, paired,
)
from research.iteration32_ieee14_topology_transfer import SCENARIOS

class NoRealACBoundary:
    def __init__(self,fail=None,unknown=None):
        self.real_routing_calls=0
        self.fail=fail
        self.unknown=unknown
    def evaluate_scenario(self,x,s):
        self.real_routing_calls+=1
        if s==self.unknown:return dict(converged=False,feasible=False,error="unit synthetic nonconvergence")
        v=.1 if s==self.fail else 0.
        return dict(converged=True,feasible=not bool(v),
                    normalized_violation=v,original_economic_cost=8500.,
                    max_nodal_mismatch_mva=0.)

class IEEE14I36NoSolver(unittest.TestCase):
    def test_frozen_params(self):
        self.assertEqual(METHODS,("legacy_fixed","ucb_objective_fixed",
                         "uniform_censor_safe_fixed","ucb_censor_safe_fixed"))
        self.assertEqual(SEEDS,tuple(range(2500,2512)))
        self.assertEqual(BUDGET,180)
        self.assertEqual(POPULATION,12)
        self.assertEqual(MAX_REAL_AC,8640)
        self.assertEqual(SCENARIOS,("nominal","odd_bus_plus1pct","even_bus_plus1pct"))

    def test_source_9D_and_original_branch_demand_only_variation_without_ac(self):
        src=IEEE14ActualNativeACBoundary()
        g=src.grid
        self.assertEqual(src.n,9)
        self.assertEqual(g.real_ac_calls,0)
        x=[(a+b)/2 for a,b in src.bounds]
        nominal=g.source_case_without_ac(x,"nominal")
        odd=g.source_case_without_ac(x,"odd_bus_plus1pct")
        even=g.source_case_without_ac(x,"even_bus_plus1pct")
        self.assertEqual(g.real_ac_calls,0)
        self.assertEqual(len(nominal["bus"]),14)
        self.assertEqual(len(nominal["gen"]),5)
        parity=nominal["bus"][:,BUS_I].astype(int)%2==1
        np.testing.assert_allclose(nominal["bus"][:,PD],g.original["bus"][:,PD])
        np.testing.assert_allclose(odd["bus"][:,PD],
            g.original["bus"][:,PD]*np.where(parity,1.01,.99))
        np.testing.assert_allclose(even["bus"][:,QD],
            g.original["bus"][:,QD]*np.where(parity,.99,1.01))
        np.testing.assert_array_equal(odd["branch"],g.original["branch"])
        np.testing.assert_array_equal(odd["gencost"],g.original["gencost"])

    def test_proven_first_source_failure_never_equated_to_three_feasible(self):
        src=NoRealACBoundary(fail="nominal")
        ev=IEEE14SourceACObserved(src)
        score=ev([1]*9)
        self.assertGreater(score,1e9)
        self.assertEqual(src.real_routing_calls,1)
        obs=ev.censor_safe_cached_feedback([1]*9,score)
        self.assertEqual(obs["actual_calls"],1)
        self.assertEqual(obs["status"],"measured_infeasible")
        self.assertEqual(obs["observed_scenarios"],["nominal"])
        self.assertEqual(obs["observed_violations"],[.1])
        self.assertEqual(ev.summary()["verified_all_scenario_feasible_candidates"],0)
        self.assertEqual(ev.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],2)

    def test_three_source_scenarios_needed_for_credit_and_verified_cost(self):
        src=NoRealACBoundary()
        ev=IEEE14SourceACObserved(src)
        score=ev([1]*9)
        self.assertEqual(score,8500.)
        self.assertEqual(src.real_routing_calls,3)
        self.assertEqual(ev.summary()["verified_all_scenario_feasible_candidates"],1)
        self.assertEqual(ev.censor_safe_cached_feedback([1]*9,score)["actual_calls"],3)
        self.assertIsNone(ev.censor_safe_cached_feedback([2]*9,score))

    def test_numerical_unknown_never_fabricates_feasibility(self):
        src=NoRealACBoundary(unknown="nominal")
        ev=IEEE14SourceACObserved(src)
        score=ev([1]*9)
        self.assertEqual(ev.calls,1)
        self.assertIsNone(ev.censor_safe_cached_feedback([1]*9,score))
        self.assertEqual(ev.summary()["numerically_unknown_candidates"],1)
        self.assertEqual(ev.summary()["early_screened_physically_infeasible_candidates"],0)

    def test_paired_exact_binomial_n12(self):
        rows=[]
        for seed in SEEDS:
            rows.extend([
                dict(seed=seed,method="new",verified_all_scenario_feasible_candidates=1),
                dict(seed=seed,method="old",
                     verified_all_scenario_feasible_candidates=int(seed not in SEEDS[:4])),
            ])
        q=paired(rows,"new","old")
        self.assertEqual(q["first_only"],4)
        self.assertAlmostEqual(q["exact_two_sided_p_unadjusted"],.125)

if __name__=="__main__":unittest.main()
