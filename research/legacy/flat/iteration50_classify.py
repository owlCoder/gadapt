"""I50: documentation classification (pre-specified in ITERATION50_ELIGIBILITY.md §3) and a POST HOC sensitivity
analysis without C1. Reads research/results/iteration50/integrity_audit.json; writes classification.json.
"""
import json
import os

from scipy.stats import beta

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "iteration50")

# ELIGIBILITY §3, "Primena pravila iz §6 protokola (unapred)"
C4_DOCUMENTED = {"bayes_opt", "gfo", "niapy", "smac"}
BOUNDS_QUOTE = {"bayes_opt", "cmaes", "gfo", "evolopy", "evox", "baybe", "bofire"}
SEED_QUOTE = {"bayes_opt", "cmaes", "gfo", "niapy", "smac", "evotorch", "baybe", "bofire"}
BEST_QUOTE = {"bayes_opt", "gfo", "niapy", "evolopy", "evox"}
INTEGRITY = ("C1", "C3", "C4", "C5", "R1", "R2", "R3", "D2", "D3", "D3x")


def contradicts(lib, cls):
    return ((cls == "C4" and lib in C4_DOCUMENTED) or (cls == "C3" and lib in BOUNDS_QUOTE)
            or (cls in ("D3", "D3x") and lib in SEED_QUOTE) or (cls in ("R1", "R2", "R3") and lib in BEST_QUOTE))


def cp(k, n):
    return [0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1)),
            1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))]


def main():
    audit = json.load(open(os.path.join(OUT, "integrity_audit.json")))
    per = {lib: row for lib, row in audit["per_library"].items() if row["assessable"]}
    rows, contra_libs, no_c1_libs = {}, [], []
    for lib, row in per.items():
        found = [k for k in INTEGRITY if row["runs_with_class"].get(k)]
        rows[lib] = {k: ("protivreči dokumentaciji" if contradicts(lib, k) else "dokumentovano ili praznina")
                     for k in found}
        if any(contradicts(lib, k) for k in found):
            contra_libs.append(lib)
        if any(k != "C1" for k in found):
            no_c1_libs.append(lib)
    n = len(per)
    out = dict(
        n=n, findings=rows,
        secondary_contradicts_docs=dict(k=len(contra_libs), libraries=sorted(contra_libs),
                                        clopper_pearson_95=cp(len(contra_libs), n)),
        post_hoc_without_C1=dict(k=len(no_c1_libs), libraries=sorted(no_c1_libs),
                                 clopper_pearson_95=cp(len(no_c1_libs), n),
                                 pooled_with_i49=dict(k=len(no_c1_libs) + 4, n=n + 9,
                                                      clopper_pearson_95=cp(len(no_c1_libs) + 4, n + 9)),
                                 note="POST HOC: C1 is not specific to probe calls for algorithms that clip to "
                                      "the bounds; I49's 4/9 contained no C1-only library."))
    json.dump(out, open(os.path.join(OUT, "classification.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
