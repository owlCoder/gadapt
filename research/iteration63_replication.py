"""I63: final conceptual replication of H56a with the fixed-budget win-score estimand.

Frozen protocol: research/ITERATION63_PROTOCOL.md (v2, frozen in 7c1f698 before this code and before any I63 measurement).
Reuses the I61 driver (OPF roster, instrument gate, provenance chain, tilting, Wilson, one-run machinery) and, through it, the
frozen I56/I58 instrument; none of those modules is modified. The I63-specific parts are the scenarios, seeds, estimand,
FX-T calibration statistic, rehearsal criteria, power simulation, freeze and analysis. Stages (each a fresh process):

  python research/iteration63_replication.py gate [workers]        (OPF roster + I56 instrument bit-identity, I61 gate on the
                                                                    current library; no I63 optimisation outcome is involved)
  python research/iteration63_replication.py normalizers           (OPF loss r_ij of every eligible scenario, recomputed independently)
  python research/iteration63_replication.py fxt [workers]
  python research/iteration63_replication.py rehearsal [workers]
  python research/iteration63_replication.py power
  python research/iteration63_replication.py freeze
  python research/iteration63_replication.py test [workers]
  python research/iteration63_replication.py check [workers]
  python research/iteration63_replication.py analyse

A stage that cannot continue under the protocol raises SystemExit("STOP: ..."). Every stage is create-once in the I63 directory
(research/results/iteration63); a final STOP is final (STOP.json blocks every later call).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = (os.path.join(os.environ.get("TMPDIR", "/tmp"), "i63_test_out") if (os.environ.get("I63_TESTING") or os.environ.get("I63_TEMP"))
       else os.path.join(HERE, "results", "iteration63"))  # fixed experiment identity (a new directory would allow re-deciding)
os.environ["I61_OUT"] = OUT  # the I61 machinery writes into the I63 directory
os.environ.setdefault("I61_LIBRARY", os.path.dirname(HERE))

import numpy as np  # noqa: E402

sys.path.insert(0, HERE)
import iteration61_replication as i61  # noqa: E402
import iteration56_cht_study as i56  # noqa: E402

assert i61.OUT == OUT

# ------------------------------------------------------------------ constants (protocol §2-§8)
NETWORKS = i61.NETWORKS
TESTING = bool(os.environ.get("I63_TESTING"))  # pipeline rehearsal in a temp directory only: tiny budget, relaxed thresholds
B = 300 if TESTING else 12000
TIE = 0.001
THETA = 0.05
TEST_SCENARIOS = ((0.92, 630201), (1.02, 630202), (1.08, 630203))  # j = 2, 3, 4 (new realisations)
i61.TEST_SCENARIOS = TEST_SCENARIOS  # scenario(j) of the I61 machinery (also in spawned workers: this module is re-imported)
ARMS = i61.ARMS
CALIBRATION_SEEDS, REHEARSAL_SEEDS = range(1, 4), range(1, 5 if TESTING else 21)
N_GRID = (8, 16) if TESTING else (80, 160, 240, 320, 480)
SIM = dict(experiments=20, reps=100, confirm_reps=200) if TESTING else dict(experiments=1000, reps=2000, confirm_reps=20000)
# frozen thresholds (§5, §6); the testing values only let the pipeline run through every stage
FEAS_MIN, NONTIE_MIN, NONZERO_MIN, VAR_MIN = (0, 0, 0, 0.0) if TESTING else (10, 8, 8, 0.02)
WILSON_POWER, WILSON_ERROR = (0.0, 1.0) if TESTING else (0.8, 0.05)
SEED_BASE = 1_700_000_000
PURPOSE = dict(fxt=1, rehearsal=2, test=3)
POWER_SEEDS = dict(screening=63023, confirmation=63024, calibration=63025)
BOOTSTRAP_SEED = 63
VARIANTS = ("pooled", "j0", "j1")
FXT_GRID = [tuple(g) for g in i56.FXT_GRID][:3 if TESTING else 27]
TARGETS = (THETA, 0.0, -THETA)  # §6 order: +0.05, 0, -0.05


def seed63(purpose, network, j, s):
    """SEED_BASE + 10^7 p + 10^6 i + 10^4 j + s; injective for i < 10, j < 10, s < 10^4 (asserted)."""
    i = NETWORKS.index(network)
    assert purpose in PURPOSE and 0 <= i < 10 and 0 <= j < 10 and 1 <= s < 10 ** 4
    return SEED_BASE + 10 ** 7 * PURPOSE[purpose] + 10 ** 6 * i + 10 ** 4 * j + s


def task63(network, j, cht, arm, purpose, s, fixed=None):
    return dict(network=network, j=j, cht=cht, arm=arm, purpose=purpose, s=s, seed=seed63(purpose, network, j, s),
                budget=B, reference=None, fixed=list(fixed) if fixed else None, stop=False)


# ------------------------------------------------------------------ provenance (I61 chain, I63 stage graph)
i61.CODE = i61.CODE + ("iteration63_replication.py", "test_iteration63_replication.py", "ITERATION63_PROTOCOL.md",
                       "iteration57_external.py", "test_iteration56_cht_study.py")
INPUTS = dict(normalizers=(), fxt=("normalizers",), rehearsal=("normalizers", "fxt"), power=("rehearsal",),
              freeze=("normalizers", "fxt", "rehearsal", "power"), test=("freeze",),
              check=("normalizers", "fxt", "rehearsal", "freeze", "test"), analysis=("normalizers", "freeze", "test", "check"))
_build_manifest = i61.build_manifest


def build_manifest(stage):
    m = _build_manifest(stage)
    m["settings"] = dict(m["settings"], i63=dict(B=B, tie=TIE, theta=THETA, test=TEST_SCENARIOS, seed_base=SEED_BASE,
                                                 purpose=PURPOSE, n_grid=N_GRID, power_seeds=POWER_SEEDS,
                                                 bootstrap_seed=BOOTSTRAP_SEED, fxt_grid=FXT_GRID,
                                                 i56_archive_sha256=sha256(i56.path("test.json.gz"))))
    return m


i61.build_manifest = build_manifest  # the gate, finish and publish of the I61 machinery use the I63 manifest
publish = i61.publish
load, save, artifact, path, sha256 = i61.load, i61.save, i61.artifact, i61.path, i61.sha256


import hashlib  # noqa: E402

_make61 = i61.make_problem


def signature63(p):
    """Hash of the scenario data the optimiser sees and of the OPF normalizer (§2: later construction must match)."""
    if not math.isfinite(p.opf_losses) or p.opf_losses <= 0:
        raise RuntimeError("invalid OPF normalizer")
    data = [p.opf_losses, p.lo, p.hi, p.step, p.bus_groups]
    raw = json.dumps(data, sort_keys=True, default=lambda x: x.tolist()).encode()
    return hashlib.sha256(raw).hexdigest()


def preflight63():
    """OPF eligibility of all 15 scenarios before any optimisation; only an explicit OPF failure excludes (§2)."""
    from iteration56_orpd import ScenarioError
    roster = dict(dev=[], test=[], excluded=[], scenario_hashes={})
    for n in NETWORKS:
        for j in range(5):
            try:
                p = _make61(n, j)
            except ScenarioError:
                roster["excluded"].append([n, j])
                continue
            roster["scenario_hashes"][f"{n}|{j}"] = signature63(p)
            roster["dev" if j < 2 else "test"].append([n, j])
    save("roster.json", roster)
    if any(j < 2 for _, j in roster["excluded"]) or any(sum(nn == n for nn, _ in roster["test"]) < 2 for n in NETWORKS):
        raise SystemExit(f"STOP: both development scenarios and >= 2 confirmatory scenarios per network are required "
                         f"{roster['excluded']} (§2)")
    return roster


def make_problem63(network, j):
    p = _make61(network, j)
    if signature63(p) != load("roster.json")["scenario_hashes"][f"{network}|{j}"]:
        raise RuntimeError("scenario or OPF normalizer differs from the frozen roster")  # RuntimeError: a worker returns a failed record
    return p


i61.make_problem = make_problem63
_chain61 = i61.verify_chain


def verify_chain63(stage, current):
    """I61 chain plus: the producer used this gate/roster and this freeze."""
    _chain61(stage, current)
    m = load(f"manifest_{stage}.json")
    gate = i61.verify_gate()
    if any(m.get(k) != gate[k] for k in ("gate_sha256", "roster_sha256")):
        raise SystemExit("STOP: a producer used another gate or roster")
    if "frozen_sha256" in m and m["frozen_sha256"] != sha256(path("manifest_frozen.json.gz")):
        raise SystemExit("STOP: a producer used another freeze")


i61.verify_chain = verify_chain63


def require_provenance(stage):
    """I61 pattern with the I63 stage graph; test/check/analysis additionally bind the freeze artifact and its manifest."""
    if os.path.exists(path(f"manifest_{stage}.json.gz")):
        raise SystemExit(f"STOP: {stage} already completed in this experiment directory (create-once)")
    gate = i61.verify_gate()
    current = build_manifest(stage)
    if not i61.same_provenance(gate, current):
        raise SystemExit("STOP: code, library, environment or settings differ from the gated build")
    inputs = {}
    for producer in INPUTS[stage]:
        i61.verify_chain(producer, current)
        inputs[producer] = sha256(artifact(producer))
    if stage in ("test", "check", "analysis"):
        frozen = load("manifest_frozen.json")
        bound = load("manifest_freeze.json")["frozen_sha256"]
        if not i61.same_provenance(frozen, current) or sha256(path("manifest_frozen.json.gz")) != bound:
            raise SystemExit("STOP: the build differs from the frozen manifest or the freeze changed")
        current["frozen_sha256"] = bound
    current["inputs_sha256"] = inputs
    current["gate_sha256"], current["roster_sha256"] = gate["gate_sha256"], gate["roster_sha256"]
    return current


# ------------------------------------------------------------------ one run (I61/I56 instrument, fixed budget, no stop)

def run63(task):
    """Defined here so that spawned workers re-import this module (and with it the I63 scenarios)."""
    record = i61.run(task)
    if record.get("ok"):
        # technical success needs exactly B real power flows (§7); anything else is a technical failure
        record["ok"] = record["calls"] == B and not record["errors"]
    return record


def execute(tasks, workers):
    """Fresh process per run; a technically failed run is repeated once with the same task and seed (§7). Failed first
    attempts and every repeat are archived in full (even if the stage later STOPs on a repeated failure)."""
    from multiprocessing import Pool
    purpose = tasks[0]["purpose"]
    with Pool(workers, maxtasksperchild=1) as pool:
        records = list(pool.imap(run63, tasks))
    for k, r in enumerate(records):
        if not r.get("ok"):
            save(f"attempt_{purpose}_{k}_1.json", r)
            with Pool(1, maxtasksperchild=1) as pool:
                again = pool.apply(run63, (tasks[k],))
            save(f"attempt_{purpose}_{k}_2.json", again)
            again["rerun"], again["first_attempt"] = True, r
            records[k] = again
    seen = [(t["network"], t["j"], t["cht"], t["arm"], tuple(t["fixed"] or ()), t["s"]) for t in (r["task"] for r in records)]
    assert len(seen) == len(set(seen)), "duplicate task"
    return records


def all_attempts(records):
    for r in records:
        if "first_attempt" in r:
            yield r["first_attempt"]
        yield r


def require_all_ok(records, what):
    """§7: a repeated technical failure of any planned branch is a final STOP (no selection, no exclusion)."""
    bad = [r["task"] for r in records if not r.get("ok")]
    if bad:
        raise SystemExit(f"STOP: {len(bad)} {what} runs failed technically twice (first {bad[0]}) (§7)")


def assert_seeds(tasks, units_of_task):
    """Seeds are unique across distinct units and shared only inside a unit."""
    owner = {}
    for t in tasks:
        unit = units_of_task(t)
        if owner.setdefault(t["seed"], unit) != unit:
            raise SystemExit(f"STOP: seed collision between units {owner[t['seed']]} and {unit}")
    return owner


def archive_seeds():
    """Optimisation seeds of the I56 and I58-I61 archives; an unreadable archive is an error, not silence."""
    import gzip
    seeds = set()
    for name in ("iteration56", "iteration58", "iteration59", "iteration60", "iteration61"):
        folder = os.path.join(HERE, "results", name)
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            if not f.endswith(".json.gz") or f.startswith("manifest"):
                continue
            with gzip.open(os.path.join(folder, f), "rt") as fh:
                stack = [json.load(fh)]
            while stack:
                x = stack.pop()
                if isinstance(x, dict):
                    if isinstance(x.get("seed"), int):
                        seeds.add(x["seed"])
                    stack.extend(x.values())
                elif isinstance(x, list):
                    stack.extend(x)
    return seeds


def check_archive_collisions(tasks):
    mine = {t["seed"] for t in tasks}
    clash = mine & archive_seeds()
    if clash:
        raise SystemExit(f"STOP: {len(clash)} I63 seeds collide with earlier archives (first {sorted(clash)[0]})")


# ------------------------------------------------------------------ estimand (§3)

def gap(record, r):
    """G = (f_best_feasible(B) - r)/r, or None for +inf (no feasible solution)."""
    f = record["best_feasible"]
    return None if f is None else (f - r) / r


def win2(f_cand, f_other, r):
    """2 x score of `cand` against `other` (§3): 2 = clear win, 0 = clear loss, 1 = tie; infeasibility ranks last."""
    if f_cand is None and f_other is None:
        return 1
    if f_cand is None:
        return 0
    if f_other is None:
        return 2
    delta = (f_other - f_cand) / r
    if delta > TIE:
        return 2
    if delta < -TIE:
        return 0
    return 1


def d2_of(unit, r):
    """2 x d = 2 x (W_FR - W_SP), W = score of FX-T against AD-N; unit = {(cht, arm): record}."""
    w = {c: win2(unit[(c, "FX-T")]["best_feasible"], unit[(c, "AD-N")]["best_feasible"], r) for c in ("FR", "SP")}
    return w["FR"] - w["SP"]


def d_of(unit, r):
    return d2_of(unit, r) / 2.0


def units_of(records):
    units = {}
    for rec in records:
        t = rec["task"]
        units.setdefault((t["network"], t["j"], t["s"]), {})[(t["cht"], t["arm"])] = rec
    return units


def normalizers():
    return load("normalizers.json")["r"]


# ------------------------------------------------------------------ stages

def stage_gate(workers):
    """Create-once. The library is the repository's current one (selected before the gate; no automatic fallback)."""
    if any(os.path.exists(path(f)) for f in ("roster.json.gz", "gate_current.json.gz", "gate.json.gz", "manifest_gate.json.gz")):
        raise SystemExit("STOP: the gate was already attempted (create-once)")
    if os.path.abspath(i61.LIB) != os.path.abspath(i61.REPO):
        raise SystemExit("STOP: the gate runs on the repository library")
    before = build_manifest("gate-before")
    preflight63()
    if not i61.gate_run("current", workers):
        raise SystemExit("STOP: the frozen I56 instrument is not bit-identical on the selected library (§2)")
    attempt = load("gate_current.json")
    if not (i61.same_provenance(before, attempt["manifest"]) and i61.same_provenance(before, build_manifest("gate-after"))):
        raise SystemExit("STOP: provenance changed during the gate")
    i61.select_gate("current")


