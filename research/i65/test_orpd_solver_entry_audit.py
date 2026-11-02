"""Adversarial accounting tests using a fake PYPOWER facade, no solver runs."""
import json
import sys
import types
import unittest
from unittest.mock import patch

from orpd_solver_entry_audit import SolverEntryAudit


class SolverEntryAuditTests(unittest.TestCase):
    def setUp(self):
        self.called = []
        api = types.ModuleType("pypower.api")
        api.runopf = lambda *a, **k: self.called.append("opf") or {"success": True}
        api.runpf = lambda *a, **k: self.called.append("pf") or (None, True)
        root = types.ModuleType("pypower")
        root.__path__ = []
        root.api = api
        self.fake = patch.dict(sys.modules, {"pypower": root, "pypower.api": api})
        self.fake.start()
        self.addCleanup(self.fake.stop)
        self.api = api

    def test_count_by_phase_and_kind_without_altering_results(self):
        a = SolverEntryAudit()
        before = (self.api.runopf, self.api.runpf)
        with a.trace():
            with a.phase("setup"):
                self.assertEqual(self.api.runopf()["success"], True)
            with a.phase("search"):
                self.assertEqual(self.api.runpf()[1], True)
                self.api.runpf()
            with a.phase("witness"):
                self.api.runopf()
                self.api.runpf()
        self.assertEqual(before, (self.api.runopf, self.api.runpf))
        self.assertEqual(self.called, ["opf", "pf", "pf", "opf", "pf"])
        self.assertEqual(a.count(), 5)
        self.assertEqual(a.evidence()["phases"], {
            "setup": {"runopf": 1, "runpf": 0},
            "search": {"runopf": 0, "runpf": 2},
            "witness": {"runopf": 1, "runpf": 1}})

    def test_exception_counts_attempt_before_callback_and_restores_api(self):
        def fail(*args, **kwargs):
            self.called.append("failed")
            raise ArithmeticError("bad PF")
        self.api.runpf = fail
        before = self.api.runpf
        a = SolverEntryAudit()
        with self.assertRaisesRegex(ArithmeticError, "bad PF"):
            with a.trace():
                with a.phase("search"):
                    self.api.runpf()
        self.assertIs(self.api.runpf, before)
        self.assertEqual(a.events, [{"index": 1, "phase": "search", "kind": "runpf",
                                     "outcome": "exception", "error_type": "ArithmeticError"}])

    def test_base_exception_counts_and_propagates(self):
        def exit_solver(*args):
            raise KeyboardInterrupt()
        self.api.runopf = exit_solver
        a = SolverEntryAudit()
        with self.assertRaises(KeyboardInterrupt):
            with a.trace():
                with a.phase("setup"):
                    self.api.runopf()
        self.assertEqual(a.events[0]["error_type"], "KeyboardInterrupt")

    def test_missing_phase_prevents_unlogged_solver_attempt(self):
        a = SolverEntryAudit()
        with a.trace():
            with self.assertRaisesRegex(RuntimeError, "missing explicit phase"):
                self.api.runpf()
        self.assertEqual(a.count(), 0)
        self.assertFalse(self.called)

    def test_unknown_phase_raises_and_untrusted_kind_rejected(self):
        a = SolverEntryAudit()
        with a.trace():
            with self.assertRaisesRegex(ValueError, "unknown solver phase"):
                with a.phase("verification"):
                    pass
            with self.assertRaisesRegex(ValueError, "unknown solver entrypoint"):
                a.count(kind="runqf")
        self.assertEqual(a.count(), 0)

    def test_nested_phase_and_trace_fail_closed(self):
        a = SolverEntryAudit()
        with a.trace():
            with a.phase("setup"):
                with self.assertRaisesRegex(RuntimeError, "nested solver phase"):
                    with a.phase("search"):
                        pass
                with self.assertRaisesRegex(RuntimeError, "already active"):
                    with a.trace():
                        pass
                self.api.runopf()
        self.assertEqual(a.count(), 1)
        self.assertEqual(a.events[0]["phase"], "setup")

    def test_immutable_serialized_evidence_across_runs(self):
        outputs = []
        for _ in range(2):
            a = SolverEntryAudit()
            with a.trace():
                with a.phase("witness"):
                    self.api.runpf()
            outputs.append(a.evidence())
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(len(outputs[0]["sha256"]), 64)
        self.assertEqual(json.loads(json.dumps(outputs[0]))["totals"]["runpf"], 1)

    def test_phase_without_trace_rejected(self):
        a = SolverEntryAudit()
        with self.assertRaisesRegex(RuntimeError, "start audit"):
            with a.phase("setup"):
                pass


if __name__ == "__main__":
    unittest.main()
