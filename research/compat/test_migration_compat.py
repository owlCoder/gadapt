"""Cheap local filesystem/CLI regression suite for research migration.

Runs in temporary Git repositories with synthetic modules, never re-runs I64
or operates on frozen data. Python unittest, stdlib only; no dependency install.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("restore_legacy_paths.py")


class MigrationCompatibility(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.d = self.root / "research"
        (self.d / "compat").mkdir(parents=True)
        (self.d / "legacy" / "flat").mkdir(parents=True)
        shutil.copy2(SCRIPT, self.d / "compat" / SCRIPT.name)
        (self.d / "__init__.py").write_text('"""Research package; compatibility is opt-in."""\n')
        self.manifest = []

    def item(self, name, body):
        dst = self.d / "legacy" / "flat" / name
        dst.write_text(body)
        b = dst.read_bytes()
        sha = hashlib.sha1(f"blob {len(b)}\0".encode() + b).hexdigest()
        self.manifest.append({"old": "research/" + name,
                              "canonical": "research/legacy/flat/" + name,
                              "sha": sha})
        self.save()
        return dst

    def save(self):
        (self.d / "MIGRATION_MANIFEST_2026-11-01.json").write_text(
            json.dumps({"moved_files": self.manifest}))

    def run_cli(self, *args):
        return subprocess.run([sys.executable,
                               str(self.d / "compat" / SCRIPT.name), *args],
                              cwd=str(self.root), capture_output=True, text=True)

    def test_dry_run_creates_no_files(self):
        self.item("iteration61_replication.py", "X = 1\n")
        p = self.run_cli("--verify")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("mode=dry-run", p.stdout)
        self.assertFalse((self.d / "iteration61_replication.py").exists())

    def test_apply_restores_old_path_and_is_idempotent(self):
        self.item("iteration41_certified_temporal_rows.py", "SENTINEL = 41\n")
        p = self.run_cli("--apply", "--verify")
        self.assertEqual(p.returncode, 0, p.stderr)
        alias = self.d / "iteration41_certified_temporal_rows.py"
        self.assertTrue(alias.is_symlink())
        self.assertEqual(alias.resolve(), (self.d / "legacy" / "flat" / alias.name))
        p = self.run_cli("--apply", "--verify")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("existing=1", p.stdout)

    def test_existing_non_symlink_never_overwritten(self):
        self.item("iteration41_certified_temporal_rows.py", "X = 1\n")
        old = self.d / "iteration41_certified_temporal_rows.py"
        old.write_text("USER DATA\n")
        p = self.run_cli("--apply", "--verify")
        self.assertEqual(p.returncode, 1)
        self.assertEqual(old.read_text(), "USER DATA\n")

    def test_wrong_symlink_never_replaced(self):
        self.item("iteration41_certified_temporal_rows.py", "X = 1\n")
        old = self.d / "iteration41_certified_temporal_rows.py"
        another = self.d / "other.py"
        another.write_text("X = 2\n")
        old.symlink_to(another)
        p = self.run_cli("--apply")
        self.assertEqual(p.returncode, 1)
        self.assertEqual(old.resolve(), another.resolve())

    def test_nonexistent_canonical_fails_closed(self):
        dst = self.item("iteration41_certified_temporal_rows.py", "X = 1\n")
        dst.unlink()
        p = self.run_cli("--apply", "--verify")
        self.assertEqual(p.returncode, 1)
        self.assertFalse((self.d / dst.name).exists())

    def test_hash_mismatch_fails_before_any_symlink(self):
        self.item("iteration40_temporal_calibrated_plan.py", "X = 1\n")
        dst = self.item("iteration41_certified_temporal_rows.py", "X = 41\n")
        dst.write_text("MODIFIED SOURCE\n")
        p = self.run_cli("--apply", "--verify")
        self.assertEqual(p.returncode, 1)
        self.assertIn("no aliases created", p.stderr)
        self.assertFalse((self.d / "iteration40_temporal_calibrated_plan.py").exists())
        self.assertFalse((self.d / "iteration41_certified_temporal_rows.py").exists())

    def test_duplicate_old_path_rejected_preflight(self):
        self.item("iteration40_temporal_calibrated_plan.py", "X = 1\n")
        self.manifest.append(dict(self.manifest[0]))
        self.save()
        p = self.run_cli("--apply")
        self.assertEqual(p.returncode, 1)
        self.assertFalse((self.d / "iteration40_temporal_calibrated_plan.py").exists())

    def test_old_symlink_preserves_here_for_cli_and_import(self):
        self.item("iteration63_replication.py", (
            "from pathlib import Path\n"
            "HERE = Path(__file__).absolute().parent\n"
            "REPO = HERE.parent\n"
            "if __name__ == '__main__':\n"
            "    print(str(HERE))\n"
            "    print(str(REPO))\n"
        ))
        before = subprocess.run([sys.executable, "-c", "import research.iteration63_replication"],
                                cwd=str(self.root), capture_output=True, text=True)
        self.assertNotEqual(before.returncode, 0, "implicit imports must fail before restore")
        self.assertEqual(self.run_cli("--apply", "--verify").returncode, 0)
        p = subprocess.run([sys.executable, str(self.d / "iteration63_replication.py")],
                           cwd=str(self.root), capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.splitlines(), [str(self.d), str(self.root)])
        after = subprocess.run([sys.executable, "-c", (
            "from research import iteration63_replication as m;"
            "print(m.HERE); print(m.REPO)")], cwd=str(self.root), capture_output=True, text=True)
        self.assertEqual(after.returncode, 0, after.stderr)
        self.assertEqual(after.stdout.splitlines(), [str(self.d), str(self.root)])

    def test_curated_symlink_view_is_read_only_navigation(self):
        self.item("ITERATION41_PROTOCOL.md", "# Frozen text\n")
        view = self.d / "studies" / "i41" / "ITERATION41_PROTOCOL.md"
        view.parent.mkdir(parents=True)
        view.symlink_to("../../legacy/flat/ITERATION41_PROTOCOL.md")
        self.assertEqual(view.read_text(), "# Frozen text\n")
        self.assertEqual(view.resolve(), (self.d / "legacy" / "flat" / view.name))


if __name__ == "__main__":
    unittest.main()