def independent_opf_loss(network, j):
    """OPF branch losses rebuilt from raw pypower data (independent of iteration56_orpd)."""
    import contextlib
    import io
    from pypower import api
    case = getattr(api, network)()
    load_factor, scenario_seed = i61.scenario(j)
    rng = np.random.RandomState(scenario_seed)
    factor = load_factor * (1 + i56.SPREAD * (2 * rng.random_sample(case["bus"].shape[0]) - 1))
    case["bus"][:, 2] *= factor
    case["bus"][:, 3] *= factor
    with contextlib.redirect_stdout(io.StringIO()):
        opf = api.runopf(case, api.ppoption(VERBOSE=0, OUT_ALL=0))
    if not opf["success"]:
        return None
    return float(np.sum(opf["branch"][:, 13] + opf["branch"][:, 15]))


def normalizer_item(item):
    network, j = item
    r_instrument = i61.make_problem(network, j).opf_losses
    return dict(network=network, j=j, instrument=float(r_instrument), independent=independent_opf_loss(network, j))


def stage_normalizers(workers=4):
    from multiprocessing import Pool
    before = require_provenance("normalizers")
    roster = load("roster.json")
    cells = [tuple(x) for x in roster["dev"] + roster["test"]]
    with Pool(workers) as pool:
        rows = pool.map(normalizer_item, cells)
    r = {}
    for row in rows:
        ok = (row["independent"] is not None and math.isfinite(row["instrument"]) and row["instrument"] > 0
              and abs(row["instrument"] - row["independent"]) <= 1e-6 * row["instrument"])
        if not ok:
            raise SystemExit(f"STOP: OPF normalizer invalid or inconsistent {row} (§2)")
        r[f"{row['network']}|{row['j']}"] = row["instrument"]
    publish("normalizers", before, dict(r=r, rows=rows))


