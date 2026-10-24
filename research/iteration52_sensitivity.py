"""Post hoc sensitivity of the I52 transfer agreement (plan: research/ITERATION52_SENSITIVITY_PLAN.md).

Descriptive only, archived data only. Usage: .venv/bin/python research/iteration52_sensitivity.py
"""
import glob
import hashlib
import json
import os
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
OUT = os.path.join(RES, "iteration52", "sensitivity.json")
K = ["C3", "C4", "C5", "R1", "R2", "R3", "D2", "D3", "D3x"]
DISPATCH_CELLS = 15
THRESHOLD = 17
inputs = []


def load(path):
    inputs.append(path)
    with open(path) as f:
        return json.load(f)


def positive(flags):
    return any((flags.get(c) or 0) > 0 for c in K)


def archive_a():
    """library -> list of positivity of successful synthetic cells (I49 + I51 D3x, I50)."""
    out = {}
    i49 = load(os.path.join(RES, "iteration49", "integrity_audit.json"))["cells"]
    i51 = {(c["library"], c["function"], c["d"], c["seed"]): c
           for c in load(os.path.join(RES, "iteration51", "d3x.json"))["cells"]}
    for c in i49:
        if c["library"] == "gadapt":
            continue
        d = i51.get((c["library"], c["function"], c["d"], c["seed"]))
        if c["error"] is not None or d is None or d["error"] is not None:
            continue
        out.setdefault(c["library"], []).append(positive(dict(c["flags"], D3x=d["D3x"])))
    for path in sorted(glob.glob(os.path.join(RES, "iteration50", "cells_*.json"))):
        for c in load(path)["cells"]:
            if c["error"] is None:
                out.setdefault(c["library"], []).append(positive(c["flags"]))
    return out


def archive_b():
    """library -> list of positivity of valid I55 cells (D3x = D3x_diff)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(RES, "iteration55", "cells_*.json"))):
        for c in load(path)["cells"]:
            if c["library"] == "gadapt" or c["error"] is not None or not c.get("manipulation_ok"):
                continue
            flags = dict(c["flags"], D3=c["D3"], D3x=c["D3x_diff"])
            out.setdefault(c["library"], []).append(positive(flags))
    return out


def dispatch():
    """library -> (successful cells m_l, D_l)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(RES, "iteration52", "cells_*.json"))):
        cells = [c for c in load(path)["cells"] if c["error"] is None]
        lib = load(path)["library"]
        if lib == "gadapt":
            continue
        out[lib] = (len(cells), any(positive(c["flags"]) for c in cells))
    return out


def convolve(probabilities):
    dist = [1.0]
    for p in probabilities:
        nxt = [0.0] * (len(dist) + 1)
        for a, mass in enumerate(dist):
            nxt[a] += mass * (1 - p)
            nxt[a + 1] += mass * p
        dist = nxt
    return dist


def analyse(synthetic, disp):
    libs = sorted(disp)
    assert sorted(synthetic) == libs, (sorted(synthetic), libs)
    per_lib, agree_p = {}, []
    for lib in libs:
        n, k = len(synthetic[lib]), sum(synthetic[lib])
        m, d = disp[lib]
        q = comb(n - k, m) / comb(n, m)
        p_agree = q if not d else 1 - q
        agree_p.append(p_agree)
        per_lib[lib] = {"n": n, "k": k, "S": k > 0, "m": m, "D": d, "agree": (k > 0) == d,
                        "q_matched_negative": q, "p_agree_matched": p_agree}
    dist = convolve(agree_p)
    support = [a for a, mass in enumerate(dist) if mass > 1e-15]
    complete = [lib for lib in libs if per_lib[lib]["m"] == DISPATCH_CELLS]
    confusion = {f"S{int(s)}_D{int(d)}": sum(1 for lib in complete if per_lib[lib]["S"] == s and per_lib[lib]["D"] == d)
                 for s in (True, False) for d in (True, False)}
    lower = upper = all_pos = 0
    for lib in libs:
        r = per_lib[lib]
        options = {r["D"], r["D"] or r["m"] < DISPATCH_CELLS}
        hits = [r["S"] == d for d in options]
        lower += min(hits)
        upper += max(hits)
        all_pos += r["S"] == (r["D"] or r["m"] < DISPATCH_CELLS)
    observed = sum(r["agree"] for r in per_lib.values())
    return {
        "observed_agreement": observed, "libraries": len(libs),
        "disagreements": [lib for lib in libs if not per_lib[lib]["agree"]],
        "matched_exposure": {"distribution": dist, "support": [min(support), max(support)],
                             "expectation": sum(a * mass for a, mass in enumerate(dist)),
                             "p_at_least_17": sum(dist[THRESHOLD:])},
        "complete_only": {"libraries": complete, "agreement": sum(per_lib[lib]["agree"] for lib in complete),
                          "denominator": len(complete), "confusion": confusion,
                          "positive_recurrence": [confusion["S1_D1"], confusion["S1_D1"] + confusion["S1_D0"]]},
        "missing_bounds": {"incomplete": [lib for lib in libs if per_lib[lib]["m"] < DISPATCH_CELLS],
                           "lower": lower, "upper": upper, "all_missing_negative": observed,
                           "all_missing_positive": all_pos, "denominator": len(libs)},
        "per_library": per_lib,
    }


def main():
    disp = dispatch()
    a = analyse(archive_a(), disp)
    if a["observed_agreement"] != 19 or sorted(a["disagreements"]) != ["nevergrad", "scipy_de"]:
        raise SystemExit(f"STOP: control failed, {a['observed_agreement']}/21, {a['disagreements']}")
    b = analyse(archive_b(), disp)
    not_robust = any(r["matched_exposure"]["support"][0] < THRESHOLD or r["missing_bounds"]["lower"] < THRESHOLD
                     for r in (a, b))
    hashes = {os.path.relpath(p, HERE): hashlib.sha256(open(p, "rb").read()).hexdigest() for p in sorted(set(inputs))}
    hashes[os.path.basename(__file__)] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    result = {"plan": "research/ITERATION52_SENSITIVITY_PLAN.md", "post_hoc_descriptive": True,
              "archive_A_original": a, "archive_B_i55": b, "not_uniformly_robust": not_robust, "sha256": hashes}
    with open(OUT, "w") as f:
        json.dump(result, f, indent=1)
    for name, r in (("A", a), ("B", b)):
        me, cb, mb = r["matched_exposure"], r["complete_only"], r["missing_bounds"]
        print(f"archive {name}: observed {r['observed_agreement']}/{r['libraries']} {r['disagreements']}; matched "
              f"support {me['support']} E={me['expectation']:.2f} P(>=17)={me['p_at_least_17']:.3f}; complete "
              f"{cb['agreement']}/{cb['denominator']} pos {cb['positive_recurrence']}; bounds "
              f"[{mb['lower']}, {mb['upper']}] all+ {mb['all_missing_positive']} incomplete {mb['incomplete']}")
    print("not uniformly robust:", not_robust)


if __name__ == "__main__":
    main()
