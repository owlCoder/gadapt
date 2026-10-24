"""I61: replication of the H56a interaction (adaptation x CHT) on the I58 networks with new scenarios.

Frozen protocol: research/ITERATION61_PROTOCOL.md (frozen before any I58 test result and before this code).
Reuses the I56 instrument (CHT, CHTCostFinder, StudyFactory; constraint_handling=None) and the I58 BusORPD and
independent checker; neither frozen module is modified. Stages, in order (each one a fresh process):

  python research/iteration61_replication.py gate [workers]        (I56 instrument bit-identity on this library)
  python research/iteration61_replication.py dev_ref [workers]
  python research/iteration61_replication.py select_b [workers]
  python research/iteration61_replication.py fxt [workers]
  python research/iteration61_replication.py stopcheck [workers]
  python research/iteration61_replication.py rehearsal [workers]
  python research/iteration61_replication.py power
  python research/iteration61_replication.py test_ref [workers]
  python research/iteration61_replication.py test [workers]
  python research/iteration61_replication.py check [workers]
  python research/iteration61_replication.py analyse

A stage that cannot continue under the protocol raises SystemExit("STOP: ...") and writes nothing further.
"""
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for p in (REPO, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402

import iteration56_cht_study as i56  # noqa: E402
import iteration58_validation as i58  # noqa: E402

OUT = os.path.join(HERE, "results", "iteration61")
NETWORKS = ("case30", "case39", "case24_ieee_rts")
R = 17
DEV_SCENARIOS = ((0.97, 6101), (1.03, 6102))  # j = 0, 1
TEST_SCENARIOS = ((0.92, 6201), (1.02, 6202), (1.08, 6203))  # j = 2, 3, 4
REF_BUDGET = 30000
B_GRID = (3000, 6000, 12000)
N_GRID = (80, 160, 240, 320, 480)
ARMS = (("FR", "AD-N"), ("FR", "FX-T"), ("SP", "AD-N"), ("SP", "FX-T"))
REF_CHTS = ("SP", "AP", "FR", "EC")
PURPOSE = dict(dev_ref=61, select_b=62, fxt=63, rehearsal=64, test_ref=65, test=66, stopcheck=67)
SELECT_SEEDS, FXT_SEEDS, REHEARSAL_SEEDS = range(1, 6), range(1, 4), range(1, 11)
TARGET_THETA = 0.02


def seed_of(purpose, network, j, s):
    """§9: 10^7 p + 10^6 i + 10^4 R + 10^3 j + s; injective for i, j < 10 and s < 1000 (asserted)."""
    i = NETWORKS.index(network)
    assert 0 <= i < 10 and 0 <= j < 10 and 1 <= s < 1000
    return 10 ** 7 * PURPOSE[purpose] + 10 ** 6 * i + 10 ** 4 * R + 10 ** 3 * j + s


def scenario(j):
    return (DEV_SCENARIOS + TEST_SCENARIOS)[j]


# ------------------------------------------------------------------ files and provenance

def path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def save(name, data):
    import gzip
    with gzip.open(path(name + ".gz"), "wt") as f:
        json.dump(data, f)


def load(name):
    import gzip
    with gzip.open(path(name + ".gz"), "rt") as f:
        return json.load(f)


def sha256(file):
    with open(file, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


CODE = ("iteration61_replication.py", "iteration56_cht_study.py", "iteration56_orpd.py", "iteration58_validation.py",
        "ITERATION61_PROTOCOL.md")


def build_manifest(stage):
    import platform
    import subprocess
    tree = {}
    for root, _, files in os.walk(os.path.join(REPO, "gadapt")):
        for f in sorted(files):
            if f.endswith(".py"):
                full = os.path.join(root, f)
                tree[os.path.relpath(full, REPO)] = sha256(full)
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.split()
    return dict(stage=stage, python=platform.python_version(), pip_freeze=freeze, gadapt_tree_sha256=tree,
                code_sha256={f: sha256(os.path.join(HERE, f)) for f in CODE},
                settings=dict(networks=NETWORKS, R=R, dev=DEV_SCENARIOS, test=TEST_SCENARIOS, spread=i56.SPREAD,
                              ref_budget=REF_BUDGET, b_grid=B_GRID, n_grid=N_GRID, arms=ARMS, ref_chts=REF_CHTS,
                              purpose=PURPOSE, population=i56.POPULATION_SIZE, fxt_grid=i56.FXT_GRID,
                              ga_resolved=i58.resolved_ga_settings()))


PROVENANCE = ("python", "pip_freeze", "gadapt_tree_sha256", "code_sha256", "settings")


def same_provenance(a, b):
    return all(i58.normalised(a[f]) == i58.normalised(b[f]) for f in PROVENANCE)


def require_provenance(stage):
    """Every stage after the gate runs on exactly the gated build."""
    gate = load("manifest_gate.json")
    if not load("gate.json")["passed"]:
        raise SystemExit("STOP: the instrument gate did not pass")
    current = build_manifest(stage)
    if not same_provenance(gate, current):
        raise SystemExit("STOP: code, library, environment or settings differ from the gated build")
    save(f"manifest_{stage}.json", current)
    return current


# ------------------------------------------------------------------ one run

class StopEvaluator(i58.WitnessEvaluator):
    """I58 witness evaluator; optionally done at the first target (§10). Also keeps the genotypes passed to the cost
    function for the first population (the generated initial population, evaluated or not) and the PF-sequence hash
    at the first target (prefix through h)."""

    def __init__(self, problem, budget, target, stop=False):
        super().__init__(problem, budget, target)
        self.stop = stop
        self.generated = []
        self.prefix_at_target = None

    @property
    def done(self):
        return self.calls >= self.budget or (self.stop and self.first_target is not None)

    def _call(self, values):
        if len(self.generated) < i56.POPULATION_SIZE:
            self.generated.append(tuple(values))
        before = self.first_target
        result = super()._call(values)
        if before is None and self.first_target is not None:
            self.prefix_at_target = self.sequence.copy().hexdigest()
        return result


def make_problem(network, j):
    load_factor, scenario_seed = scenario(j)
    return i58.BusORPD(network, R, load_factor, i56.SPREAD, scenario_seed)


def run(task):
    import traceback
    try:
        return _run(task)
    except Exception:
        return dict(task=task, ok=False, error=traceback.format_exc()[-2000:], T=None)


def _run(task):
    """task: dict(network, j, cht, arm, seed, budget, reference, fixed, stop)."""
    from gadapt.ga import GA
    problem = make_problem(task["network"], task["j"])
    evaluator = StopEvaluator(problem, task["budget"], i56.make_target(task.get("reference")), task.get("stop", False))
    cht = i56.CHT(task["cht"], evaluator.f_ref)
    log = []
    factory = i56.StudyFactory(evaluator, cht, task["arm"], log, task.get("fixed"), None)
    random.seed(task["seed"])
    np.random.seed(task["seed"])
    ga = GA(cost_function=evaluator, probe_cost_function=False, exit_check="generations",
            number_of_generations=10 ** 9, exit_function=lambda *a, **k: evaluator.done, timeout=10 ** 6,
            factory=factory)
    for lo, hi, step in zip(problem.lo, problem.hi, problem.step):
        ga.add(float(lo), float(hi), float(step))
    result = ga.execute()
    first = evaluator.first_target
    # §10: success = no error and either a (witnessed) target or the whole budget
    complete = evaluator.calls >= task["budget"] or (task.get("stop", False) and first is not None)
    best_x = None
    if math.isfinite(evaluator.best_feasible):
        best_x = next(list(k) for k, r in evaluator.cache.items() if r.feasible and r.f == evaluator.best_feasible)
    return dict(task=task, calls=evaluator.calls, complete=complete, success=bool(result.success),
                errors=evaluator.errors, ok=complete and bool(result.success) and evaluator.errors == 0,
                T=(first / task["budget"]) if first is not None else 1.0, first_target=first,
                first_target_x=evaluator.first_target_x, prefix_at_target=evaluator.prefix_at_target,
                first_feasible=evaluator.first_feasible,
                best_feasible=evaluator.best_feasible if math.isfinite(evaluator.best_feasible) else None,
                best_feasible_x=best_x, failures=evaluator.failures, generations=len(log),
                generated=[list(k) for k in evaluator.generated], initial=[list(k) for k in evaluator.initial],
                sequence=evaluator.sequence.hexdigest())


def execute(tasks, workers, function=None):
    """Fresh process per run; a failed run is retried once with the same seed (§10)."""
    from multiprocessing import Pool
    function = function or run
    with Pool(workers, maxtasksperchild=1) as pool:
        records = list(pool.imap(function, tasks))
    for i, r in enumerate(records):
        if not r.get("ok"):
            with Pool(1, maxtasksperchild=1) as pool:
                again = pool.apply(function, (tasks[i],))
            again["rerun"], again["first_attempt"] = True, {k: v for k, v in r.items() if k != "generated"}
            records[i] = again
    return records


def task(network, j, cht, arm, purpose, s, budget, reference=None, fixed=None, stop=False):
    return dict(network=network, j=j, cht=cht, arm=arm, purpose=purpose, s=s, seed=seed_of(purpose, network, j, s),
                budget=budget, reference=reference, fixed=list(fixed) if fixed else None, stop=stop)


def instances(kind):
    """(network, j) with a successful OPF, determined before the stage's optimisation runs (§2)."""
    from iteration56_orpd import ScenarioError
    js = (0, 1) if kind == "dev" else (2, 3, 4)
    valid, excluded = [], []
    for n in NETWORKS:
        for j in js:
            try:
                make_problem(n, j)
                valid.append((n, j))
            except ScenarioError:
                excluded.append([n, j])
    if kind == "dev" and excluded:
        raise SystemExit(f"STOP: development scenario OPF failed {excluded} (both are required, §2)")
    if kind == "test" and {n for n, _ in valid} != set(NETWORKS):
        raise SystemExit(f"STOP: a network has no test scenario with a successful OPF {excluded} (§2)")
    return valid, excluded


def references(records):
    """L* per (network, j) = best feasible loss over successful reference runs; None = feasibility target;
    an instance without any successful reference run -> STOP (§4)."""
    best, any_ok = {}, set()
    for r in records:
        key = f"{r['task']['network']}|{r['task']['j']}"
        best.setdefault(key, math.inf)
        if r.get("ok"):
            any_ok.add(key)
            if r["best_feasible"] is not None:
                best[key] = min(best[key], r["best_feasible"])
    missing = sorted(set(best) - any_ok)
    if missing:
        raise SystemExit(f"STOP: no successful reference run for {missing} (§4)")
    return {k: (v if math.isfinite(v) else None) for k, v in best.items()}


def assert_paired(records, arms=ARMS):
    """The arms of one unit start from the same generated initial population (§9)."""
    units = {}
    for r in records:
        if r.get("ok"):
            t = r["task"]
            units.setdefault((t["network"], t["j"], t["s"]), {})[(t["cht"], t["arm"])] = r["generated"]
    for key, u in units.items():
        values = [u[a] for a in arms if a in u]
        if any(v != values[0] or len(v) != i56.POPULATION_SIZE for v in values):
            raise SystemExit(f"STOP: generated initial populations differ between arms for {key}")


# ------------------------------------------------------------------ §3 gate

GATE_FIELDS = ("calls", "complete", "success", "errors", "ok", "T", "first_target", "first_feasible", "best_feasible",
               "min_violation", "failures", "generations", "sequence", "initial", "trace", "cht_trace", "fx")


def gate_tasks():
    """The archived I56 test tasks: all 9 network x R, scenario j = 2 (0.90; 201), s = 1, SP/FR x AD-N/FX-T and
    AP/EC x AD-N (54 runs)."""
    wanted = {(c, a) for c in ("SP", "FR") for a in ("AD-N", "FX-T")} | {("AP", "AD-N"), ("EC", "AD-N")}
    archived = {}
    for r in i56.load("test.json")["records"]:
        t = r["task"]
        if t["scenario_index"] == 2 and t["seed"] == i56.seed_of("test", t["network"], t["resolution"], 2, 1) \
                and (t["cht"], t["arm"]) in wanted:
            archived[(t["network"], t["resolution"], t["cht"], t["arm"])] = r
    if len(archived) != 54:
        raise SystemExit(f"STOP: expected 54 archived gate tasks, found {len(archived)}")
    return archived


def stage_gate(workers):
    import subprocess
    manifest = build_manifest("gate")
    save("manifest_gate.json", manifest)
    archived = gate_tasks()
    keys = sorted(archived)
    tasks = [dict(archived[k]["task"]) for k in keys]
    rerun = i56.run_pool(tasks, workers)
    mismatches = []
    for k, new in zip(keys, rerun):
        old = archived[k]
        new = i58.normalised(new)
        for f in GATE_FIELDS:
            if (f in old or f in new) and old.get(f) != new.get(f):
                mismatches.append(dict(task=list(map(str, k)), field=f))
    plain_tasks = [dict(archived[k]["task"]) for k in keys if k[2:] == ("SP", "AD-N")]
    plain = i56.run_pool(plain_tasks, workers, i56.run_plain)
    for t, p in zip(plain_tasks, plain):
        k = (t["network"], t["resolution"], "SP", "AD-N")
        if p["sequence"] != archived[k]["sequence"] or p["calls"] != archived[k]["calls"]:
            mismatches.append(dict(task=list(map(str, k)), field="run_plain"))
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                            os.path.join(HERE, "test_iteration56_cht_study.py")], capture_output=True, text=True)
    passed = not mismatches and tests.returncode == 0
    save("gate.json", dict(passed=passed, runs=len(rerun), plain=len(plain), mismatches=mismatches,
                           i56_tests=tests.stdout[-2000:], i56_tests_returncode=tests.returncode))
    print(json.dumps(dict(passed=passed, runs=len(rerun), mismatches=len(mismatches)), indent=1))
    if not passed:
        raise SystemExit("STOP: the I56 instrument is not bit-identical on this library (§3)")


