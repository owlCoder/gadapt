"""I24 original IEEE118 source five-PV controls. All unit tests use ZERO AC solves."""
import unittest
import numpy as np

from research.iteration24_ieee118_fivepv_real_gadapt import (
    calibrated_source_center,IEEE118FiveRelevantPV,
    CONTROL_BUS_TO_SOURCE_GEN,CONTROL_HALF_WIDTH_PU,
    METHODS,SEEDS,BUDGET,POPULATION,
)


class CalibratedPhysicalPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid=IEEE118FiveRelevantPV()

    def test_exact_five_physically_identified_source_controls(self):
        self.assertEqual(CONTROL_BUS_TO_SOURCE_GEN,
                         ((103,45),(32,14),(34,15),(92,42),(19,8)))
        self.assertEqual(self.grid.n,5)
        self.assertEqual(len(self.grid.bounds),5)
        self.assertEqual(len(self.grid.source["gen"]),54)
        self.assertEqual(len(self.grid.source["bus"]),118)
        self.assertEqual(len(self.grid.source["branch"]),186)
        self.assertEqual(self.grid.real_ac_calls,0)

    def test_common_calibration_box_and_source_historical_feasible_region(self):
        center,bounds=calibrated_source_center()
        self.assertAlmostEqual(center[0],.99)
        self.assertAlmostEqual(center[1],.973)
        self.assertAlmostEqual(center[2],.984+.75*.004016033221868577)
        self.assertAlmostEqual(center[3],.990+.75*.003533199035653122)
        self.assertAlmostEqual(center[4],.962+.75*.004619105395208329)
        for value,(lo,hi) in zip(center,bounds):
            self.assertAlmostEqual(value-lo,CONTROL_HALF_WIDTH_PU)
            self.assertAlmostEqual(hi-value,CONTROL_HALF_WIDTH_PU)
            self.assertGreater(value,lo)
            self.assertLess(value,hi)
        self.assertEqual(self.grid.real_ac_calls,0)

    def test_matpower_original_PG_are_not_free_optimizer_controls(self):
        source=self.grid.source["gen"]
        self.assertEqual([int(source[i,0]) for _,i in CONTROL_BUS_TO_SOURCE_GEN],
                         [103,32,34,92,19])
        self.assertEqual(len(source[:,1]),54)
        self.assertEqual(self.grid.real_ac_calls,0)

    def test_out_of_bounds_or_nonfinite_does_not_claim_ac(self):
        grid=IEEE118FiveRelevantPV()
        with self.assertRaises(ValueError):
            grid.evaluate(np.zeros(5))
        with self.assertRaises(ValueError):
            grid.evaluate(np.ones(5)*float("nan"))
        with self.assertRaises(ValueError):
            grid.evaluate(np.ones(8))
        self.assertEqual(grid.real_ac_calls,0)

    def test_comparison_methods_and_budget_frozen(self):
        self.assertEqual(METHODS,
            ("gadapt_legacy","scipy_de","random_search","bounded_powell"))
        self.assertEqual(SEEDS,(2026,2027,2028))
        self.assertEqual(BUDGET,96)
        self.assertEqual(POPULATION,16)
        self.assertEqual(BUDGET*len(SEEDS)*len(METHODS),1152)

if __name__=="__main__":
    unittest.main()
