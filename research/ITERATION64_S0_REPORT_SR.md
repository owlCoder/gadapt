# ITERATION64-S0: replikacija mentorovog benchmarka sa stvarnim brojanjem poziva — izveštaj (generisan iz arhive)

Protokol: [ITERATION64_PROTOCOL.md](ITERATION64_PROTOCOL.md) (v2, S0 zamrznut pre merenja). Driver: `research/i64/s0_replication.py`. Sirovi izlazi: `research/results/iteration64_s0/`.
Pokretanja: 1680 (21 ćelija × 4 konfiguracije × 20 semena, p = 0); gate prošao: True.

## 1. Ishod H64a na S0 (mentorova tvrdnja, četiri originalne konfiguracije): **supported**

supported = True, opposite = False, kandidati za „izuzetak“ = ['pygad_random', 'pygad_adaptive', 'de']; simultani bootstrap (20000 ponavljanja), α = 0.01, t* = 3.214.

| Kontrast (GAdapt − konkurent za ΔA; konkurent − GAdapt za ΔM) | procena | donja | gornja |
|---|---|---|---|
| dA|pygad_random | 0.1638 | 0.1437 | 0.184 |
| dA|pygad_adaptive | 0.2044 | 0.1877 | 0.2212 |
| dA|de | 0.04731 | 0.03332 | 0.0613 |
| dM|pygad_random | 0.04526 | 0.0383 | 0.05222 |
| dM|pygad_adaptive | 0.04345 | 0.03714 | 0.04976 |
| dM|de | 0.007141 | 0.003526 | 0.01076 |

ΔA > 0: GAdapt ima veću ECDF-površinu (efikasniji). ΔM > 0: GAdapt ima niži završni medijalni jaz (tačniji). Jaz je normalizovan medijanom slučajnih tačaka (§2).

## 2. Agregati po konfiguraciji (težine §2)

| konfiguracija | poziva/pokretanju | generacija | ECDF površina A | A (samo „search“ pozivi) | CVaR₀,₉ (L) | medijana jaza |
|---|---|---|---|---|---|---|
| gadapt | 10184 | 317.2 | 0.698 | 0.698 | 0.0063 | 0.000998 |
| pygad_random | 16515 | 260.0 | 0.534 | 0.593 | 0.0532 | 0.0463 |
| pygad_adaptive | 25155 | 264.6 | 0.494 | 0.539 | 0.0589 | 0.0444 |
| de | 11887 | 189.3 | 0.651 | 0.653 | 0.0157 | 0.00814 |

## 3. Generacije nisu jedinica troška (stvarni pozivi po fazama, sva pokretanja)

| konfiguracija | best_solution | de_callback | gadapt_validation | init_manual | search |
|---|---|---|---|---|---|
| gadapt | 0 | 0 | 840 | 0 | 4675360 |
| pygad_random | 3278374 | 0 | 0 | 26880 | 3305254 |
| pygad_adaptive | 3246069 | 0 | 0 | 26880 | 6543701 |
| de | 0 | 94916 | 0 | 0 | 5842814 |

`best_solution` = ponovna računanja mentorovog callback-a u PyGAD-u; `de_callback` = DE callback; `init_manual` = ručna početna evaluacija PyGAD-a; `gadapt_validation` = all-min/all-max probe.

## 4. Opisno po ćelijama

