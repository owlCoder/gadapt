"""Synthetic regression tests: not a run of the archived ORPD optimizer."""
import copy
import gzip
import json
import math
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0, str(Path(__file__).resolve().parent))
import i64_i2_cell_influence as m


def record(ci, s, config, best, ref=10.):
    return {"task": {"ci": ci, "s": s, "config": config, "seed": m.seed_of(ci,s), "net": "test", "j": ci},
            "ok": True, "calls": m.BUDGET, "r": ref, "best_feasible": best,
            "witness_checked": best is not None, "best_x": None if best is None else [0.1], "events": []}


def fixture_cell(ci, data=None):
    data = data or {"gadapt": 10.1, "ipop": 10.1, "gadapt_hyb": 10.1}
    return m.by_cell({c:[record(ci,s,c,data[c]) for s in range(1,m.N_SEEDS+1)] for c in m.CONFIGS},ci)


class TestI64I2PointRecheck(unittest.TestCase):
    def test_pinned_source_ids(self):
        self.assertEqual(len(m.I_BLOBS), 8)
        self.assertEqual(len(m.I2_BLOBS), 8)
        self.assertTrue(all(len(s) == 40 for s in m.I_BLOBS + m.I2_BLOBS))

    def test_cvar_top_three(self):
        self.assertEqual(m.cv90([0.] * 27 + [1.] * 3), 1.0)
        self.assertAlmostEqual(m.cv90([0.] * 28 + [1.] * 2), 2/3)

    def test_feasible_loss_zero(self):
        self.assertEqual(m.loss_and_feasible(record(0,1,"ipop",10.)), (0.,1))
        v,f = m.loss_and_feasible(record(0,1,"ipop",11.))
        self.assertAlmostEqual(v, 1/11)
        self.assertEqual(f,1)

    def test_infeasible_loss_one(self):
        self.assertEqual(m.loss_and_feasible(record(0,1,"ipop",None)), (1.,0))

    def test_witness_flag_guard(self):
        x=record(0,1,"ipop",None); x["witness_checked"]=True
        with self.assertRaises(ValueError):m.loss_and_feasible(x)
        y=record(0,1,"ipop",10.); y["witness_checked"]=False
        with self.assertRaises(ValueError):m.loss_and_feasible(y)

    def test_by_cell_three_configs(self):
        c=fixture_cell(0)
        self.assertEqual(c["configs"]["gadapt"]["feasible_count"],30)
        self.assertAlmostEqual(c["contrasts"][m.CONTRASTS[2]],0.)

    def test_infeasible_seed_reporting(self):
        v={k:[record(3,s,k,10.) for s in range(1,31)] for k in m.CONFIGS}
        for s in (15, 18, 28):v["gadapt_hyb"][s-1]=record(3,s,"gadapt_hyb",None)
        x=m.by_cell(v,3)
        self.assertEqual(x["configs"]["gadapt_hyb"]["infeasible_seeds"], [68003015,68003018,68003028])

    def test_three_hybrid_failures_saturate(self):
        v={k:[record(0,s,k,10.) for s in range(1,31)] for k in m.CONFIGS}
        for j in (0,1,2):
            v["gadapt_hyb"][j]=record(0,j+1,"gadapt_hyb",None)
        c=m.by_cell(v,0)
        self.assertEqual(c["configs"]["gadapt_hyb"]["cvar90"],1)
        self.assertEqual(c["configs"]["ipop"]["cvar90"],0)
        self.assertEqual(c["contrasts"][m.CONTRASTS[2]],-1)

    def test_reject_duplicate_seed(self):
        v={k:[record(0,s,k,10.) for s in range(1,31)] for k in m.CONFIGS}
        v["ipop"][0]=v["ipop"][1]
        with self.assertRaises(ValueError):m.by_cell(v,0)

    def test_reject_budget_or_seed_deviation(self):
        v={k:[record(0,s,k,10.) for s in range(1,31)] for k in m.CONFIGS}
        v["gadapt"][0]["calls"]-=1
        with self.assertRaises(ValueError):m.by_cell(v,0)

    def test_reject_unmatched_network(self):
        v={k:[record(0,s,k,10.) for s in range(1,31)] for k in m.CONFIGS}
        v["ipop"][0]["task"]["net"]="wrong"
        with self.assertRaises(ValueError):m.by_cell(v,0)

    def test_aggregate_and_loo(self):
        cells=[fixture_cell(i) for i in range(8)]
        # One cell worsens the hybrid tail by 1.0.
        v={k:[record(3,s,k,10.) for s in range(1,31)] for k in m.CONFIGS}
        for j in (0,1,2):v["gadapt_hyb"][j]=record(3,j+1,"gadapt_hyb",None)
        cells[3]=m.by_cell(v,3)
        out=m.summarize(cells)
        self.assertAlmostEqual(out["contrasts_from_original_run_records"][m.CONTRASTS[2]], -1/8)
        self.assertEqual(out["dominant_cell"]["index"],3)
        self.assertAlmostEqual(out["dominant_cell"]["mean_without_this_cell"],0)

    def test_reject_aggregate_tampering(self):
        cells=[fixture_cell(i) for i in range(8)]
        x=m.summarize(cells)
        f={"aggregate":x["aggregate_from_original_run_records"],"contrasts":{k:{"estimate":v} for k,v in x["contrasts_from_original_run_records"].items()}}
        self.assertEqual(m.summarize(cells,f)["aggregate_from_original_run_records"],f["aggregate"])
        f["aggregate"]["ipop"]["P"] += 0.001
        with self.assertRaises(ValueError):m.summarize(cells,f)

    def test_checksum(self):
        self.assertEqual(m.git_blob_sha1(b"hello\n"),"ce013625030ba8dba906f756967f9e9ca394464a")

    def test_full_roster_required(self):
        with self.assertRaises(ValueError):m.summarize([fixture_cell(i) for i in range(7)])


if __name__ == "__main__":unittest.main()
