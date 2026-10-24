"""I61: replication of the H56a interaction (adaptation x CHT) on the I58 networks with new scenarios.

Frozen protocol: research/ITERATION61_PROTOCOL.md (frozen before any I58 test result and before this code).
Reuses the I56 instrument (CHT, CHTCostFinder, StudyFactory; constraint_handling=None) and the I58 BusORPD and
independent checker; neither frozen module is modified. Stages, in order (each one a fresh process):

  python research/iteration61_replication.py gate [workers]        (OPF roster + I56 instrument bit-identity; if the
                                                                    current library fails, the same gate on 17e9ce7)
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
The gate and the freeze are create-once: another attempt needs a new experiment directory (I61_OUT). If the gate selects
the fallback library, every later stage must run with I61_LIBRARY set to it (the provenance check enforces this).
"""
import hashlib
import json
import math
import os
import random
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LIB = os.environ.get("I61_LIBRARY", REPO)  # root that contains the gadapt package used by every run
FALLBACK_COMMIT = "17e9ce7"
FALLBACK_LIB = os.path.join(REPO, ".i61_lib_" + FALLBACK_COMMIT)
for p in (REPO, HERE):  # present in sys.path, so iteration56 does not put REPO in front of LIB
    if p not in sys.path:
        sys.path.append(p)
if LIB in sys.path:
    sys.path.remove(LIB)
sys.path.insert(0, LIB)

import numpy as np  # noqa: E402

import gadapt  # noqa: E402
import iteration56_cht_study as i56  # noqa: E402
import iteration58_validation as i58  # noqa: E402

assert os.path.dirname(os.path.dirname(os.path.abspath(gadapt.__file__))) == os.path.abspath(LIB), gadapt.__file__

OUT = os.environ.get("I61_OUT", os.path.join(HERE, "results", "iteration61"))
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
    tree = {}
    for root, _, files in os.walk(os.path.join(LIB, "gadapt")):
        for f in sorted(files):
            if f.endswith(".py"):
                full = os.path.join(root, f)
                tree[os.path.relpath(full, LIB)] = sha256(full)
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.split()
    return dict(stage=stage, python=platform.python_version(), pip_freeze=freeze, gadapt_tree_sha256=tree,
                library_root=os.path.relpath(LIB, REPO),
                code_sha256={f: sha256(os.path.join(HERE, f)) for f in CODE},
                settings=dict(networks=NETWORKS, R=R, dev=DEV_SCENARIOS, test=TEST_SCENARIOS, spread=i56.SPREAD,
                              ref_budget=REF_BUDGET, b_grid=B_GRID, n_grid=N_GRID, arms=ARMS, ref_chts=REF_CHTS,
                              purpose=PURPOSE, population=i56.POPULATION_SIZE, fxt_grid=i56.FXT_GRID,
                              ga_resolved=i58.resolved_ga_settings()))


PROVENANCE = ("python", "pip_freeze", "gadapt_tree_sha256", "library_root", "code_sha256", "settings")
# artifacts each stage consumes (their producer manifests and hashes are checked before and after the stage)
INPUTS = dict(dev_ref=(), select_b=("dev_ref",), fxt=("dev_ref", "select_b"),
              stopcheck=("dev_ref", "select_b", "fxt"), rehearsal=("dev_ref", "select_b", "fxt", "stopcheck"),
              power=("rehearsal",), test_ref=("dev_ref", "select_b", "fxt", "stopcheck", "rehearsal", "power"),
              test=("test_ref",), check=("dev_ref", "select_b", "fxt", "stopcheck", "rehearsal", "test_ref", "test"),
              analysis=("test_ref", "test", "check"))


def same_provenance(a, b):
    return all(i58.normalised(a[f]) == i58.normalised(b[f]) for f in PROVENANCE)


def artifact(stage):
    return path(f"{stage}.json.gz")


