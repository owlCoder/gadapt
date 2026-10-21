"""I20 reactive Q-screen protocol/regression guards; 0 real AC calls."""
import unittest
import numpy as np

from research.iteration20_ieee118_reactive_sensitivity import (
    source_sensitivity_preflight,preregistered_states,original_specific_q,
    ID103,ID105,DELTA,
)


class OriginalIEEE118QScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref,cls.system=source_sensitivity_preflight()

    def test_source_Q_offenders_and_previous_real_baseline_only(self):
        self.assertAlmostEqual(self.ref["generator_q_mvar"]["total_excess"],
                               78.09919501728558,places=5)
        self.assertEqual(int(self.system.source["gen"][ID103,0]),103)
        self.assertEqual(int(self.system.source["gen"][ID105,0]),105)
        self.assertEqual(self.system.real_ac_calls,0)

    def test_exact_eight_unique_original_source_vg_perturbations(self):
        scenarios=preregistered_states()
        self.assertEqual(len(scenarios),8)
        self.assertEqual(len(set((a,b) for _,a,b in scenarios)),8)
        self.assertEqual(scenarios[0],("gen103_minus",-.02,0.))
        self.assertEqual(scenarios[-1],("both_plus_plus",.02,.02))
        self.assertEqual(self.system.real_ac_calls,0)

    def test_original_bus_source_bounds(self):
        source=self.system.source
        for genid,busid in [(ID103,103),(ID105,105)]:
            rows=source["bus"][source["bus"][:,0]==busid]
            self.assertEqual(int(rows[0,1]),2)
            low,high=float(rows[0,12]),float(rows[0,11])
            setpoint=source["gen"][genid,5]
            self.assertGreaterEqual(setpoint-DELTA,low)
            self.assertLessEqual(setpoint+DELTA,high)
        self.assertAlmostEqual(self.system.source["gen"][ID103,5],1.01)
        self.assertAlmostEqual(self.system.source["gen"][ID105,5],.965)

    def test_generator_Q_ranking_matches_previous_actual_source(self):
        g=self.system.source["gen"]
        fake=g.copy()
        fake[ID103,2]=75.42236358206827
        fake[ID105,2]=-18.334525252389284
        q103=original_specific_q(fake,g,ID103)
        q105=original_specific_q(fake,g,ID105)
        self.assertAlmostEqual(q103["q_excess_above_max_mvar"],35.42236358206827,places=6)
        self.assertAlmostEqual(q105["q_excess_below_min_mvar"],10.334525252389284,places=6)
        self.assertEqual(self.system.real_ac_calls,0)

if __name__=="__main__":
    unittest.main()
