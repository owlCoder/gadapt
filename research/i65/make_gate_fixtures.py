"""Generate transparent, small gate-test traces (NOT optimization experiments)."""
import json
import math
from pathlib import Path
import numpy as np
from audited_budget import AuditedBudget, BudgetReached
from stagnation_checked import CheckedStagnation

out = Path(__file__).resolve().parent.parent / 'I65_INSTRUMENTATION_FIXTURES.json'
case={}
B=7
b=AuditedBudget(lambda x: float((np.asarray(x)-.2).dot(np.asarray(x)-.2)),B)
for y in [[.5],[.4],[.3],[.25],[.21],[.2]]:
    b(y)
try:
    b([0.])
except BudgetReached:
    pass
case['exact_budget']={'limit':B, 'before_witness':b.attempts,
   'verification':b.verify(lambda x:float(np.sum((np.asarray(x)-.2)**2))),
   'after_witness':b.attempts,'trace_sha256':b.trace_hash(),
   'trace':[r.__dict__ for r in b.records]}

bad=AuditedBudget(lambda x:(_ for _ in ()).throw(ArithmeticError('synthetic evaluator failure')),3)
for _ in range(2):
    try: bad([1.])
    except ArithmeticError: pass
case['exception_attempts']={'limit':3,'attempted':bad.attempts,'recheck':bad.verify(lambda x:0.),
 'trace':[r.__dict__ for r in bad.records]}

mut=AuditedBudget(lambda x:(float(x[0]**2), x.__setitem__(0, 999.))[0],2)
mut([2.]); case['mutable_input']={'recorded_best':mut.best_x,
   'witness':mut.verify(lambda x:float(x[0]**2)),
   'trace':[r.__dict__ for r in mut.records]}

m=CheckedStagnation(1.,initial_attempts=10,patience=20)
for k in range(1,22): m.complete(1.,10+k*4)
case['stagnation']={'event_count':len(m.events),
 'events':[e.__dict__ for e in m.events],'completed_generations':m.generations}
out.write_text(json.dumps({'kind':'VALIDATION_FIXTURES_NOT_SCIENTIFIC_EXPERIMENTS',
                           'cases':case},indent=2,sort_keys=True)+'\n')
print(out)