# ------------------------------------------------------------------ §4 development references, §5 budget

def stage_dev_ref(workers):
    require_provenance("dev_ref")
    valid, _ = instances("dev")
    tasks = [task(n, j, c, "AD-N", "dev_ref", 1, REF_BUDGET) for n, j in valid for c in REF_CHTS]
    records = execute(tasks, workers)
    save("dev_ref.json", dict(records=records, references=references(records)))


def t_of(record, budget):
    h = record["first_target"]
    return min(h / budget, 1.0) if h is not None else 1.0


def stage_select_b(workers):
    require_provenance("select_b")
    refs = load("dev_ref.json")["references"]
    valid, _ = instances("dev")
    tasks = [task(n, j, c, "AD-N", "select_b", s, max(B_GRID), refs[f"{n}|{j}"])
             for n, j in valid for c in ("SP", "FR") for s in SELECT_SEEDS]
    records = execute(tasks, workers)
    if not all(r["ok"] for r in records):
        raise SystemExit("STOP: a budget-selection run failed twice (the medians would be incomplete)")
    chosen, table = {}, {}
    for n in NETWORKS:
        for b in B_GRID:
            medians = {f"{c}|{j}": float(np.median([t_of(r, b) for r in records if r["task"]["network"] == n
                                                     and r["task"]["cht"] == c and r["task"]["j"] == j]))
                       for c in ("SP", "FR") for j in (0, 1)}
            table[f"{n}|{b}"] = medians
            if n not in chosen and all(0.3 <= m <= 0.8 for m in medians.values()):
                chosen[n] = b
    save("select_b.json", dict(chosen=chosen, medians=table, records=records))
    if set(chosen) != set(NETWORKS):
        raise SystemExit(f"STOP: no admissible budget for {sorted(set(NETWORKS) - set(chosen))} (§5)")


