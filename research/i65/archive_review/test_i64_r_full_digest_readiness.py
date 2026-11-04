"""Synthetic-only I64-R off-Git full-digest readiness gate tests.

No optimizer, physics, PF/OPF, COCO, real R data or bootstrap invoked.
The structural parser is mocked ONLY to isolate digest readiness policy.
"""
from __future__ import annotations
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import i64_r_off_git_raw_recovery_gate as gate


class FullDigestReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = self.root / 'synthetic_r_not_original.json.gz'
        self.raw.write_bytes(gzip.compress(json.dumps({
            'e_inputs': {'synthetic_key': '0'*64},
            'records': [{'synthetic_only': True}],
            'manifest': {'synthetic_only': True},
        }).encode()))
        self.sha = hashlib.sha256(self.raw.read_bytes()).hexdigest()

    def invoke(self, full_digest=None):
        def check_e_only(root, digests, records, *,
                         original_r_roster_attested=False):
            return {
                'E_missing_required_paths': [],
                'ready_for_independent_raw_seed_bootstrap':
                    original_r_roster_attested,
            }
        with patch.object(gate, 'HISTORICAL_SHA256_PREFIX', self.sha[:8]), \
             patch.object(gate, 'HISTORICAL_SHA256_SUFFIX', self.sha[-4:]), \
             patch.object(gate, 'read_pinned', side_effect=[
                 {'synthetic': 'analysis'}, {'synthetic': 'repro'}]), \
             patch.object(gate, 'validate_r_records',
                          return_value={'records_checked': 4200}), \
             patch.object(gate, 'verify_lineage',
                          return_value={'synthetic': 'lineage'}), \
             patch.object(gate, 'validate_required_e_inputs',
                          side_effect=check_e_only):
            return gate.audit(repo_root=self.root, raw_run_path=self.raw,
                              expected_full_sha256=full_digest)

    def test_truncated_48_bit_digest_never_grants_readiness(self):
        result = self.invoke()
        self.assertEqual(result['status'], 'STRUCTURE_MATCHES_ARCHIVED_R_SPEC')
        self.assertFalse(result['trusted_full_digest_confirmed'])
        self.assertFalse(result['ready_for_independent_raw_seed_bootstrap'])
        self.assertIn('48_BIT', result['digest_authentication'])
        self.assertTrue(result['original_R_raw_full_digest_required_for_readiness'])

    def test_matching_explicit_full_digest_permits_structural_readiness(self):
        result = self.invoke(self.sha)
        self.assertTrue(result['trusted_full_digest_confirmed'])
        self.assertTrue(result['ready_for_independent_raw_seed_bootstrap'])
        self.assertEqual(result['digest_authentication'], 'FULL_TRUSTED_MATCH')
        self.assertNotIn('bootstrap_replay', result)

    def test_wrong_64_hex_full_digest_fails_closed(self):
        mismatch = ('0' if self.sha[0] != '0' else '1') + self.sha[1:]
        with self.assertRaisesRegex(ValueError, 'FULL trusted SHA256'):
            self.invoke(mismatch)

    def test_abbreviated_full_digest_string_fails_closed(self):
        with self.assertRaisesRegex(ValueError, '64 lowercase'):
            self.invoke(self.sha[:8] + '...' + self.sha[-4:])

    def test_absent_raw_is_not_a_verified_original(self):
        self.raw.unlink()
        result = gate.audit(repo_root=self.root, raw_run_path=self.raw)
        self.assertEqual(result['status'], 'NOT_AVAILABLE_ON_THIS_FILESYSTEM')
        self.assertEqual(result['bootstrap_replay'], 'BLOCKED_ON_ORIGINAL_RAW_R')


if __name__ == '__main__':
    unittest.main()
