"""Fail-closed regression tests for fresh, date-dependent I55 source report lineage.

Reads ONLY archived-source JSON from the current read-only workflow; does not
run an optimizer, numerical benchmark or physics/COCO calculation.
"""
import hashlib
import json
from pathlib import Path
import unittest

from i55_fresh_original_report_lineage import verify


class FreshOriginalOutputLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = Path('i55_620_original_readonly_audit.json').read_bytes()
        cls.census = Path('i55_620_original_flag_census.json').read_bytes()
        cls.phase = Path('i55_620_npz_phase_duplicate_context.json').read_bytes()

    @staticmethod
    def dump(value):
        return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()

    def derived(self, *, full=None, census=None, phase=None):
        return (self.full if full is None else full,
                self.census if census is None else census,
                self.phase if phase is None else phase)

    def check_fail(self, args, msg):
        with self.assertRaisesRegex(ValueError, msg):
            verify(*args)

    def test_01_real_original_attestation_census_phase_chain_passes(self):
        result = verify(*self.derived())
        self.assertEqual(result['source_620_npz'], 620)
        self.assertEqual(result['original_counts']['both'], 40)

    def test_02_date_only_change_with_fresh_child_sha_is_accepted(self):
        f, c, p = map(json.loads, self.derived())
        f['date'] = '2026-11-05' if f['date'] != '2026-11-05' else '2026-11-06'
        fb = self.dump(f)
        changed_sha = hashlib.sha256(fb).hexdigest()
        c['original_620_full_attestation_sha256'] = changed_sha
        p['full_attestation_json_sha256'] = changed_sha
        r = verify(fb, self.dump(c), self.dump(p))
        self.assertEqual(r['current_full_attestation_sha256'], changed_sha)
        self.assertNotEqual(changed_sha, hashlib.sha256(self.full).hexdigest())

    def test_03_stale_child_hashes_for_new_date_are_rejected(self):
        f = json.loads(self.full)
        f['date'] = '2031-01-01'
        self.check_fail(self.derived(full=self.dump(f)), 'lineage')

    def test_04_original_git_tree_change_rejected(self):
        f = json.loads(self.full)
        f['original_git_tree']['original_root_tree_sha1'] = '0'*40
        self.check_fail(self.derived(full=self.dump(f)), 'Git commit/root tree')

    def test_05_original_git_blob_count_change_rejected(self):
        f = json.loads(self.full)
        f['npz_byte_gate']['raw_bytes_verified'] = 619
        self.check_fail(self.derived(full=self.dump(f)), '620 binary Git blobs')

    def test_06_old_replay_cannot_be_forged_as_success(self):
        f = json.loads(self.full)
        f['original_trace_replay']['npz']['full_raw_trace_pass'] = False
        self.check_fail(self.derived(full=self.dump(f)), 'frozen trace replay')

    def test_07_frozen_c1_census_change_rejected(self):
        c = json.loads(self.census)
        c['overall']['flag_occurrences']['C1'] += 1
        self.check_fail(self.derived(census=self.dump(c)), 'C1/C2')

    def test_08_frozen_c2_duplicate_phase_change_rejected(self):
        p = json.loads(self.phase)
        p['overall']['C1_C2_search'] -= 1
        self.check_fail(self.derived(phase=self.dump(p)), 'Frozen original 620-source population')

    def test_09_different_source_library_total_rejected(self):
        c = json.loads(self.census)
        c['by_library']['baybe']['flagged_cells']['C1'] += 1
        self.check_fail(self.derived(census=self.dump(c)), 'sum mismatch')

    def test_10_missing_function_stratum_rejected(self):
        p = json.loads(self.phase)
        del p['by_function']['sphere']
        self.check_fail(self.derived(phase=self.dump(p)), 'coverage')

    def test_11_not_all_npz_sources_authenticated_rejected(self):
        p = json.loads(self.phase)
        p['all_original_git_blobs_authenticated_again'] = False
        self.check_fail(self.derived(phase=self.dump(p)), 'fully replayed')

    def test_12_unchanged_original_but_forged_manifest_rejected(self):
        c = json.loads(self.census)
        c['original_manifest_git_blob'] = 'f'*40
        self.check_fail(self.derived(census=self.dump(c)), 'manifest identity')


if __name__ == '__main__':
    unittest.main()
