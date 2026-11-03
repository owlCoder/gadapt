"""Pure synthetic tests for I55 archival recheck; no historic tests are executed."""
import hashlib
import unittest
from i55_cell_archive_recheck import ArchiveMismatch, audit_library, git_blob_sha


def cell(seed):
    h = lambda x: hashlib.sha256(x.encode()).hexdigest()
    return {"library": "smac", "function": "sphere", "d": 2, "seed": seed,
            "hash_sentinel": 100, "sentinel_same": 100, "sentinel_diff": 200,
            "manipulation_ok": True, "error": None, "errors": [],
            "hash": h("a"), "hash_rerun": h("a"), "hash_same": h("a"),
            "hash_diff": h("b"), "D3": 0, "D3x_same": 0, "D3x_diff": 1}


def cohort():
    return [cell(i) for i in range(30)]


class CheckArchivedCellRecords(unittest.TestCase):
    def test_empty_git_blob_sha(self):
        self.assertEqual(git_blob_sha(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")

    def test_valid_cells_and_independent_hash_flags(self):
        x = audit_library("smac", cohort())
        self.assertEqual((x["cells"], x["valid"], x["manipulation_ok"], x["D3x_diff"]),
                         (30, 30, 30, 30))

    def test_duplicate_cell_fails(self):
        values=cohort()
        values[1]["seed"] = values[0]["seed"]
        with self.assertRaisesRegex(ArchiveMismatch, "duplicate cell"):
            audit_library("smac", values)

    def test_unchanged_seed_sentinel_fails(self):
        values=cohort()
        values[0]["sentinel_diff"] = 100
        with self.assertRaisesRegex(ArchiveMismatch, "manipulation ineffective"):
            audit_library("smac", values)

    def test_reclassified_hash_must_match_flag(self):
        values=cohort()
        values[0]["D3x_diff"] = 0
        with self.assertRaisesRegex(ArchiveMismatch, "disagrees with source hashes"):
            audit_library("smac", values)

    def test_same_seed_hash_mismatch_is_not_overlooked(self):
        values=cohort()
        values[0]["hash_same"] = hashlib.sha256(b"other").hexdigest()
        with self.assertRaisesRegex(ArchiveMismatch, "D3x_same flag"):
            audit_library("smac", values)

    def test_invalid_cell_cannot_be_counted_as_valid(self):
        values=cohort()
        values[0]["error"] = "simulated error"
        with self.assertRaisesRegex(ArchiveMismatch, "invalid cell marked manipulation success"):
            audit_library("smac", values)

    def test_bad_digest_is_rejected(self):
        values=cohort()
        values[0]["hash_diff"] = "garbage"
        with self.assertRaisesRegex(ArchiveMismatch, "invalid hash_diff digest"):
            audit_library("smac", values)

if __name__ == "__main__":
    unittest.main()
