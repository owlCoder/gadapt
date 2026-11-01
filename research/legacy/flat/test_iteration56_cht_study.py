"""Checks of the I56 study code against the frozen protocol (research/ITERATION56_PROTOCOL.md, §10)."""
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import iteration56_cht_study as st  # noqa: E402

BASE = dict(network="case14", resolution=17, scenario=(0.95, 101), budget=600, reference=None,
            seed=st.seed_of("dev", "case14", 17, 0, 1))


def task(cht, arm, **kw):
    return dict(BASE, cht=cht, arm=arm, fixed=(0.5, 0.2, 0.05) if arm.startswith("FX") else None, **kw)


def test_seeds_collision_free():
    seeds = [st.seed_of(p, n, r, i, s) for p in st.PURPOSE for n in st.NETWORKS for r in st.RESOLUTIONS
             for i in range(6) for s in range(1, 21)]
    assert len(seeds) == len(set(seeds))


def test_fr_merit_is_deb_order():
    cht = st.CHT("FR", 10.0)
    rng = random.Random(1)
    raws = [st.Raw(rng.uniform(5, 15), rng.choice([0.0, rng.uniform(0, 2)]), rng.random() < 0.1) for _ in range(200)]

    def deb_key(r):
        return (2, 0) if r.failed else ((0, r.f) if r.V == 0 else (1, r.V))
    assert sorted(raws, key=cht.merit) == sorted(raws, key=deb_key)


def test_ec_schedule_and_limit():
    cht = st.CHT("EC", 10.0)
    initial = [st.Raw(10.0, v, False) for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)]
    cht.update(0, None, initial, 0.0)
    assert abs(cht.eps0 - 0.1) < 1e-12 and abs(cht.eps - 0.1) < 1e-12
    cht.update(1, None, initial, 0.25)
    assert abs(cht.eps - 0.1 * 0.5 ** 5) < 1e-15
    cht.update(2, None, initial, 0.5)
    assert cht.eps == 0.0
    fr = st.CHT("FR", 10.0)
    raws = [st.Raw(9.0, 0.0, False), st.Raw(8.0, 0.01, False), st.Raw(12.0, 0.0, False), st.Raw(9.0, 0.0, True)]
    assert sorted(raws, key=cht.merit) == sorted(raws, key=fr.merit)


def test_ap_counters_reset():
    cht = st.CHT("AP", 10.0)
    infeasible, feasible = st.Raw(10, 1.0, False), st.Raw(10, 0.0, False)
    for best in (infeasible, infeasible, infeasible):
        cht.update(1, best, [], 0.1)
    assert cht.lam == 2000.0 and cht.infeasible_streak == 0
    for best in (infeasible, infeasible, feasible, feasible, feasible):
        cht.update(1, best, [], 0.1)
    assert abs(cht.lam - 2000.0 / 1.5) < 1e-9


def test_same_initial_population_all_test_arms():
    tasks = [task(c, a) for c, a in st.TEST_ARMS]
    records = st.run_pool(tasks, 8)
    assert all(r["ok"] for r in records)
    assert all(len(r["initial"]) == st.POPULATION_SIZE and r["initial"] == records[0]["initial"] for r in records)


def test_instrument_counts_crossover_repairs():
    r = st.run_pool([task("SP", "AD-N", instrument=True)], 1)[0]
    inst = r["instrument"]
    assert inst["crossover_repairs"] == len(inst["crossover_repair_variables"])
    assert len(inst["v_fractions"]) > 0 and len(inst["sigmas"]) > 0


def test_execution_error_is_structured():
    bad = task("SP", "AD-N")
    bad["network"] = "case_does_not_exist"
    r = st.run(bad)
    assert r["ok"] is False and "error" in r


def test_runs_against_protocol():
    tasks = [task("SP", "AD-N"), task("SP", "AD-N", instrument=True), task("AP", "AD-N"), task("EC", "AD-N"),
             task("FR", "FX-T"), task("EC", "AD-C")]
    records = st.run_pool(tasks, 6)
    plain = st.run_pool([dict(BASE)], 1, st.run_plain)[0]
    sp, sp_instrumented, ap, ec, fx, adc = records
    for r in records:
        assert r["calls"] == 600 and r["complete"] and r["success"] and r["ok"]
        assert all(g["consistent"] for g in r["trace"])  # re-scalarization before truncation
    assert sp["sequence"] == plain["sequence"]  # AD-N/SP bit-identical to plain GAdapt on the same scalar
    assert sp_instrumented["sequence"] == sp["sequence"]  # logging does not change behaviour
    first = [r["initial"][:32] for r in records]
    assert all(f == first[0] for f in first)  # same seed -> same initial population in every arm
    d = len(sp["initial"][0])
    v = min(d, max(1, round(0.2 * d)))
    assert all(x == v for x in fx["fx"]["v"])
    for e in fx["fx"]["population_events"]:
        assert e["k"] == (0 if e["pool"] == 0 else min(e["pool"], max(1, round(0.5 * e["pool"]))))
    assert ap["cht_trace"][-1]["lam"] > 0 and ec["cht_trace"][0]["eps"] >= 0


def test_evaluator_counts_any_exception():
    class Problem:
        opf_losses = 10.0

        def evaluate(self, x):
            return dict(converged=True, losses=-1.0, violations=dict(voltage=0.0), feasible=True)
    evaluator = st.Evaluator(Problem(), 10, st.make_target(None))
    try:
        evaluator([1.0, 2.0])
    except AssertionError:
        pass
    assert evaluator.errors == 1
