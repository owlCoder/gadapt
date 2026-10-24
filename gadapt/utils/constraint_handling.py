"""
Constraint handling (opt-in, GA parameter constraint_handling): the cost function returns (objective, violation),
violation >= 0 and 0 for a feasible solution. Selection uses an explicit comparison key; the scalar cost (cost_value)
only feeds GAdapt's adaptation signals and the reported min_cost.
"""
import math
import statistics
from numbers import Real

PENALTY = "penalty"
ADAPTIVE_PENALTY = "adaptive_penalty"
FEASIBILITY_RULES = "feasibility_rules"
EPSILON = "epsilon"
CONSTRAINT_HANDLING_STRINGS = [PENALTY, ADAPTIVE_PENALTY, FEASIBILITY_RULES, EPSILON]

PATIENCE = 3  # adaptive penalty: generations in a row before the weight changes
INCREASE, DECREASE = 2.0, 1.5
WEIGHT_RANGE = 1e6  # the adaptive weight stays within [initial / 1e6, initial * 1e6]
COST_LIMIT = 1e12  # penalty scalars for the adaptation are clipped to [-COST_LIMIT, COST_LIMIT]
VALUE_LIMIT = 1e150  # |objective| and violation; with weights <= 1e106 every penalized objective stays finite
EPSILON_PERCENTILE = 20  # epsilon: initial level from the initial population
EPSILON_CONTROL_FRACTION, EPSILON_EXPONENT = 0.5, 5


def parse_pair(result):
    """(objective, violation) as floats; raises ValueError unless both are finite real numbers and violation >= 0."""
    if not isinstance(result, (tuple, list)) or len(result) != 2:
        raise ValueError("With constraint_handling, the cost function must return (objective, violation)")
    objective, violation = result
    for value in (objective, violation):
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(float(value)):
            raise ValueError("The objective and the violation must be finite real numbers")
    if violation < 0:
        raise ValueError("The violation must be >= 0")
    if abs(objective) > VALUE_LIMIT or violation > VALUE_LIMIT:
        raise ValueError("The objective and the violation must be within ±1e150")
    return float(objective), float(violation)


class ConstraintHandler:
    """
    penalty: objective + weight * violation (Deb 2000 baseline).
    adaptive_penalty: the weight is doubled after PATIENCE generations with an infeasible best candidate solution
        and divided by 1.5 after PATIENCE feasible ones (Ben Hadj-Alouane and Bean 1997).
    feasibility_rules: feasible before infeasible, by objective among feasible, by violation among infeasible
        (Deb 2000).
    epsilon: as feasibility_rules, with violation <= epsilon counted as feasible; epsilon decreases to 0 over the
        first half of the run (Takahama and Sakai 2006).
    A failed evaluation (objective None) is always last.
    """

    def __init__(self, technique, weight=1000.0):
        if technique not in CONSTRAINT_HANDLING_STRINGS:
            raise ValueError("constraint_handling must be one of " + ", ".join(CONSTRAINT_HANDLING_STRINGS))
        self.technique = technique
        self.initial_weight = self.weight = float(weight)
        self.infeasible_streak = self.feasible_streak = 0
        self.f_ref = None
        self.epsilon0 = None
        self.epsilon = 0.0

    def start_generation(self, previous_best, initial_pairs, progress):
        """Updates the parameters from the completed history. progress: elapsed share of the run in [0, 1]."""
        if self.f_ref is None:
            objectives = [abs(o) for o, _ in initial_pairs if o is not None]
            self.f_ref = statistics.median(objectives) if objectives else 1.0
            if self.f_ref == 0:
                self.f_ref = 1.0
        if self.technique == ADAPTIVE_PENALTY and previous_best is not None:
            if previous_best[0] is not None and previous_best[1] == 0:
                self.feasible_streak, self.infeasible_streak = self.feasible_streak + 1, 0
            else:
                self.infeasible_streak, self.feasible_streak = self.infeasible_streak + 1, 0
            if self.infeasible_streak >= PATIENCE:
                self.weight = min(self.weight * INCREASE, self.initial_weight * WEIGHT_RANGE)
                self.infeasible_streak = self.feasible_streak = 0
            elif self.feasible_streak >= PATIENCE:
                self.weight = max(self.weight / DECREASE, self.initial_weight / WEIGHT_RANGE)
                self.infeasible_streak = self.feasible_streak = 0
        if self.technique == EPSILON:
            if self.epsilon0 is None:
                violations = sorted(v for o, v in initial_pairs if o is not None)
                self.epsilon0 = _percentile(violations, EPSILON_PERCENTILE) if violations else 0.0
            self.epsilon = (self.epsilon0 * (1 - progress / EPSILON_CONTROL_FRACTION) ** EPSILON_EXPONENT
                            if progress < EPSILON_CONTROL_FRACTION else 0.0)

    def is_feasible(self, objective, violation):
        """Feasible in the technique's sense (epsilon: violation up to the current level)."""
        if objective is None:
            return False
        return violation <= self.epsilon if self.technique == EPSILON else violation == 0

    def _penalized(self, objective, violation):
        """objective + weight * violation; finite for parsed pairs (VALUE_LIMIT) and bounded weights."""
        return objective + self.weight * violation

    def key(self, objective, violation):
        """Selection key (smaller is better), exact for any finite values."""
        if objective is None:
            return (2, 0.0, 0.0)
        if self.technique in (PENALTY, ADAPTIVE_PENALTY):
            return (0, 0.0, self._penalized(objective, violation))
        if self.is_feasible(objective, violation):
            return (0, 0.0, objective)
        return (1, 0.0, violation)

    def cost(self, objective, violation, failure_cost=None):
        """
        The scalar cost_value (adaptation signals and min_cost). Rule-based techniques: 1 + u(objective) if feasible,
        2 + violation / (1 + violation) if infeasible, 3 if failed, with u(f) = 1/2 + arctan(f / f_ref) / pi.
        Penalties: the penalized objective; a failed evaluation gets failure_cost (the largest finite penalized cost
        in the population), so a failure does not inflate the cost diversity.
        """
        if self.technique in (PENALTY, ADAPTIVE_PENALTY):
            if objective is None:
                return failure_cost if failure_cost is not None else 1.0
            return max(-COST_LIMIT, min(COST_LIMIT, self._penalized(objective, violation)))
        if objective is None:
            return 3.0
        if self.is_feasible(objective, violation):
            return 1.0 + 0.5 + math.atan(objective / self.f_ref) / math.pi
        return 2.0 + violation / (1.0 + violation)


def _percentile(sorted_values, q):
    """Linear-interpolation percentile (numpy's default) of a sorted, non-empty list."""
    position = (len(sorted_values) - 1) * q / 100.0
    low = math.floor(position)
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (position - low)