def dev_cells():
    return [tuple(x) for x in load("roster.json")["dev"]]


def test_cells():
    return [tuple(x) for x in load("roster.json")["test"]]


def stage_fxt(workers):
    before = require_provenance("fxt")
    cells = dev_cells()
    tasks = [task63(n, j, c, "FX-T", "fxt", s, fixed=g) for n, j in cells for c in ("SP", "FR") for g in FXT_GRID
             for s in CALIBRATION_SEEDS]
    check_archive_collisions(tasks)
    assert_seeds(tasks, lambda t: (t["network"], t["j"], t["s"]))
    records = execute(tasks, workers)
    i61.assert_paired(records)
    require_all_ok(records, "calibration")
    r = normalizers()
    chosen, totals = {}, {}
    for c in ("SP", "FR"):
        totals[c] = calibration_totals(records, c, r)
        chosen[c] = list(FXT_GRID[select_config(totals[c])])
    publish("fxt", before, dict(chosen=chosen, totals2=totals, records=records))


def calibration_totals(records, cht, r):
    """Integer sum of 2 x S_ijsc(k, l) over l != k, i, j, s for each FXT_GRID index k (§4)."""
    by_unit = {}
    for rec in records:
        t = rec["task"]
        if t["cht"] == cht:
            by_unit.setdefault((t["network"], t["j"], t["s"]), {})[tuple(t["fixed"])] = rec["best_feasible"]
    totals = [0] * len(FXT_GRID)
    for (n, j, _), by_config in by_unit.items():
        assert len(by_config) == len(FXT_GRID)
        for k, gk in enumerate(FXT_GRID):
            for ell, gl in enumerate(FXT_GRID):
                if ell != k:
                    totals[k] += win2(by_config[gk], by_config[gl], r[f"{n}|{j}"])
    return totals


