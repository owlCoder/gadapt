"""Opt-in accounting and incumbent capture for reliability-oriented executions.

Every call made through this wrapper is charged before invoking the objective,
including validation probes, exceptions and non-finite returns. The wrapper never
re-evaluates the incumbent: it copies the arguments and validated result.
"""
import math
from numbers import Real

from gadapt.utils.constraint_handling import parse_pair


class EvaluationBudgetExhausted(RuntimeError):
    """An objective call was refused because the hard budget is exhausted."""


class ReliabilityMonitor:
    def __init__(self, objective, max_evaluations, acceptable_cost, constrained):
        self.objective = objective
        self.max_evaluations = max_evaluations
        self.acceptable_cost = float(acceptable_cost)
        self.constrained = constrained
        self.evaluations = 0
        self.valid_evaluations = 0
        self.invalid_evaluations = 0
        self.best = None  # (objective, violation, immutable snapshot of decision values)

    def __call__(self, values):
        if self.evaluations >= self.max_evaluations:
            raise EvaluationBudgetExhausted("Objective evaluation budget exhausted")
        self.evaluations += 1  # Charge failed calls, too.
        evaluated_values = tuple(values)  # Snapshot before user callback can mutate the list.
        try:
            result = self.objective(values)
        except Exception:
            self.invalid_evaluations += 1
            raise
        try:
            if self.constrained:
                objective, violation = parse_pair(result)
            else:
                if isinstance(result, bool) or not isinstance(result, Real):
                    self.invalid_evaluations += 1
                    return result
                objective = float(result)
                if not math.isfinite(objective):
                    self.invalid_evaluations += 1
                    return result
                violation = 0.0
        except (TypeError, ValueError, OverflowError):
            self.invalid_evaluations += 1
            return result  # Let the original cost finder report invalid output.

        self.valid_evaluations += 1
        if self.best is None:
            replace = True
        else:
            best_objective, best_violation, _ = self.best
            replace = (violation == 0 and (best_violation != 0 or objective < best_objective)
                       or violation > 0 and best_violation > 0
                       and (violation, objective) < (best_violation, best_objective))
        if replace:
            self.best = (objective, violation, evaluated_values)
        return result

    @property
    def acceptable(self):
        return (self.best is not None and self.best[1] == 0
                and self.best[0] <= self.acceptable_cost)

    def annotate(self, results):
        """Expose separately the technical execution status and solution quality."""
        results.objective_evaluations = self.evaluations
        results.valid_objective_evaluations = self.valid_evaluations
        results.invalid_objective_evaluations = self.invalid_evaluations
        results.acceptable = self.acceptable
        results.feasible = self.best is not None and self.best[1] == 0
        if self.best is None:
            results.solution_status = "no_valid_evaluation"
        elif self.best[1] != 0:
            results.solution_status = "no_feasible_solution"
        elif self.acceptable:
            results.solution_status = "acceptable"
        else:
            results.solution_status = "feasible_but_unacceptable"
        if self.best is not None:
            objective, violation, values = self.best
            results.best_objective = objective
            results.best_violation = violation
            results.result_values = dict(enumerate(values))
            if not self.constrained:
                results.min_cost = objective
