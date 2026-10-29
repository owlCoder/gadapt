"""Renders ITERATION64_E2_REPORT_SR.md from results/iteration64_e2/analysis.json.gz."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "results", "iteration64_e2")
a = json.load(gzip.open(os.path.join(OUT, "analysis.json.gz"), "rt"))
L = []; w = L.append
w("# ITERATION64-E2: diferencijalni krosover pod rotacijom — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_E2_SPEC.md](ITERATION64_E2_SPEC.md) (zamrznuta `aeff985`). Uparivanje sa arhiviranim E zapisima po ključu (ćelija, seme); 63 ćelije × 100 semena, 12.000 stvarnih poziva.\n")
w(f"## 1. Ishod hipoteza (jedna simultana porodica od pet kontrasta, α = {a['alpha']}, t* = {a['tstar']:.3f}, {a['bootstrap']} ponavljanja)\n")
w(f"- **H64e1** (zatvaranje jaza pod rotacijom prema GAdapt-M): **{a['H64e1']}**\n- **H64e2** (tolerisana šteta na orig+shift): **{a['H64e2']}**\n- **H64e3** (neinferiornost prema IPOP-u, margina 0,05): **{a['H64e3']}**\n- ukupno podržano: **{a['supported']}**; C_rot(GAdapt-M) = {a['CVaR_rot_M']:.4f}\n")
w("| kontrast | procena | donja | gornja |\n|---|---|---|---|")
for k, v in a["contrasts"].items():
    w(f"| {k} | {v['estimate']:.4g} | {v['lower']:.4g} | {v['upper']:.4g} |")
w("\n## 2. Agregati po varijanti (težine: funkcije jednake, dimenzije jednake unutar funkcije; „medijana jaza“ = ponderisani prosek ćelijskih medijana normalizovanog jaza; CVaR = ponderisani prosek ćelijskih CVaR₀,₉(L))\n")
for var, d in a["aggregate_by_variant"].items():
    w(f"**{var}**\n\n| konfiguracija | A | CVaR₀,₉ | medijana jaza |\n|---|---|---|---|")
    for c, v in d.items():
        w(f"| {c} | {v['A']:.4f} | {v['cvar90']:.4f} | {v['median_gap']:.3g} |")
    w("")
w("## 3. Zaključak\nOpt-in diferencijalni krosover **ne zatvara** rotacijski jaz GAdapt-a: A je niži pod rotacijom i na objedinjenom orig+shift podskupu (ΔA < 0, simultani intervali ispod nule); pojedinačne varijante opisno prate isti smer; rep raspodele pod rotacijom je lošiji. Opcija ostaje u biblioteci kao dokumentovana, podrazumevano isključena, BEZ preporuke. "
  "Rezultat je preregistrovan i negativan; nije ponovljen sa drugim F. Uzrok neuspeha nije izolovan (operator je rotaciono ekvivarijantan samo kao neograničen korak; mutacioni operatori ostaju koordinatni).\n")
open(os.path.join(os.path.dirname(HERE), "ITERATION64_E2_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