def select_config(totals):
    """Largest integer total; the first FXT_GRID index on an exact tie (§4)."""
    best = max(totals)
    return totals.index(best)


def stage_rehearsal(workers):
    before = require_provenance("rehearsal")
    fxt = load("fxt.json")["chosen"]
    cells = dev_cells()
    tasks = [task63(n, j, c, a, "rehearsal", s, fixed=fxt[c] if a == "FX-T" else None)
             for n, j in cells for s in REHEARSAL_SEEDS for c, a in ARMS]
    check_archive_collisions(tasks)
    assert_seeds(tasks, lambda t: (t["network"], t["j"], t["s"]))
    records = execute(tasks, workers)
    i61.assert_paired(records)
    require_all_ok(records, "rehearsal")
    r = normalizers()
    units = units_of(records)
    criteria, pools = {}, {}
    for n in NETWORKS:
        mine = {k: u for k, u in units.items() if k[0] == n}
        rows = [dict(j=k[1], s=k[2], d=d_of(u, r[f"{n}|{k[1]}"]), w={c: win2(u[(c, "FX-T")]["best_feasible"],
                                                                         u[(c, "AD-N")]["best_feasible"],
                                                                         r[f"{n}|{k[1]}"]) for c in ("FR", "SP")},
                     gaps={f"{c}|{a}": gap(u[(c, a)], r[f"{n}|{k[1]}"]) for c, a in ARMS}) for k, u in sorted(mine.items())]
        complete = {j: sum(1 for x in rows if x["j"] == j) for j in (0, 1)}
        feasible = {f"{j}|{c}|{a}": sum(1 for k, u in mine.items() if k[1] == j and u[(c, a)]["best_feasible"] is not None)
                    for j in (0, 1) for c, a in ARMS}
        non_tie = {c: sum(1 for x in rows if x["w"][c] != 1) for c in ("FR", "SP")}
        d = np.array([x["d"] for x in rows], float)
        nonzero, variance = int(np.sum(d != 0)), float(np.mean((d - d.mean()) ** 2)) if len(d) else None
        ok = (all(v == len(REHEARSAL_SEEDS) for v in complete.values()) and all(v >= FEAS_MIN for v in feasible.values())
              and all(v >= NONTIE_MIN for v in non_tie.values()) and nonzero >= NONZERO_MIN and variance is not None
              and variance >= VAR_MIN)
        criteria[n] = dict(complete=complete, feasible=feasible, non_tie=non_tie, nonzero=nonzero, variance=variance,
                           passed=bool(ok))
        pools[n] = rows
    passed = all(c["passed"] for c in criteria.values())
    publish("rehearsal", before, dict(passed=passed, criteria=criteria, pools=pools, records=records))
    print(json.dumps(dict(passed=passed, criteria=criteria), indent=1))
    if not passed:
        raise SystemExit("STOP: rehearsal criteria not met (§5); final")


