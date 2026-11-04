"""E-only original frozen R manifest and custody checks: synthetic, no experiments."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from i64_r_off_git_raw_recovery_gate import BUILDS
from test_i64_r_repro_witness_identities import synthetic_witness_rows
from i64_r_e_source_manifest_validation import EXPECTED_KEYS
from i64_r_archived_e_only_attestation import (
    E_RUN_ORIGINAL_SHA256, verify_archived_R_E_lineage,
)


class OriginalREManifestEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.digests={key:'0'*64 for key in EXPECTED_KEYS}
        cls.digests['run']=E_RUN_ORIGINAL_SHA256
        cls.analysis={'e_inputs':cls.digests,'freeze_commit':'original-frozen',
                      'boot':20000,'boot_seed':70,'alpha':0.05}
        cls.check={'e_inputs':cls.digests,
                   'manifest':dict.fromkeys(BUILDS,'original-frozen'),
                   'results':synthetic_witness_rows()}

    def test_original_fixed_manifest_shape_is_valid(self):
        x=verify_archived_R_E_lineage(self.analysis,self.check,E_RUN_ORIGINAL_SHA256)
        self.assertEqual(x['analysis_check_repro_E_sha256_manifest'],'MATCH')
        self.assertIn('NOT_REPLAYED',x['original_R_bootstrap_settings'])

    def test_E_archive_full_digest_must_match_historical_sha(self):
        with self.assertRaisesRegex(ValueError,'full SHA256'):
            verify_archived_R_E_lineage(self.analysis,self.check,'f'*64)

    def test_original_analysis_and_repro_input_sha_must_match(self):
        c=copy.deepcopy(self.check)
        c['e_inputs']['run_part_0']='1'*64
        with self.assertRaisesRegex(ValueError,'digests differ'):
            verify_archived_R_E_lineage(self.analysis,c,E_RUN_ORIGINAL_SHA256)

    def test_original_R_bootstrap_settings_cannot_be_forged(self):
        a=copy.deepcopy(self.analysis)
        a['boot_seed']=9
        with self.assertRaisesRegex(ValueError,'bootstrap settings'):
            verify_archived_R_E_lineage(a,self.check,E_RUN_ORIGINAL_SHA256)

    def test_original_freeze_commit_must_match(self):
        a=copy.deepcopy(self.analysis)
        a['freeze_commit']='different-revision'
        with self.assertRaisesRegex(ValueError,'freeze commit'):
            verify_archived_R_E_lineage(a,self.check,E_RUN_ORIGINAL_SHA256)

    def test_five_original_witnesses_required(self):
        c=copy.deepcopy(self.check)
        c['results'][2]['identical']=False
        with self.assertRaisesRegex(ValueError,'five frozen E'):
            verify_archived_R_E_lineage(self.analysis,c,E_RUN_ORIGINAL_SHA256)

    def test_no_missing_or_extra_sha_manifest_entries(self):
        a=copy.deepcopy(self.analysis)
        del a['e_inputs']['run_part_62']
        with self.assertRaisesRegex(ValueError,'E input digest roster'):
            verify_archived_R_E_lineage(a,self.check,E_RUN_ORIGINAL_SHA256)

    def test_missing_build_manifest_field_rejected(self):
        c=copy.deepcopy(self.check)
        del c['manifest']['r_files']
        with self.assertRaisesRegex(ValueError,'build manifest incomplete'):
            verify_archived_R_E_lineage(self.analysis,c,E_RUN_ORIGINAL_SHA256)


if __name__=='__main__':
    unittest.main()
