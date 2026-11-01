"""I33 zero-real-routing unit tests. No network fetch, no Dijkstra and no AC."""
import unittest
import math
from types import SimpleNamespace
import numpy as np

from gadapt.operations.cost_finding.sequential_scenario_budget_cost import (
    CENSORED_BASE_SCORE, SequentialScenarioBudgetCost, UNVERIFIED_SCORE,
)
from research.iteration33_geant_routing_budget import (
    make_scenario_without_routing, SCENARIOS, METHODS, SEEDS, BUDGET,
    POPULATION, HYPOTHETICAL_CAP, UPPER_BOUND_ROUTING_CALLS,
    holm_adjust, paired, FullPaidFirstFailureScore
)


class FakeGraph:
    def __init__(self,nodes):
        self.nodes=nodes


class FakeGeant:
    def __init__(self):
        nodes=[f"N{i:02d}" for i in range(1,23)]
        self.graph=FakeGraph(nodes)
        self.edges=[("link",1.,2.)]*36
        self.demands=[(nodes[i%22],nodes[(i+1)%22],float(10+i))
                      for i in range(462)]


class FakeEvaluations:
    """Synthetic values: NEVER a real networkx Dijkstra/module evaluation."""
    def __init__(self,first_fail=True,unknown=None):
        self.count=0
        self.calls=[]
        self.fail=first_fail
        self.unknown=unknown

    def __call__(self,x,scenario):
        self.count+=1
        self.calls.append(scenario)
        if self.unknown==scenario:
            return {"converged":False,"feasible":False,"error":"fake"}
        violated=self.fail and scenario=="nominal" and x[0]==1
        return {"converged":True,"feasible":not violated,
                "original_economic_cost":140000.,
                "normalized_violation":.2 if violated else 0.,
                "max_nodal_mismatch_mva":None}

    def build(self,mode="full",fully_censored=False,budget=9):
        params=dict(scenarios=SCENARIOS,scenario_evaluator=self,
                    physical_counter=lambda:self.count,budget=budget,penalty=1e5)
        return FullPaidFirstFailureScore(**params) if fully_censored else (
            SequentialScenarioBudgetCost(mode=mode,**params))


class NoTrueRoutingTests(unittest.TestCase):
    def test_preregistration_stability(self):
        self.assertEqual(len(METHODS),6)
        self.assertEqual(SEEDS,tuple(range(2200,2212)))
        self.assertEqual(BUDGET,120)
        self.assertEqual(POPULATION,24)
        self.assertEqual(HYPOTHETICAL_CAP,145000.)
        self.assertEqual(UPPER_BOUND_ROUTING_CALLS,8640)

    def test_synthetic_load_variants_preserve_topology_weights_demand_pairs(self):
        old=FakeGeant()
        matrices={s:make_scenario_without_routing(old,s) for s in SCENARIOS}
        self.assertEqual(len(old.demands),462)
        self.assertEqual(len(matrices["nominal"].demands),462)
        for scenario,model in matrices.items():
            self.assertIsNot(model,old)
            self.assertIs(model.graph,old.graph)
            self.assertIs(model.edges,old.edges)
            self.assertEqual([(a,b) for a,b,_ in model.demands],
                             [(a,b) for a,b,_ in old.demands])
            for i,(a,_,z) in enumerate(old.demands):
                ordinal=int(a[-2:])
                odd=bool(ordinal%2)
                expected=(1. if scenario=="nominal" else
                          1.08 if (scenario=="odd_source_heavy" and odd or
                                   scenario=="even_source_heavy" and not odd)
                          else .92)
                self.assertAlmostEqual(model.demands[i][2],z*expected)
        self.assertEqual(old.demands[0][2],10.)

    def test_invalid_source_fails_pre_simulator(self):
        source=FakeGeant()
        with self.assertRaises(ValueError):
            make_scenario_without_routing(source,"extra_unregistered_profile")
        source.demands[5]=("bad-node","N03",4.)
        with self.assertRaises(ValueError):
            make_scenario_without_routing(source,"nominal")

    def test_full_censored_physically_costs_three_synthetic_measurements(self):
        full=FakeEvaluations()
        control=FakeEvaluations()
        screen=FakeEvaluations()
        score_a=full.build("full")([1])
        score_b=control.build(fully_censored=True)([1])
        score_c=screen.build("stop_fixed")([1])
        self.assertEqual(full.count,3)
        self.assertEqual(control.count,3)
        self.assertEqual(screen.count,1)
        self.assertAlmostEqual(score_a,140000+20000)
        self.assertEqual(score_b,score_c)
        self.assertAlmostEqual(score_b,CENSORED_BASE_SCORE+20000.)

    def test_cost_cap_all_three_synthetic_feasible_verified(self):
        f=FakeEvaluations(first_fail=False)
        eval=f.build("stop_fixed")
        self.assertEqual(eval([5]),140000)
        self.assertEqual(f.count,3)
        self.assertEqual(eval.summary()["verified_all_scenario_feasible_candidates"],1)
        self.assertEqual(eval.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],0)

    def test_missing_routing_scenarios_are_not_feasible(self):
        f=FakeEvaluations()
        eval=f.build("stop_fixed")
        eval([1])
        self.assertEqual(eval.summary()["verified_all_scenario_feasible_candidates"],0)
        self.assertEqual(eval.summary()["early_screened_physically_infeasible_candidates"],1)
        self.assertEqual(eval.summary()["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"],2)

    def test_numeric_unknown_not_a_proven_budget_failure(self):
        f=FakeEvaluations(unknown="nominal")
        eval=f.build("stop_fixed")
        self.assertEqual(eval([1]),UNVERIFIED_SCORE)
        self.assertEqual(eval.summary()["numerically_unknown_candidates"],1)
        self.assertEqual(eval.summary()["early_screened_physically_infeasible_candidates"],0)

    def test_no_fake_free_dijkstra_calls(self):
        def lying(x,s):
            return {"converged":True,"feasible":True,
                    "original_economic_cost":130000.,"normalized_violation":0.}
        eval=SequentialScenarioBudgetCost(
            SCENARIOS,lying,lambda:0,budget=3,mode="stop_fixed")
        with self.assertRaises(RuntimeError):
            eval([2])

    def test_holm_and_exact_paired_binary(self):
        p=holm_adjust([.01,.02,.06,.20,1.])
        self.assertEqual(p,[.05,.08,.18,.4,1.])
        rows=[]
        for seed in SEEDS:
            rows.extend(({"seed":seed,"method":"a",
                          "verified_all_scenario_feasible_candidates":
                          0 if seed in SEEDS[:4] else 1},
                         {"seed":seed,"method":"b",
                          "verified_all_scenario_feasible_candidates":1}))
        q=paired(rows,"a","b")
        self.assertEqual(q["second_only"],4)
        self.assertAlmostEqual(q["exact_two_sided_discordant_binomial_p_unadjusted"],.125)


if __name__=="__main__":
    unittest.main()
