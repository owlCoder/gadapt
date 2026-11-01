"""Research-only fail-closed evaluator preflight tests, not optimizer benchmarks."""
import math
import numpy as np
import pytest
from audited_budget import AuditedBudget, BudgetReached


def constant_cost(x):
    return 1.0


@pytest.mark.parametrize("bad", [[math.nan], [math.inf], [-math.inf], [1., math.nan]])
def test_invalid_coordinate_rejected_before_physical_attempt(bad):
    objective_calls = []
    b = AuditedBudget(lambda x: objective_calls.append(1) or constant_cost(x), 3)
    with pytest.raises(ValueError, match="finite candidate"):
        b(bad)
    assert not objective_calls and b.attempts == 0 and not b.records


@pytest.mark.parametrize("bounds", [
    ([math.nan], [1.]), ([0.], [math.nan]),
    ([2.], [1.]), ([0., 0.], [1., 1.]),
    ([-math.inf], [math.inf]),
])
def test_invalid_bounds_cannot_validate_witness(bounds):
    b = AuditedBudget(constant_cost, 2)
    b([0.5])
    out = b.verify(lambda x: constant_cost(x), bounds=bounds)
    assert out["status"] == "INVALID_RESULT"
    assert out["reason"] == "invalid_bounds"
    assert b.attempts == 1 and not b.checked


@pytest.mark.parametrize("value", [math.nan, -1., math.inf, -math.inf])
@pytest.mark.parametrize("name", ["rtol", "atol"])
def test_invalid_tolerance_rejected_before_witness_call(value, name):
    b = AuditedBudget(constant_cost, 2)
    b([0.5])
    with pytest.raises(ValueError, match="invalid witness tolerances"):
        b.verify(lambda x: constant_cost(x), **{name: value})
    assert b.attempts == 1 and not b.checked


def test_legal_bounds_tolerances_and_final_budget_boundary():
    calls = []
    def objective(x):
        calls.append(tuple(x))
        return float(np.sum(x * x))
    b = AuditedBudget(objective, 3)
    b([2.]); b([1.])
    with pytest.raises(BudgetReached):
        b([0.])
    out = b.verify(lambda x: float(np.sum(x * x)), bounds=([0.], [3.]),
                   rtol=1e-10, atol=1e-12)
    assert out["status"] == "VALIDATED_WITNESS"
    assert b.attempts == 3 and len(calls) == 2
    assert [rec.n for rec in b.records] == [1, 2, 3]


def test_raised_callback_counts_real_attempt_even_with_preflight():
    attempted = []
    def objective(x):
        attempted.append(1)
        raise ArithmeticError("physical failure")
    b = AuditedBudget(objective, 3)
    for _ in range(2):
        with pytest.raises(ArithmeticError):
            b([1.])
    assert b.attempts == len(attempted) == 2
    assert [r.outcome for r in b.records] == ["exception", "exception"]
    assert b.verify(lambda x: 0.)["status"] == "NOT_SOLVED"


def test_invalid_coordinate_cannot_poison_json_trace():
    b = AuditedBudget(lambda x: 1., 3)
    with pytest.raises(ValueError):
        b([math.nan])
    b([1.])
    assert len(b.trace_hash()) == 64
