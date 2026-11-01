"""Iteration 22 central-difference proposals and source PG/VG guards: 0 real AC."""
import unittest
import math

from research.iteration22_ieee118_qmidpoint_repair import (
    fixed_control_preflight,five_fixed_scenarios,
    SOURCE_ID_BY_BUS,Q_BASELINE,MAX_PREDICTED_STEP,
)


class IEEE118MidpointQRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid,cls.formula=fixed_control_preflight()

    def test_exact_prior_source_three_remaining_qmin_and_source_base(self):
        self.assertEqual(set(self.formula),{34,92,19})
        self.assertEqual(SOURCE_ID_BY_BUS,{34:15,92:42,19:8})
        self.assertAlmostEqual(Q_BASELINE,30.525900533161856)
        self.assertEqual(self.grid.real_ac_calls,0)

    def test_source_q_slope_and_trust_region(self):
        for bus,row in self.formula.items():
            self.assertGreater(row["finite_difference_q_slope_mvar_per_pu"],0)
            self.assertGreater(row["preregistered_clipped_delta_vg_pu"],0)
            self.assertLessEqual(row["preregistered_clipped_delta_vg_pu"],MAX_PREDICTED_STEP)
            self.assertGreater(row["target_midpoint_mvar"],row["already_measured_q_base_mvar"])
            self.assertEqual(int(self.grid.source["gen"][SOURCE_ID_BY_BUS[bus],0]),bus)
        self.assertTrue(all(math.isfinite(z["finite_difference_q_slope_mvar_per_pu"])
            for z in self.formula.values()))

    def test_exact_five_new_real_source_states_frozen(self):
        cases=five_fixed_scenarios()
        self.assertEqual([name for name,_ in cases],
                         ["bus34_predicted","bus92_predicted","bus19_predicted",
                          "all_three_half","all_three_full"])
        self.assertEqual(cases[-2][1],{34:.5,92:.5,19:.5})
        self.assertEqual(cases[-1][1],{34:1.,92:1.,19:1.})
        self.assertEqual(len(cases),5)

    def test_no_physics_called_in_source_preflight(self):
        self.assertEqual(self.grid.real_ac_calls,0)
        self.assertEqual(len(self.grid.source["bus"]),118)
        self.assertEqual(len(self.grid.source["gen"]),54)
        self.assertEqual(len(self.grid.source["branch"]),186)

if __name__=="__main__":
    unittest.main()
