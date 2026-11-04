"""Synthetic original E input custody attestation; never executes a solver."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from i64_r_e_source_manifest_validation import (
    EXPECTED_KEYS, REQUIRED_KEYS, validate_required_e_inputs,
)


class OriginalRInputSecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.e = self.repo / 'research/results/iteration64_e'
        self.e.mkdir(parents=True)
        self.params = {'gadapt': {'test_only_param': 3}, 'ipop': None}
        self.records = [
            {'task': {'k': 0, 'config': 'gadapt', 'seed': 67063001,
                      'params': self.params['gadapt']}},
            {'task': {'k': 0, 'config': 'ipop', 'seed': 67063001,
                      'params': self.params['ipop']}},
        ]
        self.digests = {key: hashlib.sha256(key.encode()).hexdigest()
                        for key in EXPECTED_KEYS}
        for key in REQUIRED_KEYS:
            payload = (gzip.compress(json.dumps({'params': self.params}).encode())
                       if key == 'freeze' else ('TEST_ONLY:' + key).encode())
            (self.e / (key + '.json.gz')).write_bytes(payload)
            self.digests[key] = hashlib.sha256(payload).hexdigest()

    def test_44_required_present_verified_and_no_full_67_claim(self):
        report = validate_required_e_inputs(self.repo, self.digests, self.records)
        self.assertEqual((report['E_original_manifest_entries'],
                          report['required_for_independent_R_seed_bootstrap']), (67, 44))
        self.assertEqual(report['E_required_source_SHA256_verified'], 44)
        self.assertEqual(report['E_source_sha256_verified_count'], 44)
        self.assertEqual(report['E_original_R_tasks_params_matched_to_frozen_E'], 2)
        self.assertFalse(report['ready_for_independent_raw_seed_bootstrap'])
        self.assertFalse(report['E_full_original_input_manifest_present_and_sha256_verified'])
        self.assertEqual(len(report['E_missing_optional_paths']), 23)

    def test_missing_required_input_does_not_grant_ready(self):
        (self.e / 'normalizers.json.gz').unlink()
        report = validate_required_e_inputs(self.repo, self.digests, self.records)
        self.assertFalse(report['ready_for_independent_raw_seed_bootstrap'])
        self.assertEqual(len(report['E_missing_required_paths']), 1)

    def test_tampered_present_required_input_fails_closed(self):
        (self.e / 'run_part_1.json.gz').write_bytes(b'NEW_SYNTHETIC_WRONG_BYTES')
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            validate_required_e_inputs(self.repo, self.digests, self.records)

    def test_tampered_optional_input_fails_closed(self):
        (self.e / 'run_part_0.json.gz').write_bytes(b'NEW_SYNTHETIC_WRONG_BYTES')
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            validate_required_e_inputs(self.repo, self.digests, self.records)

    def test_frozen_algorithm_params_mismatch_fails_closed(self):
        wrong = copy.deepcopy(self.records)
        wrong[1]['task']['params'] = {'fake': 100}
        with self.assertRaisesRegex(ValueError, 'optimizer parameters differ'):
            validate_required_e_inputs(self.repo, self.digests, wrong)

    def test_forged_task_shape_fails_closed(self):
        wrong = copy.deepcopy(self.records)
        wrong[0]['task']['free_additional_field'] = True
        with self.assertRaisesRegex(ValueError, 'task shape'):
            validate_required_e_inputs(self.repo, self.digests, wrong)

    def test_missing_manifest_key_is_not_trusted(self):
        d = dict(self.digests)
        d.pop('freeze')
        with self.assertRaisesRegex(ValueError, '63 parts plus four'):
            validate_required_e_inputs(self.repo, d, self.records)

    def test_not_a_full_digest_is_rejected(self):
        d = dict(self.digests)
        d['run_part_2'] = 'f23046f6...3618'
        with self.assertRaisesRegex(ValueError, 'full 64-hex'):
            validate_required_e_inputs(self.repo, d, self.records)

    def test_optional_extra_present_authenticates_before_full_claim(self):
        path = self.e / 'run.json.gz'
        raw = b'TEST_ONLY_OPTIONAL_AGGREGATE'
        path.write_bytes(raw)
        d = dict(self.digests)
        d['run'] = hashlib.sha256(raw).hexdigest()
        report = validate_required_e_inputs(self.repo, d, self.records)
        self.assertFalse(report['ready_for_independent_raw_seed_bootstrap'])
        self.assertEqual(report['E_source_sha256_verified_count'], 45)
        self.assertFalse(report['E_full_original_input_manifest_present_and_sha256_verified'])

    def test_freeze_absent_blocks_task_provenance(self):
        (self.e / 'freeze.json.gz').unlink()
        report = validate_required_e_inputs(self.repo, self.digests, self.records)
        self.assertFalse(report['ready_for_independent_raw_seed_bootstrap'])
        self.assertEqual(report['E_original_R_tasks_params_matched_to_frozen_E'], 0)


    def test_partial_two_records_cannot_be_ready_even_with_attestation_flag(self):
        report = validate_required_e_inputs(self.repo, self.digests, self.records,
                                            original_r_roster_attested=True)
        self.assertFalse(report['ready_for_independent_raw_seed_bootstrap'])

    def test_complete_synthetic_original_roster_requires_explicit_attestation(self):
        all_rows = [
            {'task': {'k': k, 'config': cfg,
                      'seed': 67_000_000 + 1000*(63+k) + seed_index,
                      'params': self.params[cfg]}}
            for k in range(21) for seed_index in range(1,101)
            for cfg in ('gadapt', 'ipop')
        ]
        self.assertEqual(len(all_rows), 4200)
        no = validate_required_e_inputs(self.repo, self.digests, all_rows)
        self.assertFalse(no['ready_for_independent_raw_seed_bootstrap'])
        yes = validate_required_e_inputs(self.repo, self.digests, all_rows,
                                          original_r_roster_attested=True)
        self.assertTrue(yes['ready_for_independent_raw_seed_bootstrap'])
        self.assertEqual(yes['E_original_R_tasks_params_matched_to_frozen_E'], 4200)

    def test_absent_R_records_can_never_be_ready(self):
        report = validate_required_e_inputs(self.repo, self.digests, [])
        self.assertEqual(report['E_required_source_SHA256_verified'], 44)
        self.assertEqual(report['E_original_R_tasks_params_matched_to_frozen_E'], 0)
        self.assertFalse(report['ready_for_independent_raw_seed_bootstrap'])


if __name__ == '__main__':
    unittest.main()
