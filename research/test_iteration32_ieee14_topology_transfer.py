"""Zero-native-AC I32 tests; never call PYPOWER runpf here."""
import unittest
import numpy as np
from pypower.idx_bus import BUS_I, PD, QD
from pypower.idx_gen import PG, VG
from gadapt.operations.cost_finding.sequential_scenario_budget_cost import (
    SequentialScenarioBudgetCost, CENSORED_BASE_SCORE, UNVERIFIED_SCORE
)
from research.iteration32_ieee14_topology_transfer import (
    IEEE14OriginalSpatialLoad, FullPaidFirstFailureScore,
    SCENARIOS, METHODS, SEEDS, BUDGET, POPULATION, UPPER_BOUND_AC, paired
)


class FakeScenario:
    """Synthetic counter ONLY. Not a physically solved candidate."""
    def __init__(self,fail=(),unknown=()):
        self.counter=0
        self.trace=[]
        self.fail=set(fail)
        self.unknown=set(unknown)

    def call(self,x,profile):
        self.counter+=1
        self.trace.append(profile)
        if profile in self.unknown:
            return {"converged":False,"feasible":False,"error":"fake unknown"}
        bad=profile in self.fail and x[0]<0.5
        return {"converged":True,"feasible":not bad,
                "normalized_violation":0.12 if bad else 0.,
                "original_economic_cost":6000.0,
                "max_nodal_mismatch_mva":0.}

    def instrument(self,cls,mode=None,budget=9):
        kwargs=dict(scenarios=SCENARIOS,scenario_evaluator=self.call,
                    physical_counter=lambda:self.counter,budget=budget,penalty=1e5)
        return cls(**kwargs) if cls is FullPaidFirstFailureScore else cls(mode=mode,**kwargs)


