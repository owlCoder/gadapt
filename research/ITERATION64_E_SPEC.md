# ITERATION64-E: proširenje (pomereno/rotirano, jednak budžet, jači konkurenti) — specifikacija za zamrzavanje (dopuna protokola v2 §4)

Status: ZAMRZNUTO ovim komitom (Codex 086 nije stigao: limit do 23:28; samopregled koda: zaštita od praznog restarta dodata, native-domen mapiranje i analiza provereni testovima). Razvojna merenja slede posle komita. Realizacija: `research/i64/e_study.py`, `e_algos.py`, `e_common.py` (testovi `test_e_*.py`).

1. **Ćelije**: 21 funkcija/dimenzija × {orig, shift, rot} = 63 ćelije (c = 3·i + v u redosledu FUNCS; i = indeks u listi funkcija sa dimenzijama). Pomeraj o ∈ [0,25; 0,75]^D i Haar-ortogonalna Q generišu se jednom po ćeliji iz javnog semena
   `default_rng([64, purpose, c])` (dev: purpose 1, run: purpose 3), zajedničke svim konfiguracijama; f* i normalizatori s_i su isti kao u S0 (seme 64001).
2. **Konfiguracije (9)**: GAdapt-M (mentorova konfiguracija, bez stagnacije, `exit_check="generations"`, restart ako biblioteka vrati pre budžeta), isto sa presetom
   (`normal_distribution_mutation_min_std_dev=1e-4`, `…_decay_generations=2.5`), PyGAD random, PyGAD adaptive (mentorovi operatori, `keep_elitism=32`), SciPy DE (best1exp, 64 početnih jedinki, `tol=0`, restart pri konvergenciji),
   CMA-ES sa restartima iste populacije, IPOP-CMA-ES, BIPOP-CMA-ES (pycma 4.5.0), (1+1)-ES sa restartima. **L-SHADE i jDE su IZOSTAVLJENI**: nema validirane implementacije u zaključanom okruženju (obelodanjeno; mogu u zasebnu dopunu).
   GAdapt, preset, PyGAD i DE rade u MENTOROVOM izvornom domenu [lo, hi] (GAdapt-ova kolonska raznovrsnost nije invarijantna na jedinice; normalizacija na [0,1] bi menjala testirani metod — odstupanje od "sve na [0,1]" iz protokola §4, obelodanjeno);
   CMA porodica i (1+1)-ES rade na jediničnoj kocki (skalarno neutralno). Biblioteka GAdapt: ona iz repozitorijuma (hešovano drvo `gadapt/`), jer opcija `decay_generations` postoji samo tamo (PyPI 0.5.0 je nema).
3. **Budžet**: B = 12.000 stvarnih poziva (spoljni `BudgetReached(BaseException)`; poziv B se izvršava; probe GAdapt-a i PyGAD re-evaluacije se broje). Primarni rezultat: najmanji f među prvim B pozivima.
4. **Razvoj** (samo ovde se biraju parametri; p = 1; 5 semena po ćeliji; samo 'rot' ćelije — 21 ćelija): kandidati unapred: CMA/IPOP/BIPOP σ0 ∈ {0,2; 0,3; 0,5}; (1+1)-ES σ0 ∈ {0,1; 0,3} × up ∈ {1,2; 1,5} × stagnacija ∈ {100; 1000}.
   Izbor = najveća srednja ECDF površina A; veza → prvi kandidat. Ostale konfiguracije bez podešavanja (mentorove vrednosti). Posle razvoja `freeze` hešuje izbore.
5. **Potvrda**: 63 ćelije × 9 konfiguracija × 100 semena (p = 3; seme = 64·10⁶ + 3·10⁶ + 1000·c + s); isto seme = isti zadatak za svih 9 konfiguracija (različiti RNG tokovi po biblioteci); 56.700 pokretanja.
6. **Hipoteze/analiza**: kao u protokolu §2–3: H64a sa fokalnim GAdapt-M i osam konkurenata (uključujući preset), 16 kontrasta (ΔA, ΔM), simultani bootstrap α = 0,02; H64b (preset naspram GAdapt-M): četiri kontrasta, α = 0,01
   (0,8·R₀ − R_preset ≥ 0; razlike verovatnoće dostizanja ≥ −0,05 za tri cilja). Težine 1/9 po funkciji, jednako po dimenzijama i varijantama. 20.000 bootstrap ponavljanja, seme 64 (H64a) i 65 (H64b).
7. **CPU**: ≈ 56.700 pokretanja × 0,3–2 s ≈ 5–30 CPU-sati (procena); pokreće se na jednom jezgru uz nice dok I63 koristi devet.
8. **Obelodanjivanja**: (a) ishodi S0 su poznati pre zamrzavanja E; dizajn E nije podešavan prema njima (potiče iz Codex 083/084); (b) probno izvršavanje celog cevovoda sa B = 600, 2 semena, u privremenom direktorijumu (izlazi odbačeni);
   (c) normalizacija f* za Styblinski–Tang u dvostrukoj preciznosti; (d) PyGAD i DE dobijaju seme preko globalnog RNG-a / `rng`.

## Dopuna A1 (2026-10-28, PRE uvida u ijedan E rezultat): ispravljena analiza
Nezavisna matematička recenzija analize (agent `math-reviewer`, Codex nedostupan) našla je 0 blokirajućih i 6 neblokirajućih nedostataka (otkaz → L = 1 umesto NaN; NaN/inf u kontrastima blokira zaključak; nulta varijansa H64b ne sme da obori
H64a; strukturne provere; dokumentovanje neglatkosti CVaR bootstrapa; manifest analize). Ispravke su u `research/i64/e_analysis.py` (izlaz `analysis_v2`), a kod koji proizvodi podatke (`e_study.py` razvoj/freeze/run, `e_algos.py`, `e_common.py`) je NEPROMENJEN.
Lanac `run_e.sh` na kraju još pokreće staru `e_study.py analyse` (izlaz `analysis`); **primarna je `analysis_v2`**, stara je zamenjena i prijavljuje se samo ako se razlikuje. Provenijencija: `e_analysis.py` proverava heševe `e_algos.py`/`e_common.py`
iz manifesta `run` i da je `e_study.py` u zamrzavajućem komitu (`E_FREEZE_COMMIT`) bajt-identičan zapisanom heševu. Pri jednakom broju ćelija i semenima (63 × 9 × 100) i familija: H64a 16 kontrasta α = 0,02; H64b 4 kontrasta α = 0,01.
