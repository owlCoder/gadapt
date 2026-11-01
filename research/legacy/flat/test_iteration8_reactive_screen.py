"""Structural tests of Iteration 8 selection and Q diagnostics; no AC calls."""
import math
import unittest
from types import SimpleNamespace

import numpy as np
import pandas as pd

from research.iteration8_reactive_screen import (
    select_nearest_controls, eligible_controls, q_limit_summary, json_safe,
)


def small_network():
    buses = pd.DataFrame({
        "in_service": [True]*6,
        "min_vm_pu": [0.95]*6,
        "max_vm_pu": [1.05]*6,
    })
    gens = pd.DataFrame({
        "bus": [0,3,4,5],
        "in_service": [True]*4,
        "vm_pu": [1.0]*4,
        "min_q_mvar": [-2.]*4,
        "max_q_mvar": [2.]*4,
    }, index=[0,1,2,3])
    lines = pd.DataFrame({
        "from_bus":[0,1,2],
        "to_bus":[1,2,3],
        "in_service":[True,True,True],
    })
    transformers = pd.DataFrame({
        "hv_bus":[2],"lv_bus":[4],"in_service":[True],
    })
    return SimpleNamespace(
        bus=buses, gen=gens, line=lines, trafo=transformers,
    )


class Iteration8StructuralTests(unittest.TestCase):
    def test_nearest_control_excludes_first_eight_legacy_subset(self):
        net=small_network()
        measured=np.array([0.88,1.,1.10,1.,1.,1.])
        targets,count=select_nearest_controls(
            net,measured,np.array([0.95]*6),np.array([1.05]*6),
            excluded={0},n=2)
        self.assertEqual(count,2)
        self.assertEqual([x["gen_id"] for x in targets],[1,2])
        self.assertEqual([x["target_bus"] for x in targets],[0,2])
        self.assertEqual([x["graph_distance"] for x in targets],[3,1])

    def test_invalid_or_offline_controls_not_made_available(self):
        net=small_network()
        net.gen.at[1,"max_q_mvar"]=math.nan
        net.gen.at[2,"vm_pu"]=1.2
        net.gen.at[3,"in_service"]=False
        self.assertEqual(list(eligible_controls(net,{0})),[])

    def test_reactive_limit_saturation_and_excess_are_distinct(self):
        gen=pd.DataFrame({
            "in_service":[True,True,False],
            "min_q_mvar":[-1.,0.,-1.],
            "max_q_mvar":[1.,2.,1.],
        })
        res_gen=pd.DataFrame({"q_mvar":[-1.,2.5,100.]})
        net=SimpleNamespace(gen=gen,res_gen=res_gen)
        q=q_limit_summary(net)
        self.assertEqual(q["generators_online"],2)
        self.assertEqual(q["generators_with_valid_q_bounds_and_results"],2)
        self.assertEqual(q["q_at_lower_count"],1)
        self.assertEqual(q["q_at_upper_count"],0)
        self.assertEqual(q["q_above_max_count"],1)
        self.assertAlmostEqual(q["q_max_excess_mvar"],0.5)

    def test_json_null_for_missing_physics(self):
        self.assertEqual(json_safe({"failed": math.inf,"xs":[math.nan,2.]}),
                         {"failed":None,"xs":[None,2.]})


if __name__=="__main__":
    unittest.main()
