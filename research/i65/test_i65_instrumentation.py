import copy
import hashlib
import math
import random
import numpy as np
import pytest
from e_common_snapshot import Budget, BudgetReached
from stagnation_reference import StagnationMonitor, AttemptBudget


def test_original_last_call_and_b_plus_one():
    physical=[]
    b=Budget(lambda x: physical.append(tuple(x)) or float(sum(x)), 3)
    assert [b([v]) for v in (3,2,1)] == [3,2,1]
    with pytest.raises(BudgetReached): b([0])
    assert b.n == len(physical) == 3
    assert b.events == [(1,3.0),(2,2.0),(3,1.0)]
    assert b.best_y == [1.0]


def test_original_validation_probe_and_duplicate_count():
    physical=[]
    b=Budget(lambda x: physical.append(tuple(x)) or 9., 4)
    for name, x in [('allmin',[0]),('allmax',[1]),('search',[1]),('callback',[1])]:
        b(x)
    assert len(physical)==b.n==4
    assert b.events == [(1,9.0)]
    with pytest.raises(BudgetReached): b([1])


def test_original_nonfinite_and_tie():
    values=iter([float('nan'),float('inf'),2.,2.,float('-inf')])
    b=Budget(lambda x: next(values),5)
    for _ in range(5):
        try: b([4])
        except TypeError:
            pytest.fail('objective must accept positional vector')
    assert b.n == 5
    assert b.best == 2.
    assert b.events == [(3,2.)]


def test_original_deepcopy_identity_for_ga():
    b=Budget(lambda x: 1., 2)
    assert copy.deepcopy(b) is b
    copy.deepcopy(b)([0])
    assert b.n == 1


def test_stagnation_exact_20_completed_generations():
    m=StagnationMonitor(5.,eps_abs=0.,eps_rel=0.)
    for k in range(1,20):
        assert m.complete_generation(5., k*64) is None
    evt=m.complete_generation(5.,20*64)
    assert evt == dict(type='STAGNATION',at_generation=20,at_evaluations=1280,best=5.)
    assert m.complete_generation(5.,21*64) is None
    assert len(m.events)==1


def test_stagnation_strict_threshold_and_reset():
    m=StagnationMonitor(100.0,eps_abs=0.5,eps_rel=0.01,patience=3)
    assert m.complete_generation(98.5,64) is None # equality -> not meaningful
    assert m.no_improvement==1
    assert m.complete_generation(96.0,128) is None # 2.5 > 1.485 -> reset
    assert m.no_improvement==0
    assert m.complete_generation(96.,192) is None
    assert m.complete_generation(96.,256) is None
    assert m.complete_generation(96.,320)['type']=='STAGNATION'
    m.restart()
    assert m.no_improvement==0
    assert m.complete_generation(96.,384) is None


def test_stagnation_zero_negative_and_small_changes():
    m=StagnationMonitor(0.,eps_abs=1e-4,eps_rel=0.,patience=2)
    assert m.complete_generation(-0.0001, 2) is None
    assert m.complete_generation(-0.00019, 3)['type']=='STAGNATION'
    assert m.complete_generation(-1,4) is None
    assert m.no_improvement==0


def test_incomplete_generation_never_triggers():
    m=StagnationMonitor(4.,patience=20)
    for i in range(19): m.complete_generation(4.,i+1)
    # Budget cut mid-generation: no complete_generation() call
    assert m.events==[]


def test_invalid_nonfinite_baseline():
    with pytest.raises(ValueError): StagnationMonitor(math.inf)
    m=StagnationMonitor(1.)
    with pytest.raises(ValueError): m.complete_generation(math.nan,1)
    with pytest.raises(ValueError): m.complete_generation(1.1,1)


def test_restart_independent_of_generation_cost():
    m=StagnationMonitor(0.,patience=2,eps_abs=0.,eps_rel=0.)
    assert m.complete_generation(0.,10) is None
    assert m.complete_generation(0.,170)['at_evaluations']==170
    m.restart()
    assert m.complete_generation(0.,171) is None
    assert m.complete_generation(0.,250)['at_evaluations']==250


def test_replay_same_rng_same_event_hash():
    def run(seed):
        rng=random.Random(seed)
        m=StagnationMonitor(4.,eps_abs=0.001,eps_rel=0.,patience=20)
        for k in range(90):
            trial=4.0-rng.randint(0,7)*0.0002
            m.complete_generation(min(m.best,trial), k*13)
        return hashlib.sha256(repr((m.best,m.events)).encode()).hexdigest()
    assert run(171)==run(171)


def test_attempt_budget_counts_failed_calls():
    n=[0]
    def throws(x):
        n[0]+=1
        raise ArithmeticError('failed physical computation')
    b=AttemptBudget(throws,2)
    for i in range(2):
        with pytest.raises(ArithmeticError): b([i])
    with pytest.raises(RuntimeError,match='BUDGET_EXHAUSTED'): b([3])
    assert n[0]==b.attempts==2


@pytest.mark.xfail(strict=True,reason='I64 Budget increments only AFTER objective returns, undercounts raised attempts')
def test_original_budget_counts_failed_evaluation_attempts():
    n=[0]
    def throws(x):
        n[0]+=1
        raise ArithmeticError('real evaluation attempted')
    b=Budget(throws,2)
    for _ in range(2):
        with pytest.raises(ArithmeticError): b([0])
    assert b.n==n[0]==2  # KNOWN FAIL: n is 0 despite two physical attempts


@pytest.mark.xfail(strict=True,reason='I64 Budget snapshots witness AFTER objective, fails if input was mutated in place')
def test_original_budget_snapshots_witness_before_evaluation():
    def mutating_obj(x):
        v=float(x[0]**2)
        x[0]=999.
        return v
    b=Budget(mutating_obj,1)
    x=[2.]
    assert b(x)==4.
    assert b.best_y==[2.]  # KNOWN FAIL: [999] recorded
