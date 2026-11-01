"""Instrumentation smoke tests ONLY, not a benchmark or scientific comparison.

SciPy DE's generations, callback handling and internal convergence are not
assumed equivalent to the I65 stagnation event semantics.
"""
import numpy as np
import scipy
from scipy.optimize import differential_evolution
from audited_budget import AuditedBudget, BudgetReached


def objective(x):
    return float(np.sum((np.asarray(x, float) - .347)**2))


def test_scipy_de_counts_initial_population_and_partial_generation():
    dim=2
    init=np.random.default_rng(9).uniform(size=(12,dim))
    B=14
    b=AuditedBudget(objective,B)
    try:
        differential_evolution(b,[(0,1)]*dim,init=init,polish=False,
                               rng=np.random.default_rng(11), maxiter=50,
                               tol=0,atol=0)
    except BudgetReached:
        pass
    else:
        raise AssertionError('expected exact budget stop')
    assert b.attempts==B-1
    assert len(b.records)==B-1
    assert all(r.phase=='search' for r in b.records)
    assert all(r.outcome=='finite' for r in b.records)
    # B-1 includes entire initial population of 12 + exactly one trial.
    assert [r.x for r in b.records[:12]]==[tuple(map(float,x)) for x in init]
    assert b.verify(lambda x: objective(x))['status']=='VALIDATED_WITNESS'
    assert b.attempts==B


def test_scipy_de_callback_extra_evaluation_charged_and_replay():
    def run(seed):
        b=AuditedBudget(objective,250)
        called=[0]
        def cb(intermediate_result=None):
            called[0]+=1
            # An explicit callback objective invocation MUST be paid.
            b.evaluate(intermediate_result.x, phase='callback')
            return False
        r=differential_evolution(b,[(0,1)]*2,init='latinhypercube',
                                 popsize=6,polish=False,rng=np.random.default_rng(seed),
                                 maxiter=3,callback=cb,tol=0,atol=0)
        assert called[0]==3
        assert b.attempts == r.nfev+called[0]
        assert sum(rec.phase=='callback' for rec in b.records)==3
        assert b.verify(lambda x: objective(x))['status']=='VALIDATED_WITNESS'
        return b.trace_hash(), b.attempts, b.best
    assert run(491)==run(491)
