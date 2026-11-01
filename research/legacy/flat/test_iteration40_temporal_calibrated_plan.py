"""I40 finite-sample order statistic + source-capacity containment unit tests.

All networks/traffic here are SYNTHETIC; no SNDlib fetch, no MILP benchmark.
"""
import unittest
import numpy as np
from research.test_iteration39_source_modular_capacity import tiny
from research.iteration40_temporal_calibrated_plan import (
    calibrated_policies, order_stat_threshold, modular_cover, network_loads)


class I40NoSourceOptimizationTests(unittest.TestCase):
    def test_64_sample_quantile_rank_59_and_1_frame_feasibility_containment(self):
        s=np.asarray([.45]*60+[1.45]*4)
        q,k=order_stat_threshold(s,alpha=.10)
        self.assertEqual(k,59)
        self.assertAlmostEqual(q,.45)
        self.assertAlmostEqual(k/65,59/65)
        self.assertLessEqual(int(np.sum(s>q)),64-k)

    def test_calibration_never_uses_unseen_test_and_source_cost_matches_modules(self):
        # One original unsplittable A->C directed pair on an explicit 3-link toy.
        # FIT peak 10; CAL 60x19 + 4x39; HOLDOUT 3x28.
        f=np.asarray([[10.]]*128 + [[19.]]*60 + [[39.]]*4 + [[28.]]*3)
        model=tiny(f[:128])
        a=calibrated_policies(model,[0],f,fit=128,cal=64,alpha=.10)
        pol=a["policies"]
        self.assertEqual(set(pol),{
            "fit_only","calibrated_90_relative","calibrated_90_absolute",
            "calibration_max_relative","fit_plus_cal_per_edge_max"})
        self.assertEqual(a["calibration_score_summary"]["rank_k"],59)
        self.assertEqual(pol["fit_only"]["cost"],12.)
        self.assertEqual(pol["calibrated_90_relative"]["cost"],12.)
        self.assertEqual(pol["calibrated_90_relative"]["evaluation"]["calibration"]["violating_slices"],4)
        self.assertEqual(pol["calibrated_90_relative"]["evaluation"]["holdout"]["violating_slices"],3)
        self.assertEqual(pol["calibration_max_relative"]["cost"],18.)
        self.assertEqual(pol["calibration_max_relative"]["evaluation"]["holdout"]["violating_slices"],0)
        self.assertEqual(pol["fit_plus_cal_per_edge_max"]["cost"],18.)

        # Alter ONLY held-out values; the built frozen plans MUST not change.
        g=f.copy()
        g[192:]=100000.
        later=calibrated_policies(model,[0],g,fit=128,cal=64,alpha=.10)
        for k in pol:
            self.assertEqual(pol[k]["cost"],later["policies"][k]["cost"])
            self.assertEqual(pol[k]["installed_capacity"],later["policies"][k]["installed_capacity"])
        self.assertGreater(later["policies"]["calibrated_90_relative"]["evaluation"]["holdout"]["max_source_unit_excess"],1.)

    def test_source_capacity_ceiling_20_40_and_fixed_route(self):
        p=tiny([[1.]])
        m=modular_cover(p,[0.,0.,41.])
        self.assertEqual(m["modules_20"],[0,0,1])
        self.assertEqual(m["modules_40"],[0,0,1])
        self.assertEqual(m["installed_capacity"],[0.,0.,60.])
        self.assertEqual(m["cost"],30.) # toy link AC: 20@12 + 40@18
        matrix=np.array([[1.],[2.]])
        first,used=network_loads(p,[0],matrix)
        second,_=network_loads(p,[1],matrix)
        self.assertEqual(first[:,2].tolist(),[1.,2.])
        self.assertEqual(second[:,2].tolist(),[0.,0.])
        self.assertEqual(used.tolist(),[False,False,True])

    def test_invalid_score_and_nonfinite_capacity_do_not_pass(self):
        for v in ([np.nan],[float("inf")],[],[-0.1]):
            with self.assertRaises(ValueError):
                order_stat_threshold(v)
        p=tiny([[1.]])
        with self.assertRaises(ValueError):
            modular_cover(p,[0.,0.,float("nan")])
        with self.assertRaises(ValueError):
            network_loads(p,[0.5],[[1.]])

    def test_quantile_out_of_range_is_infinite_not_invented(self):
        val,k=order_stat_threshold([0,1],alpha=.10)
        self.assertEqual(k,3)
        self.assertEqual(val,float("inf"))


if __name__=="__main__":
    unittest.main()
