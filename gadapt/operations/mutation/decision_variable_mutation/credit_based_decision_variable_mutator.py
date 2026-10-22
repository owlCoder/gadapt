"""Experimental credit assignment for existing GAdapt mutation operators.

This is a research ablation, NOT a novel AOS theorem. Rewards are associated
with a whole evaluated offspring and are not causal mutation-only effects:
crossover and selection can also influence an offspring's quality.
"""
import math
import random
import sys
from collections import deque

from gadapt.operations.mutation.decision_variable_mutation.verified_call_rate_bandit import (
    VerifiedCallRateBandit,
)

from gadapt.operations.mutation.decision_variable_mutation.composed_decision_variable_mutator import (
    ComposedDecisionVariableMutator,
)


class CreditBasedDecisionVariableMutator(ComposedDecisionVariableMutator):
    """Uniform or UCB1 selection with a bounded recent-reward memory.

    Paired mode evaluates an unmutated offspring immediately before mutation;\n    this DOES consume an additional true objective evaluation. The mandatory\n    monotone counter tracks actual solver calls, not wrapper requests.
    In feasibility mode, the user must provide a *cached/pure* callback
    returning a finite nonnegative NORMALIZED violation (or None if the\n    trial was NOT physically evaluated, e.g. after a hard evaluation cap). Its physical
    evaluation cost (if any) must be separately counted by the experiment.
    """

    def __init__(self, policy="ucb", credit="objective", violation_function=None,
                 window=64, assignment="offspring", evaluation_counter=None,
                 scenario_count=None):
        super().__init__()
        if policy not in ("uniform", "ucb", "ucb_true_call_rate"):
            raise ValueError("policy must be uniform/ucb/ucb_true_call_rate")
        if policy == "ucb_true_call_rate" and credit != "censored_verified_per_cost":
            raise ValueError("true-call rate requires censored_verified_per_cost feedback")
        if credit not in ("objective", "feasibility", "scenario_feasibility", "censored_verified_per_cost"):
            raise ValueError("credit must be objective/feasibility/scenario_feasibility/censored_verified_per_cost")
        if credit in ("feasibility", "scenario_feasibility", "censored_verified_per_cost") and not callable(violation_function):
            raise ValueError("feasibility credit needs a violation callback")
        if assignment not in ("offspring", "paired"):
            raise ValueError("assignment must be offspring/paired")
        if assignment == "paired" and not callable(evaluation_counter):
            raise ValueError("paired credit requires monotone evaluation counter")
        if credit in ("scenario_feasibility", "censored_verified_per_cost"):
            if type(scenario_count) is not int or scenario_count < 2:
                raise ValueError("multi-scenario credit requires scenario_count >= 2")
            if not callable(evaluation_counter):
                raise ValueError("multi-scenario credit requires physical evaluation counter")
            if assignment != "offspring":
                raise ValueError("multi-scenario credit currently requires offspring assignment")
        elif scenario_count is not None:
            raise ValueError("scenario_count only applies to multi-scenario feasibility credit")
        self.scenario_count = scenario_count
        self.assignment = assignment
        self.evaluation_counter = evaluation_counter
        self._paired_baselines = {}
        self.paired_evaluations = 0
        self.paired_abandoned = 0
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
        self._unevaluated_traces = 0
        self._scenario_fully_feasible_observations = 0
        self._censor_safe_verified_feedback = 0
        self._censor_safe_measured_failures = 0
        self._censor_safe_withheld_unknown = 0
        self._last_censor_status = None
        self._call_rate = (VerifiedCallRateBandit(scenario_count)
                           if policy == "ucb_true_call_rate" else None)

    def append(self, mutator):
        super().append(mutator)
        self._counts.append(0)
        self._observed.append(0)
        self._positive.append(0)
        self._history.append(deque(maxlen=self.window))
        if self._call_rate is not None:
            self._call_rate.add_operator()

    def begin_generation(self, population):
        # Reset temporary traces: a candidate rejected for lack of uniqueness
        # must not receive credit from a previous generation.
        self._traces.clear()
        self._paired_baselines.clear()
        previous = sorted(float(c.cost_value) for c in population
                          if math.isfinite(c.cost_value) and
                          c.cost_value != sys.float_info.max)
        self._reference_cost = previous[len(previous) // 2] if previous else None

    def _choose(self):
        if not self.mutators:
            raise ValueError("at least one operator is required")
        if self.policy == "uniform":
            selected = random.randrange(len(self.mutators))
        elif self.policy == "ucb_true_call_rate":
            selected = self._call_rate.choose()
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

    def _counter_value(self):
        counter = self.evaluation_counter()
        if type(counter) is not int or counter < 0:
            raise ValueError("evaluation counter must be a nonnegative int")
        return counter

    def before_candidate_mutation(self, candidate, cost_function):
        """Evaluate exact pre-mutation chromosome once, charging real budget.

        This pre-mutation genome shares parent and crossover history with the
        subsequently mutated genome. It is a LOCAL control, not a causal
        estimate of downstream optimization performance, and is not retained
        by GA selection. No baseline credit if no physical evaluation occurred.
        """
        if self.assignment != "paired":
            return
        before = self._counter_value()
        vector = [v.value for v in sorted(
            candidate, key=lambda v: v.decision_variable.variable_id)]
        cost = cost_function(vector)
        after = self._counter_value()
        if after < before or after > before + 1:
            raise ValueError("evaluation counter must rise exactly once per physical probe")
        if after == before or not isinstance(cost, (int, float)) or not math.isfinite(cost):
            self.paired_abandoned += 1
            return
        violation = None
        if self.credit == "feasibility":
            violation = self.violation_function(vector, cost)
            if violation is None:
                self.paired_abandoned += 1
                return
            if (not isinstance(violation, (int, float))
                    or not math.isfinite(violation) or violation < 0):
                raise ValueError("invalid baseline physical-violation signal")
            violation = float(violation)
        self._paired_baselines[id(candidate)] = (float(cost), violation)
        self.paired_evaluations += 1

    def _scenario_reward(self, values, objective_score, improvement):
        """Use ONLY a cached full scenario violation vector; never run a solver.

        A completely source-feasible N-scenario design gets more reward than
        any incomplete one. This is a heuristic AOS credit, not causal proof.
        """
        signal = self.violation_function(values, objective_score)
        if signal is None:
            return None
        if isinstance(signal, (str, bytes)):
            raise ValueError("scenario feedback must be a sequence, not text")
        try:
            violations = list(signal)
        except TypeError:
            raise ValueError("scenario feedback must be a sequence of violations")
        if len(violations) != self.scenario_count:
            raise ValueError("scenario feedback length must equal scenario_count")
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(v) or v < 0 for v in violations):
            raise ValueError("scenario violations must be finite nonnegative numbers")
        if all(v == 0 for v in violations):
            self._scenario_fully_feasible_observations += 1
            return 0.75 + 0.25 * improvement
        coverage = sum(v == 0 for v in violations) / self.scenario_count
        return (0.5 * coverage +
                0.125 / (1.0 + max(violations)) +
                0.125 / (1.0 + sum(violations) / self.scenario_count))


    def _censored_verified_reward(self, values, objective_score, measured_calls):
        """Credit only physically verified robust success, normalized by true cost.

        Feedback is PURE last-evaluation metadata, never another simulator call.
        A known measured failure is zero reward, NEVER an optimistic cheap success.
        Missing or numerically unknown observations are withheld entirely.
        """
        if type(measured_calls) is not int or not 1 <= measured_calls <= self.scenario_count:
            raise ValueError("credit requires actual measured calls within scenario count")
        self._last_censor_status = None
        feedback = self.violation_function(values, objective_score)
        if feedback is None:
            self._censor_safe_withheld_unknown += 1
            return None
        if not isinstance(feedback, dict):
            raise ValueError("censored credit requires a physical observation mapping")
        if set(feedback) != {"status", "actual_calls", "observed_scenarios", "observed_violations"}:
            raise ValueError("censored credit requires exactly status/calls/scenarios/violations")
        if type(feedback["actual_calls"]) is not int or feedback["actual_calls"] != measured_calls:
            raise ValueError("censored feedback real-call count does not match counter")
        names = feedback["observed_scenarios"]
        values_seen = feedback["observed_violations"]
        if (not isinstance(names, (tuple, list)) or not isinstance(values_seen, (tuple, list))
                or len(names) != measured_calls or len(values_seen) != measured_calls
                or any(not isinstance(n, str) or not n for n in names)
                or len(set(names)) != measured_calls):
            raise ValueError("censored feedback must give distinct measured scenario identifiers")
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(float(v)) or v < 0 for v in values_seen):
            raise ValueError("censored feedback requires finite nonnegative measured violations")
        status = feedback["status"]
        self._last_censor_status = status
        if status == "numerically_unknown":
            self._censor_safe_withheld_unknown += 1
            return None
        if status == "verified_feasible":
            if measured_calls != self.scenario_count or any(v != 0 for v in values_seen):
                raise ValueError("robust feasible credit requires all measured source scenarios")
            self._censor_safe_verified_feedback += 1
            return 1.0 / measured_calls
        if status == "measured_infeasible":
            if not any(v > 0 for v in values_seen):
                raise ValueError("screened physical failure needs a positive measured violation")
            self._censor_safe_measured_failures += 1
            return 0.0
        raise ValueError("censored feedback uses unknown status")

    def observe(self, candidate, physically_evaluated=None, measured_scenarios=None):
        indices = [self._traces.pop(id(v)) for v in candidate
                   if id(v) in self._traces]
        if not indices:
            return
        if self._call_rate is not None and len(indices) != 1:
            raise ValueError("true-call rate requires exactly one mutated operator per offspring")
        baseline = self._paired_baselines.pop(id(candidate), None)
        if self.credit in ("scenario_feasibility", "censored_verified_per_cost") and physically_evaluated is not True:
            self._unevaluated_traces += len(indices)
            return
        if self.assignment == "paired":
            # No rewards for incomplete physical pairs; calling an objective
            # after its hard budget is NOT the same as evaluating an offspring.
            if baseline is None or physically_evaluated is not True or len(indices) != 1:
                self.paired_abandoned += 1
                return
            reference = baseline[0]
        else:
            reference = self._reference_cost
        improvement = 0.0
        if (getattr(candidate, "_succ", False) and reference is not None
                and math.isfinite(candidate.cost_value)):
            improvement = min(1.0, max(0.0, (reference - candidate.cost_value)
                                      / (1.0 + abs(reference))))
        if self.credit == "censored_verified_per_cost":
            if not getattr(candidate, "_succ", False):
                # A paid but non-finite objective has UNKNOWN outcome. Its
                # real physical calls must not disappear from throughput.
                if self._call_rate is not None and physically_evaluated is True:
                    self._call_rate.observe(
                        indices[0], "numerically_unknown", measured_scenarios)
                self._unevaluated_traces += len(indices)
                return
            values = [v.value for v in sorted(
                candidate, key=lambda v: v.decision_variable.variable_id)]
            reward = self._censored_verified_reward(
                values, candidate.cost_value, measured_scenarios)
            if self._call_rate is not None:
                # Already validated by _censored_verified_reward; unknowns
                # cost true calls, but never become certified successes.
                self._call_rate.observe(
                    indices[0], self._last_censor_status
                    if reward is not None else "numerically_unknown",
                    measured_scenarios)
            if reward is None:
                self._unevaluated_traces += len(indices)
                return
        elif self.credit == "scenario_feasibility":
            if not getattr(candidate, "_succ", False):
                self._unevaluated_traces += len(indices)
                return
            values = [v.value for v in sorted(
                candidate, key=lambda v: v.decision_variable.variable_id)]
            reward = self._scenario_reward(values, candidate.cost_value, improvement)
            if reward is None:
                self._unevaluated_traces += len(indices)
                return
        elif self.credit == "feasibility" and getattr(candidate, "_succ", False):
            values = [v.value for v in sorted(
                candidate, key=lambda v: v.decision_variable.variable_id)]
            violation = self.violation_function(values, candidate.cost_value)
            if violation is None:
                # Never reward/discredit trials without a real evaluation.
                self._unevaluated_traces += len(indices)
                return
            if (not isinstance(violation, (int, float))
                    or not math.isfinite(float(violation))
                    or violation < 0):
                raise ValueError("violation callback must return finite nonnegative scalar")
            if self.assignment == "paired":
                before_violation = baseline[1]
                if before_violation > 0:
                    # Reward only reducing independently normalized violation.
                    reward = max(0.0, (before_violation - float(violation))
                                 / (1.0 + before_violation))
                else:
                    # A previously feasible design must remain feasible, then
                    # strictly improve the objective to earn credit.
                    reward = improvement if violation == 0 else 0.0
            else:
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
        out = [
            dict(operator=type(m).__name__, selections=n, observations=o,
                 credit_assignment=self.assignment,
                 paired_physical_baselines=self.paired_evaluations,
                 paired_incomplete_trials=self.paired_abandoned,
                 rewarded=r,
                 withheld_unpaid_credits=self._unevaluated_traces,
                 scenario_complete_feasible_feedback=self._scenario_fully_feasible_observations,
                 censor_safe_verified_feedback=self._censor_safe_verified_feedback,
                 censor_safe_measured_failures=self._censor_safe_measured_failures,
                 censor_safe_withheld_unknown=self._censor_safe_withheld_unknown,
                 recent_mean_reward=(
                     sum(h) / len(h) if h else 0.0))
            for m, n, o, r, h in zip(self.mutators, self._counts,
                                    self._observed, self._positive, self._history)
        ]
        if self._call_rate is not None:
            for item, paid in zip(out, self._call_rate.summary()):
                item["verified_true_call_rate"] = paid
        return out
