# ITERATION50: potvrdna replikacija revizije integriteta evaluacija (IZVEŠTAJ)

**Datum:** 2026-10-23. Merenje je pokrenuto jednom.
- Protokol: [ITERATION50_PROTOCOL.md](ITERATION50_PROTOCOL.md) (`c3598f6`).
- Prihvatljivost, konfiguracije i citati: [ITERATION50_ELIGIBILITY.md](ITERATION50_ELIGIBILITY.md) (`a5554f8`),
  zamrznuti pre pokretanja.
- Sirovi izlazi: [results/iteration50/](results/iteration50/) (`cells_<lib>.json` sa `pip freeze` po biblioteci,
  `integrity_audit.json`, `classification.json`, `validation.json`).
- Kod: [iteration50_integrity_audit.py](iteration50_integrity_audit.py) i
  [iteration50_classify.py](iteration50_classify.py). I49 klasifikator je korišćen bez izmene.

## 1. Odgovor ukratko
- **Preregistrovani primarni ishod:** 11 od 12 biblioteka ima bar jedan nalaz integriteta (95% CI 62–100%), pa je
  presuda **PONOVLJENO (ČESTO)**.
  - Taj broj je, međutim, naduvan merom C1 (§3). Bez C1 ostaje **4/12** (CI 10–65%), što bi po istim pragovima bilo
    NEODLUČENO (donja granica 0,099 < 0,10). Ova analiza je **post hoc**.
- **Protivreči dokumentaciji (unapred zadato pravilo):** **2/12** (CI 2–48%): GFO i SMAC. Oba nalaza su **nova**,
  potvrđena na glavnoj grani i prijavljena (§5).
  - Zajedno sa I49 (2/9): **4/21** (CI 5–42%).
- **Odbranjiva tvrdnja:** problemi integriteta koji nisu C1 pojavljuju se u oko trećine biblioteka. U I50 je to 4/12,
  a zajedno sa I49 8/21 (38%, CI 18–62%). Jedno automatsko pokretanje alata našlo je dve ranije neprijavljene
  greške koje protivreče dokumentaciji.

## 2. Validacija alata (pre glavnog pokretanja)
11 od 11 provera je prošlo:
- 5 I49 mutanata i čista referenca;
- GAdapt sa probnim pozivom i bez njega;
- čista referenca bez D3 i D3x;
- `hash_seeded` daje samo D3x;
- `time_seeded` daje D3 i D3x.

## 3. Glavni problem validnosti: C1 nije specifičan
C1 (x tačno jednako vektoru svih donjih ili svih gornjih granica) uveden je u I49 da uhvati probne pozive kakve
pravi GAdapt validator. U I50 se javlja kod 9 biblioteka, ali skoro uvek kao legitimna evaluacija:
- **Usred pretrage, posle sečenja na granici ili kad optimum akvizicije padne u ugao:** evox (pozivi 108–177),
  EvoloPy, NiaPy, bayes_opt i emukit (post hoc 2D dijagnostika:
  [c1_positions_posthoc.txt](results/iteration50/c1_positions_posthoc.txt)).
- **Namerna inicijalizacija:** GFO `initialize` podrazumevano uključuje `"vertices": 4` (pozivi 7 i 9); baybe
  početni dizajn (poziv 1).
- **Plato `Σ⌊x_i⌋`:** donji ugao je područje globalnog optimuma, pa je C1 tu evaluacija optimuma (bofire 190/200
  tačaka na granici).

Zato C1 ne meri problem integriteta za ove algoritme. U I49, 4/9 nije sadržalo nijednu biblioteku samo sa C1, pa je
poređenje sa I49 smisleno samo bez C1. **Pouka za alat (za buduću verziju, ne retroaktivno):** C1 treba ograničiti
na pozive koje biblioteka pravi izvan svoje pretrage (npr. validacija ulaza pre prve generacije), a ne na sve tačke u
uglu.

## 4. Rezultati po biblioteci (30 ćelija; N ∈ {2, 10}; sfera, Rastrigin i plato; budžet 200)