| ćelija | konfiguracija | poziva | generacija | medijana jaza | CVaR₀,₉ | P(g≤1e−2) | P(≤1e−4) | P(≤1e−6) |
|---|---|---|---|---|---|---|---|---|
| ackley d=20 | de | 36660 | 600.0 | 9.41e-08 | 0.0000 | 1.00 | 1.00 | 1.00 |
| ackley d=20 | gadapt | 19151 | 597.4 | 0.000133 | 0.0003 | 1.00 | 0.15 | 0.00 |
| ackley d=20 | pygad_adaptive | 14187 | 147.4 | 0.139 | 0.2570 | 0.00 | 0.00 | 0.00 |
| ackley d=20 | pygad_random | 9830 | 152.6 | 0.172 | 0.2254 | 0.00 | 0.00 | 0.00 |
| ackley d=2 | de | 5937 | 90.3 | 5.06e-17 | 0.0000 | 1.00 | 1.00 | 1.00 |
| ackley d=2 | gadapt | 4450 | 138.0 | 2.81e-11 | 0.0000 | 1.00 | 1.00 | 0.90 |
| ackley d=2 | pygad_adaptive | 16261 | 169.1 | 5.06e-17 | 0.0000 | 1.00 | 1.00 | 1.00 |
| ackley d=2 | pygad_random | 11242 | 174.7 | 5.06e-17 | 0.0000 | 1.00 | 1.00 | 1.00 |
| ackley d=7 | de | 20636 | 321.4 | 1.34e-14 | 0.0000 | 1.00 | 1.00 | 1.00 |
| ackley d=7 | gadapt | 11586 | 361.0 | 7.58e-06 | 0.0000 | 1.00 | 1.00 | 0.00 |
| ackley d=7 | pygad_adaptive | 56077 | 583.8 | 1.13e-07 | 0.0000 | 1.00 | 1.00 | 0.70 |
| ackley d=7 | pygad_random | 36861 | 575.0 | 9.05e-08 | 0.0002 | 1.00 | 0.95 | 0.70 |
| beale d=2 | de | 4058 | 61.5 | 3.46e-21 | 0.0000 | 1.00 | 1.00 | 1.00 |
| beale d=2 | gadapt | 9951 | 309.9 | 3.71e-09 | 0.0000 | 1.00 | 1.00 | 1.00 |
| beale d=2 | pygad_adaptive | 42816 | 452.9 | 2.9e-13 | 0.0000 | 1.00 | 1.00 | 1.00 |
| beale d=2 | pygad_random | 21178 | 336.1 | 1.85e-10 | 0.0000 | 1.00 | 1.00 | 0.90 |
| booth d=2 | de | 3944 | 59.7 | 2.48e-21 | 0.0000 | 1.00 | 1.00 | 1.00 |
| booth d=2 | gadapt | 5212 | 161.8 | 1.46e-14 | 0.0000 | 1.00 | 1.00 | 1.00 |
| booth d=2 | pygad_adaptive | 32646 | 349.6 | 1.68e-30 | 0.0000 | 1.00 | 1.00 | 1.00 |
| booth d=2 | pygad_random | 25913 | 410.9 | 4.19e-15 | 0.0000 | 1.00 | 1.00 | 0.90 |
| griewank d=20 | de | 36535 | 598.0 | 3.31e-10 | 0.0017 | 1.00 | 0.85 | 0.85 |
| griewank d=20 | gadapt | 18797 | 586.4 | 0.00333 | 0.0131 | 0.90 | 0.25 | 0.00 |
| griewank d=20 | pygad_adaptive | 13582 | 141.2 | 0.197 | 0.1749 | 0.00 | 0.00 | 0.00 |
| griewank d=20 | pygad_random | 10301 | 159.9 | 0.198 | 0.1793 | 0.00 | 0.00 | 0.00 |
| griewank d=2 | de | 4858 | 73.8 | 0 | 0.0163 | 0.95 | 0.75 | 0.75 |
| griewank d=2 | gadapt | 3762 | 116.5 | 0.00534 | 0.0106 | 0.95 | 0.40 | 0.40 |
| griewank d=2 | pygad_adaptive | 6454 | 66.9 | 0.00934 | 0.0314 | 0.50 | 0.10 | 0.10 |
| griewank d=2 | pygad_random | 4534 | 69.8 | 0.00626 | 0.0243 | 0.75 | 0.05 | 0.05 |
| griewank d=7 | de | 5458 | 84.3 | 0.101 | 0.1660 | 0.00 | 0.00 | 0.00 |
| griewank d=7 | gadapt | 11416 | 355.7 | 0.0127 | 0.0661 | 0.30 | 0.00 | 0.00 |
| griewank d=7 | pygad_adaptive | 4947 | 51.2 | 0.165 | 0.2096 | 0.00 | 0.00 | 0.00 |
| griewank d=7 | pygad_random | 3651 | 56.0 | 0.167 | 0.1985 | 0.00 | 0.00 | 0.00 |
| himmelblau d=2 | de | 4022 | 60.9 | 4.19e-22 | 0.0000 | 1.00 | 1.00 | 1.00 |
| himmelblau d=2 | gadapt | 5418 | 168.2 | 9.87e-19 | 0.0000 | 1.00 | 1.00 | 1.00 |
| himmelblau d=2 | pygad_adaptive | 18718 | 203.2 | 0 | 0.0000 | 1.00 | 1.00 | 1.00 |
| himmelblau d=2 | pygad_random | 10597 | 178.1 | 0 | 0.0000 | 1.00 | 1.00 | 1.00 |
| rastrigin d=20 | de | 11171 | 182.2 | 0.119 | 0.2075 | 0.05 | 0.05 | 0.05 |
| rastrigin d=20 | gadapt | 18319 | 571.4 | 0.00542 | 0.0787 | 0.85 | 0.10 | 0.00 |
| rastrigin d=20 | pygad_adaptive | 5274 | 54.6 | 0.352 | 0.3239 | 0.00 | 0.00 | 0.00 |
| rastrigin d=20 | pygad_random | 3987 | 61.3 | 0.379 | 0.2964 | 0.00 | 0.00 | 0.00 |
| rastrigin d=2 | de | 4218 | 63.9 | 0 | 0.0000 | 1.00 | 1.00 | 1.00 |
| rastrigin d=2 | gadapt | 3604 | 111.5 | 0 | 0.0000 | 1.00 | 1.00 | 1.00 |
| rastrigin d=2 | pygad_adaptive | 10386 | 107.8 | 0 | 0.0032 | 1.00 | 0.80 | 0.80 |
| rastrigin d=2 | pygad_random | 7392 | 114.5 | 0 | 0.0011 | 1.00 | 0.95 | 0.95 |
| rastrigin d=7 | de | 16073 | 250.2 | 0 | 0.0327 | 0.90 | 0.90 | 0.90 |
| rastrigin d=7 | gadapt | 12440 | 387.7 | 4.35e-09 | 0.0000 | 1.00 | 1.00 | 1.00 |
| rastrigin d=7 | pygad_adaptive | 9608 | 99.8 | 0.0728 | 0.1712 | 0.10 | 0.05 | 0.00 |
| rastrigin d=7 | pygad_random | 9754 | 151.4 | 0.113 | 0.1577 | 0.20 | 0.15 | 0.15 |
| rosenbrock d=20 | de | 35861 | 586.9 | 2.74e-08 | 0.0000 | 1.00 | 1.00 | 1.00 |
| rosenbrock d=20 | gadapt | 19215 | 599.4 | 1.82e-05 | 0.0001 | 1.00 | 0.95 | 0.00 |
| rosenbrock d=20 | pygad_adaptive | 12661 | 131.6 | 0.0104 | 0.0341 | 0.45 | 0.00 | 0.00 |
| rosenbrock d=20 | pygad_random | 8854 | 137.3 | 0.0125 | 0.0316 | 0.30 | 0.00 | 0.00 |
| rosenbrock d=2 | de | 3863 | 58.5 | 6.96e-20 | 0.0000 | 1.00 | 1.00 | 1.00 |
| rosenbrock d=2 | gadapt | 5941 | 184.6 | 1.08e-05 | 0.0003 | 1.00 | 0.85 | 0.25 |
| rosenbrock d=2 | pygad_adaptive | 8173 | 84.8 | 3.45e-06 | 0.0000 | 1.00 | 1.00 | 0.30 |
| rosenbrock d=2 | pygad_random | 5814 | 89.8 | 4.85e-06 | 0.0001 | 1.00 | 0.95 | 0.45 |
| rosenbrock d=7 | de | 23676 | 368.9 | 1.83e-14 | 0.0000 | 1.00 | 1.00 | 1.00 |
| rosenbrock d=7 | gadapt | 18757 | 585.1 | 1.82e-05 | 0.0002 | 1.00 | 0.80 | 0.20 |
| rosenbrock d=7 | pygad_adaptive | 51978 | 541.1 | 5.68e-05 | 0.0006 | 1.00 | 0.55 | 0.15 |
| rosenbrock d=7 | pygad_random | 32259 | 503.1 | 5.76e-05 | 0.0011 | 1.00 | 0.65 | 0.10 |
| sphere d=20 | de | 36651 | 599.9 | 7.78e-15 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=20 | gadapt | 18549 | 578.6 | 1.14e-08 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=20 | pygad_adaptive | 14773 | 153.6 | 0.00627 | 0.0203 | 0.60 | 0.05 | 0.00 |
| sphere d=20 | pygad_random | 8851 | 137.3 | 0.00756 | 0.0250 | 0.70 | 0.00 | 0.00 |
| sphere d=2 | de | 3528 | 53.3 | 8.94e-21 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=2 | gadapt | 5453 | 169.3 | 5.57e-23 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=2 | pygad_adaptive | 57632 | 600.0 | 5.12e-127 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=2 | pygad_random | 38464 | 600.0 | 1e-125 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=7 | de | 11509 | 178.8 | 1.8e-16 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=7 | gadapt | 10469 | 326.1 | 1.86e-11 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=7 | pygad_adaptive | 57632 | 600.0 | 1.3e-20 | 0.0000 | 1.00 | 1.00 | 1.00 |
| sphere d=7 | pygad_random | 37754 | 588.9 | 8.14e-19 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=20 | de | 20477 | 334.7 | 1.36e-07 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=20 | gadapt | 19175 | 598.1 | 8.44e-08 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=20 | pygad_adaptive | 8566 | 88.9 | 0.248 | 0.2776 | 0.00 | 0.00 | 0.00 |
| styblinski_tang d=20 | pygad_random | 6173 | 95.5 | 0.194 | 0.2954 | 0.00 | 0.00 | 0.00 |
| styblinski_tang d=2 | de | 1634 | 24.1 | 1.17e-09 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=2 | gadapt | 2868 | 88.5 | 0 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=2 | pygad_adaptive | 10126 | 105.2 | 0 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=2 | pygad_random | 6778 | 104.9 | 0 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=7 | de | 6117 | 94.6 | 3.08e-08 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=7 | gadapt | 9277 | 288.9 | 6.1e-10 | 0.0000 | 1.00 | 1.00 | 1.00 |
| styblinski_tang d=7 | pygad_adaptive | 38336 | 399.0 | 9.87e-13 | 0.0855 | 0.90 | 0.90 | 0.90 |
| styblinski_tang d=7 | pygad_random | 30339 | 473.1 | 4.89e-16 | 0.0000 | 1.00 | 1.00 | 0.90 |

