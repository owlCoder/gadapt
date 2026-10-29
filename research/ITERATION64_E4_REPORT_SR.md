# ITERATION64-E4: kompenzaciona mutacija (opt-in `compensatory_mutation`) sa kontrolama — izveštaj (generisan iz arhive)

Specifikacija: [ITERATION64_E4_SPEC.md](ITERATION64_E4_SPEC.md) (zamrznuta `226c757`, dopuna A1 `6368959`). Uparivanje sa arhiviranim E zapisima po ključu (ćelija, seme); 63 ćelije × 100 semena, 12.000 stvarnih poziva.

## 1. Ishod hipoteza (jedna simultana porodica od pet kontrasta, α = 0.05, t* = 2.665, 20000 ponavljanja)

- **H64k1** (zatvaranje jaza prema GAdapt-M pod rotacijom): **undecided**
- **H64k2** (tolerisana šteta na orig+shift): **supported**
- **H64k3** (gated bolji od kontrole sa permutovanim partnerom pod rotacijom): **undecided**
- **H64k4** (gated bolji od Bouter-stil resample kontrole): **undecided**
- **H64k5** (neinferiornost prema IPOP-u, margina 0,05): **opposite**
- jezgro (k1–k4) podržano: **False**; C_rot(GAdapt-M) = 0.0300

| kontrast | procena | donja | gornja |
|---|---|---|---|
| dA_rot(G-M) | 0.01403 | 0.005221 | 0.02284 |
| 0.8*CVaR_rot(M)-CVaR_rot(G) | -0.003166 | -0.006589 | 0.0002576 |
| dA_nonrot(G-M) | 0.003022 | -0.00108 | 0.007123 |
| 1.5*CVaR_nonrot(M)-CVaR_nonrot(G) | 0.0008672 | 0.0005319 | 0.001202 |
| dA_rot(G-permuted) | -0.002892 | -0.01235 | 0.00657 |
| dA_rot(G-resample) | -0.00292 | -0.01137 | 0.005534 |
| dA_rot(G-IPOP) | -0.1322 | -0.142 | -0.1224 |

## 2. Agregati po varijanti (težine: funkcije jednake, dimenzije jednake unutar funkcije; „medijana jaza“ = ponderisani prosek ćelijskih medijana normalizovanog jaza; CVaR = ponderisani prosek ćelijskih CVaR₀,₉(L))

**orig**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.7022 | 0.0026 | 0.00101 |
| gadapt_cg | 0.7022 | 0.0029 | 0.00151 |
| gadapt_cu | 0.6790 | 0.0044 | 0.00163 |
| gadapt_cp | 0.6836 | 0.0047 | 0.00193 |
| gadapt_cr | 0.6762 | 0.0040 | 0.0017 |
| ipop | 0.7765 | 0.0122 | 0.00568 |
| cma | 0.7554 | 0.0156 | 0.0102 |
| bipop | 0.7717 | 0.0135 | 0.00594 |
| de | 0.6522 | 0.0082 | 0.00584 |

**shift**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.7007 | 0.0025 | 0.0011 |
| gadapt_cg | 0.7067 | 0.0031 | 0.00134 |
| gadapt_cu | 0.6821 | 0.0043 | 0.00204 |
| gadapt_cp | 0.6915 | 0.0046 | 0.00182 |
| gadapt_cr | 0.6798 | 0.0041 | 0.0023 |
| ipop | 0.7701 | 0.0147 | 0.00855 |
| cma | 0.7697 | 0.0134 | 0.00749 |
| bipop | 0.7712 | 0.0140 | 0.00709 |
| de | 0.6542 | 0.0082 | 0.00578 |

**rot**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.6167 | 0.0300 | 0.0108 |
| gadapt_cg | 0.6308 | 0.0272 | 0.0134 |
| gadapt_cu | 0.6286 | 0.0278 | 0.0118 |
| gadapt_cp | 0.6337 | 0.0292 | 0.0107 |
| gadapt_cr | 0.6337 | 0.0292 | 0.0121 |
| ipop | 0.7630 | 0.0158 | 0.00913 |
| cma | 0.7603 | 0.0145 | 0.00996 |
| bipop | 0.7636 | 0.0151 | 0.00889 |
| de | 0.6124 | 0.0391 | 0.0335 |

## 3. Tumačenje (post hoc, oprezno)
Mali dobitak efikasnosti prema GAdapt-M pod rotacijom (ΔA ≈ +0,014) nije razlučiv od kontrole sa slučajnim partnerom ni od Bouter-stil resample kontrole (intervali obuhvataju nulu), pa se NE može pripisati iskorišćavanju elitnih korelacija; rep raspodele se ne smanjuje za traženih 20%. Jaz prema IPOP-u ostaje velik. Opcija je dokumentovana i podrazumevano isključena, bez preporuke. Kontrola `permuted` meri razliku kompletnih režima (Codex 092); `resample` je ispravljen i ponovljen (dopuna A1); algoritamska originalnost i industrijska korist nisu ustanovljene.

