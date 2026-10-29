# ITERATION64-I: diskretni ORPD pod jednakim budžetom stvarnih proračuna toka snage — izveštaj (generisan iz arhive)

Specifikacija: [ITERATION64_I_SPEC.md](ITERATION64_I_SPEC.md) (zamrznuta `a17f7dc`, dopune I-A1/I-A2). Sirovi izlazi: `research/results/iteration64_i/`. 8 ćelija (case30 ×2, case39 ×3, case24_ieee_rts ×3), R = 17, 30 semena, B = 12.000 PF.

## 1. Odluke

- **H64c** (GAdapt-M nije lošiji u izvodljivosti i ima niži CVaR od ≥ 4 konkurenta): **undecided**
- **H64d** (preset): **opposite**
- blokirano: False; t* = 3.1098081557191866; α aktivnih = 0.025, rezervni = 0.025; degenerisani kontrasti: []

| kontrast | procena | donja | gornja |
|---|---|---|---|
| P(gadapt_preset)-P(G) | -0.004167 | -0.01667 | 0.008333 |
| P(pygad_random)-P(G) | -0.07917 | -0.1134 | -0.04497 |
| P(pygad_adaptive)-P(G) | -0.125 | -0.1429 | -0.1071 |
| P(de)-P(G) | -0.1208 | -0.1334 | -0.1082 |
| P(cma)-P(G) | 0.008333 | -0.009631 | 0.0263 |
| P(ipop)-P(G) | 0.025 | -0.004254 | 0.05425 |
| P(bipop)-P(G) | 0.02083 | -0.006552 | 0.04822 |
| P(es11)-P(G) | 0.004167 | -0.02438 | 0.03271 |
| CVaR(gadapt_preset)-CVaR(G) | 0.04224 | -0.06264 | 0.1471 |
| CVaR(pygad_random)-CVaR(G) | 0.1166 | -0.00258 | 0.2357 |
| CVaR(pygad_adaptive)-CVaR(G) | 0.1725 | 0.0129 | 0.332 |
| CVaR(de)-CVaR(G) | 0.09143 | -0.02758 | 0.2104 |
| CVaR(cma)-CVaR(G) | -0.04613 | -0.1651 | 0.07288 |
| CVaR(ipop)-CVaR(G) | -0.04542 | -0.1644 | 0.0736 |
| CVaR(bipop)-CVaR(G) | -0.04396 | -0.163 | 0.07506 |
| CVaR(es11)-CVaR(G) | 0.0403 | -0.1429 | 0.2235 |
| 0.8CVaR(G)-CVaR(preset) | -0.1017 | -0.202 | -0.00137 |
| P(preset)-P(G) | -0.004167 | -0.01667 | 0.008333 |

P(c) − P(G) > 0 šteti GAdapt-u; CVaR(c) − CVaR(G) > 0 koristi GAdapt-u.

## 2. Agregati po konfiguraciji (ćelije jednako ponderisane)

**B = 12000**

| konfiguracija | P(izvodljivo) | CVaR₀,₉(L) | srednja ćelijska medijana G |
|---|---|---|---|
| gadapt | 0.746 | 0.2973 | inf |
| gadapt_preset | 0.742 | 0.3395 | inf |
| pygad_random | 0.667 | 0.4138 | inf |
| pygad_adaptive | 0.621 | 0.4697 | inf |
| de | 0.625 | 0.3887 | inf |
| cma | 0.754 | 0.2511 | inf |
| ipop | 0.771 | 0.2518 | inf |
| bipop | 0.767 | 0.2533 | inf |
| es11 | 0.750 | 0.3376 | inf |

**B = 3000**

| konfiguracija | P(izvodljivo) | CVaR₀,₉(L) | srednja ćelijska medijana G |
|---|---|---|---|
| gadapt | 0.646 | 0.4144 | inf |
| gadapt_preset | 0.658 | 0.4139 | inf |
| pygad_random | 0.554 | 0.7694 | inf |
| pygad_adaptive | 0.438 | 0.7722 | inf |
| de | 0.604 | 0.5761 | inf |
| cma | 0.696 | 0.4414 | inf |
| ipop | 0.654 | 0.4137 | inf |
| bipop | 0.650 | 0.4486 | inf |
| es11 | 0.629 | 0.4919 | inf |

## 3. Po ćeliji (najveći budžet): P(izvodljivo) / medijana G

| ćelija | gadapt | gadapt_preset | pygad_random | pygad_adaptive | de | cma | ipop | bipop | es11 |
|---|---|---|---|---|---|---|---|---|---|
| case24_ieee_rts 2 | 1.00 / 4.32e-05 | 1.00 / 0.00276 | 1.00 / 0.0466 | 1.00 / 0.0811 | 1.00 / 0.0127 | 1.00 / 1.87e-07 | 1.00 / -3.81e-07 | 1.00 / 7.05e-07 | 1.00 / 1.54e-05 |
| case24_ieee_rts 3 | 1.00 / 0.00253 | 1.00 / 0.00492 | 1.00 / 0.06 | 1.00 / 0.0701 | 1.00 / 0.0162 | 1.00 / -0.0032 | 1.00 / -0.00416 | 1.00 / -0.00416 | 1.00 / 0.000616 |
| case24_ieee_rts 4 | 1.00 / 0.0123 | 1.00 / 0.013 | 1.00 / 0.0611 | 0.97 / 0.0826 | 1.00 / 0.0211 | 1.00 / -0.00282 | 1.00 / -0.00282 | 1.00 / 2.08e-05 | 1.00 / 0.00478 |
| case30 2 | 1.00 / 0.00657 | 1.00 / 0.00657 | 1.00 / 0.00657 | 1.00 / 0.0248 | 1.00 / 0.00657 | 1.00 / 0.00657 | 1.00 / 0.00657 | 1.00 / 0.00657 | 1.00 / 0.00657 |
| case30 3 | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.00 / inf |
| case39 2 | 1.00 / -0.00611 | 1.00 / -0.00608 | 1.00 / 0.0008 | 1.00 / 0.0267 | 1.00 / 0.0195 | 1.00 / -0.00615 | 1.00 / -0.0098 | 1.00 / -0.00948 | 1.00 / -0.00432 |
| case39 3 | 0.97 / -0.00819 | 0.93 / -0.00607 | 0.33 / inf | 0.00 / inf | 0.00 / inf | 1.00 / -0.00717 | 1.00 / -0.00684 | 1.00 / -0.0096 | 0.93 / -0.00677 |
| case39 4 | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.00 / inf | 0.03 / inf | 0.17 / inf | 0.13 / inf | 0.07 / inf |

## 4. Ograničenja
Diskretni ORPD sa tri mreže i osam ćelija; 30 semena (retki otkazi nisu pouzdano procenljivi; CVaR je prosek 3 najgora od 30); CMA porodica kontinualna sa zaokruživanjem (bez margine); I57 (CMAwM) samo opisni kontekst; r je kontinualni OPF, ne optimum diskretnog problema; svedok na 3.000 poziva nije nezavisno proveren. Nema tvrdnje o industrijskoj spremnosti.
