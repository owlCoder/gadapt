"""Renders ITERATION64_E4_REPORT_SR.md from results/iteration64_e4/analysis.json.gz."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "results", "iteration64_e4")
a = json.load(gzip.open(os.path.join(OUT, "analysis.json.gz"), "rt"))
L = []; w = L.append
w("# ITERATION64-E4: kompenzaciona mutacija (opt-in `compensatory_mutation`) sa kontrolama — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_E4_SPEC.md](ITERATION64_E4_SPEC.md) (zamrznuta `226c757`, dopuna A1 `6368959`). Uparivanje sa arhiviranim E zapisima po ključu (ćelija, seme); 63 ćelije × 100 semena, 12.000 stvarnih poziva.\n")
w(f"## 1. Ishod hipoteza (jedna simultana porodica od pet kontrasta, α = {a['alpha']}, t* = {a['tstar']:.3f}, {a['bootstrap']} ponavljanja)\n")
w(f"- **H64k1** (zatvaranje jaza prema GAdapt-M pod rotacijom): **{a['H64k1']}**\n- **H64k2** (tolerisana šteta na orig+shift): **{a['H64k2']}**\n- **H64k3** (gated bolji od kontrole sa permutovanim partnerom pod rotacijom): **{a['H64k3']}**\n- **H64k4** (gated bolji od Bouter-stil resample kontrole): **{a['H64k4']}**\n- **H64k5** (neinferiornost prema IPOP-u, margina 0,05): **{a['H64k5']}**\n- jezgro (k1–k4) podržano: **{a['supported_core']}**; C_rot(GAdapt-M) = {a['CVaR_rot_M']:.4f}\n")
w("| kontrast | procena | donja | gornja |\n|---|---|---|---|")
for k, v in a["contrasts"].items():
    w(f"| {k} | {v['estimate']:.4g} | {v['lower']:.4g} | {v['upper']:.4g} |")
w("\n## 2. Agregati po varijanti (težine: funkcije jednake, dimenzije jednake unutar funkcije; „medijana jaza“ = ponderisani prosek ćelijskih medijana normalizovanog jaza; CVaR = ponderisani prosek ćelijskih CVaR₀,₉(L))\n")
for var, d in a["aggregate_by_variant"].items():
    w(f"**{var}**\n\n| konfiguracija | A | CVaR₀,₉ | medijana jaza |\n|---|---|---|---|")
    for c, v in d.items():
        w(f"| {c} | {v['A']:.4f} | {v['cvar90']:.4f} | {v['median_gap']:.3g} |")
    w("")
w("## 3. Tumačenje (post hoc, oprezno)\nMali dobitak efikasnosti prema GAdapt-M pod rotacijom (ΔA ≈ +0,014) nije razlučiv od kontrole sa slučajnim partnerom ni od Bouter-stil resample kontrole (intervali obuhvataju nulu), pa se NE može pripisati iskorišćavanju elitnih korelacija; rep raspodele se ne smanjuje za traženih 20%. Jaz prema IPOP-u ostaje velik. Opcija je dokumentovana i podrazumevano isključena, bez preporuke. Kontrola `permuted` meri razliku kompletnih režima (Codex 092); `resample` je ispravljen i ponovljen (dopuna A1); algoritamska originalnost i industrijska korist nisu ustanovljene.\n")
open(os.path.join(os.path.dirname(HERE), "ITERATION64_E4_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