# ------------------------------------------------------------------ §6 power

def variant_pools(rehearsal, variant):
    """Pool of d values per network for a transfer assumption: pooled (all 40), j0 (20) or j1 (20)."""
    out = {}
    for n in NETWORKS:
        rows = rehearsal["pools"][n]
        out[n] = [x["d"] for x in rows if variant == "pooled" or x["j"] == int(variant[1])]
    return out


def tilt63(pools, target):
    """Tilt with a common lambda (I61 solver); strict attainability, error <= 1e-8, ESS_iv >= N_iv/2 (§6)."""
    t = i61.tilt(pools, target)
    if t is None and TESTING:  # pipeline rehearsal on tiny synthetic data: uniform weights stand in for an unattainable tilt
        w = [np.full(len(pools[n]), 1.0 / len(pools[n])) for n in NETWORKS]
        t = dict(lam=0.0, weights=[x.tolist() for x in w], error=0.0, ess=[float(len(x)) for x in w],
                 max_weight=[float(x.max()) for x in w])
    if t is None:
        return None
    t["n_pool"] = [len(pools[n]) for n in NETWORKS]
    t["ess_ok"] = TESTING or all(e >= m / 2 for e, m in zip(t["ess"], t["n_pool"]))
    return t


def decide(draws, observed_nonzero):
    """Decision function of §6 / §8 from the bootstrap draws of theta (shared by the simulation and the analysis)."""
    lo95, hi95, lo90, hi90 = np.percentile(draws, [2.5, 97.5, 5, 95])
    return dict(positive=bool(lo95 > 0), negative=bool(hi95 < 0),
                equivalent=bool(lo90 > -THETA and hi90 < THETA and observed_nonzero))


