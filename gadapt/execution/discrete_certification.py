"""Exact, budget-bounded coverage for small finite GAdapt decision grids.

Unlike stochastic evolutionary search, enumerating all points provides a
completeness guarantee on a *finite declared grid*, subject to a stationary,
deterministic objective, valid responses, and enough wall-clock time.
"""
import itertools
import math
import time

from gadapt.ga_model.ga_results import GAResults


def discrete_grid_axes(decision_variables, max_points):
    """Return finite grid axes or None if full coverage is unsafe/unaffordable.

    Each generated value matches DecisionVariable.make_random_value's
    discretization (step count, cap to upper bound and decimal rounding).
    Duplicated rounded points or a non-finite grid disqualify certification.
    """
    if not decision_variables or type(max_points) is not int or max_points < 1:
        return None
    axes = []
    total = 1
    for variable in sorted(decision_variables, key=lambda v: v.variable_id):
        try:
            low, high = float(variable.min_value), float(variable.max_value)
            step = float(variable.step)
            if not all(math.isfinite(x) for x in (low, high, step)):
                return None
            # Never certify an incomplete grid after narrowing exact integer
            # bounds or a step to binary64. E.g. 2**54 and 2**54+2 both
            # become the same float, spuriously suggesting a one-point grid.
            if (low != variable.min_value or high != variable.max_value
                    or step != variable.step):
                return None
            if low > high or step <= 0.0:
                return None
            ratio = (high - low) / step
            if not math.isfinite(ratio) or ratio > 1e9:
                return None
            count = ((round(ratio) if math.isclose(ratio, round(ratio),
                      rel_tol=1e-9, abs_tol=1e-9) else int(ratio)) + 1)
            if count < 1 or total * count > max_points:
                return None
            values = tuple(round(min(low + i * step, high), variable.decimal_places)
                           for i in range(count))
            if len(set(values)) != len(values) or not all(
                    math.isfinite(x) and low <= x <= high for x in values):
                return None
            # Even when the endpoints themselves survive conversion, a
            # generated interior integer can be lost (1+2**53 rounds to
            # 2**53). Full-grid certification requires every enumerated
            # candidate to match the original variable's arithmetic.
            if any(point != round(
                    min(variable.min_value + i * variable.step, variable.max_value),
                    variable.decimal_places) for i, point in enumerate(values)):
                return None
            axes.append(values)
            total *= count
        except (TypeError, ValueError, OverflowError, AttributeError):
            return None
    return axes


def evaluate_discrete_grid(monitor, axes, timeout_seconds):
    """Visit each distinct grid point at most once and stop at first acceptance."""
    results = GAResults()
    results.number_of_iterations = 0  # This is not a genetic generation.
    results.discrete_space_size = math.prod(len(axis) for axis in axes)
    results.discrete_points_checked = 0
    results.discrete_search_applied = True
    # A charged exception is not evidence that its grid point was validly
    # classified. Never certify absence from partially completed processing.
    unclassified_exception = False
    start = time.monotonic()
    for point in itertools.product(*axes):
        if time.monotonic() - start >= timeout_seconds:
            results.termination_reason = "timeout"
            break
        before = monitor.evaluations
        try:
            monitor(list(point))
        except Exception:
            # Never claim a point was checked if the hard budget refused it.
            if monitor.evaluations == before:
                results.termination_reason = "budget_exhausted"
                break
            # The objective may have raised *after* charging the physical
            # attempt but before marking it valid/invalid. Even if no invalid
            # count was recorded, that point cannot support a proof of
            # complete negative coverage. Monitor acceptance is still
            # handled below, after its verified incumbent has been recorded.
            unclassified_exception = True
        results.discrete_points_checked += 1
        if monitor.acceptable:
            results.termination_reason = "acceptable_target"
            break

    results.discrete_space_exhausted = (
        results.discrete_points_checked == results.discrete_space_size
    )
    results.discrete_absence_certified = (
        results.discrete_space_exhausted and not monitor.acceptable
        and not unclassified_exception
        and monitor.invalid_evaluations == 0
        # A point is not proof-checked merely because the callback returned
        # without raising (or because the call counter advanced). Every grid
        # point needs a distinctly charged, classified valid evaluation.
        and monitor.evaluations == results.discrete_space_size
        and monitor.valid_evaluations == results.discrete_space_size
    )
    if results.termination_reason is None:
        results.termination_reason = "discrete_space_exhausted"
    if monitor.valid_evaluations == 0:
        results.success = False
    monitor.annotate(results)
    return results
