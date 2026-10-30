# ITERATION64-A: ablacija hibrida GAdapt → CMA-ES (zamena GAdapt prve faze slučajnim uzorkovanjem) — izveštaj (generisan iz arhive)

Specifikacija: [ITERATION64_A_SPEC.md](ITERATION64_A_SPEC.md). H = arhivirani E3 hibrid (GAdapt-M 30% → CMA); R = slučajno uzorkovanje 30% → isti CMA. 63 ćelije × 100 semena, 12.000 stvarnih poziva, upareno po (ćelija, seme).

Simultani interval (4 kontrasta, α = 0.05, 20000 ponavljanja, seme 71), t* = 2.5028.

| kontrast | procena | donja | gornja |
|---|---|---|---|
| c1 dA_rot(H-R) | 0.1313 | 0.1237 | 0.1389 |
| c2 dA_nonrot(H-R) | 0.1779 | 0.1735 | 0.1822 |
| c3 CVaR_rot(R)-CVaR_rot(H) | 0.0055 | 0.0041 | 0.0070 |
| c4 CVaR_nonrot(R)-CVaR_nonrot(H) | 0.0134 | 0.0124 | 0.0144 |

- **H64a1** (efekat zamene GAdapt faze na A pod rotacijom ≥ 0,02): **supported**
- **H64a2** (isto na orig+shift): **supported**
- ukupno `contribution_supported`: **True**

Agregati po varijanti:

| varijanta | konf. | A | CVaR₀,₉ | medijana jaza |
|---|---|---|---|---|
| orig | H | 0.7628 | 0.0048 | 0.00216 |
| orig | R | 0.5876 | 0.0184 | 0.01132 |
| shift | H | 0.7708 | 0.0043 | 0.00219 |
| shift | R | 0.5903 | 0.0176 | 0.00891 |
| rot | H | 0.7196 | 0.0119 | 0.00443 |
| rot | R | 0.5884 | 0.0174 | 0.00911 |

## Ograničenja
Procenjuje se efekat zamene prve faze (30%) uniformnim uzorkovanjem u ovom fiksiranom hibridu; ne tvrdi se da GAdapt samostalno nadmašuje slučajno uzorkovanje, mehanizam, niti važenje za druge udele, budžete, σ₀ ili CMA varijante. Bootstrap obuhvata samo varijaciju algoritamskih semena. Moguća zbunjujuća okolnost: CMA faza kreće iz najbolje slučajne tačke sa σ₀ = 0,05 (podešeno za hibrid sa GAdapt fazom), što može biti slab start za slučajnu inicijalizaciju; σ₀ nije varirano, pa efekat treba čitati kao efekat zamene u ovom fiksiranom hibridu, ne kao čistu meru kvaliteta GAdapt faze.
