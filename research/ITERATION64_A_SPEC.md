# ITERATION64-A: ablacija hibrida GAdapt → CMA-ES (da li GAdapt faza doprinosi?) — specifikacija za zamrzavanje

Motiv (Codex 093, tačka 4; Codex 095): E3 ne pokazuje da je zasluga hibrida u GAdapt fazi, jer 70% budžeta troši CMA. A zamenjuje GAdapt fazu (prvih 30% budžeta) uniformnim slučajnim uzorkovanjem i zadržava ostalo IDENTIČNO; razlika hibrid − slučajna inicijalizacija izoluje doprinos GAdapt faze (uz isti CMA, isti σ₀ = 0,05 iz najbolje tačke prve faze, iste restarte i isti budžet). Prior art: hibridi (Krasnogor & Smith 2005) — nema novine; empirijska provera atribucije.

1. **Algoritam R-HYB (`hyb_rand`)**: prvih ⌊0,3·12.000⌋ = 3.600 stvarnih poziva = uniformno slučajne tačke u jediničnoj kocki (`default_rng([seed, 5])`); zatim IDENTIČNO kao E3 (`e3_algo.gadapt_cma_runner` faza 2: CMA-ES iz najbolje tačke, σ₀ = 0,05, granice [0,1], posle prirodnog završetka restart iz slučajne tačke σ₀ = 0,3, tokovi `[seed,3,k]` i `[seed,4,k]`). Bez podešavanja (frac = 0,3 iz E3 `freeze`).
2. **Ćelije/semena**: IDENTIČNO kao E3: 63 ćelije × 100 semena (seed_of("run", ci, s)), 12.000 stvarnih poziva, 6.300 pokretanja. Poređenje sa arhiviranim E3 zapisima `gadapt_hyb` (isto seme = isti zadatak).
3. **Kontrasti (jedna simultana porodica od 4, bootstrap sa zajedničkim indeksom semena po ćeliji, 20.000 ponavljanja, `default_rng(71)`, max-studentizovano, α = 0,05)**: c1 = ΔA_rot(H − R); c2 = ΔA_nonrot(H − R); c3 = CVaR_rot(R) − CVaR_rot(H); c4 = CVaR_nonrot(R) − CVaR_nonrot(H). Težine kao E3 (1/9)/dims po ćeliji, renormalizovano unutar stratuma (rot = 21 ćelija; nonrot = orig + shift = 42 ćelije).
4. **Hipoteze**:
   - **H64a1** (GAdapt faza doprinosi A pod rotacijom): podržana ako je LB(c1) > 0,02; `below_threshold` ako je UB(c1) < 0,02; inače neodlučena.
   - **H64a2** (GAdapt faza doprinosi A na orig+shift): podržana ako je LB(c2) > 0,02; `below_threshold` ako je UB(c2) < 0,02; inače neodlučena.
   - c3 i c4 su opisni (rep), ne ulaze u odluku; prijavljuju se sa intervalima.
   Ukupno „GAdapt faza doprinosi“ samo ako su obe podržane. Beskonačne vrednosti / nulta varijansa blokiraju.
5. **Provera ponovljivosti**: pre pokretanja 3 arhivirana E3 zapisa `gadapt_hyb` (seme 1; ćelije 2 (sphere-2 rot), 29 (ackley-2 rot), 28 (ackley-2 shift)) ponovo se izvršavaju na trenutnom stablu i moraju dati identične `calls`, `best_f`, `best_y`, `events`; E3 `run`, `freeze` i svi ulazni heševi beleže se pre pokretanja.
6. **Ne tvrdi se**: da je GAdapt faza „neophodna“ ili „suvišna“ van 63 ćelija i fiksiranog udela 30%; mehanizam; opšta industrijska korist. Atribucija se odnosi samo na zamenu prve faze slučajnim uzorkovanjem.
7. **Realizacija**: `research/i64/a_algo.py`, `a_study.py` (`check_repro`, `run`, `analyse`), `a_report.py`, `run_a.sh`.
