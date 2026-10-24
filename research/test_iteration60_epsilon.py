"""I60 configuration checks (research/ITERATION60_PROTOCOL.md)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import iteration60_epsilon as i60  # noqa: E402
import iteration58_validation as i58  # noqa: E402


def test_budget_stops_before_the_generation_limit_and_epsilon_ends_near_half():
    assert 32 + 16 * i60.GENERATIONS >= i60.BUDGET
    assert abs((32 + 16 * (i60.GENERATIONS // 2)) - i60.BUDGET / 2) < 60


def test_seeds_are_a_new_stream():
    seeds = {i58.seed_of(i60.PURPOSE, n, j, s) for n in i58.NETWORKS for j in range(3) for s in range(1, 16)}
    used = {i58.seed_of(p, n, j, s) for p in (6, 7) for n in i58.NETWORKS for j in range(3) for s in range(1, 16)}
    assert not seeds & used
