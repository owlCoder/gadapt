"""Iteration 9 source provenance and strict one-to-one mapping unit tests (0 AC)."""
import unittest
from types import SimpleNamespace

import pandas as pd

from research.iteration9_source_generators import (
    read_sources, index_converted_bus_ids, single_unit_differences, audit,
)

class SourceGeneratorAuditTests(unittest.TestCase):
    def test_verbatim_source_case_counts_and_slack(self):
        gens,bus=read_sources()
        self.assertEqual(len(gens),298)
        self.assertEqual(len(bus),1888)
        self.assertEqual(sum(int(g["gen_status"])==1 for g in gens),291)
        self.assertEqual(sum(int(b["bus_type"])==3 for b in bus.values()),1)
        self.assertEqual(next(i for i,b in bus.items() if int(b["bus_type"])==3),1320)

    def test_converted_bus_name_is_one_based_original(self):
        frame=pd.DataFrame({"name":[0,12,2],"min_vm_pu":[.9]*3,
                            "max_vm_pu":[1.1]*3,"vn_kv":[110.]*3},
                           index=[9,10,12])
        self.assertEqual(index_converted_bus_ids(SimpleNamespace(bus=frame)),
                         {1:9,13:10,3:12})
        frame.at[12,"name"]=12
        with self.assertRaises(ValueError):
            index_converted_bus_ids(SimpleNamespace(bus=frame))

    def test_exact_generator_limits_all_six_fields(self):
        original={"source_row_1based":99,"pg_mw":4,"pmin_mw":1,
          "pmax_mw":8,"qmin_mvar":-2,"qmax_mvar":5,"vg_pu":1.02}
        converted=pd.Series({"p_mw":4,"min_p_mw":1,"max_p_mw":8,
          "min_q_mvar":-2,"max_q_mvar":5,"vm_pu":1.02})
        result=single_unit_differences(original,converted,3)
        self.assertTrue(result["all_within_tolerance"])
        converted["min_q_mvar"]=-1
        result=single_unit_differences(original,converted,3)
        self.assertFalse(result["all_within_tolerance"])
        self.assertAlmostEqual(result["fields"]["qmin_mvar"]["difference"],1)

    def test_ambiguous_units_cannot_be_falsely_called_one_to_one(self):
        gen=pd.DataFrame({"bus":[3],"in_service":[True],"p_mw":[4.],
          "min_p_mw":[1.],"max_p_mw":[8.],"min_q_mvar":[-2.],
          "max_q_mvar":[5.],"vm_pu":[1.02]})
        net=SimpleNamespace(bus=pd.DataFrame({
           "name":[0,1],"vn_kv":[110.,110.],
           "min_vm_pu":[.9,.9],"max_vm_pu":[1.1,1.1]},
           index=[3,4]),
           gen=gen,sgen=pd.DataFrame(columns=["bus","in_service"]),
           ext_grid=pd.DataFrame(columns=["bus","in_service"]))
        original_bus={
           1:{"vmin_pu":.9,"vmax_pu":1.1,"base_kv":110.,"bus_type":1.},
           2:{"vmin_pu":.9,"vmax_pu":1.1,"base_kv":110.,"bus_type":3.},
        }
        row=dict(source_row_1based=1,gen_bus=1,gen_status=1,
                 pg_mw=4,qg_mvar=0,pmin_mw=1,pmax_mw=8,
                 qmin_mvar=-2,qmax_mvar=5,vg_pu=1.02)
        one=audit(net,[row],original_bus)
        self.assertEqual(one["crosswalk"]["one_to_one_compared_count"],1)
        two=audit(net,[row,dict(row,source_row_1based=2)],original_bus)
        self.assertEqual(two["crosswalk"]["one_to_one_compared_count"],0)
        self.assertEqual(two["crosswalk"]["many_to_one_or_ambiguous_bus_count"],1)
        self.assertEqual(two["actual_ac_powerflow_calls"],0)

if __name__=="__main__":
    unittest.main()
