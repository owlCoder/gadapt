"""Synthetic adversarial tests: these are NOT replay tests of original NPZ bytes."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i55_181_npz_evidence_reconcile as r


def fixture():
    libs=frozenset(("baybe","evox"))
    before=[f"research/results/iteration55/traces/prior/prior_{i:03d}.npz" for i in range(55)]
    manifest={"schema":"I65_I55_ORIGINAL_NPZ_GIT_TREE_V1","original_source_commit":r.SOURCE_SHA,
              "entries":[{"path":p,"git_blob_sha1":f"{k:040x}","size":100} for k,p in enumerate(before)]}
    prior={"prior_five_source_paths":before[:5],"new_fifty_source_paths":before[5:],
           "prior_original_npz_replayed":5,"new_valid_npz":50,
           "cumulative_original_evaluations_recomputed":24298}
    original={}
    batches=[]
    for j,lib in enumerate(sorted(libs),1):
        orig=[]
        for fn in ("sphere","rastrigin","plateau"):
            for dim in (2,10):
                for seed in range(6000,6005):
                    orig.append(dict(library=lib,function=fn,d=dim,seed=seed,error=None,
                                     hash="a"*64,flags={k:0 for k in ("C1","C2","C3","C4","C5","R1","R2","R3","D2")},calls=200))
        original[lib]={"cells":orig}
        records=[]
        for i,fn in enumerate(("sphere","rastrigin","plateau"),1):
            dim=2 if i!=2 else 10
            path=f"{r.BASE}{lib}/{fn}_{dim}_6003.npz"
            sha=f"{j*10+i:040x}"
            manifest["entries"].append({"path":path,"git_blob_sha1":sha,"size":1300})
            records.append(dict(path=path,library=lib,function=fn,d=dim,seed=6003,pass_=True,
                                source_git_blob_sha1=sha,source_binary_size=1300,
                                objective_calls_rechecked=200,objective_mismatches=0,
                                archived_trace_sha256="a"*64,recomputed_trace_sha256="a"*64,
                                trace_sha256_match=True,recomputed_flags_match=True,
                                original_flag_counts=orig[0]["flags"],
                                float32_recorder=lib=="evox",
                                float64_wrong_policy_rejections=40 if lib=="evox" else 0))
            records[-1]["pass"]=records[-1].pop("pass_")
        batches.append({"batch_library":lib,"iteration_batch":j,"original_commit":r.SOURCE_SHA,
                        "manifest_blob":r.MANIFEST_SHA,"engine_git_blob":r.ENGINE_SHA,
                        "files_requested":3,"replayed":3,"failed":0,"objective_calls":600,
                        "float32_calls":600 if lib=="evox" else 0,
                        "float64_wrong_policy_rejections":120 if lib=="evox" else 0,
                        "results":records,"no_new_optimizers":True,"full_original_620_replayed":False})
    return manifest,prior,batches,original,libs


def run(data):
    m, p, b, c, ls=data
    return r.reconcile(m,p,b,c,expected_libraries=ls,per_library=3,original_total=61)


class LedgerTests(unittest.TestCase):
    def test_healthy_evidence(self):
        got=run(fixture())
        self.assertTrue(got["reconciliation_pass"])
        self.assertEqual(got["new_replays"],6)
        self.assertEqual(got["original_replayed_cumulative"],61)
        self.assertEqual(got["new_original_calls"],1200)
        self.assertEqual(got["new_float32_objective_calls"],600)
        self.assertEqual(got["wrong_float64_policy_false_rejections"],120)

    def test_duplicate_path_rejected(self):
        f=fixture(); f[2][0]["results"][1]["path"]=f[2][0]["results"][0]["path"]
        with self.assertRaisesRegex(r.ReconciliationError,"Duplicate"):
            run(f)

    def test_prior_overlap_rejected(self):
        f=fixture(); path=f[2][0]["results"][0]["path"]
        f[1]["prior_five_source_paths"][0]=path
        with self.assertRaisesRegex(r.ReconciliationError,"Duplicate"):
            run(f)

    def test_archive_blob_identity_mismatch(self):
        f=fixture(); f[2][1]["results"][0]["source_git_blob_sha1"]="f"*40
        with self.assertRaisesRegex(r.ReconciliationError,"original blob mismatch"):
            run(f)

    def test_original_cell_trace_hash_mismatch(self):
        f=fixture(); f[2][0]["results"][0]["recomputed_trace_sha256"]="b"*64
        with self.assertRaisesRegex(r.ReconciliationError,"SHA256"):
            run(f)

    def test_original_detector_flag_mismatch(self):
        f=fixture(); f[2][0]["results"][0]["original_flag_counts"]["C1"]=1
        with self.assertRaisesRegex(r.ReconciliationError,"detector flag"):
            run(f)

    def test_replay_declared_failure_rejected(self):
        f=fixture(); f[2][0]["results"][0]["objective_mismatches"]=1
        with self.assertRaisesRegex(r.ReconciliationError,"numerical or detector"):
            run(f)

    def test_wrong_numeric_precision_rejected(self):
        f=fixture(); f[2][1]["results"][0]["float32_recorder"]=False
        with self.assertRaisesRegex(r.ReconciliationError,"precision"):
            run(f)

    def test_batch_sum_inflation_rejected(self):
        f=fixture(); f[2][1]["objective_calls"]+=100
        with self.assertRaisesRegex(r.ReconciliationError,"call aggregate"):
            run(f)

    def test_batch_id_gap_rejected(self):
        f=fixture(); f[2][1]["iteration_batch"]=5
        with self.assertRaisesRegex(r.ReconciliationError,"batch ID"):
            run(f)

    def test_missing_function_fails(self):
        f=fixture(); d=f[2][0]["results"][2]
        d["path"]=d["path"].replace("plateau", "sphere")
        with self.assertRaises(r.ReconciliationError):
            run(f)

    def test_source_commit_mutant_fails(self):
        f=fixture(); f[0]["original_source_commit"]="0"*40
        with self.assertRaisesRegex(r.ReconciliationError,"source commit"):
            run(f)

    def test_fake_pass_evidence_without_archive_source_fails(self):
        f=fixture(); f[2][0]["results"][0]["path"]=f"{r.BASE}baybe/sphere_2_6004.npz"
        with self.assertRaisesRegex(r.ReconciliationError,"non-original"):
            run(f)

    def test_omitted_library_fails(self):
        f=fixture(); f[2].pop()
        with self.assertRaisesRegex(r.ReconciliationError,"Missing or extra"):
            run(f)


if __name__=="__main__":
    unittest.main()
