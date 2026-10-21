# Iteracija 8 — eksploratorna reaktivno-naponska provera RTE1888

**Datum:** 21. oktobar 2026. **Repo:** `owlCoder/gadapt:main` (bez izmena upstream-a).
**Status:** završeni protokol, implementacija, strukturni testovi, 17 stvarnih AC provera;
sirovi CSV i JSON trajno arhivirani. **Nije izvedeno puno AC-OPF rešavanje.**

## 1. Polazište i metod

Protokol: [ITERATION8_PROTOCOL.md](ITERATION8_PROTOCOL.md), sačuvan u
commitu `b2685440d16e40ca62e26673b605dff92202d235` **pre novih AC poziva**.
Nastavljena je odvojena source-rated `RATE_A` formulacija iz iteracije 7:
`RATE_A=0` ne postavlja limit, a pozitivni izvorni `RATE_A` se
meri u MVA na oba kraja grane. Nisu menjani opterećenje, P-dispečing,
šantovi, trafo tapovi, ostali generatorski naponi ni izvorna mrežna
topologija. Jedino se ispituje uticaj pojedinačnih naponskih setpointa.

Deterministički izbor osam dodatnih generatora temelji se na *referentno
izmerenim* naponskim prekoračenjima i broju aktivnih grana do najbližeg
dostupnog generatora. Prvih osam generatora iz iteracije 7 izostavljeno
je iz novog skupa; Qmin/Qmax i lokalni naponski opsezi zahtevani su
kao numerički definisani. Dobijeni ID-jevi dodatnih generatora:
**8, 85, 23, 190, 46, 26, 15, 141**. To je data-dependent
*exploratory screening*, ne nezavisni holdout ili slučajan uzorak.

Svaka od osam kontrola ispitana je sa dve nezavisne perturbacije
`+/-0.02 p.u.`, odsečene na lokalni dozvoljeni interval, dok su
sve druge kontrole vraćene na referencu:
**1 referenca + 16 probnih tačaka = 17 stvarnih AC poziva**.
Koristi se identičan Newton-Raphson `runpp` i `enforce_q_lims=True`
kao u iteraciji 7. Evaluator ostaje
[iteration7_rte_source_physics.py](iteration7_rte_source_physics.py).

## 2. Verifikovani numerički rezultati

[GitHub Actions uspešno izvršavanje #39619997942](https://github.com/owlCoder/gadapt/actions/runs/39619997942):
svi regresioni testovi prošli; svih 17 stvarnih AC poziva konvergiralo.
Izvorni dokumenti čuvaju i svih 16 neuspešno/neutralno korisnih
perturbacija, ne samo najbolji rezultat.

| Pokazatelj | Referenca | Najmanji rezidual među 17 poziva |
|---|---:|---:|
| Ukupni source-rated rezidual | 1,0917864473 | **1,0554562585** |
| Naponski rezidual (p.u. zbir) | 1,0917864473 | **1,0554562585** |
| Rezidual pozitivnih izvornih RATE_A MVA limita | 0 | 0 |
| Potpuno source-rated izvodljiv? | Ne | **Ne** |

Najniži rezidual postignut je pojedinačnim pomeranjem naponskog
setpointa **generatora #26 za +0,02 p.u.** u odnosu na referencu,
uz sve ostale generatore nepromenjene. Apsolutni pad reziduala iznosi
0,0363301888 (oko 3,33% referentne eksperimentalne metrike).
Od 16 perturbacija, sedam je smanjilo rezidual, sedam ga je povećalo,
a dve su imale nulti efektivni pomeraj zbog dozvoljenog opsega.

**Ključno: nula od 17 kandidata je fizički izvodljivo čak i po
ovom ograničenom source-rated kriterijumu.** Gubici od približno
990 MW vidljivi u izlazu nisu validni *izvodljivi optimumi* i
ne smeju se predstavljati kao takvi.

## 3. Reaktivna dijagnostika i granice interpretacije

Svih 271 aktivnih `net.gen` elemenata u konvertovanoj mreži ima
validne numeričke Q granice i očitanu Q snagu. U referentnom
`runpp(enforce_q_lims=True)` stanju:
- **11** generatora je na Q minimumu (tolerancija 0,001 MVAr);
- **14** generatora je na Q maksimumu;
- **0** eksplicitnih prekoračenja konvertovanih generator Q granica.
  Takvih prekoračenja nije bilo ni u ostalih 16 konvergentnih poziva.

Ovo potvrđuje očitanje konvertovanih generator Q ograničenja u izvršenim
proračunima, **ne** punu OPF izvodljivost. Nisu nezavisno provereni
izvorno MATPOWER poreklo svakog generatorskog Q limita, sve
`sgen`/`ext_grid` P/Q obaveze, aktivni slack limit, reaktivna
capability kriva, P-dispečing, N-1 niti električna identičnost
MATPOWER i pandapower modela. Selektovanje pomoću topološkog
BFS odstojanja nije isto što i AC električna osetljivost.

Instaliran je Python 3.12, `pandapower==2.14.11`,
`scipy==1.13.1`, `pandas==2.2.3`; interni
`pandapower.__version__` u JSON iznosi `2.14.10` (isto
je bilo u iteraciji 7), pa oba signala verzije ostaju eksplicitno
zabeležena. BLAS/OMP režim je jednonitni.

## 4. Provera, negativni pokušaj i ponovljivost

Prvi [CI #39619880417](https://github.com/owlCoder/gadapt/actions/runs/39619880417)
zaustavljen je **pre AC poziva** jer je sintetički test očekivao
redosled gotovo jednakih naponskih prekoračenja, a binarno
zaokruživanje dalo suprotan redosled. Test primer je ispravljen
nedvosmisleno različitim povredama; algoritamsko pravilo nije menjano.
Novi [CI #39619997942](https://github.com/owlCoder/gadapt/actions/runs/39619997942)
je uspešan (7 testova, 17 AC poziva, CSV/JSON sačuvani).

Verzionisani dokazi:
- [CSV: svih 17 poziva](results/rte1888_iteration8_reactive_screen_20261021.csv)
- [JSON: pun izbor kontrola, metrike i neuspešni slučajevi](results/rte1888_iteration8_reactive_screen_20261021.json)
- [Kod](iteration8_reactive_screen.py) i [regresioni testovi](test_iteration8_reactive_screen.py)
- [GitHub Actions workflow](../.github/workflows/iteration8-rte-reactive-screen.yml)

Reprodukcija:
```bash
export PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
python -m pip install -e . 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration8_reactive_screen research.test_iteration7_source_physics
python -m research.iteration8_reactive_screen --csv /tmp/i8.csv --json /tmp/i8.json
```

## 5. Sledeći naučno opravdan zadatak

Pre bilo kakvog poređenja GAdapt-a sa optimizacionim solverom potrebno je:
(1) nezavisno proveriti izvorne MATPOWER generator Q/P i `ext_grid` limite
i specifičnosti konverzije, (2) proveriti zašto 75 trafo impedansi pokazuje
ranije uočena odstupanja, (3) definisati punu AC-OPF formulaciju i referentni
domenski solver sa stvarnom proverom svih ograničenja, (4) tek onda
zamrznuti uporedni benchmark sa nezavisnim semenima, sačuvanim
fizičkim pozivima i pravilnom statistikom.

**Naučni zaključak:** otkrivena je merljiva lokalna osetljivost
na dodatne naponske kontrole uz aktivna Q zasićenja, ali nema
izvodljivog rezultata, novog algoritma, dokaza superiornosti niti
industrijske validacije.
