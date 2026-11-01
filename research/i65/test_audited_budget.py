"""Research-only deterministic model and adversarial regression tests."""
import copy
import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from audited_budget import AuditedBudget, BudgetReached
from stagnation_reference import StagnationMonitor


def f(x):
    return float((np.asarray(x, float)**2).sum())


@pytest.mark.parametrize('B', [2, 3, 4, 10, 12000])
def test_exact_bound_search_and_witness(B):
    calls = []
    def obj(x):
        calls.append(tuple(x))
        return f(x)
    b = AuditedBudget(obj, B)
    for k in range(B-1):
        b([1.0/(k+1)])
    assert b.attempts == B-1 == len(calls)
    with pytest.raises(BudgetReached):
        b([0])
    assert b.attempts == B-1
    out = b.verify(lambda x: f(x), bounds=([0.], [1.]))
    assert out['status'] == 'VALIDATED_WITNESS'
    assert b.attempts == B
    assert len(b.records) == B
    with pytest.raises(BudgetReached):
        b([0])


def test_probe_callback_restart_polish_and_duplicate_are_physical():
    b = AuditedBudget(f, 6)
    for p in ('probe', 'init', 'search', 'callback', 'polish'):
        b.evaluate([1], phase=p)
    assert b.attempts == 5
    assert [r.phase for r in b.records] == ['probe','init','search','callback','polish']
    assert b.best == 1.0
    assert b.best_at == 1
    assert b.verify(lambda x: f(x))['status'] == 'VALIDATED_WITNESS'
    assert len(b.records) == 6


def test_exception_is_counted_before_invoking_callback():
    n = [0]
    def bad(x):
        n[0] += 1
        raise ArithmeticError('real attempt')
    b = AuditedBudget(bad, 3)
    for _ in range(2):
        with pytest.raises(ArithmeticError):
            b([3])
    assert b.attempts == n[0] == 2
    assert [r.outcome for r in b.records] == ['exception','exception']
    assert b.verify(f)['status'] == 'NOT_SOLVED'  # no search witness
    assert b.attempts == 2
    with pytest.raises(BudgetReached): b([3])


def test_nonfinite_and_negative_finite_values():
    vals = iter([float('nan'), float('inf'), float('-inf'), -6.0, -6.0])
    b = AuditedBudget(lambda x: next(vals), 6)
    for k in range(5): b([k])
    assert b.attempts == 5
    assert [r.outcome for r in b.records] == ['nonfinite']*3+['finite','finite']
    assert b.best_x == (3.,) and b.best == -6. and b.best_at == 4
    assert b.verify(lambda x: -6.)['status'] == 'VALIDATED_WITNESS'


def test_callback_mutates_its_input_without_corrupting_witness():
    b = AuditedBudget(lambda x: (float(x[0]*x[0]), x.__setitem__(0, 900))[0], 2)
    caller = np.array([2.0]); assert b(caller) == 4.
    assert caller.tolist() == [2.0]
    assert b.best_x == (2.,)
    assert b.records[0].x == (2.,)
    assert b.verify(lambda x: (float(x[0]*x[0]), x.__setitem__(0, 777))[0])['status'] == 'VALIDATED_WITNESS'
    assert b.best_x == (2.,)


def test_witness_not_allowed_to_modify_search_incumbent():
    b = AuditedBudget(f, 2); b([2.])
    assert b.verify(lambda x: -999.)['status'] == 'INVALID_RESULT'
    assert b.best == 4. and b.best_at == 1
    assert b.records[-1].phase == 'recheck'


def test_failed_or_nonfinite_witness_is_invalid():
    for cb, cause in [(lambda x: float('nan'), 'recheck_nonfinite'),
                      (lambda x: (_ for _ in ()).throw(ZeroDivisionError()), 'recheck_exception')]:
        b = AuditedBudget(f, 2); b([2])
        res = b.verify(cb)
        assert res['status'] == 'INVALID_RESULT' and res['reason'] == cause
        assert b.attempts == 2


def test_independent_witness_must_be_separate_callable():
    b = AuditedBudget(f, 2); b([2])
    with pytest.raises(ValueError, match='independent'):
        b.verify(f)
    assert b.attempts == 1  # invalid witness setup must NOT consume budget
    assert b.verify(lambda x: f(x))['status'] == 'VALIDATED_WITNESS'


def test_outside_bounds_and_no_witness_skip_physical_call():
    b = AuditedBudget(f, 2); b([10])
    d = b.verify(lambda x: f(x), bounds=([0], [5]))
    assert d['status'] == 'INVALID_RESULT' and d['reason'] == 'out_of_bounds'
    assert b.attempts == 1