# ------------------------------------------------------------------ §6 FX-T

def stage_fxt(workers):
    require_provenance("fxt")
    refs = load("dev_ref.json")["references"]
    budgets = load("select_b.json")["chosen"]
    valid, _ = instances("dev")
    tasks = [task(n, j, c, "FX-T", "fxt", s, budgets[n], refs[f"{n}|{j}"], fixed=g)
             for n, j in valid for c in ("SP", "FR") for g in i56.FXT_GRID for s in FXT_SEEDS]
    records = execute(tasks, workers)
    chosen = {}
    for c in ("SP", "FR"):
        groups = [[r["T"] for r in records if r["ok"] and r["task"]["cht"] == c and r["task"]["fixed"] == list(g)]
                  for g in i56.FXT_GRID]
        if any(len(g) != len(valid) * len(FXT_SEEDS) for g in groups):
            raise SystemExit(f"STOP: FX-T calibration incomplete for {c} (§6)")
        chosen[c] = list(i56.FXT_GRID[int(np.argmin([np.mean(g) for g in groups]))])  # balanced: equal weights
    save("fxt.json", dict(chosen=chosen, records=records))


# ------------------------------------------------------------------ §10 stop-at-target validation

def stage_stopcheck(workers):
    require_provenance("stopcheck")
    refs = load("dev_ref.json")["references"]
    budgets = load("select_b.json")["chosen"]
    fxt = load("fxt.json")["chosen"]
    valid, _ = instances("dev")
    pairs = [(n, j, c, a) for n, j in valid for c, a in ARMS]
    tasks = [task(n, j, c, a, "stopcheck", 1, budgets[n], refs[f"{n}|{j}"], fixed=fxt[c] if a == "FX-T" else None,
                  stop=stop) for n, j, c, a in pairs for stop in (False, True)]
    records = execute(tasks, workers)
    mismatches, attained = [], 0
    for k in range(len(pairs)):
        full, stopped = records[2 * k], records[2 * k + 1]
        if not (full["ok"] and stopped["ok"]):
            mismatches.append(dict(pair=list(pairs[k]), reason="run failed"))
            continue
        if full["first_target"] is not None:
            attained += 1
        same = (full["first_target"] == stopped["first_target"] and full["generated"] == stopped["generated"]
                and (full["prefix_at_target"] == stopped["prefix_at_target"] if full["first_target"] is not None
                     else full["sequence"] == stopped["sequence"]))
        if stopped["first_target"] is not None and stopped["calls"] != stopped["first_target"]:
            same = False  # no PF call after the witnessed target
        if not same:
            mismatches.append(dict(pair=list(pairs[k]), reason="h, initial population or PF prefix differ"))
    if mismatches:
        decision = "blocked"
    elif attained == 0:
        decision = "inconclusive"
    else:
        decision = "allowed"
    save("stopcheck.json", dict(decision=decision, attained=attained, mismatches=mismatches, records=records))
    print(json.dumps(dict(decision=decision, attained=attained, mismatches=len(mismatches))))