def simulate_once(pools, tilted, cells, n, reps, rng):
    """One simulated experiment: whole d-vectors drawn with the tilted weights per cell, inner multinomial bootstrap."""
    arrays = {k: np.asarray(pools[k], float) for k in NETWORKS}
    weights = dict(zip(NETWORKS, tilted["weights"]))
    network_draws, nonzero = {}, {n_: False for n_ in NETWORKS}
    for network, j in sorted(cells):
        counts = rng.multinomial(n, weights[network])
        nonzero[network] |= bool(np.any((counts > 0) & (arrays[network] != 0)))
        boot = rng.multinomial(n, counts / n, size=reps)
        network_draws.setdefault(network, []).append(boot @ arrays[network] / n)
    draws = np.mean([np.mean(v, axis=0) for v in network_draws.values()], axis=0)
    return decide(draws, all(nonzero[k] for k in network_draws))


def series(pools_by_variant, tilts, cells, n, experiments, reps, rng, wanted):
    """wanted: list of (variant, target); returns {(variant, target): counts of positive/negative/equivalent}."""
    out = {}
    for variant in VARIANTS:
        for target in TARGETS:
            if (variant, target) not in wanted:
                continue
            counts = dict(positive=0, negative=0, equivalent=0)
            for _ in range(experiments):
                d = simulate_once(pools_by_variant[variant], tilts[(variant, target)], cells, n, reps, rng)
                for k in counts:
                    counts[k] += d[k]
            out[(variant, target)] = counts
    return out


def key_of(variant, target):
    return f"{variant}|{target:+.2f}"


def stage_power():
    before = require_provenance("power")
    rehearsal = load("rehearsal.json")
    if not rehearsal["passed"]:
        raise SystemExit("STOP: rehearsal did not pass")
    cells = test_cells()
    pools = {v: variant_pools(rehearsal, v) for v in VARIANTS}
    tilts, report = {}, {}
    for v in VARIANTS:
        for t in TARGETS:
            tl = tilt63(pools[v], t)
            report[key_of(v, t)] = None if tl is None else {k: tl[k] for k in ("lam", "weights", "error", "ess", "n_pool",
                                                                            "max_weight", "ess_ok")}
            if tl is None or tl["error"] > 1e-8 or not tl["ess_ok"]:
                publish("power", before, dict(cells=cells, tilts=report))
                raise SystemExit(f"STOP: tilt {key_of(v, t)} unattainable, inaccurate or ESS below N/2 (§6)")
            tilts[(v, t)] = tl
    out = dict(cells=cells, tilts=report)
    rng = np.random.default_rng(POWER_SEEDS["screening"])
    wanted = [(v, THETA) for v in VARIANTS] + [(v, 0.0) for v in VARIANTS]
    screening, chosen = {}, None
    for n in N_GRID:
        res = series(pools, tilts, cells, n, SIM["experiments"], SIM["reps"], rng, wanted)
        screening[n] = {key_of(*k): dict(counts=c, wilson_pos=i61.wilson(c["positive"], SIM["experiments"]),
                                         wilson_equiv=i61.wilson(c["equivalent"], SIM["experiments"])) for k, c in res.items()}
        if all(i61.wilson(res[(v, THETA)]["positive"], SIM["experiments"])[0] >= WILSON_POWER
               and i61.wilson(res[(v, 0.0)]["equivalent"], SIM["experiments"])[0] >= WILSON_POWER for v in VARIANTS):
            chosen = n
            break
    out["screening"] = screening
    if chosen is None:
        publish("power", before, out)
        raise SystemExit("STOP: no n <= 480 reaches power 0.8 in all three transfer variants (§6); final")
    rng = np.random.default_rng(POWER_SEEDS["confirmation"])
    conf = series(pools, tilts, cells, chosen, SIM["experiments"], SIM["confirm_reps"], rng, [(v, THETA) for v in VARIANTS] + [(v, 0.0) for v in VARIANTS])
    confirmation = {key_of(*k): dict(counts=c, wilson_pos=i61.wilson(c["positive"], SIM["experiments"]),
                                     wilson_equiv=i61.wilson(c["equivalent"], SIM["experiments"])) for k, c in conf.items()}
    conf_ok = all(i61.wilson(conf[(v, THETA)]["positive"], SIM["experiments"])[0] >= WILSON_POWER
                  and i61.wilson(conf[(v, 0.0)]["equivalent"], SIM["experiments"])[0] >= WILSON_POWER for v in VARIANTS)
    rng = np.random.default_rng(POWER_SEEDS["calibration"])
    cal = series(pools, tilts, cells, chosen, SIM["experiments"], SIM["confirm_reps"], rng, [(v, t) for v in VARIANTS for t in TARGETS])
    calibration = {key_of(*k): dict(counts=c, wilson_pos=i61.wilson(c["positive"], SIM["experiments"]),
                                    wilson_neg=i61.wilson(c["negative"], SIM["experiments"]), wilson_equiv=i61.wilson(c["equivalent"], SIM["experiments"]))
                   for k, c in cal.items()}
    cal_ok = all(i61.wilson(cal[(v, 0.0)]["positive"], SIM["experiments"])[1] <= WILSON_ERROR and i61.wilson(cal[(v, 0.0)]["negative"], SIM["experiments"])[1] <= WILSON_ERROR
                 and i61.wilson(cal[(v, THETA)]["equivalent"], SIM["experiments"])[1] <= WILSON_ERROR
                 and i61.wilson(cal[(v, -THETA)]["equivalent"], SIM["experiments"])[1] <= WILSON_ERROR for v in VARIANTS)
    out.update(chosen_n=chosen, confirmation=confirmation, calibration=calibration, passed=bool(conf_ok and cal_ok),
               confirmation_ok=bool(conf_ok), calibration_ok=bool(cal_ok))
    publish("power", before, out)
    print(json.dumps({k: out[k] for k in ("chosen_n", "confirmation_ok", "calibration_ok", "passed")}, indent=1))
    if not out["passed"]:
        raise SystemExit("STOP: power confirmation or null/equivalence calibration failed (§6); final")


