"""I34 zero-real-routing instrument contract and paired statistical controls."""
import unittest

from research.iteration34_censor_credit_geant import (
    ObservedSequentialCost, SEEDS, METHODS, BUDGET, POPULATION,
    MAX_REAL_ROUTINGS, paired,
)


class FakeGenuineBoundary:
    """Count a deliberately synthetic marker, NOT networkx Dijkstra or AC."""
    def __init__(self, fail="nominal", numerical=None):
        self.real_routing_calls=0
        self.fail=fail
        self.numerical=numerical

    def evaluate_scenario(self,x,scenario):
        self.real_routing_calls+=1
        if scenario==self.numerical:
            return dict(converged=False,feasible=False,error="fake numerical unknown")
        v=.1 if scenario==self.fail else 0.
        return dict(converged=True,feasible=v==0,
                    normalized_violation=v,original_economic_cost=140000.,
                    max_nodal_mismatch_mva=None)


class I34ZeroRealRouting(unittest.TestCase):
    def test_frozen_constraints(self):
        self.assertEqual(SEEDS,tuple(range(2300,2312)))
        self.assertEqual(len(METHODS),5)
        self.assertEqual(BUDGET,120)
        self.assertEqual(POPULATION,24)
        self.assertEqual(MAX_REAL_ROUTINGS,7200)

    def test_first_failure_proves_only_measured_scenario(self):
        route=FakeGenuineBoundary(fail="nominal")
        cost=ObservedSequentialCost(route,"stop_fixed")
        score=cost([1,2,3])
        self.assertGreater(score,1e9)
        self.assertEqual(cost.calls,1)
        self.assertEqual(route.real_routing_calls,1)
        self.assertEqual(cost.last["observed_scenarios"],["nominal"])
        self.assertEqual(cost.last["actual_calls"],1)
        self.assertEqual(cost.last["status"],"measured_infeasible")
        self.assertEqual(cost.censor_safe_cached_feedback([1,2,3],score)["observed_violations"],[.1])
        self.assertIsNone(cost.censor_safe_cached_feedback([2,1,3],score))
        self.assertIsNone(cost.full_scenario_cached_feedback([1,2,3],score))
        self.assertEqual(cost.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],2)

    def test_exact_all_scenario_verification_and_last_only_callback(self):
        route=FakeGenuineBoundary(fail=None)
        cost=ObservedSequentialCost(route,"stop_fixed")
        score=cost([1,2,3])
        self.assertEqual(score,140000.)
        self.assertEqual(cost.calls,3)
        self.assertEqual(cost.last["status"],"verified_feasible")
        self.assertEqual(cost.censor_safe_cached_feedback([1,2,3],score)["observed_violations"],[0,0,0])
        self.assertEqual(cost.full_scenario_cached_feedback([1,2,3],score),[0,0,0])
        self.assertEqual(cost.summary()["verified_all_scenario_feasible_candidates"],1)

    def test_numeric_unknown_withheld_and_not_misdiagnosed_constraint(self):
        route=FakeGenuineBoundary(fail=None,numerical="nominal")
        cost=ObservedSequentialCost(route,"stop_fixed")
        score=cost([1,2,3])
        self.assertEqual(cost.calls,1)
        self.assertIsNone(cost.censor_safe_cached_feedback([1,2,3],score))
        self.assertEqual(cost.last["status"],"numerically_unknown")
        self.assertEqual(cost.summary()["numerically_unknown_candidates"],1)
        self.assertEqual(cost.summary()["early_screened_physically_infeasible_candidates"],0)

    def test_postbudget_repeated_candidate_cannot_reuse_stale_3scenario_reward(self):
        route=FakeGenuineBoundary(fail=None)
        cost=ObservedSequentialCost(route,"full")
        cost.budget=3
        first=cost([1,2,3])
        self.assertIsNotNone(cost.censor_safe_cached_feedback([1,2,3],first))
        second=cost([1,2,3])
        self.assertEqual(second,1e12)
        self.assertEqual(cost.calls,3)
        self.assertIsNone(cost.censor_safe_cached_feedback([1,2,3],second))

    def test_full_prior_scenario_feedback_is_three_physically_measured(self):
        route=FakeGenuineBoundary(fail="even_source_heavy")
        cost=ObservedSequentialCost(route,"full")
        cost([1,2,3])
        self.assertEqual(route.real_routing_calls,3)
        self.assertEqual(cost.full_scenario_cached_feedback([1,2,3],1e5),[0,0,.1])
        self.assertEqual(cost.last["status"],"measured_infeasible")

    def test_exact_paired_seed_inference(self):
        rows=[]
        for seed in SEEDS:
            rows.extend((
                dict(seed=seed,method="safe",verified_all_scenario_feasible_candidates=1),
                dict(seed=seed,method="legacy",
                     verified_all_scenario_feasible_candidates=0 if seed in SEEDS[:4] else 1),
            ))
        p=paired(rows,"safe","legacy")
        self.assertEqual(p["both"],8)
        self.assertEqual(p["first_only"],4)
        self.assertEqual(p["second_only"],0)
        self.assertAlmostEqual(p["exact_two_sided_p_unadjusted"],.125)


if __name__=="__main__":unittest.main()
