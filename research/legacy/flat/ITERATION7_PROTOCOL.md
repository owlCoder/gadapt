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

## Dodatak B — pokušaj NUŽNOG uslova preko radijalnog terminala
Pre testiranja ove analitičke provere, u statičkom auditu top 15
transformatora identifikovani su krajnji autobusi povezani sa samo
jednim serijskim elementom, koji sadrže generatore na njihovim
publikovanim minimalnim aktivnim snagama. Primer: transformator 404
100 MVA, terminal 1705 sa 236,69 MW proizvodnje i 40 MW potrošnje.

Sada se proverava *nužan* uslov (nije dovoljan za izvodljivost):
na pravom jedino vezanom krajnjem busu bez drugih serijskih veza,
šantova, sgen/ext_grid i sa konstantnim P potrošačima,
`P_export_min = sum(P_gen_min) - sum(P_load)`. Za slučaj pozitivnog
min. eksporta iz busa, transformator sa nazivnom snagom S_n i 100%
**strujnim** limitom (pandapower `trafo_loading="current"`)
zahteva `P_export_min <= S_n * vmax_pu * V_nom_bus / V_nom_trafo_terminal`.
Ako je stroga suprotna nejednakost ispunjena i svi uslovi zaista
provereni iz net strukture, to je sertifikat neizvodljivosti
**za ovaj fiksirani model i termički uslov**, nezavisan od heuristike.
Za izvodljivost cele mreže dovoljno je da jedan tako obavezan
terminal ne može zadovoljiti fizičku granicu.

Obavezno proveriti radijalnost po **broju elemenata** (ne broju
različitih suseda), odsustvo prekidača i drugih izvora, konst. P
potrošnju, postojanje granica i stvarni odnos nazivnih napona.
Poređenje se odnosi na pretpostavljenu termičku granicu iz
pandapower konverzije; validnost izvornog RATE_A kao operativnog
limita ostaje **odvojeno otvoreno pitanje**. Nema potrebe za novim
AC pozivima u ovom matematičkom skriningu.

## Dodatak C — izvornim podacima verna termička ograničenja i pilot (PRE novih AC poziva)
**Fiksirano pre pokretanja novog AC eksperimenta, nakon strukturne
dijagnostike i transparentnog razotkrivanja RATE_A=0.**
Izvor MATPOWER `case1888rte.m`:
`MATPOWER/matpower@80b6e16f760f58721ad31221c7287c28259cd4ad`,
blob SHA `820bd317167381baf819d67eab7d886013e8b05a`;
CC BY 4.0, citirati Josz i saradnici 2016.
Originalni RATE_A=0 znači **neograničeno**.
Sirova matrica 2531 izvorna reda i redosled trajno su sačuvani u
`research/results/rte1888_matpower_original_branch_ratings_2019.csv`.
Izvršeni nezavisni CI #39607656391 potvrdio je 2531/2531 preslikanih
elemenata (1976 vodova, 555 transformatora) po `net.bus.name+1`,
krajnjim sabirnicama i očuvanom redosledu; 69 paralelnih grupa ima
različite RATE_A pa je provereno slaganje redosleda sa nezavisnim
preslikavanjem impedansi. Potvrđeno je 455 RATE_A=0, među kojima
233 transformatora i 222 voda. Konverzija ekvivalentnih impedansi
75 transformatora ima veće normalizovano odstupanje, pa je to
zaseban metodološki rezidual, ne dokaz bitovskog identiteta
svih električnih parametara originalnog i konvertovanog modela.

### Nova izdvojena AC formulacija (NIJE ekvivalentna iteraciji 6)
- Ista topologija/dispatch/pandapower `case1888rte` i
  `runpp(init="dc", algorithm="nr", calculate_voltage_angles=True,
  numba=False, enforce_q_lims=True, max_iteration=40,
  tolerance_mva=1e-8)`.
- Samo prvi osam `net.gen.vm_pu`, [0.95,1.08], opterećenje 100%
  za optimizacioni pilot; eksplicitno ne puni OPF niti N-1.