class I32ZeroPhysicalAC(unittest.TestCase):
    def test_preregistered_constants(self):
        self.assertEqual(len(METHODS),6)
        self.assertEqual(SEEDS,tuple(range(2104,2116)))
        self.assertEqual(BUDGET,180)
        self.assertEqual(POPULATION,12)
        self.assertEqual(UPPER_BOUND_AC,12960)
        self.assertEqual(SCENARIOS,("nominal","odd_bus_plus1pct","even_bus_plus1pct"))

    def test_spatial_load_source_invariance_and_zero_real_ac(self):
        g=IEEE14OriginalSpatialLoad()
        self.assertEqual(g.real_ac_calls,0)
        x=np.asarray([(lo+hi)/2 for lo,hi in g.bounds])
        n=g.source_case_without_ac(x,"nominal")
        o=g.source_case_without_ac(x,"odd_bus_plus1pct")
        e=g.source_case_without_ac(x,"even_bus_plus1pct")
        self.assertEqual(g.real_ac_calls,0)
        odd=np.asarray(g.source_bus_ids)%2==1
        for m,f in ((n,np.ones(14)),(o,np.where(odd,1.01,.99)),
                    (e,np.where(odd,.99,1.01))):
            for idx in (PD,QD):
                np.testing.assert_allclose(m["bus"][:,idx],g.original["bus"][:,idx]*f,
                                           atol=0,rtol=1e-14)
            np.testing.assert_array_equal(m["branch"],g.original["branch"])
            np.testing.assert_array_equal(m["gencost"],g.original["gencost"])
            np.testing.assert_array_equal(m["bus"][:,BUS_I],g.original["bus"][:,BUS_I])
            self.assertEqual(len(m["gen"]),5)
            for row,val in zip(g.reference.non_slack_gen_ids,x[:4]):
                self.assertEqual(m["gen"][row,PG],val)
            for row,val in zip(g.reference.all_gen_ids,x[4:]):
                self.assertEqual(m["gen"][row,VG],val)
        np.testing.assert_array_equal(g.original["bus"][:,PD],n["bus"][:,PD])
        np.testing.assert_array_equal(g.original["bus"][:,QD],n["bus"][:,QD])

    def test_profiles_and_bounds_fail_before_true_ac(self):
        g=IEEE14OriginalSpatialLoad()
        x=[(lo+hi)/2 for lo,hi in g.bounds]
        with self.assertRaises(ValueError):
            g.source_case_without_ac(x,"unregistered")
        with self.assertRaises(ValueError):
            g.source_case_without_ac(x[:-1],SCENARIOS[0])
        x[0]=g.bounds[0][1]+1
        with self.assertRaises(ValueError):
            g.source_case_without_ac(x,SCENARIOS[0])
        self.assertEqual(g.real_ac_calls,0)

    def test_same_censored_score_different_fake_costs(self):
        full=FakeScenario(fail=("nominal",))
        ctrl=FakeScenario(fail=("nominal",))
        screen=FakeScenario(fail=("nominal",))
        a=full.instrument(SequentialScenarioBudgetCost,"full")
        b=ctrl.instrument(FullPaidFirstFailureScore)
        c=screen.instrument(SequentialScenarioBudgetCost,"stop_fixed")
        real=a([0.1]); censored=b([0.1]); screened=c([0.1])
        self.assertAlmostEqual(real,6000.+1e5*.12)
        self.assertEqual(censored,screened)
        self.assertEqual(censored,CENSORED_BASE_SCORE+12000.)
        self.assertEqual(full.counter,3)
        self.assertEqual(ctrl.counter,3)
        self.assertEqual(screen.counter,1)
        self.assertEqual(b.summary()["completely_evaluated_candidates"],1)
        self.assertEqual(b.summary()["fully_paid_candidates_with_censored_selection_score"],1)
        self.assertEqual(b.summary()["actual_native_AC_calls"],3)
        self.assertEqual(c.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],2)

    def test_original_full_feasible_source_cost_not_censored(self):
        s=FakeScenario()
        cost=s.instrument(FullPaidFirstFailureScore)
        self.assertEqual(cost([0.8]),6000.)
        self.assertEqual(s.counter,3)
        self.assertEqual(cost.summary()["verified_all_scenario_feasible_candidates"],1)
        self.assertEqual(cost.summary()["best_verified_robust_mean_economic_cost_or_null"],6000.)

    def test_numeric_unknown_not_source_infeasible_even_after_physical_failure(self):
        s=FakeScenario(fail=("nominal",),unknown=("even_bus_plus1pct",))
        ev=s.instrument(FullPaidFirstFailureScore)
        self.assertEqual(ev([.1]),UNVERIFIED_SCORE)
        self.assertEqual(ev.summary()["numerically_unknown_candidates"],1)
        self.assertEqual(ev.summary()["verified_all_scenario_feasible_candidates"],0)
        self.assertEqual(s.counter,3)

    def test_complete_batch_reservation_after_fake_partial(self):
        s=FakeScenario(fail=("nominal",))
        ev=s.instrument(FullPaidFirstFailureScore,budget=4)
        ev([.1])
        self.assertEqual(ev([.8]),UNVERIFIED_SCORE)
        self.assertEqual(s.counter,3)
        self.assertEqual(ev.summary()["post_budget_requests_without_AC"],1)

    def test_monotone_native_ac_counter_required(self):
        counter={"n":0}
        def lying(x,s):
            return {"converged":True,"feasible":True,
                    "original_economic_cost":1.0,"normalized_violation":0.0}
        ev=FullPaidFirstFailureScore(scenarios=SCENARIOS,
              scenario_evaluator=lying,physical_counter=lambda:counter["n"],
              budget=3)
        with self.assertRaises(RuntimeError):
            ev([.5])

    def test_exact_paired_success_discordance(self):
        rows=[]
        for seed in SEEDS:
            rows.append({"seed":seed,"method":"a",
                         "verified_all_scenario_feasible_candidates":0 if seed in SEEDS[:4] else 1})
            rows.append({"seed":seed,"method":"b",
                         "verified_all_scenario_feasible_candidates":1})
        q=paired(rows,"a","b")
        self.assertEqual(q["first_only"],0)
        self.assertEqual(q["second_only"],4)
        self.assertEqual(q["both"],8)
        self.assertEqual(q["neither"],0)
        self.assertAlmostEqual(q["exact_two_sided_discordant_binomial_p_UNADJUSTED"],0.125)


if __name__=="__main__":
    unittest.main()
