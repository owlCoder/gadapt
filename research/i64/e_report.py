"""Renders research/ITERATION64_E_REPORT_SR.md from results/iteration64_e/analysis_v2.json.gz (no hand-picked numbers)."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("E_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_e"))
load = lambda n: json.load(gzip.open(os.path.join(OUT, n + ".json.gz"), "rt"))
a, fr = load("analysis_v2"), load("freeze")
CFG = ["gadapt", "gadapt_preset", "pygad_random", "pygad_adaptive", "de", "cma", "ipop", "bipop", "es11"]
L = []; w = L.append
w("# ITERATION64-E: pomereno/rotirano, jednak budžet od 12.000 stvarnih poziva, jači konkurenti — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_E_SPEC.md](ITERATION64_E_SPEC.md) (zamrznuta `c015730`, dopuna A1 pre uvida u rezultate). Analiza: `research/i64/e_analysis.py` (izlaz `analysis_v2`). Sirovi izlazi: `research/results/iteration64_e/`.")
w(f"63 ćelije × 9 konfiguracija × 100 semena. Izabrani parametri (razvoj): {fr['params']}.\n")
w(f"## 1. H64a (GAdapt-M naspram osam konkurenata, 16 simultanih kontrasta, α = {a['alpha']}): **{a['verdict']}**\n")
w(f"flags: {a['flags']}; t* = {a['tstar']:.3f}; bootstrap {a['bootstrap']}.\n")
w("| konkurent | ΔA (GAdapt − konk.) | donja | gornja | ΔM (konk. − GAdapt) | donja | gornja |\n|---|---|---|---|---|---|---|")
for c in CFG[1:]:
    x, y = a["contrasts"][f"dA|{c}"], a["contrasts"][f"dM|{c}"]
    w(f"| {c} | {x['estimate']:.4g} | {x['lower']:.4g} | {x['upper']:.4g} | {y['estimate']:.4g} | {y['lower']:.4g} | {y['upper']:.4g} |")
w("\nΔA > 0: GAdapt efikasniji (veća ECDF-površina do 12.000 poziva). ΔM > 0: GAdapt tačniji (niža ponderisana medijana normalizovanog jaza). Simultani intervali: maksimum standardizovanog odstupanja.\n")
w("## 2. Agregati (ponderisano: 1/9 po funkciji, jednako po dimenzijama i varijantama)\n")
w("| konfiguracija | ECDF površina A | CVaR₀,₉(L) | medijana jaza | P(g≤1e−2) | P(g≤1e−4) | P(g≤1e−6) | pokretanja sa L > 0,5 |\n|---|---|---|---|---|---|---|---|")
for c in CFG:
    g = a["aggregate"][c]
    w(f"| {c} | {g['A']:.4f} | {g['cvar90']:.4f} | {g['median_gap']:.3g} | {g['reach'][0]:.3f} | {g['reach'][1]:.3f} | {g['reach'][2]:.3f} | {a['heavy_failures_L_gt_0_5'][c]} |")
h = a["h64b"]
w("\n## 3. H64b (preset naspram GAdapt-M)\n")
w(f"R₀ (CVaR GAdapt-M) = {h['R0']:.4f}; R_preset = {h['Rpreset']:.4f}; tačkaste vrednosti [0,8·R₀ − R_preset, Δreach(1e−2), Δreach(1e−4), Δreach(1e−6)] = {[round(x,4) for x in h['point']]}; donje simultane granice = {[round(x,4) for x in h['lower']]}; t* = {h['tstar']:.3f}; flags {h['flags']}.")
w(f"**H64b podržana: {h['supported']}** (zahteva R₀ > 0, donju granicu 0,8·R₀ − R_preset ≥ 0 i donje granice razlika dostizanja ≥ −0,05).\n")
w("## 4. Po varijanti i funkciji (opisno: ECDF površina A, medijana jaza; ćelije ponderisane jednako u okviru grupe)\n")
import collections
grp = collections.defaultdict(lambda: collections.defaultdict(list))
for k, v in a["per_cell"].items():
    f, d, var, c = k.split("|"); grp[(var, c)]["A"].append(v["A"]); grp[(var, c)]["g"].append(v["median_gap"])
import statistics as st
w("| varijanta | " + " | ".join(CFG) + " |\n|---|" + "---|" * len(CFG))
for var in ("orig", "shift", "rot"):
    w(f"| {var} (A / med. gap) | " + " | ".join(f"{st.mean(grp[(var,c)]['A']):.3f} / {st.mean(grp[(var,c)]['g']):.2g}" for c in CFG) + " |")
w("\n## 5. Ograničenja (unapred)\nKlasične funkcije (nisu CEC/BBOB); optimum u domenu; 100 semena (retki otkazi nisu pouzdano procenljivi; CVaR-bootstrap nije gladak kad ~10% pokretanja otkaže — zato je prikazan broj pokretanja sa L > 0,5); L-SHADE/jDE izostavljeni;"
  " CMA bez margine; GAdapt/PyGAD/DE u izvornom domenu a CMA/ES na jediničnoj kocki; GAdapt iz repozitorijuma (0.5.2+), ne PyPI 0.5.0; razvoj parametara na rotiranim ćelijama iz drugih semena.")
open(os.path.join(os.path.dirname(HERE), "ITERATION64_E_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