# ------------------------------------------------------------------ freeze, test, check, analysis

def stage_freeze():
    current = require_provenance("freeze")
    power = load("power.json")
    if not power.get("passed"):
        raise SystemExit("STOP: power stage did not pass")
    if os.path.exists(path("manifest_frozen.json.gz")):
        raise SystemExit("STOP: the choices are already frozen (create-once)")
    choices = dict(fxt=load("fxt.json")["chosen"], n=power["chosen_n"], cells=test_cells())
    save("manifest_frozen.json", dict(current, choices=choices,
                                      hashes={f: sha256(path(f + ".gz")) for f in
                                              ("roster.json", "normalizers.json", "fxt.json", "rehearsal.json", "power.json")}))
    current["frozen_sha256"] = sha256(path("manifest_frozen.json.gz"))
    publish("freeze", current, dict(choices=choices))


def require_frozen():
    frozen = load("manifest_frozen.json")
    if frozen["choices"]["n"] != load("power.json")["chosen_n"] or frozen["choices"]["fxt"] != load("fxt.json")["chosen"] \
            or [list(x) for x in frozen["choices"]["cells"]] != [list(x) for x in test_cells()]:
        raise SystemExit("STOP: development choices changed after freezing")
    for f, h in frozen["hashes"].items():
        if sha256(path(f + ".gz")) != h:
            raise SystemExit(f"STOP: {f} changed after freezing")
    return frozen


def stage_test(workers):
    current = require_provenance("test")
    choices = require_frozen()["choices"]
    tasks = [task63(n, j, c, a, "test", s, fixed=choices["fxt"][c] if a == "FX-T" else None)
             for n, j in test_cells() for s in range(1, choices["n"] + 1) for c, a in ARMS]
    check_archive_collisions(tasks)
    assert_seeds(tasks, lambda t: (t["network"], t["j"], t["s"]))
    records = execute(tasks, workers)
    i61.assert_paired(records)
    publish("test", current, dict(choices=choices, manifest=current, records=records,
                                  all_ok=all(r.get("ok") for r in records)))
    require_all_ok(records, "confirmatory")


def check_item(item):
    """I58 independent checker with the I63 scenarios (this module is what workers import)."""
    return i61.independent_check(item)


def stage_check(workers):
    from multiprocessing import Pool
    before = require_provenance("check")
    items = []
    for source in ("fxt", "rehearsal", "test"):
        for r in all_attempts(load(f"{source}.json")["records"]):
            if r.get("best_feasible") is not None:
                t = r["task"]
                items.append(((t["network"], t["j"], r["best_feasible_x"]), dict(source=source, value=r["best_feasible"])))
    with Pool(workers) as pool:
        checks = pool.map(check_item, [x for x, _ in items], chunksize=64)
    failures = {}
    for (_, m), c in zip(items, checks):
        ok = bool(c.get("valid") and c.get("converged") and c.get("feasible")
                  and abs(c["losses"] - m["value"]) <= 1e-6 * max(1.0, m["value"]))
        if not ok:
            failures[m["source"]] = failures.get(m["source"], 0) + 1
    publish("check", before, dict(expected=len(items), rows=len(checks), failures=failures,
                                  bound={k: sha256(artifact(k)) for k in INPUTS["check"]}))
    print("checked", len(checks), "failures", failures)
    if failures or len(checks) != len(items):
        raise SystemExit(1)


