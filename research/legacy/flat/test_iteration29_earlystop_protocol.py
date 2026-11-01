"""I29 native IEEE118 experiment preflight: no AC solves."""
import unittest

from research.iteration29_real_scenario_earlystop_benchmark import (
    METHODS,SEEDS,BUDGET,POPULATION,EXPECTED_MAX_REAL_AC,method_mode,
)
from research.iteration27_real_scenario_credit_benchmark import (
    IEEE118SixSourcePVThreeScenarios,LOADS,CONTROL_BUS_GEN
)


class IEEE118SequentialScenarioExperimentTests(unittest.TestCase):
    def test_preregistered_four_new_seeds_5_mode_real_ac_budget(self):
        self.assertEqual(SEEDS,(2060,2061,2062,2063))
        self.assertEqual(METHODS,(
            "gadapt_full","gadapt_stop_fixed","gadapt_stop_adaptive",
            "scipy_de_full","scipy_de_stop_fixed"))
        self.assertEqual(len(SEEDS)*len(METHODS),20)
        self.assertEqual(BUDGET,180)
        self.assertEqual(POPULATION,12)
        self.assertEqual(EXPECTED_MAX_REAL_AC,3600)
        self.assertEqual(method_mode("gadapt_full"),"full")
        self.assertEqual(method_mode("gadapt_stop_adaptive"),"stop_adaptive")
        self.assertEqual(method_mode("scipy_de_stop_fixed"),"stop_fixed")
        with self.assertRaises(ValueError):
            method_mode("gadapt_magic_success")

    def test_original_electrical_model_same_six_source_PV_controls(self):
        p=IEEE118SixSourcePVThreeScenarios()
        self.assertEqual(p.real_ac_calls,0)
        self.assertEqual(p.n,6)
        self.assertEqual(LOADS,(.98,1.,1.02))
        self.assertEqual([bus for bus,_ in CONTROL_BUS_GEN],
            [103,32,34,92,19,74])
        self.assertEqual(len(p.source["gen"]),54)
        self.assertEqual(len(p.source["bus"]),118)
        self.assertEqual(len(p.source["branch"]),186)
        self.assertEqual(p.real_ac_calls,0)

if __name__=="__main__":
    unittest.main()
