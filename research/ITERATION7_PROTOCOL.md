# Iteracija 7 — pre-registracija strukturne dijagnostike RTE1888
**Registrovano 2026-10-21, pre novih RTE1888 dijagnostičkih AC izvršavanja.**
Repo: `owlCoder/gadapt:main`. Zabranjene izmene na `bpzoran/gadapt`.

## Naučni status i pitanje
Iteracija 6 je pronašla 0/12 izvodljivih incumbenta u uskoj
formulaciji od prvih osam generatorskih naponskih zadatih vrednosti.
To nije dokaz nepostojanja izvodljivog rešenja. Sledeći korak je
**audit izvora ograničenja pre predlaganja novog algoritma**.

Nezavisni izvor modela je MATPOWER `case1888rte` (Josz i sar., 2016):
https://matpower.org/docs/ref/matpower6.0/case1888rte.html
Ovi podaci služe validaciji metoda, ne eksploataciji ili planiranju
stvarne mreže. MATPOWER RATE_A=0 znači neograničenu granu:
https://matpower.app/manual/matpower/DataFileFormat.html .
Pandapower `loading_percent` predstavlja relativni termički kriterijum
u odnosu na parametre preuzete pri konverziji. Ispitati dostupnost
`max_i_ka`, `max_loading_percent`, `sn_mva` i njihovih vrednosti
**pre** zaključka o statusu granica.

## Zamrznuta prva faza — pregled i osetljivost, bez optimizacionog poređenja
- Javni `pandapower.networks.case1888rte()`, netaknut topološki model,
  množioci potrošnje 1.0 (glavni) i 1.1 (odvojeni stres), dokumentovati
  sve varijante; ispoštovati `runpp(init="dc", algorithm="nr",
  enforce_q_lims=True, max_iteration=40, tolerance_mva=1e-8,
  numba=False)` iz iteracije 6.
- Referentni vektor *prvih osam* `net.gen.vm_pu`, ograničen na
  0.95–1.08 kao u iteraciji 6. Jedna početna fizička evaluacija
  plus po dve nezavisne perturbacije za svaki od 8 napona (+/- 0.02 p.u.,
  isečeno na opseg), ukupno **17 pravih AC solver poziva po faktoru**,
  uključujući neuspehe; nikakvo prikriveno naknadno PF pozivanje.
- Sačuvati statistike ulaznih limita i raspoloživih naponskih,
  reaktivnih, šant i tap/transformator elemenata. Rezidual: posebno
  zbrojevi kršenja napona, vodova, transformatora, ekstremne grane,
  promena reziduala pri perturbaciji, Q-limit zasićenja.
- Jedinica reziduala: napon p.u. i `(loading_percent-100)/100` za
  vode/trafo. Ovo je *heuristička normalizacija*, ne indeks
  sistemske bezbednosti. Poštovati ograničenja iz izvornih podataka,
  ali 100% pravilo ostaje samo **istraživački eksperiment** dok se ne
  utvrdi odnos sa publikovanim RATE_A i pretpostavkama konverzije.
- Sačuvati ceo CSV/JSON i GitHub Actions logove. Ako je solver
  nekonvergentan, bez lažne izvodljivosti. Poređenja metoda i
  statističko testiranje NISU deo ove dijagnostičke faze;
  17 perturbacija nisu nezavisna optimizaciona semena.

## Posle dijagnostike
Na osnovu merenja unapred definisati novu, odvojenu formulaciju,
sa izborom stvarno raspoloživih kontrole i fizičkih ograničenja.
Svaki novi benchmark zamrznuti pre izvođenja. Nema naknadnog
šminkanja izvodljivosti. Debova pravila, epsilon-constraint,
stochastic ranking, lokalna restauracija, OPF i memetička
hibridizacija već su u literaturi (npr. pregled
https://doi.org/10.1007/s11081-022-09782-9).
Poređenje sa standardnim solverom iz **iste** formulacije je obavezno.

## Reproduktivnost
Python 3.12, pandapower 2.14.11, scipy 1.13.1, pandas 2.2.3,
`PYTHONHASHSEED=0` i jednonitni OPENBLAS/OMP/MKL/NUMEXPR.
Ovo nije potvrda potpunog numeričkog identiteta van proverenog CI.

## Dodatak A (2026-10-21): statička topološka provera pre širenja promenljivih
Posle prvog AC audita ustanovljeno je da svih 29 prema modelu
preopterećenih grana pripadaju transformatorima. `net.trafo` nema
kompletne `tap_min/tap_max/tap_step_percent` opsege, a svih 45
šantova imaju `step=max_step=1`; zato se tapovi i šant koraci
**ne tretiraju kao slobodne kontrole** bez novog modela.

Bez dodatnih AC poziva proveriti veze tih transformatora sa
generatorima, vrednosti fiksnog P dispatch-a, nominalne snage,
stvarne konverzije limita i stepen susedstva. Tražiti nove P
kontrole **samo** među `net.gen` sa konačnim objavljenim
`min_p_mw/max_p_mw`, važećim opsegom i bar 5 MW raspoloživog
smanjenja snage. Prioritet: najmanje topološko rastojanje od
krajeva 15 preopterećenih transformatora, zatim veći raspoloživi
raspon smanjenja, zatim indeks generatora; najviše osam.
Izbor iz ovog razvoja NIJE nezavisan holdout.

Ako postoji radijalna grana, prisustvo fiksne aktivne
injekcije veće od nazivne snage je samo **indikacija**
ograničenog prostora restauracije; dokaz bi dodatno zahtevao
proveru svih razmena, šantova, ugla/tapa i precizne definicije
strujnog ograničenja na odgovarajućem terminalu.
Nema predviđanja uspjeha novog algoritma pre testa.

Zasebna potencijalna proširena formulacija: prvih osam
generatorskih napona plus do osam tako odabranih P setpointa,
uz automatsko aktivno balansiranje spoljne mreže. Ova formulacija
ima drugačiju raspoloživu fleksibilnost od istorijskih 8 napona,
pa se ne sme direktno porediti sa istorijskim optima.
Eksperimentalne metode i budžet dodatno će se zamrznuti
pre novih optimizacionih izvršavanja.
