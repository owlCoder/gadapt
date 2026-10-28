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


@pytest.mark.parametrize("name", ["gadapt", "gadapt_preset", "pygad_random", "pygad_adaptive", "de"])
def test_native_domain_budget_exact(name):
    if name.startswith("pygad") and not MENTOR:
        pytest.skip("MBENCH not set")
    d, B = 3, 500
    b = e.Budget(lambda y: float(np.sum((np.asarray(y) - 0.3) ** 2)), B)  # objective on the unit cube; native domain [-5, 5]
    kw = dict(mentor_dir=MENTOR, lo=-5.0, hi=5.0) if name.startswith("pygad") else dict(lo=-5.0, hi=5.0)
    try:
        a.RUNNERS[name](b, d, 3, **kw)
        pytest.fail("no BudgetReached")
    except e.BudgetReached:
        pass
    assert b.n == B and b.best < 0.3


def test_idle_restart_guard():
    b = e.Budget(lambda y: 0.0, 10)
    with pytest.raises(RuntimeError):
        a._restart_loop(lambda rng, k: None, 1, b)
