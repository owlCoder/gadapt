"""I54 pre-run checks without any power-flow call."""
import itertools

import numpy as np

from research import iteration54_oracle_geometry as i54
from research.iteration53_oracle_step import Tracked


class Quadratic:
    def __init__(self, x_star):
        self.x_star = np.asarray(x_star, dtype=float)

    def evaluate(self, x):
        v = float(np.sum((np.asarray(x) - self.x_star) ** 2))
        return dict(score=v, converged=True, feasible=False, cost=v)


def random_covariance(n, seed):
    rng = np.random.default_rng(seed)
    q = np.linalg.qr(rng.standard_normal((n, n)))[0]
    return q @ np.diag(10.0 ** rng.uniform(-4, 0, n)) @ q.T


def test_shape_reproduces_covariance_shape_with_unit_max():
    c = random_covariance(5, 1)
    a = i54.shape(c)
    reconstructed = a @ a.T
    assert np.allclose(reconstructed / np.linalg.eigvalsh(reconstructed).max(), c / np.linalg.eigvalsh(c).max())
    assert np.isclose(np.linalg.svd(a, compute_uv=False).max(), 1.0)


def test_y_box_covers_the_whole_unit_box_and_centre_is_box_centre():
    a = i54.shape(random_covariance(4, 2))
    h = i54.y_half_widths(a)
    inverse = np.linalg.inv(a)
    for corner in itertools.product((0.0, 1.0), repeat=4):
        y = inverse @ (np.array(corner) - 0.5)
        assert np.all(np.abs(y) <= h + 1e-12)
    lower, upper = np.zeros(4), np.full(4, 10.0)
    x, clipped = i54.Whitened(Tracked(Quadratic(np.zeros(4)), 5), a, lower, upper).to_x(np.zeros(4))
    assert np.allclose(x, 5.0) and not clipped


def test_whitened_clips_counts_and_respects_budget():
    a = np.eye(2)
    tracked = Tracked(Quadratic(np.zeros(2)), 2)
    w = i54.Whitened(tracked, a, np.zeros(2), np.ones(2))
    w.cost([0.9, 0.0]); w.cost([0.0, 0.0]); w.cost([0.9, 0.9])
    assert w.clipped == 1 and tracked.calls == 2 and tracked.over_budget == 1
    assert tracked.best_x.tolist() == [0.5, 0.5]


def test_diagonal_shape_has_no_rotation():
    d = i54.diagonal_shape(random_covariance(4, 3))
    assert np.allclose(d, np.diag(np.diag(d))) and np.isclose(d.max(), 1.0)


def test_whitened_gadapt_run_uses_exact_budget():
    from research.iteration53_oracle_step import gadapt_run
    a = i54.shape(random_covariance(3, 4))
    lower, upper = np.full(3, -5.0), np.full(3, 5.0)
    tracked = Tracked(Quadratic([1.0, -2.0, 0.5]), 300)
    w = i54.Whitened(tracked, a, lower, upper)
    h = i54.y_half_widths(a)
    gadapt_run(w.cost, list(zip(-h, h)), 1, lambda: tracked.done)
    assert tracked.calls == 300


def test_analysis_decision():
    reference = {c: {"best_score": 100.0} for c in i54.CASES}

    def runs_for(level):
        return [dict(case=c, method=m, seed=s, best_score=100.0 + level[m] * (1 + 0.01 * k), best_feasible_cost=None,
                     clipped_evaluations=0, calls=3000)
                for c in i54.CASES for m in i54.METHODS for k, s in enumerate(i54.SEEDS)]

    assert i54.analyse(runs_for({"g0": 1e3, "w": 1e0, "wd": 1e2, "cma": 1e-2}), reference)["decision"]["verdict"] == "SUPPORTED"
    assert i54.analyse(runs_for({"g0": 1e3, "w": 5e2, "wd": 1e3, "cma": 1e-2}), reference)["decision"]["verdict"] == "REFUTED"
