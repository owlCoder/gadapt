# I64 — dijagnostika brojanja evaluacija u mentorovom benchmarku (NEPREREGISTROVANO, samo orijentacija za dizajn)

Datum 2026-10-28. Skripta: `mbench_count_diagnostic.py` (mentorove klase/operatori i parametri iz `gadapt_experiments@0e388356`, Sphere, pop 64, stagnacija 20, limit 600;
GAdapt koristi zajednički brojač jer `GA.execute()` duboko kopira GA). 8 pokretanja po konfiguraciji, semena 0..7. Ne koristi se kao dokaz; ne utiče na protokol osim što potvrđuje
da je brojanje stvarnih poziva neophodno.

| Sphere | konfiguracija | poziva/pokretanju (sr.) | generacija | poziva/gen. | sr. završna greška |
|---|---|---|---|---|---|
| D=7 | GAdapt diversity | 9.942 | 309,6 | 32,1 | 9,4e−9 |
| D=7 | PyGAD random | 19.232 | 600 (limit) | 32,1 | 4,0e−9 |
| D=7 | PyGAD adaptive | 38.400 | 600 (limit) | 64,0 | 1,4e−7 |
| D=7 | SciPy DE | 11.447 | 177,9 | 64,4 | 1,8e−14 |
| D=2 | GAdapt diversity | 5.406 | 167,9 | 32,2 | 1,3e−14 |
| D=2 | PyGAD random | 19.232 | 600 (limit) | 32,1 | 2,2e−123 |
| D=2 | PyGAD adaptive | 38.400 | 600 (limit) | 64,0 | 7,7e−120 |
| D=2 | SciPy DE | 3.558 | 53,8 | 66,2 | 1,9e−19 |

Opažanja (opisno, jedna funkcija): (1) generacija nije jedinica troška: DE i PyGAD adaptive evaluiraju ≈ 64 po generaciji, GAdapt i PyGAD random ≈ 32; PyGAD adaptive troši 2× evaluacija od PyGAD random za iste generacije.
(2) Obe PyGAD konfiguracije stižu do limita od 600 generacija (stagnaciono pravilo se ne aktivira jer fitnes i dalje blago opada), pa im je „tačnost pri zaustavljanju“ posledica 2–4× većeg budžeta nego kod GAdapt-a.
(3) Na Sphere u ovom podešavanju SciPy DE je i brži i tačniji od GAdapt-a po broju evaluacija; mentorova formulacija „tačniji od onog jednog“ ovde nije potvrđena za DE, što samo ukazuje da treba tačno saznati koji algoritam i koja funkcija.
Ovo je razlog za I64-S: isti budžet u stvarnim evaluacijama, nezavisno brojanje, više funkcija, pomerene/rotirane varijante, i mere repa raspodele.
