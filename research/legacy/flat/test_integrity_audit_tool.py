"""Planted-fault validation of research/integrity_audit_tool.py: each runner plants exactly one problem class."""
import os
import tempfile
import textwrap
import unittest

import research.integrity_audit_tool as tool

RUNNERS = textwrap.dedent('''
    import time
    import numpy as np


    def _search(f, lower, upper, budget, rng):
        best_x, best_f = None, np.inf
        for _ in range(budget):
            x = rng.uniform(lower, upper)
            y = f(x)
            if y < best_f:
                best_x, best_f = x.copy(), y
        return best_x, best_f


    def clean(f, lower, upper, budget, seed):
        out = _search(f, lower, upper, budget, np.random.default_rng(seed))
        f.search_done()
        return out


    def no_result(f, lower, upper, budget, seed):
        _search(f, lower, upper, budget, np.random.default_rng(seed))


    def out_of_box(f, lower, upper, budget, seed):
        f(upper + 1.0)
        return _search(f, lower, upper, budget - 1, np.random.default_rng(seed))


    def over_budget(f, lower, upper, budget, seed):
        return _search(f, lower, upper, budget + 1, np.random.default_rng(seed))


    def after_return(f, lower, upper, budget, seed):
        x, y = _search(f, lower, upper, budget - 1, np.random.default_rng(seed))
        f.search_done()
        return x, f(x)


    def unevaluated(f, lower, upper, budget, seed):
        x, y = _search(f, lower, upper, budget, np.random.default_rng(seed))
        return x + 1e-6, y


    def wrong_value(f, lower, upper, budget, seed):
        x, y = _search(f, lower, upper, budget, np.random.default_rng(seed))
        return x, y - 1.0


    def not_best(f, lower, upper, budget, seed):
        rng = np.random.default_rng(seed)
        xs = [rng.uniform(lower, upper) for _ in range(budget)]
        ys = [f(x) for x in xs]
        worst = int(np.argmax(ys))
        return xs[worst], ys[worst]


    def hash_seeded(f, lower, upper, budget, seed):
        return _search(f, lower, upper, budget, np.random.default_rng(abs(hash(f"s{seed}")) % 2**32))


    def time_seeded(f, lower, upper, budget, seed):
        return _search(f, lower, upper, budget, np.random.default_rng(time.time_ns() % 2**32))


    def corner_probe(f, lower, upper, budget, seed):
        f(lower)
        return _search(f, lower, upper, budget - 1, np.random.default_rng(seed))
''')

EXPECTED = {
    "clean": set(), "no_result": set(), "corner_probe": set(),
    "out_of_box": {"C3"}, "over_budget": {"C4"}, "after_return": {"C5"}, "unevaluated": {"R1"},
    "wrong_value": {"R2"}, "not_best": {"R3"}, "hash_seeded": {"D3x"}, "time_seeded": {"D3", "D3x"},
}


class IntegrityAuditToolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = os.path.join(cls.tmp.name, "runners.py")
        with open(cls.path, "w") as fh:
            fh.write(RUNNERS)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def audit(self, name):
        return tool.audit(f"{self.path}:{name}", budget=30, dims=(2,), seeds=1)

    def test_each_planted_fault_is_detected_exactly(self):
        for name, want in EXPECTED.items():
            with self.subTest(name=name):
                summary = self.audit(name)
                self.assertEqual(summary["errors"], [])
                self.assertEqual(set(summary["integrity"]), want)

    def test_corner_probe_is_reported_as_info_not_integrity(self):
        summary = self.audit("corner_probe")
        self.assertEqual(summary["corner_calls_runs"], 3)
        self.assertEqual(summary["integrity"], {})

    def test_no_result_disables_result_checks(self):
        self.assertFalse(self.audit("no_result")["reports_result"])


if __name__ == "__main__":
    unittest.main()
