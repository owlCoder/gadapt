# ITERATION49 — revizija integriteta evaluacija u Python optimizacionim bibliotekama (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda alata i pre ijednog posmatranog obrasca poziva.** Datum: 2026-10-23.
- Prior art i odluka GO: [H4_PRIOR_ART_AUDIT_SR.md](H4_PRIOR_ART_AUDIT_SR.md).
- Izvodljivost: [H4_FEASIBILITY_SR.md](H4_FEASIBILITY_SR.md). Tada su biblioteke pokretane samo sa konstantnom funkcijom,
  a obrasci poziva nisu gledani.

## 0. Tvrdnja i pitanje
- **Doprinos (uzak, metodološki):** black-box alat koji:
  - klasifikuje svaki poziv funkcije troška;
  - proverava doslednost prijavljenog rezultata;
  - proverava dokumentovane relacije (budžet, prijavljeni broj evaluacija, reproduktivnost uz seme).

  Prati ga studija rasprostranjenosti na zaključanim verzijama.
- Invarijantnost (pristrasnost ka centru, afine transformacije) i brojanje evaluacija **nisu novi** i služe samo kao
  komponente, uz citiranje Kůdele, BIAS-a, COCO-a, IOH-a, Jiana i Zhua.
- **Pitanje:** koliko je čest bar jedan problem integriteta evaluacija, uz podrazumevanu upotrebu, u popularnim Python
  bibliotekama koje praksa koristi za black-box optimizaciju?

## 1. Biblioteke (fiksirane; verzije u [h4_requirements_lock.txt](h4_requirements_lock.txt))
- **Kriterijum izbora:** popularne Python biblioteke za jednokriterijumsku black-box optimizaciju sa korisničkom
  funkcijom troška nad kutijom, instalabilne na Python 3.14.
- **Uključeno (9):** pymoo 0.6.2 (GA), DEAP 1.4.4 (`eaSimple`), PyGAD 3.9.2, geneticalgorithm 1.0.2, Nevergrad 1.0.12
  (`NGOpt`), Optuna 5.0.0 (podrazumevani sampler, TPE), PySwarms 1.3.0 (`GlobalBestPSO`), cma 4.5.0 (`fmin2`),
  SciPy 1.18.1 (`differential_evolution`).
- **Isključeno:** mealpy (build ne uspeva).
- **GAdapt** (`owlCoder/gadapt` na komitu ovog protokola) je **pozitivna kontrola** sa poznatim probnim pozivima.
  Prijavljuje se odvojeno i ne ulazi u stopu rasprostranjenosti.

## 2. Konfiguracije (podrazumevane, osim budžeta i semena)
Budžet je zadat preko dokumentovanog parametra, sa ciljem od oko 1000 evaluacija:

| Biblioteka | Budžet | Seme | Prijavljeni rezultat | Prijavljeni broj evaluacija |
|---|---|---|---|---|
| pymoo GA (pop 100) | `("n_evals", 1000)` (dokumentovani maksimum) | `seed` | `res.X`, `res.F` | `res.algorithm.evaluator.n_eval` |
| DEAP `eaSimple` (pop 50, cxBlend 0,5, mutGaussian σ = opseg/10 i indpb 0,1, turnir 3, cxpb 0,5, mutpb 0,2) | `ngen = 19` (nema dokumentovanog broja evaluacija) | `random.seed` | `HallOfFame(1)` | zbir `nevals` u logbook-u |
| PyGAD (sol_per_pop 50, num_parents_mating 10) | `num_generations = 19` | `random_seed` | `best_solution()` | — |
| geneticalgorithm (population 50) | `max_num_iteration = 19`, `max_iteration_without_improv=None` | `numpy.random.seed` | `output_dict` | — |
| Nevergrad `NGOpt` | `budget = 1000` (dokumentovano: broj dozvoljenih evaluacija) | `parametrization.random_state` | `minimize` (dokumentovano: kandidat sa minimalnom vrednošću) | `num_tell` |
| Optuna (TPE) | `n_trials = 1000` | `TPESampler(seed)` | `best_params`, `best_value` | `len(trials)` |
| PySwarms GlobalBestPSO (50 čestica, c1 0,5, c2 0,3, w 0,9) | `iters = 19` | `numpy.random.seed` | povratni `(cost, pos)` | — |
| cma `fmin2` (x0 = centar, σ0 = 0,3 · opseg) | `maxfevals = 1000` (dokumentovani maksimum) | opcija `seed` | `xbest`, `es.result.fbest` | `es.result.evaluations` |
| SciPy DE (podrazumevano, uključujući `polish=True`) | `maxiter = ⌊1000 / (15·N)⌋ − 1` (dokumentovana formula važi **samo bez poliranja** → D1 nije primenljivo) | `rng` | `res.x`, `res.fun` | `res.nfev` |
| GAdapt (kontrola) | `exit_check="generations"`, 40 generacija | `random`, `numpy.random` | `min_cost`, `result_values` | — |

