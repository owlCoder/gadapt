"""Research: optimistic verified-feasible successes per PAID physical scenario call.

Not a novel bandit theorem: this tests an algebraic objective mismatch in I34.
No simulator calls are made here. Costs include paid numerical-unknown trials.
Stationary-arm concentration bounds are only heuristic in evolving GAdapt.
"""
import math
import random


class VerifiedCallRateBandit:
    """One observed offspring, one attributed operator, integer true-call cost."""

    def __init__(self, scenario_count, delta=0.05):
        if type(scenario_count) is not int or scenario_count < 2:
            raise ValueError("scenario_count must be an integer >= 2")
        if not isinstance(delta, (float, int)) or isinstance(delta, bool) or not 0 < delta < 1:
            raise ValueError("delta must be in (0,1)")
        self.scenario_count = scenario_count
        self.delta = float(delta)
        self._arms = []

    def add_operator(self):
        self._arms.append(dict(trials=0, verified_successes=0,
                               unknown=0, actual_calls=0))

    def observe(self, operator_index, status, actual_calls):
        if type(operator_index) is not int or not 0 <= operator_index < len(self._arms):
            raise ValueError("unknown operator")
        if type(actual_calls) is not int or not 1 <= actual_calls <= self.scenario_count:
            raise ValueError("actual_calls must be a genuine 1..N event")
        if status not in ("verified_feasible", "measured_infeasible", "numerically_unknown"):
            raise ValueError("unrecognized physical status")
        if status == "verified_feasible" and actual_calls != self.scenario_count:
            raise ValueError("only all-N verified observations certify success")
        a = self._arms[operator_index]
        a["trials"] += 1
        a["actual_calls"] += actual_calls
        if status == "verified_feasible":
            a["verified_successes"] += 1
        elif status == "numerically_unknown":
            a["unknown"] += 1

    def optimistic_score(self, operator_index):
        if type(operator_index) is not int or not 0 <= operator_index < len(self._arms):
            raise ValueError("unknown operator")
        a = self._arms[operator_index]
        n = a["trials"]
        if not n:
            return float("inf")
        t = sum(x["trials"] for x in self._arms)
        k = len(self._arms)
        rad = math.sqrt(math.log(8.0 * k * (t + 1) ** 2 / self.delta) / (2.0 * n))
        # Unknowns contribute ONLY to an optimistic bound, never to certified rate.
        p_upper = min(1.0, (a["verified_successes"] + a["unknown"]) / n + rad)
        cost_lower = max(1.0, a["actual_calls"] / n -
                         (self.scenario_count - 1) * rad)
        return p_upper / cost_lower

    def choose(self):
        if not self._arms:
            raise ValueError("need at least one operator")
        cold = [i for i, a in enumerate(self._arms) if a["trials"] == 0]
        if cold:
            return random.choice(cold)
        scores = [self.optimistic_score(i) for i in range(len(self._arms))]
        best = max(scores)
        return random.choice([i for i, v in enumerate(scores) if v == best])

    def summary(self):
        return [dict(v,
                     certified_success_per_true_call=(
                         v["verified_successes"] / v["actual_calls"]
                         if v["actual_calls"] else None),
                     optimistic_score=(self.optimistic_score(i) if v["trials"] else None))
                for i, v in enumerate(self._arms)]