def bootstrap(cells, reps=20000, seed=BOOTSTRAP_SEED):
    """cells: {(network, j): [d, ...]}; equal weights over networks and over each network's scenarios; one rng, one set
    of draws for the 95% and the 90% intervals."""
    rng = np.random.default_rng(seed)
    blocks = {}
    for key in sorted(cells):
        v = np.asarray(cells[key], float)
        blocks.setdefault(key[0], []).append(v[rng.integers(0, len(v), size=(reps, len(v)))].mean(axis=1))
    draws = np.mean([np.mean(b, axis=0) for b in blocks.values()], axis=0)
    point = float(np.mean([np.mean([np.mean(cells[k]) for k in cells if k[0] == n]) for n in blocks]))
    nonzero = all(any(x != 0 for k in cells if k[0] == n for x in cells[k]) for n in blocks)
    lo95, hi95, lo90, hi90 = np.percentile(draws, [2.5, 97.5, 5, 95])
    return dict(estimate=point, ci95=[float(lo95), float(hi95)], ci90=[float(lo90), float(hi90)], **decide(draws, nonzero))


def analyse():
    before = require_provenance("analysis")
    check = load("check.json")
    if check["failures"] or check["rows"] != check["expected"] or check["bound"] != {k: sha256(artifact(k)) for k in INPUTS["check"]}:
        raise SystemExit("STOP: independent check missing, failed or not bound to these artifacts")
    data = load("test.json")
    if not i61.same_provenance(data["manifest"], build_manifest("analysis")):
        raise SystemExit("STOP: provenance differs from the test manifest")
    choices = require_frozen()["choices"]
    r = normalizers()
    cells_list = test_cells()
    planned = [(n, j, s) for n, j in cells_list for s in range(1, choices["n"] + 1)]
    units = units_of(data["records"])
    if sorted(units) != sorted(planned) or any(set(u) != set(ARMS) or not all(x["ok"] for x in u.values()) for u in units.values()):
        raise SystemExit("STOP: the confirmatory records are not exactly the planned complete units")
    cells = {}
    for (n, j, s), u in sorted(units.items()):
        cells.setdefault((n, j), []).append(d_of(u, r[f"{n}|{j}"]))
    primary = bootstrap(cells)
    network_means = {n: float(np.mean([np.mean(v) for k, v in cells.items() if k[0] == n])) for n in NETWORKS}
    leave_out = {n: float(np.mean([m for k, m in network_means.items() if k != n])) for n in NETWORKS}
    expansion = bool(primary["ci95"][0] > THETA and sum(m > 0 for m in network_means.values()) >= 2
                     and all(v > 0 for v in leave_out.values()))
    descriptive = {}
    for n, j in cells_list:
        us = [u for (nn, jj, _), u in units.items() if (nn, jj) == (n, j)]
        rr = r[f"{n}|{j}"]
        row = {"d_mean": float(np.mean(cells[(n, j)])), "n": len(us)}
        for c, a in ARMS:
            g = [gap(u[(c, a)], rr) for u in us]
            fin = [x for x in g if x is not None]
            row[f"{c}|{a}"] = dict(feasible=len(fin) / len(g), mean_gap=float(np.mean(fin)) if fin else None,
                                   median_gap=float(np.median(fin)) if fin else None)
            row[f"MW|{c}|{a}"] = [None if u[(c, a)]["best_feasible"] is None else u[(c, a)]["best_feasible"] - rr for u in us]
        for c in ("FR", "SP"):
            row[f"W|{c}"] = float(np.mean([win2(u[(c, 'FX-T')]["best_feasible"], u[(c, 'AD-N')]["best_feasible"], rr) / 2 for u in us]))
        descriptive[f"{n}|{j}"] = row
    out = dict(H63=primary, network_means=network_means, leave_one_network_out=leave_out, expansion_rule_met=expansion,
               planned_units=len(planned), choices=choices, descriptive=descriptive)
    publish("analysis", before, out)
    print(json.dumps(dict(H63=primary, network_means=network_means, expansion=expansion), indent=1))


STAGES = dict(gate=stage_gate, normalizers=stage_normalizers, fxt=stage_fxt, rehearsal=stage_rehearsal, test=stage_test,
              check=stage_check)

if __name__ == "__main__":
    actions = dict(STAGES, power=lambda _: stage_power(), freeze=lambda _: stage_freeze(), analyse=lambda _: analyse())
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    if stage not in actions:
        raise SystemExit(__doc__)
    if os.path.exists(path("STOP.json.gz")):
        raise SystemExit("STOP: the experiment is terminal (STOP.json)")
    with open(path("attempts.log"), "a") as log:  # an interrupted stage (crash) may be restarted; a protocol STOP may not
        log.write(f"{stage}\n")
    try:
        actions[stage](workers)
    except SystemExit as exc:
        if str(exc.code).startswith("STOP:"):
            save("STOP.json", dict(stage=stage, reason=str(exc.code)))
        raise
