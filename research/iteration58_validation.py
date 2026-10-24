"""I58: validation of the integrated GAdapt constraint_handling ("feasibility_rules") on fresh networks.

Frozen protocol: research/ITERATION58_PROTOCOL.md (frozen before any I56 test result). Needs the library with patch v4
(research/patches/constraint_api.patch). Reuses the I56 evaluator/targets/bootstrap and the I57 external adapters.

  python research/iteration58_validation.py refs [workers]
  python research/iteration58_validation.py test [workers]
  python research/iteration58_validation.py analyse
  python research/iteration58_validation.py check        (independent re-check of returned / target solutions)

Before the patch is applied, G1 can only be tried from a copy of the repository that has it (with research/ inside).
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)  # the library is the repository's gadapt/ (patch v4 applied before running)
for p in (REPO, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402

import iteration56_cht_study as i56  # noqa: E402
import iteration57_external as i57  # noqa: E402
from iteration56_orpd import ORPD  # noqa: E402

NETWORKS = ("case30", "case39", "case24_ieee_rts", "case300")
PRIMARY = ("case30", "case39", "case24_ieee_rts")
SCENARIOS = ((0.95, 301), (1.00, 302), (1.05, 303))
RESOLUTION = 17
TEST_BUDGET, PRIMARY_BUDGET, REF_BUDGET = 10000, 3000, 30000
METHODS = ("G0", "G1", "CMAwM", "DE", "Random")


def seed_of(p, network, j, s):
    return 10 ** 7 * p + 10 ** 5 * NETWORKS.index(network) + 10 ** 3 * RESOLUTION + 100 * j + s


class BusORPD:
    """The unchanged I56 instrument (delegate) with ONE voltage set-point per generator bus, applied to every
    generator on that bus (composition; the frozen iteration56_orpd.py is not touched)."""

    def __init__(self, network, resolution, load_factor, spread, scenario_seed):
        from pypower.idx_gen import GEN_BUS
        self.delegate = ORPD(network, resolution, load_factor, spread, scenario_seed)
        d = self.delegate
        self.resolution, self.opf_losses, self.base = d.resolution, d.opf_losses, d.base
        self.gen_rows, self.tap_rows, self.shunt_rows = d.gen_rows, d.tap_rows, d.shunt_rows
        buses = []
        for g in d.gen_rows:
            b = int(d.base["gen"][g, GEN_BUS])
            if b not in buses:
                buses.append(b)
        self.bus_groups = [[g for g in d.gen_rows if int(d.base["gen"][g, GEN_BUS]) == b] for b in buses]
        self.first = [d.gen_rows.index(group[0]) for group in self.bus_groups]
        self.expand = [next(k for k, group in enumerate(self.bus_groups) if g in group) for g in d.gen_rows]
        n_g = len(d.gen_rows)
        keep = self.first + list(range(n_g, d.d))
        self.lo, self.hi = d.lo[keep], d.hi[keep]
        self.d = len(keep)
        self.step = (self.hi - self.lo) / (self.resolution - 1)

    def snap(self, x):
        k = np.clip(np.rint((np.asarray(x, float) - self.lo) / self.step), 0, self.resolution - 1)
        return self.lo + k * self.step

    def evaluate(self, x):
        x = self.snap(x)
        n_b = len(self.bus_groups)
        return self.delegate.evaluate(np.concatenate([x[:n_b][self.expand], x[n_b:]]))


class WitnessEvaluator(i56.Evaluator):
    """I56 evaluator that also keeps the genotype and call index of the first target attainment."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_target_x = None

    def _call(self, values):
        before = self.first_target
        result = super()._call(values)
        if before is None and self.first_target is not None:
            self.first_target_x = list(values)
        return result


def make_problem(network, j):
    load_factor, scenario_seed = SCENARIOS[j]
    return BusORPD(network, RESOLUTION, load_factor, i56.SPREAD, scenario_seed)


