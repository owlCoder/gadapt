"""Adapter validation for I57 (research/ITERATION57_PROTOCOL.md): exact budget, grid decoding, scalars."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import iteration57_external as i57  # noqa: E402

BASE = dict(network="case14", resolution=9, scenario_index=0, scenario=[0.95, 101], budget=300, reference=None,
            seed=i57.seed_of("case14", 9, 0, 1))


def test_each_external_method_uses_exactly_the_budget():
    for method, cht in (("CMAwM", "SP"), ("CMAwM", "FR"), ("DE", "SP"), ("DE", "FR"), ("Random", "-")):
        r = i57.run(dict(BASE, method=method, cht=cht))
        assert r["ok"] and r["calls"] == 300, (method, cht, r.get("error"))


def test_scalar_decodes_to_grid_and_applies_fr():
    from iteration56_orpd import ORPD
    import iteration56_cht_study as i56
    problem = ORPD("case14", 9, 0.95, 0.1, 101)
    evaluator = i56.Evaluator(problem, 5, i56.make_target(None))
    scalar = i57.Scalar(problem, evaluator, "FR")
    value = scalar(np.full(problem.d, 3.4))
    key = next(iter(evaluator.cache))
    assert np.allclose(key, problem.lo + 3 * problem.step)
    assert value == i56.CHT("FR", evaluator.f_ref).merit(evaluator.cache[key])
