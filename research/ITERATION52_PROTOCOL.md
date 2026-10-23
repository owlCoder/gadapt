# ITERATION52: da li se nalazi integriteta prenose na stvarnu infrastrukturnu funkciju troška? (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda i pre pokretanja.** Datum: 2026-10-23.

## Obavezni elementi (CLAUDE.md)
- **Pitanje:** I49–I51 su merili integritet na sintetičkim funkcijama (sfera, Rastrigin, plato). Da li isti nalazi
  postoje kada je funkcija troška stvaran AC ekonomski dispečing (pypower `runpf`, MATPOWER slučajevi)? Ovo odvaja
  sintetičku validaciju od dokaza na stvarnoj infrastrukturi.
- **Prior art i novina:** kao H4. Nema nove tvrdnje; ovo je test spoljne validnosti.
- **Hipoteza H52 (falsifikovana ako):** status po biblioteci („bar jedan nalaz integriteta bez C1“) na dispečingu
  poklapa se sa sintetičkim statusom za **≥ 17/21** biblioteka (≥ 80%). Hipoteza je opovrgnuta ako se poklapa ≤ 16/21.
  - Sintetički status: I49 + I51 (D3x) za uzorak 1, I50 za uzorak 2. Uvek bez C1.
- **Kontrole:** D3x validacija iz I50 ponavlja se pre pokretanja. GAdapt (podrazumevano, sa probnim pozivima) je
  pozitivna kontrola za C1, ali se ne broji.
- **Budžet:** CPU. Jedna evaluacija traje 3–16 ms. Timeout je 600 s po pokretanju.
- **GO.**

## Dizajn (zamrznuto)
- **Funkcija troška:** `Dispatch(case).evaluate(pg)["score"]` iz `research/iteration47_invariance.py`, bez izmene:
  troškovi generatora plus kazne za napone, slack, Q i opterećenje grana. Promenljive su PG neslack generatora,
  u granicama [PMIN, PMAX] u MW.
- **Slučajevi:** case14 (4 promenljive), case39 (9) i case118 (53). Semena 6000–6004. **15 ćelija po biblioteci.**
- **Biblioteke i adapteri:** svih 21, sa **nepromenjenim** adapterima.
  - Uzorak 1 (I49): budžet 1000, okruženje iz `h4_requirements_lock.txt`.
  - Uzorak 2 (I50): budžet 200, venv po biblioteci iz I50.
  - U svako okruženje se dodaje `pypower==5.1.19` (kao u I47).
- **Mere:** I49 klasifikator bez izmene (C2–C5, R1–R3, D2), plus D3 i D3x kao u I50, sa istim pravilom „R n/a“.
  **C1 se ne broji kao integritet** (I50 §3), samo se prijavljuje.
- **Primarno:** broj biblioteka (od 21) čiji se status poklapa. Sekundarno:
  1. poklapanje po klasama, tj. koje sintetičke klase se javljaju i na dispečingu;
  2. medijana udela duplikata (C2) i procenjeno vreme potrošeno na duplikate (C2 × izmereno prosečno vreme
     evaluacije po slučaju).
- **Neocenljivo:** biblioteka kojoj se svih 15 ćelija završi greškom izuzima se iz brojioca i imenioca i prijavljuje
  posebno.
- **Jedno pokretanje.** Izlaz `research/results/iteration52/` i `ITERATION52_REPORT_SR.md`.

## Dopuna A1 (2026-10-23, pre ijednog izmerenog poziva)
- **Prvo izvršavanje nije dalo merenje.** Svih 315 ćelija palo je pri uvozu, pre ijedne evaluacije funkcije troška.
  Arhivirano je u `results/iteration52/failed_run_env/`.
  - Uzrok 1: ponovo korišćeni modul `iteration47_invariance` uvozi `iteration43_budget_operator_diagnostic`, koji
    zahteva `networkx`, a toga nije bilo u okruženjima biblioteka.
  - Uzrok 2: `pypower==5.1.19` uvozi `numpy.in1d`, koji NumPy 2.4+ nema.
- **Ispravka podatka iz protokola:** I47 nije koristio 5.1.19. I47 skripta beleži fiksnu podrazumevanu vrednost
  „5.1.19“, jer pypower nema `__version__`, a 5.1.19 se sa NumPy 2.5.4 ne može uvesti. Repo `.venv` ima 5.1.21.
- **Promena:** u sva okruženja se instaliraju `pypower==5.1.21` i `networkx==3.7`, iste verzije kao repo `.venv`.
  Ostatak protokola se ne menja. Pre ponovnog izvršavanja, u svakom okruženju se proveravaju uvoz i jedna
  evaluacija `Dispatch("case14")` u sredini kutije (bez optimizatora).
