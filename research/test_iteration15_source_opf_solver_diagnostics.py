"""Iteration 15 raw solver metadata preservation without AC power flow calls."""
import unittest
from research.iteration15_source_opf_solver_diagnostics import (
    safe_raw_termination,finite_or_null
)

class Iteration15DiagnosticTests(unittest.TestCase):
    def test_real_pips_failure_does_not_fake_feasible_physical_values(self):
        raw={"success":False,"raw":{
             "info":-1,
             "output":{"message":"Numerically failed","iterations":6,
                       "hist":[{"feascond":.5,"gradcond":2,"compcond":.7,"costcond":1},
                               {"feascond":.1,"gradcond":4,"compcond":1.1,"costcond":.2}]}}}
        d=safe_raw_termination(raw)
        self.assertEqual(d["raw_info"],-1.)
        self.assertEqual(d["message"],"Numerically failed")
        self.assertEqual(d["iterations"],6)
        self.assertEqual(d["last"]["gradcond"],4)
        self.assertAlmostEqual(d["first"]["feascond"],.5)
        self.assertNotIn("f",d)

    def test_no_raw_data_keeps_numerical_status_unknown(self):
        r=safe_raw_termination({})
        self.assertIsNone(r["raw_info"])
        self.assertIsNone(r["iterations"])
        self.assertIsNone(r["last"])

    def test_nonfinite_values_are_nullable_not_invented(self):
        x={"raw":{"info":float("nan"),"output":{
          "iterations":0,"message":"failed","hist":[{
            "feascond":float("inf"),"gradcond":float("-inf"),
            "compcond":None,"costcond":1.}]}}}
        d=safe_raw_termination(x)
        self.assertIsNone(d["raw_info"])
        self.assertIsNone(d["last"]["feascond"])
        self.assertIsNone(d["last"]["gradcond"])
        self.assertIsNone(d["last"]["compcond"])
        self.assertEqual(d["last"]["costcond"],1.0)
        self.assertIsNone(finite_or_null("not a number"))

if __name__=="__main__":
    unittest.main()
