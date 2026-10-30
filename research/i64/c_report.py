"""Renders ITERATION64_C_REPORT_SR.md from results/iteration64_c/analysis.json.gz (generated; no hand-written numbers)."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "results", "iteration64_c")
a = json.load(gzip.open(os.path.join(RES, "analysis.json.gz"), "rt"))
L = []; w = L.append
w("# ITERATION64-C: koeficijentni potpis gubitka GAdapt-a pod ortogonalnom transformacijom — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_C_SPEC.md](ITERATION64_C_SPEC.md). 21 par (funkcija, dimenzija), `shift` naspram `rotm` (isti pomeraj, Q iz E `rot`), GAdapt-M, prvih 1.200 poziva, 30 semena; koeficijenti kolonske raznovrsnosti (log-relative) snimani pasivno po generaciji.\n")
if a.get("blocked"):
    w("**BLOKIRANO**: nedovoljno validnih bootstrap uzoraka ili degenerisane statistike; hipoteze se ne ocenjuju.")
else:
    w(f"- Ponderisana srednja Δ (pad CV koeficijenata, shift − rotm): **{a['wmean_delta']:.4f}** [{a['lo_wmean']:.4f}; {a['hi_wmean']:.4f}] (Bonferroni α/3 = {a['alpha']/3:.4f}); Δ_k > 0 u {a['positive_pairs']} od {a['nonzero_pairs']} nenultih parova (binomni p = {a['p_binomial']:.4f})")
    w(f"- Spearman ρ(Δ_k, ΔA_k) = **{a['spearman_delta_dA']:.3f}** [{a['lo_rd']:.3f}; {a['hi_rd']:.3f}]; osnovna linija ρ(E_k, ΔA_k) = {a['spearman_E_dA']:.3f}; razlika = {a['diff']:.3f} [{a['lo_dd']:.3f}; {a['hi_dd']:.3f}]")
    w(f"\n- **H64c1** (homogenizacija koeficijenata): **{a['H64c1']}**\n- **H64c2** (asocijacija sa padom A): **{a['H64c2']}**\n- **H64c3** (jača marginalna rang-asocijacija od osnovne linije): **{a['H64c3']}**\n- predviđeni koeficijentni potpis podržan: **{a['signature_supported']}**; jača marginalna asocijacija od osnovne linije: **{a['stronger_marginal_than_baseline']}**\n")
    w("Spearman ρ(Δ_k, ΔA_k) uz izostavljanje jedne funkcije (opisno):\n\n| izostavljena funkcija | ρ |\n|---|---|")
    for n, r in a["lofo_spearman"].items():
        w(f"| {n} | {r:.3f} |")
    w("\nPo parovima:\n\n| par | Δ_k | ΔA_k | E_k |\n|---|---|---|---|")
    for p, d, da, e in zip(a["pairs"], a["delta_k"], a["dA_k"], a["E_k"]):
        w(f"| {p} | {d:.4f} | {da:.4f} | {e:.4f} |")
w("\n## Ograničenja\nKorelaciona studija na 21 fiksnu ćeliju iz 9 funkcija; meri se samo log-relative koeficijent (ne dijagonala kovarijanse); nema intervencije ni medijacije, pa se ne tvrdi uzrok; ne tvrdi se inkrementalna prediktivna vrednost; važi za GAdapt-M, native domen, b = 1.200 i ove ćelije; ne važi za diskretne probleme (ORPD se ne rotira). Bootstrap obuhvata semena i izbor funkcija, ne izbor Q i pomeraja.")
open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "research", "ITERATION64_C_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
