# ITERATION64: replikacija i proširenje mentorovog benchmarka (PROTOKOL v2; faza S0 se zamrzava ovim komitom, ostale faze zasebno)

Izvor pitanja: mentor (preko korisnika, 2026-10-28): GAdapt je dobar, nadmašuje sve algoritme osim jednog, ali je tačniji; cilj je stabilnost i primena u industriji.
Eksperiment mentora: https://github.com/bpzoran/gadapt_experiments, komit `0e388356ba954d17a8d78941bd18a4580cc9d210` (GAdapt diversity mutation, PyGAD random/adaptive mutation,
SciPy DE best1exp; 9 klasičnih funkcija, 2/7/20 dimenzija, stagnacija, 1000 pokretanja). Recenzije: Codex 083, 084 (FREEZE AFTER FIXES, uneto).
Doprinos: replikacija, proširenje i karakterizacija pouzdanosti — NE nova metoda ni teorema (prior art poređenja adaptivnih mutacija na klasičnim funkcijama: Srinivas–Patnaik 1994
10.1109/21.286385; Marsili Libelli–Alba 2000 10.1007/s005000000042). Nema tvrdnje o industrijskoj spremnosti ni opšte superiornosti.
Napomena: dijagnostika brojanja evaluacija (`research/i64/PILOT_NOTES_SR.md`, 8 semena 0..7, Sphere D=2,7) rađena je pre zamrzavanja i NEPREREGISTROVANA je; semena S0 su druga (§6).

## Faze
- **S0** (zamrznuta ovde): replikacija sa stvarnim brojanjem na originalnim 21 ćelijom i četiri originalne konfiguracije, 20 semena, jedno jezgro, originalna stagnacija.
- **R, razvoj, E, I64-I**: estimandi, težine, ciljevi, budžeti, roster i pravila odlučivanja zamrznuti ovde (§2–§5); parametri CMA/IPOP/BIPOP/(1+1)-ES i konkretan roster biraju se samo na razvoju
  i zamrzavaju zasebnim komitom PRE merenja svake faze. S0 nije deo potvrdnog uzorka. I64-I (ORPD i AC dispečing; ≈ 528 M AC poziva, 293–2347 CPU-sati) je zasebna zamrznuta dopuna.

## 1. Replikacija — vernost (S0 i R)
Klon `0e388356…`, originalni GAdapt 0.5.0 (PyPI) i zaključano kompatibilno okruženje (`requirements.txt` mentora; verzije u manifestu). Eksplicitno `saturation_criterias=[20]` (skalarna 20; lista
`[15]` bi je prepisala), populacija 64, elitizam 50%, limit 600 generacija, četiri uključene konfiguracije. Originalne razlike zaustavljanja se zadržavaju (DE: tolerancija `tol=1e-7` i callback
sa `min_delta=1e-12`; PyGAD `saturate_20`; GAdapt `exit_check="min_cost"`, `max_attempt_no=20`). PyGAD: mentorova selekcija po rangu bez vraćanja, BLX-α = 0,5, mutacione verovatnoće 0,1 odnosno [0,6; 0,1].
GAdapt: originalni operatori, mutacioni procenti 60/60, imigracija 0, jedinstvenost isključena. Manifest beleži sva razrešena podešavanja. Eventualna razlika prema istorijskoj biblioteci se prijavljuje.
Funkcije i granice iz mentorovog `functions/` i use-case modula (Rosenbrock zadržava uzak opseg [0,5; 1,5] — zaključak ne obuhvata standardni širi domen).

## 2. Estimandi (zamrznuti za sve faze)
- **Normalizacija.** Za funkciju/dimenziju i: s_i = median_{k=1..4096}[f_i(U_k) − f_i*] > 0, U_k unapred generisane uniformne tačke originalnog domena (seme zapisano, vrednosti arhivirane PRE optimizacije);
  isti s_i za sve algoritme i transformacije. g = max(0, (f − f*)/s_i); vrednost ispod f* − 1e−12·s_i blokira instrument. f* = 0 za sve osim Styblinski–Tang: f* = D(a⁴ − 16a² + 5a)/2, a = negativni
  globalno minimizujući koren 4a³ − 32a + 5 = 0 (visoka preciznost). L = g/(1+g); algoritamski otkaz (bez konačnog rezultata) L = 1; greška instrumenta = STOP.
