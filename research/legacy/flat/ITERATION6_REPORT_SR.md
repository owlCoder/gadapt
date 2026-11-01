# Iteracija 6 — adaptivna raspodela budžeta, IEEE118 i RTE1888 (2026-10-21)

**Odluka: negativan/mješovit naučni rezultat; novi heuristički kontroler ostaje
isključivo istraživački, nije uključen u podrazumevani GAdapt.**
Sav kod i brojčani podaci su direktno na `owlCoder/gadapt:main`,
uz eksplicitno ovlašćenje vlasnika. Nema promena u `bpzoran/gadapt`.

## Polazna hipoteza, literatura i unapred definisani protokol

Prethodna iteracija: klasični multistart SLSQP (bez GAdapt-a) nadmašio je
GAdapt na petodimenzionalnoj IEEE14 optimizaciji. Zbog toga smo, PRE
izvođenja, fiksirali hipotezu da odluka zavisna od fizičke izvodljivosti
i ranog napretka može pametnije raspodeliti budžet između GA istraživanja
i poznate SLSQP lokalne pretrage. Potpuna specifikacija, semena i
testna procedura: `research/ITERATION6_PROTOCOL.md`.

Adaptivni memetički algoritmi i učenje intenziteta lokalne pretrage već su
poznati u literaturi, npr. Cheng i saradnici 2024, DOI
10.23919/CSMS.2024.0006, i *learning-based memetic algorithm* 2024, DOI
10.1016/j.swevo.2024.101694. **Zato se trenutni kontroler ne predstavlja
kao teorijski ili originalan algoritam za doktorat.**

### Implementirani kontroler

`research/ieee118_allocation.py` koristi STVARNI `GA(...).execute()`
iz instaliranog GAdapt-a, a ne posebno imitiran algoritam.
`AllocationSwitch` proverava napredak na kraju generacija nakon
25% raspoloživih fizičkih poziva:
- još nema nezavisno potvrđene izvodljivosti: 75% ukupnog budžeta GA;
- izvodljivost ostvarena i poboljšanje od kontrolne tačke 12,5% >= 0,002:
  55% GA;
- izvodljivost ostvarena, ali napredak ispod 0,002: 30% GA.
Ostatak ukupnog budžeta dobija multistart SciPy SLSQP. Odluka koristi samo
do tada već izvršene stvarne AC proračune, nikada nedostupni kasniji rezultat.
Kada GA generacija preseče ciljni budžet, objektiv vraća eksplicitno
evidentiranu sentinel vrednost BEZ fizičkog proračuna, a lokalnoj pretrazi
ostaje tačno stvarno preostali broj PF evaluacija. Procentualni budžet
računa se CELIM brojevima, nakon što je prvi regression test otkrio
grešku `ceil(0.55*180)` (u float aritmetici ponekad 100 umesto 99).
Ta greška je ispravljena i pet kontrolnih testova je prošlo.

### Metodološka ograničenja
IEEE118: javni `pandapower.networks.case118`, osam naponskih kontrola
prvih osam generatora; opseg 0,95–1,08 p.u., izvornom
`GridProblem` proverene naponske i termičke granice,
`enforce_q_lims=True`. Nije puni AC-OPF, ne optimizuje sve upravljačke
promenljive, N-1 sigurnost niti dodatni tržišni/tehnički trošak.
Prethodni pouzdani fizički dijagnostički CI:
https://github.com/owlCoder/gadapt/actions/runs/39580915103
potvrdio je izvodljive referentne napone za IEEE118 100% i 110%.
RTE1888 referenca je već nominalno neizvodljiva u istom ograničenom
modelu, maksimalna opterećenost jedne grane bila je oko 209%.
Upotreba različitih dimenzija, kvaliteta podataka ili mrežnih ograničenja
ne dopušta direktno poređenje sa literaturnim globalnim AC-OPF ciljevima.

## IEEE118: potpuno izvršeno i stvarno budžetirano

Originalno izvođenje (kompletne linije RUN, CSV i statistika):
https://github.com/owlCoder/gadapt/actions/runs/39582074680
Actions artefakt:
https://github.com/owlCoder/gadapt/actions/runs/39582074680/artifacts/12337137647