| Biblioteka | Klase (broj pokretanja) | R | Medijana duplikata | Razvrstavanje (unapred) | Poznato? |
|---|---|---|---|---|---|
| GFO 1.13.0 | **R2 (25)**, **R3 (10)**, C1 (15) | da | 0 | **protivreči**: `best_score` je negiran uz `optimum="minimum"` | **novo** → [GFO #106](https://github.com/gfo-project/Gradient-Free-Optimizers/issues/106) |
| SMAC 2.4.1 | **D3x (30)**, bez D3 | da | 0 | **protivreči**: seme „to make results reproducible“ | **novo** → [SMAC #1380](https://github.com/automl/SMAC3/issues/1380) |
| scikit-opt 0.6.6 | **R3 (1)**, C2 (30) | da | **47%** | praznina u dokumentaciji (nema citata „najbolje“) | povezano: [sko #187](https://github.com/guofei9987/scikit-opt/issues/187) (samo naslov) |
| evotorch 0.6.1 | **C3 (30)** | da | 0 | dizajn: SNES ne podržava granice, README koristi samo `initial_bounds` | — |
| bayes_opt 3.4.0 | C1 (18) | da | 0 | — | — |
| emukit 0.5.1 | C1 (20), C2 (9) | n/a | 0 | — | — |
| baybe 0.15.0 | C1 (18), C2 (10) | n/a | 0 | — | — |
| bofire 0.5.0 | C1 (11), C2 (10); 2 timeout-a | n/a | 0 | — | — |
| evox 1.4.0 | C1 (15), C2 (13) | da | 0 | — | — |
| EvoloPy 4.0.6 | C1 (9), C2 (30) | da | 1,3% | — | — |
| NiaPy 2.7.1 | C1 (3), C2 (22) | da | 0,5% | — | — |
| cmaes 0.13.1 | nema | n/a | 0 | — | — |

- Nijedna biblioteka nema D3 (reproduktivnost u istom procesu), C4, C5, R1 ni D2.
- D3x, nova mera, otkrila je SMAC. Postojeći D3 to ne bi otkrio.
- **Greške:** bofire, Rastrigin 10D, semena 6001 i 6004: timeout (> 1200 s za dva pokretanja). Ostale ćelije su
  završene. Nijedna biblioteka nije neocenljiva.

## 5. Mehanizmi, uzročno provereni posle pokretanja

**GFO (R2/R3).** `search()` uz `optimum="minimum"` negira funkciju, a `best_score` vraća negiranu vrednost iz
`SearchTracker`-a. `search_data` je negiran na isti način. Docstring kaže: „The reported `best_score` is in original
(non-negated) units.“
- Minimalni primer na 1.13.0 i na `main` (`a3ef5471`): `best_score = -1.00003`, a `f(best_para) = 1.00003`.
- `best_para` je tačan.

**SMAC (D3x).** `LocalSearch._get_initial_points` vraća `list(set(...))` nad `Configuration` objektima, a
`Configuration.__hash__` je `hash(repr)`. Redosled početnih tačaka zato zavisi od `PYTHONHASHSEED`.
- Sa podrazumevanom heš randomizacijom, tri pokretanja sa `seed=0` daju tri različita incumbenta.
- Razilaženje počinje na evaluaciji 20 (2D), tj. na prvom predlogu modela.
- Deduplikacija koja čuva redosled (`dict.fromkeys`) daje isti niz za `PYTHONHASHSEED` 1, 2 i 3 (2D) i za 1 i 2
  (Rastrigin 10D, 200 pokušaja). Zakrpa se primenjuje na `main` (`84148879`).

**scikit-opt DE (R3, duplikati).**
- **Duplikati:** `selection()` u svakoj iteraciji ponovo evaluira roditelje i probne vektore. `run()` zatim još
  jednom evaluira najbolje rešenje. Ishod: 301 poziv za nominalnih 200 (6 × 50 + 1), sa samo 124 jedinstvene
  tačke u ćeliji sfera 2D.
- **R3:** posle selekcije, `self.Y` sadrži samo vrednosti probnih vektora, a `run()` iz njega bira najbolje. Zadržani
  roditelj koji je bolji od svih probnih vektora zato se ne vidi. U ćeliji plato 10D, seme 6004, prijavljeno je −22,
  a evaluirano −23 (poziv 11).
- Po unapred zadatom pravilu ovo nije protivrečnost dokumentaciji, pa se po protokolu §7 ne prijavljuje.

**bayes_opt (van klasa, praktično).** Na platou, ponovljeni predlog se ne evaluira (`TargetSpace.probe` vraća
keširanu vrednost), ali troši iteraciju. Rezultat: 7 umesto 200 evaluacija (2D, seme 6000) i 20–42 u 10D, bez
upozorenja. Ponašanje je dokumentovano u `TargetSpace.probe`.

## 6. Odstupanja i ograde
- **Tehnička provera pune veličine** (konstantna funkcija, 10D, budžet 200) dodata je posle protokola, a pre
  pokretanja. Gledani su samo završetak i trajanje.
- **Ograničenje niti:** BLAS i OpenMP su ograničeni na 1 nit po procesu (zapisano pre pokretanja).
- **Prihvatljivost:** pravilo smoke testa primenjeno je strogo. gaft je isključen zbog deljenja nulom na konstantnoj
  funkciji, što verovatno nije relevantno za stvarnu upotrebu.
- **Okvir uzorka:** GitHub teme i prag od 300 zvezdica ne obuhvataju sve. Na primer, NiaPy (281 zvezdica) ušao je samo
  preko izvora B (Ravber i sar. 2025).
- **Neprimenljive provere:** R1–R3 nisu primenljivi za 4 ask/tell biblioteke. C4 je primenljiv samo za 4 biblioteke.
- **Post hoc analize:** C1 analiza i provere mehanizama su post hoc i tako su označene. Preregistrovani ishod je
  prijavljen kakav jeste.

## 7. Zaključak za tezu
- Alat se uopštava na novih 12 biblioteka bez izmene klasifikatora.
- D3x je dodao stvarnu vrednost: otkrio je SMAC.
- Jedno pokretanje od oko 81 minut (dve paralelne trake) našlo je dve nove greške koje protivreče dokumentaciji. Obe su potvrđene na
  glavnoj grani i prijavljene održavaocima.
- Mera C1 se pokazala nespecifičnom. To je negativan metodološki nalaz koji ide u poglavlje: tvrdnja „često“ zavisi
  od definicije klase, a robustna procena bez C1 je oko trećine biblioteka.
- **Praktična preporuka ostaje ista:** pre poređenja optimizatora na skupoj funkciji pokrenuti reviziju integriteta,
  i reproduktivnost proveravati **između procesa**, ne samo unutar procesa.
