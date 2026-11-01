"""Iteration18 IEEE118 transfer tests; no real AC calls in unit suite."""
import unittest
import numpy as np

from research.iteration18_ieee118_gadapt_transfer import (
    IEEE118NineControlSubset,physics_118,EXPECTED_SELECTED,EXPECTED_SLACK
)
from research.iteration17_ieee14_gadapt_economic_pf import (
    PhysicalBudgetRecorder,TOLS
)


class IEEE118TransferTests(unittest.TestCase):
    def test_preregistered_original_generator_ids_and_source_limits(self):
        g=IEEE118NineControlSubset()
        self.assertEqual(g.n,9)
        self.assertEqual(g.non_slack_gen_ids,list(EXPECTED_SELECTED))
        self.assertEqual(g.slack_gen_ids,[EXPECTED_SLACK])
        self.assertEqual([int(g.source["gen"][i,0]) for i in g.non_slack_gen_ids],
                         [89,80,10,66])
        self.assertEqual(int(g.source["gen"][EXPECTED_SLACK,0]),69)
        self.assertEqual(len(g.source["gen"]),54)
        self.assertEqual(len(g.source["bus"]),118)
        self.assertEqual(len(g.source["branch"]),186)
        self.assertTrue(all(high>low for low,high in g.bounds))

    def test_49_uncontrolled_original_generators(self):
        g=IEEE118NineControlSubset()
        self.assertEqual(len(g.all_gen_ids),5)
        self.assertEqual(len(g.source["gen"])-len(g.all_gen_ids),49)
        self.assertEqual(g.settings["ENFORCE_Q_LIMS"],0)
        self.assertEqual(g.real_ac_calls,0)

    def test_source_incomplete_solver_output_rejected(self):
        g=IEEE118NineControlSubset()
        with self.assertRaises((ValueError,KeyError,IndexError)):
            physics_118({"bus":g.source["bus"],"gen":g.source["gen"],
                         "branch":g.source["branch"]},g.source)

    def test_invalid_candidate_does_not_use_fictitious_physical_call(self):
        g=IEEE118NineControlSubset()
        with self.assertRaises(ValueError):
            g.evaluate(np.ones(9)*float("nan"))
        self.assertEqual(g.real_ac_calls,0)
        with self.assertRaises(ValueError):
            g.evaluate([9999]*9)
        self.assertEqual(g.real_ac_calls,0)

    def test_shared_source_physics_tolerances(self):
        self.assertEqual(TOLS["generator_q_mvar"],1e-3)
        self.assertEqual(TOLS["ac_nodal_balance_mva"],1e-3)

if __name__=="__main__":
    unittest.main()
