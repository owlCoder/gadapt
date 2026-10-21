"""Experimental credit assignment for existing GAdapt mutation operators.

This is a research ablation, NOT a novel AOS theorem. Rewards are associated
with a whole evaluated offspring and are not causal mutation-only effects:
crossover and selection can also influence an offspring's quality.
"""
import math
import random
import sys
from collections import deque

from gadapt.operations.mutation.decision_variable_mutation.composed_decision_variable_mutator import (
    ComposedDecisionVariableMutator,
)


class CreditBasedDecisionVariableMutator(ComposedDecisionVariableMutator):
    """Uniform or UCB1 selection with a bounded recent-reward memory.

    No additional objective evaluations are performed by this class.
    In feasibility mode, the user must provide a *cached/pure* callback
    returning a finite nonnegative NORMALIZED violation. Its physical
    evaluation cost (if any) must be separately counted by the experiment.
    """

    def __init__(self, policy="ucb", credit="objective", violation_function=None,
                 window=64):
        super().__init__()
        if policy not in ("uniform", "ucb"):
            raise ValueError("policy must be 'uniform' or 'ucb'")
        if credit not in ("objective", "feasibility"):
            raise ValueError("credit must be 'objective' or 'feasibility'")
        if credit == "feasibility" and not callable(violation_function):
            raise ValueError("feasibility credit needs a violation callback")
        self.policy = policy
        self.credit = credit
        self.violation_function = violation_function
        self.window = window
        self._counts = []
        self._observed = []
        self._positive = []
        self._history = []
        self._traces = {}
        self._reference_cost = None

    def append(self, mutator):
        super().append(mutator)
        self._counts.append(0)
        self._observed.append(0)
        self._positive.append(0)
        self._history.append(deque(maxlen=self.window))

    def begin_generation(self, population):
        # Reset temporary traces: a candidate rejected for lack of uniqueness
        # must not receive credit from a previous generation.
        self._traces.clear()
        previous = sorted(float(c.cost_value) for c in population
                          if math.isfinite(c.cost_value) and
                          c.cost_value != sys.float_info.max)
        self._reference_cost = previous[len(previous) // 2] if previous else None

    def _choose(self):
        if not self.mutators:
            raise ValueError("at least one operator is required")
        if self.policy == "uniform":
            selected = random.randrange(len(self.mutators))
        else:
            cold = [i for i, n in enumerate(self._counts) if n == 0]
            if cold:
                selected = random.choice(cold)
            else:
                total = sum(self._counts)
                scores = [
                    (sum(h) / len(h) if h else 0.0)
                    + math.sqrt(2.0 * math.log(total + 1.0) / n)
                    for h, n in zip(self._history, self._counts)
                ]
                top = max(scores)
                selected = random.choice([i for i, value in enumerate(scores)
                                          if value == top])
        self._counts[selected] += 1
        return selected

    def _make_mutated_value(self):
        if self.variable_value is None:
            raise ValueError("No variable to mutate")
        index = self._choose()
        operator = self.mutators[index]
        operator.variable_value = self.variable_value
        new_value = operator._make_mutated_value()
        # Only the *last* operator for a repeatedly mutated variable counts.
        # id keys are safe because this trace is cleared each generation.
        self._traces[id(self.variable_value)] = index
        return new_value

    def observe(self, candidate):
        indices = [self._traces.pop(id(v)) for v in candidate
                   if id(v) in self._traces]
        if not indices:
            return
        reference = self._reference_cost
        improvement = 0.0
        if (getattr(candidate, "_succ", False) and reference is not None
                and math.isfinite(candidate.cost_value)):
            improvement = min(1.0, max(0.0, (reference - candidate.cost_value)
                                      / (1.0 + abs(reference))))
        if self.credit == "feasibility" and getattr(candidate, "_succ", False):
            values = [v.value for v in sorted(
                candidate, key=lambda v: v.decision_variable.variable_id)]
            violation = self.violation_function(values, candidate.cost_value)
            if (not isinstance(violation, (int, float))
                    or not math.isfinite(float(violation))
                    or violation < 0):
                raise ValueError("violation callback must return finite nonnegative scalar")
            reward = (0.5 + 0.5 * improvement) if violation == 0 else (
                0.5 / (1.0 + float(violation)))
        else:
            reward = improvement
        # Per-gene attribution is heuristic: neither crossover nor parental
        # quality is controlled. Equal splitting avoids multi-gene inflation.
        share = reward / len(indices)
        for i in indices:
            self._history[i].append(share)
            self._observed[i] += 1
            if share > 0:
                self._positive[i] += 1

    def summary(self):
        return [
            dict(operator=type(m).__name__, selections=n, observations=o,
                 rewarded=r, recent_mean_reward=(
                     sum(h) / len(h) if h else 0.0))
            for m, n, o, r, h in zip(self.mutators, self._counts,
                                    self._observed, self._positive, self._history)
        ]
