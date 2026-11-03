"""Local synthetic / exact-arithmetic tests; no physical simulation."""
import unittest
from pathlib import Path

import numpy as np

import i64_i2_rare_failure_audit as rf


class RareFailureAuditTests(unittest.TestCase):
    def test_clopper_pearson_zero_of_thirty(self):
        low,high=rf.clopper_pearson(0,30)
        self.assertEqual(low,0.0)
        self.assertAlmostEqual(high,0.11570330822202778,places=12)

    def test_clopper_pearson_three_of_thirty(self):
        low,high=rf.clopper_pearson(3,30)
        self.assertAlmostEqual(low,0.02111713702972257,places=12)
        self.assertAlmostEqual(high,0.2652884504742081,places=12)

    def test_clopper_pearson_all_thirty(self):
        low,high=rf.clopper_pearson(30,30)
        self.assertAlmostEqual(low,0.8842966917779722,places=12)
        self.assertEqual(high,1.)

    def test_clopper_pearson_invalid(self):
        for k,n in [(31,30),(-1,30),(0,0)]:
            with self.assertRaises(ValueError):rf.clopper_pearson(k,n)

    def test_exact_paired_mcnemar_three_vs_zero(self):
        a=np.ones(30);b=np.ones(30);a[[14,17,27]]=0
        result=rf.exact_paired_feasibility_test(a,b)
        self.assertEqual(result['discordant_pairs'],3)
        self.assertEqual(result['hybrid_only_feasible'],0)
        self.assertEqual(result['ipop_only_feasible'],3)
        self.assertEqual(result['mcnemar_two_sided_exact_p'],0.25)
        self.assertEqual(result['one_sided_more_ipop_feasible_p'],0.125)

    def test_paired_mcnemar_identical(self):
        a=b=np.ones(30)
        self.assertEqual(rf.exact_paired_feasibility_test(a,b)['mcnemar_two_sided_exact_p'],1.0)

    def test_cvar_tail_count(self):
        l=np.zeros((8,3,30));l[3,1,[14,17,27]]=1
        self.assertAlmostEqual(rf.cvar_by_config(l,3)[1],1/8)
        self.assertAlmostEqual(rf.cvar_by_config(l,6)[1],0.5/8)

    def test_validate_derived_shape(self):
        with self.assertRaises(ValueError):rf.validate(np.zeros((8,3,29)),np.zeros((8,3,29)))

    def test_validate_nonfeasible_loss(self):
        l=np.zeros((8,3,30));f=np.ones_like(l);f[3,1,0]=0
        with self.assertRaises(ValueError):rf.validate(l,f)

    def obtain_arrays(self):
        local=Path(__file__).with_name('i64_i2_archived_losses_derived_2026-11-03.npz')
        if local.exists(): return rf.load_derived(local)
        root=Path(__file__).resolve().parents[3]
        if (root/'research/results/iteration64_i/run_part_0.json.gz').exists():
            return rf.load_archived(root)
        self.skipTest('pinned original archive and optional derived fixture are unavailable')

    def test_archived_fixture_original_c3(self):
        loss,feasible=self.obtain_arrays()
        self.assertAlmostEqual(rf.cvar_by_config(loss,3)[2]-rf.cvar_by_config(loss,3)[1],rf.REG_C3,places=14)

    def test_original_seed68_bootstrap_replay(self):
        loss,feasible=self.obtain_arrays()
        out=rf.boot_endpoints(loss,feasible,seed=68,repetitions=20000)
        self.assertAlmostEqual(out['tstar'],rf.REG_TSTAR,places=10)
        self.assertAlmostEqual(out['c3_upper_simultaneous'],rf.REG_UPPER,places=10)


if __name__=='__main__':unittest.main()
