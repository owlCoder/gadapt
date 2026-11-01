"""Source-faithful thermal constraint regression tests; no AC solves."""
import unittest
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pandapower.networks as pn

from research.iteration7_rte_source_physics import (
    read_and_validate_map,source_apparent_violations
)

class SourceRatedPhysicalTests(unittest.TestCase):
    def test_zero_rate_does_not_create_fictitious_thermal_violation(self):
        net=SimpleNamespace(
            line=pd.DataFrame({"in_service":[True]}),
            trafo=pd.DataFrame({"in_service":[True]}),
            res_line=pd.DataFrame({"p_from_mw":[230.],"q_from_mvar":[0.],
                                   "p_to_mw":[220.],"q_to_mvar":[0.]}),
            res_trafo=pd.DataFrame({"p_hv_mw":[120.],"q_hv_mvar":[0.],
                                    "p_lv_mw":[110.],"q_lv_mvar":[0.]})
        )
        totals,count,maximum=source_apparent_violations(
            net,{"line":np.array([0.]),"trafo":np.array([100.])})
        self.assertEqual(totals["line"],0.)
        self.assertEqual(count["line"],0)
        self.assertAlmostEqual(totals["trafo"],0.2)
        self.assertEqual(count["trafo"],1)
        self.assertAlmostEqual(maximum["trafo"],120.)

    def test_both_ends_and_reactive_flow_count(self):
        net=SimpleNamespace(
            line=pd.DataFrame({"in_service":[True]}),
            trafo=pd.DataFrame(columns=["in_service"]),
            res_line=pd.DataFrame({"p_from_mw":[60.],"q_from_mvar":[80.],
                                   "p_to_mw":[40.],"q_to_mvar":[120.]}),
            res_trafo=pd.DataFrame({"p_hv_mw":[],"q_hv_mvar":[],
                                    "p_lv_mw":[],"q_lv_mvar":[]}))
        totals,count,_=source_apparent_violations(
            net,{"line":np.array([100.]),"trafo":np.array([],float)})
        self.assertAlmostEqual(totals["line"],(1600+14400)**.5/100-1.)
        self.assertEqual(count["line"],1)

    def test_2531_source_ratings_match_physical_pandapower_element_endpoints(self):
        net=pn.case1888rte()
        rates=read_and_validate_map(net)
        self.assertEqual(len(rates["line"]),1976)
        self.assertEqual(len(rates["trafo"]),555)
        self.assertEqual(int(np.sum(rates["line"]==0)),222)
        self.assertEqual(int(np.sum(rates["trafo"]==0)),233)
        for i in (404,466,402,403,493,380):
            self.assertEqual(rates["trafo"][i],0.)

if __name__=="__main__":
    unittest.main()