def stop_allowed():
    return load("stopcheck.json")["decision"] == "allowed"


# ------------------------------------------------------------------ §7 rehearsal and power

def units_of(records):
    units = {}
    for r in records:
        t = r["task"]
        units.setdefault((t["network"], t["j"], t["s"]), {})[(t["cht"], t["arm"])] = r
    return units


def d_of(u):
    return (u[("FR", "AD-N")]["T"] - u[("FR", "FX-T")]["T"]) - (u[("SP", "AD-N")]["T"] - u[("SP", "FX-T")]["T"])


def stage_rehearsal(workers):
    require_provenance("rehearsal")
    refs = load("dev_ref.json")["references"]
    budgets = load("select_b.json")["chosen"]
    fxt = load("fxt.json")["chosen"]
    stop = stop_allowed()
    valid, _ = instances("dev")
    tasks = [task(n, j, c, a, "rehearsal", s, budgets[n], refs[f"{n}|{j}"], fixed=fxt[c] if a == "FX-T" else None,
                  stop=stop) for n, j in valid for s in REHEARSAL_SEEDS for c, a in ARMS]
    records = execute(tasks, workers)
    assert_paired(records)
    units = units_of(records)
    pools, criteria = {}, {}
    for n in NETWORKS:
        mine = {k: u for k, u in units.items() if k[0] == n}
        complete = [u for u in mine.values() if set(u) == set(ARMS) and all(r["ok"] for r in u.values())]
        medians = {f"{c}|{j}": float(np.median([u[(c, "AD-N")]["T"] for k, u in mine.items() if k[1] == j
                                                 and (c, "AD-N") in u and u[(c, "AD-N")]["ok"]] or [math.nan]))
                   for c in ("SP", "FR") for j in (0, 1)}
        attained = {f"{c}|{a}": sum(u[(c, a)]["first_target"] is not None for u in complete) for c, a in ARMS}
        d = [d_of(u) for u in complete]
        ok = (len(complete) == 2 * len(REHEARSAL_SEEDS) and all(0.3 <= m <= 0.8 for m in medians.values())
              and all(v >= 4 for v in attained.values()) and len(d) > 1 and float(np.var(d)) > 0)
        criteria[n] = dict(complete=len(complete), medians=medians, attained=attained,
                           variance=float(np.var(d)) if d else None, passed=bool(ok))
        pools[n] = d
    passed = all(c["passed"] for c in criteria.values())
    save("rehearsal.json", dict(passed=passed, criteria=criteria, pools=pools, stop=stop, records=records))
    if not passed:
        raise SystemExit(f"STOP: rehearsal criteria not met {criteria} (§7)")


