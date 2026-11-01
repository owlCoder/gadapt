"""I58 independent check, amended (deviation D1, documented in the I58 report) — written after the original check
failed and BEFORE the I58 analysis was run or any I58 outcome was looked at.

Finding: the original stage_check (research/iteration58_validation.py) failed only on the RETURNED solutions of G0/G1
on case300 (descriptive network): 67 of 374 returned-solution checks, all with a returned genotype whose power flow
does not converge. The instrument records such a solution with the failure convention (f = 2 f_ref, V = V_FAIL = 10),
and the independent checker also finds a non-converging power flow, i.e. they AGREE; the original rule required
`converged` and so had no branch for the failure convention.

Amendment: identical to the original check, except for a returned solution whose independent power flow does not
converge: it passes only if the instrument reported exactly the failure convention for it (G0: min_cost =
2 f_ref + 1000 * V_FAIL; G1: best_objective = 2 f_ref, best_violation = V_FAIL, feasible False), with f_ref recomputed
independently (raw pypower data, OPF of the scenario). Converged returned solutions keep the original rule. The original
check output is archived unchanged as i58_check_v1.json.gz; this module writes i58_check.json (same structure + the
amendment record). iteration58_validation.py is not modified (its hash is part of the I58 provenance).

  python research/iteration58_check_amendment.py
"""
import contextlib
import io
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import iteration56_cht_study as i56  # noqa: E402
import iteration57_external as i57  # noqa: E402
import iteration58_validation as i58  # noqa: E402

_F_REF = {}


def independent_f_ref(network, j):
    """Losses of the scenario's continuous AC OPF from raw pypower data (as in i58._independent_case)."""
    if (network, j) not in _F_REF:
        from pypower import api
        case = getattr(api, network)()
        load_factor, scenario_seed = i58.SCENARIOS[j]
        rng = np.random.RandomState(scenario_seed)
        factor = load_factor * (1 + i56.SPREAD * (2 * rng.random_sample(case["bus"].shape[0]) - 1))
        case["bus"][:, 2] *= factor
        case["bus"][:, 3] *= factor
        with contextlib.redirect_stdout(io.StringIO()):
            opf = api.runopf(case, api.ppoption(VERBOSE=0, OUT_ALL=0))
        _F_REF[(network, j)] = float(np.sum(opf["branch"][:, 13] + opf["branch"][:, 15])) if opf["success"] else None
    return _F_REF[(network, j)]


def failure_convention(method, ret, f_ref):
    if f_ref is None or not ret:
        return False
    close = lambda a, b: a is not None and abs(a - b) <= 1e-6 * max(1.0, abs(b))  # noqa: E731
    if method == "G0":
        return close(ret["min_cost"], 2 * f_ref + i56.SP_WEIGHT * i56.V_FAIL)
    return (close(ret["best_objective"], 2 * f_ref) and ret["best_violation"] == i56.V_FAIL
            and ret["feasible"] is False)


def amended_check():
    rows, failures = [], {}
    refs = i58.references()
    amended = 0

    def record(source, task, kind, ok, check):
        rows.append(dict(source=source, task=task, kind=kind, ok=bool(ok), check=check))
        if not ok:
            failures[kind] = failures.get(kind, 0) + 1
    for source in ("i58_refs.json", "i58_test.json"):
        for r in i56.load(source)["records"]:
            t = r["task"]
            if not r.get("ok"):
                continue
            if r["best_feasible"] is not None:  # unchanged
                x = r.get("best_feasible_x")
                c = i58.independent_check(t["network"], t["j"], x) if x is not None else dict(valid=False)
                record(source, t, "best_feasible", x is not None and c.get("feasible")
                       and abs(c["losses"] - r["best_feasible"]) <= 1e-6 * max(1.0, r["best_feasible"]), c)
            if source == "i58_test.json" and r["first_target"] is not None:  # unchanged
                x = r.get("first_target_x")
                c = i58.independent_check(t["network"], t["j"], x) if x is not None else dict(valid=False)
                reference = refs.get(f"{t['network']}|{t['j']}")
                record(source, t, "first_target", x is not None and c.get("feasible")
                       and (reference is None or c["losses"] <= reference * 1.01 + 0.01), c)
            if t["method"] in ("G0", "G1"):
                ret = r.get("returned")
                c = i58.independent_check(t["network"], t["j"], ret["x"]) if ret else dict(valid=False)
                if ret and c.get("valid") and c.get("converged") is False:  # D1: the failure convention
                    ok = failure_convention(t["method"], ret, independent_f_ref(t["network"], t["j"]))
                    amended += 1
                    c = dict(c, amendment="D1 failure convention", f_ref=independent_f_ref(t["network"], t["j"]))
                else:  # unchanged original rule
                    ok = bool(ret) and c.get("valid") and c.get("converged")
                    if ok and t["method"] == "G1":
                        ok = (abs(c["losses"] - ret["best_objective"]) <= 1e-6 * max(1.0, abs(ret["best_objective"]))
                              and abs(i58._violation(c) - ret["best_violation"]) <= 1e-9
                              and bool(c["feasible"]) == bool(ret["feasible"]))
                    if ok and t["method"] == "G0":
                        scalar = c["losses"] + i56.SP_WEIGHT * i58._violation(c)
                        ok = abs(scalar - ret["min_cost"]) <= 1e-6 * max(1.0, abs(ret["min_cost"]))
                record(source, t, f"returned_{t['method']}", ok, c)
    return rows, failures, amended


def main():
    original = i56.path("i58_check.json.gz")
    archive = i56.path("i58_check_v1.json.gz")
    if not os.path.exists(archive):
        shutil.copyfile(original, archive)
    v1 = i56.load("i58_check_v1.json")
    rows, failures, amended = amended_check()
    # the unchanged kinds must reproduce the original check row by row
    def key(row):
        return (row["source"], row["task"]["network"], row["task"]["j"], row["task"]["seed"], row["task"]["method"],
                row["kind"])
    old = {key(r): r["ok"] for r in v1["checks"]}
    new = {key(r): r["ok"] for r in rows}
    if set(old) != set(new):
        raise SystemExit("STOP: the amended check does not cover exactly the original rows")
    changed = sorted(k for k in old if old[k] != new[k])
    if any(not k[-1].startswith("returned") or old[k] or not new[k] for k in changed):
        raise SystemExit(f"STOP: the amendment changed rows other than failed returned solutions: {changed[:5]}")
    i56.save("i58_check.json", dict(checks=rows, failures=failures,
                                    bound=dict(refs=i57.sha256(i56.path("i58_refs.json.gz")),
                                               test=i57.sha256(i56.path("i58_test.json.gz"))),
                                    amendment=dict(id="D1", rows_using_failure_convention=amended,
                                                   rows_changed=len(changed),
                                                   original_sha256=i57.sha256(archive),
                                                   code_sha256=i57.sha256(os.path.abspath(__file__)))))
    print("checked", len(rows), "failures", failures, "failure-convention rows", amended, "changed", len(changed))
    if failures or not rows:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
