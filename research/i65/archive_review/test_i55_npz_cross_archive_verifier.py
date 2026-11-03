"""Offline synthetic tests for read-only verifier; no optimizer or network."""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
from i55_npz_cross_archive_verifier import (
    sequence_hash, classify_arrays, replay_npz, paired_i50_i55,
    posthoc_diagnostic, blob_sha
)


class I55ArchiveVerifierTests(unittest.TestCase):
    def arrays(self):
        x = np.array([[0.0, 0.0], [0.0, 0.0], [-5., -5.], [6., 0.]], dtype=np.float64)
        f = np.array([1.0, 1.0, 3.0, -2.0], dtype=np.float64)
        phase = np.array([0, 0, 1, 0], dtype=np.int8)
        return x, f, phase

    def test_sequence_hash_reimplements_synthetic_reference(self):
        import hashlib
        x, f, phase = self.arrays()
        manual = hashlib.sha256()
        for row, value, ph in zip(x, f, phase):
            manual.update(row.tobytes())
            manual.update(repr(float(value)).encode())
            manual.update(b'search' if ph == 0 else b'post')
        self.assertEqual(sequence_hash(x, f, phase), manual.hexdigest())

    def test_sequence_hash_changes_on_value_and_phase(self):
        x, f, phase = self.arrays()
        baseline = sequence_hash(x, f, phase)
        f[0] += 0.5
        self.assertNotEqual(sequence_hash(x, f, phase), baseline)
        f[0] -= 0.5
        phase[0] = 1
        self.assertNotEqual(sequence_hash(x, f, phase), baseline)

    def test_classifier_duplicates_out_of_bounds_corner_post(self):
        x, f, phase = self.arrays()
        result = classify_arrays(x, f, phase, np.array([0.0, 0.0]), 1.0, 2, 2)
        self.assertEqual(result['C1'], 1)
        self.assertEqual(result['C2'], 1)
        self.assertEqual(result['C3'], 1)
        self.assertEqual(result['C4'], 2)
        self.assertEqual(result['C5'], 1)
        self.assertEqual(result['R1'], 0)
        self.assertEqual(result['R2'], 0)
        self.assertEqual(result['R3'], 1)
        self.assertEqual(result['D2'], 1)

    def test_classifier_no_reported_result(self):
        x, f, phase = self.arrays()
        result = classify_arrays(x, f, phase, np.zeros(0), None, None, None)
        self.assertEqual([result[t] for t in ('R1', 'R2', 'R3', 'D2')], [0, 0, 0, 0])

    def test_npz_replay_from_real_numpy_fixture(self):
        x, f, phase = self.arrays()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'sphere_2_6000.npz'
            np.savez_compressed(p, x=x, f=f, phase=phase,
                                x_star=np.array([0., 0.]), f_star=np.array([1.0]),
                                reported_evals=np.array([2]), documented_max=np.array([2]))
            flags = classify_arrays(x, f, phase, np.array([0., 0.]), 1., 2, 2)
            cell = {'d': 2, 'calls': 4, 'hash': sequence_hash(x, f, phase), 'flags': flags}
            report = replay_npz(p, cell)
            self.assertEqual(report['flag_mismatches'], {})
            self.assertEqual(report['repeated_count'], 1)
            with patch.dict(cell, {'hash': 'f' * 64}):
                with self.assertRaisesRegex(ValueError, 'hash'): replay_npz(p, cell)

    def test_npz_rejects_bad_phase(self):
        x, f, phase = self.arrays()
        phase[0] = 7
        with self.assertRaisesRegex(ValueError, 'phase'):
            sequence_hash(x, f, phase)

    def test_paired_missing_and_unequal(self):
        k = [('sphere', 2, i) for i in (6000, 6001, 6002)]
        old = {'a': {'cells': [{'function': v[0], 'd': v[1], 'seed': v[2],
                               'hash': str(i), 'error': 'timeout' if i == 2 else None}
                              for i, v in enumerate(k)]}}
        new = {'a': {'cells': [{'function': v[0], 'd': v[1], 'seed': v[2],
                               'hash': 'different' if i == 1 else str(i), 'error': None}
                              for i, v in enumerate(k)]}}
        # Fixture has 3, not the frozen 30-cell roster: hard-fail instead of diluting denominator.
        with self.assertRaisesRegex(ValueError, 'roster'):
            paired_i50_i55(old, new)

    def test_paired_30_cell_digest_denominator_and_timeout(self):
        cells = [('sphere', 2, 6000 + i) for i in range(30)]
        def row(k, digest, err=None):
            return {'function': k[0], 'd': k[1], 'seed': k[2], 'hash': digest, 'error': err}
        older = {'unit_lib': {'cells': [row(k, str(i), 'timeout' if i == 29 else None)
                                        for i, k in enumerate(cells)]}}
        newer = {'unit_lib': {'cells': [row(k, 'changed' if i == 28 else str(i))
                                        for i, k in enumerate(cells)]}}
        result = paired_i50_i55(older, newer)
        self.assertEqual(result['totals'], {'same': 28, 'different': 1,
                                            'skipped': 1, 'comparison_valid': 29})
        self.assertEqual(result['skipped'][0]['i50_error'], 'timeout')
        self.assertEqual(result['different_by_library']['unit_lib'], [['sphere', 2, 6028]])

    def test_posthoc_checks_digest_not_claimed_boolean(self):
        def c(h): return {'function': 'plateau', 'd': 2, 'seed': 6001, 'hash': h}
        old, new = {'cells': [c('original')]}, {'cells': [c('different')]}
        diag = {'cells': [dict(c('original'), veclib_threads=1, matches_i50_archive=False)]}
        out = posthoc_diagnostic(old, new, diag)
        self.assertEqual(out['count'], 1)
        self.assertTrue(out['cases'][0]['matches_original_i50'])
        self.assertFalse(out['all_10_match_i50_and_differ_i55'])

    def test_blob_checksum(self):
        self.assertEqual(blob_sha(b'abc'), 'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f')


if __name__ == '__main__':
    unittest.main()
