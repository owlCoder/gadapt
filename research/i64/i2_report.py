"""Renders ITERATION64_I2_REPORT_SR.md from results/iteration64_i2/analysis.json.gz."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "results", "iteration64_i2")
a = json.load(gzip.open(os.path.join(OUT, "analysis.json.gz"), "rt"))
L = []; w = L.append
w("# ITERATION64-I2: hibrid GAdapt → CMA-ES na diskretnom ORPD-u — izveštaj (generisan iz arhive)\n")
w("Specifikacija: [ITERATION64_I2_SPEC.md](ITERATION64_I2_SPEC.md) (zamrznuta `e0c0ed1` pre uvida u I64-I). Uparivanje sa I64-I zapisima po (ćelija, seme); 8 ćelija × 30 semena, 12.000 stvarnih PF.\n")
w(f"## 1. Odluke (jedna simultana porodica od četiri kontrasta, α = {a['alpha']}, t* = {a['tstar']:.3f}, {a['bootstrap']} ponavljanja)\n")
w(f"- **H64h1** (hibrid bolji od GAdapt-M u repu bez gubitka izvodljivosti): **{a['H64h1']}**\n- **H64h2** (hibrid bolji od IPOP u repu bez gubitka izvodljivosti): **{a['H64h2']}**\n")
w("| kontrast | procena | donja | gornja |\n|---|---|---|---|")
for k, v in a["contrasts"].items():
    w(f"| {k} | {v['estimate']:.4g} | {v['lower']:.4g} | {v['upper']:.4g} |")
w("\nCVaR(ref) − CVaR(H) > 0 koristi hibridu; P(H) − P(ref) ≥ −0,05 znači da izvodljivost nije lošija za više od 5 p.p.\n")
w("## 2. Agregati (ćelije jednako ponderisane)\n\n| konfiguracija | P(izvodljivo) | CVaR₀,₉(L) |\n|---|---|---|")
for c, v in a["aggregate"].items():
    w(f"| {c} | {v['P']:.3f} | {v['cvar90']:.4f} |")
w("\n## 3. Tumačenje\nPrednost hibrida iz E3 (sintetičke funkcije) se NE prenosi na ovaj ORPD skup: hibrid nije dokazano bolji od GAdapt-M, a rep je lošiji od IPOP-a (H64h2 suprotno). Zaseban doprinos GAdapt faze nije identifikovan. Rezultat važi za osam ćelija i 30 semena; nema tvrdnje o industrijskoj spremnosti.\n")
open(os.path.join(os.path.dirname(HERE), "ITERATION64_I2_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
