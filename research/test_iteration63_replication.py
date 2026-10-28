"""Tests of the I63 driver (estimand, seeds, calibration statistic, tilting, decision function, scenarios)."""
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("I63_OUT", os.path.join(os.environ.get("TMPDIR", "/tmp"), "i63_test_out"))
import iteration63_replication as m  # noqa: E402


class Estimand(unittest.TestCase):
    def test_win_symmetry_and_tie_threshold(self):
        r = 10.0
        for a, b in [(10.0, 10.5), (10.5, 10.0), (10.0, 10.005), (None, 3.0), (3.0, None), (None, None), (10.0, 10.01)]:
            self.assertEqual(m.win2(a, b, r) + m.win2(b, a, r), 2)
        self.assertEqual(m.win2(10.0, 10.01, r), 1)          # delta = 0.001 exactly is a tie
        self.assertEqual(m.win2(10.0, 10.0101, r), 2)
        self.assertEqual(m.win2(10.0101, 10.0, r), 0)
        self.assertEqual(m.win2(None, None, r), 1)
        self.assertEqual(m.win2(5.0, None, r), 2)
        self.assertEqual(m.win2(None, 5.0, r), 0)

    def test_unit_scaling_invariance(self):
        for a, b in [(10.0, 10.3), (7.0, 7.001), (None, 1.0)]:
            for k in (0.001, 1.0, 1000.0):
                self.assertEqual(m.win2(a, b, 10.0), m.win2(None if a is None else a * k, None if b is None else b * k, 10.0 * k))

    def test_d_sign_convention(self):
        unit = {("FR", "FX-T"): dict(best_feasible=9.0), ("FR", "AD-N"): dict(best_feasible=12.0),
                ("SP", "FX-T"): dict(best_feasible=12.0), ("SP", "AD-N"): dict(best_feasible=9.0)}
        self.assertEqual(m.d_of(unit, 10.0), 1.0)  # FX-T wins under FR and loses under SP: positive theta
        unit[("SP", "FX-T")], unit[("SP", "AD-N")] = dict(best_feasible=9.0), dict(best_feasible=12.0)
        self.assertEqual(m.d_of(unit, 10.0), 0.0)

    def test_gap(self):
        self.assertIsNone(m.gap(dict(best_feasible=None), 5.0))
        self.assertAlmostEqual(m.gap(dict(best_feasible=6.0), 5.0), 0.2)


class Seeds(unittest.TestCase):
    def test_injective_and_in_range(self):
        seen = set()
        for p, sizes in (("fxt", 3), ("rehearsal", 20), ("test", 480)):
            for n in m.NETWORKS:
                for j in range(5):
                    for s in range(1, sizes + 1):
                        v = m.seed63(p, n, j, s)
                        self.assertNotIn(v, seen)
                        seen.add(v)
                        self.assertLess(v, 2 ** 32)
        self.assertEqual(m.seed63("test", "case30", 2, 1), 1_700_000_000 + 3 * 10 ** 7 + 2 * 10 ** 4 + 1)

    def test_tasks_pair_arms_by_seed(self):
        a = m.task63("case39", 3, "FR", "AD-N", "test", 7)
        b = m.task63("case39", 3, "SP", "FX-T", "test", 7, fixed=m.FXT_GRID[0])
        self.assertEqual(a["seed"], b["seed"])
        self.assertEqual((a["budget"], a["stop"], a["reference"]), (12000, False, None))

    def test_scenarios_are_new(self):
        self.assertEqual([m.i61.scenario(j) for j in range(5)],
                         [(0.97, 6101), (1.03, 6102), (0.92, 630201), (1.02, 630202), (1.08, 630203)])


