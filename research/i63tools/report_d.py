"""Renders ITERATION63D_REPORT_SR.md from results/iteration63d/analysis.json.gz (DESCRIPTIVE; not confirmatory)."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "results", "iteration63d")
a = json.load(gzip.open(os.path.join(OUT, "analysis.json.gz"), "rt")); h = a["H63_descriptive"]
L = []; w = L.append
w("# ITERATION63-D: deskriptivna ekstenzija I63 (NEPOTVRDNO) — izveštaj (generisan iz arhive)\n")
w("**Status: DESKRIPTIVNO.** I63 je stao na konačnom STOP-u u fazi snage (kalibracija lažne ekvivalencije na granicama ±0,05 nije dostižna ni za test tačne veličine 5%; vidi `ITERATION63_REPORT_SR.md`). Ovde je izvršen isti zamrznuti test dizajn (roster, normalizatori, FX-T vektor, n iz I63 skrininga, estimand W/θ₆₃, bootstrap) u novom direktorijumu, bez zaključka o H56a/H63 i bez zamene I63. Izveštava se procena sa intervalima.\n")
w(f"n po ćeliji = {a['n']}. θ₆₃ = {h['estimate']:.4f}; 95% CI [{h['ci95'][0]:.4f}, {h['ci95'][1]:.4f}]; 90% CI [{h['ci90'][0]:.4f}, {h['ci90'][1]:.4f}].\n")
w(f"Znak (donja 95% granica > 0): {h['positive']}; suprotan (gornja < 0): {h['negative']}; unutar (−0,05; 0,05) na 90% (informativno): {h['equivalent']}. Srednje po mreži: {a['network_means']}; izostavljanje jedne mreže: {a['leave_one_network_out']}.\n")
w("| ćelija | n | srednje d | W(FR) | W(SP) | izv. FR AD-N | izv. FR FX-T | izv. SP AD-N | izv. SP FX-T |\n|---|---|---|---|---|---|---|---|---|")
for k, v in sorted(a["descriptive"].items()):
    w(f"| {k} | {v['n']} | {v['d_mean']:.3f} | {v['W|FR']:.3f} | {v['W|SP']:.3f} | {v['FR|AD-N']['feasible']:.2f} | {v['FR|FX-T']['feasible']:.2f} | {v['SP|AD-N']['feasible']:.2f} | {v['SP|FX-T']['feasible']:.2f} |")
w("\n## Ograničenja\nNepotvrdno (I63 STOP); topologije ponovo korišćene; B izabran posle uvida u I61 pilot; kontrast uključuje zasebno podešavanje FX-T po CHT-u; ne identifikuje numerički mehanizam adaptacije.")
open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "research", "ITERATION63D_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
