# ITERATION46 — ablacija: koja GAdapt komponenta uzrokuje deficit na binarnom izboru ruta? (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda i pre pokretanja.** Datum: 2026-10-22. Prethodno: [ITERATION45_REPORT_SR.md](ITERATION45_REPORT_SR.md)
(deficit je specifičan za GAdapt). Dijagnostika (lokalizacija uzroka), bez tvrdnje o novini.

## 1. Pitanje
Koja od razlika GAdapt-a u odnosu na udžbenički GA objašnjava deficit? Svaki krak menja **tačno jednu** komponentu
GAdapt-I39 ka udžbeničkoj vrednosti, koristeći **postojeće** GAdapt opcije. Biblioteka se ne menja.

## 2. Krakovi (validacioni pozivi isključeni kao u I44; izlaz samo po budžetu)
| Krak | Promena u odnosu na GAdapt-I39 |
|---|---|
| A0 | nema (GAdapt-I39, identično kao u I44/I45) |
| A1 | `parent_selection="tournament"` (umesto ruleta) |
| A2 | `crossover="uniform"` (umesto „blending“) |
| A3 | `keep_elitism_percentage=4` (čuva se 1 od 24, umesto 12 od 24) |
| A4 | A1 + A2 + A3 |
| A5 | A4 + `candidate_solution_mutation="random"`, `number_of_mutation_decision_variables=1` (paket iz I44-m1) |
| TB | udžbenički GA iz I45 (referenca) |
| EA | (1+1)-EA iz I43 (referenca) |

Vrednosti su fiksirane unapred, prema udžbeničkoj kontroli iz I45. Nijedna se ne podešava.

## 3. Instance i semena
- Šest instanci iz I43 (`polska`, `nobel-germany`, `atlanta`, `france`, `geant`, `germany50`), uz istu sintetičku cenu.
- Ovo je **razvojni skup**: I43 je na njemu već video GA-I39 i EA. Ponovna upotreba je prihvatljiva jer se ništa ne
  podešava, ali rezultat ablacije pre bilo kakve tvrdnje treba potvrditi na I44/I45 instancama (§6).
- Semena 4600–4611, budžet 10.000, kontrolne tačke {360, 2000, 10000}, ishod `r` kao u I43.

## 4. Statistika i odluka (B = 10000)
- **Primarno (porodica P, Holm preko 3 × 6 = 18 testova):** A1, A2 i A3, svaki vs A0, uparen dvostrani Wilcoxon.
  Komponenta je **uzročna** ako je krak značajno bolji od A0 na ≥ 4/6 instanci.
- **Sekundarno (porodica S, Holm preko 2 × 6 testova):** A4 i A5 vs TB.
  - **„Deficit objašnjen“:** krak nije značajno lošiji od TB na ≥ 4/6.
  - **„Deficit nije objašnjen“:** krak je značajno lošiji od TB na ≥ 4/6.
- Opisno: sve kontrolne tačke, svi krakovi vs EA.
- Moguće je da nijedna pojedinačna komponenta nije uzročna, a da kombinacija jeste. To se prijavljuje kao takvo.

## 5. Kontrole pre pokretanja
- Svaki krak se konstruiše i izvršava na sintetičkom grafu sa malim budžetom; `ValidatorFree` provera prolazi.
- A3: `keep_number == 1` (iz `GAOptions`), A0: `keep_number == 12`.
- `git diff gadapt/` je prazan.

## 6. Potvrda (preregistrovana sada, izvršava se samo ako primarni ili sekundarni ishod imenuje uzrok)
Isti dizajn, ali samo krakovi A0, imenovani krak (ili kombinacija) i TB, na **I45 instancama** (`dfn-gwin`, `newyork`,
`norway`, `pioro40`, `zib54`, `cost266`), sa semenima 4700–4711. Potvrda važi ako je imenovani krak značajno bolji od A0
na ≥ 4/6 (Holm preko 6).

## 7. Budžet i arhiviranje
Glavni deo: 6 × 12 × 8 = 576 pokretanja (≈ 35–45 min). Potvrda: ≈ 216 pokretanja na većim instancama (≈ 40 min).
Lokalno, bez CI-a. Izlazi: `research/results/iteration46/ablation.json`, eventualno `.../confirmation.json`, i
`ITERATION46_REPORT_SR.md`, i negativni.
