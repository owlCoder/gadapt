"""Standalone REFERENCE state machine, NOT integrated with GAdapt / NOT a new optimizer.

Semantics for review: best-so-far is supplied once after every *completed*
generation; initial population is a baseline, not generation 1. A single
STAGNATION event is emitted when 20 consecutive completed generations do not
make a significant improvement over the preceding generation's best-so-far.
Restart resets the failure counter, but not the global incumbent.
"""
import math

class StagnationMonitor:
    def __init__(self, initial_best, eps_abs=1e-12, eps_rel=1e-8, patience=20):
        if not math.isfinite(initial_best):
            raise ValueError('initial incumbent must be finite')
        if not (math.isfinite(eps_abs) and math.isfinite(eps_rel) and eps_abs >= 0 and eps_rel >= 0):
            raise ValueError('invalid tolerances')
        if type(patience) is not int or patience < 1:
            raise ValueError('invalid patience')
        self.best, self.eps_abs, self.eps_rel, self.patience = float(initial_best), eps_abs, eps_rel, patience
        self.no_improvement, self.completed_generations, self.armed = 0, 0, True
        self.events = []

    def complete_generation(self, current_best, physical_evaluations):
        if not math.isfinite(current_best):
            raise ValueError('nonfinite best-so-far must be handled as invalid, not success')
        if current_best > self.best:
            raise ValueError('global best-so-far cannot deteriorate')
        if type(physical_evaluations) is not int or physical_evaluations < 0:
            raise ValueError('invalid physical evaluation count')
        previous = self.best
        threshold = self.eps_abs + self.eps_rel * max(1.0, abs(previous))
        delta = previous - current_best
        improved = delta > threshold
        self.best = float(current_best)
        self.completed_generations += 1
        if improved:
            self.no_improvement, self.armed = 0, True
        else:
            self.no_improvement += 1
        if self.no_improvement == self.patience and self.armed:
            self.armed = False
            event = dict(type='STAGNATION', at_generation=self.completed_generations,
                         at_evaluations=physical_evaluations, best=self.best)
            self.events.append(event)
            return event
        return None

    def restart(self):
        self.no_improvement, self.armed = 0, True


class AttemptBudget:
    """Reference for a fail-closed boundary. Counts objective *attempts* before invocation.

    Partial batches and asynchronous evaluations need their own reservation logic.
    This class is a validation oracle only, not a drop-in concurrent replacement.
    """
    def __init__(self, objective, limit):
        if type(limit) is not int or limit < 1:
            raise ValueError('invalid budget')
        self.objective, self.limit, self.attempts = objective, limit, 0

    def __call__(self, x):
        if self.attempts >= self.limit:
            raise RuntimeError('BUDGET_EXHAUSTED')
        self.attempts += 1
        return self.objective(x)
