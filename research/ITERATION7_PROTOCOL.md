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