72 metod–seme–faktor pokretanja,
6 novih uparenih semena (200–205), faktori opterećenja 1.0 i 1.1,
**180 stvarnih poziva pandapower NR solvera PO POKRETANJU** (12.960 ukupno).
Svi su sprovedeni sa jednakim resursnim budžetom i svih 72/72 pokretanja
imalo je izvodljivo rešenje, uz registrovane individualne AC
nekonvergencije, koje se NE nazivaju izvodljivim.
Sirovi podaci: `research/results/ieee118_allocation_20261021.csv`.
Grafici se generišu iz tog CSV kroz `research/plot_iteration6_ieee118.py`.

| Metod | 100% medijana izvodljivih gubitaka MW | 110% medijana MW |
|---|---:|---:|
| GAdapt original | 131.841563 | 172.760037 |
| Samostalni multistart SLSQP | **131.553953** | **172.554719** |
| Fiksni hibrid (90 GA + 90 SLSQP) | 131.720128 | 172.675001 |
| Adaptivni GA + SLSQP | 131.677102 | 172.695446 |
| SciPy DE | 131.834761 | 172.812701 |
| CMA-ES | 131.960103 | 172.949908 |

U 6/6 pokretanja samostalni SLSQP je nadmašio GAdapt pri oba faktora.
Ali egzaktno dvosmerno sign p=0,03125, a Holm-korigovano za 5
unapred definisanih poređenja `p=0,15625` na svakom faktoru.
Nema potvrđene familijarne značajnosti.
Medijalna uparena razlika SLSQP − GAdapt je −0,287610 MW na 100%
(bootstrap 95% [−0,368014, −0,105721]) i −0,205318 MW na 110%
([−0,253835, −0,105945]); intervali su deskriptivni zbog
malog i ponavljano istraživanog javnog benchmarka.

Adaptivni hibrid naspram ORIGINALNOG GAdapt-a: 4/6 pobeda pri 100%
(sign p=0,6875; Holm p=1.0) i 6/6 pri 110%
(sign p=0,03125; Holm p=0,15625). NEMA statistički dokazane prednosti.
Adaptivni hibrid naspram FIKSNOG hibrida:
1/6 pobeda pri 100% i 2/6 pri 110%,
bez pouzdane prednosti (sign p=0,21875, odnosno 0,6875).
Adaptivni naspram SAMOSTALNOG SLSQP-a: 1/6 pobeda pri oba faktora.
U svim opterećenjima, stvarne unapred fiksirane odluke
kontrolera su: 4 slučaja `feasible_stalled`,
2 `feasible_improving`, 0 `infeasible_explore`.
Dakle logika se zaista izvršavala, ali nije pokazala razumnu
prednost nad jednostavnim fiksnim ili lokalnim metodima.
Nema opravdanja za promenu podrazumevanog GAdapt-a.

Ključno: 6/6 fizički izvodljivih pokretanja po metodi i opterećenju
daje Wilson 95% interval [0.6097, 1.0] za nepoznatu pouzdanost,
što je isuviše široko za industrijsku tvrdnju ili repne rizike.
Sa samo n=6, čak potpuna dominacija 6/6 daje posle Holm korekcije
p≥0,15625 ako svi pet primarnih poređenja imaju iste minimalne p-vrednosti.
Zbog toga je ovaj eksperiment isključivo MEHANISTIČKA pilot provera
generalizacije, kao što je unapred zapisano.

## RTE1888: odvojena kontrola fizičke izvodljivosti

Izvođenje:
https://github.com/owlCoder/gadapt/actions/runs/39582153291
Actions artefakt:
https://github.com/owlCoder/gadapt/actions/runs/39582153291/artifacts/12338810253
Sirovi podaci:
`research/results/rte1888_stress_20261021.csv` (12 redova).
Metode: originalni GAdapt, SLSQP, adaptivni hibrid, SciPy DE,
3 semena (300–302), tačno 72 stvarna AC NR proračuna po
pokretanju (864 ukupno). **Nijedna metoda nije našla nezavisno
fizički izvodljivo rešenje** sa samo osam generatorskih napona.

