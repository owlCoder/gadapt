"""I55 pre-run checks: the corrected launcher applies PYTHONHASHSEED (the I50 D3x mutants), traces are complete."""
import sys
import tempfile

import numpy as np
import pytest

from research import iteration55_d3x_traces as i55


@pytest.mark.parametrize("mode, expected", [("-", (0, 0, 0)), ("hash_seeded", (0, 0, 1)), ("time_seeded", (1, 1, 1))])
def test_mutants_give_expected_d3_d3x_same_d3x_diff(mode, expected):
    with tempfile.TemporaryDirectory() as tmp:
        c = i55.audit_cell(sys.executable, "i50", "ref_seeded", "sphere", 2, 1, tmp, mode)
    assert c["manipulation_ok"], c
    assert (c["D3"], c["D3x_same"], c["D3x_diff"]) == expected


def test_trace_is_complete_and_reclassifies_identically():
    import research.iteration49_integrity_audit as i49
    import research.iteration50_integrity_audit as i50
    with tempfile.TemporaryDirectory() as tmp:
        c = i55.audit_cell(sys.executable, "i50", "ref_seeded", "rastrigin", 10, 2, tmp)
        t = np.load(f"{tmp}/rastrigin_10_2.npz")
        problem = i49.Problem("rastrigin", 10)
        calls = [(t["x"][k], float(t["f"][k]), i55.PHASES[t["phase"][k]]) for k in range(len(t["f"]))]
        res = dict(x=t["x_star"], f=float(t["f_star"][0]), reported_evals=int(t["reported_evals"][0]),
                   documented_max=int(t["documented_max"][0]))
        flags, n, _ = i50.classify(calls, res, problem)
    assert n == c["calls"] == i50.BUDGET
    assert flags == c["flags"]
    assert i49.sequence_hash(calls) == c["hash"]
