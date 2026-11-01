# ITERATION55 (rad: Studija 5) — ispravljeni D3x sa stvarnim heš semenima i arhiva kompletnih tragova poziva

**Status: preregistrovano pre koda.** Datum: 2026-10-23. Razlog: nezavisna recenzija rada (Codex 009) i moja provera:
drajveri I50–I52 (i alat za praksu) pokretali su interpreter biblioteke sa `python -I`, koji podrazumeva `-E` i
ignoriše `PYTHONHASHSEED`. D3x je zato poredio dva procesa sa nezavisnim nasumičnim heširanjem stringova, a ne
semena 1 i 2. Takođe, arhiva I49–I52 nema kompletne tragove poziva, pa se klase ne mogu nezavisno ponovo izračunati.

## 1. Obim

- Svih 21 biblioteka, iste ćelije kao u I49 (9 biblioteka, budžet 1000) i I50 (12 biblioteka, budžet 200):
  3 test-funkcije × N ∈ {2, 10} × semena 6000–6004 = 30 ćelija po biblioteci; isti adapteri i konfiguracije
  (`research/iteration49_integrity_audit.py`, `research/iteration50_integrity_audit.py`, nepromenjeni).
- Okruženja: I49 uzorak iz `research/h4_requirements_lock.txt`; svaka I50 biblioteka iz svog arhiviranog `pip freeze`
  (`research/results/iteration50/cells_<lib>.json`). Verzije se ponovo beleže.
- Dispečing (I52) nije u obimu (posebna odluka).

## 2. Postupak po ćeliji

Tri sveža procesa, pokrenuta sa `-s` i `PYTHONSAFEPATH=1` (bez `-I`), svaki beleži kontrolni heš
`hash("integrity-audit-sentinel")`:
- **A:** `PYTHONHASHSEED=1`, pokretanje + ponovljeno pokretanje u istom procesu (D3).
- **A′:** `PYTHONHASHSEED=1`.
- **B:** `PYTHONHASHSEED=2`.
Provera manipulacije: kontrolni heš A = A′ i A ≠ B; u suprotnom ćelija je nevažeća i prijavljuje se.

Mere: D3 (A naspram ponovljenog A), **D3x_isto** (A naspram A′), **D3x_razl** (A naspram B), uz sve klase iz Dodatka A
rada, izračunate iz tragova procesa A. Arhivira se kompletan trag procesa A (x, f, faza za svaki poziv; kompresovano)
i vraćeni rezultat (x\*, f\*, broj evaluacija), kao i heševi A, A′ i B.

## 3. Hipoteze (pre merenja)

- **H55a:** skup biblioteka sa D3x_razl > 0 u bar jednoj ćeliji jednak je {Nevergrad, SMAC} (nalaz Studija 2–3).
- **H55b (SMAC, atribucija na heš seme unutar revizije):** SMAC ima D3x_isto = 0 u svih 30 ćelija i D3x_razl > 0 u
  bar 25/30.
- **H55c (Nevergrad, uzrok nije heš):** Nevergrad ima D3x_isto > 0 u bar jednoj ćeliji (seme iz sata u `cma.fmin`).
- **H55d (reproduktivnost arhive):** za biblioteke bez D3 i D3x, zastavice izračunate iz novih tragova jednake su
  arhiviranim zastavicama iz I49/I50 u svim ćelijama; svako odstupanje se prijavljuje sa uzrokom.
- Odluka: svaka hipoteza se prijavljuje posebno kao PODRŽANO / NIJE PODRŽANO; nema zbirne presude.

## 4. Arhiva i ponovni račun

Kod `research/iteration55_d3x_traces.py`, testovi `research/test_iteration55_d3x_traces.py`, izlazi
`research/results/iteration55/` (po biblioteci: JSON sa ćelijama + `traces_<lib>.npz`), i skripta
`research/iteration55_recompute.py` koja iz tragova ponovo izračunava sve brojeve iz §6.1 rada i tabele Studija 1–2.

## 5. Budžet

21 × 30 ćelija × 4 izvršavanja (A dva puta, A′, B) × 200–1000 evaluacija jeftinih test-funkcija; vreme dominira
SMAC i Bayesove biblioteke (I50: SMAC 1635 s za 2 izvršavanja po ćeliji). Procena: nekoliko sati na 4–8 radnika.

## Odstupanje u izvršavanju (zabeleženo tokom merenja, 2026-10-23; Codex 011)

- **O1:** argument `twice` se u ćeliju prenosi kao string; `"0"` je istinit, pa i procesi A′ i B rade ponovljeno
  pokretanje: 6 izvršavanja po ćeliji umesto 4. Merene veličine se ne menjaju (D3x koristi heš PRVOG izvršavanja u
  svakom procesu; D3 samo iz A). Posledice: ~50% više vremena; greška u suvišnom ponavljanju bi poništila poređenje
  (prijavljuje se po ćeliji). Kod se NE menja dok merenje traje (podprocesi ga učitavaju pri svakom pokretanju);
  ispravka posle završetka.
- **O2:** skripta za ponovni račun (`iteration55_recompute.py`, ne izvršava se tokom merenja) ispravljena pre analize:
  nevažeća poređenja se ne broje kao nule; odvojeni imenioci (trag / važeće poređenje); provera kompletnosti.
- **O1 (nastavak, 21:15):** I49 uzorak (9 biblioteka) i baybe rađeni su sa 6 izvršavanja po ćeliji. Petlja je
  zaustavljena posle pokretanja baybe-a (baybe završava sa istim kodom). Ispravka samo na strani drajvera
  (`""` umesto `"0"`; funkcija ćelije nepromenjena), provereno: ponavljanje samo u procesu A. Preostalih 11 biblioteka
  (bayes_opt, bofire, cmaes, emukit, evolopy, evotorch, evox, gfo, niapy, scikit_opt, smac) radi sa 4 izvršavanja po
  ćeliji, paralelno u dve grupe. Merene veličine su iste u oba režima.
- **O3 (otkriveno u međurezultatu H55d, 21:35):** drajver I55 postavlja OMP/MKL/OPENBLAS niti na 1, ali ne i
  `VECLIB_MAXIMUM_THREADS=1` (Apple Accelerate), koji je I50 postavljao. Posledica: emukit 10/30 ćelija (sve N = 2)
  daje drugačiji niz poziva od arhive I50, uz D3 = D3x = 0 unutar I55. Post hoc dijagnostika
  (`research/results/iteration55_posthoc/emukit_veclib.json`): sa `VECLIB_MAXIMUM_THREADS=1` svih 10/10 ćelija
  poklapa arhivu bit po bit → uzrok je broj BLAS niti, ne biblioteka. D3/D3x unutar I55 ostaju važeći (isto okruženje
  u A, A′, B). Za biblioteke koje su tada još radile (baybe, bofire, bayes_opt, smac) poređenje sa arhivom (H55d)
  tumači se uz ovu ogradu i, gde se ne poklapa, proverava istom dijagnostikom.
