"""Iteration21 source B34 B92 B19 B32 Q controls; all static, zero AC."""
import unittest
import numpy as np
from research.iteration21_ieee118_four_qmin_controls import (
    previous_measured_source_preflight, preregistered_states,
    VG_BASELINE_103,CONTROL_LIST,VG_DELTA,
)


class IEEE118FourQMINSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous,cls.grid=previous_measured_source_preflight()

    def test_original_source_Q_reference_is_a_real_prior_physical_call(self):
        self.assertAlmostEqual(
            self.previous["generator_q"]["total_excess"],32.34580769680004)
        self.assertEqual(self.previous["scenario"],"gen103_minus")
        self.assertEqual(self.grid.real_ac_calls,0)
        self.assertFalse(self.previous["physics"]["feasible"])

    def test_exact_eight_preregistered_target_vg_scenarios(self):
        cases=preregistered_states()
        self.assertEqual(len(cases),8)
        self.assertEqual(len(set((idx,delta) for _,idx,_,delta in cases)),8)
        self.assertEqual(cases[0],("bus34_minus",15,34,-.01))
        self.assertEqual(cases[-1],("bus32_plus",14,32,+.01))
        self.assertEqual([bus for _,bus,_ in CONTROL_LIST],[34,92,19,32])

    def test_all_other_original_generator_pg_vg_are_not_control_inputs(self):
        p=self.grid.source
        self.assertEqual(len(p["gen"]),54)
        self.assertEqual(int(p["gen"][45,0]),103)
        self.assertEqual(VG_BASELINE_103,.99)
        for j,bus,original_vg in CONTROL_LIST:
            self.assertEqual(int(p["gen"][j,0]),bus)
            self.assertAlmostEqual(float(p["gen"][j,5]),original_vg)
            source_bus=p["bus"][p["bus"][:,0]==bus][0]
            self.assertEqual(int(source_bus[1]),2)
            self.assertGreaterEqual(original_vg-VG_DELTA,source_bus[12])
            self.assertLessEqual(original_vg+VG_DELTA,source_bus[11])
        self.assertEqual(self.grid.real_ac_calls,0)

    def test_targeted_previous_q_min_violations(self):
        entries=self.previous["generator_q"]["top_12"]
        self.assertEqual({e["bus_id"] for e in entries},{34,92,19,32})
        self.assertEqual(sum(e["total_excess"] for e in entries),
                         self.previous["generator_q"]["total_excess"])

if __name__=="__main__":
    unittest.main()
