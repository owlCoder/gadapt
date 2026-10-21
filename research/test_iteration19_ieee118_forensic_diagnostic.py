"""Iteration19 forensic source/offender diagnostics tests. ZERO true AC calls."""
import unittest
import numpy as np

from research.iteration19_ieee118_forensic_diagnostic import (
    source_vectors_and_preflight,top_generator_violations,
    top_voltage_violations,branch_terminal_source_limits,
)
from research.iteration18_ieee118_gadapt_transfer import IEEE118NineControlSubset


class ForensicNoACUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system=IEEE118NineControlSubset()

    def test_archived_nine_physical_source_vectors_and_initial(self):
        original,candidates=source_vectors_and_preflight()
        self.assertEqual(original.shape,(9,))
        self.assertEqual(len(candidates),9)
        self.assertEqual(sorted({z[0] for z in candidates}),[2026,2027,2028])
        self.assertEqual(self.system.real_ac_calls,0)

    def test_q_offender_row_bus_min_max_not_average(self):
        source=self.system.source["gen"].copy()
        solved=source.copy()
        solved[0,2]=source[0,4]-12.
        r=top_generator_violations(solved,source,"Q")
        self.assertGreaterEqual(r["count"],1)
        self.assertEqual(r["top_12"][0]["generator_row_1based"],1)
        self.assertEqual(r["top_12"][0]["bus_id"],1)
        self.assertGreaterEqual(r["top_12"][0]["below"],12.-1e-9)
        self.assertEqual(self.system.real_ac_calls,0)

    def test_generator_P_violations_separate_from_Q(self):
        source=self.system.source["gen"].copy()
        solved=source.copy()
        solved[1,1]=source[1,8]+22.
        r=top_generator_violations(solved,source,"P")
        self.assertTrue(any(z["generator_row_1based"]==2 and z["above"]>21.99
                            for z in r["top_12"]))

    def test_voltage_offender_original_bus_id(self):
        original=self.system.source["bus"].copy()
        solved=original.copy()
        solved[3,7]=original[3,12]-.025
        out=top_voltage_violations(solved,original)
        self.assertTrue(any(z["bus_id"]==4 and z["below_pu"]>.024
                            for z in out["top_12"]))

    def test_original_unrated_source_rate_a_not_thermal_violation(self):
        original=self.system.source["branch"].copy()
        fake=np.pad(original,((0,0),(0,4)))
        rated=np.flatnonzero((original[:,5]>0)&(original[:,10]>0))
        unrated=np.flatnonzero((original[:,5]==0)&(original[:,10]>0))
        self.assertGreater(len(rated),0)
        j=int(rated[0])
        fake[j,15]=original[j,5]+10.
        if len(unrated):
            fake[int(unrated[0]),13]=5000.
        out=branch_terminal_source_limits(fake,original)
        self.assertTrue(any(x["branch_row_1based"]==j+1 for x in out["top_12"]))
        self.assertEqual(out["violated_branches"],1)
        self.assertGreaterEqual(out["total_excess_mva"],10.)

    def test_pypower_original_source_is_not_mutated_by_tests(self):
        self.assertEqual(len(self.system.source["gen"]),54)
        self.assertEqual(int(self.system.source["gen"][29,0]),69)
        self.assertEqual(self.system.real_ac_calls,0)

if __name__=="__main__":
    unittest.main()
