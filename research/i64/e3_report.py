"""Renders ITERATION64_E3_REPORT_SR.md from results/iteration64_e3/analysis.json.gz."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "results", "iteration64_e3")
a = json.load(gzip.open(os.path.join(OUT, "analysis.json.gz"), "rt"))
L = []; w = L.append
w("# ITERATION64-E3: hibrid GAdapt→CMA (globalna pretraga + lokalno doterivanje) — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_E3_SPEC.md](ITERATION64_E3_SPEC.md) (zamrznuta `f228044`). Uparivanje sa arhiviranim E zapisima po ključu (ćelija, seme); 63 ćelije × 100 semena, 12.000 stvarnih poziva.\n")
w(f"## 1. Ishod hipoteza (jedna simultana porodica od pet kontrasta, α = {a['alpha']}, t* = {a['tstar']:.3f}, {a['bootstrap']} ponavljanja)\n")
w(f"- **H64g1** (zatvaranje jaza pod rotacijom prema GAdapt-M): **{a['H64g1']}**\n- **H64g2** (tolerisana šteta na orig+shift): **{a['H64g2']}**\n- **H64g3** (neinferiornost prema IPOP-u, margina 0,05): **{a['H64g3']}**\n- ukupno podržano: **{a['supported']}**; C_rot(GAdapt-M) = {a['CVaR_rot_M']:.4f}\n")
w("| kontrast | procena | donja | gornja |\n|---|---|---|---|")
for k, v in a["contrasts"].items():
    w(f"| {k} | {v['estimate']:.4g} | {v['lower']:.4g} | {v['upper']:.4g} |")
w("\n## 2. Agregati po varijanti (težine: funkcije jednake, dimenzije jednake unutar funkcije; „medijana jaza“ = ponderisani prosek ćelijskih medijana normalizovanog jaza; CVaR = ponderisani prosek ćelijskih CVaR₀,₉(L))\n")
for var, d in a["aggregate_by_variant"].items():
    w(f"**{var}**\n\n| konfiguracija | A | CVaR₀,₉ | medijana jaza |\n|---|---|---|---|")
    for c, v in d.items():
        w(f"| {c} | {v['A']:.4f} | {v['cvar90']:.4f} | {v['median_gap']:.3g} |")
    w("")
w("## 2b. Prosek po tri varijante (jednaka težina varijanti; opisno)\n\n| konfiguracija | A | CVaR₀,₉ | medijana jaza |\n|---|---|---|---|")
for c in ("gadapt", "gadapt_hyb", "ipop", "cma", "bipop", "de"):
    vs = [a["aggregate_by_variant"][v][c] for v in ("orig", "shift", "rot")]
    w(f"| {c} | {sum(x['A'] for x in vs)/3:.4f} | {sum(x['cvar90'] for x in vs)/3:.4f} | {sum(x['median_gap'] for x in vs)/3:.3g} |")
w("\n## 3. Napomena o tumačenju\nHibrid NIJE GAdapt sam: poslednjih 70% budžeta troši CMA-ES. Rezultat se zato čita kao empirijska provera hibrida (globalna pretraga, pa lokalno doterivanje) na klasičnim funkcijama, ne kao svojstvo GAdapt-a i ne kao dokaz industrijske primenljivosti. Nema tvrdnje o novoj metodi (hibridni algoritmi su poznati). Zamrznuta pravila odluke daju mešan ishod: pogledati hipoteze u odeljku 1. Post hoc, opisno (ista arhiva, ne dodatna hipoteza): hibrid ima viši orig/shift CVaR od GAdapt-M i preseta, a niži od prikazanih CMA varijanti; pod rotacijom A zaostaje za IPOP-om (neinferiornost nije potvrđena). Bez ablacija nije utvrđen zaseban doprinos GAdapt i CMA faze.\n")
open(os.path.join(os.path.dirname(HERE), "ITERATION64_E3_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