def tilt(pools, theta):
    """Common lambda with (1/3) sum_i sum_u w_iu d_iu = theta, w_iu ∝ exp(lambda d_iu) within network (§7)."""
    arrays = [np.asarray(pools[n], float) for n in NETWORKS]
    low = np.mean([a.min() for a in arrays])
    high = np.mean([a.max() for a in arrays])
    if not low < theta < high:
        return None

    def weights(lam):
        out = []
        for a in arrays:
            z = lam * a
            w = np.exp(z - z.max())
            out.append(w / w.sum())
        return out

    def mean(lam):
        return float(np.mean([np.dot(w, a) for w, a in zip(weights(lam), arrays)]))
    lo, hi = -1.0, 1.0
    while mean(lo) > theta:
        lo *= 2
    while mean(hi) < theta:
        hi *= 2
    for _ in range(300):
        mid = (lo + hi) / 2
        if mean(mid) < theta:
            lo = mid
        else:
            hi = mid
    lam = (lo + hi) / 2
    w = weights(lam)
    error = abs(mean(lam) - theta)
    ess = [float(1 / np.sum(x ** 2)) for x in w]
    return dict(lam=lam, weights=[x.tolist() for x in w], error=error, ess=ess, max_weight=[float(x.max()) for x in w])


def simulate(pools, tilted, cells, n, experiments, reps, rng):
    """Positive primary conclusions (lower 95% bound > 0) over simulated experiments. A resample of the n sampled
    vectors is a multinomial draw over the pool's distinct vectors (the same distribution as resampling indices)."""
    arrays = {k: np.asarray(pools[k], float) for k in NETWORKS}
    weights = {k: np.asarray(w) for k, w in zip(NETWORKS, tilted["weights"])}
    positives = 0
    for _ in range(experiments):
        block_draws = {}
        for network, j in cells:
            counts = rng.multinomial(n, weights[network])
            boot = rng.multinomial(n, counts / n, size=reps)
            block_draws.setdefault(network, []).append(boot @ arrays[network] / n)
        draws = np.mean([np.mean(v, axis=0) for v in block_draws.values()], axis=0)
        positives += np.percentile(draws, 2.5) > 0
    return int(positives)


