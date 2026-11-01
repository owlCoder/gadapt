"""I53 pre-run checks without any power-flow call."""
import math

import numpy as np

from research import iteration53_oracle_step as i53
from research.iteration53_oracle_step import gadapt_run


class Quadratic:
    """Stands in for Dispatch: same evaluate() contract, no power flow."""

    def __init__(self, x_star):
        self.x_star = np.asarray(x_star, dtype=float)

    def evaluate(self, x):
        v = float(np.sum((np.asarray(x) - self.x_star) ** 2))
        return dict(score=v, converged=True, feasible=v < 1.0, cost=v)


def test_oracle_std_dev_formula_and_clip():
    tracked = i53.Tracked(Quadratic([0, 0, 0, 0]), 10)
    lower, upper = np.zeros(4), np.full(4, 10.0)
    assert i53.oracle_std_dev(tracked, np.zeros(4), lower, upper, 1.0) == 0.6
    tracked.mw([2, 0, 0, 0])
    assert math.isclose(i53.oracle_std_dev(tracked, np.zeros(4), lower, upper, 1.0), 0.2 / 2)
    assert math.isclose(i53.oracle_std_dev(tracked, np.zeros(4), lower, upper, 0.1), 0.02 / 2)
    tracked.mw([0, 0, 0, 0])
    assert i53.oracle_std_dev(tracked, np.zeros(4), lower, upper, 1.0) == 1e-12


def test_tracked_counts_budget_and_best():
    tracked = i53.Tracked(Quadratic([1, 1]), 2)
    tracked.mw([0, 0]); tracked.mw([1, 1]); tracked.mw([5, 5])
    assert tracked.calls == 2 and tracked.over_budget == 1 and tracked.best_feasible == 0.0
    assert tracked.best_score == 0.0 and tracked.best_x.tolist() == [1.0, 1.0]


def test_oracle_patch_is_used_and_restored():
    original = i53.ColumnarMutator._calculate_normal_distribution_standard_deviation
    x_star = np.array([1.0, -2.0, 0.5])
    tracked = i53.Tracked(Quadratic(x_star), 300)
    lower, upper = np.full(3, -5.0), np.full(3, 5.0)
    calls = []

    def patched(self):
        calls.append(1)
        return i53.oracle_std_dev(tracked, x_star, lower, upper, 1.0)

    i53.ColumnarMutator._calculate_normal_distribution_standard_deviation = patched
    try:
        gadapt_run(tracked.mw, list(zip(lower, upper)), 1, lambda: tracked.done)
    finally:
        i53.ColumnarMutator._calculate_normal_distribution_standard_deviation = original
    assert calls and tracked.calls == 300
    assert i53.ColumnarMutator._calculate_normal_distribution_standard_deviation is original


def test_with_oracle_restores_after_exception():
    original = i53.ColumnarMutator._calculate_normal_distribution_standard_deviation

    def boom():
        raise RuntimeError("boom")

    try:
        i53.with_oracle(1.0, None, np.zeros(2), np.zeros(2), np.ones(2), boom)
    except RuntimeError:
        pass
    assert i53.ColumnarMutator._calculate_normal_distribution_standard_deviation is original


def test_synthetic_problems_optimum_and_rotation():
    for problem in i53.SYNTH_PROBLEMS:
        s = i53.Synthetic(problem, 5400)
        assert s.evaluate(s.x_star)["score"] == 0.0
        assert np.allclose(s.rotation @ s.rotation.T, np.eye(i53.SYNTH_N))
    assert not np.allclose(i53.Synthetic("rotated_ellipsoid", 5400).rotation, np.eye(i53.SYNTH_N))


def test_reset_factor_controls_uniform_resets():
    from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (
        RandomDecisionVariableMutator,
    )
    original = RandomDecisionVariableMutator._make_mutated_value
    counts = {}
    for reset in (True, False):
        calls = []

        def counted(self, _calls=calls):
            _calls.append(1)
            return original(self)

        RandomDecisionVariableMutator._make_mutated_value = counted
        try:
            tracked = i53.Tracked(Quadratic(np.zeros(4)), 300)
            gadapt_run(tracked.mw, [(-5.0, 5.0)] * 4, 3, lambda: tracked.done, reset=reset)
        finally:
            RandomDecisionVariableMutator._make_mutated_value = original
        counts[reset] = len(calls)
    assert counts[True] > 0 and counts[False] == 0


def test_dispatch_analysis_decides_on_orn_vs_g0():
    """Synthetic run records: ORN at CMA level on every case -> SUPPORTED; all arms present and used."""
    reference = {c: {"best_score": 100.0} for c in i53.CASES}
    level = {"g0": 1e3, "gn": 1e2, "or1": 1e2, "orn": 1e-3, "orn01": 1e1, "cma": 1e-3}
    runs = [dict(case=c, method=m, seed=s, best_score=100.0 + level[m] * (1 + 0.01 * k), best_feasible_cost=None)
            for c in i53.CASES for m in i53.METHODS for k, s in enumerate(i53.SEEDS)]
    # a secondary arm far below the reference must not change the primary decision
    runs.append(dict(case="case14", method="orn01", seed=-1, best_score=-1e9, best_feasible_cost=None))
    out = i53.analyse(runs, reference)
    assert out["case14"]["below_reference"]["orn01"] == 1
    assert out["decision"]["verdict"] == "SUPPORTED"
    assert set(out["case14"]["closure"]) == {"gn", "or1", "orn", "orn01"}
    assert out["case14"]["holm_p"]["primary"] < i53.ALPHA
    level["orn"] = 1e2
    runs = [dict(case=c, method=m, seed=s, best_score=100.0 + level[m] * (1 + 0.01 * k), best_feasible_cost=None)
            for c in i53.CASES for m in i53.METHODS for k, s in enumerate(i53.SEEDS)]
    assert i53.analyse(runs, reference)["decision"]["verdict"] == "REFUTED"


def test_synthetic_analysis_runs_on_fake_records():
    level = {"DR": 1e-2, "DN": 1e-3, "FR": 1e-2, "FN": 1e-4, "OR": 1e-3, "ON": 1e-8, "CMA": 1e-9}
    runs = [dict(problem=p, arm=a, seed=s, gap=level[a] * (1 + 0.01 * k))
            for p in i53.SYNTH_PROBLEMS for a in level for k, s in enumerate(i53.SYNTH_SEEDS)]
    out = i53.analyse_synthetic(runs)
    assert out["A1"] is True and out["A2"] is False
    assert set(out["contrasts_holm"]) == {"F_vs_D_reset", "F_vs_D_noreset", "N_vs_R_default", "N_vs_R_oracle",
                                          "O_vs_D_noreset"}
