"""Research-only checked implementation of I65 per-completed-generation stagnation.

It does not implement a new optimizer; it only processes aggregate best-so-far
snapshots from complete algorithm generations. Instrumentation review required
before applying it to GAdapt, DE, CMA or COCO instances.
"""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class StagnationEvent:
    kind: str
    generation: int
    physical_attempts: int
    incumbent: float

class CheckedStagnation:
    def __init__(self, incumbent, *, eps_abs=0., eps_rel=0., patience=20,
                 initial_attempts=0):
        if not math.isfinite(incumbent):
            raise ValueError('nonfinite initial incumbent')
        if type(patience) is not int or patience < 1:
            raise ValueError('invalid patience')
        for v in (eps_abs, eps_rel):
            if not math.isfinite(v) or v < 0:
                raise ValueError('invalid epsilon')
        if type(initial_attempts) is not int or initial_attempts < 0:
            raise ValueError('invalid initial physical attempts')
        self.incumbent = float(incumbent)
        self.eps_abs = eps_abs
        self.eps_rel = eps_rel
        self.patience = patience
        self.attempts = initial_attempts
        self.generations = 0
        self.unimproved = 0
        self.armed = True
        self.events = []

    def complete(self, incumbent, physical_attempts):
        if type(physical_attempts) is not int or physical_attempts < self.attempts:
            raise ValueError('nonmonotone physical attempts')
        if not math.isfinite(incumbent) or incumbent > self.incumbent:
            raise ValueError('invalid global incumbent')
        threshold = self.eps_abs + self.eps_rel * max(1., abs(self.incumbent))
        if not math.isfinite(threshold):
            raise ValueError('overflowed threshold')
        improved = (self.incumbent - incumbent) > threshold
        self.incumbent = float(incumbent)
        self.attempts = physical_attempts
        self.generations += 1
        if improved:
            self.unimproved = 0
            self.armed = True
        else:
            self.unimproved += 1
        if self.unimproved == self.patience and self.armed:
            self.armed = False
            e = StagnationEvent('STAGNATION', self.generations,
                                self.attempts, self.incumbent)
            self.events.append(e)
            return e
        return None

    def restart(self):
        self.unimproved = 0
        self.armed = True
