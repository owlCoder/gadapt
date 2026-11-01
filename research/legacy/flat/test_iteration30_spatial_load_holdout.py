"""I30 genuine original IEEE118 spatial stress preflight: ZERO AC runpf."""
import unittest

import numpy as np
from pypower.idx_bus import BUS_I, PD, QD
from pypower.idx_gen import PG, VG

from research.iteration30_spatial_load_holdout import (
    IEEE118SourceParityLoadScenario, SPATIAL_SCENARIOS, SPATIAL_SEEDS,
    METHODS, BUDGET, POPULATION, UPPER_BOUND_TRUE_AC
)
from research.iteration27_real_scenario_credit_benchmark import CONTROL_BUS_GEN


class OriginalSourceParityHoldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network=IEEE118SourceParityLoadScenario()

    def test_three_new_explicit_spatial_profiles_unseen_in_earlier_uniform_load(self):
        self.assertEqual(SPATIAL_SCENARIOS,
             ("nominal","odd_bus_heavier","even_bus_heavier"))
        self.assertEqual(SPATIAL_SEEDS,(2070,2071,2072,2073))
        self.assertEqual(len(METHODS),5)
        self.assertEqual(len(METHODS)*len(SPATIAL_SEEDS),20)
        self.assertEqual(BUDGET,180)
        self.assertEqual(POPULATION,12)
        self.assertEqual(UPPER_BOUND_TRUE_AC,3600)
        self.assertEqual(self.network.real_ac_calls,0)

    def test_only_original_bus_PD_QD_scale_by_bus_I_parity(self):
        source=self.network.source
        original=source["bus"]
        odd=(original[:,BUS_I].astype(int)%2)==1
        for name in SPATIAL_SCENARIOS:
            case=self.network.new_source_case_no_ac(self.network.center,name)
            if name=="nominal":
                scale=np.ones(118)
            elif name=="odd_bus_heavier":
                scale=np.where(odd,1.02,.98)
            else:
                scale=np.where(odd,.98,1.02)
            np.testing.assert_allclose(case["bus"][:,PD],original[:,PD]*scale,rtol=0,atol=1e-10)
            np.testing.assert_allclose(case["bus"][:,QD],original[:,QD]*scale,rtol=0,atol=1e-10)
            for col in range(original.shape[1]):
                if col not in (PD,QD):
                    np.testing.assert_array_equal(case["bus"][:,col],original[:,col])
            np.testing.assert_array_equal(case["branch"],source["branch"])
            np.testing.assert_array_equal(case["gen"][:,PG],source["gen"][:,PG])
            allowed=np.ones(54,dtype=bool)
            allowed[[i for _,i in CONTROL_BUS_GEN]]=False
            np.testing.assert_array_equal(case["gen"][allowed,VG],
                                         source["gen"][allowed,VG])
            self.assertEqual(self.network.real_ac_calls,0)

    def test_invalid_profile_fails_pre_solver_without_a_real_ac(self):
        with self.assertRaises(ValueError):
            self.network.new_source_case_no_ac(self.network.center,"favorable_result")
        with self.assertRaises(ValueError):
            self.network.new_source_case_no_ac(np.zeros(6),"nominal")
        self.assertEqual(self.network.real_ac_calls,0)

if __name__=="__main__":
    unittest.main()