def gadapt_run(problem, evaluator, method, seed):
    from gadapt.ga import GA
    random.seed(seed)
    np.random.seed(seed)
    # after the budget the I56 evaluator returns 0.0 without evaluating; such candidates must never be reported
    if method == "G0":
        def cost(values):
            return 1e300 if evaluator.done else evaluator(values)
        kwargs = {}
    else:
        def cost(values):
            if evaluator.done:
                return 0.0, 1e150  # the largest admissible violation: never better than an evaluated solution
            evaluator(values)
            raw = evaluator.cache[tuple(values)]
            return raw.f, raw.V
        kwargs = dict(constraint_handling="feasibility_rules")
    ga = GA(cost_function=cost, probe_cost_function=False, exit_check="generations", number_of_generations=10 ** 9,
            exit_function=lambda *a, **k: evaluator.done, timeout=10 ** 6, **kwargs)
    for lo, hi, step in zip(problem.lo, problem.hi, problem.step):
        ga.add(float(lo), float(hi), float(step))
    result = ga.execute()
    returned = None
    if result.success and result.result_values:
        returned = dict(x=[result.result_values[i] for i in sorted(result.result_values)],
                        min_cost=result.min_cost,
                        best_objective=None if math.isnan(result.best_objective) else result.best_objective,
                        best_violation=None if math.isnan(result.best_violation) else result.best_violation,
                        feasible=result.feasible)
    return bool(result.success), returned


def run(task):
    import traceback
    try:
        return _run(task)
    except Exception:
        return dict(task=task, ok=False, error=traceback.format_exc()[-2000:])


def _run(task):
    problem = make_problem(task["network"], task["j"])
    target = i56.make_target(task.get("reference"))
    evaluator = WitnessEvaluator(problem, task["budget"], target)
    success, returned = True, None
    if task["method"] in ("G0", "G1"):
        success, returned = gadapt_run(problem, evaluator, task["method"], task["seed"])
    else:
        scalar = i57.Scalar(problem, evaluator, "FR" if task["method"] != "Random" else "-")
        dict(CMAwM=i57.run_cmawm, DE=i57.run_de, Random=i57.run_random)[task["method"]](problem, scalar, task["seed"])
    complete = evaluator.calls == task["budget"]
    first = evaluator.first_target
    best_x = None
    if math.isfinite(evaluator.best_feasible):
        best_x = [list(k) for k, r in evaluator.cache.items() if r.feasible and r.f == evaluator.best_feasible][:1]
    return dict(task=task, ok=complete and success and evaluator.errors == 0, calls=evaluator.calls,
                errors=evaluator.errors, first_target=first, first_feasible=evaluator.first_feasible,
                T3000=min(first / PRIMARY_BUDGET, 1.0) if first is not None else 1.0,
                T10000=min(first / TEST_BUDGET, 1.0) if first is not None else 1.0,
                best_feasible=evaluator.best_feasible if math.isfinite(evaluator.best_feasible) else None,
                best_feasible_x=best_x[0] if best_x else None, returned=returned,
                first_target_x=evaluator.first_target_x,
                initial=[list(k) for k in evaluator.initial], sequence=evaluator.sequence.hexdigest())


def instances():
    """(network, j) with a successful OPF; exclusions reported (protocol: before any optimization run)."""
    from iteration56_orpd import ScenarioError
    valid, excluded = [], []
    for n in NETWORKS:
        for j in range(len(SCENARIOS)):
            try:
                make_problem(n, j)
                valid.append((n, j))
            except ScenarioError:
                excluded.append([n, j])
    return valid, excluded


def assert_paired_initial(records):
    """G0/G1 of the same (network, scenario, seed) must start from the same 32 genotypes (collection time)."""
    pairs = {}
    for r in records:
        t = r["task"]
        if t["method"] in ("G0", "G1") and r.get("ok"):
            pairs.setdefault((t["network"], t["j"], t["seed"]), {})[t["method"]] = r["initial"]
    for key, p in pairs.items():
        if len(p) == 2 and (p["G0"] != p["G1"] or len(p["G0"]) != i56.POPULATION_SIZE):
            raise SystemExit(f"STOP: G0/G1 initial populations differ for {key}")


