"""Renders ITERATION64_S0_REPORT_SR.md from results/iteration64_s0/analysis.json.gz and runs.json.gz (no hand-picked numbers)."""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "results", "iteration64_s0")


def load(n):
    with gzip.open(os.path.join(OUT, n + ".json.gz"), "rt") as fh:
        return json.load(fh)


a, runs, gate = load("analysis"), load("runs")["records"], load("gate")
cfg = ["gadapt", "pygad_random", "pygad_adaptive", "de"]
lines = []
w = lines.append
w("# ITERATION64-S0: replikacija mentorovog benchmarka sa stvarnim brojanjem poziva — izveštaj (generisan iz arhive)\n")
w("Protokol: [ITERATION64_PROTOCOL.md](ITERATION64_PROTOCOL.md) (v2, S0 zamrznut pre merenja). Driver: `research/i64/s0_replication.py`. Sirovi izlazi: `research/results/iteration64_s0/`.")
w(f"Pokretanja: {len(runs)} (21 ćelija × 4 konfiguracije × 20 semena, p = 0); gate prošao: {gate['passed']}.\n")
w(f"## 1. Ishod H64a na S0 (mentorova tvrdnja, četiri originalne konfiguracije): **{a['verdict']}**\n")
w(f"supported = {a['supported']}, opposite = {a['opposite']}, kandidati za „izuzetak“ = {a['exception_candidates']}; simultani bootstrap ({a['bootstrap']} ponavljanja), α = {a['alpha']}, t* = {a['tstar']:.3f}.\n")
w("| Kontrast (GAdapt − konkurent za ΔA; konkurent − GAdapt za ΔM) | procena | donja | gornja |\n|---|---|---|---|")
for k, v in a["contrasts"].items():
    w(f"| {k} | {v['estimate']:.4g} | {v['lower']:.4g} | {v['upper']:.4g} |")
w("\nΔA > 0: GAdapt ima veću ECDF-površinu (efikasniji). ΔM > 0: GAdapt ima niži završni medijalni jaz (tačniji). Jaz je normalizovan medijanom slučajnih tačaka (§2).\n")
w("## 2. Agregati po konfiguraciji (težine §2)\n")
w("| konfiguracija | poziva/pokretanju | generacija | ECDF površina A | A (samo „search“ pozivi) | CVaR₀,₉ (L) | medijana jaza |\n|---|---|---|---|---|---|---|")
for c in cfg:
    g = a["aggregate"][c]
    w(f"| {c} | {g['calls_mean']:.0f} | {g['gens_mean']:.1f} | {g['A']:.3f} | {g['A_search_only']:.3f} | {g['cvar90']:.4f} | {g['median_gap']:.3g} |")
w("\n## 3. Generacije nisu jedinica troška (stvarni pozivi po fazama, sva pokretanja)\n")
tot = {}
for r in runs:
    t = tot.setdefault(r["config"], {})
    for ph, n in r["phases"].items():
        t[ph] = t.get(ph, 0) + n
w("| konfiguracija | " + " | ".join(sorted({p for t in tot.values() for p in t})) + " |\n|---|" + "---|" * len({p for t in tot.values() for p in t}))
phases = sorted({p for t in tot.values() for p in t})
for c in cfg:
    w(f"| {c} | " + " | ".join(str(tot[c].get(p, 0)) for p in phases) + " |")
w("\n`best_solution` = ponovna računanja mentorovog callback-a u PyGAD-u; `de_callback` = DE callback; `init_manual` = ručna početna evaluacija PyGAD-a; `gadapt_validation` = all-min/all-max probe.\n")
w("## 4. Opisno po ćelijama\n")
w("| ćelija | konfiguracija | poziva | generacija | medijana jaza | CVaR₀,₉ | P(g≤1e−2) | P(≤1e−4) | P(≤1e−6) |\n|---|---|---|---|---|---|---|---|---|")
for k, v in sorted(a["descriptive"].items()):
    f, d, c = k.split("|")
    w(f"| {f} d={d} | {c} | {v['calls_mean']:.0f} | {v['gens_mean']:.1f} | {v['gap_median']:.3g} | {v['cvar90']:.4f} | {v['reach'][0]:.2f} | {v['reach'][1]:.2f} | {v['reach'][2]:.2f} |")
w("\n## 4b. (POST HOC, opisno) Po ćelijama: ko pobeđuje (mehanički prebrojano iz tabele 4)\n")
cells = sorted({tuple(k.split("|")[:2]) for k in a["descriptive"]})
w("| konkurent | ćelije gde GAdapt ima manju medijanu jaza | ćelije gde konkurent ima manju | jednako | ćelije gde GAdapt ima veći A (srednja ECDF površina) | gde konkurent ima veći A |\n|---|---|---|---|---|---|")
for c in cfg[1:]:
    gw = cw = tie = aw = al = 0
    for f, d in cells:
        g, o = a["descriptive"][f"{f}|{d}|gadapt"], a["descriptive"][f"{f}|{d}|{c}"]
        if g["gap_median"] < o["gap_median"]: gw += 1
        elif g["gap_median"] > o["gap_median"]: cw += 1
        else: tie += 1
        if g["A_mean"] > o["A_mean"]: aw += 1
        elif g["A_mean"] < o["A_mean"]: al += 1
    w(f"| {c} | {gw} | {cw} | {tie} | {aw} | {al} |")
w("\nAgregatna ΔM je ponderisana srednja vrednost medijana NORMALIZOVANOG jaza, pa je dominiraju ćelije sa velikim jazom (multimodalne i 20-dimenzione); prebrojavanje gore pokazuje koliko je pobeda raspoređeno po ćelijama.\n")
w("\n## 5. Ograničenja (unapred)\nJednokorisnički S0 ima 20 semena po ćeliji; zaključak važi za mentorove konfiguracije i funkcije bez rotacije i pomeranja; okruženje GAdapt 0.5.0 (PyPI) i PyGAD 3.5.0. "
  "Mentorova zaokruživanja izlaza (10 decimala) zamenjena su nezaokruženim svedokom. Ovo nije dokaz opšte superiornosti ni industrijske spremnosti.")
open(os.path.join(os.path.dirname(HERE), "ITERATION64_S0_REPORT_SR.md"), "w").write("\n".join(lines) + "\n")
print("written")