def wilson(k, n, z=1.959963984540054):
    p = k / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - half) / (1 + z * z / n), (centre + half) / (1 + z * z / n)


def stage_power():
    require_provenance("power")
    rehearsal = load("rehearsal.json")
    if not rehearsal["passed"]:
        raise SystemExit("STOP: rehearsal did not pass")
    pools = rehearsal["pools"]
    cells, excluded = instances("test")
    out = dict(cells=cells, excluded=excluded)
    alt, null = tilt(pools, TARGET_THETA), tilt(pools, 0.0)
    out["alternative"], out["null"] = alt, null
    for name, t in (("alternative", alt), ("null", null)):
        if t is None or t["error"] > 1e-8 or min(t["ess"]) < 10:
            save("power.json", out)
            raise SystemExit(f"STOP: {name} tilt unattainable, inaccurate or ESS < 10 (§7)")
    rng = np.random.default_rng(61023)
    screening = {}
    chosen = None
    for n in N_GRID:
        k = simulate(pools, alt, cells, n, 1000, 2000, rng)
        screening[n] = dict(positives=k, wilson=wilson(k, 1000))
        if chosen is None and wilson(k, 1000)[0] >= 0.8:
            chosen = n
            break
    out["screening"] = screening
    if chosen is None:
        save("power.json", out)
        raise SystemExit("STOP: no n <= 480 reaches power 0.8 (§7)")
    confirm = simulate(pools, alt, cells, chosen, 1000, 20000, np.random.default_rng(61024))
    false_pos = simulate(pools, null, cells, chosen, 1000, 20000, np.random.default_rng(61025))
    out.update(chosen_n=chosen, confirmation=dict(positives=confirm, wilson=wilson(confirm, 1000)),
               null_calibration=dict(positives=false_pos, wilson=wilson(false_pos, 1000)),
               passed=confirm >= 825 and false_pos <= 36)
    save("power.json", out)
    print(json.dumps({k: out[k] for k in ("chosen_n", "confirmation", "null_calibration", "passed")}, indent=1))
    if not out["passed"]:
        raise SystemExit("STOP: power confirmation or null calibration failed (§7)")


# ------------------------------------------------------------------ test references and test

def frozen_choices():
    power = load("power.json")
    if not power.get("passed"):
        raise SystemExit("STOP: power stage did not pass")
    return dict(budgets=load("select_b.json")["chosen"], fxt=load("fxt.json")["chosen"], n=power["chosen_n"],
                stop=stop_allowed())


def stage_test_ref(workers):
    current = require_provenance("test_ref")
    choices = frozen_choices()
    save("manifest_frozen.json", dict(current, choices=choices,
                                      hashes={f: sha256(path(f + ".gz")) for f in
                                              ("dev_ref.json", "select_b.json", "fxt.json", "stopcheck.json",
                                               "rehearsal.json", "power.json")}))
    valid, excluded = instances("test")
    tasks = [task(n, j, c, "AD-N", "test_ref", s, REF_BUDGET) for n, j in valid for c in REF_CHTS for s in (1, 2)]
    records = execute(tasks, workers)
    save("test_ref.json", dict(excluded=excluded, records=records, references=references(records)))


