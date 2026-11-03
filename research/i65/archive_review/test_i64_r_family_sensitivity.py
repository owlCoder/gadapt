"""Synthetic unit tests; not a replay of the frozen I64-R primary inputs."""
import copy
import gzip
import json
import math
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i64_r_family_sensitivity as mod


def synthetic_frozen():
    pairs = {}
    for key in mod.EXPECTED_PAIRS:
        pairs[key] = {"shift|gadapt": .7, "shift|ipop": .8,
                      "rot|gadapt": .6, "rot|ipop": .78,
                      "rotm|gadapt": .62, "rotm|ipop": .79}
    full = {"per_pair": pairs, "lower": [0] * 4, "upper": [1] * 4,
            "H64r1": "supported", "H64r2": "supported", "H64r3": "supported",
            "boot": 20_000, "alpha": .05}
    rs = mod.rows_from_frozen(full)
    full["estimates"] = [mod.effect(rs, k) for k in mod.ORIGINAL_CONTRASTS]
    return full


class TestFunctionFamilySensitivity(unittest.TestCase):
    def test_21_cells_roster(self):
        self.assertEqual(len(mod.EXPECTED_PAIRS), 21)
        self.assertEqual(len(mod.FAMILIES), 9)

    def test_weight_by_family(self):
        rows = mod.rows_from_frozen(synthetic_frozen())
        self.assertAlmostEqual(sum(r["weight"] for r in rows), 1)
        for family in mod.FAMILIES:
            self.assertAlmostEqual(sum(r["weight"] for r in rows if r["family"] == family), 1 / 9)

    def test_reconstruct_contrasts(self):
        out = mod.evaluate(synthetic_frozen())
        self.assertAlmostEqual(out["reconstructed_contrasts"]["c1"], .02)
        self.assertAlmostEqual(out["reconstructed_contrasts"]["c2"], .08)
        self.assertAlmostEqual(out["reconstructed_contrasts"]["c3"], .01)
        self.assertAlmostEqual(out["reconstructed_contrasts"]["c4"], .07)

    def test_loo_is_weight_normalized(self):
        x = synthetic_frozen()
        x["per_pair"]["rastrigin|7"]["shift|gadapt"] = 1.0
        x["estimates"] = [mod.effect(mod.rows_from_frozen(x), k) for k in mod.ORIGINAL_CONTRASTS]
        out = mod.evaluate(x)
        row = next(y for y in out["family_leave_one_out"] if y["family"] == "rastrigin")
        self.assertAlmostEqual(row["c4"], .07)
        self.assertAlmostEqual(row["removed_c4_contribution"], (.07 + .07 + .37) / 27)

    def test_loo_dimensions(self):
        out = mod.evaluate(synthetic_frozen())
        expected = {2: 4/9, 7: 7/9, 20: 7/9}
        for entry in out["dimension_leave_one_out"]:
            self.assertAlmostEqual(entry["remaining_weight"], expected[entry["dimension_removed"]])
            self.assertAlmostEqual(entry["c4"], .07)

    def test_21_cell_loo(self):
        out = mod.evaluate(synthetic_frozen())
        self.assertEqual(len(out["cell_leave_one_out"]), 21)
        self.assertTrue(all(abs(y["c4"] - .07) < 1e-12 for y in out["cell_leave_one_out"]))

    def test_reject_roster_change(self):
        x = synthetic_frozen()
        del x["per_pair"]["booth|2"]
        with self.assertRaises(ValueError):
            mod.rows_from_frozen(x)  # already checked by parse_frozen, not rows alone

    def test_detect_registered_contrast_mismatch(self):
        x = synthetic_frozen()
        x["estimates"][3] = -1
        with self.assertRaises(ValueError):
            mod.evaluate(x)

    def test_reject_out_of_range_ecdf(self):
        x = synthetic_frozen()
        x["per_pair"]["beale|2"]["rot|gadapt"] = 1.1
        with self.assertRaises(ValueError):
            mod.rows_from_frozen(x)

    def test_blob_sha(self):
        self.assertEqual(mod.git_blob_sha1(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_gzip_read_fixture_without_pin(self):
        obj = synthetic_frozen()
        with TemporaryDirectory() as d:
            p = Path(d) / "a.json.gz"
            p.write_bytes(gzip.compress(json.dumps(obj).encode()))
            self.assertEqual(len(mod.parse_frozen(p, check_blob=False)["per_pair"]), 21)
            with self.assertRaises(ValueError):
                mod.parse_frozen(p, check_blob=True)


if __name__ == "__main__":
    unittest.main()
