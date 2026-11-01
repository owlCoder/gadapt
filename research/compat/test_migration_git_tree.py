"""Synthetic fast tests for the read-only committed-tree provenance gate."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("check_migration_git_tree.py")


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


class ProvenanceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "user.name", "Migration test")
        self.research = self.root / "research"
        self.research.mkdir()
        old = self.research / "legacy_demo.py"
        old.write_text("X = 41\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "original")
        self.source = git(self.root, "rev-parse", "HEAD")
        original_sha = git(self.root, "rev-parse", "HEAD:research/legacy_demo.py")
        dst = self.research / "legacy" / "flat" / "legacy_demo.py"
        dst.parent.mkdir(parents=True)
        old.rename(dst)
        view = self.research / "studies" / "i41" / "legacy_demo.py"
        view.parent.mkdir(parents=True)
        view.symlink_to("../../legacy/flat/legacy_demo.py")
        self.manifest = self.research / "MIGRATION_MANIFEST_2026-11-01.json"
        self.data = {"source_commit": self.source, "moved_files": [{
            "old": "research/legacy_demo.py", "canonical": "research/legacy/flat/legacy_demo.py",
            "view": "research/studies/i41/legacy_demo.py", "sha": original_sha,
            "bytes": 7, "mode": "100644", "name": "legacy_demo.py"}]}
        self.save()
        self.commit()

    def save(self):
        self.manifest.write_text(json.dumps(self.data))

    def commit(self):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "migration")

    def call(self):
        p = subprocess.run(["python", str(SCRIPT), "--root", str(self.root)],
                           text=True, capture_output=True)
        return p.returncode, json.loads(p.stdout)

    def test_valid_history_and_symlinks(self):
        rc, out = self.call()
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["count"], 1)

    def test_tampered_canonical_is_detected(self):
        (self.research / "legacy/flat/legacy_demo.py").write_text("X = 999\n")
        self.commit()
        rc, out = self.call()
        self.assertEqual(rc, 1)
        self.assertIn("canonical", out["reason"])

    def test_misdirected_view_detected(self):
        view = self.research / "studies/i41/legacy_demo.py"
        view.unlink()
        view.symlink_to("../../wrong.py")
        self.commit()
        rc, out = self.call()
        self.assertEqual(rc, 1)
        self.assertIn("symlink", out["reason"])

    def test_path_escape_rejected(self):
        self.data["moved_files"][0]["canonical"] = "research/../outside.py"
        self.save()
        rc, out = self.call()
        self.assertEqual(rc, 1)
        self.assertIn("escaping", out["reason"])

    def test_bad_original_history_rejected(self):
        self.data["moved_files"][0]["sha"] = "0" * 40
        self.save()
        rc, out = self.call()
        self.assertEqual(rc, 1)
        self.assertIn("source commit", out["reason"])

    def test_repeated_entry_rejected(self):
        self.data["moved_files"].append(dict(self.data["moved_files"][0]))
        self.save()
        rc, out = self.call()
        self.assertEqual(rc, 1)
        self.assertIn("repeated", out["reason"])


if __name__ == "__main__":
    unittest.main()
