import os, sys
import numpy as np
import pytest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e_common as e, e_algos as a

MENTOR = os.environ.get("MBENCH")
ALGOS = ["cma", "ipop", "bipop", "es11", "de", "gadapt", "gadapt_preset", "pygad_random", "pygad_adaptive"]


@pytest.mark.parametrize("name", ALGOS)
def test_exact_budget_and_progress(name):
    if name.startswith("pygad") and not MENTOR:
        pytest.skip("MBENCH not set")
    d, B = 4, 600
    b = e.Budget(lambda y: float(np.sum((np.asarray(y) - 0.3) ** 2)), B)
    kw = dict(mentor_dir=MENTOR) if name.startswith("pygad") else {}
    try:
        a.RUNNERS[name](b, d, 7, **kw)
        pytest.fail("runner returned without BudgetReached")
    except e.BudgetReached:
        pass
    assert b.n == B, (name, b.n)
    assert b.best < 0.2 and np.isfinite(b.best)