def test_invalid_logical_arguments_dont_consume_physical_calls():
    b = AuditedBudget(f, 3)
    for x in ([], [[2.]], ["bad"]):
        with pytest.raises((ValueError, TypeError)):
            b(x)
    with pytest.raises(ValueError, match='unknown phase'):
        b.evaluate([1], phase='fake')
    with pytest.raises(ValueError, match='independent'):
        b.evaluate([1], evaluator=lambda x: f(x))
    assert b.attempts == len(b.records) == 0


@pytest.mark.parametrize('B', [0, 1, -1, 4.0, True])
def test_invalid_budget_rejected(B):
    with pytest.raises(ValueError): AuditedBudget(f, B)


def test_no_witness_mode_budget_one():
    b = AuditedBudget(f, 1, reserve_witness=False)
    assert b([1.]) == 1.
    with pytest.raises(BudgetReached): b([0.])
    with pytest.raises(RuntimeError): b.verify(lambda x: f(x))
    assert b.attempts == 1


def test_deepcopy_shares_physical_counter():
    b = AuditedBudget(f, 3)
    assert copy.deepcopy(b) is b
    copy.deepcopy(b)([2]); b([1]); assert b.attempts == 2


def test_replay_in_two_separate_python_processes():
    here = str(Path(__file__).parent)
    script = """from audited_budget import AuditedBudget\nimport numpy as np\nb=AuditedBudget(lambda x:float(np.sum(x*x)), 50)\nfor k in range(49): b(np.random.default_rng([99,k]).uniform(size=3))\nb.verify(lambda x:float(np.sum(x*x)))\nprint(b.trace_hash())"""
    env = {**os.environ, 'PYTHONPATH': here}
    a = subprocess.check_output([sys.executable, '-c', script], env=env, text=True).strip()
    c = subprocess.check_output([sys.executable, '-c', script], env=env, text=True).strip()
    assert a == c and len(a)==64


def test_randomized_differential_accounting_100_fixed_seeds():
    for seed in range(100):
        rng = random.Random(seed)
        seen = []
        def obj(x):
            kind = rng.choice(['finite', 'finite','negative','nan','raise'])
            x[0] = 1e9  # evaluator mutates its own buffer
            if kind == 'raise':
                seen.append(('exception',None))
                raise ArithmeticError
            val = float('nan') if kind == 'nan' else (-seed-.5 if kind=='negative' else seed+.5)
            seen.append((kind,val))
            return val
        B = 15
        b=AuditedBudget(obj,B)
        for i in range(B-1):
            try: b([float(i)])
            except ArithmeticError: pass
            assert len(b.records) == b.attempts == len(seen) == i+1
            assert b.records[-1].x == (float(i),)
            good = [v for _,v in seen if v is not None and math.isfinite(v)]
            assert b.best == (min(good) if good else math.inf)
        with pytest.raises(BudgetReached): b([0.])
        assert b.attempts == B-1
        if b.best_x is not None:
            v = b.best
            assert b.verify(lambda x: v)['status']=='VALIDATED_WITNESS'
            assert b.attempts == B


def test_stagnation_20_with_total_physical_attempts():
    m=StagnationMonitor(100,eps_abs=0.,eps_rel=0.,patience=20)
    for k in range(19): assert m.complete_generation(100., 64+7*(k+1)) is None
    e=m.complete_generation(100.,64+7*20)
    assert e == {'type':'STAGNATION','at_generation':20,'at_evaluations':204,'best':100.}
    assert m.complete_generation(100.,210) is None  # no repeated event


def test_stagnation_rearm_after_meaningful_improvement():
    m=StagnationMonitor(100.,eps_abs=0.01,eps_rel=0.,patience=2)
    m.complete_generation(100.,10)
    assert m.complete_generation(100.,20)['at_generation']==2
    assert m.complete_generation(99.98,30) is None
    m.complete_generation(99.98,40)
    assert m.complete_generation(99.98,50)['at_generation']==5
    assert len(m.events)==2


def test_stagnation_relative_rule_additive_shift_sensitivity():
    # A scientifically important limitation: raw best value is sensitive to
    # additive offsets for eps_rel>0. Not a bug in the specified formula.
    a=StagnationMonitor(1.,eps_abs=0.,eps_rel=.01,patience=1)
    b=StagnationMonitor(1001.,eps_abs=0.,eps_rel=.01,patience=1)
    assert a.complete_generation(.5,1) is None
    assert b.complete_generation(1000.5,1)['type']=='STAGNATION'


@pytest.mark.xfail(strict=True,reason='Original reference monitor does not validate nonmonotone evaluation timestamps')
def test_original_monitor_rejects_nonmonotone_timestamp():
    m=StagnationMonitor(1., patience=2)
    m.complete_generation(1.,100)
    with pytest.raises(ValueError): m.complete_generation(1.,5)
