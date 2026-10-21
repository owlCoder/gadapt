"""Regression checks for the iteration 7 RTE audit; no extra AC solve."""
import math
import unittest
from types import SimpleNamespace

import numpy as np
import pandas as pd

from research.iteration7_rte_audit import components, field_summary, json_safe


class AuditTest(unittest.TestCase):
    def test_missing_and_nonfinite_limits_do_not_masquerade_as_ratings(self):
        frame=pd.DataFrame({"rating":[100.0, np.nan, math.inf, -2., 0.]})
        summary=field_summary(frame,"rating")
        self.assertEqual(summary["non_null_finite"],3)
        self.assertEqual(summary["positive"],1)
        self.assertEqual(summary["zero"],1)
        self.assertEqual(summary["negative"],1)
        self.assertFalse(field_summary(frame,"missing")["column_exists"])

    def test_ac_failure_serializes_as_missing_not_false_feasible(self):
        nested={"violation":math.inf,"rows":[math.nan,-math.inf,3.5]}
        self.assertEqual(json_safe(nested),{"violation":None,
                                            "rows":[None,None,3.5]})

    def test_thermal_and_voltage_components_match_iter6_definition(self):
        net=SimpleNamespace(
            res_bus=pd.DataFrame({"vm_pu":[0.93,1.0]}),
            res_line=pd.DataFrame({"loading_percent":[99.,150.]}),
            res_trafo=pd.DataFrame({"loading_percent":[120.]}),
            gen=pd.DataFrame({"min_q_mvar":[-10.],"max_q_mvar":[10.]}),
            res_gen=pd.DataFrame({"q_mvar":[10.]})
        )
        grid=SimpleNamespace(net=net, v_lower=np.array([.95,.94]),
                             v_upper=np.array([1.08,1.08]))
        obs=components(grid,{"solver_failed":False})
        self.assertAlmostEqual(obs["voltage_under_pu"],0.02)
        self.assertAlmostEqual(obs["line_excess_per_unit_sum"],0.5)
        self.assertAlmostEqual(obs["trafo_excess_per_unit_sum"],0.2)
        self.assertEqual(obs["trafo_overloads_count"],1)
        self.assertEqual(obs["q_at_upper_limit_count"],1)
        self.assertIsNone(components(grid,{"solver_failed":True})
                          ["line_excess_per_unit_sum"])


if __name__=="__main__":
    unittest.main()
