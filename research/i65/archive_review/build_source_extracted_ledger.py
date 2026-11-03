#!/usr/bin/env python3
"""Compute a current-turn arithmetic ledger from SELECTED fields manually recorded
from GitHub-connected, decompressed I64 gzip sources. Not a local gzip replay.
The full pinned-archive auditor in i64_archival_recheck.py is the runnable
replacement when a complete checked-out repository is available.
"""
from __future__ import annotations
import json
from pathlib import Path
from i64_archival_recheck import ARCHIVES, PINNED_HEAD, arithmetic_checks

SRC = {
    "S0": {"verdict": "supported", "aggregate": {
        "gadapt": {"A": 0.6983036008230452},
        "de": {"A": 0.6509895576131688}}},
    "E": {"verdict": "opposite", "aggregate": {
        "gadapt": {"A": 0.6732050137174209},
        "ipop": {"A": 0.7698678429355281},
        "cma": {"A": 0.7618085699588476}},
        "contrasts": {
            "dA|ipop": {"estimate": -0.09666282921810702,
                          "lower": -0.10335092147172405, "upper": -0.08997473696449},
            "dA|cma": {"estimate": -0.08860355624142663}}},
    "R": {"aggregates": {
        "shift|gadapt": 0.7007133744855967, "shift|ipop": 0.770072355967078,
        "rot|gadapt": 0.6167328086419752, "rot|ipop": 0.7629837345679013,
        "rotm|gadapt": 0.6198270061728393, "rotm|ipop": 0.7599777674897119},
        "estimates": [0.00309419753086404, 0.08088636831275742,
                      0.010094588477366107, 0.07079177983539131],
        "lower": [-0.00805143951297009, 0.07211420407582879,
                  0.0036370169694745352, 0.059811869725967554],
        "upper": [0.01423983457469817, 0.08965853254968605,
                  0.016552159985257678, 0.08177168994481507],
        "H64r2": "supported", "H64r3": "supported"},
    "E3": {"supported": False, "H64g2": "opposite",
        "aggregate_by_variant": {
            "orig": {"gadapt": {"A": 0.7021688580246913, "cvar90": 0.0025886268487890474},
                     "gadapt_hyb": {"A": 0.7628009670781891, "cvar90": 0.004771194868098625},
                     "ipop": {"A": 0.776547438271605}},
            "shift": {"gadapt": {"A": 0.7007133744855967, "cvar90": 0.0025437743343927482},
                      "gadapt_hyb": {"A": 0.7707763580246916, "cvar90": 0.004320262140456046},
                      "ipop": {"A": 0.7700723559670782}},
            "rot": {"gadapt": {"A": 0.6167328086419753, "cvar90": 0.03003950524796759},
                    "gadapt_hyb": {"A": 0.7196330246913581, "cvar90": 0.011916067967877472},
                    "ipop": {"A": 0.7629837345679013}}},
        "contrasts": {
            "dA_rot(H-M)": {"estimate": 0.10290021604938274},
            "0.8*CVaR_rot(M)-CVaR_rot(H)": {"estimate": 0.0121155362304966},
            "dA_nonrot(H-M)": {"estimate": 0.06534754629629633},
            "1.5*CVaR_nonrot(M)-CVaR_nonrot(H)": {
                "estimate": -0.0006964276168909891,
                "lower": -0.0011091038824615844,
                "upper": -0.00028375135132039395},
            "dA_rot(H-IPOP)": {"estimate": -0.04335070987654325}}},
    "A": {"contribution_supported": True, "aggregate_by_variant": {
        "orig": {"H": {"A": 0.7628009670781891, "cvar90": 0.004771194868098625},
                 "R": {"A": 0.5875884053497943, "cvar90": 0.01836711821000868}},
        "shift": {"H": {"A": 0.7707763580246916, "cvar90": 0.004320262140456046},
                  "R": {"A": 0.5902525, "cvar90": 0.017555117034079304}},
        "rot": {"H": {"A": 0.7196330246913581, "cvar90": 0.011916067967877472},
                "R": {"A": 0.5883776028806583, "cvar90": 0.017426233488765888}}},
        "estimates": [0.13125542181069957, 0.17786820987654323,
                      0.005510165520888415, 0.013415389117766654]},
    "I": {"H64c": "undecided", "H64d": "opposite", "CVaR_G": 0.29725831682237963},
    "I2": {"H64h1": "undecided", "H64h2": "opposite", "aggregate": {
        "gadapt": {"P": 0.7458333333333333, "cvar90": 0.29725831682237963},
        "gadapt_hyb": {"P": 0.7416666666666667, "cvar90": 0.3771500251324287},
        "ipop": {"P": 0.7708333333333333, "cvar90": 0.25184326402003326}},
        "contrasts": {
            "CVaR(M)-CVaR(H)": {"estimate": -0.07989170831004905},
            "P(H)-P(M)": {"estimate": -0.004166666666666652},
            "CVaR(IPOP)-CVaR(H)": {"estimate": -0.12530676111239542,
                 "lower": -0.25022390683283424, "upper": -0.00038961539195656036},
            "P(H)-P(IPOP)": {"estimate": -0.029166666666666563,
                 "lower": -0.06427941895198026, "upper": 0.005946085618647137}}}
}


def make_ledger():
    calculated = arithmetic_checks(SRC)
    return {"schema": "I65_I64_GITHUB_EXTRACTED_SEVEN_ANALYSIS_ARITHMETIC_V1",
            "date": "2026-11-02", "repository": "owlCoder/gadapt",
            "pinned_commit": PINNED_HEAD,
            "source_level": "Selected scalar fields independently decompressed from seven original gzip analyses using GitHub connector; formulas evaluated with fresh Python implementation",
            "not_done": ["Full local clone unavailable", "Raw optimizer stochastic runs NOT_RECOMPUTED", "Original bootstrap resampling NOT_RECOMPUTED", "No new COCO / OPF / PF / optimizer calls", "Supervisor originality decision UNSIGNED"],
            "verified_blob_ids": {k: {"path": "research/results/" + v[0], "blob_sha": v[1]}
                                  for k, v in ARCHIVES.items()},
            "method": "Snapshot contains only selected archived fields, not a copy of the seven full analysis artifacts",
            **calculated}

if __name__ == "__main__":
    out = Path(__file__).with_name("I65_I64_GITHUB_SEVEN_ANALYSIS_RECHECK_2026-11-02.json")
    out.write_text(json.dumps(make_ledger(), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(f"Wrote {out} ({make_ledger()['passed']}/{make_ledger()['total']} PASS)")
