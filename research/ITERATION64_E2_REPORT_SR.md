# ITERATION64-E2: diferencijalni krosover pod rotacijom — izveštaj (generisan iz arhive)

Specifikacija: [ITERATION64_E2_SPEC.md](ITERATION64_E2_SPEC.md) (zamrznuta `aeff985`). Uparivanje sa arhiviranim E zapisima po ključu (ćelija, seme); 63 ćelije × 100 semena, 12.000 stvarnih poziva.

## 1. Ishod hipoteza (jedna simultana porodica od pet kontrasta, α = 0.05, t* = 2.559, 20000 ponavljanja)

- **H64e1** (zatvaranje jaza pod rotacijom prema GAdapt-M): **opposite**
- **H64e2** (tolerisana šteta na orig+shift): **undecided**
- **H64e3** (neinferiornost prema IPOP-u, margina 0,05): **opposite**
- ukupno podržano: **False**; C_rot(GAdapt-M) = 0.0300

| kontrast | procena | donja | gornja |
|---|---|---|---|
| dA_rot(D-M) | -0.03619 | -0.04722 | -0.02516 |
| 0.8*CVaR_rot(M)-CVaR_rot(D) | -0.02534 | -0.02941 | -0.02126 |
| dA_nonrot(D-M) | -0.04215 | -0.04611 | -0.0382 |
| 1.5*CVaR_nonrot(M)-CVaR_nonrot(D) | 9.15e-05 | -0.000238 | 0.000421 |
| dA_rot(D-IPOP) | -0.1824 | -0.192 | -0.1728 |

## 2. Agregati po varijanti (ćelije jednako ponderisane unutar varijante)

**orig**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.7022 | 0.0026 | 0.00101 |
| gadapt_diff | 0.6597 | 0.0038 | 0.00187 |
| ipop | 0.7765 | 0.0122 | 0.00568 |
| cma | 0.7554 | 0.0156 | 0.0102 |
| bipop | 0.7717 | 0.0135 | 0.00594 |
| de | 0.6522 | 0.0082 | 0.00584 |

**shift**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.7007 | 0.0025 | 0.0011 |
| gadapt_diff | 0.6588 | 0.0037 | 0.00174 |
| ipop | 0.7701 | 0.0147 | 0.00855 |
| cma | 0.7697 | 0.0134 | 0.00749 |
| bipop | 0.7712 | 0.0140 | 0.00709 |
| de | 0.6542 | 0.0082 | 0.00578 |

**rot**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.6167 | 0.0300 | 0.0108 |
| gadapt_diff | 0.5805 | 0.0494 | 0.0252 |
| ipop | 0.7630 | 0.0158 | 0.00913 |
| cma | 0.7603 | 0.0145 | 0.00996 |
| bipop | 0.7636 | 0.0151 | 0.00889 |
| de | 0.6124 | 0.0391 | 0.0335 |

## 3. Zaključak
Opt-in diferencijalni krosover **ne zatvara** rotacijski jaz GAdapt-a i na svim varijantama smanjuje efikasnost (ΔA < 0 sa intervalom koji ne obuhvata nulu); rep raspodele pod rotacijom je lošiji. Opcija ostaje u biblioteci kao dokumentovana, podrazumevano isključena, BEZ preporuke. Rezultat je preregistrovan i negativan; nije ponovljen sa drugim F. Operator je rotaciono ekvivarijantan samo kao neograničen korak; mutacioni operatori ostaju koordinatni, pa sam krosover ne menja ponašanje celog algoritma dovoljno.