def require_frozen():
    frozen = load("manifest_frozen.json")
    if i58.normalised(frozen["choices"]) != i58.normalised(frozen_choices()):
        raise SystemExit("STOP: development choices changed after freezing")
    for f, h in frozen["hashes"].items():
        if sha256(path(f + ".gz")) != h:
            raise SystemExit(f"STOP: {f} changed after freezing")
    return frozen


def stage_test(workers):
    current = require_provenance("test")
    frozen = require_frozen()
    choices = frozen["choices"]
    refs_data = load("test_ref.json")
    refs = refs_data["references"]
    valid, excluded = instances("test")
    tasks = [task(n, j, c, a, "test", s, choices["budgets"][n], refs[f"{n}|{j}"],
                  fixed=choices["fxt"][c] if a == "FX-T" else None, stop=choices["stop"])
             for n, j in valid for s in range(1, choices["n"] + 1) for c, a in ARMS]
    assert len({t["seed"] for t in tasks}) == len(tasks) // len(ARMS)
    records = execute(tasks, workers)
    assert_paired(records)
    save("test.json", dict(excluded=excluded, choices=choices, references=refs,
                           test_ref_sha256=sha256(path("test_ref.json.gz")), manifest=current, records=records))


# ------------------------------------------------------------------ independent check (I58 checker)

_CASES = {}


def independent_check(item):
    """I58's independent checker (raw pypower data, no iteration56_orpd code) for scenario j at R = 17."""
    network, j, x = item
    if x is None:
        return dict(valid=False, reason="no witness")
    original_scenarios, original_case = i58.SCENARIOS, i58._independent_case
    import copy

    def cached(net, _):
        key = (net, j)
        if key not in _CASES:
            i58.SCENARIOS = (scenario(j),)
            _CASES[key] = original_case(net, 0)
        case, st = _CASES[key]
        return (copy.deepcopy(case), st) if case is not None else (None, None)
    try:
        i58._independent_case = cached
        return i58.independent_check(network, 0, x)
    finally:
        i58.SCENARIOS, i58._independent_case = original_scenarios, original_case


def stage_check(workers):
    from multiprocessing import Pool
    data = load("test.json")
    refs_data = load("test_ref.json")
    items, meta = [], []
    for key, value in refs_data["references"].items():  # the witness of every L*
        if value is None:
            continue
        n, j = key.split("|")
        r = next(r for r in refs_data["records"] if r.get("ok") and r["task"]["network"] == n
                 and r["task"]["j"] == int(j) and r["best_feasible"] == value)
        items.append((n, int(j), r["best_feasible_x"]))
        meta.append(dict(kind="reference", key=key, value=value))
    for r in data["records"]:
        if not r.get("ok"):
            continue
        t = r["task"]
        if r["first_target"] is not None:
            items.append((t["network"], t["j"], r["first_target_x"]))
            meta.append(dict(kind="first_target", task=t, reference=t["reference"]))
        if r["best_feasible"] is not None:
            items.append((t["network"], t["j"], r["best_feasible_x"]))
            meta.append(dict(kind="best_feasible", task=t, value=r["best_feasible"]))
    with Pool(workers) as pool:
        checks = pool.map(independent_check, items, chunksize=64)
    failures = {}
    rows = []
    for m, c in zip(meta, checks):
        ok = bool(c.get("valid") and c.get("converged") and c.get("feasible"))
        if ok and m["kind"] in ("reference", "best_feasible"):
            ok = abs(c["losses"] - m["value"]) <= 1e-6 * max(1.0, m["value"])
        if ok and m["kind"] == "first_target" and m["reference"] is not None:
            ok = c["losses"] <= m["reference"] * 1.01 + 0.01
        rows.append(dict(meta=m, ok=ok))
        if not ok:
            failures[m["kind"]] = failures.get(m["kind"], 0) + 1
    save("check.json", dict(rows=len(rows), failures=failures,
                            bound=dict(test=sha256(path("test.json.gz")), test_ref=sha256(path("test_ref.json.gz")))))
    print("checked", len(rows), "failures", failures)
    if failures or not rows:
        raise SystemExit(1)


# ------------------------------------------------------------------ §8 analysis

