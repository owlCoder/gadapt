"""Pure statistical regression tests for iteration 7, independent of AC."""
import math
import tempfile
from pathlib import Path
import unittest

from research.analyze_iteration7_source_rated import (
    sign_p, holm, wilson, records, analyze
)

class StatsTests(unittest.TestCase):
    def test_exact_sign_p_and_holm(self):
        self.assertEqual(sign_p(3,0),.25)
        self.assertEqual(sign_p(0,0),1.)
        self.assertEqual(sign_p(2,1),1.)
        self.assertEqual(holm([.25,.5,1.,1.]),[1.,1.,1.,1.])

    def test_wilson_small_sample_is_wide(self):
        self.assertAlmostEqual(wilson(0,3)[1],0.561497,places=5)
        self.assertAlmostEqual(wilson(3,3)[0],0.438503,places=5)

    def test_csv_requires_fifteen_real_preregistered_runs(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"not_15.csv"
            p.write_text("method,seed\ngadapt_penalty,350\n")
            with self.assertRaises(ValueError):
                records(p)

    def test_infeasible_records_not_silently_assigned_loss(self):
        rows=[]
        from research.analyze_iteration7_source_rated import METHODS
        for method in METHODS:
            for seed in (350,351,352):
                rows.append({"method":method,"seed":seed,
                             "feasible":False,"violation":1.,
                             "loss":None,"failures":0,"calls":72,
                             "runtime":.1,"optimizer_completed":True})
        summary,pairs=analyze(rows)
        self.assertEqual(len(summary),5)
        self.assertTrue(all(v["median_best_feasible_loss_mw"]==""
                            for v in summary))
        self.assertTrue(all(c["holm_4_p"]==1. for c in pairs))


if __name__=="__main__":
    unittest.main()
