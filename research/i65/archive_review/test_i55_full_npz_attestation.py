"""Synthetic unit tests ONLY. These do NOT replay the 620 original NPZ files."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import i55_full_npz_attestation as chain
from i55_npz_git_blob_manifest_gate import (
    SOURCE_COMMIT, SOURCE_TREE, blob_id, wanted_paths,
)


def fake_manifest():
    entries = [dict(path=p, git_blob_sha1=blob_id(p.encode()), size=len(p.encode()))
               for p in sorted(wanted_paths())]
    entries[0]["size"] += 12_319_037 - sum(r["size"] for r in entries)
    entries[0]["git_blob_sha1"] = "a" * 40
    return {"schema": "I65_I55_ORIGINAL_NPZ_GIT_TREE_V1",
            "original_source_commit": SOURCE_COMMIT,
            "original_source_tree_sha1": SOURCE_TREE,
            "original_npz_count": 620,
            "total_bytes": 12_319_037, "entries": entries}


def fake_git(repo, *args):
    if args == ("rev-parse", "--show-toplevel"):
        return str(Path(repo).resolve())
    if args == ("rev-parse", SOURCE_COMMIT + "^{tree}"):
        return SOURCE_TREE
    if args == ("ls-tree", "--full-tree", "-r", "-l", SOURCE_COMMIT, "--", chain.gate.BASE):
        return "\n".join(f'100644 blob {r["git_blob_sha1"]} {r["size"]:>7}\t{r["path"]}'
                         for r in fake_manifest()["entries"])
    raise AssertionError(f"Unexpected Git query: {args}")


class OriginalGitTreeTests(unittest.TestCase):
    def test_620_path_roster_and_exact_tree(self):
        m = fake_manifest()
        with patch.object(chain, "_git", side_effect=fake_git):
            output = chain.check_original_commit_tree(Path("/tmp/nonexistent-repo"), m)
        self.assertEqual(output["original_npz_tree_entries"], 620)
        self.assertTrue(output["exact_tree_manifest_match"])

    def test_missing_original_blob_rejected(self):
        m = fake_manifest()
        def wrong(repo, *args):
            out = fake_git(repo, *args)
            if args[0] == "ls-tree":
                return "\n".join(out.splitlines()[:-1])
            return out
        with patch.object(chain, "_git", side_effect=wrong):
            with self.assertRaisesRegex(chain.AttestationFailure, "Original Git tree differs"):
                chain.check_original_commit_tree(Path("/tmp/nonexistent-repo"), m)

    def test_modified_blob_rejected(self):
        m = fake_manifest()
        def wrong(repo, *args):
            out = fake_git(repo, *args)
            if args[0] == "ls-tree":
                out = out.replace(" blob " + m["entries"][0]["git_blob_sha1"] + " ",
                                  " blob " + "b" * 40 + " ", 1)
            return out
        with patch.object(chain, "_git", side_effect=wrong):
            with self.assertRaisesRegex(chain.AttestationFailure, "blob/size mismatch"):
                chain.check_original_commit_tree(Path("/tmp/nonexistent-repo"), m)

    def test_wrong_original_tree_rejected(self):
        m = fake_manifest()
        def wrong(repo, *args):
            return "0" * 40 if args == ("rev-parse", SOURCE_COMMIT + "^{tree}") else fake_git(repo, *args)
        with patch.object(chain, "_git", side_effect=wrong):
            with self.assertRaisesRegex(chain.AttestationFailure, "root tree changed"):
                chain.check_original_commit_tree(Path("/tmp/nonexistent-repo"), m)

    def test_wrong_git_root_rejected(self):
        m = fake_manifest()
        def wrong(repo, *args):
            return "/other" if args == ("rev-parse", "--show-toplevel") else fake_git(repo, *args)
        with patch.object(chain, "_git", side_effect=wrong):
            with self.assertRaisesRegex(chain.AttestationFailure, "Repository root mismatch"):
                chain.check_original_commit_tree(Path("/tmp/nonexistent-repo"), m)

    def test_unexpected_source_symlink_rejected(self):
        m = fake_manifest()
        def wrong(repo, *args):
            out = fake_git(repo, *args)
            if args[0] == "ls-tree":
                return out.replace("100644 blob ", "120000 blob ", 1)
            return out
        with patch.object(chain, "_git", side_effect=wrong):
            with self.assertRaisesRegex(chain.AttestationFailure, "Unexpected Git tree record"):
                chain.check_original_commit_tree(Path("/tmp/nonexistent-repo"), m)

    def test_unexpected_extra_path_rejected(self):
        m = fake_manifest()
        def wrong(repo, *args):
            out = fake_git(repo, *args)
            if args[0] == "ls-tree":
                out += "\n100644 blob " + "c" * 40 + " 3\t" + chain.gate.BASE + "/extra.npz"
            return out
        with patch.object(chain, "_git", side_effect=wrong):
            with self.assertRaisesRegex(chain.AttestationFailure, "Original Git tree differs"):
                chain.check_original_commit_tree(Path("/tmp/nonexistent-repo"), m)


class PinTests(unittest.TestCase):
    def test_manifest_must_have_pinned_git_blob(self):
        m = fake_manifest()
        data = (json.dumps(m, sort_keys=True) + "\n").encode()
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "manifest.json"
            p.write_bytes(data)
            with patch.object(chain, "PINNED_MANIFEST_GIT_BLOB", blob_id(data)):
                self.assertEqual(len(chain.load_pinned_manifest(p)["entries"]), 620)
            p.write_bytes(data + b" ")
            with patch.object(chain, "PINNED_MANIFEST_GIT_BLOB", blob_id(data)):
                with self.assertRaisesRegex(chain.AttestationFailure, "Untrusted manifest"):
                    chain.load_pinned_manifest(p)

    def test_invalid_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "manifest.json"
            p.write_bytes(b"not JSON")
            with patch.object(chain, "PINNED_MANIFEST_GIT_BLOB", blob_id(b"not JSON")):
                with self.assertRaisesRegex(chain.AttestationFailure, "Invalid pinned NPZ"):
                    chain.load_pinned_manifest(p)


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.manifest = fake_manifest()

    def test_stop_before_trace_on_corrupt_npz(self):
        with patch.object(chain, "load_pinned_manifest", return_value=self.manifest), \
             patch.object(chain, "check_original_commit_tree", return_value={"exact_tree_manifest_match": True}), \
             patch.object(chain.gate, "check_local_bytes", return_value={"full_git_blob_pass": False}), \
             patch.object(chain.trace, "audit") as check:
            out = chain.attest(Path("/tmp"), Path("/tmp/m.json"))
        check.assert_not_called()
        self.assertEqual(out["status"], "BLOCKED")
        self.assertNotIn("620_trace_sha256_and_detector_flags_replayed", out["completed_levels"])

    def test_trace_mismatch_must_not_pass(self):
        with patch.object(chain, "load_pinned_manifest", return_value=self.manifest), \
             patch.object(chain, "check_original_commit_tree", return_value={"exact_tree_manifest_match": True}), \
             patch.object(chain.gate, "check_local_bytes", return_value={"full_git_blob_pass": True}), \
             patch.object(chain.trace, "audit", return_value={
                 "cross_i50_i55": {"matches_frozen_318_358": True},
                 "posthoc_emukit_saved_digest_check": {"all_10_match_i50_and_differ_i55": True},
                 "npz": {"checked": 619, "full_raw_trace_pass": True}}):
            out = chain.attest(Path("/tmp"), Path("/tmp/m.json"))
        self.assertFalse(out["full_attestation_pass"])
        self.assertIn("Original 620", out["failure"]["description"])

    def test_all_levels_require_real_success(self):
        with patch.object(chain, "load_pinned_manifest", return_value=self.manifest), \
             patch.object(chain, "check_original_commit_tree", return_value={"exact_tree_manifest_match": True}), \
             patch.object(chain.gate, "check_local_bytes", return_value={"full_git_blob_pass": True}), \
             patch.object(chain.trace, "audit", return_value={
                 "cross_i50_i55": {"matches_frozen_318_358": True},
                 "posthoc_emukit_saved_digest_check": {"all_10_match_i50_and_differ_i55": True},
                 "npz": {"checked": 620, "full_raw_trace_pass": True}}):
            out = chain.attest(Path("/tmp"), Path("/tmp/m.json"))
        self.assertTrue(out["full_attestation_pass"])
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(len(out["completed_levels"]), 4)

    def test_posthoc_digest_mismatch_blocks(self):
        with patch.object(chain, "load_pinned_manifest", return_value=self.manifest), \
             patch.object(chain, "check_original_commit_tree", return_value={"exact_tree_manifest_match": True}), \
             patch.object(chain.gate, "check_local_bytes", return_value={"full_git_blob_pass": True}), \
             patch.object(chain.trace, "audit", return_value={
                 "cross_i50_i55": {"matches_frozen_318_358": True},
                 "posthoc_emukit_saved_digest_check": {"all_10_match_i50_and_differ_i55": False},
                 "npz": {"checked": 620, "full_raw_trace_pass": True}}):
            out = chain.attest(Path("/tmp"), Path("/tmp/m.json"))
        self.assertFalse(out["full_attestation_pass"])
        self.assertIn("VECLIB", out["failure"]["description"])


if __name__ == "__main__":
    unittest.main()