def build_manifest(stage):
    import platform
    import subprocess
    library = os.path.join(REPO, "gadapt")
    tree = {}
    for root, _, files in os.walk(library):
        for f in sorted(files):
            if f.endswith(".py"):
                full = os.path.join(root, f)
                tree[os.path.relpath(full, REPO)] = i57.sha256(full)
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.split()
    patch = os.path.join(HERE, "patches", "constraint_api.patch")
    return dict(stage=stage, python=platform.python_version(), pip_freeze=freeze, gadapt_tree_sha256=tree,
                patch_sha256=i57.sha256(patch),
                code_sha256={f: i57.sha256(os.path.join(HERE, f)) for f in
                             ("iteration58_validation.py", "iteration57_external.py", "iteration56_cht_study.py",
                              "iteration56_orpd.py", "ITERATION58_PROTOCOL.md")},
                settings=dict(population_size=i56.POPULATION_SIZE, probe_cost_function=False, immigration_number=0,
                              exit_check="generations", number_of_generations=10 ** 9, timeout=10 ** 6,
                              g0="scalar f + 1000 V; post-budget 1e300", g1="constraint_handling=feasibility_rules; "
                              "post-budget (0, 1e150)", sp_weight=i56.SP_WEIGHT, resolution=RESOLUTION, spread=i56.SPREAD,
                              scenarios=SCENARIOS, budgets=[PRIMARY_BUDGET, TEST_BUDGET, REF_BUDGET], tol=i56.TOL,
                              v_fail=i56.V_FAIL, external="I57 frozen settings (CMAwM, SciPy DE best1bin, Random)",
                              seeds="10^7 p + 10^5 i + 10^3 R + 100 j + s; test p=6 s=1..15; refs p=7 s=1,2",
                              bootstrap=dict(reps=20000, seed=58)))


def pool_run(tasks, workers):
    from multiprocessing import Pool
    with Pool(workers, maxtasksperchild=1) as pool:
        records = list(pool.imap(run, tasks))
    for i, r in enumerate(records):
        if not r["ok"]:
            with Pool(1, maxtasksperchild=1) as pool:
                again = pool.apply(run, (tasks[i],))
            again["rerun"], again["first_attempt"] = True, {k: v for k, v in r.items() if k != "initial"}
            records[i] = again
    assert_paired_initial(records)
    return records


def stage_refs(workers):
    i56.save("i58_refs_manifest.json", build_manifest("refs"))
    valid, excluded = instances()
    tasks = [dict(network=n, j=j, method=m, seed=seed_of(7, n, j, s), budget=REF_BUDGET, reference=None)
             for n, j in valid for m in METHODS for s in (1, 2)]
    i56.save("i58_refs.json", dict(excluded=excluded, records=pool_run(tasks, workers)))


def references():
    best = {}
    for r in i56.load("i58_refs.json")["records"]:
        key = f"{r['task']['network']}|{r['task']['j']}"
        value = r["best_feasible"] if r["ok"] and r["best_feasible"] is not None else math.inf
        best[key] = min(best.get(key, math.inf), value)
    return {k: (v if math.isfinite(v) else None) for k, v in best.items()}


def stage_test(workers):
    refs = references()
    pre = dict(build_manifest("test"), refs_sha256=i57.sha256(i56.path("i58_refs.json.gz")), references=refs)
    refs_build = i56.load("i58_refs_manifest.json")
    for field in ("gadapt_tree_sha256", "patch_sha256", "code_sha256", "pip_freeze", "python", "settings"):
        if refs_build[field] != pre[field]:
            raise SystemExit(f"STOP: references and test differ in {field}")
    i56.save("i58_manifest.json", pre)
    valid, excluded = instances()
    tasks = [dict(network=n, j=j, method=m, seed=seed_of(6, n, j, s), budget=TEST_BUDGET, reference=refs[f"{n}|{j}"])
             for n, j in valid for s in range(1, 16) for m in METHODS]
    records = pool_run(tasks, workers)
    if i57.sha256(i56.path("i58_refs.json.gz")) != pre["refs_sha256"]:
        raise SystemExit("STOP: references changed during the test")
    post = build_manifest("test-after")
    for field in ("gadapt_tree_sha256", "patch_sha256", "code_sha256", "pip_freeze", "python"):
        if post[field] != pre[field]:
            raise SystemExit(f"STOP: {field} changed during the test")
    i56.save("i58_test.json", dict(excluded=excluded, references=refs, records=records))


