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


def _synthetic(monkeypatch, drop=()):
    """Synthetic I60 test records (no real result is read): G2 always 0.2 faster than G0."""
    records = []
    for n in i58.PRIMARY:
        for j in range(3):
            for s in range(1, 16):
                for a in i60.ARMS:
                    ok = (n, j, s, a) not in drop
                    records.append(dict(task=dict(network=n, j=j, seed=s, arm=a), ok=ok,
                                        T=0.5 if a == "G0" else 0.3, best_feasible=1.0))
    store = {"i60_test.json": dict(records=records, excluded=[]),
             "i60_check.json": dict(failures={}, checks=[1], bound=dict(test="t", refs="r")),
             "i60_manifest.json": dict(m=1)}
    saved = {}
    monkeypatch.setattr(i60.i56, "load", lambda name: store[name])
    monkeypatch.setattr(i60.i56, "save", lambda name, value: saved.__setitem__(name, value))
    monkeypatch.setattr(i60.i56, "path", lambda name: "i60_test.json.gz" if "i60" in name else "refs")
    monkeypatch.setattr(i60.i57, "sha256", lambda path: "t" if "i60" in path else "r")
    monkeypatch.setattr(i60, "manifest", lambda stage: dict(m=1))
    monkeypatch.setattr(i60, "same_provenance", lambda a, b: a == b)
    monkeypatch.setattr(i60, "require_i58_reference_check", lambda: None)
    i60.analyse()
    return saved["i60_analysis.json"]


def test_analysis_follows_the_i58_exclusion_and_sensitivity_rules(monkeypatch):
    out = _synthetic(monkeypatch)
    assert abs(out["H60"]["estimate"] + 0.2) < 1e-12 and out["H60"]["supported"] and out["sensitivity"] is None
    # one failed run: the pair is excluded but primary inference stays available (I58 rules), no sensitivity (<= 5%)
    out = _synthetic(monkeypatch, drop={("case30", 0, 1, "G2")})
    assert len(out["excluded"]) == 1 and out["H60"] is not None and out["sensitivity"] is None
    # a whole network x scenario cell lost: no primary inference, sensitivity with failed runs as T = 1
    out = _synthetic(monkeypatch, drop={("case39", 1, s, "G0") for s in range(1, 16)})
    assert out["H60"] is None and out["empty_cells"] == [["case39", "1"]] and out["sensitivity"] is not None


def test_provenance_includes_the_i60_fields(monkeypatch):
    base = {f: 1 for f in i58.PROVENANCE + i60.I60_PROVENANCE}
    assert i60.same_provenance(base, dict(base))
    for f in i60.I60_PROVENANCE:
        assert not i60.same_provenance(base, dict(base, **{f: 2}))