def bootstrap(cells, contrast, reps=20000, seed=61):
    """i56.bootstrap (cell-stratified, whole paired vectors, equal block and scenario weights) with the 95% and the
    90% percentile intervals from the same draws."""
    rng = np.random.RandomState(seed)
    blocks = {}
    for k in sorted(cells):
        values = np.array([contrast(u) for u in cells[k]], float)
        means = values[rng.randint(0, len(values), size=(reps, len(values)))].mean(axis=1)
        blocks.setdefault(k[:2], []).append(means)
    draws = np.mean([np.mean(v, axis=0) for v in blocks.values()], axis=0)
    lo95, hi95, lo90, hi90 = np.percentile(draws, [2.5, 97.5, 5, 95])
    return dict(estimate=i56.theta(cells, contrast), ci95=[float(lo95), float(hi95)], ci90=[float(lo90), float(hi90)])


def labels(b):
    return dict(supported=b["ci95"][0] > 0, opposite=b["ci95"][1] < 0,
                equivalent=-TARGET_THETA < b["ci90"][0] and b["ci90"][1] < TARGET_THETA)


def analyse():
    data = load("test.json")
    check = load("check.json")
    if check["failures"] or not check["rows"] or check["bound"] != dict(
            test=sha256(path("test.json.gz")), test_ref=sha256(path("test_ref.json.gz"))):
        raise SystemExit("STOP: independent check missing, failed or not bound to these artifacts")
    if not same_provenance(data["manifest"], build_manifest("analysis")):
        raise SystemExit("STOP: provenance differs from the test manifest")
    units = units_of(data["records"])
    planned = sorted(units)
    complete = {k: u for k, u in units.items() if set(u) == set(ARMS) and all(r["ok"] for r in u.values())}
    excluded = sorted(set(planned) - set(complete))
    cells = {}
    for (n, j, s), u in complete.items():
        cells.setdefault((n, n, j), []).append(u)
    expected = {(n, n, j) for n, j, s in planned}
    empty = sorted(expected - set(cells))
    per_cell = {f"{n}|{j}": dict(planned=sum(1 for k in planned if k[:2] == (n, j)),
                                 excluded=sum(1 for k in excluded if k[:2] == (n, j))) for (n, _, j) in expected}
    primary = None
    if not empty:
        primary = bootstrap(cells, d_of)
        primary.update(labels(primary))
    sensitivity = None
    if excluded:
        failed = dict(T=1.0, ok=False)
        restored = {}
        for (n, j, s), u in units.items():
            restored.setdefault((n, n, j), []).append({a: (u[a] if a in u and u[a]["ok"] else failed) for a in ARMS})
        sensitivity = bootstrap(restored, d_of)
        sensitivity.update(labels(sensitivity))
    descriptive = {}
    for (n, n2, j), us in cells.items():
        for c, a in ARMS:
            rs = [u[(c, a)] for u in us]
            descriptive[f"{n}|{j}|{c}|{a}"] = dict(mean_T=float(np.mean([r["T"] for r in rs])),
                                                   attained=float(np.mean([r["first_target"] is not None for r in rs])),
                                                   feasible=float(np.mean([r["best_feasible"] is not None for r in rs])))
        descriptive[f"{n}|{j}|d"] = dict(mean=float(np.mean([d_of(u) for u in us])), n=len(us))
    out = dict(planned_units=len(planned), complete_units=len(complete), excluded_units=[list(map(str, k)) for k in excluded],
               exclusion_rate=len(excluded) / len(planned) if planned else None,
               exclusion_flag=len(excluded) > 0.05 * len(planned), per_cell=per_cell,
               empty_cells=[[n, j] for n, _, j in empty], excluded_instances=data["excluded"], choices=data["choices"],
               H61=primary, sensitivity=sensitivity, descriptive=descriptive)
    save("analysis.json", out)
    print(json.dumps(dict(H61=primary, complete=len(complete), excluded=len(excluded), empty=out["empty_cells"]),
                     indent=1))


STAGES = dict(gate=stage_gate, dev_ref=stage_dev_ref, select_b=stage_select_b, fxt=stage_fxt, stopcheck=stage_stopcheck,
              rehearsal=stage_rehearsal, test_ref=stage_test_ref, test=stage_test, check=stage_check)

if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "power":
        stage_power()
    elif stage == "analyse":
        analyse()
    elif stage in STAGES:
        STAGES[stage](int(sys.argv[2]) if len(sys.argv) > 2 else 8)
    else:
        print(__doc__)