def analyse():
    data = i56.load("i58_test.json")
    check = i56.load("i58_check.json")
    if check["failures"] or not check["checks"] or check["bound"] != dict(
            refs=i57.sha256(i56.path("i58_refs.json.gz")), test=i57.sha256(i56.path("i58_test.json.gz"))):
        raise SystemExit("STOP: independent check missing, failed, or not bound to these artifacts")
    units = {}
    for r in data["records"]:
        t = r["task"]
        units.setdefault((t["network"], t["j"], t["seed"]), {})[t["method"]] = r
    for u in units.values():  # G0 and G1 must start from the same initial population
        if "G0" in u and "G1" in u and u["G0"].get("ok") and u["G1"].get("ok"):
            assert u["G0"]["initial"] == u["G1"]["initial"], "G0/G1 initial populations differ"
    expected_cells = {(n, j) for (n, j, s) in units if n in PRIMARY}
    complete = {k: u for k, u in units.items() if k[0] in PRIMARY and all(u.get(m, {}).get("ok") for m in METHODS)}
    excluded = sorted(set(k for k in units if k[0] in PRIMARY) - set(complete))
    cells = {}
    for (n, j, s), u in complete.items():
        cells.setdefault((n, j), []).append(u)
    empty = sorted(expected_cells - set(cells))
    networks_left = {n for n, j in cells}

    def theta(cell_map, key="T3000"):
        # equal weight per network and per remaining scenario: bootstrap() averages cells within a "block" k[:2];
        # here the block is the network, so cells are re-keyed (network, network, j)
        remapped = {(n, n, j): v for (n, j), v in cell_map.items()}
        return i56.bootstrap(remapped, lambda u: u["G1"][key] - u["G0"][key], seed=58)

    primary = None
    if not empty and networks_left == set(PRIMARY):
        b = theta(cells)
        primary = dict(estimate=b["estimate"], ci=b["ci"], supported=b["ci"][1] < 0)
    sensitivity = None
    if empty or len(excluded) > 0.05 * len([k for k in units if k[0] in PRIMARY]):
        failed = dict(T3000=1.0, T10000=1.0, ok=False)
        restored = {}
        for (n, j, s), u in units.items():
            if n in PRIMARY:
                restored.setdefault((n, j), []).append({m: (u[m] if m in u and u[m]["ok"] else failed) for m in METHODS})
        b = theta(restored)
        sensitivity = dict(estimate=b["estimate"], ci=b["ci"])
    descriptive = {}
    for (n, j, s), u in units.items():
        for m, r in u.items():
            d = descriptive.setdefault(f"{n}|{m}", dict(T3000=[], T10000=[], feasible=[], best=[]))
            if r.get("ok"):
                d["T3000"].append(r["T3000"])
                d["T10000"].append(r["T10000"])
                d["feasible"].append(r["best_feasible"] is not None)
                if r["best_feasible"] is not None:
                    d["best"].append(r["best_feasible"])
    descriptive = {k: dict(runs=len(v["T3000"]), mean_T3000=float(np.mean(v["T3000"])) if v["T3000"] else None,
                           mean_T10000=float(np.mean(v["T10000"])) if v["T10000"] else None,
                           feasible=float(np.mean(v["feasible"])) if v["feasible"] else None,
                           median_best=float(np.median(v["best"])) if v["best"] else None)
                   for k, v in descriptive.items()}
    out = dict(units=len(units), complete_primary=len(complete), excluded=[list(map(str, k)) for k in excluded],
               empty_cells=[list(map(str, k)) for k in empty], excluded_instances=data["excluded"], H58=primary,
               sensitivity=sensitivity, descriptive=descriptive)
    i56.save("i58_analysis.json", out)
    print(json.dumps(dict(H58=primary, empty=out["empty_cells"], complete=len(complete)), indent=1))


