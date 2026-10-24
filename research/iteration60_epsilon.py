"""I60: confirmatory test of the library epsilon-constraint (G2) vs the usual penalty (G0) on the I58 instances.

Frozen protocol: research/ITERATION60_PROTOCOL.md (frozen before any I58 result). Reuses the I58 instrument,
witness evaluator, independent checker and references (i58_refs.json.gz). Needs the library with patch v4.

  python research/iteration60_epsilon.py test [workers]
  python research/iteration60_epsilon.py check
  python research/iteration60_epsilon.py analyse
"""
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
import iteration57_external as i57  # noqa: E402
import iteration58_validation as i58  # noqa: E402

BUDGET = 3000
GENERATIONS = 188  # 32 + 16 * 188 = 3040 > 3000: the budget stops the run; epsilon reaches zero at ~1536 calls
PURPOSE = 8
PAIRS = 15
ARMS = ("G0", "G2")


def gadapt_run(problem, evaluator, arm, seed):
    from gadapt.ga import GA
    random.seed(seed)
    np.random.seed(seed)
    if arm == "G0":
        def cost(values):
            return 1e300 if evaluator.done else evaluator(values)
        kwargs = {}
    else:
        def cost(values):
            if evaluator.done:
                return 0.0, 1e150
            evaluator(values)
            raw = evaluator.cache[tuple(values)]
            return raw.f, raw.V
        kwargs = dict(constraint_handling="epsilon")
    ga = GA(cost_function=cost, probe_cost_function=False, exit_check="generations", number_of_generations=GENERATIONS,
            exit_function=lambda *a, **k: evaluator.done, timeout=10 ** 6, **kwargs)
    for lo, hi, step in zip(problem.lo, problem.hi, problem.step):
        ga.add(float(lo), float(hi), float(step))
    result = ga.execute()
    returned = None
    if result.success and result.result_values:
        returned = dict(x=[result.result_values[i] for i in sorted(result.result_values)], min_cost=result.min_cost,
                        best_objective=None if math.isnan(result.best_objective) else result.best_objective,
                        best_violation=None if math.isnan(result.best_violation) else result.best_violation,
                        feasible=result.feasible)
    return bool(result.success), returned


def run(task):
    import traceback
    try:
        problem = i58.make_problem(task["network"], task["j"])
        evaluator = i58.WitnessEvaluator(problem, BUDGET, i56.make_target(task.get("reference")))
        success, returned = gadapt_run(problem, evaluator, task["arm"], task["seed"])
        first = evaluator.first_target
        best_x = None
        if math.isfinite(evaluator.best_feasible):
            best_x = next(list(k) for k, r in evaluator.cache.items() if r.feasible and r.f == evaluator.best_feasible)
        return dict(task=task, ok=evaluator.calls == BUDGET and success and evaluator.errors == 0,
                    calls=evaluator.calls, errors=evaluator.errors, first_target=first,
                    T=min(first / BUDGET, 1.0) if first is not None else 1.0,
                    best_feasible=evaluator.best_feasible if math.isfinite(evaluator.best_feasible) else None,
                    best_feasible_x=best_x, first_target_x=evaluator.first_target_x, returned=returned,
                    initial=[list(k) for k in evaluator.initial])
    except Exception:
        return dict(task=task, ok=False, error=traceback.format_exc()[-2000:])


def manifest(stage):
    out = i58.build_manifest(stage)
    out["i60_sha256"] = i57.sha256(os.path.join(HERE, "iteration60_epsilon.py"))
    out["i60_protocol_sha256"] = i57.sha256(os.path.join(HERE, "ITERATION60_PROTOCOL.md"))
    out["refs_sha256"] = i57.sha256(i56.path("i58_refs.json.gz"))
    out["refs_manifest_sha256"] = i57.sha256(i56.path("i58_refs_manifest.json.gz"))
    out["i60_settings"] = dict(budget=BUDGET, generations=GENERATIONS, purpose=PURPOSE, pairs=PAIRS, arms=ARMS,
                               g2="constraint_handling=epsilon; post-budget (0, 1e150)", bootstrap=dict(reps=20000, seed=60))
    return out


I60_PROVENANCE = ("i60_sha256", "i60_protocol_sha256", "refs_sha256", "refs_manifest_sha256", "i60_settings")


