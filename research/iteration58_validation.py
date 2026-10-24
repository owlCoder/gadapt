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


class BusORPD(ORPD):
    """I56 instrument with ONE voltage set-point per generator bus, applied to every generator on that bus."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from pypower.idx_gen import GEN_BUS
        gen = self.base["gen"]
        buses = []
        for g in self.gen_rows:
            b = int(gen[g, GEN_BUS])
            if b not in buses:
                buses.append(b)
        self.bus_groups = [[g for g in self.gen_rows if int(gen[g, GEN_BUS]) == b] for b in buses]
        first = [self.gen_rows.index(group[0]) for group in self.bus_groups]
        n_g = len(self.gen_rows)
        keep = first + list(range(n_g, self.d))
        self.lo, self.hi = self.lo[keep], self.hi[keep]
        self.d = len(keep)
        self.step = (self.hi - self.lo) / (self.resolution - 1)

    def evaluate(self, x):
        x = self.snap(x)
        n_b = len(self.bus_groups)
        per_gen = np.empty(len(self.gen_rows))
        for value, group in zip(x[:n_b], self.bus_groups):
            for g in group:
                per_gen[self.gen_rows.index(g)] = value
        full_lo, full_hi, full_step, full_d = self.lo, self.hi, self.step, self.d
        expanded = np.concatenate([per_gen, x[n_b:]])
        try:  # the parent evaluates the expanded vector on the parent's grid (already on grid: snap is identity)
            self.lo = np.concatenate([per_gen, full_lo[n_b:]])
            self.hi = np.concatenate([per_gen, full_hi[n_b:]])
            self.step = np.concatenate([np.ones(len(per_gen)), full_step[n_b:]])
            self.d = len(expanded)
            return super().evaluate(expanded)
        finally:
            self.lo, self.hi, self.step, self.d = full_lo, full_hi, full_step, full_d


def make_problem(network, j):
    load_factor, scenario_seed = SCENARIOS[j]
    return BusORPD(network, RESOLUTION, load_factor, i56.SPREAD, scenario_seed)


def gadapt_run(problem, evaluator, method, seed):
    from gadapt.ga import GA
    random.seed(seed)
    np.random.seed(seed)
    if method == "G0":
        cost, kwargs = evaluator, {}
    else:
        def cost(values):
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
    if method == "G1" and result.success and not math.isnan(result.best_objective):
        returned = [result.result_values[i] for i in sorted(result.result_values)]
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
    evaluator = i56.Evaluator(problem, task["budget"], target)
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
    return records


def stage_refs(workers):
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
    pre = dict(refs_sha256=i57.sha256(i56.path("i58_refs.json.gz")), references=refs,
               code_sha256={f: i57.sha256(os.path.join(HERE, f)) for f in
                            ("iteration58_validation.py", "iteration57_external.py", "iteration56_cht_study.py",
                             "iteration56_orpd.py", "ITERATION58_PROTOCOL.md")})
    import gadapt.ga as gadapt_ga
    pre["gadapt_ga_sha256"] = i57.sha256(gadapt_ga.__file__)
    i56.save("i58_manifest.json", pre)
    valid, excluded = instances()
    tasks = [dict(network=n, j=j, method=m, seed=seed_of(6, n, j, s), budget=TEST_BUDGET, reference=refs[f"{n}|{j}"])
             for n, j in valid for s in range(1, 16) for m in METHODS]
    records = pool_run(tasks, workers)
    if i57.sha256(i56.path("i58_refs.json.gz")) != pre["refs_sha256"]:
        raise SystemExit("STOP: references changed during the test")
    i56.save("i58_test.json", dict(excluded=excluded, references=refs, records=records))


def analyse():
    data = i56.load("i58_test.json")
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

def independent_check(network, j, x_controls):
    """Re-implements scenario, OPF dispatch, controls and all violations directly on pypower data."""
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
    case["gen"][:, 1] = opf["gen"][:, 1]  # PG
    online = np.flatnonzero(case["gen"][:, 7] > 0)
    gen_buses = []
    for g in online:
        if int(case["gen"][g, 0]) not in gen_buses:
            gen_buses.append(int(case["gen"][g, 0]))
    taps = np.flatnonzero((case["branch"][:, 8] != 0) & (case["branch"][:, 10] > 0))
    shunts = np.flatnonzero(case["bus"][:, 5] != 0)
    x = np.asarray(x_controls, float)
    for value, bus in zip(x[:len(gen_buses)], gen_buses):
        case["gen"][(case["gen"][:, 0] == bus) & (case["gen"][:, 7] > 0), 5] = value  # VG
    case["branch"][taps, 8] = x[len(gen_buses):len(gen_buses) + len(taps)]
    case["bus"][shunts, 5] = x[len(gen_buses) + len(taps):]
    with contextlib.redirect_stdout(io.StringIO()):
        solved, converged = api.runpf(case, api.ppoption(VERBOSE=0, OUT_ALL=0, ENFORCE_Q_LIMS=0, PF_TOL=1e-8,
                                                         PF_MAX_IT=30))
    if not converged:
        return dict(converged=False)
    bus, gen, branch, base = solved["bus"], solved["gen"][online], solved["branch"], solved["baseMVA"]
    losses = float(np.sum(branch[:, 13] + branch[:, 15]))
    voltage = float(np.sum(np.clip(bus[:, 7] - bus[:, 11], 0, None) + np.clip(bus[:, 12] - bus[:, 7], 0, None)))
    reactive = float(np.sum(np.clip(gen[:, 2] - gen[:, 3], 0, None) + np.clip(gen[:, 4] - gen[:, 2], 0, None))) / base
    ref_buses = bus[bus[:, 1] == 3, 0]
    slack = gen[np.isin(gen[:, 0], ref_buses)]
    slack_v = float(np.sum(np.clip(slack[:, 1] - slack[:, 8], 0, None) + np.clip(slack[:, 9] - slack[:, 1], 0, None))) / base
    s_from = np.hypot(branch[:, 13], branch[:, 14])
    s_to = np.hypot(branch[:, 15], branch[:, 16])
    rating = branch[:, 5]
    thermal = float(np.sum(np.where(rating > 0, np.clip(np.maximum(s_from, s_to) - rating, 0, None), 0))) / base
    violations = dict(voltage=voltage, reactive=reactive, slack=slack_v, thermal=thermal)
    return dict(converged=True, losses=losses, violations=violations,
                feasible=all(v <= i56.TOL for v in violations.values()))


def stage_check():
    data = i56.load("i58_test.json")
    out = []
    for r in data["records"]:
        t = r["task"]
        for label in ("returned", "best_feasible_x"):
            if r.get(label):
                problem = make_problem(t["network"], t["j"])
                x = problem.snap(r[label])
                check = independent_check(t["network"], t["j"], x)
                out.append(dict(task=t, which=label, recorded=r.get("best_feasible"), check=check))
    bad = [c for c in out if c["which"] == "best_feasible_x" and not (
        c["check"].get("feasible") and abs(c["check"]["losses"] - c["recorded"]) <= 1e-6 * max(1, c["recorded"]))]
    i56.save("i58_check.json", dict(checks=out, mismatches=len(bad)))
    print("checked", len(out), "mismatches", len(bad))


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
