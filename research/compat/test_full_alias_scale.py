"""End-to-end 341-path Git-tree+worktree stress gate with SYNTHETIC data.

Real Git objects, exact official migration helper sources, no real I41/ORPD
cost functions and no scientific test results.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import posixpath
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).parent
RESTORE = HERE / 'restore_legacy_paths.py'
CHECK = HERE / 'check_migration_git_tree.py'


def execute(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


def digest(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


class All341PathStress(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for command in (['git', 'init', '-q', '-b', 'main'],
                        ['git', 'config', 'user.email', 'synthetic@example.invalid'],
                        ['git', 'config', 'user.name', 'Synthetic Migration']):
            p = execute(*command, cwd=self.root)
            self.assertEqual(p.returncode, 0, p.stderr)
        self.research = self.root / 'research'
        self.research.mkdir()
        self.manifest_entries = []
        for i in range(341):
            name = f'iteration_{i:03d}_synthetic.py'
            contents = f'INDEX = {i}\n'.encode()
            (self.research / name).write_bytes(contents)
            self.manifest_entries.append({
                'old': f'research/{name}',
                'canonical': f'research/legacy/flat/{name}',
                'view': f'research/studies/i{i%42:02d}/{name}',
                'name': name, 'sha': digest(contents), 'mode': '100644',
                'bytes': len(contents)})
        self.commit('pre-migration synthetic baseline')
        source = execute('git', 'rev-parse', 'HEAD', cwd=self.root).stdout.strip()
        for entry in self.manifest_entries:
            old = self.root / entry['old']
            dst = self.root / entry['canonical']
            dst.parent.mkdir(parents=True, exist_ok=True)
            old.rename(dst)
            view = self.root / entry['view']
            view.parent.mkdir(parents=True, exist_ok=True)
            view.symlink_to(posixpath.relpath(entry['canonical'], posixpath.dirname(entry['view'])))
        (self.research / 'MIGRATION_MANIFEST_2026-11-01.json').write_text(
            json.dumps({'source_commit': source, 'moved_files': self.manifest_entries}))
        self.commit('migrated synthetic tree')

    def commit(self, message):
        self.assertEqual(execute('git', 'add', '-A', cwd=self.root).returncode, 0)
        p = execute('git', 'commit', '-qm', message, cwd=self.root)
        self.assertEqual(p.returncode, 0, p.stderr)

    def check(self):
        return execute(sys.executable, str(CHECK), '--root', str(self.root), cwd=self.root)

    def restore(self, *args):
        dest = self.research / 'compat' / 'restore_legacy_paths.py'
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RESTORE, dest)
        return execute(sys.executable, str(dest), *args, cwd=self.root)

    def test_341_real_git_objects_restore_and_idempotence(self):
        p = self.check()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)['count'], 341)
        p = self.restore('--verify')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('checked=341; planned=341;', p.stdout)
        self.assertFalse((self.research / self.manifest_entries[0]['name']).exists())
        p = self.restore('--apply', '--verify')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('created=341; existing=0;', p.stdout)
        p = self.restore('--apply', '--verify')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('created=0; existing=341;', p.stdout)
        for entry in self.manifest_entries:
            self.assertEqual((self.root / entry['old']).read_bytes(),
                             (self.root / entry['canonical']).read_bytes())
        # The ignored worktree aliases have NOT modified committed Git objects.
        self.assertEqual(json.loads(self.check().stdout)['count'], 341)

    def test_one_corrupt_source_refuses_all_341_aliases(self):
        (self.root / self.manifest_entries[222]['canonical']).write_text('CORRUPTED\n')
        p = self.restore('--apply', '--verify')
        self.assertEqual(p.returncode, 1)
        self.assertIn('no aliases created', p.stderr)
        for entry in self.manifest_entries:
            self.assertFalse((self.root / entry['old']).is_symlink())


if __name__ == '__main__':
    unittest.main()
