# ITERATION57: GAdapt naspram spoljnih metoda na istom diskretnom ORPD-u (PREREGISTRACIJA)

**Status: ZAMRZNUTO 2026-10-24, PRE ijednog I56 test rezultata** (u trenutku zamrzavanja I56 je imao samo
razvojne faze `dev_ref`, `dev_fxm`; `dev_fxt` u toku). Predlog: [ITERATION57_PROPOSAL_SR.md](ITERATION57_PROPOSAL_SR.md);
recenzija: Codex 027 (tekst ispod je njegov predloženi zamrznuti tekst, uz odluku o L-SHADE/jDE).

## Obim
I57 je **opisno poređenje** na fiksnom I56 skupu instanci, bez konfirmatornih hipoteza o superiornosti, bez
tvrdnje o novoj metodi i bez generalizacije van ovih instanci. Konfiguracije: GAdapt AD-N/SP i AD-N/FR;
CMAwM/SP i CMAwM/FR; SciPy DE/SP i DE/FR; uniformna nasumična pretraga. Nijedna konfiguracija se ne bira na osnovu
I56 test ishoda. L-SHADE / jDE nisu deo I57 (implementacije bi tražile zasebnu validaciju; eventualno kasnija
iteracija sa sopstvenim protokolom).

## Reprezentacija i podešavanja
Spoljni metodi koriste indekse k_j ∈ {0, …, R−1}, dekodirane kao `lo + k*step`.
- **CMAwM** (`cmaes` 0.13.1, Hamano i sar. 2022, [10.1145/3512290.3528827](https://doi.org/10.1145/3512290.3528827)):
  granice [0, R−1], jedinični koraci, srednja vrednost u sredini, sigma (R−1)/3, ostala podrazumevana podešavanja;
  `x_for_eval` se evaluira, a `x_for_tell` se predaje `tell()` uz njegov skalar. `should_stop()` se ne koristi.
- **SciPy DE** (1.18.1): `best1bin`, `popsize=15`, mutation (0,5, 1), recombination 0,7, `init="latinhypercube"`,
  `updating="immediate"`, `workers=1`, `vectorized=False`, `integrality=True` (na svim koordinatama),
  `constraints=()`, `polish=False`, `maxiter=10**9`, `tol=0`, `atol=-1`.
- **Nasumična pretraga:** nezavisne uniformne celobrojne koordinate sa vraćanjem; jedna putanja daje obe CHT
  procene (skalar ne utiče na pretragu).
- Ovo su konfiguracije ograničene budžetom.

## Evaluacija i zaustavljanje
Ponovo se koriste I56 merilo, sirovi ishodi, FR/SP skalari (FR adapter eksplicitno primenjuje `CHT("FR").merit(raw)`;
direktan poziv `Evaluator`-a bi tiho bio SP), izvodljivost, konvencije neuspeha, ciljevi i T. Svako uspešno
pokretanje izvršava tačno 3000 stvarnih `runpf` poziva, uključujući inicijalizaciju, ponovljene evaluacije i
neuspele PF. Keširana skalarizacija ne izvršava PF. Zaustavljanje na budžetu bez obzira na dostizanje cilja. CMA u
poslednjoj generaciji evaluira samo preostale kandidate, bez delimičnog `tell`; DE omotač podiže namenski izuzetak
pre poziva 3001. Ishodi dolaze isključivo iz omotača. Završetak budžetom je uspešan završetak bez obzira na
`success` rešavača; ostale greške izvršavanja prate I56 pravila ponovnog pokretanja, izuzimanja i osetljivosti.

## Semena i reference
I56 formula semena sa namenom 5 i s = 1..10, upareno po konfiguracijama; svaki RNG se eksplicitno seje. Ista oznaka
semena ne znači istu početnu populaciju. I56 `test_ref` ciljevi se koriste nepromenjeni; njihovi heševi se
arhiviraju pre I57 pokretanja. Ciljevi potiču iz GAdapt referentnih pokretanja (navesti kao ograničenje).

## Analiza
Šest kontrasta: CMA, DE i nasumična pretraga naspram GAdapt-a pod istim CHT-om. Procena: srednja
T(metod) − T(GAdapt) sa jednakim težinama blokova i jednakim težinama preostalih scenarija u bloku. Uzorkuju se celi
upareni vektori unutar ćelija mreža × R × scenario: 20.000 ponavljanja, seme 57, tačkasti 95% percentilni
intervali. Bez p-vrednosti, bez proglašavanja značajnosti i bez tvrdnji o ekvivalenciji. Dostizanje, izvodljivost i
najbolji izvodljiv gubitak se prijavljuju odvojeno. Pre pokretanja: validacija adaptera (tačno 3000 poziva,
dekodiranje, skalar) i heševi okruženja/koda.

## Budžet
7 putanja × 30 važećih instanci × 10 semena × 3000 = 6,3 miliona PF poziva ≈ 5,25 CPU-sati (bez pripreme i
ponavljanja). Izvršava se POSLE I56 analize.
