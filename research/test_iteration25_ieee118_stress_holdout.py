"""Iteration25 source IEEE118 load holdout preflight; ZERO actual AC solves."""
import unittest
import numpy as np
from research.iteration25_ieee118_stress_holdout import (
    selected_original_source_controllers, FACTORS, ORDER,
)


class IEEE118OutOfSampleFixedPVTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid,cls.selected=selected_original_source_controllers()

    def test_exact_five_existing_source_physically_feasible_controller_names(self):
        self.assertEqual(tuple(self.selected),ORDER)
        self.assertEqual(len(self.selected),5)
        self.assertEqual(ORDER,
            ("historic_i23_alpha08","gadapt_legacy","scipy_de","random_search","bounded_powell"))
        self.assertEqual(self.grid.real_ac_calls,0)

    def test_previous_historical_best_is_paid_once_not_a_new_baseline(self):
        history=self.selected["historic_i23_alpha08"]
        self.assertIsNone(history["historic_seed"])
        self.assertAlmostEqual(history["historic_original_feasible_cost"],131198.7975746236)
        self.assertAlmostEqual(history["vector"][0],.99)
        self.assertAlmostEqual(history["vector"][1],.973)

    def test_all_five_existing_source_controls_within_source_local_box(self):
        for label,data in self.selected.items():
            x=np.asarray(data["vector"],float)
            self.assertEqual(x.shape,(5,))
            self.assertTrue(np.all(np.isfinite(x)))
            self.assertGreater(data["historic_original_feasible_cost"],0)
            for v,(low,high) in zip(x,self.grid.bounds):
                self.assertGreaterEqual(v,low-1e-10)
                self.assertLessEqual(v,high+1e-10)
        self.assertEqual(self.grid.real_ac_calls,0)

    def test_original_load_is_not_modified_in_source_fixture(self):
        self.assertEqual(FACTORS,(.98,1.02))
        self.assertEqual(len(FACTORS)*len(ORDER),10)
        self.assertEqual(len(self.grid.source["bus"]),118)
        self.assertEqual(len(self.grid.source["gen"]),54)
        self.assertEqual(len(self.grid.source["branch"]),186)
        self.assertEqual(self.grid.real_ac_calls,0)

if __name__=="__main__":
    unittest.main()