- **Brojanje.** Jednonitni omotač broji svaki fizički poziv (duplikati, validacione all-min/all-max probe GAdapt-a, PyGAD ručna početna evaluacija i dodatne adaptive evaluacije, `best_solution()`
  ponovna računanja, DE callback); keširan fitnes nije novi poziv. Primarni rezultat = najmanji konačan f među prvim B pozivima (S0: svi pozivi do izvornog završetka), uključujući probe; pri jednakosti prvi vektor.
  Čuvaju se kopija vektora, faza i trag „najbolje do sada“ po pozivu. Izvorni povratni rezultat se beleži odvojeno (pri nasilnom prekidu u E označen nedostupnim).
- **ECDF površina.** Za cilj τ ∈ {1e−2, 1e−4, 1e−6}, T_τ = prvi stvarni poziv sa g ≤ τ, ili ∞. A = (1/(3B)) Σ_τ Σ_{b=1..B} 1(T_τ ≤ b); nedostizanje daje nulu. S0/R: B = 12.000 služi analizi
  putanje (posle izvornog završetka najbolje ostaje konstantno, bez dodatnih poziva); završna preciznost koristi izvorni kraj.
- **CVaR₀,₉** za n = 100: sortirano L rastuće, CVaR = (1/10) Σ_{r=91..100} L_(r) (veze zadržavaju multiplicitet). Agregat = ponderisan prosek ćelijskih CVaR.
- **Težine.** Funkcije 1/9, njihove dimenzije jednaka unutrašnja težina (2D funkcije jedna ćelija), E varijante 1/3. ΔA_j = E_w[A_G − A_j]; ΔM_j = M_j − M_G (M = ponderisan prosek ćelijskih završnih medijana g).
  Neodređene razlike beskonačnosti blokiraju odgovarajući zaključak.

## 3. Hipoteze i pravila odlučivanja
- **H64a (mentorova)**: GAdapt nadmašuje sve konkurente osim najviše jednog, i ima niži završni medijalni jaz od tog izuzetka. Prolazi ako svi konkurenti imaju donju simultanu granicu ΔA > 0, ILI postoji jedan e
  takav da to važi za sve j ≠ e i donja granica ΔM_e > 0. U E se konkurenti uzimaju svih deset (uključujući preset); fokalni GAdapt se ne bira naknadno. Veze nisu pobede.
  Suprotan ishod: dva dokazano efikasnija konkurenta, ili jedan dokazano efikasniji i preciznijeg; ostalo = neodlučeno.
- **H64b (preset)**: R_0 = agregatni CVaR podrazumevanog GAdapt-a > 0; donja granica 0,8·R_0 − R_preset ≥ 0; donje granice razlika verovatnoće dostizanja ≥ −0,05 za sva tri cilja. Dva nulta rizika nisu poboljšanje.
- **Inferencija**: 20.000 stratifikovanih bootstrap uzoraka celih uparenih vektora (po ćeliji); simultani intervali preko maksimalnog standardizovanog odstupanja. Porodice: S0 šest kontrasta (α = 0,01); R šest (0,01);
  E-H64a dvadeset (0,02); H64b četiri (0,01); nominalni FWER ukupno 0,05 (bootstrap nije konačnouzoračka garancija). Nulta procenjena varijansa blokira potvrdu. Snimak na 3000 je opisan. Wilcoxon/rank-biserial samo opisno.

## 4. Konfiguracije proširenja (E, zasebno zamrzavanje) i razvoj
E: GAdapt-M (mentorova konfiguracija) i ista konfiguracija sa presetom (`normal_distribution_mutation_min_std_dev=1e-4`, `…_decay_generations=2.5`; podrazumevano isključeno, bit-identičan trag preset-off),
PyGAD random i adaptive, SciPy DE, CMA sa restartima iste populacije, IPOP-CMA-ES, BIPOP-CMA-ES (`cma`), (1+1)-ES sa restartima; L-SHADE/jDE samo uz validiranu implementaciju (CEC-provera, zasebno okruženje), inače izostavljeno
i prijavljeno. Sve promenljive normalizovane na [0,1]; original f(l + w·y); pomerena/rotirana f(x* + w·Qᵀ(y − o)), w = u − l, o ∈ [0,25; 0,75]^D, Q ortogonalna (Q = I za samo pomeranje); o, Q, x* arhivirani; minimum
dostižan; rotirana Sphere = negativna kontrola (jednaka pomerenoj do tolerancije). U E nema spoljašnje stagnacije: pri izvornom završetku pre B sledi unapred definisan restart sa zajedničkim preostalim budžetom (važi i za DE).
Budžet B = 12.000 stvarnih poziva; spoljni omotač podiže `BudgetReached(BaseException)` pre poziva B+1 (poziv B se potpuno izvršava); proverava se da svaka biblioteka propušta signal; nema lažnog fitnesa.
Samo razvoj bira CMA σ₀, populacije, tolerancije i IPOP/BIPOP raspored, odnosno korak, adaptaciju i restart (1+1)-ES, iz unapred navedenih kandidata uz jednak kalibracioni budžet.
Ponavljanja: 100 semena po ćeliji (R i E); semena §6.

