"""Iteration 12 tests for transparent local BSD-PYPOWER Q-index repair.

Import and inspect only: does NOT run a real AC power flow.
"""
import copy
import inspect
import json
import unittest

from research.iteration11_original_matpower_native_pf import load_original
from research.iteration12_local_pypower_qlim_patch import runpf
from research.iteration12_native_q_repair import compare_native_control, PREVIOUS


class NativeQLimitRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=load_original()
        with open(PREVIOUS,encoding="utf-8") as f:
            cls.previous=json.load(f)
        cls.baseline=cls.previous["attempts"][0]

    def test_source_has_ten_preexisting_online_pg_below_pmin(self):
        gen=self.source["gen"]
        online=[(index,row) for index,row in enumerate(gen,1) if row[7]>0]
        prior=[(index,row) for index,row in online if row[1]<row[9]-1e-7]
        self.assertEqual(len(prior),10)
        self.assertEqual([int(i) for i,_ in prior],
            [17,25,26,27,35,39,43,46,48,49])
        self.assertAlmostEqual(sum(row[9]-row[1] for _,row in prior),54.95)
        self.assertAlmostEqual(
            self.baseline["metrics"]["p_generator_bounds_mw"]["below_limit_total"],
            54.95)

    def test_local_vendor_q_indices_and_queuing_guards(self):
        src=inspect.getsource(runpf)
        self.assertIn("bus[gen[:, GEN_BUS].astype(int), BUS_TYPE]",src)
        self.assertIn("bus[gen[mx, GEN_BUS].astype(int), BUS_TYPE]",src)
        self.assertIn(
            "if len(infeas) == len(remaining) and all(infeas == remaining):",
            src)
        self.assertNotIn("bus[gen[:, GEN_BUS], BUS_TYPE]",src)
        self.assertNotIn("or all(infeas == remaining)",src)

    def test_unmodified_electrical_control_matches_identity(self):
        control=copy.deepcopy(self.baseline)
        self.assertTrue(compare_native_control(control,self.baseline))
        control["metrics"]["original_source_slack_qg_mvar"]+=1
        with self.assertRaises(ValueError):
            compare_native_control(control,self.baseline)

    def test_native_original_slack_is_1320(self):
        self.assertEqual(int(self.source["bus"][self.source["bus"][:,1]==3,0][0]),1320)
        self.assertEqual(self.baseline["metrics"]["original_source_slack_bus_id"],1320)
        self.assertFalse(self.baseline["metrics"]["all_explicit_checked_constraints_feasible"])

if __name__=="__main__":
    unittest.main()
