# Iteracija 7 — revizija RTE1888 izvora ograničenja i fizičke izvodljivosti
**Datum:** 21.10.2026. **Rep:** `owlCoder/gadapt:main`. Bez izmena u upstream `bpzoran/gadapt`.
**Status:** kompletna dijagnostika i petometodni stvarni AC pilot izvršeni; statistika nezavisno proverena i arhivirana.
**Nema originalnog niti statistički superiornog doktorskog algoritma.**

## 1. Ključno novo otkriće: problem je delom posledica naše formulacije

U iteraciji 6 optimizovan je model sa osam generatorskih naponskih
setpointa i blanket `loading_percent <= 100` za svaki pandapower
vod i transformator. Sa 12 optimizacionih pokretanja nijedan
fizički izvodljiv vektor u toj **istorijskoj eksperimentalnoj**
formulaciji nije pronađen. Taj empirijski nalaz ostaje validan
i podaci se **ne prepravljaju**. Ali raniji opis da su to
nesavladiva originalna RTE mrežna termička ograničenja bio bi
neutemeljen.

Nezavisno je pregledan javni originalni
[MATPOWER case1888rte.m](https://github.com/MATPOWER/matpower/blob/80b6e16f760f58721ad31221c7287c28259cd4ad/data/case1888rte.m),
blob `820bd317167381baf819d67eab7d886013e8b05a`,
objavljena referentna datoteka ažurirana 5.6.2019.
MATPOWER `mpc.branch(:,RATE_A)` je MVA termički limit;
**`RATE_A=0` znači da grana NEMA zadanog MVA limita**.
Izvor:
[MATPOWER Data File Format, tabela B-3](https://matpower.app/manual/matpower/DataFileFormat.html)
i izvorni kod `lib/caseformat.m`.
Istraživački case služi testiranju matematičkih metoda,
**ne operativnom planiranju stvarne francuske mreže**.

Originalni model sadrži 2.531 granu:
**455 bez termičkog ograničenja (`RATE_A=0`)** i
2.076 sa pozitivnim izvornim MVA rating-om.
Unutar pandapower 2.14.11 to odgovara
**233 transformatora + 222 vodova sa `RATE_A=0`**.
Primer transformatora `net.trafo[404]`:
- konverzija: `sn_mva=99.999`, `max_loading_percent=100`,
  početno opterećenje približno 209,10%;
- izvor MATPOWER branch, 453→1699: `RATE_A=RATE_B=RATE_C=0`
  i tap 1.092105;
- krajnja sabirnica `net.bus[1705].name=1698`,
  originalna jedinicom bazirana MATPOWER oznaka 1699;
- generator `net.gen[122]` na terminalu: 236,69 MW
  proizvodnje (takođe Pmin), lokalna potrošnja 40 MW.
**Nameplate `sn_mva=99.999` koji je dodeljen pri konverziji
nije validiran operativni MVA limit tog elementa.**

## 2. Ponovljivi dokaz porekla termičkih ograničenja

Implementirani su:
- `research/iteration7_conversion_probe.py`: izvorno mapiranje
  `net.bus.name`, impedanse, nameplate parametri;
- `research/iteration7_source_rating_map.py`: kompletno
  povezivanje svih 2.531 originalnih grana sa
  1.976 vodova i 555 transformatora u konvertovanom modelu;
  mapiranje proverava oba terminala, izvornu bus oznaku,
  relativni redosled, a paralelne grane sa razlikama
  u MVA limitima poredi i preko impedansi;
- `research/test_iteration7_rate_source.py` i
  `research/test_iteration7_source_physics.py`: strukturni
  i analitički regresioni testovi.

[Nezavisni uspešni CI preslikavanja #39607656391](https://github.com/owlCoder/gadapt/actions/runs/39607656391):
2.531/2.531 preslikanih elemenata,
**nula nepodudarnih parova i nula neslaganja
redosleda naspram nezavisnog impedansnog uparivanja**.
Zabeleženo je 69 paralelnih grupa sa različitim rating-om;
preslikavanje nije izvedeno samo prema krajnjim čvorovima.
Nije dokazano bitovsko poklapanje pandapower i originalnog
MATPOWER rešenja: 75 transformatora imaju značajno
odstupanje u metrikama ekvivalentne impedanse; izvori
i numerička značenja moraju biti predmet daljeg audita.

Izvorni podaci i trajni artefakti:
- `results/rte1888_matpower_original_branch_ratings_2019.csv`
  (svih 2.531 izvornih redova, originalni P/Q thermal RATE i impedanse);
- `results/rte1888_iteration7_matpower_to_pandapower_thermal_map_20261021.csv`
  (mapiranje svih 2.531 na konkretne elemente);
- `results/rte1888_iteration7_matpower_provenance_20261021.json`;
- `results/rte1888_iteration7_conversion_probe_20261021.json`.

## 3. Originalna formulacija: prva fizička dijagnostika

Protokol pre proračuna:
`research/ITERATION7_PROTOCOL.md`.
Ista 8V prethodna formulacija, nominalno i 110% opterećenje,
17 AC poziva po faktoru (referenca + 16 promene +/-0.02).
Koristi STVARNI `pandapower.runpp` sa istim podešavanjima
kao prethodna iteracija.

[Uspešan CI #39602815796](https://github.com/owlCoder/gadapt/actions/runs/39602815796):
| Izvorno u našem starom evaluatoru | 100% početno | 110% |
|---|---:|---:|
| Konvergentni PF pozivi / 17 | 17 | 0 |
| Transformatori iznad nametnutih 100% | 29 | Nije izračunljivo |
| Vodovi iznad nametnutih 100% | 0 | Nije izračunljivo |
| Početni zbir termičkih prekoračenja | 15,177411 | Nije izračunljivo |
| Početni zbir naponskih prekoračenja | 1,091786 | Nije izračunljivo |
| Ukupni početni penalizovani fizički rezidual | 16,269198 | Nije izračunljivo |
| Najmanji od 17 reziduala | 16,249574 | Nije izračunljivo |

Na 100% opterećenju početno stanje prema implementiranim
bus limitima narušava napon na 120 sabirnica.
Neke od 29 termičkih prijava potiču od nepostojećih originalnih
RATE_A limita; nisu dokaz industrijskog preopterećenja.
110% nije 'matematički neizvodljivo', nego NR solver nije
konvergirao u 17/17 fiksno propisanih poziva.

## 4. Uslovni analitički dokazi — obavezno ograničenje primene

`research/iteration7_leaf_certificate.py` uz sintetičke
regresione testove identifikovao je 14 **uslovnih**
radijalnih terminalsko-aktivnih nejednakosti.
Na primer, pretpostavimo li da je trafo404 stvarno ograničen
na 100 MVA i da je terminalni Vmax 1.05 p.u.,
minimalni izvoz iz krajnje sabirnice bio bi
236,69−40 = 196,69 MW,
dok je napon ograničio približnu maksimalnu aktivnu
isporuku po nazivnoj struji na 104,99895 MW.
Ta matematička protivrečnost dokazuje neuskladivost
**samo** kada je termički limit 100 MVA zaista ograničenje.

Originalni MATPOWER `RATE_A=0` upravo ruši ovu
ključnu pretpostavku. Zato 14 uslovnih dokaza **ne mogu**
sertifikovati neizvodljivost originalnog RTE zadatka.
Sačuvani su kao primer naučne važnosti auditovanja
fizičkih pretpostavki, uz eksplicitno navedenu
neprimenljivost na izvorne neograničene grane.
[Prvobitni CI](https://github.com/owlCoder/gadapt/actions/runs/39604450906);
[regresioni CI sa dodatnom proverom skaliranja](https://github.com/owlCoder/gadapt/actions/runs/39604965948).

## 5. Nova izvorno validirana MVA formulacija — zaseban eksperiment

`research/iteration7_rte_source_physics.py` koristi
`SourceRatedRTEGrid` izveden iz prethodnog evaluatora:
- realan `runpp` sa numerički pinovanim okruženjem;
- ako je izvorni `RATE_A>0`: zahteva
  `max(|S_from|,|S_to|) <= RATE_A`, pri čemu
  `|S|=sqrt(P²+Q²)` uključuje reaktivni tok;
- za `RATE_A=0` ne izmišlja termičku granicu;
- i dalje zasebno proverava objavljene naponske granice,
  sve nekonvergencije i stvarni broj AC poziva;
- optimizuje samo osam napona, nije puni OPF.

[Uspešan CI sa 34 NOVA stvarna AC poziva #39608593545](https://github.com/owlCoder/gadapt/actions/runs/39608593545):
| Nova source-rated provera | 100%, početno | 110%, početno |
|---|---:|---:|
| Konvergentnih od 17 | 17 | 0 |
| Stvarnih source RATE_A prekoračenja | **0 vodova, 0 transformatora** | Nije izračunljivo |
| Maksimalni odnos toka/pozitivni RATE_A, vodovi | 83,29% | Nije izračunljivo |
| Maksimalni odnos toka/pozitivni RATE_A, transformatori | 85,93% | Nije izračunljivo |
| Početni naponski rezidual | **1,091786** | Nije izračunljivo |
| Najmanji rezidual među 17 | **1,079486** | Nije izračunljivo |

Dakle, u referentnom stanju za 100% **termika ne dominira**
kada se koristi izvorni RATE_A; dominantan problem je
naponska izvodljivost uz postojeća generator Q ograničenja,
a tek onda preciznost cilja u MW. Ni ovim nije dokazana
izvodljivost ili neizvodljivost izvorne pune AC-OPF mreže.
Sirovi CSV:
`research/results/rte1888_iteration7_source_rated_ac_probe_20261021.csv`.

## 6. Mehanistički pilot algoritama i evaluacionog budžeta

Unapred fiksiran dodatak C protokola pre proračuna:
5 metoda × 3 nova uparena semena 350–352 × 72 stvarna AC
evaluaciona poziva = **1.080 fizičkih simulacija**, population12,
samo 100% opterećenje, identična ispravljenа formulacija
za sve metode. Metode:
`gadapt_penalty`, `gadapt_feasibility_first`,
`slsqp_penalty`, `hybrid_fixed`, `scipy_de`.
Feasibility-first leksikografsko rangiranje je već poznata
tehnika, ne predlog novog doktorског mehanizma.
Stvarni GAdapt `GA.execute()` se poziva kroz
`research.ieee118_allocation.ga_stage`, koji broji svaku
AC simulaciju, čak i kada krajnji optimizator ne konvergira.

Podaci će biti razdvojeni od obe ranije formulacije.
Čak i ako se metod pokaže uspešnijim, **n=3**
predstavlja samo mehanističku probu, ne dokaz
statističke ili međudomenske superiornosti.

## 7. Naučni status i ograničenja

Ova iteracija pruža **materijalnu reproduktivnu korekciju
postavke eksperimenta**, ne novi superioran optimizacioni
algoritam. Bez identifikovanja izvornog RATE_A bilo kakva
feasibility-restoration heuristika bi ciljala lažna ograničenja.
Nakon korekcije, preostaje osam napona naspram 120
početnih bus naponskih povreda i 271 raspoloživih
generatorskih naponskih setpointa.
Potrebno je posebno predefinisati smislen
reaktivni/naponski OPF kontrolni prostor
sa stvarnim fizičkim uslovima i odgovarajućim solverskim
referencama, PRE eventualne potvrde novog algoritma.

Nema tvrdnji o globalnom optimumu, N-1 sigurnosti,
industrijskoj primenljivosti, novosti poznatih constraint
handling metoda, pouzdanosti malog uzorka, ili
ekvivalenciji između stare i nove formulacije.
Precizne numeričke vrednosti iz iteracije 6 ostaju
neizmenjene i dostupne kao istorijska evidencija.

## 8. Reprodukcija i provera

```bash
export PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
python -m pip install -e . 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration7_audit research.test_iteration7_leaf_certificate research.test_iteration7_rate_source research.test_iteration7_source_physics research.test_iteration7_source_pilot
python -m research.iteration7_rte_audit --loads 1.0 1.1 --csv /tmp/rte_old.csv --json /tmp/rte_old.json
python -m research.iteration7_rte_topology --output /tmp/rte_topology.json
python -m research.iteration7_leaf_certificate --output /tmp/rte_cert.json
python -m research.iteration7_source_rating_map --compact /tmp/rte_source_rating_map.csv --output /tmp/rte_source_rating_map.json
python -m research.iteration7_rte_source_physics --loads 1.0 1.1 --output /tmp/rte_source_probes.csv
python -m research.iteration7_source_rated_pilot --seed-start 350 --seeds 3 --budget 72 --population 12 --output /tmp/rte_source_pilot.csv
```

Godina izvornih podataka i reference:
Josz, Fliscounakis, Maeght i Panciatici,
*AC Power Flow Data in MATPOWER and QCQP Format:
iTesla, RTE Snapshots, and PEGASE*, arXiv:1603.01533.
MATPOWER user manual, definicija nultog RATE_A.
Za feasibility-first princip videti:
Deb (2000), *An efficient constraint handling method
for genetic algorithms*, Comput. Methods Appl. Mech. Engrg.


## 9. Završni ishodi uporednog algoritamskog pilota

[Uspešan CI eksperiment #39608967519](https://github.com/owlCoder/gadapt/actions/runs/39608967519)
izvršio je **svih 15 zamrznutih metod–seme pokretanja**:
5 metoda × semena 350, 351, 352 × 72 prave fizičke NR
evaluacije = **1.080 stvarnih AC poziva**. U svakoj metodi
izvršen je isti `SourceRatedRTEGrid` sa izvornim MVA
ograničenjima. Stvarna implementacija GAdapt-a pozvana je
kroz postojeći `ga_stage`, ne putem alternativne simulacije GA.

Sirovi podaci, uključujući stvarne fizičke pozive,
broj nekonvergentnih poziva, vreme, najbolje izvodljive
i najbolja fizička neizvodljiva rešenja, arhivirani su u
`research/results/rte1888_iteration7_source_rated_pilot_20261021.csv`.

| Metod | Izvodljivi runovi /3 | Medijana najmanjeg kršenja | Najgore najmanje kršenje | Nekonvergentni PF /216 |
|---|---:|---:|---:|---:|
| GAdapt (penalitet) | 0/3 | 1,073343 | 1,081066 | 7 |
| GAdapt (feasibility-first) | 0/3 | 1,073343 | 1,076937 | 7 |
| Samostalni SLSQP | 0/3 | 1,078234 | 1,078234 | 15 |
| Fiksni GAdapt→SLSQP | 0/3 | 1,078234 | 1,081066 | 11 |
| SciPy DE | 0/3 | 1,073555 | 1,074570 | 3 |

**Nijedna metoda nije ostvarila stvarno izvodljiv rezultat.
Gubici u MW se zato ne porede kao izvodljivi optimumi.**
Leksičko rangiranje feasibility-first nije potvrdilo
superiornost nad originalnim GAdapt-om;
uparenim odnosom uz prag `1e-9` postignuto je
1 pobeda, 0 poraza i 2 praktične nerešene replikacije.
Mogućnost različitog najgoreg ishoda na samo 3 semena
nije robustan zaključak.

### Nezavisna statistička kontrola

[GitHub Actions #39610466327](https://github.com/owlCoder/gadapt/actions/runs/39610466327)
uspešno je ponovo pročitao već sačuvani sirovi CSV
bez novih PF simulacija; proverio je izvornu formulaciju,
3 tačno planirana semena po metodi, svih 72 fizička poziva
po runu, i odbacio implicitne gubitke u MW kod
neizvodljivih kandidata. Svaki izvodljivosti negativan
uzorak 0/3 daje Wilson 95% opseg stope uspeha
približno **[0, 0,5615]**, veoma širok.
Četiri uparena poređenja po minimumu fizičkog kršenja
prema GAdapt-penalitet baseline daju, uz definisanu
porodicu Holm korigovanih dvosmernih egzaktnоg sign testa,
**p=1,0 za svako poređenje**. Sa n=3 to nije dokaz jednakosti
metoda niti superiornosti bilo kog pristupa.

Ponovna analiza ne generiše novi statistički uzorak:
upotrebljava ISTE rezultate i ISTA tri semena.
Dodatni proverljivi fajlovi:
- `research/results/rte1888_iteration7_source_rated_stats_20261021.json`;
- `research/figures/rte1888_iteration7_source_rated_violation.svg`;
- PNG i SVG u istom GitHub Actions artefaktu
  `iteration7-rte-source-rated-verified-statistics`.

U ograničenju od osam napona fizika je i dalje teško
izvodljiva u testiranom malom budžetu, ali sada znamo
da je dominantno ostalo **naponsko**, ne lažno
nametnuto **termičko** kršenje. Ne zaključujemo da
puni izvorni AC-OPF nema rešenje niti da je
treba nekritički menjati sve generatore.
Sledeći naučni korak je posebno modelovan
reaktivni/naponski feasibility-restoration benchmark
sa raspoloživim kontrolama, izvorno definisanim Q
granicama i domenskim referentnim solverom.

### Naučna interpretacija

**Dokazani rezultat iteracije 7:** otkrivanje,
reprodukcija i ispravka pogrešnog tumačenja RATE_A=0,
potkrepljena celovitim mapiranjem 2.531 grane,
pravim AC simulacijama i analitičkom revizijom 14
uslovnih neizvodljivosti.
**Negativan algoritamski rezultat:** feasibility-first
GAdapt nije pokazao potvrđenu prednost; n=3 nije
potvrdni eksperiment.
**Nerešeno:** originalan doktorски doprinos, puna
AC OPF izvodljivost, brojne nezavisne mreže, N-1
i industrijski relevantni operativni rizici.
Predhodni pozitivan rezultat ne sme biti
rekonstruisan post hoc iz ovih 15 pokretanja.

Dodatni bibliografski pregled:
`research/ITERATION7_LITERATURE.md` (Deb, Runarsson/Yao,
Coello Coello, pregled memetike, AC-OPF, skupe simulacije
i multiverodostojna optimizacija).


## 10. Konačna arhiva podataka i kontrolni trag

Trajni repozitorijumski artefakti glavnog poređenja:
- [Sirovi CSV — 15 pokretanja × 72 stvarna AC poziva](results/rte1888_iteration7_source_rated_pilot_20261021.csv)
- [Vremenski označeni zapisi svih 15 pokretanja](results/rte1888_iteration7_source_rated_pilot_20261021.log)
- [Nezavisno ponovo izračunati Holm, Wilson, medijane, Q90, najgori slučajevi](results/rte1888_iteration7_source_rated_stats_20261021.json)
- [SVG grafikon](figures/rte1888_iteration7_source_rated_violation.svg)
  i [PNG grafikon](figures/rte1888_iteration7_source_rated_violation.png)
- [Sirovi izvorno MVA ocenjeni PF dijagnostički podaci](results/rte1888_iteration7_source_rated_ac_probe_20261021.csv)
  i [vremenski označeni dijagnostički log](results/rte1888_iteration7_source_rated_ac_probe_20261021.log)
- [Kompletno izvorno MVA ograničenje po granama](results/rte1888_matpower_original_branch_ratings_2019.csv),
  [mapiranje na pandapower elemente](results/rte1888_iteration7_matpower_to_pandapower_thermal_map_20261021.csv)
  i [podaci o poreklu](results/rte1888_iteration7_matpower_provenance_20261021.json).

Sve slike potiču samo od arhiviranog CSV, ne od
novih semena ili nezavisne validacije. Uzorak ostaje
**n=3**, a ne n=6 nakon dva statistička čitanja.
Kompletni GitHub Actions logovi su:
[mapiranje 2531 grane](https://github.com/owlCoder/gadapt/actions/runs/39607656391),
[novi fizički evaluator](https://github.com/owlCoder/gadapt/actions/runs/39608593545),
[algoritamski pilot](https://github.com/owlCoder/gadapt/actions/runs/39608967519),
[nezavisna statistika i SVG/PNG](https://github.com/owlCoder/gadapt/actions/runs/39611147372).