## 4b. Po ćelijama: ko pobeđuje (mehanički prebrojano iz tabele 4)

| konkurent | ćelije gde GAdapt ima manju medijanu jaza | ćelije gde konkurent ima manju | jednako | ćelije gde GAdapt ima veći A (srednja ECDF površina) | gde konkurent ima veći A |
|---|---|---|---|---|---|
| pygad_random | 10 | 9 | 2 | 20 | 1 |
| pygad_adaptive | 10 | 9 | 2 | 20 | 1 |
| de | 6 | 14 | 1 | 17 | 4 |

Agregatna ΔM je ponderisana srednja vrednost medijana NORMALIZOVANOG jaza, pa je dominiraju ćelije sa velikim jazom (multimodalne i 20-dimenzione); prebrojavanje gore pokazuje koliko je pobeda raspoređeno po ćelijama.


## 5. Ograničenja (unapred)
Jednokorisnički S0 ima 20 semena po ćeliji; zaključak važi za mentorove konfiguracije i funkcije bez rotacije i pomeranja; okruženje GAdapt 0.5.0 (PyPI) i PyGAD 3.5.0. Mentorova zaokruživanja izlaza (10 decimala) zamenjena su nezaokruženim svedokom. Ovo nije dokaz opšte superiornosti ni industrijske spremnosti.
