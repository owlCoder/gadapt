# ITERATION64-R: izolovanje ortogonalne transformacije (isti pomeraj) — izveštaj (generisan iz arhive)

Specifikacija: [ITERATION64_R_SPEC.md](ITERATION64_R_SPEC.md). Ćelija `rotm` = Q iz E `rot` i o iz E `shift`; 21 par funkcija/dimenzija, 100 semena, 12.000 stvarnih poziva, GAdapt-M i IPOP-CMA-ES. Q je Haar-ortogonalna (moguće sa refleksijom), pa se ne govori o čistoj rotaciji.

Simultani interval (4 kontrasta, α = 0.05, 20000 ponavljanja, seme 70), t* = 2.4289.

| kontrast | procena | donja | gornja |
|---|---|---|---|
| c1 A_G(rotm)-A_G(rot) | 0.0031 | -0.0081 | 0.0142 |
| c2 A_G(shift)-A_G(rotm) | 0.0809 | 0.0721 | 0.0897 |
| c3 A_I(shift)-A_I(rotm) | 0.0101 | 0.0036 | 0.0166 |
| c4 c2-c3 | 0.0708 | 0.0598 | 0.0818 |

- **H64r1** (agregatni efekat zamene pomeraja u ±0,03, uslovno na 21 fiksni Q): **supported**
- **H64r2** (pad A GAdapt-M zbog Q najmanje 0,05): **supported**
- **H64r3** (Q umanjuje A GAdapt-M bar 0,05 više nego IPOP-a, uz H64r2): **supported**

Agregati A (ponderisani):

| varijanta | GAdapt-M | IPOP |
|---|---|---|
| shift | 0.7007 | 0.7701 |
| rot | 0.6167 | 0.7630 |
| rotm | 0.6198 | 0.7600 |

Po parovima (A, GAdapt-M / IPOP):

| par | shift | rot | rotm |
|---|---|---|---|
| sphere|2 | 0.976 / 0.991 | 0.975 / 0.991 | 0.976 / 0.991 |
| sphere|7 | 0.910 / 0.961 | 0.909 / 0.961 | 0.907 / 0.959 |
| sphere|20 | 0.626 / 0.895 | 0.616 / 0.892 | 0.626 / 0.893 |
| rosenbrock|2 | 0.709 / 0.989 | 0.705 / 0.990 | 0.796 / 0.990 |
| rosenbrock|7 | 0.600 / 0.934 | 0.616 / 0.930 | 0.603 / 0.930 |
| rosenbrock|20 | 0.344 / 0.785 | 0.323 / 0.775 | 0.297 / 0.769 |
| rastrigin|2 | 0.938 / 0.809 | 0.522 / 0.781 | 0.552 / 0.826 |
| rastrigin|7 | 0.534 / 0.026 | 0.003 / 0.034 | 0.008 / 0.014 |
| rastrigin|20 | 0.013 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| ackley|2 | 0.923 / 0.980 | 0.917 / 0.980 | 0.922 / 0.980 |
| ackley|7 | 0.531 / 0.913 | 0.469 / 0.912 | 0.504 / 0.919 |
| ackley|20 | 0.161 / 0.778 | 0.023 / 0.785 | 0.031 / 0.778 |
| griewank|2 | 0.590 / 0.393 | 0.500 / 0.434 | 0.558 / 0.327 |
| griewank|7 | 0.069 / 0.497 | 0.041 / 0.474 | 0.050 / 0.463 |
| griewank|20 | 0.160 / 0.680 | 0.074 / 0.697 | 0.065 / 0.707 |
| styblinski_tang|2 | 0.968 / 0.967 | 0.965 / 0.951 | 0.953 / 0.963 |
| styblinski_tang|7 | 0.862 / 0.308 | 0.459 / 0.205 | 0.357 / 0.094 |
| styblinski_tang|20 | 0.340 / 0.000 | 0.046 / 0.000 | 0.069 / 0.000 |
| beale|2 | 0.949 / 0.986 | 0.908 / 0.989 | 0.880 / 0.992 |
| himmelblau|2 | 0.968 / 0.985 | 0.945 / 0.955 | 0.964 / 0.988 |
| booth|2 | 0.971 / 0.991 | 0.976 / 0.991 | 0.976 / 0.991 |

## Ograničenja
Bootstrap obuhvata samo varijaciju semena, ne izbor funkcija, dimenzija, Q ili o; nalaz važi za 21 ćeliju i dve konfiguracije i ne generalizuje se na proizvoljne Haar transformacije. Ne tvrdi se mehanizam. Težine: d = 2 ćelije nose 5/9 ukupne težine.
