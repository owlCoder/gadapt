# ITERATION64-E2: hibrid GAdapt→CMA (globalna pretraga + lokalno doterivanje) — izveštaj (generisan iz arhive)

Specifikacija: [ITERATION64_E3_SPEC.md](ITERATION64_E3_SPEC.md) (zamrznuta `f228044`). Uparivanje sa arhiviranim E zapisima po ključu (ćelija, seme); 63 ćelije × 100 semena, 12.000 stvarnih poziva.

## 1. Ishod hipoteza (jedna simultana porodica od pet kontrasta, α = 0.05, t* = 2.558, 20000 ponavljanja)

- **H64g1** (zatvaranje jaza pod rotacijom prema GAdapt-M): **supported**
- **H64g2** (tolerisana šteta na orig+shift): **opposite**
- **H64g3** (neinferiornost prema IPOP-u, margina 0,05): **undecided**
- ukupno podržano: **False**; C_rot(GAdapt-M) = 0.0300

| kontrast | procena | donja | gornja |
|---|---|---|---|
| dA_rot(H-M) | 0.1029 | 0.09264 | 0.1132 |
| 0.8*CVaR_rot(M)-CVaR_rot(H) | 0.01212 | 0.009443 | 0.01479 |
| dA_nonrot(H-M) | 0.06535 | 0.06073 | 0.06996 |
| 1.5*CVaR_nonrot(M)-CVaR_nonrot(H) | -0.0006964 | -0.001109 | -0.0002838 |
| dA_rot(H-IPOP) | -0.04335 | -0.05189 | -0.03482 |

## 2. Agregati po varijanti (ćelije jednako ponderisane unutar varijante)

**orig**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.7022 | 0.0026 | 0.00101 |
| gadapt_hyb | 0.7628 | 0.0048 | 0.00216 |
| ipop | 0.7765 | 0.0122 | 0.00568 |
| cma | 0.7554 | 0.0156 | 0.0102 |
| bipop | 0.7717 | 0.0135 | 0.00594 |
| de | 0.6522 | 0.0082 | 0.00584 |

**shift**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.7007 | 0.0025 | 0.0011 |
| gadapt_hyb | 0.7708 | 0.0043 | 0.00219 |
| ipop | 0.7701 | 0.0147 | 0.00855 |
| cma | 0.7697 | 0.0134 | 0.00749 |
| bipop | 0.7712 | 0.0140 | 0.00709 |
| de | 0.6542 | 0.0082 | 0.00578 |

**rot**

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.6167 | 0.0300 | 0.0108 |
| gadapt_hyb | 0.7196 | 0.0119 | 0.00443 |
| ipop | 0.7630 | 0.0158 | 0.00913 |
| cma | 0.7603 | 0.0145 | 0.00996 |
| bipop | 0.7636 | 0.0151 | 0.00889 |
| de | 0.6124 | 0.0391 | 0.0335 |

## 2b. Prosek po tri varijante (jednaka težina varijanti; opisno)

| konfiguracija | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|
| gadapt | 0.6732 | 0.0117 | 0.00429 |
| gadapt_hyb | 0.7511 | 0.0070 | 0.00293 |
| ipop | 0.7699 | 0.0142 | 0.00779 |
| cma | 0.7618 | 0.0145 | 0.00921 |
| bipop | 0.7688 | 0.0142 | 0.00731 |
| de | 0.6396 | 0.0185 | 0.015 |

## 3. Napomena o tumačenju
Hibrid NIJE GAdapt sam: poslednjih 70% budžeta troši CMA-ES. Rezultat se zato čita kao provera industrijskog recepta „globalna pretraga, pa lokalno doterivanje“, ne kao svojstvo GAdapt-a. Nema tvrdnje o novoj metodi (hibridni algoritmi su poznati). Zamrznuta pravila odluke daju mešan ishod: pogledati hipoteze u odeljku 1. Opisno: hibrid ima najniži CVaR od svih konfiguracija osim GAdapt-M na osno-poravnatim ćelijama, i znatno niži od CMA porodice u svim varijantama; njegova ECDF-površina je u blizini IPOP-a. Ovo je opisna slika iste arhive, ne dodatna hipoteza.