# ------------------------------------------------------------------ independent checker (no instrument code)

def _independent_case(network, j):
    """Scenario and OPF dispatch rebuilt from raw pypower data (independently of iteration56_orpd)."""
    import contextlib
    import io
    from pypower import api
    case = getattr(api, network)()
    load_factor, scenario_seed = SCENARIOS[j]
    rng = np.random.RandomState(scenario_seed)
    factor = load_factor * (1 + i56.SPREAD * (2 * rng.random_sample(case["bus"].shape[0]) - 1))
    case["bus"][:, 2] *= factor  # PD
    case["bus"][:, 3] *= factor  # QD
    with contextlib.redirect_stdout(io.StringIO()):
        opf = api.runopf(case, api.ppoption(VERBOSE=0, OUT_ALL=0))
    if not opf["success"]:
        return None, None
    case["gen"][:, 1] = opf["gen"][:, 1]  # PG
    online = np.flatnonzero(case["gen"][:, 7] > 0)
    gen_buses = []
    for g in online:
        if int(case["gen"][g, 0]) not in gen_buses:
            gen_buses.append(int(case["gen"][g, 0]))
    taps = np.flatnonzero((case["branch"][:, 8] != 0) & (case["branch"][:, 10] > 0))
    shunts = np.flatnonzero(case["bus"][:, 5] != 0)
    row = {int(b): k for k, b in enumerate(case["bus"][:, 0])}
    lo = [case["bus"][row[b], 12] for b in gen_buses] + [0.9] * len(taps) + [min(0.0, 2 * case["bus"][k, 5]) for k in shunts]
    hi = [case["bus"][row[b], 11] for b in gen_buses] + [1.1] * len(taps) + [max(0.0, 2 * case["bus"][k, 5]) for k in shunts]
    structure = dict(online=online, gen_buses=gen_buses, taps=taps, shunts=shunts, lo=np.array(lo), hi=np.array(hi))
    return case, structure


def independent_check(network, j, x_controls):
    """Validates the vector itself (dimension, bounds, R = 17 grid; no repair) and re-derives losses and all
    violations directly from pypower indices."""
    from pypower import api
    case, st = _independent_case(network, j)
    if case is None:
        return dict(valid=False, reason="OPF failed")
    x = np.asarray(x_controls, float)
    if x.shape != st["lo"].shape:
        return dict(valid=False, reason=f"dimension {x.shape} != {st['lo'].shape}")
    if not np.all(np.isfinite(x)):
        return dict(valid=False, reason="nonfinite controls")
    step = (st["hi"] - st["lo"]) / (RESOLUTION - 1)
    k = (x - st["lo"]) / np.where(step > 0, step, 1)
    if np.any(x < st["lo"] - 1e-9) or np.any(x > st["hi"] + 1e-9) or np.any(np.abs(k - np.rint(k)) > 1e-6):
        return dict(valid=False, reason="outside bounds or off the grid")
    n_b, n_t = len(st["gen_buses"]), len(st["taps"])
    for value, bus in zip(x[:n_b], st["gen_buses"]):
        case["gen"][(case["gen"][:, 0] == bus) & (case["gen"][:, 7] > 0), 5] = value  # VG
    case["branch"][st["taps"], 8] = x[n_b:n_b + n_t]
    case["bus"][st["shunts"], 5] = x[n_b + n_t:]
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        solved, converged = api.runpf(case, api.ppoption(VERBOSE=0, OUT_ALL=0, ENFORCE_Q_LIMS=0, PF_TOL=1e-8,
                                                         PF_MAX_IT=30))
    if not converged or not all(np.isfinite(solved[a]).all() for a in ("bus", "gen", "branch")):
        return dict(valid=True, converged=False)
    bus, gen, branch, base = solved["bus"], solved["gen"][st["online"]], solved["branch"], solved["baseMVA"]
    losses = float(np.sum(branch[:, 13] + branch[:, 15]))
    voltage = float(np.sum(np.clip(bus[:, 7] - bus[:, 11], 0, None) + np.clip(bus[:, 12] - bus[:, 7], 0, None)))
    reactive = float(np.sum(np.clip(gen[:, 2] - gen[:, 3], 0, None) + np.clip(gen[:, 4] - gen[:, 2], 0, None))) / base
    slack = gen[np.isin(gen[:, 0], bus[bus[:, 1] == 3, 0])]
    slack_v = float(np.sum(np.clip(slack[:, 1] - slack[:, 8], 0, None) + np.clip(slack[:, 9] - slack[:, 1], 0, None))) / base
    rating = branch[:, 5]
    flow = np.maximum(np.hypot(branch[:, 13], branch[:, 14]), np.hypot(branch[:, 15], branch[:, 16]))
    thermal = float(np.sum(np.where(rating > 0, np.clip(flow - rating, 0, None), 0))) / base
    violations = dict(voltage=voltage, reactive=reactive, slack=slack_v, thermal=thermal)
    return dict(valid=True, converged=True, losses=losses, violations=violations,
                feasible=all(v <= i56.TOL for v in violations.values()))


