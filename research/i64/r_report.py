"""Renders ITERATION64_R_REPORT_SR.md from results/iteration64_r/analysis.json.gz (generated; no hand-written numbers)."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "results", "iteration64_r")
a = json.load(gzip.open(os.path.join(RES, "analysis.json.gz"), "rt"))
L = []; w = L.append
w("# ITERATION64-R: izolovanje ortogonalne transformacije (isti pomeraj) — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_R_SPEC.md](ITERATION64_R_SPEC.md). Ćelija `rotm` = Q iz E `rot` i o iz E `shift`; 21 par funkcija/dimenzija, 100 semena, 12.000 stvarnih poziva, GAdapt-M i IPOP-CMA-ES. Q je Haar-ortogonalna (moguće sa refleksijom), pa se ne govori o čistoj rotaciji.\n")
if a.get("blocked"):
    w("**BLOKIRANO**: degenerisana standardna greška bootstrap-a; hipoteze se ne ocenjuju.")
else:
    w(f"Simultani interval (4 kontrasta, α = {a['alpha']}, {a['boot']} ponavljanja, seme {a['boot_seed']}), t* = {a['tstar']:.4f}.\n")
    w("| kontrast | procena | donja | gornja |\n|---|---|---|---|")
    for n, e, l, u in zip(a["names"], a["estimates"], a["lower"], a["upper"]):
        w(f"| {n} | {e:.4f} | {l:.4f} | {u:.4f} |")
    w(f"\n- **H64r1** (agregatni efekat zamene pomeraja u ±0,03, uslovno na 21 fiksni Q): **{a['H64r1']}**\n- **H64r2** (pad A GAdapt-M zbog Q najmanje 0,05): **{a['H64r2']}**\n- **H64r3** (Q umanjuje A GAdapt-M bar 0,05 više nego IPOP-a, uz H64r2): **{a['H64r3']}**\n")
    w("Agregati A (ponderisani):\n\n| varijanta | GAdapt-M | IPOP |\n|---|---|---|")
    for v in ("shift", "rot", "rotm"):
        w(f"| {v} | {a['aggregates'][v + '|gadapt']:.4f} | {a['aggregates'][v + '|ipop']:.4f} |")
    w("\nPo parovima (A, GAdapt-M / IPOP):\n\n| par | shift | rot | rotm |\n|---|---|---|---|")
    for k, v in a["per_pair"].items():
        w(f"| {k} | {v['shift|gadapt']:.3f} / {v['shift|ipop']:.3f} | {v['rot|gadapt']:.3f} / {v['rot|ipop']:.3f} | {v['rotm|gadapt']:.3f} / {v['rotm|ipop']:.3f} |")
w("\n## Ograničenja\nBootstrap obuhvata samo varijaciju semena, ne izbor funkcija, dimenzija, Q ili o; nalaz važi za 21 ćeliju i dve konfiguracije i ne generalizuje se na proizvoljne Haar transformacije. Ne tvrdi se mehanizam. Težine: d = 2 ćelije nose 5/9 ukupne težine.")
open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "research", "ITERATION64_R_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
