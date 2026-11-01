"""Fast fail-closed lifecycle regressions; no optimizer experiments."""

import numpy as np
import pytest

from audited_budget import AuditedBudget, BudgetReached


def sphere(x):
    return float(np.sum(np.asarray(x, dtype=float) ** 2))


@pytest.mark.parametrize('phase', sorted(AuditedBudget.ALLOWED - {'recheck'}))
def test_early_valid_witness_seals_all_search_phases(phase):
    b = AuditedBudget(sphere, 8)
    assert b([2.]) == 4.
    result = b.verify(lambda x: sphere(x))
    assert result['status'] == 'VALIDATED_WITNESS'
    before = (b.attempts, b.best, b.best_x, b.best_at, b.trace_hash())
    with pytest.raises(BudgetReached):
        b.evaluate([0.], phase=phase)
    assert (b.attempts, b.best, b.best_x, b.best_at, b.trace_hash()) == before
    with pytest.raises(RuntimeError, match='already checked'):
        b.verify(lambda x: sphere(x))


def test_early_mismatched_witness_also_seals_search():
    b = AuditedBudget(sphere, 7)
    b([2.])
    out = b.verify(lambda x: sphere(x) + 42.)
    assert out['status'] == 'INVALID_RESULT' and out['reason'] == 'objective_mismatch'
    assert b.attempts == 2
    with pytest.raises(BudgetReached):
        b([1.])
    assert b.best == 4. and b.best_at == 1


@pytest.mark.parametrize('bad', [float('nan'), float('inf')])
def test_early_nonfinite_witness_seals_search(bad):
    b = AuditedBudget(sphere, 6)
    b([2.])
    assert b.verify(lambda x: bad)['reason'] == 'recheck_nonfinite'
    with pytest.raises(BudgetReached):
        b.evaluate([0.], phase='callback')
    assert b.attempts == 2


@pytest.mark.parametrize('exc', [ArithmeticError('simulation failed'), BudgetReached()])
def test_exception_inside_witness_is_invalid_and_seals_search(exc):
    b = AuditedBudget(sphere, 6)
    b([2.])

    def failed_witness(x):
        raise exc

    out = b.verify(failed_witness)
    assert out['status'] == 'INVALID_RESULT'
    assert out['reason'] == 'recheck_exception'
    assert out['error_type'] == type(exc).__name__
    assert b.attempts == len(b.records) == 2
    assert b.records[-1].outcome == 'exception'
    assert b.records[-1].phase == 'recheck'
    with pytest.raises(BudgetReached):
        b([0.])


def test_direct_recheck_is_not_a_validation_result_but_seals_search():
    b = AuditedBudget(sphere, 6)
    b([2.])
    assert b.evaluate([2.], phase='recheck', evaluator=lambda x: -99.) == -99.
    assert b.best == 4. and b.attempts == 2
    with pytest.raises(BudgetReached):
        b([0.])
    with pytest.raises(RuntimeError, match='already checked'):
        b.verify(lambda x: sphere(x))


def test_invalid_preflight_does_not_consume_witness_or_seal():
    b = AuditedBudget(sphere, 5)
    b([2.])
    assert b.verify(lambda x: sphere(x), bounds=([float('nan')], [3.]))['reason'] == 'invalid_bounds'
    with pytest.raises(ValueError, match='independent'):
        b.verify(sphere)
    assert b.attempts == 1 and not b.checked
    assert b([1.]) == 1.
    assert b.verify(lambda x: sphere(x))['status'] == 'VALIDATED_WITNESS'
    assert b.attempts == 3


def test_no_witness_reservation_still_permits_search_up_to_b():
    b = AuditedBudget(sphere, 3, reserve_witness=False)
    for v in (3., 2., 1.):
        assert b([v]) == v * v
    assert b.attempts == 3
    with pytest.raises(BudgetReached):
        b([0.])
    with pytest.raises(RuntimeError, match='no witness'):
        b.verify(lambda x: sphere(x))
