"""Source-only original five-E-check_repro-witness tamper tests. No experiments."""
import copy
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from i64_r_off_git_raw_recovery_gate import (
    FROZEN_E_REPRO_WITNESSES, verify_frozen_five_e_repro_witnesses,
)

EXPECTED_ORIGINAL_SOURCE_ROWS = (
    (1, ['sphere', 2, 'shift'], 'gadapt'),
    (2, ['sphere', 2, 'rot'], 'gadapt'),
    (2, ['sphere', 2, 'rot'], 'ipop'),
    (28, ['ackley', 2, 'shift'], 'gadapt'),
    (29, ['ackley', 2, 'rot'], 'ipop'),
)


def synthetic_witness_rows():
    return [
        {'cell': cell, 'cell_def': list(cell_def), 'config': cfg,
         'old': 1.0 + i / 100, 'new': 1.0 + i / 100, 'identical': True}
        for i, (cell, cell_def, cfg) in enumerate(EXPECTED_ORIGINAL_SOURCE_ROWS)
    ]


class OriginalFiveEReproIdentityGateTests(unittest.TestCase):
    def setUp(self):
        self.good = {'results': synthetic_witness_rows()}

    def changed(self, mutate):
        c = copy.deepcopy(self.good)
        mutate(c['results'])
        return c

    def reject(self, message, mutate):
        with self.assertRaisesRegex(ValueError, message):
            verify_frozen_five_e_repro_witnesses(self.changed(mutate))

    def test_original_predeclared_five_exact_identities(self):
        self.assertEqual(FROZEN_E_REPRO_WITNESSES, EXPECTED_ORIGINAL_SOURCE_ROWS)
        self.assertEqual(verify_frozen_five_e_repro_witnesses(self.good), 5)

    def test_wrong_cell_with_all_flags_true(self):
        self.reject('cell/config/order', lambda rows: rows[0].update(cell=20))

    def test_reordered_witnesses_with_all_flags_true(self):
        self.reject('cell/config/order', lambda rows: rows.reverse())

    def test_duplicated_witness_with_all_flags_true(self):
        self.reject('cell/config/order', lambda rows: rows.__setitem__(2, rows[1].copy()))

    def test_wrong_transform_in_cell_definition(self):
        self.reject('cell/config/order', lambda rows: rows[4]['cell_def'].__setitem__(2, 'shift'))

    def test_wrong_algorithm_for_frozen_cell(self):
        self.reject('cell/config/order', lambda rows: rows[3].update(config='ipop'))

    def test_missing_saved_old_value(self):
        self.reject('schema mismatch', lambda rows: rows[1].pop('old'))

    def test_forged_reproduction_best_value(self):
        self.reject('old/new value mismatch', lambda rows: rows[2].update(new=0.001))

    def test_nonfinite_reproduction_best_value(self):
        self.reject('old/new value mismatch', lambda rows: rows[2].update(old=math.nan, new=math.nan))

    def test_false_reproduction_flag(self):
        self.reject('cell/config/order', lambda rows: rows[1].update(identical=False))

    def test_boolean_best_value(self):
        self.reject('old/new value mismatch', lambda rows: rows[1].update(old=True, new=True))

    def test_missing_fifth_witness(self):
        self.reject('incomplete', lambda rows: rows.pop())


if __name__ == '__main__':
    unittest.main()
