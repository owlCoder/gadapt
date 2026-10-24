"""I58 instrument and checker validation (research/ITERATION58_PROTOCOL.md)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import iteration58_validation as i58  # noqa: E402
from iteration56_orpd import ORPD  # noqa: E402


def test_bus_orpd_equals_i56_instrument_with_one_generator_per_bus():
    for network in ("case30", "case39"):
        bus, plain = i58.make_problem(network, 1), ORPD(network, 17, 1.00, 0.1, 302)
        assert bus.d == plain.d
        rng = np.random.RandomState(0)
        for _ in range(5):
            x = plain.lo + rng.random_sample(plain.d) * (plain.hi - plain.lo)
            a, b = bus.evaluate(x), plain.evaluate(x)
            assert a["converged"] == b["converged"] and a["losses"] == b["losses"] and a["violations"] == b["violations"]


def test_case24_has_one_voltage_control_per_generator_bus():
    problem = i58.make_problem("case24_ieee_rts", 0)
    assert len(problem.bus_groups) == 11
    assert problem.d == 11 + len(problem.tap_rows) + len(problem.shunt_rows)


def test_independent_checker_agrees_with_the_instrument():
    for network in ("case30", "case39", "case24_ieee_rts"):
        problem = i58.make_problem(network, 0)
        rng = np.random.RandomState(1)
        for _ in range(4):
            x = problem.snap(problem.lo + rng.random_sample(problem.d) * (problem.hi - problem.lo))
            a, b = problem.evaluate(x), i58.independent_check(network, 0, x)
            assert a["converged"] == b["converged"]
            if a["converged"]:
                assert abs(a["losses"] - b["losses"]) < 1e-9
                for k in a["violations"]:
                    assert abs(a["violations"][k] - b["violations"][k]) < 1e-9, (network, k)
