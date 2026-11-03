#!/usr/bin/env python3
"""Read-only arithmetic audit of seven frozen I64 compressed analysis archives.

No optimizer, power-flow solver, random bootstrap, or new experiment is run.
For a full clone of owlCoder/gadapt pinned to 6b56fbc...:

  python i64_archival_recheck.py --repo-root /path/to/gadapt \
      > I65_I64_FULL_ANALYSIS_RECHECK.json

Every gzip source is verified against its historical Git *blob* SHA before
its contents are inspected. The calculations below independently combine
selected archived aggregates; they do NOT independently rerun the original
20,000 bootstrap replicates or examine every individual stochastic run.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
from typing import Any

PINNED_HEAD = "6b56fbc53ffc4d275ecef5e911ea4663474c9a08"
ARCHIVES = {
    "S0": ("iteration64_s0/analysis.json.gz", "db5f5f97f70b4bf611e5f592d141549d29fe7fcb"),
    "E": ("iteration64_e/analysis_v2.json.gz", "a101501c3ff59ba8207502f5eff15c3da9b59f84"),
    "R": ("iteration64_r/analysis.json.gz", "59025d6cc052baef76b14e5496962704bdb7604a"),
    "E3": ("iteration64_e3/analysis.json.gz", "f6b819a560a3a203c941469cf4b23fac77307e7f"),
    "A": ("iteration64_a/analysis.json.gz", "9a93cc45d6bcbd610ff9e0be5ae8ac9c0696f241"),
    "I": ("iteration64_i/analysis.json.gz", "f20065966af7e20a19bb40ba32c004eece6ba7e2"),
    "I2": ("iteration64_i2/analysis.json.gz", "2b38375126a43128dba37aaf7966b92eb6df8691"),
}


def git_blob_sha(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def open_pinned(root: Path, key: str) -> dict[str, Any]:
    path, sha = ARCHIVES[key]
    target = root / "research" / "results" / path
    buf = target.read_bytes()
    observed = git_blob_sha(buf)
    if observed != sha:
        raise ValueError(f"{key} source Git blob mismatch: {observed} (expected {sha})")
    doc = json.loads(gzip.decompress(buf))
    if not isinstance(doc, dict):
        raise ValueError(f"{key} source is not a JSON object")
    return doc


def arithmetic_checks(src: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Recalculate source-level arithmetic, preserving predeclared labels."""
    checks = []

    def eq(label: str, derived: float, archived: float, tol: float = 5e-12) -> None:
        good = math.isfinite(derived) and math.isfinite(archived) and math.isclose(
            derived, archived, rel_tol=0, abs_tol=tol)
        checks.append({"name": label, "derived": derived, "archived": archived,
                       "abs_difference": abs(derived - archived), "pass": good})

    def claim(label: str, actual: Any, expected: Any) -> None:
        checks.append({"name": label, "observed": actual, "expected": expected,
                       "pass": actual == expected})

    s0, e, r, e3, a, i, i2 = (src[n] for n in ARCHIVES)
    S = s0["aggregate"]
    E = e["aggregate"]
    claim("S0 aggregate A(GAdapt) > A(DE) at its original stopping regime",
          S["gadapt"]["A"] > S["de"]["A"], True)
    claim("S0 frozen hypothesis direction", s0["verdict"], "supported")
    claim("E stronger-baseline reversal", e["verdict"], "opposite")
    eq("E dA GAdapt-IPOP from full equal-budget aggregates",
       E["gadapt"]["A"] - E["ipop"]["A"], e["contrasts"]["dA|ipop"]["estimate"])
    eq("E dA GAdapt-CMA from aggregates",
       E["gadapt"]["A"] - E["cma"]["A"], e["contrasts"]["dA|cma"]["estimate"])
    claim("E dA GAdapt-IPOP simultaneous interval negative",
          e["contrasts"]["dA|ipop"]["upper"] < 0, True)

    G = r["aggregates"]
    r_exp = [G["rotm|gadapt"] - G["rot|gadapt"],
             G["shift|gadapt"] - G["rotm|gadapt"],
             G["shift|ipop"] - G["rotm|ipop"]]
    r_exp.append(r_exp[1] - r_exp[2])
    for j, value in enumerate(r_exp):
        eq(f"R c{j + 1} reconstructed from six aggregate A values", value, r["estimates"][j])
        claim(f"R c{j + 1} estimate in original simultaneous interval",
              r["lower"][j] <= r["estimates"][j] <= r["upper"][j], True)
    claim("R prespecified H64r2", r["H64r2"], "supported")
    claim("R prespecified H64r3", r["H64r3"], "supported")
    claim("R positive simultaneous lower bound on differential Q loss", r["lower"][3] > 0.05, True)

    T = e3["aggregate_by_variant"]
    A3 = lambda variant, method, stat: T[variant][method][stat]
    eq("E3 rotated A(H)-A(M)", A3("rot", "gadapt_hyb", "A") - A3("rot", "gadapt", "A"),
       e3["contrasts"]["dA_rot(H-M)"]["estimate"])
    eq("E3 non-rotated A(H)-A(M)",
       sum(A3(v, "gadapt_hyb", "A") - A3(v, "gadapt", "A") for v in ("orig", "shift")) / 2,
       e3["contrasts"]["dA_nonrot(H-M)"]["estimate"])
    eq("E3 rotated 0.8*CVAR(M)-CVAR(H)",
       0.8*A3("rot", "gadapt", "cvar90") - A3("rot", "gadapt_hyb", "cvar90"),
       e3["contrasts"]["0.8*CVaR_rot(M)-CVaR_rot(H)"]["estimate"])
    eq("E3 non-rotated 1.5*CVAR(M)-CVAR(H)",
       sum(1.5*A3(v, "gadapt", "cvar90") - A3(v, "gadapt_hyb", "cvar90") for v in ("orig", "shift")) / 2,
       e3["contrasts"]["1.5*CVaR_nonrot(M)-CVaR_nonrot(H)"]["estimate"])
    eq("E3 rotated A(H)-A(IPOP)",
       A3("rot", "gadapt_hyb", "A") - A3("rot", "ipop", "A"),
       e3["contrasts"]["dA_rot(H-IPOP)"]["estimate"])
    claim("E3 negative nonrotated tail lower and upper", e3["contrasts"][
          "1.5*CVaR_nonrot(M)-CVaR_nonrot(H)"]["upper"] < 0, True)
    claim("E3 H64g2 opposite", e3["H64g2"], "opposite")
    claim("E3 overall support is false", e3["supported"], False)

    B = a["aggregate_by_variant"]
    for j, value in enumerate([
        B["rot"]["H"]["A"] - B["rot"]["R"]["A"],
        sum(B[v]["H"]["A"] - B[v]["R"]["A"] for v in ("orig", "shift")) / 2,
        B["rot"]["R"]["cvar90"] - B["rot"]["H"]["cvar90"],
        sum(B[v]["R"]["cvar90"] - B[v]["H"]["cvar90"] for v in ("orig", "shift")) / 2,
    ]):
        eq(f"A ablation c{j + 1} from H versus random-stage R aggregates", value, a["estimates"][j])
    claim("A ablation effect conditional on fixed CMA initialization", a["contribution_supported"], True)

    claim("I primary H64c undecided", i["H64c"], "undecided")
    claim("I preset H64d opposite", i["H64d"], "opposite")
    claim("I2 H64h1 undecided", i2["H64h1"], "undecided")
    claim("I2 H64h2 opposite", i2["H64h2"], "opposite")
    Q = i2["aggregate"]
    eq("I2 original GAdapt CVaR equals I original GAdapt CVaR",
       Q["gadapt"]["cvar90"], i["CVaR_G"])
    inputs = [
        ("CVaR(M)-CVaR(H)", Q["gadapt"]["cvar90"] - Q["gadapt_hyb"]["cvar90"]),
        ("P(H)-P(M)", Q["gadapt_hyb"]["P"] - Q["gadapt"]["P"]),
        ("CVaR(IPOP)-CVaR(H)", Q["ipop"]["cvar90"] - Q["gadapt_hyb"]["cvar90"]),
        ("P(H)-P(IPOP)", Q["gadapt_hyb"]["P"] - Q["ipop"]["P"]),
    ]
    for label, value in inputs:
        eq("I2 " + label + " from aggregate outcomes", value, i2["contrasts"][label]["estimate"])
    claim("I2 simultaneous tail-CVaR interval strictly favors IPOP",
          i2["contrasts"]["CVaR(IPOP)-CVaR(H)"]["upper"] < 0, True)
    claim("I2 feasibility contrast does not establish strict deterioration at zero",
          i2["contrasts"]["P(H)-P(IPOP)"]["lower"] < 0 <
          i2["contrasts"]["P(H)-P(IPOP)"]["upper"], True)

    return {"checks": checks, "passed": sum(x["pass"] for x in checks),
            "total": len(checks), "all_pass": all(x["pass"] for x in checks),
            "highlights": {
                "S0_original_A_gadapt": S["gadapt"]["A"],
                "S0_original_A_de": S["de"]["A"],
                "E_equal_budget_A_gadapt": E["gadapt"]["A"],
                "E_equal_budget_A_ipop": E["ipop"]["A"],
                "R_added_orthogonal_Q_gap_difference": r["estimates"][3],
                "R_Q_gap_difference_CI": [r["lower"][3], r["upper"][3]],
                "E3_nonrot_tail_contrast": e3["contrasts"][
                    "1.5*CVaR_nonrot(M)-CVaR_nonrot(H)"],
                "I2_ipop_vs_hybrid_tail_CI": i2["contrasts"]["CVaR(IPOP)-CVaR(H)"],
            }}


def audit(repo_root: Path) -> dict[str, Any]:
    data = {key: open_pinned(repo_root, key) for key in ARCHIVES}
    return {"schema": "GADAPT_I65_I64_SEVEN_ARCHIVE_ARITHMETIC_V1",
            "pinned_source_head": PINNED_HEAD,
            "sources": {k: {"path": "research/results/" + p, "git_blob_sha": sha}
                        for k, (p, sha) in ARCHIVES.items()},
            "no_new_optimizations": True,
            "no_new_bootstrap": True,
            "verification_level": "Seven original compressed analysis sources; derived scalar arithmetic only",
            **arithmetic_checks(data),
            "limits": ["No individual run replay", "No independent 20,000-replicate bootstrap", "Conditional fixed-cell conclusions; not a randomly sampled problem universe", "No new objective/PF/OPF/COCO calls", "No human supervisor or novelty signoff"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", required=True, type=Path)
    o = p.parse_args()
    report = audit(o.repo_root)
    print(json.dumps(report, indent=2, allow_nan=False, sort_keys=True))
    if not report["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
