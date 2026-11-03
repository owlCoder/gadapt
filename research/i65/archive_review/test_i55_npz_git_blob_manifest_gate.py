import copy
import json
import tempfile
import unittest
from pathlib import Path

from i55_npz_git_blob_manifest_gate import (
    ArchiveIndexError, BASE, LIBRARIES, SOURCE_COMMIT, SOURCE_TREE,
    blob_id, check_local_bytes, validate_manifest, wanted_paths,
)


class NPZGitBlobGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_files = {p: ("archive://" + p).encode() for p in wanted_paths()}
        cls.manifest = {
            "schema": "I65_I55_ORIGINAL_NPZ_GIT_TREE_V1",
            "original_source_commit": SOURCE_COMMIT,
            "original_source_tree_sha1": SOURCE_TREE,
            "original_npz_count": 620,
            "total_bytes": 12319037,
            "entries": [dict(path=p, git_blob_sha1=blob_id(cls.raw_files[p]), size=len(cls.raw_files[p]))
                        for p in sorted(cls.raw_files)],
        }
        # The original total size is a hard gate; tests exercise synthetics by
        # changing the bytes of one large fake fixture to match exactly.
        gap = 12319037 - sum(x["size"] for x in cls.manifest["entries"])
        cls.special_path = cls.manifest["entries"][0]["path"]
        cls.raw_files[cls.special_path] += b"X" * gap
        cls.manifest["entries"][0]["size"] += gap
        cls.manifest["entries"][0]["git_blob_sha1"] = blob_id(cls.raw_files[cls.special_path])

    def test_expected_roster_size(self):
        self.assertEqual(len(wanted_paths()), 620)
        self.assertEqual(len(LIBRARIES), 21)
        self.assertFalse(any(p.endswith("sphere_10_6000.npz") and "/nevergrad/" in p for p in wanted_paths()))

    def test_git_blob_fixture(self):
        self.assertEqual(blob_id(b"hello"), "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_manifest_valid(self):
        result = validate_manifest(self.manifest)
        self.assertEqual(result["manifest_files"], 620)
        self.assertEqual(result["manifest_bytes"], 12319037)
        self.assertEqual(result["library_counts"]["nevergrad"], 20)

    def test_duplicate_path_fail_closed(self):
        m = copy.deepcopy(self.manifest)
        m["entries"][1]["path"] = m["entries"][0]["path"]
        with self.assertRaises(ArchiveIndexError): validate_manifest(m)

    def test_unknown_path_fail_closed(self):
        m = copy.deepcopy(self.manifest)
        m["entries"][1]["path"] = m["entries"][1]["path"] + ".bak"
        with self.assertRaises(ArchiveIndexError): validate_manifest(m)

    def test_wrong_source_tree_fail_closed(self):
        m = copy.deepcopy(self.manifest)
        m["original_source_tree_sha1"] = "0" * 40
        with self.assertRaises(ArchiveIndexError): validate_manifest(m)

    def test_wrong_original_bytes_fail_closed(self):
        m = copy.deepcopy(self.manifest)
        m["entries"][2]["size"] += 1
        with self.assertRaises(ArchiveIndexError): validate_manifest(m)

    def test_bad_hash_fail_closed(self):
        m = copy.deepcopy(self.manifest)
        m["entries"][2]["git_blob_sha1"] = "N" * 40
        with self.assertRaises(ArchiveIndexError): validate_manifest(m)

    def test_boolean_file_size_fail_closed(self):
        m = copy.deepcopy(self.manifest)
        m["entries"][2]["size"] = True
        with self.assertRaises(ArchiveIndexError): validate_manifest(m)

    def test_complete_local_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for p, content in self.raw_files.items():
                target = root / p
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            result = check_local_bytes(root, self.manifest)
            self.assertTrue(result["full_git_blob_pass"])
            self.assertEqual(result["raw_bytes_verified"], 620)
            self.assertFalse(result["npz_trace_arrays_replayed"])
            # Mutation even without changing file size must fail Git blob check.
            path = root / sorted(self.raw_files)[1]
            content = path.read_bytes()
            path.write_bytes(content[:-1] + bytes([content[-1] ^ 1]))
            result = check_local_bytes(root, self.manifest)
            self.assertFalse(result["full_git_blob_pass"])
            self.assertEqual(len(result["corrupt"]), 1)

    def test_missing_local_byte_file(self):
        with tempfile.TemporaryDirectory() as folder:
            result = check_local_bytes(Path(folder), self.manifest)
            self.assertFalse(result["full_git_blob_pass"])
            self.assertEqual(len(result["missing"]), 620)

    def test_unexpected_local_npz_file(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / BASE / "fake").mkdir(parents=True)
            (Path(folder) / BASE / "fake" / "not_a_cell.npz").write_bytes(b"abc")
            result = check_local_bytes(Path(folder), self.manifest)
            self.assertEqual(len(result["unexpected"]), 1)


if __name__ == "__main__":
    unittest.main()
