# ITERATION64-I2: hibrid GAdapt → CMA-ES na diskretnom ORPD-u — izveštaj (generisan iz arhive)

Specifikacija: [ITERATION64_I2_SPEC.md](ITERATION64_I2_SPEC.md) (zamrznuta `e0c0ed1` pre uvida u I64-I). Uparivanje sa I64-I zapisima po (ćelija, seme); 8 ćelija × 30 semena, 12.000 stvarnih PF.

## 1. Odluke (jedna simultana porodica od četiri kontrasta, α = 0.05, t* = 3.413, 20000 ponavljanja)

- **H64h1** (hibrid bolji od GAdapt-M u repu bez gubitka izvodljivosti): **undecided**
- **H64h2** (hibrid bolji od IPOP u repu bez gubitka izvodljivosti): **opposite**

| kontrast | procena | donja | gornja |
|---|---|---|---|
| CVaR(M)-CVaR(H) | -0.07989 | -0.2656 | 0.1058 |
| P(H)-P(M) | -0.004167 | -0.03548 | 0.02715 |
| CVaR(IPOP)-CVaR(H) | -0.1253 | -0.2502 | -0.0003896 |
| P(H)-P(IPOP) | -0.02917 | -0.06428 | 0.005946 |

CVaR(ref) − CVaR(H) > 0 koristi hibridu; P(H) − P(ref) ≥ −0,05 znači da izvodljivost nije lošija za više od 5 p.p.

## 2. Agregati (ćelije jednako ponderisane)

| konfiguracija | P(izvodljivo) | CVaR₀,₉(L) |
|---|---|---|
| gadapt | 0.746 | 0.2973 |
| gadapt_hyb | 0.742 | 0.3772 |
| ipop | 0.771 | 0.2518 |

## 3. Tumačenje
Prednost hibrida iz E3 (sintetičke funkcije) nije potvrđena na ovom ORPD skupu: hibrid nije dokazano bolji od GAdapt-M (H64h1 neodlučeno), a njegov rep je lošiji od IPOP-ovog (H64h2 suprotno). Zaseban doprinos GAdapt faze nije identifikovan. Rezultat važi za osam ćelija i 30 semena; nema tvrdnje o industrijskoj spremnosti.