def same_provenance(a, b):
    """I58 provenance fields plus the I60 code, protocol, references and settings (Codex 051)."""
    return i58.same_provenance(a, b) and all(i58.normalised(a[f]) == i58.normalised(b[f]) for f in I60_PROVENANCE)


def require_i58_reference_check():
    """The protocol binds I60 to the I58 references; their witnesses (L*) must have passed the I58 independent check."""
    check = i56.load("i58_check.json")
    if check["failures"] or not check["checks"] or check["bound"]["refs"] != i57.sha256(i56.path("i58_refs.json.gz")):
        raise SystemExit("STOP: the I58 independent check of the references is missing, failed, or not bound to them")
    if not any(row["source"] == "i58_refs.json" for row in check["checks"]):
        raise SystemExit("STOP: the I58 independent check contains no reference witnesses")
    # the references must come from the same I58 code, library, environment and settings as this run (Codex 054)
    if not i58.same_provenance(i56.load("i58_refs_manifest.json"), i58.build_manifest("i60-refs-binding")):
        raise SystemExit("STOP: the I58 reference manifest differs from the current I58 code/library/environment/settings")


def stage_test(workers):
    from multiprocessing import Pool
    require_i58_reference_check()
    pre = manifest("i60-test")
    i56.save("i60_manifest.json", pre)
    refs = i58.references()
    valid, excluded = i58.instances()
    tasks = [dict(network=n, j=j, arm=a, seed=i58.seed_of(PURPOSE, n, j, s), reference=refs[f"{n}|{j}"])
             for n, j in valid for s in range(1, PAIRS + 1) for a in ARMS]
    with Pool(workers, maxtasksperchild=1) as pool:
        records = list(pool.imap(run, tasks))
    for i, r in enumerate(records):
        if not r["ok"]:
            with Pool(1, maxtasksperchild=1) as pool:
                again = pool.apply(run, (tasks[i],))
            again["rerun"], again["first_attempt"] = True, {k: v for k, v in r.items() if k != "initial"}
            records[i] = again
    pairs = {}
    for r in records:
        if r.get("ok"):
            pairs.setdefault((r["task"]["network"], r["task"]["j"], r["task"]["seed"]), {})[r["task"]["arm"]] = r["initial"]
    for key, p in pairs.items():
        if len(p) == 2 and (p["G0"] != p["G2"] or len(p["G0"]) != i56.POPULATION_SIZE):
            raise SystemExit(f"STOP: G0/G2 initial populations differ for {key}")
    post = manifest("i60-test-after")
    if not same_provenance(pre, post):
        raise SystemExit("STOP: provenance or references changed during the I60 test")
    i56.save("i60_test.json", dict(excluded=excluded, references=refs, records=records))


def stage_check():
    rows, failures = [], {}
    refs = i58.references()
    for r in i56.load("i60_test.json")["records"]:
        if not r.get("ok"):
            continue
        t = r["task"]

        def add(kind, ok, c):
            rows.append(dict(task=t, kind=kind, ok=bool(ok), check=c))
            if not ok:
                failures[kind] = failures.get(kind, 0) + 1
        if r["best_feasible"] is not None:
            x = r.get("best_feasible_x")
            c = i58.independent_check(t["network"], t["j"], x) if x is not None else dict(valid=False)
            add("best_feasible", x is not None and c.get("feasible")
                and abs(c["losses"] - r["best_feasible"]) <= 1e-6 * max(1.0, r["best_feasible"]), c)
        if r["first_target"] is not None:
            x = r.get("first_target_x")
            c = i58.independent_check(t["network"], t["j"], x) if x is not None else dict(valid=False)
            reference = refs.get(f"{t['network']}|{t['j']}")
            add("first_target", x is not None and c.get("feasible")
                and (reference is None or c["losses"] <= reference * 1.01 + 0.01), c)
        ret = r.get("returned")
        c = i58.independent_check(t["network"], t["j"], ret["x"]) if ret else dict(valid=False)
        ok = bool(ret) and c.get("valid") and c.get("converged")
        if ok and t["arm"] == "G2":
            ok = (abs(c["losses"] - ret["best_objective"]) <= 1e-6 * max(1.0, abs(ret["best_objective"]))
                  and abs(i58._violation(c) - ret["best_violation"]) <= 1e-9 and bool(c["feasible"]) == bool(ret["feasible"]))
        if ok and t["arm"] == "G0":
            scalar = c["losses"] + i56.SP_WEIGHT * i58._violation(c)
            ok = abs(scalar - ret["min_cost"]) <= 1e-6 * max(1.0, abs(ret["min_cost"]))
        add(f"returned_{t['arm']}", ok, c)
    i56.save("i60_check.json", dict(checks=rows, failures=failures,
                                    bound=dict(test=i57.sha256(i56.path("i60_test.json.gz")),
                                               refs=i57.sha256(i56.path("i58_refs.json.gz")))))
    print("checked", len(rows), "failures", failures)
    if failures or not rows:
        raise SystemExit(1)


