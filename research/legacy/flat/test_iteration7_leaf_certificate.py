"""Pure analytical regression tests, no powerflow evaluations."""
import unittest
from types import SimpleNamespace

import pandas as pd

from research.iteration7_leaf_certificate import candidate, terminal_capacity


class RadialCertificateTests(unittest.TestCase):
    def make_net(self):
        return SimpleNamespace(
            bus=pd.DataFrame({"vn_kv":[220.,20.],
                              "max_vm_pu":[1.05,1.05]},index=[1,2]),
            line=pd.DataFrame(columns=["from_bus","to_bus","in_service"]),
            trafo=pd.DataFrame({"hv_bus":[1],"lv_bus":[2],"in_service":[True],
                                "vn_hv_kv":[220.],"vn_lv_kv":[20.],
                                "sn_mva":[100.],"max_loading_percent":[100.]},index=[8]),
            gen=pd.DataFrame({"bus":[2],"in_service":[True],"p_mw":[200.],
                              "min_p_mw":[200.],"max_p_mw":[250.],
                              "scaling":[1.]},index=[33]),
            load=pd.DataFrame({"bus":[2],"in_service":[True],"p_mw":[20.],
                               "scaling":[1.],"const_i_percent":[0.],
                               "const_z_percent":[0.]},index=[0]),
            sgen=pd.DataFrame(columns=["bus","in_service"]),
            ext_grid=pd.DataFrame(columns=["bus","in_service"]),
            shunt=pd.DataFrame(columns=["bus","in_service"]),
            storage=pd.DataFrame(columns=["bus","in_service"]),
            ward=pd.DataFrame(columns=["bus","in_service"]),
            xward=pd.DataFrame(columns=["bus","in_service"]),
            switch=pd.DataFrame(columns=["bus"])
        )

    def test_large_fixed_export_yields_strict_lower_bound(self):
        net=self.make_net()
        c=candidate(net,8,2)
        self.assertTrue(c["eligible"])
        self.assertTrue(c["certified_infeasible_under_assumptions"])
        self.assertEqual(c["minimum_export_p_mw"],180)
        self.assertAlmostEqual(c["necessary_max_export_mw_from_current_limit"],105.)
        self.assertAlmostEqual(c["excess_lower_bound_mw"],75.)

    def test_parallel_branch_disqualifies_leaf_certificate(self):
        net=self.make_net()
        net.line=pd.DataFrame({"from_bus":[2],"to_bus":[3],"in_service":[True]})
        c=candidate(net,8,2)
        self.assertFalse(c["eligible"])

    def test_variable_current_power_load_disqualifies_certificate(self):
        net=self.make_net()
        net.load.at[0,"const_i_percent"]=20.
        self.assertFalse(candidate(net,8,2)["eligible"])

    def test_lower_export_does_not_prove_infeasible(self):
        net=self.make_net()
        net.gen.at[33,"min_p_mw"]=80.
        c=candidate(net,8,2)
        self.assertTrue(c["eligible"])
        self.assertFalse(c["certified_infeasible_under_assumptions"])

    def test_generator_scaling_must_be_known_unity(self):
        net=self.make_net()
        net.gen.at[33,"scaling"]=0.5
        self.assertFalse(candidate(net,8,2)["eligible"])

    def test_capacity_uses_terminal_nominal_voltage(self):
        self.assertAlmostEqual(terminal_capacity(100.,1.05,20.,20.,100.),105.)
        self.assertAlmostEqual(terminal_capacity(100.,1.05,10.,20.,100.),52.5)


if __name__=="__main__":
    unittest.main()