Najmanje postignuto ukupno fizičko kršenje, medijana od 3 pokretanja:

| Metod | Medijana minimalnog kršenja | Izvodljivo |
|---|---:|---:|
| GAdapt | 16.235587 | 0/3 |
| SLSQP | 16.266642 | 0/3 |
| Adaptivni hibrid | 16.235587 | 0/3 |
| SciPy DE | 16.235587 | 0/3 |

Ovo je snažna NEGATIVNA fizička provera konkretne formulacije:
smanjen penal nije isto što i zadovoljena mrežna ograničenja.
Osam kontrolnih napona ne ispravljaju strukturna prekoračenja
termičkih kapaciteta u ovom ograničenom modelu; ne tvrditi da je
matematički dokazano da NIJEDNO rešenje ne postoji, već samo
da testirana pretraga nijedno nije našla.
Takvi kandidati nemaju legitimno `best feasible loss MW`
i nisu predstavljeni kao optimum.

## Reprodukcija bez skrivene fizičke evaluacije

```bash
python -m pip install -e . 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3' 'cma>=4,<5'
python -m unittest -v research.test_iteration6_policy
python -m research.iteration6_grid_probe --rte
python -m research.ieee118_allocation --seeds 6 --seed-start 200 --budget 180 --output ieee118.csv
python -m research.analyze_ieee118_allocation ieee118.csv --budget 180
python -m research.iteration6_rte_stress --output rte1888.csv
python -m research.analyze_iteration6_rte rte1888.csv
```

Vrednosti iz sirovih CSV trajno arhivirane u git repozitorijumu koriste
Python `True`/`False`, pa reproduktivna analiza odbija nepotpune redove,
duplirane (seme,metod,faktor) kombinacije i nejednake stvarne solver budžete.
Sve statistike su izračunate samo iz stvarno izmerenih podataka.
Zaseban CI `.github/workflows/iteration6-independent-audit.yml`
ponavlja statistiku i generiše SVG/PNG iz GitHub CSV zapisa.

## Značaj za buduću disertaciju

**Nije potvrđena originalna superiorna GA tehnika u iteraciji 6.**
Na IEEE118 postojeći lokalni SLSQP i dalje ima najniži medijalni gubitak;
adaptivna raspodela ima samo negativan/mešovit signal i nije pouzdanija
od jednostavnog fiksnog hibrida.
RTE1888 naglašava važnije pitanje: *feasibility restoration* mora biti
odvojena od smanjivanja penalizovanog cilja i ne može se rešavati samo
odabirom operatora sa osam naponskih promenljivih.

**Preporučeni sledeći NAUČNI korak:** prvo eksplicitno razviti
fizičku komponentu ograničenja i operator projekcije/popravke sa stvarno
odabranim aktivnim generatorima, transformatorima i reaktivnim resursima,
uporediv s OPF pristupom; zatim testirati da li
constraint-/cost-aware upravljač resursima pretrage donosi prednost preko
jakih lokalnih algoritama bez prepravljanja praga nakon posmatranih
rezultata. Potrebni su nezavisni i veći uzorci, više fizičkih domena,
realni sigurnosni/operativni limiti i eksperimenti sa repnim rizikom.


## Dodatak: stvarna međupokretačka ponovljivost, bez povećavanja uzorka