## 3. Problemi i ponavljanja
- **Funkcije:** pomerena sfera (optimum na 0,37 opsega), Rastrigin i plato `Σ ⌊x_i⌋`.
- **Dimenzije i kutija:** N ∈ {2, 10}, kutija [−5, 5]^N.
- **Semena:** 5 (6000–6004).
- **Ukupno:** 9 biblioteka + GAdapt, × 6 problema × 5 semena, plus po jedno ponovljeno pokretanje sa istim semenom (D3).

## 4. Mere (sve iz omotača koji beleži svaki poziv: redni broj, x, f, faza)
- **C1 probni pozivi na uglovima:** x je jednako vektoru svih donjih ili svih gornjih granica.
- **C2 tačni duplikati:** x je bitski jednako ranije evaluiranom x. Prijavljuje se kao udeo rasipanja, ne kao kršenje.
- **C3 van granica:** bar jedna koordinata je van [lo, hi].
- **C4 preko dokumentovanog maksimuma:** samo tamo gde je maksimum dokumentovan (pymoo, Nevergrad, Optuna, cma).
- **C5 pozivi posle povratka:** pozivi tokom izdvajanja prijavljenog rezultata, posle povratka glavne funkcije
  optimizatora.
- **R1 prijavljeno x\* nije evaluirano:** nijedan zabeleženi x nije jednak x\* (tolerancija 1e-12 po koordinati).
- **R2 neslaganje vrednosti:** prijavljeno f\* se razlikuje od zabeleženog f(x\*) (relativno > 1e-9).
- **R3 prijavljeno nije najbolje:** prijavljeno f\* je veće od minimuma zabeleženih f u fazi pretrage (relativno > 1e-9).
- **D2 netačan prijavljeni broj evaluacija:** prijavljeni broj se razlikuje od stvarnog (gde biblioteka izveštava broj).
- **D3 nereproduktivno:** dva pokretanja sa istim semenom, dokumentovanim mehanizmom, daju različit heš niza poziva.
- **Sekundarno, invarijantnost G1:** afina promena jedinica po promenljivoj (x → a·x + b, granice preslikane isto), isto
  seme. Da li je niz poziva u normalizovanim koordinatama isti (≤ 1e-9)? Ovo je **svojstvo, ne greška**, i citira se
  prior art.

## 5. Primarni ishod i odluka
- **Nalaz integriteta za biblioteku:** bar jedan od C1, C3, C4, C5, R1, R2, R3, D2 ili D3, u bar jednom pokretanju.
- **Primarno:** broj biblioteka (od 9) sa nalazom, uz Clopper–Pearson 95% interval.
  - **ČESTO:** ≥ 3/9.
  - **RETKO:** ≤ 1/9.
  - **IZMEĐU:** 2/9.
- **Razvrstavanje nalaza (post hoc, eksplicitno):**
  - greška / dizajnerska odluka / praznina u dokumentaciji;
  - već prijavljeno u issue tracker-u / novo. Pretraga se radi posle pokretanja, po unapred datim terminima iz audita.

## 6. Validacija alata (pre glavnog pokretanja; mora proći)
- **Referentni optimizator:** nasumična pretraga sa dokumentovanim budžetom koja vraća najbolju tačku.
- **Pet mutanata,** svaki sa jednom podmetnutom greškom: ugaoni probni poziv, ponovna evaluacija duplikata, jedan
  poziv preko budžeta, prijava neevaluirane tačke, prijava pogrešne vrednosti.
- **Kriterijum:** alat označava **tačno** podmetnutu klasu kod svih 5 mutanata (osetljivost 5/5), a čistu referencu
  ne označava ni za jednu klasu (specifičnost).
- **GAdapt sa podrazumevanim podešavanjima mora dati C1.** Sa `probe_cost_function=False` ne sme dati C1.

## 7. Etika i arhiviranje
- Nalazi se pre ikakve objave šalju održavaocima. Otvaranje issue-a je spoljna radnja i traži posebno odobrenje
  korisnika.
- Izlaz: `research/results/iteration49/integrity_audit.json` i `ITERATION49_REPORT_SR.md`, i negativni.
- Jedno pokretanje; bez menjanja konfiguracija posle gledanja rezultata.
