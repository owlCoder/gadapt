"""I59 evaluator and MILP checks (research/ITERATION59_PROTOCOL.md); the MILP is tested on a synthetic graph only."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import iteration59_telecom as t  # noqa: E402

# a 4-cycle with a chord; distances make the chord expensive
TOY = dict(directed=False, multigraph=False, graph=dict(name="toy", demands={"0": {"2": 8.0}, "1": {"3": 4.0}}),
           nodes=[dict(id=i) for i in range(4)],
           edges=[dict(source=0, target=1, dist=100.0), dict(source=1, target=2, dist=100.0),
                  dict(source=2, target=3, dist=100.0), dict(source=3, target=0, dist=100.0),
                  dict(source=0, target=2, dist=5000.0)])


def test_shortest_path_design_is_feasible_and_empty_design_is_not():
    for name in t.INSTANCES[:5]:
        instance = t.Instance(name)
        assert instance.evaluate(instance.x_sp)["V"] == 0.0
        assert abs(instance.evaluate(np.zeros(len(instance.edges)))["V"] - 1.0) < 1e-9
        assert instance.x_sp.max() == 8


def test_shortest_path_tie_break_is_lexicographic():
    toy = t.Instance("toy", TOY)
    # 0 -> 2 has the direct chord (1 hop); 1 -> 3 has two 2-hop paths 1-0-3 and 1-2-3: the smaller is 1-0-3
    adjacency = toy._neighbours()
    path = toy._shortest_path(1, 3, adjacency)
    assert [toy.edges[e][:2] for e in path] == [(0, 1), (0, 3)]


def test_milp_on_a_synthetic_graph_is_certified_and_feasible_for_the_evaluator():
    toy = t.Instance("toy", TOY)
    ref = toy.milp_reference(time_limit=60)
    assert ref["certified"]
    assert toy.evaluate(ref["x"])["V"] == 0.0
    assert ref["C"] <= toy.c_sp + 1e-9


def test_partial_capacity_gives_a_graded_shortage():
    toy = t.Instance("toy", TOY)
    x = toy.x_sp.copy()
    x[np.argmax(x)] = 0
    v = toy.evaluate(x)["V"]
    assert 0.0 < v <= 1.0