def _violation(check):
    return float(sum(max(0.0, v - i56.TOL) for v in check["violations"].values()))


def stage_check():
    """Independent re-check of EVERY required witness: references (L*), first-target, best feasible and both returned
    arms; reported quantities are recomputed. Exits nonzero on any failure (the chain stops)."""
    refs = references()
    rows, failures = [], {}

    def record(source, task, kind, ok, check):
        rows.append(dict(source=source, task=task, kind=kind, ok=bool(ok), check=check))
        if not ok:
            failures[kind] = failures.get(kind, 0) + 1

    for source in ("i58_refs.json", "i58_test.json"):
        for r in i56.load(source)["records"]:
            t = r["task"]
            if not r.get("ok"):
                continue  # execution failures are handled by the analysis rules, not by the checker
            if r["best_feasible"] is not None:
                x = r.get("best_feasible_x")
                c = independent_check(t["network"], t["j"], x) if x is not None else dict(valid=False)
                record(source, t, "best_feasible", x is not None and c.get("feasible")
                       and abs(c["losses"] - r["best_feasible"]) <= 1e-6 * max(1.0, r["best_feasible"]), c)
            if source == "i58_test.json" and r["first_target"] is not None:
                x = r.get("first_target_x")
                c = independent_check(t["network"], t["j"], x) if x is not None else dict(valid=False)
                reference = refs.get(f"{t['network']}|{t['j']}")
                record(source, t, "first_target", x is not None and c.get("feasible")
                       and (reference is None or c["losses"] <= reference * 1.01 + 0.01), c)
            if t["method"] in ("G0", "G1"):
                ret = r.get("returned")
                c = independent_check(t["network"], t["j"], ret["x"]) if ret else dict(valid=False)
                ok = bool(ret) and c.get("valid") and c.get("converged")
                if ok and t["method"] == "G1":
                    ok = (abs(c["losses"] - ret["best_objective"]) <= 1e-6 * max(1.0, abs(ret["best_objective"]))
                          and abs(_violation(c) - ret["best_violation"]) <= 1e-9
                          and bool(c["feasible"]) == bool(ret["feasible"]))
                if ok and t["method"] == "G0":
                    scalar = c["losses"] + i56.SP_WEIGHT * _violation(c)
                    ok = abs(scalar - ret["min_cost"]) <= 1e-6 * max(1.0, abs(ret["min_cost"]))
                record(source, t, f"returned_{t['method']}", ok, c)
    i56.save("i58_check.json", dict(checks=rows, failures=failures,
                                    bound=dict(refs=i57.sha256(i56.path("i58_refs.json.gz")),
                                               test=i57.sha256(i56.path("i58_test.json.gz")))))
    print("checked", len(rows), "failures by kind", failures)
    if failures or not rows:
        raise SystemExit(1)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    if stage == "refs":
        stage_refs(workers)
    elif stage == "test":
        stage_test(workers)
    elif stage == "analyse":
        analyse()
    elif stage == "check":
        stage_check()
    else:
        print(__doc__)
