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


class AcceptableTargetReached(RuntimeError):
    """A valid feasible candidate has reached the requested quality threshold."""


class ReliabilityMonitor:
    def __init__(self, objective, max_evaluations, acceptable_cost, constrained,
                 cache_evaluations=False):
        self.objective = objective
        # Opt-in only: correct for stationary, deterministic objectives.
        self.cache_evaluations = cache_evaluations
        self.cached_objective_requests = 0
        self._evaluation_cache = {}
        self.max_evaluations = max_evaluations
        self.acceptable_cost = float(acceptable_cost)
        self.constrained = constrained
        self.evaluations = 0
        self.valid_evaluations = 0
        self.invalid_evaluations = 0
        self.best = None  # (objective, violation, immutable snapshot of decision values)
        self.stagnant_generations = 0
        self.stagnation_refreshes = 0
        self.refreshes_since_improvement = 0
        self.restarts = 0
        self.invalid_population_resamples = 0
        self._completed_generation_best = None
        # Validation probes must keep their normal return contract. Enable
        # immediate stopping only after the caller finishes validation.
        self.stop_on_acceptance = False

    def __deepcopy__(self, memo):
        # Population.clone() deep-copies GAOptions for its initial snapshot.
        # Never clone the user's stateful objective or split the call counter.
        memo[id(self)] = self
        return self

    def __call__(self, values):
        evaluated_values = tuple(values)  # Snapshot before user callback can mutate the list.
        cache_key = self._cache_key(evaluated_values)
        if cache_key is not None and cache_key in self._evaluation_cache:
            self.cached_objective_requests += 1
            if self.stop_on_acceptance and self.acceptable:
                raise AcceptableTargetReached("Acceptable evaluated candidate found")
            return self._evaluation_cache[cache_key]
        if self.evaluations >= self.max_evaluations:
            raise EvaluationBudgetExhausted("Objective evaluation budget exhausted")
        self.evaluations += 1  # Charge failed calls, too.
        try:
            result = self.objective(values)
        except (EvaluationBudgetExhausted, AcceptableTargetReached) as ex:
            # These exceptions are internal monitor-to-executor signals.
            # A user callback may raise the same public exception classes;
            # never let that impersonate a real budget or acceptance event.
            self.invalid_evaluations += 1
            raise ValueError("Objective callback raised a reserved reliability control exception") from ex
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
                try:
                    objective = float(result)
                except (TypeError, ValueError, OverflowError):
                    # A Real may be too large for binary64 (e.g. 10**400).
                    # Count it as an invalid attempted call, not a structural
                    # executor error or an uncharged evaluation.
                    self.invalid_evaluations += 1
                    return result
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
        if cache_key is not None:
            # Store the validated scalar or immutable pair, never a mutable
            # reference returned by the user's callback.
            self._evaluation_cache[cache_key] = (
                (objective, violation) if self.constrained else objective
            )
        if self.stop_on_acceptance and self.acceptable:
            # Abort the remainder of this costly generation, including when
            # the successful call is the final allowed evaluation.
            # The complete, actually evaluated result is cached in self.best.
            raise AcceptableTargetReached("Acceptable evaluated candidate found")
        return result

    def _cache_key(self, values):
        """Identify identical numerical inputs, preserving types and signed zero.

        Unsupported/nonhashable values simply bypass caching; no objective
        errors or calls are hidden by the optimization.
        """
        if not self.cache_evaluations:
            return None
        # float(value) loses integer precision beyond 2**53 and may
        # collapse distinct extended-precision scalars. Never use a lossy
        # conversion to decide whether a real objective call can be skipped.
        # Other numeric/user-defined types deliberately bypass caching.
        key = []
        for value in values:
            if type(value) is int:
                key.append((int, value))
            elif type(value) is float:
                key.append((float, value.hex()))
            elif type(value) is bool:
                key.append((bool, value))
            else:
                return None
        return tuple(key)

    def completed_generation(self):
        """Count generations without a better *evaluated* incumbent.

        Compare objective only among feasible candidates; until feasible,
        prioritize lower violation. This deliberately ignores changing
        penalty weights, scalar cost diversity, and population averages.
        Call once after a complete generation's objective evaluations.
        """
        if self.best is None:
            return
        objective, violation, _ = self.best
        quality = (0, objective) if violation == 0 else (1, violation, objective)
        if self._completed_generation_best is None or quality < self._completed_generation_best:
            self.stagnant_generations = 0
            self.refreshes_since_improvement = 0
        else:
            self.stagnant_generations += 1
        self._completed_generation_best = quality

    @property
    def acceptable(self):
        return (self.best is not None and self.best[1] == 0
                and self.best[0] <= self.acceptable_cost)

    def annotate(self, results):
        """Expose separately the technical execution status and solution quality."""
        results.objective_evaluations = self.evaluations
        results.valid_objective_evaluations = self.valid_evaluations
        results.invalid_objective_evaluations = self.invalid_evaluations
        results.cached_objective_requests = self.cached_objective_requests
        if getattr(self, "probe_validation_warning", None):
            results.messages.append(("WARNING", self.probe_validation_warning))
        results.stagnation_refreshes = self.stagnation_refreshes
        results.reliability_restarts = self.restarts
        results.invalid_population_resamples = self.invalid_population_resamples
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
