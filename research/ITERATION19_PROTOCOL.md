# Iteracija 19 — forenzička dijagnostika uzroka IEEE118 fizičke neizvodljivosti

**Preregistracija: 21.10.2026, pre svih NOVIH IEEE118 AC pokušaja iteracije 19.** Fork `owlCoder/gadapt:main`; ne dirati upstream `bpzoran/gadapt`. Status: **deterministička dijagnostika, ne optimizacija niti nova GAdapt metoda**.

## Tačno deset unapred fiksiranih stvarnih poziva

Koristiti **neizmenjen** `pypower.case118()`, PYPOWER 5.1.19, isti `runpf` Newton–Raphson kao u završenoj iteraciji 18: `PF_ALG=1, PF_DC=0, ENFORCE_Q_LIMS=0, PF_TOL=1e-8, PF_MAX_IT=40, VERBOSE=0, OUT_ALL=0`. Originalni `gencost`, originalni load, PG/Q/V i `RATE_A` ostaju netaknuti. PV-kontrolisan 9D podskup identičan I18: non-slack 0-based gen `[39,36,4,28]` PG i 0-based `[29,39,36,4,28]` VG. Sve ostalo fiksno. Originalni slack BUS69. **Q ne nametati numerički**, već proveriti QMIN/QMAX na svakoj originalnoj aktivnoj jedinici.

Strogo definisan redosled:
1. **Jedan originalni početni izvorni dispečing**: originalni PG/VG za svih 54 generatora.
2. **Tačno devet prethodno stvarno evaluiranih I18 najboljih penalizovanih jedinki**, redom `seed=2026,2027,2028`; za svaki seed `gadapt_legacy,scipy_de,random_search` iz **nepromenjenog i već arhiviranog** `research/results/ieee118_iteration18_real_gadapt_de_random_20261021.json`.

Pre simulatora fail-closed preflight mora potvrditi: izvor I18 ima 9 redova, svaka od 9 kombinacija jednom, sve `real_ac_pf_calls=96`, `feasible_real_ac_candidates=0`, predviđeni budžet 864 i kompletne konačne fizičke vektore dužine 9; proveriti originalna IEEE118 118 BUS / 54 aktivnih GEN / 186 BRANCH i kontrolne ID-je. **Maksimalno i očekivano 10 stvarnih AC NR poziva; nijedan metod se ne restartuje.**

## Metrike i nezavisni status

Za svaki **konvergirani** izvorni AC PF ishod, izračunati:
- puni izvorni IEEE118 `physics_118` fizički kriterijum iz I18, uključujući kompleksni AC nodalni bilans;
- **svih 54** izvornih Pmin/Pmax i Qmin/Qmax, zasebno broj, ukupni i najveći nedostatak/višak, + originalni gen redovi i BUS ID za najviše 12 najgorih **Q offenders**; isto P offenders;
- svih 118 izvornih VMIN/VMAX (broj, ukupni p.u. i top 12 originalnih BUS ID); oba kraja source-rated `RATE_A` MVA (broj, maksimum, total; RATE_A=0 *nije* ocenjeno ograničenje);
- PG/QG originalnog slack BUS69; originalnu ekonomski izračunatu polinomnu cenu samo kao **dijagnostiku konvergiranog ali potencijalno neizvodljivog** kandidata, **nikada** kao ostvareni OPF cilj;
- za devet I18 vektora reproducirati stari penalizovani score iz arhive u toleranciji apsolutno <=0,001; ako ne odgovara, označiti `replay_matches_archived_score=False`, podaci se ne brišu. Nikada ne tvrditi fizičku izvodljivost ako je I18 vec bila neizvodljiva bez obzira na score.
- jasno evidentirati da `requests` nisu solver pozivi, i da originalna AC-OPF ekonomska referenca iz I16 nije dostupna kao besplatna 9D GA tačka.

**Neuspeh solvera**: `converged=False`, fizičke metrike `null`, uz izvornu grešku. Brojati ulaz u **svaki stvarni `runpf`** (čak i Exception). Nijedan `objective` sentinel ne predstavlja AC poziv. Nema selekcije/filtriranja uspešnih kandidata, cherry-pick-a, testiranja nove GA adaptacije, p-vrednosti ili tvrđenja da je puna IEEE118 mreža neizvodljiva: njen puni originalni AC-OPF je već lokalno post-hoc potvrđen u iteraciji 16.

## Šta se smatra rezultatom

Ovo je lokalna **dijagnostika komponenata** na namerno fiksiranih 10 stanja, ne reprezentativna raspodela svih IEEE118 kandidata. Ako Q kršenja dominiraju, to samo motiviše sledeći izričito preregistrovani test **kontrolabilnosti generator VG izvan sadašnjih 5**, ne dokazuje da prilagođavanje GA operatora rešava problem. Ako dominira aktivna snaga slack-a, prioritet je smisleniji izvorni aktivni redispečing. Isto važi za V i termička ograničenja.

CI: Python3.12, pypower==5.1.19, scipy==1.13.1, pandas==2.2.3, pandapower==2.14.11, single-thread BLAS/OMP. Pre proračuna unit testovi za preflight, originalni Q/P/naponski limiter, RATE_A=0, dva kraja grana i 10/10 fizičkih pokušaja. Trajno arhivirati kod, sirovi JSON/CSV, CI i celovit srpski izveštaj na owlCoder/gadapt:main. Ovo su javni IEEE akademski podaci, ne dokazi rada u stvarnoj industrijskoj mreži.
