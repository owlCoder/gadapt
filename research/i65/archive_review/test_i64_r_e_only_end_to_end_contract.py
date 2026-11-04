"""Integration smoke over 66 entirely synthetic E files. Never runs optimizer or AC."""
from __future__ import annotations
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import i64_r_archived_e_only_attestation as e
from i64_r_off_git_raw_recovery_gate import BUILDS
from i64_r_e_source_manifest_validation import EXPECTED_KEYS, REQUIRED_KEYS


class EOnlyOriginalSourceAuditIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.e = self.root / 'research/results/iteration64_e'
        self.e.mkdir(parents=True)
        self.params = {'cma': {'sigma0': 0.2}, 'ipop': {'sigma0': 0.3},
                       'bipop': {'sigma0': 0.5},
                       'es11': {'sigma0': 0.3, 'up': 1.5, 'stagnation': 100}}
        digests = {}
        for key in sorted(EXPECTED_KEYS - {'run'}):
            p = self.e / (key + '.json.gz')
            raw = gzip.compress(json.dumps({'params': self.params}).encode()) if key == 'freeze' else f'SYNTHETIC:{key}'.encode()
            p.write_bytes(raw)
            digests[key] = hashlib.sha256(raw).hexdigest()
        digests['run'] = e.E_RUN_ORIGINAL_SHA256
        self.digests = digests
        self.analysis = {'e_inputs': digests, 'freeze_commit': 'synthetic-freeze',
                         'boot': 20000, 'boot_seed': 70, 'alpha': 0.05}
        self.check = {'e_inputs': digests, 'manifest': dict.fromkeys(BUILDS, 'synthetic-freeze'),
                      'results': [{'identical': True} for _ in range(5)]}
        (self.e / 'run.json.gz.sha256').write_text(
            e.E_RUN_ORIGINAL_SHA256 + '  research/results/iteration64_e/run.json.gz\n', encoding='ascii')

    def execute(self):
        def pinned(path, blob):
            if blob == e.R_ANALYSIS_BLOB:
                return self.analysis
            if blob == e.R_CHECK_REPRO_BLOB:
                return self.check
            raise AssertionError('Unexpected source blob')
        with patch.object(e, 'read_pinned', side_effect=pinned):
            return e.audit_original_E_only(self.root)

    def test_66_sha_synthetic_files_and_missing_R_never_readied(self):
        x = self.execute()
        self.assertEqual(x['E_inputs']['E_source_sha256_verified_count'], 66)
        self.assertEqual(x['E_inputs']['E_required_source_SHA256_verified'], 44)
        self.assertEqual(len(x['E_inputs']['E_missing_optional_paths']), 1)
        self.assertTrue(x['required_E_sources_SHA256_authenticated_without_R_raw'])
        self.assertFalse(x['E_inputs']['ready_for_independent_raw_seed_bootstrap'])
        self.assertFalse(x['full_E_aggregate_original_file_available_and_attested'])
        self.assertEqual(x['R_original_raw_4200_seed_source'], 'MISSING_NOT_RECREATED')
        self.assertEqual(x['new_optimizer_PF_OPF_COCO_runs'], 0)

    def test_one_required_missing_no_false_completeness(self):
        (self.e / 'run_part_1.json.gz').unlink()
        x = self.execute()
        self.assertEqual(x['E_inputs']['E_source_sha256_verified_count'], 65)
        self.assertEqual(x['E_inputs']['E_required_source_SHA256_verified'], 43)
        self.assertFalse(x['required_E_sources_SHA256_authenticated_without_R_raw'])
        self.assertFalse(x['E_inputs']['ready_for_independent_raw_seed_bootstrap'])

    def test_one_original_optional_tampered_fails(self):
        (self.e / 'run_part_0.json.gz').write_bytes(b'altered synthetic')
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            self.execute()

    def test_missing_original_checksum_marker_fails(self):
        (self.e / 'run.json.gz.sha256').unlink()
        with self.assertRaises(FileNotFoundError):
            self.execute()

    def test_original_digest_file_tampered_fails(self):
        (self.e / 'run.json.gz.sha256').write_text('f'*64+'  research/results/iteration64_e/run.json.gz\n')
        with self.assertRaisesRegex(ValueError, 'Git blob mismatch'):
            self.execute()

    def test_genuine_synthetic_input_e_digest_consensus_required(self):
        self.check = copy.deepcopy(self.check)
        self.check['e_inputs'] = dict(self.check['e_inputs'], run_part_30='f'*64)
        with self.assertRaisesRegex(ValueError, 'digests differ'):
            self.execute()

    def test_untrusted_optional_e_aggregate_is_not_original(self):
        (self.e / 'run.json.gz').write_bytes(b'SYNTHETIC_NOT_ORIGINAL')
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            self.execute()


if __name__ == '__main__':
    unittest.main()
