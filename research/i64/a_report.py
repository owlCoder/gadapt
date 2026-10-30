"""Renders ITERATION64_A_REPORT_SR.md from results/iteration64_a/analysis.json.gz (generated; no hand-written numbers)."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "results", "iteration64_a")
a = json.load(gzip.open(os.path.join(RES, "analysis.json.gz"), "rt"))
L = []; w = L.append
w("# ITERATION64-A: ablacija hibrida GAdapt → CMA-ES (zamena GAdapt prve faze slučajnim uzorkovanjem) — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_A_SPEC.md](ITERATION64_A_SPEC.md). H = arhivirani E3 hibrid (GAdapt-M 30% → CMA); R = slučajno uzorkovanje 30% → isti CMA. 63 ćelije × 100 semena, 12.000 stvarnih poziva, upareno po (ćelija, seme).\n")
if a.get("blocked"):
    w("**BLOKIRANO**: nekonačne vrednosti ili degenerisana standardna greška; hipoteze se ne ocenjuju.")
else:
    w(f"Simultani interval (4 kontrasta, α = {a['alpha']}, {a['boot']} ponavljanja, seme {a['boot_seed']}), t* = {a['tstar']:.4f}.\n")
    w("| kontrast | procena | donja | gornja |\n|---|---|---|---|")
    for n, e, l, u in zip(a["names"], a["estimates"], a["lower"], a["upper"]):
        w(f"| {n} | {e:.4f} | {l:.4f} | {u:.4f} |")
    w(f"\n- **H64a1** (efekat zamene GAdapt faze na A pod rotacijom ≥ 0,02): **{a['H64a1']}**\n- **H64a2** (isto na orig+shift): **{a['H64a2']}**\n- ukupno `contribution_supported`: **{a['contribution_supported']}**\n")
    w("Agregati po varijanti:\n\n| varijanta | konf. | A | CVaR₀,₉ | medijana jaza |\n|---|---|---|---|---|")
    for v, d in a["aggregate_by_variant"].items():
        for c, x in d.items():
            w(f"| {v} | {c} | {x['A']:.4f} | {x['cvar90']:.4f} | {x['median_gap']:.5f} |")
w("\n## Ograničenja\nProcenjuje se efekat zamene prve faze (30%) uniformnim uzorkovanjem u ovom fiksiranom hibridu; ne tvrdi se da GAdapt samostalno nadmašuje slučajno uzorkovanje, mehanizam, niti važenje za druge udele, budžete, σ₀ ili CMA varijante. Bootstrap obuhvata samo varijaciju algoritamskih semena.")
open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "research", "ITERATION64_A_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