def analyse():
    data = i56.load("i60_test.json")
    check = i56.load("i60_check.json")
    if check["failures"] or not check["checks"] or check["bound"] != dict(
            test=i57.sha256(i56.path("i60_test.json.gz")), refs=i57.sha256(i56.path("i58_refs.json.gz"))):
        raise SystemExit("STOP: independent check missing, failed, or not bound to these artifacts")
    require_i58_reference_check()
    pre = i56.load("i60_manifest.json")
    if not same_provenance(pre, manifest("i60-analysis")):
        raise SystemExit("STOP: provenance differs from the I60 test manifest")
    units = {}
    for r in data["records"]:
        t = r["task"]
        units.setdefault((t["network"], t["j"], t["seed"]), {})[t["arm"]] = r
    # I58 rules (protocol "Pravila i provera"): complete G0/G2 pairs; primary inference needs every primary network and
    # no empty network x scenario cell; sensitivity (failed runs as T = 1) when a cell is empty or > 5% pairs are excluded
    primary = [k for k in units if k[0] in i58.PRIMARY]
    expected_cells = {(n, n, j) for (n, j, s) in primary}
    complete = {k: units[k] for k in primary if set(units[k]) == set(ARMS) and all(r["ok"] for r in units[k].values())}
    cells = {}
    for (n, j, s), u in complete.items():
        cells.setdefault((n, n, j), []).append(u)
    networks_left = {k[0] for k in cells}
    excluded = sorted(set(primary) - set(complete))
    empty = sorted(expected_cells - set(cells))
    result = None
    if not empty and networks_left == set(i58.PRIMARY):
        b = i56.bootstrap(cells, lambda u: u["G2"]["T"] - u["G0"]["T"], seed=60)
        result = dict(estimate=b["estimate"], ci=b["ci"], supported=b["ci"][1] < 0)
    sensitivity = None
    if empty or len(excluded) > 0.05 * len(primary):
        failed = dict(T=1.0, ok=False)
        restored = {}
        for (n, j, s) in primary:
            u = units[(n, j, s)]
            restored.setdefault((n, n, j), []).append({a: (u[a] if a in u and u[a]["ok"] else failed) for a in ARMS})
        b = i56.bootstrap(restored, lambda u: u["G2"]["T"] - u["G0"]["T"], seed=60)
        sensitivity = dict(estimate=b["estimate"], ci=b["ci"])
    descriptive = {}
    for (n, j, s), u in units.items():
        for a, r in u.items():
            d = descriptive.setdefault(f"{n}|{a}", dict(T=[], feasible=[], best=[]))
            if r.get("ok"):
                d["T"].append(r["T"])
                d["feasible"].append(r["best_feasible"] is not None)
                if r["best_feasible"] is not None:
                    d["best"].append(r["best_feasible"])
    descriptive = {k: dict(runs=len(v["T"]), mean_T=float(np.mean(v["T"])) if v["T"] else None,
                           attained=float(np.mean([t < 1 for t in v["T"]])) if v["T"] else None,
                           feasible=float(np.mean(v["feasible"])) if v["feasible"] else None,
                           median_best=float(np.median(v["best"])) if v["best"] else None) for k, v in descriptive.items()}
    out = dict(H60=result, sensitivity=sensitivity, excluded=[list(map(str, k)) for k in excluded],
               empty_cells=[list(map(str, k[1:])) for k in empty], excluded_instances=data["excluded"],
               complete=len(complete), descriptive=descriptive)
    i56.save("i60_analysis.json", out)
    print(json.dumps(dict(H60=result, complete=len(complete), excluded=out["excluded"]), indent=1))


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    dict(test=lambda: stage_test(workers), check=stage_check, analyse=analyse).get(stage, lambda: print(__doc__))()
