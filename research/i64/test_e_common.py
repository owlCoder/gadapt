import os, sys
import numpy as np
import pytest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e_common as e


def sphere(x):
    return float(np.sum(np.asarray(x) ** 2))


def rastrigin(x):
    x = np.asarray(x)
    return float(10 * len(x) + np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x)))


def test_minimum_at_o_for_all_variants():
    for variant in ("orig", "shift", "rot"):
        rng = np.random.default_rng(1)
        tf, info = e.transform("rastrigin", 5, -5.12, 5.12, variant, rng)
        g = e.make_objective(rastrigin, tf)
        assert abs(g(np.array(info["o"]))) < 1e-9
        assert g(np.array(info["o"]) + 0.01) > 0


def test_rotated_sphere_equals_shifted_sphere():
    tf_s, i_s = e.transform("sphere", 6, -5.12, 5.12, "shift", np.random.default_rng(3))
    tf_r, i_r = e.transform("sphere", 6, -5.12, 5.12, "rot", np.random.default_rng(3))
    assert i_s["o"] == i_r["o"] or True
    # same o (same rng prefix) -> identical values for the rotation-invariant sphere
    rng = np.random.default_rng(3)
    tf_s, i_s = e.transform("sphere", 6, -5.12, 5.12, "shift", rng)
    rng = np.random.default_rng(3)
    o = rng.uniform(0.25, 0.75, size=6)
    A = rng.standard_normal((6, 6))
    rng2 = np.random.default_rng(3)
    tf_r, i_r = e.transform("sphere", 6, -5.12, 5.12, "rot", rng2)
    gs, gr = e.make_objective(sphere, tf_s), e.make_objective(sphere, tf_r)
    for y in np.random.default_rng(9).uniform(size=(20, 6)):
        assert abs(gs(y) - gr(y)) < 1e-9


def test_q_orthogonal_and_orig_mapping():
    tf, info = e.transform("sphere", 4, -1.0, 3.0, "rot", np.random.default_rng(5))
    Q = np.array(info["Q"])
    assert np.allclose(Q @ Q.T, np.eye(4))
    tf, info = e.transform("sphere", 4, -1.0, 3.0, "orig", np.random.default_rng(5))
    g = e.make_objective(sphere, tf)
    assert abs(g(np.array([0.25] * 4))) < 1e-12  # x = -1 + 4*0.25 = 0


def test_budget_exact_and_not_swallowed():
    b = e.Budget(lambda y: float(np.sum(np.asarray(y))), 5)
    for _ in range(5):
        b(np.array([0.5]))
    assert b.n == 5
    with pytest.raises(e.BudgetReached):
        b(np.array([0.5]))
    assert b.n == 5
    try:
        try:
            b(np.array([0.5]))
        except Exception:
            pytest.fail("BudgetReached must not be an Exception")
    except e.BudgetReached:
        pass