def verify_gate():
    gate, manifest = load("gate.json"), load("manifest_gate.json")
    selected = path(f"gate_{gate.get('selected')}.json.gz")
    if not (gate["passed"] and manifest["gate_sha256"] == sha256(artifact("gate"))
            and manifest["roster_sha256"] == sha256(artifact("roster")) and os.path.exists(selected)
            and gate["result_sha256"] == sha256(selected)
            and all(sha256(path(f"gate_{k}.json.gz")) == h for k, h in gate["attempts_sha256"].items())):
        raise SystemExit("STOP: the instrument gate did not pass or its records changed")
    return manifest


def verify_chain(stage, current):
    """A consumed artifact: produced by this build, unchanged since (output hash), and so are its own inputs."""
    m = load(f"manifest_{stage}.json")
    if not same_provenance(m, current):
        raise SystemExit(f"STOP: {stage} was produced by a different build")
    if m.get("output_sha256") != sha256(artifact(stage)):
        raise SystemExit(f"STOP: {stage} is not the artifact its manifest published")
    for producer, h in m["inputs_sha256"].items():
        if load(f"manifest_{producer}.json")["output_sha256"] != h:
            raise SystemExit(f"STOP: {stage} consumed a {producer} artifact that is no longer the published one")
        verify_chain(producer, current)


def require_provenance(stage):
    """Create-once per stage; runs on exactly the gated build; consumes only published artifacts of that build."""
    if os.path.exists(path(f"manifest_{stage}.json.gz")):
        raise SystemExit(f"STOP: {stage} already completed in this experiment directory (create-once)")
    gate = verify_gate()
    current = build_manifest(stage)
    if not same_provenance(gate, current):
        raise SystemExit("STOP: code, library, environment or settings differ from the gated build")
    inputs = {}
    for producer in INPUTS[stage]:
        verify_chain(producer, current)
        inputs[producer] = sha256(artifact(producer))
    if stage in ("test", "check", "analysis"):
        frozen = load("manifest_frozen.json")
        if not same_provenance(frozen, current):
            raise SystemExit("STOP: the build differs from the frozen manifest")
    current["inputs_sha256"] = inputs
    current["gate_sha256"], current["roster_sha256"] = gate["gate_sha256"], gate["roster_sha256"]
    return current


def finish(stage, before):
    """Before publishing: the build, the gate records and every consumed artifact are unchanged."""
    after = build_manifest(stage + "-after")
    if not same_provenance(before, after):
        raise SystemExit(f"STOP: the build changed during {stage}")
    verify_gate()
    for producer, h in before["inputs_sha256"].items():
        if sha256(artifact(producer)) != h:
            raise SystemExit(f"STOP: {producer} changed during {stage}")


def publish(stage, before, data):
    """Output first, then its manifest with the output hash (a manifest exists only for a completed stage)."""
    finish(stage, before)
    save(f"{stage}.json", data)
    save(f"manifest_{stage}.json", dict(before, output_sha256=sha256(artifact(stage))))


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


def preflight():
    """§2: OPF eligibility of ALL 15 scenarios before development; both development scenarios and >= 1 test scenario
    of every network are required. The roster is frozen (create-once, inside the gate) and reused by every stage."""
    from iteration56_orpd import ScenarioError
    roster = dict(dev=[], test=[], excluded=[])
    for n in NETWORKS:
        for j in range(5):
            try:
                make_problem(n, j)
                roster["dev" if j < 2 else "test"].append([n, j])
            except ScenarioError:
                roster["excluded"].append([n, j])
    save("roster.json", roster)
    if any(j < 2 for _, j in roster["excluded"]):
        raise SystemExit(f"STOP: a development scenario OPF failed {roster['excluded']} (both are required, §2)")
    if {n for n, _ in roster["test"]} != set(NETWORKS):
        raise SystemExit(f"STOP: a network has no test scenario with a successful OPF {roster['excluded']} (§2)")
    return roster


