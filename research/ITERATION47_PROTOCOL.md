# ITERATION47 — invarijantnost GAdapt-a na jedinice i položaj optimuma; ekonomski dispečing u MW (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda eksperimenta i pre pokretanja.** Datum: 2026-10-23.

## 0. Istraživački predlog (format iz `CLAUDE.md`)
- **Pitanje:** da li GAdapt-ova mera kolonske raznovrsnosti, koja se podrazumevano računa na
  `log((v − min) + 1)`, čini pretragu zavisnom od jedinica promenljivih i od položaja optimuma u opsegu? Da li
  opt-in `columnar_diversity_metric="linear"` (`cc2f357`) to uklanja na stvarnom infrastrukturnom problemu?
- **Najbliži prior art:** princip invarijantnosti pretrage, Hansen, Ros, Mauny, Schoenauer, Auger 2011,
  [10.1016/j.asoc.2011.03.001](https://doi.org/10.1016/j.asoc.2011.03.001) (DOI proveren). Varijansa Gaussovih EDA
  vođena disperzijom populacije i njen prerani kolaps: Grahl, Bosman, Rothlauf 2006,
  [10.1145/1143997.1144071](https://doi.org/10.1145/1143997.1144071); Bosman, Grahl, Thierens 2008,
  [10.1007/978-3-540-87700-4_14](https://doi.org/10.1007/978-3-540-87700-4_14) (DOI provereni).
- **Novost: NIJE utvrđena (i ne tvrdi se).** Invarijantnost je poznat princip. Ovo je **praktična ispravka GAdapt-a**
  (drugi cilj korisnika), ne PhD metoda.
- **Pretpostavke:** optimum blizu gornje granice promenljive sa velikim opsegom (npr. jeftin generator na Pmax u MW).
- **Kontrole:** CMA-ES (paket `cma` 4.5.0) i SciPy DE kao reference, isti budžet.
- **Budžet:** samo lokalno, bez CI-a, procena ≈ 1–2 h.
- **GO/NO-GO:** GO samo za ovu inženjersku validaciju.

**Eksplorativna osnova (pre ovog protokola, ne ulazi u zaključke):** skripte `research/iteration47_exploratory_*.py`,
izlazi u `research/results/iteration47_exploratory/`. Na sferi u 5D sa podrazumevanom merom i optimumom na 0,999 opsega,
medijana jaza je 1,9·10⁻⁸ za R = 0,12, a 5,4·10⁻⁵ za R = 1000. Sa linearnom merom, za R = 1000, medijana je 2,1·10⁻⁹.
Zbog toga **deo A ponavlja te uslove sa novim semenima i još jednom funkcijom** i jedini odlučuje o sintetičkoj tvrdnji.

## A. Sintetički deo (potvrda invarijantnosti)
- **Funkcije:** pomerena sfera i elipsoid (`Σ 10^(3(i−1)/(D−1)) z_i²`), gde je `z = (x − c)/R`.
- **Dimenzije i parametri:** D ∈ {5, 20}; opseg [0, R], R ∈ {1, 1000}; položaj optimuma `c = p·R`, p ∈ {0,5; 0,999}
  u svim koordinatama.
- **Budžet i semena:** 3000 evaluacija, 12 semena 4800–4811. Krakovi: GAdapt podrazumevano (`log_relative`) i GAdapt
  `linear`. Ostali parametri su podrazumevani, uz `probe_cost_function=False` i izlaz samo po budžetu.
- **A1 (primarno):** pri p = 0,999 i R = 1000, `linear` < `log_relative` po najboljoj vrednosti. Testira se u 4 ćelije
  (2 funkcije × 2 D), uparen Wilcoxon, Holm preko 4. **Podržano** ako je značajno u ≥ 3/4 ćelije i ni u jednoj suprotno.
- **A2 (invarijantnost, sekundarno):** za svaki krak, isto pri R = 1 i R = 1000 (p = 0,999, 4 ćelije, Holm preko 8).
  Očekuje se razlika za `log_relative`, a nijedna za `linear`.

## B. Infrastrukturni deo: AC ekonomski dispečing (stvarni MATPOWER podaci preko `pypower` 5.1.19)
- **Slučajevi:** `case14`, `case30`, `case39`, `case57`, `case118`. Nijedan nije korišćen za dispečing samo po PG u
  ranijim iteracijama; I17/I18 su koristili PG + VG sa budžetom 96.
- **Promenljive:** PG svih generatora osim slack generatora, u granicama `[PMIN, PMAX]` iz slučaja.
  - Naponi VG ostaju fiksni na vrednostima iz slučaja; opterećenja su originalna.
  - **Jedinice:** krak „MW“ zadaje promenljive u MW. Krak „p.u.“ zadaje iste promenljive podeljene sa `baseMVA`, pa je
    to matematički isti problem.
- **Evaluacija:** `runpf` (NR, `ENFORCE_Q_LIMS=0`, `PF_TOL=1e-8`, `PF_MAX_IT=40`).
  - Trošak: polinomni `gencost` svih generatora, sa slack PG iz rešenja.
  - Kazna: `1e5 · (Σ V prekoračenja [p.u.] + Σ P prekoračenja slack-a [MW]/100 + Σ Q prekoračenja [MVAr]/100 + Σ RATE_A prekoračenja [MVA]/100)`.
  - Nekonvergencija daje score 1e12.
  - Izvodljivo ako su sva prekoračenja ≤ 1e-3 (V ≤ 1e-5 p.u.).
- **Krakovi:** `log-MW` (podrazumevano), `lin-MW`, `log-pu`, `lin-pu`, kao i reference CMA-ES (normalizovane
  koordinate [0, 1], σ0 = 0,3, podrazumevana populacija, granice preko `cma` opcije `bounds`) i SciPy DE
  (`polish=False`, `tol=0`).
- **GAdapt podešavanja:** podrazumevana, uz `probe_cost_function=False`, `exit_check="generations"` i izlaz po budžetu.
- **Budžet i semena:** 3000 stvarnih `runpf` po pokretanju, 12 semena 4900–4911.
- **Ishod:** najbolji penalizovani score (uvek definisan). Sekundarno: najbolji izvodljivi trošak i broj semena sa
  izvodljivim rešenjem.
- **B1 (primarno):** `lin-MW` vs `log-MW`, uparen Wilcoxon po slučaju, Holm preko 5.
  - **PODRŽANO:** `lin-MW` je značajno bolji na ≥ 3/5 i značajno lošiji na 0/5.
  - **OPOVRGNUTO:** značajno bolji na ≤ 1/5.
  - **DELIMIČNO:** sve ostalo.
- **B2 (sekundarno, invarijantnost na stvarnom problemu):** `log-MW` vs `log-pu` i `lin-MW` vs `lin-pu`, Holm preko 10.
- **Opisno:** jaz do najboljeg skora svih metoda; CMA-ES i DE kao reference. Bez tvrdnje o superiornosti nad njima.

## Kontrole pre pokretanja
- **Evaluator:** na originalnim PG slučaja reprodukuje `runpf` slack PG i `gencost` trošak. MW i p.u. evaluator moraju
  dati identičan score za isti fizički vektor.
- **Budžet:** brojanje je tačno (pozivi preko budžeta se ne izvršavaju).
- **Biblioteka:** `git diff gadapt/` je prazan u trenutku pokretanja; biblioteka je na `cc2f357`.

## Arhiviranje
`research/results/iteration47/synthetic.json`, `research/results/iteration47/dispatch.json` i
`ITERATION47_REPORT_SR.md`, i negativni rezultati. Bez ponavljanja do pozitivnog ishoda.
