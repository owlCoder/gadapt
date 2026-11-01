import math
import random
import pytest
from stagnation_checked import CheckedStagnation, StagnationEvent


def test_20_gens_trigger_once_without_initial_population():
    m=CheckedStagnation(10., initial_attempts=64)
    for i in range(19):
        assert m.complete(10., 64+(i+1)*32) is None
    assert m.complete(10., 64+20*32) == StagnationEvent('STAGNATION',20,704,10.)
    assert m.complete(10., 800) is None
    assert len(m.events) == 1


def test_exact_tolerance_is_not_significant():
    m=CheckedStagnation(100., eps_abs=0.5, eps_rel=.01, patience=2)
    assert m.complete(98.5, 1) is None # delta equals threshold
    assert m.complete(98.5, 2) is not None


def test_19_unimproved_then_improvement_resets():
    m=CheckedStagnation(100.,eps_abs=0.,patience=20)
    for k in range(19): m.complete(100.,k+1)
    assert m.complete(99.,20) is None
    for k in range(19): assert m.complete(99.,21+k) is None
    assert m.complete(99.,40) is not None


def test_rearm_on_restart_and_physical_calls_not_reset():
    m=CheckedStagnation(0.,patience=2)
    m.complete(0., 40)
    assert m.complete(0.,41)
    m.restart()
    assert m.complete(0., 41) is None  # complete generation may have zero new calls
    assert m.complete(0., 74)
    assert len(m.events)==2


def test_strict_negative_objective_and_nonfinite_rejected():
    m=CheckedStagnation(-1.,eps_abs=1e-3,patience=2)
    m.complete(-1.0005, 10)
    assert m.complete(-1.0005, 11)
    for val in (math.nan, math.inf, -math.inf, -0.9):
        with pytest.raises(ValueError): m.complete(val, 12)


def test_nonmonotone_timestamp_is_error_without_state_change():
    m=CheckedStagnation(1., initial_attempts=64)
    m.complete(1.,128)
    with pytest.raises(ValueError,match='nonmonotone'):
        m.complete(1.,127)
    assert m.attempts == 128 and m.generations == 1


@pytest.mark.parametrize('patience', [0,-1,1.,True])
def test_invalid_patience(patience):
    with pytest.raises(ValueError): CheckedStagnation(0.,patience=patience)


@pytest.mark.parametrize('eps', [math.nan,math.inf,-1.])
def test_invalid_eps(eps):
    with pytest.raises(ValueError): CheckedStagnation(0.,eps_abs=eps)
    with pytest.raises(ValueError): CheckedStagnation(0.,eps_rel=eps)


def test_deterministic_reference_1000_seeded_traces():
    # A separate, slow list-based interpretation of the recurrence.
    for seed in range(1000):
        r = random.Random(seed)
        pat = (seed % 20)+1
        a = (seed%3) * .0001
        rel = ((seed//3)%3) * .0001
        init=10.
        m=CheckedStagnation(init,eps_abs=a,eps_rel=rel,patience=pat,initial_attempts=2)
        best=init
        previous_evals=2
        no=0
        armed=True
        oracle=[]
        for gen in range(1, 55):
            delta=max(0, r.uniform(-.001,.003))
            new=best-delta
            nfev=previous_evals+r.randint(0,6)
            meaningful=best-new > a+rel*max(1.,abs(best))
            if meaningful:
                no=0
                armed=True
            else:
                no+=1
            expected_event = (no == pat and armed)
            if expected_event:
                oracle.append((gen,nfev,new))
                armed=False
            event=m.complete(new,nfev)
            assert (event is not None) == expected_event
            assert m.unimproved==no
            assert [(e.generation,e.physical_attempts,e.incumbent) for e in m.events]==oracle
            previous_evals=nfev
            best=new