def instances(kind):
    """(network, j) from the frozen roster (§2)."""
    roster = load("roster.json")
    return [tuple(x) for x in roster[kind]], [x for x in roster["excluded"] if (x[1] < 2) == (kind == "dev")]


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


def assert_paired(records):
    """Every run with the same (network, scenario, seed) — arms, CHTs, FX-T configurations, stopped/full — starts from
    the same generated initial population (§9)."""
    groups = {}
    for r in records:
        if r.get("ok"):
            t = r["task"]
            groups.setdefault((t["network"], t["j"], t["seed"]), []).append(r["generated"])
    for key, values in groups.items():
        if any(v != values[0] or len(v) != i56.POPULATION_SIZE for v in values):
            raise SystemExit(f"STOP: generated initial populations differ within {key}")


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


def bits_equal(a, b):
    """Type-aware recursive comparison; floats by their binary representation (§3: numerical bits)."""
    if type(a) is not type(b):
        return False
    if isinstance(a, float):
        return struct.pack("<d", a) == struct.pack("<d", b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(bits_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(bits_equal(x, y) for x, y in zip(a, b))
    return a == b


def gate_run(label, workers):
    """§3 on the library at LIB; an execution exception is a failed gate (recorded), not a crash."""
    import traceback
    try:
        return _gate_run(label, workers)
    except Exception:
        save(f"gate_{label}.json", dict(label=label, library_root=os.path.relpath(LIB, REPO), passed=False,
                                        error=traceback.format_exc()[-3000:], manifest=build_manifest(f"gate-{label}")))
        return False


def _gate_run(label, workers):
    """54 archived I56 runs (fresh processes), run_plain for SP/AD-N, I56 tests."""
    archived = gate_tasks()
    keys = sorted(archived)
    rerun = i56.run_pool([dict(archived[k]["task"]) for k in keys], workers)
    mismatches = []
    for k, new in zip(keys, rerun):
        old, new = archived[k], i58.normalised(new)
        for f in GATE_FIELDS:
            if (f in old or f in new) and not bits_equal(old.get(f), new.get(f)):
                mismatches.append(dict(task=list(map(str, k)), field=f))
    plain_tasks = [dict(archived[k]["task"]) for k in keys if k[2:] == ("SP", "AD-N")]
    plain = i56.run_pool(plain_tasks, workers, i56.run_plain)
    for t, p in zip(plain_tasks, plain):
        k = (t["network"], t["resolution"], "SP", "AD-N")
        if p["sequence"] != archived[k]["sequence"] or p["calls"] != archived[k]["calls"]:
            mismatches.append(dict(task=list(map(str, k)), field="run_plain"))
    test_file = os.path.join(HERE, "test_iteration56_cht_study.py")
    runner = ("import sys; sys.path[:0] = [%r, %r, %r]; import pytest; "
              "sys.exit(pytest.main(['-q', '-p', 'no:cacheprovider', %r]))" % (LIB, REPO, HERE, test_file))
    tests = subprocess.run([sys.executable, "-c", runner], capture_output=True, text=True,
                           env=dict(os.environ, I61_LIBRARY=LIB))
    passed = not mismatches and tests.returncode == 0
    save(f"gate_{label}.json", dict(label=label, library_root=os.path.relpath(LIB, REPO), passed=passed,
                                    runs=len(rerun), plain=len(plain), mismatches=mismatches,
                                    archive_sha256=sha256(i56.path("test.json.gz")),
                                    i56_tests_sha256=sha256(test_file), i56_tests_stdout=tests.stdout,
                                    i56_tests_stderr=tests.stderr, i56_tests_returncode=tests.returncode,
                                    manifest=build_manifest(f"gate-{label}")))
    print(json.dumps(dict(label=label, passed=passed, runs=len(rerun), mismatches=len(mismatches)), indent=1))
    return passed


def select_gate(label):
    """Writes the selected gate record and the gate manifest (hash-bound to the record and the roster)."""
    attempts = {k: sha256(path(f"gate_{k}.json.gz")) for k in ("current", "fallback")
                if os.path.exists(path(f"gate_{k}.json.gz"))}
    selected = load(f"gate_{label}.json")
    if not (selected["passed"] and selected["archive_sha256"] == sha256(i56.path("test.json.gz"))
            and selected["i56_tests_sha256"] == sha256(os.path.join(HERE, "test_iteration56_cht_study.py"))):
        raise SystemExit("STOP: the selected gate record is inconsistent")
    save("gate.json", dict(passed=True, selected=label, library_root=os.path.relpath(LIB, REPO),
                           result_sha256=attempts[label], attempts_sha256=attempts))
    save("manifest_gate.json", dict(build_manifest("gate"), gate_sha256=sha256(artifact("gate")),
                                    roster_sha256=sha256(artifact("roster"))))


def stage_gate(workers):
    """Create-once. The current library first; if it is not bit-identical, the same gate on FALLBACK_COMMIT in a
    separate tree (both outcomes kept). Later stages must use the selected library (provenance enforces it)."""
    if any(os.path.exists(path(f)) for f in ("gate.json.gz", "gate_current.json.gz", "roster.json.gz")):
        raise SystemExit("STOP: the gate already ran in this experiment directory (create-once; use a new I61_OUT)")
    if os.path.abspath(LIB) != os.path.abspath(REPO):
        raise SystemExit("STOP: start the gate with the repository library (the fallback is selected automatically)")
    preflight()
    if gate_run("current", workers):
        select_gate("current")
        return
    import shutil
    if os.path.isdir(FALLBACK_LIB):  # never reuse an existing tree: always exactly FALLBACK_COMMIT
        shutil.rmtree(FALLBACK_LIB)
    os.makedirs(FALLBACK_LIB)
    archive = subprocess.run(["git", "-C", REPO, "archive", FALLBACK_COMMIT, "gadapt"], capture_output=True,
                             check=True).stdout
    subprocess.run(["tar", "-x", "-C", FALLBACK_LIB], input=archive, check=True)
    fallback = subprocess.run([sys.executable, os.path.abspath(__file__), "gate_fallback", str(workers)],
                              env=dict(os.environ, I61_LIBRARY=FALLBACK_LIB))
    if fallback.returncode != 0 or not os.path.exists(path("gate.json.gz")):
        raise SystemExit("STOP: the I56 instrument is bit-identical neither on the current library nor on "
                         f"{FALLBACK_COMMIT} (§3)")
    print(f"gate: FALLBACK selected — run every later stage with I61_LIBRARY={FALLBACK_LIB}")


def stage_gate_fallback(workers):
    if os.path.abspath(LIB) != os.path.abspath(FALLBACK_LIB) or os.path.exists(path("gate.json.gz")) \
            or os.path.exists(path("gate_fallback.json.gz")):
        raise SystemExit("STOP: the fallback gate runs only from stage gate, once")
    if gate_run("fallback", workers):
        select_gate("fallback")
    else:
        raise SystemExit(1)


# ------------------------------------------------------------------ §4 development references, §5 budget

def stage_dev_ref(workers):
    before = require_provenance("dev_ref")
    valid, _ = instances("dev")
    tasks = [task(n, j, c, "AD-N", "dev_ref", 1, REF_BUDGET) for n, j in valid for c in REF_CHTS]
    records = execute(tasks, workers)
    assert_paired(records)
    publish("dev_ref", before, dict(records=records, references=references(records)))


def t_of(record, budget):
    h = record["first_target"]
    return min(h / budget, 1.0) if h is not None else 1.0


def stage_select_b(workers):
    before = require_provenance("select_b")
    refs = load("dev_ref.json")["references"]
    valid, _ = instances("dev")
    tasks = [task(n, j, c, "AD-N", "select_b", s, max(B_GRID), refs[f"{n}|{j}"])
             for n, j in valid for c in ("SP", "FR") for s in SELECT_SEEDS]
    records = execute(tasks, workers)
    assert_paired(records)
    if not all(r["ok"] for r in records):
        publish("select_b", before, dict(chosen={}, medians={}, records=records, failed=True))
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
    publish("select_b", before, dict(chosen=chosen, medians=table, records=records))
    if set(chosen) != set(NETWORKS):
        raise SystemExit(f"STOP: no admissible budget for {sorted(set(NETWORKS) - set(chosen))} (§5)")


# ------------------------------------------------------------------ §6 FX-T

def stage_fxt(workers):
    before = require_provenance("fxt")
    refs = load("dev_ref.json")["references"]
    budgets = load("select_b.json")["chosen"]
    valid, _ = instances("dev")
    tasks = [task(n, j, c, "FX-T", "fxt", s, budgets[n], refs[f"{n}|{j}"], fixed=g)
             for n, j in valid for c in ("SP", "FR") for g in i56.FXT_GRID for s in FXT_SEEDS]
    records = execute(tasks, workers)
    assert_paired(records)
    chosen = {}
    for c in ("SP", "FR"):
        groups = [[r["T"] for r in records if r["ok"] and r["task"]["cht"] == c and r["task"]["fixed"] == list(g)]
                  for g in i56.FXT_GRID]
        if any(len(g) != len(valid) * len(FXT_SEEDS) for g in groups):
            publish("fxt", before, dict(chosen=None, records=records))
            raise SystemExit(f"STOP: FX-T calibration incomplete for {c} (§6)")
        chosen[c] = list(i56.FXT_GRID[int(np.argmin([np.mean(g) for g in groups]))])  # balanced: equal weights
    publish("fxt", before, dict(chosen=chosen, records=records))


# ------------------------------------------------------------------ §10 stop-at-target validation

def stage_stopcheck(workers):
    before = require_provenance("stopcheck")
    refs = load("dev_ref.json")["references"]
    budgets = load("select_b.json")["chosen"]
    fxt = load("fxt.json")["chosen"]
    valid, _ = instances("dev")
    pairs = [(n, j, c, a) for n, j in valid for c, a in ARMS]
    tasks = [task(n, j, c, a, "stopcheck", 1, budgets[n], refs[f"{n}|{j}"], fixed=fxt[c] if a == "FX-T" else None,
                  stop=stop) for n, j, c, a in pairs for stop in (False, True)]
    records = execute(tasks, workers)
    assert_paired(records)
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
    publish("stopcheck", before, dict(decision=decision, attained=attained, mismatches=mismatches, records=records))
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
    before = require_provenance("rehearsal")
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
    pools, pool_attained, criteria = {}, {}, {}
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
        pool_attained[n] = {f"{c}|{a}": [u[(c, a)]["first_target"] is not None for u in complete] for c, a in ARMS}
    passed = all(c["passed"] for c in criteria.values())
    publish("rehearsal", before, dict(passed=passed, criteria=criteria, pools=pools, pool_attained=pool_attained,
                                      stop=stop, records=records))
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
    before = require_provenance("power")
    rehearsal = load("rehearsal.json")
    if not rehearsal["passed"]:
        raise SystemExit("STOP: rehearsal did not pass")
    pools = rehearsal["pools"]
    cells, excluded = instances("test")
    out = dict(cells=cells, excluded=excluded)
    alt, null = tilt(pools, TARGET_THETA), tilt(pools, 0.0)
    for t in (alt, null):  # §7 diagnostics: weighted branch-attainment rates
        if t is not None:
            t["weighted_attainment"] = {n: {arm: float(np.dot(w, flags)) for arm, flags in
                                            rehearsal["pool_attained"][n].items()}
                                        for n, w in zip(NETWORKS, t["weights"])}
    out["alternative"], out["null"] = alt, null
    for name, t in (("alternative", alt), ("null", null)):
        if t is None or t["error"] > 1e-8 or min(t["ess"]) < 10:
            publish("power", before, out)
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
        publish("power", before, out)
        raise SystemExit("STOP: no n <= 480 reaches power 0.8 (§7)")
    confirm = simulate(pools, alt, cells, chosen, 1000, 20000, np.random.default_rng(61024))
    false_pos = simulate(pools, null, cells, chosen, 1000, 20000, np.random.default_rng(61025))
    out.update(chosen_n=chosen, confirmation=dict(positives=confirm, wilson=wilson(confirm, 1000)),
               null_calibration=dict(positives=false_pos, wilson=wilson(false_pos, 1000)),
               passed=confirm >= 825 and false_pos <= 36)
    publish("power", before, out)
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
    if os.path.exists(path("manifest_frozen.json.gz")):
        raise SystemExit("STOP: the choices are already frozen (create-once; another freeze needs a new I61_OUT)")
    choices = frozen_choices()
    save("manifest_frozen.json", dict(current, choices=choices,
                                      hashes={f: sha256(path(f + ".gz")) for f in
                                              ("dev_ref.json", "select_b.json", "fxt.json", "stopcheck.json",
                                               "rehearsal.json", "power.json")}))
    valid, excluded = instances("test")
    tasks = [task(n, j, c, "AD-N", "test_ref", s, REF_BUDGET) for n, j in valid for c in REF_CHTS for s in (1, 2)]
    records = execute(tasks, workers)
    assert_paired(records)
    publish("test_ref", current, dict(excluded=excluded, records=records, references=references(records)))


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
    publish("test", current, dict(excluded=excluded, choices=choices, references=refs,
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


def require_consumed_references(data):
    """The references the test consumed are the current reference artifact, and every task carries them (§4, §10)."""
    refs = load("test_ref.json")["references"]
    if data["test_ref_sha256"] != sha256(artifact("test_ref")) or data["references"] != refs:
        raise SystemExit("STOP: the test consumed other references than the current test_ref artifact")
    for r in data["records"]:
        t = r["task"]
        if t["reference"] != refs[f"{t['network']}|{t['j']}"]:
            raise SystemExit(f"STOP: a test task carries a different reference {t}")
    return refs


def witnesses(source, records, references=None):
    """Every required witness (§10): the solution of each L*, each first target and each reported best feasible."""
    items = []
    if references is not None:
        for key, value in sorted(references.items()):
            if value is None:
                continue
            n, j = key.split("|")
            r = next(r for r in records if r.get("ok") and r["task"]["network"] == n and r["task"]["j"] == int(j)
                     and r["best_feasible"] == value)
            items.append(((n, int(j), r["best_feasible_x"]), dict(source=source, kind="reference", key=key, value=value)))
    for r in records:
        if not r.get("ok"):
            continue
        t = r["task"]
        if r["first_target"] is not None:
            items.append(((t["network"], t["j"], r["first_target_x"]),
                          dict(source=source, kind="first_target", task=t, reference=t["reference"])))
        if r["best_feasible"] is not None:
            items.append(((t["network"], t["j"], r["best_feasible_x"]),
                          dict(source=source, kind="best_feasible", task=t, value=r["best_feasible"])))
    return items


def stage_check(workers):
    from multiprocessing import Pool
    before = require_provenance("check")
    data = load("test.json")
    require_consumed_references(data)
    dev, test_ref = load("dev_ref.json"), load("test_ref.json")
    items = (witnesses("dev_ref", dev["records"], dev["references"])
             + witnesses("select_b", load("select_b.json")["records"])
             + witnesses("fxt", load("fxt.json")["records"])
             + witnesses("stopcheck", load("stopcheck.json")["records"])
             + witnesses("rehearsal", load("rehearsal.json")["records"])
             + witnesses("test_ref", test_ref["records"], test_ref["references"])
             + witnesses("test", data["records"]))
    with Pool(workers) as pool:
        checks = pool.map(independent_check, [x for x, _ in items], chunksize=64)
    failures = {}
    for (_, m), c in zip(items, checks):
        ok = bool(c.get("valid") and c.get("converged") and c.get("feasible"))
        if ok and m["kind"] in ("reference", "best_feasible"):
            ok = abs(c["losses"] - m["value"]) <= 1e-6 * max(1.0, m["value"])
        if ok and m["kind"] == "first_target" and m["reference"] is not None:
            ok = c["losses"] <= m["reference"] * 1.01 + 0.01
        if not ok:
            label = f"{m['source']}|{m['kind']}"
            failures[label] = failures.get(label, 0) + 1
    # an empty expected witness set is legitimate (feasibility targets never attained): rows may be 0
    publish("check", before, dict(expected=len(items), rows=len(checks), failures=failures,
                                  bound={k: sha256(artifact(k)) for k in INPUTS["check"]}))
    print("checked", len(checks), "of", len(items), "failures", failures)
    if failures or len(checks) != len(items):
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
    before = require_provenance("analysis")
    data = load("test.json")
    check = load("check.json")
    if check["failures"] or check["rows"] != check["expected"] or check["bound"] != {
            k: sha256(artifact(k)) for k in INPUTS["check"]}:
        raise SystemExit("STOP: independent check missing, failed or not bound to these artifacts")
    if not same_provenance(data["manifest"], build_manifest("analysis")):
        raise SystemExit("STOP: provenance differs from the test manifest")
    require_consumed_references(data)
    frozen = require_frozen()
    roster, _ = instances("test")
    planned = [(n, j, s) for n, j in roster for s in range(1, frozen["choices"]["n"] + 1)]  # §10: roster x n
    units = {k: {} for k in planned}
    for r in data["records"]:
        t = r["task"]
        key, arm = (t["network"], t["j"], t["s"]), (t["cht"], t["arm"])
        if key not in units or arm not in ARMS or arm in units[key]:
            raise SystemExit(f"STOP: unplanned unit, unknown arm or duplicate record {key} {arm}")
        units[key][arm] = r
    complete = {k: u for k, u in units.items() if set(u) == set(ARMS) and all(r["ok"] for r in u.values())}
    excluded = sorted(set(planned) - set(complete))
    cells = {}
    for (n, j, s), u in complete.items():
        cells.setdefault((n, n, j), []).append(u)
    expected = {(n, n, j) for n, j in roster}
    empty = sorted(expected - set(cells))
    per_cell = {}
    for n, j in roster:
        p = sum(1 for k in planned if k[:2] == (n, j))
        e = sum(1 for k in excluded if k[:2] == (n, j))
        per_cell[f"{n}|{j}"] = dict(planned=p, excluded=e, rate=e / p)
    primary = None
    if not empty:
        primary = bootstrap(cells, d_of)
        primary.update(labels(primary))
    sensitivity = None
    if excluded:
        failed = dict(T=1.0, ok=False)
        restored = {}
        for (n, j, s) in planned:
            u = units[(n, j, s)]
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
    out = dict(planned_units=len(planned), complete_units=len(complete),
               excluded_units=[list(map(str, k)) for k in excluded], exclusion_rate=len(excluded) / len(planned),
               exclusion_flag=len(excluded) > 0.05 * len(planned), per_cell=per_cell,
               empty_cells=[[n, j] for n, _, j in empty], excluded_instances=data["excluded"], choices=data["choices"],
               H61=primary, sensitivity=sensitivity, sensitivity_descriptive_only=True, descriptive=descriptive)
    publish("analysis", before, out)
    print(json.dumps(dict(H61=primary, complete=len(complete), excluded=len(excluded), empty=out["empty_cells"]),
                     indent=1))


STAGES = dict(gate=stage_gate, gate_fallback=stage_gate_fallback, dev_ref=stage_dev_ref, select_b=stage_select_b, fxt=stage_fxt, stopcheck=stage_stopcheck,
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
