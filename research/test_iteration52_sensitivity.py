"""Checks of the exact matched-exposure computation in iteration52_sensitivity.py."""
from itertools import combinations, product
from math import comb

from iteration52_sensitivity import convolve


def test_convolve_matches_enumeration():
    ps = [0.2, 0.7, 1.0, 0.5]
    exact = [0.0] * (len(ps) + 1)
    for outcome in product((0, 1), repeat=len(ps)):
        mass = 1.0
        for o, p in zip(outcome, ps):
            mass *= p if o else 1 - p
        exact[sum(outcome)] += mass
    assert all(abs(a - b) < 1e-12 for a, b in zip(convolve(ps), exact))


def test_no_positive_probability_matches_enumeration():
    n, k, m = 12, 3, 5
    cells = [True] * k + [False] * (n - k)
    empty = sum(1 for s in combinations(range(n), m) if not any(cells[i] for i in s))
    assert empty / comb(n, m) == comb(n - k, m) / comb(n, m)
