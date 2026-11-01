"""Cheap fail-closed tests of the full-clone gate driver, no actual legacy runs."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name('run_full_clone_gate.py')
spec = importlib.util.spec_from_file_location('local_gate', SCRIPT)
local_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_gate)


class FullCloneGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'repo'
        self.root.mkdir()
        self.python = self.base / 'python312'
        self.python.write_text('synthetic executable marker')
        self.reports = self.base / 'reports'

    def fake_ready(self, *args):
        return {'status': 'READY', 'errors': [], 'head': 'a' * 40,
                'branch': 'main', 'python': str(self.python),
                'python_version': '3.12', 'root': str(self.root)}

    def fake_git(self, root, *args):
        return subprocess.CompletedProcess(['git', *args], 0, 'a' * 40 + '\n', '')

    def fake_step(self, cmd, *, cwd, timeout):
        key = ' '.join(cmd)
        if 'restore_legacy_paths.py' in key:
            if '--apply' in key:
                if not hasattr(self, 'apply_calls'):
                    self.apply_calls = 0
                self.apply_calls += 1
                suffix = 'created=341; existing=0;' if self.apply_calls == 1 else 'created=0; existing=341;'
                return subprocess.CompletedProcess(cmd, 0, 'checked=341; planned=0; ' + suffix + ' hash_verification=enabled\n', '')
            return subprocess.CompletedProcess(cmd, 0, 'checked=341; planned=341; created=0; existing=0; hash_verification=enabled\n', '')
        if 'check_migration_git_tree.py' in key:
            return subprocess.CompletedProcess(cmd, 0, '{"status":"PASS", "count": 341}', '')
        return subprocess.CompletedProcess(cmd, 0, 'ok\n', '')

    def exercise(self, fake_step=None):
        with patch.object(local_gate, 'prerequisites', side_effect=self.fake_ready), \
             patch.object(local_gate, 'git', side_effect=self.fake_git), \
             patch.object(local_gate, 'run_cmd', side_effect=fake_step or self.fake_step):
            return local_gate.perform(self.root, self.python, self.reports, 120, None)

    def test_no_real_clone_is_blocked(self):
        check = local_gate.prerequisites(self.root, self.python, None)
        self.assertEqual(check['status'], 'BLOCKED')
        self.assertIn('NOT_A_FULL_LOCAL_GIT_CHECKOUT', check['errors'])
        self.assertIn('ORIGINAL_GIT_HISTORY_MISSING', check['errors'])
        self.assertIn('REQUIRES_PYTHON_3_12', check['errors'])

    def test_full_fake_sequence_passes_only_all_eleven_steps(self):
        self.assertEqual(self.exercise(), 0)
        output = json.loads((self.reports / 'gate.json').read_text())
        self.assertEqual(output['status'], 'PASS')
        self.assertEqual(len(output['steps']), 11)
        self.assertTrue(all(x['status'] == 'PASS' for x in output['steps']))
        self.assertEqual(self.apply_calls, 2)
        for step in output['steps']:
            path = self.reports / step['log']
            self.assertEqual(step['log_sha256'], local_gate.sha256(path.read_bytes()))

    def test_wrong_manifest_count_fails_before_restore_apply(self):
        def spoof(cmd, **kwargs):
            p = self.fake_step(cmd, **kwargs)
            if '--verify' in cmd and '--apply' not in cmd:
                return subprocess.CompletedProcess(cmd, 0, 'checked=340; hash_verification=enabled', '')
            return p
        self.assertEqual(self.exercise(spoof), 1)
        out = json.loads((self.reports / 'gate.json').read_text())
        self.assertEqual(out['steps'][-1]['failure'], 'RESTORE_COUNT_OR_HASH_VERIFICATION_MISSING')
        self.assertFalse(hasattr(self, 'apply_calls'))

    def test_timeout_stops_and_marks_failure(self):
        def timeout(cmd, *, cwd, timeout):
            if 'test_i65' in ' '.join(cmd) or cmd[-1] == 'research/i65':
                raise subprocess.TimeoutExpired(cmd, timeout)
            return self.fake_step(cmd, cwd=cwd, timeout=timeout)
        self.assertEqual(self.exercise(timeout), 1)
        out = json.loads((self.reports / 'gate.json').read_text())
        self.assertEqual(out['status'], 'FAIL')
        self.assertEqual(out['steps'][-1]['exit_code'], 124)

    def test_rerun_cannot_overwrite_existing_report(self):
        self.assertEqual(self.exercise(), 0)
        with patch.object(local_gate, 'prerequisites', side_effect=self.fake_ready):
            self.assertEqual(local_gate.perform(self.root, self.python, self.reports, 120, None), 2)

    def test_dont_write_reports_inside_repo(self):
        with patch.object(local_gate, 'prerequisites', side_effect=self.fake_ready):
            self.assertEqual(local_gate.perform(self.root, self.python, self.root / 'reports', 120, None), 2)

    def test_skipped_essential_test_is_not_a_full_pass(self):
        def skipping(cmd, **kwargs):
            p = self.fake_step(cmd, **kwargs)
            if cmd[-1] == 'research/i65':
                return subprocess.CompletedProcess(cmd, 0, '88 passed, 1 skipped, 3 xfailed', '')
            return p
        self.assertEqual(self.exercise(skipping), 1)
        out = json.loads((self.reports / 'gate.json').read_text())
        self.assertEqual(out['status'], 'FAIL')
        self.assertEqual(out['steps'][-1]['status'], 'PARTIAL')
        self.assertEqual(out['steps'][-1]['warning'], 'PYTEST_SKIPPED_TESTS')

    def test_allowlist_has_no_benchmark_or_network_action(self):
        self.assertEqual(len(local_gate.STEPS), 11)
        steps = [' '.join(parts) for _, _, parts in local_gate.STEPS]
        self.assertFalse(any('install' in x or 'benchmark' in x or 'workflow' in x or 'coco' in x for x in steps))
        self.assertEqual([x[0] for x in local_gate.STEPS][-4:], ['i41', 'i63', 'i64', 'i65'])
        self.assertIn('not pygad', ' '.join(local_gate.STEPS[-2][2]))


    def test_main_preserves_venv_python_symlink(self):
        # Use real venv, not a mocked Python interpreter, to catch a repeat
        # of the GitHub Actions failure: .resolve() lost the site-packages.
        import os
        import sys
        import venv
        if os.name != "posix":
            self.skipTest("requires POSIX virtualenv symlinks")
        venv_path = self.base / "real_venv"
        venv.EnvBuilder(with_pip=False, symlinks=True).create(venv_path)
        vpython = venv_path / "bin" / "python"
        self.assertTrue(vpython.is_symlink())
        self.assertNotEqual(str(vpython.absolute()), str(vpython.resolve()))
        result = subprocess.run([str(vpython), "-c",
                                 "import sys; print(sys.prefix != sys.base_prefix)"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "True")

    def test_wrong_interpreter_or_numpy_fails_closed(self):
        import subprocess
        # Synthetic response models Python 3.12 outside venv, and NumPy 2.x
        for payload in ('{"python":"3.12","venv":false,"numpy":"1.26.4"}',
                        '{"python":"3.12","venv":true,"numpy":"2.5.4"}'):
            with patch.object(local_gate, 'run_cmd',
                              return_value=subprocess.CompletedProcess([], 0, payload, '')):
                ok, reason = local_gate.allowed_python(self.python, self.root)
                self.assertFalse(ok)
                self.assertIn('3.12', reason)


if __name__ == '__main__':
    unittest.main()
