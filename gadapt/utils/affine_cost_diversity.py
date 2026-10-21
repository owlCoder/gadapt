"""Experimental affine-invariant population cost diversity.

This opt-in coefficient is unchanged by positive affine transforms of finite
costs, up to unavoidable floating-point rounding. It compares half-ranges
with the initial generation; unlike the legacy log metric it can recover
when initial cost spread is zero. This metric is not guaranteed to improve
optimization accuracy. Benchmark before adopting it as a default.
"""
import math


def affine_cost_diversity(values, initial_spread=None):
    """Return (coefficient, initial_spread).

    Coefficient is in [0, 1]. A fully identical population has coefficient 0.
    On the first non-degenerate generation it equals 1.
    If the *initial* generation was degenerate, it becomes 1 when spread
    first appears, and returns to 0 if the costs collapse again.

    Half-range is used to avoid overflow in max-min for large finite costs.
    Finite values are required; nonfinite objective values are not valid
    indicators of diversity.
    """
    costs = tuple(float(v) for v in values)
    if not costs:
        raise ValueError("Cannot calculate diversity of an empty population")
    if not all(math.isfinite(v) for v in costs):
        raise ValueError("All cost values must be finite for affine diversity")

    maximum = max(costs)
    minimum = min(costs)
    difference = maximum - minimum
    spread = (difference * 0.5 if math.isfinite(difference)
              else (maximum * 0.5 - minimum * 0.5))

    if initial_spread is None:
        return (1.0 if spread > 0.0 else 0.0), spread
    initial_spread = float(initial_spread)
    if not math.isfinite(initial_spread) or initial_spread < 0.0:
        raise ValueError("Initial diversity reference must be finite and nonnegative")
    if initial_spread == 0.0:
        return (1.0 if spread > 0.0 else 0.0), initial_spread
    return min(1.0, max(0.0, spread / initial_spread)), initial_spread