**Otkrivena greška u pretpostavci:** dva uspešna prvobitna,
nekontrolisana IEEE118 workflow-a
[39582000049](https://github.com/owlCoder/gadapt/actions/runs/39582000049)
i [39582074680](https://github.com/owlCoder/gadapt/actions/runs/39582074680)
koristila su isto stablo koda (između njih je bila samo izmena protokola),
ista semena, iste budžete i iste adaptivne odluke, ali su izgubila
BITOVSKU ponovljivost rezultata. U 12/12 uparenih pokretanja svakog
metoda završna vrednost se donekle promenila; kod CMA-ES skoro nula
(~10^(-12) MW), kod SLSQP do oko 0,000296 MW, kod GA/DE/hibrida
sve do ~0,25 MW. Zato originalne izlaze NE predstavljamo kao
bitovski deterministične i ne prepisujemo izvorni CSV.

**Kontrolisani uslovi:** postavljen je
`PYTHONHASHSEED=0`, `OPENBLAS_NUM_THREADS=1`,
`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1` i
`NUMEXPR_NUM_THREADS=1`, uz pinovane Python/pandapower/SciPy verzije.
Ovo je naknadna ISPRAVKA NUMERIČKOG OKRUŽENJA, ne promena
metoda, objektiva, semena, statistike, algoritamskih pragova ili
stvarnog broja evaluacija.
Koje je pojedinačno podešavanje izazvalo prethodne varijacije
NIJE izolovano i zato mu se ne pripisuje uzročna tvrdnja.

- [Dva računara: hash-probe od 16 identičnih AC i 48 stvarnih GA AC
  evaluacija](https://github.com/owlCoder/gadapt/actions/runs/39584533666)
  — oba procesna ponavljanja i oba nezavisna runner-a dala su identične
  SHA256 hash-vrednosti ulaza i fizičkog izlaza.
- [Kompletno kontrolisano IEEE118 izvođenje A
  (72 pokretanja)](https://github.com/owlCoder/gadapt/actions/runs/39584783286)
  i [B (ponovljenih istih 72 pokretanja)]
  (https://github.com/owlCoder/gadapt/actions/runs/39584858314):
  **GAdapt, SLSQP, fiksni hibrid, adaptivni hibrid i DE imaju
  bitovski identične ostvarene MW vrednosti u 60/60 odgovarajućih
  slučajeva**; CMA-ES ima maksimalno samo
  `1.0317080523236655e-11` MW apsolutne razlike u 12/12 slučajeva.
  Ostala detaljna očitavanja algoritamskih odluka i pravih PF budžeta
  su podudarna. To pokazuje visoku reproduktivnost NA OVOM
  PINOVANOM SISTEMU, ali ne univerzalnu determinističnost.
- Ponavljeni francuski
  [RTE1888 stres-test](https://github.com/owlCoder/gadapt/actions/runs/39584806628)
  opet je imao **0/12 fizički izvodljivih kandidata**, uz isti
  raspon minimalnih kršenja ograničenja.
- Zaseban [CI koji ponovo čita CSV, analizira poređenja i
  generiše SVG/PNG iz fizičkih podataka]
  (https://github.com/owlCoder/gadapt/actions/runs/39586016114)
  uspešno je nezavisno ponovio statistiku. Za svih 72 originalnih
  redova naspram prve kontrolisane replike: `same_incumbent_vector=12`,
  `exact_same_feasible_loss=12` za SVAKI od šest metoda na 12
  kombinacija semenâ i opterećenjâ; znači i originalno korišćeno
  izvođenje 39582074680 slučajno se već poklapalo bitovski sa
  kontrolisanim rezultatima, ali drugo nekontrolisano nije.

**Izvori nisu pseudoreplikovani.** Replikacije imaju ISTE semena
200–205, iste javne fizičke slučajeve i iste metode, te statistički
broj nezavisnih semenâ ostaje n=6, a ne n=12 ili n=18.
Nisu ponovo računati povoljniji p-testovi iz tri kopije.
Ponavljanje dokazuje preciznost procedure pod kontrolisanim
okruženjem, ali ne validaciju na novoj infrastrukturi.

Verzionisane originalne i dodatne datoteke (sve `main`):
`research/results/ieee118_allocation_20261021.csv`,
`research/results/ieee118_allocation_pinned_20261021.csv`,
`research/results/rte1888_stress_20261021.csv`,
`research/results/rte1888_stress_pinned_20261021.csv`.
Alat za proveru stabilnosti:
`research/compare_iteration6_replications.py`.
Izvorni ZIP artefakti svakog workflow-a ostaju kanonski zapis.

**I nakon stabilizovanja numerike glavni zaključak ostaje NEGATIVAN:**
adaptivna raspodela ne nadmašuje jednostavne postojeće optimizatore.
Metodološka pouzdanost eksperimenta se povećala; originalna doktorska
superiorna optimizaciona metoda nije potvrđena.
