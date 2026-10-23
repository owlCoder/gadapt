"""I55: recompute the paper's test-function numbers from the archived call traces (protocol §4).

Reads research/results/iteration55/cells_<lib>.json and traces/<lib>/*.npz, reclassifies every run from its trace
with the unchanged I49/I50 classifier, and compares the flags with the archived I49/I50 cells (H55d).
Usage: python -m research.iteration55_recompute
"""
import glob
import json
import os

import numpy as np

import research.iteration49_integrity_audit as i49
import research.iteration50_integrity_audit as i50
from research.iteration55_d3x_traces import OUT, PHASES

INTEGRITY_NO_C1 = ("C3", "C4", "C5", "R1", "R2", "R3", "D2")


def load_trace(path):
    t = np.load(path)
    calls = [(t["x"][k], float(t["f"][k]), PHASES[t["phase"][k]]) for k in range(len(t["f"]))]
    f_star = float(t["f_star"][0])
    res = dict(x=t["x_star"] if t["x_star"].size else None, f=None if np.isnan(f_star) else f_star,
               reported_evals=None if t["reported_evals"][0] < 0 else int(t["reported_evals"][0]),
               documented_max=None if t["documented_max"][0] < 0 else int(t["documented_max"][0]))
    return calls, res


def archived_flags():
    """(library, function, d, seed) -> flags from the original I49 / I50 runs."""
    out = {}
    for c in json.load(open("research/results/iteration49/integrity_audit.json"))["cells"]:
        if c.get("flags") is not None:
            out[(c["library"], c["function"], c["d"], c["seed"])] = c["flags"]
    for f in glob.glob("research/results/iteration50/cells_*.json"):
        for c in json.load(open(f))["cells"]:
            if c.get("flags") is not None:
                out[(c["library"], c["function"], c["d"], c["seed"])] = c["flags"]
    return out


def main():
    archive = archived_flags()
    libraries, mismatches = {}, []
    for path in sorted(glob.glob(os.path.join(OUT, "cells_*.json"))):
        data = json.load(open(path))
        library = data["library"]
        rows = []
        for c in data["cells"]:
            trace = os.path.join(OUT, "traces", library, f"{c['function']}_{c['d']}_{c['seed']}.npz")
            if c.get("error") or not os.path.exists(trace):
                rows.append(dict(error=c.get("error") or "no trace"))
                continue
            calls, res = load_trace(trace)
            flags, n, _ = i50.classify(calls, res, i49.Problem(c["function"], c["d"]))
            assert i49.sequence_hash(calls) == c["hash"], (library, c["function"], c["d"], c["seed"])
            rows.append(dict(flags=flags, n=n, D3=c.get("D3"), D3x_same=c.get("D3x_same"), D3x_diff=c.get("D3x_diff"),
                             manipulation_ok=c.get("manipulation_ok")))
            old = archive.get((library, c["function"], c["d"], c["seed"]))
            if old is not None:
                keys = set(flags) & set(old)
                diff = {k: (old[k], flags[k]) for k in sorted(keys) if bool(old[k]) != bool(flags[k])}
                if diff:
                    mismatches.append(dict(library=library, function=c["function"], d=c["d"], seed=c["seed"],
                                           archived_vs_new=diff))
        ok = [r for r in rows if "flags" in r]
        any_class = lambda k: sum(1 for r in ok if r["flags"].get(k))
        libraries[library] = dict(
            sample=data["sample"], cells=len(rows), traced=len(ok),
            runs_with={k: any_class(k) for k in ("C1",) + INTEGRITY_NO_C1},
            D3=sum(r["D3"] or 0 for r in ok), D3x_same=sum(r["D3x_same"] or 0 for r in ok),
            D3x_diff=sum(r["D3x_diff"] or 0 for r in ok),
            manipulation_failures=sum(1 for r in ok if not r["manipulation_ok"]),
            median_repeated_share=float(np.median([r["flags"]["C2"] / r["n"] for r in ok if r["n"]])) if ok else None)
        lib = libraries[library]
        lib["finding_excl_C1"] = bool(any(lib["runs_with"][k] for k in INTEGRITY_NO_C1) or lib["D3"] or lib["D3x_diff"])
        lib["finding_any"] = lib["finding_excl_C1"] or bool(lib["runs_with"]["C1"])
    summary = dict(
        libraries=len(libraries),
        finding_excl_C1=sorted(k for k, v in libraries.items() if v["finding_excl_C1"]),
        finding_any=sorted(k for k, v in libraries.items() if v["finding_any"]),
        d3x_diff=sorted(k for k, v in libraries.items() if v["D3x_diff"]),
        d3x_same=sorted(k for k, v in libraries.items() if v["D3x_same"]),
        flag_mismatches_vs_archive=len(mismatches))
    json.dump(dict(summary=summary, libraries=libraries, mismatches=mismatches),
              open(os.path.join(OUT, "recompute.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
