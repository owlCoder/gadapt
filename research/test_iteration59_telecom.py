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


def test_balance_checks_cover_every_node():
    toy = t.Instance("toy", TOY)
    res = t.linprog(toy.objective, A_ub=toy.A_cap, b_ub=toy.x_sp, A_eq=toy.A_eq, b_eq=toy.b_eq, bounds=toy.bounds,
                    method="highs-ds", options=t.LP_OPTIONS)
    y, u = res.x[:toy.n_y], res.x[toy.n_y:]
    assert toy.witness_ok(y, u, toy.x_sp)
    assert toy.A_all.shape[0] == len(toy.demands) * len(toy.nodes)  # a row for EVERY node
    # move flow so that every retained row is off by ~5e-8 but the omitted (last) node by more than 1e-7
    bad = y.copy()
    n, arcs = len(toy.nodes), 2 * len(toy.edges)
    for e, (a, b, _) in enumerate(toy.edges):
        if b == n - 1:  # arc a -> last node of commodity 0
            bad[2 * e] += 1.5e-7
            break
    assert not toy.witness_ok(bad, u, toy.x_sp + 1)


def test_inputs_are_validated_and_ceiling_is_literal():
    toy = t.Instance("toy", TOY)
    for bad in (np.full(len(toy.edges), 0.5), np.full(len(toy.edges), 17.0), np.zeros(len(toy.edges) - 1),
                np.full(len(toy.edges), np.nan)):
        try:
            toy.evaluate(bad)
            raise AssertionError("accepted invalid input")
        except ValueError:
            pass
    assert np.array_equal(toy.x_sp, np.ceil(toy.sp_load / toy.q))


def test_milp_witness_is_verified():
    toy = t.Instance("toy", TOY)
    ref = toy.milp_reference(time_limit=60)
    assert ref["witness_checks"] and ref["certified"]
    assert all(t.EXPECTED_MILP_WARNING.match(w) for w in ref["warnings"])
    assert not t.EXPECTED_MILP_WARNING.match("Unrecognized options detected: {'threads', 'foo'}. These will be passed to HiGHS verbatim.")


def test_evaluate_emits_no_warnings():
    import warnings
    toy = t.Instance("toy", TOY)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        toy.evaluate(toy.x_sp)


def test_independent_checker_agrees_on_real_instances():
    rng = np.random.RandomState(3)
    for name in ("pdh", "polska"):
        instance = t.Instance(name)
        for x in (instance.x_sp, np.zeros(len(instance.edges)), rng.randint(0, 17, len(instance.edges)).astype(float)):
            a, b = instance.evaluate(x), t.independent_check(name, x)
            assert b["valid"] and abs(a["C"] - b["cost"]) < 1e-9
            assert (a["V"] == 0.0) == b["routable"]
            assert abs(a["V"] - b["shortage"]) < 1e-6


def test_attainment_refuses_failed_records():
    records = [dict(task=dict(instance="pdh"), ok=True, hits={"0.05": 10}), dict(task=dict(instance="pdh"), ok=False)]
    try:
        t.attainment(records, "pdh", 3000, 0.05)
        raise AssertionError("failed records were silently excluded")
    except AssertionError as e:
        assert "silently" not in str(e)


def test_checker_requires_full_demand_balances():
    toy = t.Instance("toy", TOY)
    assert t.independent_check("toy", toy.x_sp, TOY)["routable"]
    almost = toy.x_sp.copy()
    almost[np.argmax(almost)] -= 1
    assert toy.evaluate(almost)["V"] > 0 and not t.independent_check("toy", almost, TOY)["routable"]


def test_analysis_requires_the_exact_inventory_and_passed_checks():
    def record(n, s, arm):
        return dict(task=dict(instance=n, seed=t.seed_of(2, n, s), arm=arm, budget=3000), ok=True,
                    hits={"0.05": 100 if arm == "G1" else 2000})
    full = [record(n, s, a) for n in t.CONFIRMATION for s in range(1, 16) for a in ("G0", "G1")]
    refs = {n: dict(certified=True, C=1.0) for n in t.CONFIRMATION}
    store = {"development.json": dict(decision="GO", trivial={}),
             "check.json": dict(failures=0)}
    saved = {}
    original_load, original_save = t.load, t.save
    try:
        t.save = lambda name, d: saved.update({name: d})
        for records, checks, expect in ((full, 0, True), (full[:-2], 0, False), (full, 1, False)):
            store["confirmation.json"] = dict(chosen=[3000, 0.05], references=refs, trivial={}, records=records)
            store["check.json"] = dict(failures=checks)
            t.load = lambda name: store[name]
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                t.analyse()
            h = saved["analysis.json"]["H59"]
            assert (h is not None and h["supported"]) == expect
    finally:
        t.load, t.save = original_load, original_save