class Calibration(unittest.TestCase):
    def test_tie_goes_to_first_index(self):
        self.assertEqual(m.select_config([5, 9, 9, 1]), 1)
        self.assertEqual(m.select_config([0] * 27), 0)

    def test_totals(self):
        grid = m.FXT_GRID
        r = {"case30|0": 10.0}
        recs = []
        for k, g in enumerate(grid):
            recs.append(dict(task=dict(network="case30", j=0, s=1, cht="SP", fixed=list(g)), best_feasible=10.0 + 0.1 * k))
        totals = m.calibration_totals(recs, "SP", r)
        self.assertEqual(len(totals), 27)
        self.assertEqual(totals[0], 2 * 26)          # lowest loss wins against everybody
        self.assertEqual(totals[-1], 0)
        self.assertEqual(m.select_config(totals), 0)
        self.assertEqual(sum(totals), 27 * 26)       # every pair splits 2 points


class Decision(unittest.TestCase):
    def test_decide(self):
        rng = np.random.default_rng(0)
        pos = rng.normal(0.3, 0.01, 2000)
        self.assertTrue(m.decide(pos, True)["positive"])
        near0 = rng.normal(0.0, 0.01, 2000)
        d = m.decide(near0, True)
        self.assertTrue(d["equivalent"] and not d["positive"] and not d["negative"])
        self.assertFalse(m.decide(near0, False)["equivalent"])   # degenerate network blocks equivalence
        self.assertTrue(m.decide(-pos, True)["negative"])

    def test_bootstrap_degenerate_blocks_equivalence(self):
        cells = {(n, j): [0.0] * 30 for n in m.NETWORKS for j in (2, 3)}
        out = m.bootstrap(cells, reps=500)
        self.assertEqual(out["estimate"], 0.0)
        self.assertFalse(out["equivalent"])
        cells[("case30", 2)][0] = 0.5
        for k in cells:
            cells[k][1] = 0.5
        self.assertTrue(m.bootstrap(cells, reps=500)["estimate"] > 0)

    def test_bootstrap_equal_weights(self):
        cells = {("case30", 2): [1.0] * 10, ("case30", 3): [0.0] * 10, ("case39", 2): [0.0] * 10, ("case24_ieee_rts", 2): [0.0] * 10}
        self.assertAlmostEqual(m.bootstrap(cells, reps=200)["estimate"], (0.5 + 0 + 0) / 3)


class Power(unittest.TestCase):
    def pools(self):
        rng = np.random.RandomState(1)
        return {n: list(rng.choice([-1.0, -0.5, 0.0, 0.5, 1.0], size=40, p=[0.05, 0.15, 0.5, 0.2, 0.1])) for n in m.NETWORKS}

    def test_tilt_attains_target_and_ess_rule(self):
        pools = self.pools()
        for t in m.TARGETS:
            tl = m.tilt63(pools, t)
            self.assertIsNotNone(tl)
            self.assertLess(tl["error"], 1e-8)
            self.assertEqual(tl["n_pool"], [40, 40, 40])
        self.assertIsNone(m.tilt63(pools, 5.0))

    def test_simulation_rates(self):
        pools = self.pools()
        tilts = {("pooled", t): m.tilt63(pools, t) for t in m.TARGETS}
        rng = np.random.default_rng(7)
        cells = [(n, j) for n in m.NETWORKS for j in (2, 3)]
        pos = sum(m.simulate_once(pools, tilts[("pooled", 0.05)], cells, 240, 400, rng)["positive"] for _ in range(60))
        null = sum(m.simulate_once(pools, tilts[("pooled", 0.0)], cells, 240, 400, rng)["positive"] for _ in range(60))
        self.assertGreater(pos, null)
        self.assertLessEqual(null, 12)


class SmokeRun(unittest.TestCase):
    def test_instrument_record_fields(self):
        t = m.task63("case30", 2, "FR", "AD-N", "rehearsal", 1)
        t["budget"] = 60
        rec = m.i61.run(t)
        self.assertTrue(rec["ok"], rec.get("error"))
        self.assertEqual(rec["calls"], 60)
        self.assertIn("best_feasible", rec)
        self.assertEqual(len(rec["generated"]), 32)


if __name__ == "__main__":
    unittest.main()