## 5. Procena CPU
T_CPU = [N_f·t_f + Σ_a N_gen,a·h_a + T_start + T_zapis + T_analiza]/3600; početna aproksimacija GAdapt overhead h_G = 0,001·(P/32)·(D/10) s/generaciji. Okvirno: S0 1–2 h (jedno jezgro), R 5–10 h, razvoj 0,5–2 h po
rosteru, E 10–40 h, I64-I zasebno. E sa 11 konfiguracija: 831,6 M poziva (devet: 680,4 M).

## 6. Seme, S0
Sortirana ćelija c = 3i + v (i = indeks funkcije/dimenzije, v varijanta), seme = 64.000.000 + 1.000.000·p + 1.000·c + s; p = 0/1/2/3 za S0/razvoj/R/E; s = 1..20 (S0), 1..5 (razvoj), 1..100 (R, E).
Postavljaju se Python, NumPy i bibliotečki RNG (PyGAD `random_seed`, SciPy DE `seed`, GAdapt preko `random`/`numpy`); isto seme ne znači identičnu početnu populaciju.

## 7. S0 — tačan opseg
21 originalna ćelija × četiri originalne konfiguracije × 20 semena (p = 0, s = 1..20) = 1.680 pokretanja, jedno jezgro, originalna stagnacija, bez dodatnog evaluacionog limita (limit 600 generacija je mentorov).
Objavljuje se: originalni proseci/generacije mentora, stvarni pozivi po pokretanju i fazi, razlika generacije vs pozivi, ΔA i ΔM sa simultanim intervalima (šest kontrasta, α = 0,01), CVaR₀,₉, verovatnoće dostizanja.
Ishod može biti podržano, suprotno ili neodlučeno; GO za kasnije faze zavisi od ispravnosti instrumenta i troška, ne od pozitivnog rangiranja. Create-once identitet (jedan direktorijum `research/results/iteration64_s0`), heševi svih tranzitivnih izvora, manifest. S0 poziva mentorove funkcije `execute_gadapt_experiment`, `execute_pygad_experiment` i
`execute_scipy_de_experiment` NEPROMENJENE, sa `num_runs=1` po semenu; konstrukcije GA/pygad.GA/DE parametara su doslovno one iz `runners/experiment.py` (doslovan prepis parametara, hešovan). Jedina intervencija je
injektovanje semena u SciPy DE (`rng=seed`, mentorov poziv ga ne postavlja) i brojač poziva funkcije cilja (GAdapt: brojač sa `__deepcopy__` koji vraća self jer `GA.execute()` duboko kopira GA). Gateovi pre merenja:
(1) brojanje: zbir faza = ukupan broj poziva omotača, bez negativnih ili dvostrukih brojanja; (2) determinizam: isto seme daje identičan trag poziva u dva izvršavanja za 3 ćelije × 4 konfiguracije (seme van S0 opsega: p = 9);
(3) svedok: najbolji prijavljeni f se reprodukuje nezavisnim ponovnim računanjem iz zapisanog vektora. Greška instrumenta = STOP; tehnički neuspeh pokretanja se ponavlja jednom istim semenom, ponovljen neuspeh = STOP.
Mentorova DE callback evaluacija i PyGAD `best_solution()` se broje kao stvarni pozivi (po Codex 084).
## Obelodanjivanja pre S0 (2026-10-28)
1. Dijagnostika brojanja (`research/i64/PILOT_NOTES_SR.md`): 8 semena (0..7) na Sphere D=2,7; nepreregistrovano; semena van S0 opsega.
2. Probna serija cevovoda (gate, run, analyse) u privremenom direktorijumu sa `S0_SEEDS=3`, `S0_FULL_BOOT=0` (smanjen bootstrap): koristila je semena s=1..3 iz pravog S0 opsega (p=0),
   pa su ishodi tih 3 od 20 semena i agregati bili VIDLJIVI pre pravog pokretanja; nikakva odluka dizajna nije izvedena iz njih. Pravi S0 koristi svih 20 semena.
3. Pokretanje SciPy DE sa injektovanim semenom (`rng=seed`) je jedina izmena mentorovog poziva (mentorov poziv nije seedovan).
