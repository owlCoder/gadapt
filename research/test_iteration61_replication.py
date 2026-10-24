"""I61 driver checks (research/ITERATION61_PROTOCOL.md); synthetic data only, no I61 result is read."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import iteration56_cht_study as i56  # noqa: E402
import iteration61_replication as i61  # noqa: E402


def test_seeds_are_unique_over_every_planned_task():
    seeds = set()
    plan = dict(dev_ref=((0, 1), [1]), select_b=((0, 1), i61.SELECT_SEEDS), fxt=((0, 1), i61.FXT_SEEDS),
                stopcheck=((0, 1), [1]), rehearsal=((0, 1), i61.REHEARSAL_SEEDS), test_ref=((2, 3, 4), (1, 2)),
                test=((2, 3, 4), range(1, max(i61.N_GRID) + 1)))
    count = 0
    for purpose, (js, ss) in plan.items():
        for n in i61.NETWORKS:
            for j in js:
                for s in ss:
                    seeds.add(i61.seed_of(purpose, n, j, s))
                    count += 1
    assert len(seeds) == count and max(seeds) < 2 ** 32


def test_tilt_reaches_the_target_with_diagnostics():
    rng = np.random.RandomState(0)
    pools = {n: list(rng.normal(0, 0.3, 20)) for n in i61.NETWORKS}
    for theta in (0.0, 0.02):
        t = i61.tilt(pools, theta)
        means = [np.dot(w, pools[n]) for w, n in zip(t["weights"], i61.NETWORKS)]
        assert abs(np.mean(means) - theta) <= 1e-8 and t["error"] <= 1e-8
        assert all(abs(sum(w) - 1) < 1e-12 for w in t["weights"]) and all(1 <= e <= 20 for e in t["ess"])
    assert i61.tilt({n: [0.0] * 20 for n in i61.NETWORKS}, 0.02) is None  # degenerate: unattainable, no imputation


def test_simulation_detects_strong_effects_and_not_zero_effects():
    cells = [(n, j) for n in i61.NETWORKS for j in (2, 3, 4)]
    zero = {n: [0.0] * 20 for n in i61.NETWORKS}
    flat = dict(weights=[[1 / 20] * 20] * 3)
    assert i61.simulate(zero, flat, cells, 80, 20, 200, np.random.default_rng(1)) == 0
    strong = {n: [0.5 + 0.01 * k for k in range(20)] for n in i61.NETWORKS}
    assert i61.simulate(strong, flat, cells, 80, 20, 200, np.random.default_rng(1)) == 20


def test_wilson_bounds():
    lo, hi = i61.wilson(825, 1000)
    assert 0.80 <= lo < 0.825 < hi
    lo, hi = i61.wilson(36, 1000)
    assert lo < 0.036 < hi <= 0.05


def test_bootstrap_matches_the_i56_estimator():
    rng = np.random.RandomState(3)
    cells = {(n, n, j): [{"d": float(x)} for x in rng.normal(0.05, 0.3, 15)] for n in i61.NETWORKS for j in (2, 3)}
    mine = i61.bootstrap(cells, lambda u: u["d"])
    ref = i56.bootstrap(cells, lambda u: u["d"], seed=61)
    assert mine["estimate"] == ref["estimate"] and mine["ci95"] == ref["ci"]
    assert mine["ci95"][0] < mine["ci90"][0] < mine["ci90"][1] < mine["ci95"][1]


class Toy:
    """Tiny deterministic problem with the BusORPD interface (no power flow)."""
    opf_losses = 1.0

    def __init__(self):
        self.d, self.resolution = 4, 17
        self.lo, self.hi = np.zeros(4), np.ones(4)
        self.step = (self.hi - self.lo) / 16

    def evaluate(self, x):
        x = np.asarray(x, float)
        return dict(losses=1.0 + float(np.sum((x - 0.3) ** 2)), violations=dict(v=float(max(0.0, x[0] - 0.8))),
                    converged=True)


def test_stop_at_target_keeps_h_population_and_prefix(monkeypatch):
    monkeypatch.setattr(i61, "make_problem", lambda network, j: Toy())
    base = dict(network="case30", j=0, cht="SP", arm="AD-N", purpose="stopcheck", s=1, seed=12345, budget=600,
                reference=1.05, fixed=None)
    full = i61._run(dict(base, stop=False))
    stopped = i61._run(dict(base, stop=True))
    assert full["ok"] and stopped["ok"] and full["first_target"] is not None
    assert stopped["first_target"] == full["first_target"] == stopped["calls"] < full["calls"] == 600
    assert stopped["generated"] == full["generated"] and len(full["generated"]) == i56.POPULATION_SIZE
    assert stopped["prefix_at_target"] == full["prefix_at_target"]
    assert abs(full["T"] - full["first_target"] / 600) < 1e-15


def test_arms_of_a_unit_share_the_initial_population(monkeypatch):
    monkeypatch.setattr(i61, "make_problem", lambda network, j: Toy())
    records = [i61._run(dict(network="case30", j=0, cht=c, arm=a, purpose="rehearsal", s=1, seed=777, budget=200,
                             reference=None, fixed=[0.5, 0.2, 0.05] if a == "FX-T" else None, stop=False))
               for c, a in i61.ARMS]
    assert all(r["ok"] for r in records)
    i61.assert_paired(records)