- Bus voltage limits `net.bus.min_vm_pu/max_vm_pu`.
- Svaka originalna RATE_A>0 uvodi **MVA limit** na oba kraja
  `max(hypot(P_from,Q_from),hypot(P_to,Q_to)) <= RATE_A`.
  Za RATE_A=0 NEMA termičkog ograničenja te grane.
  Ponovo proveriti 2531 match pair identifikatora pri konstrukciji.
- Normalizovana mera reziduala =
  zbir magnituda naponskih prekoračenja p.u. + zbir
  `max(S_from,S_to)/RATE_A -1` pozitivnih prekoračenja
  samo za pozitivne RATE_A. Ovo je eksperimentalna skala, NE
  metrika sigurnosti ili industrijske pouzdanosti.
- Solver nekonvergencija je neuspeh, nikada izvodljiv rezultat.
  Reaktivna ograničenja `pp.runpp(enforce_q_lims=True)` su primenjena,
  ali ovaj test ne dokazuje potpunu OPF izvodljivost sa svim
  generator P/Q obavezama, slack ograničenjima i operativnim režimima.
- Cilj samo za izvodljiva rešenja: gubici u MW. U neuspehu:
  minimalna fizička mera kršenja; nikada ne predstavljati
  penalizovani score kao izvodljiv optimum.

### Fiksni dijagnostički AC pilot
Referentna tačka + šesnaest +/-0.02 pomeranja prvih osam
napona, kao u originalnom auditu, 17 pravih PF poziva pri 100%
plus 17 pri 110% opterećenja. Služi validaciji nove formulacije;
110% ima poznate nekonvergencije iz prethodnog eksperimenta.
Svi pozivi računaju se i čuvaju, originalna matrica i verzije pinovane.

### Fiksni nezavisni optimizacioni mehanistički pilot (samo 100% opterećenje)
Ako novo mapiranje svih 2531 source RATE_A prođe bez nepodudaranja,
uporediti sledećih pet metoda na potpuno identičnoj novoj formulaciji:
1. postojeći stvarni GAdapt sa konvencionalnim `loss + 1e5*violation`;
2. stvarni GAdapt sa poznatim feasibility-first leksikografskim
   skalarnim rangiranjem (ne tvrditi novost);
3. samostalni multistart SciPy SLSQP sa standardnim penalitetom;
4. fiksni GAdapt→SLSQP sa polovinama fizičkog budžeta;
5. SciPy differential evolution sa istim penalitetom i bez polish.
Svi koriste fizičku proveru svakog predloženog vektora.
Seme 350,351,352 (3 nova uparena semena), population=12,
budžet **72 stvarna NR solver poziva po metodi i semenu**
(ukupno 15 pokretanja i 1080 PF poziva). Standardna procedura
GA/SLSQP/DE i punjenje budžeta iz `research.ieee118_allocation`,
uz istu zamrznutu numeričku konfiguraciju.
Pobednik samo po stvarno izvodljivom cilju; kada niko nije
izvodljiv, rangirati DESKRIPTIVNO minimalno kršenje i propale
pozive. Izveštavati medijanu, maksimum, svaku replikaciju, uparene
razlike. Sa n=3 **bez tvrdnje statističke superiornosti**;
Holm korekcija, ako se računa, ne može učiniti pilot potvrdom.
Negativan rezultat posebno znači da raspoložive promene samo
osam kontrola nisu dovoljne u testiranom budžetu, a ne
dokaz da kompletan RTE AC OPF nema izvodljivo rešenje.
Nema adaptivnog nameštanja parametara prema ovih 15 ishoda.

### Novost
Feasibility-first GA (Deb), standardni constraint handling, lokalna
restauracija i memetički hibridi su dobro poznati. Ovo je samo
mehanistička pilotska kontrola nad *ispravljenom formulacijom*.
Originalan doktorски mehanizam niti njegova superiornost još
nisu potvrđeni.
