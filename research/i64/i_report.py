"""Renders ITERATION64_I_REPORT_SR.md from results/iteration64_i/analysis.json.gz (no hand-picked numbers)."""
import gzip, json, os, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("I_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_i"))
a = json.load(gzip.open(os.path.join(OUT, "analysis.json.gz"), "rt"))
CFG = ["gadapt", "gadapt_preset", "pygad_random", "pygad_adaptive", "de", "cma", "ipop", "bipop", "es11"]
L = []; w = L.append
w("# ITERATION64-I: diskretni ORPD pod jednakim budžetom stvarnih proračuna toka snage — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_I_SPEC.md](ITERATION64_I_SPEC.md) (zamrznuta `a17f7dc`, dopune I-A1/I-A2). Sirovi izlazi: `research/results/iteration64_i/`. 8 ćelija (case30 ×2, case39 ×3, case24_ieee_rts ×3), R = 17, 30 semena, B = 12.000 PF.\n")
w(f"## 1. Odluke\n\n- **H64c** (GAdapt-M nije lošiji u izvodljivosti i ima niži CVaR od ≥ 4 konkurenta): **{a['H64c']}**\n- **H64d** (preset): **{a['H64d']}**\n- blokirano: {a['blocked']}; t* = {a['tstar']}; α aktivnih = {a.get('alpha_active')}, rezervni = {a.get('alpha_fallback')}; degenerisani kontrasti: {a.get('degenerate_contrasts')}\n")
w("| kontrast | procena | donja | gornja |\n|---|---|---|---|")
for k, v in a["contrasts"].items():
    w(f"| {k} | {v['estimate']:.4g} | {v['lower']:.4g} | {v['upper']:.4g} |")
w("\nP(c) − P(G) > 0 šteti GAdapt-u; CVaR(c) − CVaR(G) > 0 koristi GAdapt-u.\n")
w("## 2. Agregati po konfiguraciji (ćelije jednako ponderisane)\n")
for B_ in ("12000", "3000"):
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    for k, v in a["descriptive"].items():
        net, j, c, b = k.split("|")
        if b == B_:
            agg[c]["P"].append(v["P_feasible"]); agg[c]["cv"].append(v["cvar90"])
            mg = v["median_G"]; agg[c]["g"].append(float("inf") if mg == "inf" else mg)
    w(f"**B = {B_}**\n\n| konfiguracija | P(izvodljivo) | CVaR₀,₉(L) | srednja ćelijska medijana G |\n|---|---|---|---|")
    for c in CFG:
        w(f"| {c} | {st.mean(agg[c]['P']):.3f} | {st.mean(agg[c]['cv']):.4f} | {st.mean(agg[c]['g']):.4g} |")
    w("")
w("## 3. Po ćeliji (B = 12.000): P(izvodljivo) / medijana G\n")
cells = sorted({tuple(k.split("|")[:2]) for k in a["descriptive"]})
w("| ćelija | " + " | ".join(CFG) + " |\n|---|" + "---|" * len(CFG))
for net, j in cells:
    row = []
    for c in CFG:
        v = a["descriptive"][f"{net}|{j}|{c}|12000"]; mg = v["median_G"]
        row.append(f"{v['P_feasible']:.2f} / {mg if mg == 'inf' else format(mg, '.3g')}")
    w(f"| {net} {j} | " + " | ".join(row) + " |")
w("\n## 4. Ograničenja\nDiskretni ORPD sa tri mreže i osam ćelija; 30 semena (retki otkazi nisu pouzdano procenljivi; CVaR je prosek 3 najgora od 30); CMA porodica kontinualna sa zaokruživanjem (bez margine); I57 (CMAwM) samo opisni kontekst; r je kontinualni OPF, ne optimum diskretnog problema; svedok na 3.000 poziva nije nezavisno proveren. Nema tvrdnje o industrijskoj spremnosti.")
open(os.path.join(os.path.dirname(HERE), "ITERATION64_I_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
