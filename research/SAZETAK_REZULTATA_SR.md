# Najnovije I32 — druga topologija IEEE14: 12.913 STVARNIH source AC, transfer signala ali NE i dokaz originalne metode (22.10.2026)

**Preregistrovano pre simulacija i završeno 72/72 run-a (6 metoda × 12 novih semena 2104–2115) na originalnoj IEEE14 mreži**, različitoj od ranije IEEE118. **12.913/12.960 stvarnih PYPOWER runpf AC**, nula numeričkih neuspeha, proverene originalne individualne PG/QG, sabirničke naponske granice, originalne pozitivne RATE_A oba kraja i KCL **u sva tri** sintetička originalna PD/QD scenarija. To je 9D PV-kontrolisani *podskup*, ne pun AC-OPF ili industrijska mreža.

| Originalni problem IEEE14, tri scenarija | Semena sa ≥1 potpuno verified source-feasible | Broj verificiranih kandidata | Stvarni native AC |
|---|---:|---:|---:|
| Legacy GA full_true | 8/12 | 47 | 2160 |
| Legacy GA full_censored (sva tri AC plaćena, cenzurisana selekcija) | 9/12 | 82 | 2160 |
| **Legacy GA stop_fixed** | **12/12** | **404** | **2149** |
| Legacy GA stop_adaptive | 12/12 | 403 | 2146 |
| SciPy DE full_true | 3/12 | 3 | 2160 |
| SciPy DE stop_fixed | 7/12 | 13 | 2138 |

**Glavni upareni kontrast:** GA fixed screening 12/12 naspram potpuno fizički plaćenog GA censored 9/12, 3 diskordantna semena, **egzaktni dvostrani p=0,25**. Fixed GA naspram fixed DE 12/12 vs 7/12, p=0,0625. **NEMA statistički značajnog testa na 0,05** niti prenosa na industriju; adaptivno ređanje nije dokazano korisnije od fiksnog. Na prethodnoj IEEE118 topologiji I31 u drugoj grani analogan GA censored/fixed rezultat bio je 7/12 vs 11/12, p=0,125: smer signala se ponavlja, ali pozitivna „algoritamska novina“ ne postoji i nije dokazana generalna prednost. I32 korigovano razdvaja *selekcioni score* od broja zaista fizički ispitanih kandidata.

[Kompletan izveštaj I32](ITERATION32_REPORT_SR.md) · [protokol pre stvarnog AC](ITERATION32_PROTOCOL.md) · [72 stvarna individualna raw JSON zapisa](results/ieee14_iteration32_12seed_6arms_12913_real_AC_20261022.json) · [72 CSV](results/ieee14_iteration32_12seed_6arms_12913_real_AC_20261022.csv) · [stvarno uspešan GitHub Actions run 39686171613](https://github.com/owlCoder/gadapt/actions/runs/39686171613) · [originalni fizički artifacts](https://github.com/owlCoder/gadapt/actions/runs/39686171613/artifacts/12386702402).

**Dalje:** novi preregistrirani kapacitetni/telekom GÉANT domen, odvojeno računanje stvarnih mrežnih evaluacija (NE električnih AC poziva), jaka nezavisna bazna metoda, prior-art pregled scenario racing i adaptivnog GAdapt budget kontrolera. **Nema još dokazanog doktoratskog originalnog doprinosa.**

---

# NAJNOVIJE I29–I30 — opipljiva ušteda AC evaluacija kroz opt-in GAdapt screening, ALI naučna originalnost NIJE dokazana (21.10.2026)

**I29: pravi opt-in source code evaluator UNUTAR GAdapt paketa**:
[gadapt/operations/cost_finding/sequential_scenario_budget_cost.py](../gadapt/operations/cost_finding/sequential_scenario_budget_cost.py).
Evaluira iste originalne 6 PV generator VG kontrole pod tri realno plaćena
AC load scenarija, i samo nakon dokazanog fizičkog izvornog Q/P/V/positive
RATE_A/KCL kršenja može **preskočiti naredni scenario bez predstavljanja
kao izmerenog**. Pozitivna robust feasibility i source original
mean economic cost zahtevaju **stvarno tri izvršena, AC-konvergentna
i source-feasible** scenarija. NR neuspeh NIJE dokaz matematičke
neizvodljivosti. Testovi, uključujući integraciju sa stvarnim default
GA, prošli Python **3.10, 3.11, 3.12**; originalni GA default
je nepromenjen.

**I29 uniformno sintetičko opterećenje 98/100/102%:**
20 run-ova, **3.583 STVARNA IEEE118 AC** od max 3.600:
GAdapt full **1/4** uspešna run-a / **1** verificiran all-three source
candidate; GAdapt stop-fixed **4/4** / **118**; GAdapt stop-adaptive
**4/4** / **118**, potpuno isti ishod kao fixed. DE full **0/4**
/ **0**, DE fixed **4/4** / **9**. Ovo nije izolovan efekat
novog adaptivnog operatora: pretraga i fizikalno proveravanje
promenjeni su pre svega poznatim first-fail screen-om i njegovom
censored heurističkom fitness ocenom. [I29 detaljan izveštaj](ITERATION29_REPORT_SR.md) ·
[raw JSON, 3583 stvarnih AC](results/ieee118_iteration29_scenario_earlyreject_20runs_trueAC_20261021.json) ·
[preregistracija I29](ITERATION29_PROTOCOL.md) ·
[CI #39669410103](https://github.com/owlCoder/gadapt/actions/runs/39669410103).

**I30 unapred definisana NOVA PROSTORNA PD/QD promena na ISTOJ
IEEE118 mreži**: za neparne source BUS_I load ×1,02 a parne ×0,98,
ili obrnuto, plus nominalni source režim.
20 run-ova, **3.580 pravih AC** od max3600; GAdapt
full **2/4** / **14** source three-scenario verified feasible,
GAdapt stop-fixed **2/4** / **58**, stop-adaptive **2/4**
/ **60**; DE full **3/4** / **3**, DE stop-fixed
**4/4** / **44**. U seed-u 2070 early GA **nije našao
nijednu** source robust-feasible tačku iako je full našao 5,
a u seed-u 2072 obrnuto — nije dokazano da screening povećava
**broj uspešnih GAdapt run-ova** na različitom spatial load-u.
Adaptivni redosled je dao samo 2 dodatna validated
kandidata, ne uspešno seme ili jeftiniji optimum.
[I30 pun izveštaj](ITERATION30_REPORT_SR.md) ·
[raw JSON 3580 source AC](results/ieee118_iteration30_spatial_parity_holdout_20runs_3580_trueAC_20261021.json) ·
[preregistracija I30](ITERATION30_PROTOCOL.md) ·
[CI #39671017417](https://github.com/owlCoder/gadapt/actions/runs/39671017417).

**KLJUČNO ZA DOKTORAT:** first-failure screening i stochastic
scenario evaluations **već postoje u literaturi**, uključujući
Sankary et al. 2018 (doi:10.1002/2017WR022068), vidi
[prior-art I29](ITERATION29_PRIOR_ART_SR.md). Naš softver jeste
direktno reproduktivan i realno štedljiviji na ovom
kalibrisanom testu, ali **nismo dokazali novu naučno
originalnu GAdapt algoritamsku metodu, statističku
superiornost ili industrijsku efikasnost**. I26 novi
scenario-UCB operator reward je u ranijoj I28
12-seed proveri dao samo 6/12 uspeha naspram 8/12
originalnog GAdapt-a i NIJE potvrđen.
**Sledeći korak pre rada sa još većim brojem iteracija:
sa mentorom definisati dokazivo različitu originalnu hipotezu,
odvojiti broj genome-a, censored fitness i redosled,
pa testirati nezavisne mreže/domene.**

---

# NAJNOVIJE I28 — 12 novih uparenih semena NIJE potvrdilo prednost novog GAdapt scenario-UCB mehanizma (21.10.2026)

**Novi direktni GAdapt mutator-credit iz I26 radi i testiran je**, ali
**stvarni unapred registrovani eksperiment I28 POBIJA tvrdnju
o njegovoj većoj ponovljivoj efikasnosti na dosadašnjem IEEE118
problemu**. Nakon I27 samo jednog pozitivnog `scenario_feasibility`
semena (1/3) i nula ostalih metoda, I28 zamrzava potpuno
**NOVIH 12 uparenih semena 2040–2051**, **4 ista originalna
core GAdapt moda**, isti 6D IEEE118 originalni PV kontrolni
prostor, ista veštačka tri PD/QD opterećenja 98%/100%/102%,
isti originalni izvorni PG/QG, bus V, source-positive RATE_A
oba kraja i KCL limiti, **180 stvarnih AC po svakom
method×seed**. **48 stvarnih GA run-ova = 8.640 originalnih
PYPOWER AC PF** u zvaničnoj analitičkoj seriji,
bez lažnih fizičkih poziva.

| GAdapt opcija | Bar jedan potpuno source-feasible 3-load kandidat na 12 semena | Broj trostruko fizički izvodljivih kandidata (720 pokušaja po metodi) |
|---|---:|---:|
| **Originalni legacy GAdapt** | **8/12** | **73/720** |
| Postojeći objective-UCB | **6/12** | **65/720** |
| Postojeći scalar-feasibility-UCB | **6/12** | **70/720** |
| **Novi I26 scenario-feasibility-UCB** | **6/12** | **70/720** |

Za sva 12 uparenih seedova, **novi UCB nikada nije uspeo
kada postojeći objective/scalar-UCB nisu**, i oba postojeća
UCB moda imaju **identične binarne success/failure
seme obrasce** kao novi. U poređenju sa originalnim
GAdapt-om, legacy uspeva na dodatna 2 semena, novi ni na
jednom dodatnom. **I28 ne pokazuje superiornost** novog
reward-a; sa 12 semena ne tvrdimo statistički značajnu
superiornost legacy modа, niti generalizaciju izvan istog
prethodno fizički kalibrisanog IEEE118 zadatka.

**Audit stvarnog broja AC:** zbog ispravke *samo*
fluktuirajućih Python testnih očekivanja, GitHub Actions
je izvršio dve **identične** uspešne serije sa po
8.640 stvarnih AC; ukupno **17.280 fizičkih AC**
u I28 CI istoriji, ali samo **12 jedinstvenih semena**
u zvaničnoj analizi (ne lažnih 24). Oba CI loga sadrže
istovetne numeričke rezultate, osim runtime-a.

[Kompletni I28 negativni izveštaj](ITERATION28_REPORT_SR.md) ·
[I28 protokol pre rezultata](ITERATION28_PROTOCOL.md) ·
[raw JSON 48 run-ova i 8.640 realnih AC](results/ieee118_iteration28_12_newseed_4_GAdapt_credit_8640_real_AC_20261021.json) ·
[zvanična puna realna CI serija #39666171453](https://github.com/owlCoder/gadapt/actions/runs/39666171453) ·
[identična nezavisno tehnički ponovljena CI #39666251610](https://github.com/owlCoder/gadapt/actions/runs/39666251610) ·
[preliminarni audit naučne originalnosti i literature 2000–2026](ITERATION28_LITERATURE_NOVELTY_AUDIT_SR.md).

**Sledeća odluka je metodološka, a ne tuning:** ne
podešavati nova reward weight podešavanja na istom
IEEE118 slučaju dok se ne proveri precizna novina
u robust AC-OPF, AOS, feasibility handling i
scenario evaluation budget literaturi. Potom
posebno unapred registrovati mehanizam koji je
stvarno različit (npr. *budžetski svesno
biranje AC scenarija* ili fizički potpuno naplaćen
uparen-mutator credit) i out-of-sample više mrežnih
scenarija i domena. **Originalni doktoratski
algoritamski doprinos još nije dokazan.**

---

# NOVO I26–I27 — prva stvarna izmena GAdapt algoritma i 3.240 realnih IEEE118 AC kontrola (21.10.2026)

**PRVI PUT smo direktno izmenili izvorni `gadapt/...` algoritamski
kod** u `owlCoder/gadapt:main`. **I26:** potpuno opcioni
`GA(mutation_operator_policy='ucb',
mutation_operator_credit='scenario_feasibility',
mutation_scenario_count=3,mutation_evaluation_counter=...,
mutation_violation_function=...)` u **stvarnom** GA mutation operator
credit controlleru, koji koristi već postojeći UCB za izbor
mutatora i novi unapred definisan reward iz tri pojedinačne
izvorne scene/constraint violation vrednosti. Svaki postbudget
candidate bez stvarno plaćena **sva 3 solver AC** ne dobija
operator nagradu; delimičan batch fail-closed. **Legacy default
GA ostao nepromenjen; stari i novi testovi uspešni na Python
3.10, 3.11, 3.12.** Ovo je inženjerski istraživački prototip;
postojeći UCB, feasibility credit, AOS i robust constraint
reward **nisu naše originalne naučne ideje**.

**I27:** prvi unapred registrovani direktni fizički benchmark:
**6 metoda × 3 semena × 180 stvarnih originalnih IEEE118 AC
poziva = 3.240 pravih simulacija**, 60 u celosti izmerenih
tri-load kandidata za svaki optimizer run. Svaki jedinstveni
6D PV VG vektor testiran je pod **PD/QD load 98%, 100% i
102%**, source P/Q svih 54 gen, V svih 118 bus, oba terminala
pozitivno rated RATE_A i kompleksni KCL svake scene. Šest PV
gen BUS103/32/34/92/19/**74**, ovaj poslednji uveden po
prethodno poznatom Q stresu, **isti za sve metode**, pa je
benchmark u **već informisanom in-sample prostoru**, ne
out-of-sample dokaz.

| Metod | Realni AC | Broj all-3 source-feasible kompleta | Broj uspešnih od 3 seed-runova |
|---|---:|---:|---:|
| Legacy GAdapt | 540 | 0 | 0/3 |
| Existing GAdapt UCB objective credit | 540 | 0 | 0/3 |
| Existing GAdapt UCB scalar worst-scenario feasibility | 540 | 0 | 0/3 |
| **NOVI GAdapt UCB scenario-feasibility** | **540** | **1** | **1/3** |
| SciPy DE | 540 | 0 | 0/3 |
| Bounded Powell (ponovljen centriran deterministički) | 540 | 0 | 0/3 |

Jedini kandidat koji zadovoljava **SVA TRI** izvorna
fizička režima je novog GA moda seed2028, stvarni AC
poziv #177, 6 PV controls
`[0.9898506009,0.9700322306,0.9865841207,0.9944308972,0.9643283682,0.9601205052]`,
originalni tri-load economic cost srednja **131.314,640348**,
source max Q violation **0** u sva tri, KCL rezidual max
~**2,02e-10 MVA**. Ostalih **17/18** run-ova nije našlo
all-three feasible, iako mnogi kandidati jesu izvodljivi za
1–2 load režima. Ovo je **samo jedna pilot naznaka**,
nipošto statistički dokaz superiornosti, uzročne zasluge
operator-credit nagrade, globalnog optimuma ili naučne
originalnosti. Problem i PG/VG prostor unapred su
fizički kalibrisani pomoću ranijih iteracija I19–I25.

[I26 izveštaj implementacije novog core GAdapt-a](ITERATION26_REPORT_SR.md) ·
[I26 pre-registracija](ITERATION26_PROTOCOL.md) ·
[I26 CI 3x Python zelen #39662796544](https://github.com/owlCoder/gadapt/actions/runs/39662796544).

[I27 kompletni izveštaj pravih novih/legacy GA ablation AC](ITERATION27_REPORT_SR.md) ·
[I27 pre-registracija](ITERATION27_PROTOCOL.md) ·
[I27 sva 18-run realna raw JSON evidence](results/ieee118_iteration27_3load_scenario_GAdapt_ablation_20261021.json) ·
[I27 zelen CI stvarnih 3240 AC #39663741753](https://github.com/owlCoder/gadapt/actions/runs/39663741753).

**Sledeći korak:** veće pre-registrirane originalne
domenske kontrolne uporedne studije, više seedova,
više izvornih multi-scenario problema, detaljni literature
review AOS/robust-constraint/feasibility-credit, ablation
reward komponenti, pa tek onda dokazivati doktorski
doprinos. **Sada IMAMO novu funkcionalnu izmenu
GAdapt-a i prvi stvarni pozitivan kandidat, ali nemamo
dokaz originalne ili statistički bolje naučne metode.**

---

# NOVO I25 — test robusnosti pet source-feasible IEEE118 VG odluka pri veštačkom PD/QD stresu ±2% (21.10.2026)

**I25: tačno 10 NOVIH stvarnih originalnih IEEE118 AC NR PF proračuna**,
pre-registriranih PRE simulatora, bez novog GAdapt/DE/random/Powell
optimiserskog pokušaja. Izveštaj se odnosi na **veštački nametnuti
faktor 0,98 ili 1,02 za PD i QD svih sabirnica** i pet unapred
selektovanih, ranije fizički izvodljivih VG vektora (I23 α=.8 i
najbolji originalni GAdapt, DE, random, Powell iz I24).

- Na **98% originalnog PD/QD: 0/5 source-feasible** kandidata.
  Svih pet konvergira u AC, ali svi krše individualne originalne
  generator Q granice, uključujući uporan BUS74 Q exces oko
  **1,552 MVAr**. Nijedan P/V/izvorni RATE_A overload.
- Na **102% originalnog PD/QD: 2/5 source-feasible**:
  prethodna I23 deterministička tačka sa stres-ekonomskom cenom
  **134.993,698462** i prethodni najbolji `random_search`
  source kandidat **134.991,355175**. Prethodni GAdapt, DE
  i Powell best 100%-load tačke nisu source-feasible na 102%
  zbog originalnog BUS92 Q prekoračenja. Njihove **feasible
  economic cene su null**. Niti jedan stres AC nije numerički fail.
- To **NE ZNAČI** da su GAdapt/DE/Powell kao algoritmi
  robusno lošiji od random ili da puna IEEE118 mreža nema
  izvodljiv AC-OPF na stresu: **metode nisu ponovo pokrenute**,
  svega jedan najbolji istorijski source kandidatski vektor
  po metodi je naknadno fizički proveravan; svi 0,98/1,02
  su veštački javni scenariji, nisu stvarni pogonski podaci.

**I24:** originalni legacy GA, DE, random i centered Powell
imali su **1.152 STVARNA AC PF** u in-sample kalibrisanom
pet-generator PV prostoru. Svaka metoda ima 3/3 source-feasible
run-a, originalni GAdapt ukupno 106/288 feasible AC,
DE 18/288, random 7/288, Powell 201/288 (67 ponovljenih
puta tri potpuno identične determinističke putanje).
**Powell** ima najniži originalni fizički feasible source cost
**131.193,636506**, uz istorijski informed start. Originalni
GAdapt: **131.195,131546** najbolji. Nema dokazane
algoritamske novine ili statističke superiornosti.

[Izveštaj I25](ITERATION25_REPORT_SR.md) ·
[raw JSON 10 pravih stres AC](results/ieee118_iteration25_5_prior_feasible_PV_2percent_stress_10_AC_20261021.json) ·
[protokol I25](ITERATION25_PROTOCOL.md) ·
[uspešan CI I25 #39660714312](https://github.com/owlCoder/gadapt/actions/runs/39660714312).

[Izveštaj I24](ITERATION24_REPORT_SR.md) ·
[raw JSON 12 real optimizer run-ova I24](results/ieee118_iteration24_legacy_gadapt_de_random_powell_20261021.json) ·
[protokol I24](ITERATION24_PROTOCOL.md) ·
[uspešan CI I24 #39659382865](https://github.com/owlCoder/gadapt/actions/runs/39659382865).

**Sledeća rigorozna faza disertacije:** sprovesti zajednički
scenario-aware **GAdapt, DE i strong local** benchmark, pri kojem
*svaki* kandidat preko N nezavisnih izvornim PD/QD scenarija
košta tačno **N STVARNIH AC** i čuva pojedinačne izvorne
P/Q/V/positive RATE_A/KCL povrede. Nakon literature o
feasibility-aware selection, AOS, sensitivity repair i robust AC OPF
formulisati potencijalno novu mehaniku *unutar stvarnog GAdapt-a*,
ablaciju, jače bazne metode i znatno više uparenih semena.
Sadašnji izvorni javni IEEE rezultati **ne dokazuju
originalnost doktorata ni industrijsku validaciju**.

---

# NOVO I24 — pravi GAdapt naspram DE, random i Powell na istih 5 originalnih IEEE118 PV kontrola (21.10.2026)

**1.152 NOVA stvarna AC PF poziva** izvršena na originalnom
`pypower.case118()` kroz stvarni **neizmenjeni `gadapt.ga.GA`**,
SciPy differential evolution (bez `polish`), uniform random i
lokalni bounded Powell, **4 metode × 3 semena × 96 pravih AC poziva**.
Sve individualne originalne generator PG/QG, 118 bus VMIN/VMAX,
pozitivni source RATE_A MVA na oba kraja i kompleksni AC nodalni
bilans provereni za svaki stvarni kandidat. Svih **12/12**
optimizatorskih pokretanja imaju fizički izvodljivog kandidata;
0/1152 numerički neuspešnih AC.

**Sva 4 metoda koriste ISTIH 5 fizički relevantnih VG kontrola**:
BUS103, BUS32, BUS34, BUS92 i BUS19. Lokalni box
`centar ±0.005 p.u.` je **izabran na osnovu ranijih stvarnih
I19–I23 AC dijagnostika**: ovo je unapred preregistrovan
**in-sample kalibracioni** eksperiment, **NIJE** nezavisna potvrda
na novom mrežnom scenariju i NIJE pokazana algoritamska novina.

| Metod | Realni AC | Izvorno fizički izvodljivi kandidati | Najbolji stvarno izvodljiv originalni ekonomski cost |
|---|---:|---:|---:|
| **Neizmenjeni originalni GAdapt** | 288 | **106** | **131.195,131546** |
| Differential evolution | 288 | **18** | **131.194,777680** |
| Uniform random | 288 | **7** | **131.196,562290** |
| **Bounded Powell** | 288 | **201** (67 ponovljena × 3 identične determinističke putanje) | **131.193,636506** |

Lokalni Powell ima **najbolji ostvareni fizički validiran cost**,
ali uz deklarisani **informisani centralni `x0`**; njegove 3
seme-putanje nisu 3 nezavisne stohastičke replikacije. Njegov
`OptimizeResult.success=False` znači samo **potrošenih 96
`maxfev`** bez formalne konvergencije, ne neizvodljivost —
67/96 AC evaluacija po putanji prošlo je proveru svih source uslova.
GAdapt ima više izvodljivih uzoraka od DE/random, ali **NIJE**
ostvario najbolji ekonomični cost. Samo 3 seed-a, **nema dokaza
statističke superiornosti**. Ponovljeni originalni I23 izvodljivi
candidate i I16 širi izvorni ekonomski AC-OPF nisu besplatno
uračunati u ove AC pozive.

[Celovit izveštaj I24](ITERATION24_REPORT_SR.md) ·
[preregistrovani protokol I24](ITERATION24_PROTOCOL.md) ·
[raw JSON svih 12 optimizer run-ova](results/ieee118_iteration24_legacy_gadapt_de_random_powell_20261021.json) ·
[uspešan GitHub Actions #39659382865](https://github.com/owlCoder/gadapt/actions/runs/39659382865).

**Sledeći disertacijski uslov:** slepi izlazni test na izmenjenim
load/P/Q/naponskim scenarijima sa istim kontrolama i jednako
naplaćenim AC pozivima, zatim tek literaturom potkrepljen
nov GAdapt feasibility-aware mehanizam i ablation; rezultati
I24 su dobar metodološki baseline, NE doktoratski dokaz
originalnog algoritamskog doprinosa ni industrijski field test.

---

# NAJNOVIJE I19–I23: IEEE118 izvorno fizički izvodljive kontrolne tačke kroz 35 pravih AC proba (21.10.2026)

**Prvi put je u ranije neuspešnom IEEE118, ograničenom
fiksni-P/PV-kontrolisanom istraživačkom podskupu pronađena potpuno
izvorno fizički izvodljiva tačka**, ali **NE pomoću novog GAdapt-a**.
Ovo je transparentan domenski deterministički Q/VG
*feasibility-repair* dijagnostički niz: **I19 = 10, I20 = 8,
I21 = 8, I22 = 5, I23 = 4, ukupno 35 NOVIH stvarnih AC PF poziva**,
svaki brojan na stvarnoj NR solver granici, sa unapred registrovanim
protokolom pre svakog fizičkog eksperimenta, bez besplatnih
simulacija ili prikrivanja neizvodljivih rezultata.

- **I19:** originalni IEEE118 PG/VG imao 6 Q-offendera,
  zbir **78,099195 MVAr**, dominantno BUS103 i BUS105; devet starih
  I18 best-penalized vektora je fizički replayovano bez promene scores.
- **I20:** source BUS103 VG 1,01→0,99 rešio obe trajne Q
  povrede BUS103/BUS105, Qtotal smanjen na **32,345808 MVAr**
  sa još 4 druga QMIN offender-a.
- **I21:** source BUS32 VG 0,963→0,973 smanjio Qtotal na
  **30,525901 MVAr**, ostala BUS34/BUS92/BUS19;
  ostali veliki `±0,01` VG koraci uglavnom pogoršavali Q.
- **I22:** mala originalna Q/VG korekcija iz *ranije zaista
  izmerenih konačnih razlika* dovela do **2,464456 MVAr**
  jednog QMIN prekršaja BUS92 na polovičnoj zajedničkoj korekciji,
  ili **3,642855 MVAr** QMIN prekršaja BUS36 na punoj korekciji,
  oboje još neizvodljivi.
- **I23:** sva četiri unapred zamrznuta međukoraka α=0,6/0,7/0,8/0,9
  stvarno rešena; **α=0,7 i α=0,8 su kompletno source-feasible**
  prema individualnim **svih 54 generatora PG/QG**, svih
  **118 naponskih VMIN/VMAX**, originalnim pozitivnim `RATE_A` MVA
  oba kraja, sa kompleksnim AC bilansom max ≈**1,6·10⁻¹⁰ MVA**.
  Bolji takav izvorni fizički izvodljiv ekonomični candidate ima
  `gencost` **131.198,797575**, ali **NIJE** pun
  globalni AC-OPF optimum, poboljšani GAdapt ili statistički dokaz.
  α=0,6 i 0,9 su ostali Q-neizvodljivi i nisu izostavljeni.

Ovi nalazi pokazuju **izbor fizički relevantnih kontrola i malih
proračunatih VG koraka** kao mogući istraživački pravac. **NE SME**
se porediti “35 dijagnostičkih AC” sa “864 GA/DE/random I18 AC”
kao fer nadmetanje: drugačije reprezentacije, uzastopno
data-guided izabrane kontrole i različiti ciljevi. Originalni
puni IEEE118 AC-OPF je već bio lokalno source-feasible u I16,
sa širim PG/Q/V kontrolama. Originalan algoritamski doprinos
unutar stvarnog GAdapt-a i industrijska primena **nisu dokazani**.

[Izveštaj I23 i detaljni dve feasible tačke](ITERATION23_REPORT_SR.md) ·
[I23 raw JSON četiri realna AC](results/ieee118_iteration23_qbracket_4_real_ac_20261021.json) ·
[I23 CI uspešan #39656195300](https://github.com/owlCoder/gadapt/actions/runs/39656195300) ·
[Izveštaj I22](ITERATION22_REPORT_SR.md) ·
[Izveštaj I21](ITERATION21_REPORT_SR.md) ·
[Izveštaj I20](ITERATION20_REPORT_SR.md) ·
[Izveštaj I19](ITERATION19_REPORT_SR.md).

**Sledeći doktorski rad:** zamrznuti istu izvorno
relevantnu PV kontrolnu reprezentaciju i fizički budžet za
legacy GAdapt, DE, random, jaku lokalnu bazu i eventualni
novi *feasibility/sensitivity-aware* GAdapt sa potpuno naplaćenim
dodatnim AC merenjima; pre tvrdnje o novosti pregledati AOS,
constraint-handling, sensitivity-guided repair literaturu i
testirati na mnogo uparenih semena i više domena. Dati broj
samo dokumentuje klasičnu inženjersku korigovanu fiziku,
ne rezultat novih GA poređenja.

---

# NOVO — Iteracije 17 i 18: realan GAdapt, 1.728 pravih IEEE AC PF poziva (21.10.2026)

**Prva stvarna, strogo fizički budžetirana provera originalnog
`gadapt.ga.GA` naspram SciPy DE i random search na *izvornim
MATPOWER/PYPOWER* javnim testnim mrežama.** Ukupno izvršeno
**1.728/1.728 stvarnih Newton–Raphson AC proračuna** (864 IEEE14 +
864 IEEE118), plus jasno izdvojeni virtualni optimizer zahtevi
posle fizičkog limita koji nisu proračuni. Originalni upstream
`bpzoran/gadapt` nije menjan. Algoritam legacy GAdapt **nije
modifikovan**; ovo je bazni pilot za buduću disertacijsku inovaciju.

**IEEE14 — izvorno opravdan fizički izvodljiv *devetodimenzionalni
PV-kontrolisan podskup* AC-OPF sa originalnom ekonomskom funkcijom:**
GAdapt je našao bar jedan fizički izvodljiv kandidat u **2/3**
uparena semena; DE u **1/3**, random u **1/3**. Najbolja fizički
izvodljiva cena među sva 9 izvršavanja bila je **8.892,350877**
za **DE**; najbolja GAdapt **9.575,672226**.
Ova tri semena **ne dokazuju superiornost** niti jednog metoda.
Izvorni puni AC-OPF referentni lokalni ekonomski cost iz I16 je
**8.081,526393**, ali on rešava **širi optimizacioni problem**,
te direktno poređenje performansi pod istim budžetom nije moguće.

**IEEE118 — devet promenljivih, četiri najveća originalna non-slack
PG, pet VG, ostalih 49 PG/VG generatora nepromenjeno:** svih **864**
AC proračuna numerički je konvergiralo, ali **0 fizički izvodljivih
kandidata** kroz 9 metoda/seme pokretanja; GAdapt, DE i random
jednako nisu našli feasible. Ovo ne znači da puna IEEE118 mreža
nema izvodljiv OPF: iteracija 16 ima proverenu punu AC-OPF tačku,
ali sadašnji pilot ima bitno **uži** prostor i mali budžet.

[Izveštaj I17 IEEE14](ITERATION17_REPORT_SR.md) ·
[protokol I17](ITERATION17_PROTOCOL.md) ·
[kompletni I17 JSON](results/ieee14_iteration17_real_gadapt_de_random_20261021.json) ·
[uspešan I17 CI #39645834755](https://github.com/owlCoder/gadapt/actions/runs/39645834755).

[Izveštaj I18 IEEE118](ITERATION18_REPORT_SR.md) ·
[protokol I18](ITERATION18_PROTOCOL.md) ·
[kompletni I18 JSON](results/ieee118_iteration18_real_gadapt_de_random_20261021.json) ·
[uspešan I18 CI #39646983369](https://github.com/owlCoder/gadapt/actions/runs/39646983369).

**Zaključak za doktorat:** potvrđena izvršiva i ponovljiva bazna
metodologija na dva javna infrastrukturna problema; u
sadašnjoj verziji algoritma nema dokazanog originalnog adaptivnog
doprinosa, nema statističke superiornosti, nema validacije
industrijske operacije niti transfera izvodljivosti na IEEE118.
Sledeća naučno smislenija faza mora prvo objasniti koji izvorni
Q/V/P resursi sprečavaju izvodljivost na većem sistemu, a potom
formulisati *nov* mehanizam sa nezavisnim i snažnim bazama, ne
slučajno dodavati heuristike.

---

# ZAVRŠENA ITERACIJA 15: originalni veliki RTE1888 AC-OPF ostaje nepotvrđen (21.10.2026)

Posle izvornog PYPOWER ekonomski AC-OPF pokušaja sa strategijom 560 iz
iteracije 14 (izvorni RTE1888 je vratio `success=False` za oko 5,20 s),
**iteracija 15** je unapred registrovala i stvarno pokrenula
step-controlled PIPS `OPF_ALG=565` sa identičnim originalnim
MATPOWER P/Q/V/RATE_A i generator `gencost` podacima. Mali kontrolni
`case9` je konvergirao za oko **0,553 s** i **12 iteracija**,
ali originalni veliki **RTE1888 nije konvergirao u unapred dozvoljenih
780 sekundi**; izvršavanje je prekinuto `TimeoutError`.
Nema prihvaćene vrednosti originalne RTE ekonomske funkcije cilja,
fizički izvodljivog rešenja niti statističkog rezultata o GAdapt-u.
Ovaj timeout **nije dokaz da je originalni AC-OPF matematički neizvodljiv**.

[Izveštaj I15](ITERATION15_REPORT_SR.md) ·
[protokol I15](ITERATION15_PROTOCOL.md) ·
[sirovi JSON I15](results/rte1888_iteration15_source_acopf_solver_565_20261021.json) ·
[uspešan CI beleženja sa isteklim timeout-om #39641058963](https://github.com/owlCoder/gadapt/actions/runs/39641058963).

**Prioritet ostaje fizički verifikovani IEEE14 i IEEE118 AC-OPF iz
iteracije 16**, kao proverljiva osnovica za naredno strogo budžetirano
testiranje pravog GAdapt algoritma. Napomena: IEEE testne mreže nemaju
dokazani industrijski stres pri izvornim jako labavim termičkim
granica; bez potvrdne fizičke provere nema tvrdnji o realnoj industriji.

---

# NAJNOVIJI PROVERENI DOMENSKI REZULTAT: originalni AC-OPF IEEE14 i IEEE118 (21.10.2026)

**Iteracija 16** donela je dve originalne javne IEEE AC-OPF reference sa
stvarnim PYPOWER `runopf` pozivima i nezavisno ponovo izračunatim
fizičkim rezultatima: oba solvera prijavila `success=True`, oba
prošla ograničenja **originalnih pojedinačnih PG/QG, VMIN/VMAX,
pozitivnih RATE_A na oba kraja, složenog AC bilansa i izvornog
polinomnog troška**. IEEE14 ekonomska vrednost: **8.081,526393**;
IEEE118: **129.660,686390**. Gubici u MW nisu ista ciljna funkcija.
Kontrolni originalni RATE_A limiti su labavi (max iskorišćenost
1,31% i 4,18%). Ovo **nisu** rezultati GAdapt-a, dokaz globalnog
optimuma, stvarna industrijska merenja ili validacija RTE1888.

[Izveštaj I16](ITERATION16_REPORT_SR.md) ·
[originalni IEEE AC-OPF JSON](results/ieee14_ieee118_iteration16_native_acopf_20261021.json) ·
[protokol I16](ITERATION16_PROTOCOL.md) ·
[potvrđeni CI #39642073586](https://github.com/owlCoder/gadapt/actions/runs/39642073586).

**Iteracija 14:** prvi direktni originalni RTE1888 *ekonomski*
AC-OPF sa slobodnim PG, originalnim generatorskim `gencost` i
native PYPOWER solverom; kontrolni `case9` uspešan, ali originalni
RTE1888 `success=False`, **nema prihvaćenog izvodljivog rešenja**.
Ta činjenica **ne dokazuje** matematičku neizvodljivost celog problema.
[Izveštaj I14](ITERATION14_REPORT_SR.md) ·
[originalni source OPF sirovi JSON](results/rte1888_iteration14_original_acopf_20261021.json) ·
[CI #39640202591](https://github.com/owlCoder/gadapt/actions/runs/39640202591).

Sledeći doprinos za mentora mora biti nova, literaturom opravdana
adaptacija **stvarnog GAdapt** algoritma, sa istom fizičkom formulacijom
i budžetima stvarnih AC poziva u odnosu na relevantne metode.
Dosadašnji rezultati to **još ne dokazuju**.

---

# NAJNOVIJE — Iteracije 11–13: originalni MATPOWER AC model direktno validiran (21.10.2026)

**Važan napredak pre algoritamskog GAdapt rada:** više se ne oslanjamo
isključivo na različitu pandapower konverziju velikog RTE1888 modela.
Direktno smo arhivirali **1888 izv. BUS / 298 GEN / 2531 BRANCH**
MATPOWER 2019 ulaza i pokrenuli **5 stvarnih originalnih native AC PF
pokušaja**: dva iz iteracije 11, dva iz iteracije 12 i jedan iz
iteracije 13. Svaki poziv je evidentiran, uključujući softverske
`IndexError` neuspehe. Izvedeni lokalni PYPOWER Q-enforcement repair
je reproducibilan, sa minimalnim unapred registrovanim izmenama,
zasebnom kontrolom i regresionim testovima.

**Poslednji rezultat (iteracija 13):** nativni originalni AC PF **uz
nametnute generator Q limite konvergirao**; međutim, originalna
slack BUS1320 postala je PQ, dok je solver novu referencu postavio na
**BUS89**. Ostaće **41** bus ispod VMIN sa ukupno **0,052373 p.u.**
nedostatka i **10** izvornih aktivnih generatora sa ukupno
**54,95 MW ispod PMIN**; ista desetorica već krše PMIN u izvornoj
ulaznoj datoteci, pre bilo kog AC proračuna. Prekoračenje izvornih
pozitivnih RATE_A nema, a Q kršenja su nakon enforcementa praktično nula.
**To još nije fizički izvodljiv originalni AC-OPF niti rezultat
optimizacije GAdapt-om.** Matematička neizvodljivost punog AC-OPF
nije dokazana, pošto P-dispečing nije optimizovan.

[Izveštaj iteracije 13](ITERATION13_REPORT_SR.md) ·
[pre-registracija](ITERATION13_PROTOCOL.md) ·
[izvorni Q-enforced JSON](results/rte1888_iteration13_original_q_limited_20261021.json) ·
[uspešan CI #39631108812](https://github.com/owlCoder/gadapt/actions/runs/39631108812) ·
[izveštaj iteracije 12 (dokumentovan neuspešan pokušaj)](ITERATION12_REPORT_SR.md) ·
[izveštaj iteracije 11 (direktni originalni native PF)](ITERATION11_REPORT_SR.md) ·
[originalni 298x21 GEN](results/rte1888_iteration11_original_matpower_gen_full21_2019.csv) ·
[originalni 2531x13 BRANCH](results/rte1888_iteration11_original_matpower_branch_full13_2019.csv) ·
[istraživačka mapa doktorskog rada](DOCTORAL_GADAPT_INDUSTRY_ROADMAP_SR.md).

**Sledeće:** nezavisna izvorna AC-OPF formulacija sa slobodnim P
dispečingom i proverenim P/Q/V/RATE_A ograničenjima, zatim
naučno novo, literaturom provereno poboljšanje **stvarnog** GAdapt-a
poređeno na istom fizičkom problemu. Bez preuranjenih tvrdnji o
superiornosti ili industrijskoj sertifikaciji.

---

# NOVO — Iteracija 10: AC slack P/Q granice — dva prava fizička proračuna (21.10.2026)

**Presudan negativan nalaz za formulaciju velikog industrijskog benchmarka:**
izvorna MATPOWER 2019 slack sabirnica jeste 1320, a stara
pandapower konverzija koristi 1268. Preregistrovane **2 stvarne AC
Newton–Raphson evaluacije** obe su konvergirale, ali nijedna nije
potpuno fizički izvodljiva: u konvertovanom originalnom stanju
slack ima P=55,006 MW, **32,994 MW ispod sopstvenog konvertovanog
ext-grid-only Pmin**. To NIJE originalni agregatni test: dodatni
sgen na istom bus-u ima 44,5 MW, pa originalni zbir BUS1268 iznosi
**99,506 MW, odnosno 9,506 MW iznad izvornog zbira Pmax=90 MW**;
post-hoc korekcija urađena bez ijednog novog AC poziva. u izolovanom scenariju sa vraćenom slack lokacijom
1320 slack Q=**1.384,477 MVAr**, a originalni QMAX=**1 MVAr**,
tj. preko limita za **1.383,477 MVAr**. Naponske povrede ostaju,
a originalna pozitivna termička RATE_A ograničenja nisu prekoračena
u ova dva slučaja. Sirovi **gubici u MW nisu izvodljivi optimumi**.

Dosadašnji indikator source-rated iz iteracije 7 proverava napone i
pozitivne izvorne RATE_A, ali **ne podrazumeva puno proverene P/Q
granice slack izvora niti potpuni AC-OPF**. Ove dve različite
formulacije ne smeju se predstavljati kao isti optimizacioni zadatak
ili kao dokaz da je originalna MATPOWER mreža matematički neizvodljiva.

[Izveštaj](ITERATION10_REPORT_SR.md) ·
[Pre-registracija](ITERATION10_PROTOCOL.md) ·
[CSV dve stvarne AC simulacije](results/rte1888_iteration10_source_slack_ac_20261021.csv) ·
[JSON](results/rte1888_iteration10_source_slack_ac_20261021.json) ·
[post-hoc izvorni zbir P](results/rte1888_iteration10_posthoc_source_bus1268_p_20261021.json) ·
[Uspesan CI #39625839475](https://github.com/owlCoder/gadapt/actions/runs/39625839475).

---

# NOVO — Iteracija 9: proverena generatorska ograničenja i neslaganje slack-a (21.10.2026)

**Kritičan nalaz pre bilo kakvog narednog industrijski relevantnog GAdapt benchmarka:**
MATPOWER original 2019 ima referentnu/slack sabirnicu **1320**, dok
`pandapower.networks.case1888rte()` postavlja `ext_grid` na originalnu
sabirnicu **1268**. Izvorni generator na sabirnici 1320 nije
prenet kao aktivni `gen`, `sgen` niti `ext_grid`. Stoga
**dosadašnji AC rezultati nisu validacija izvorno identičnog MATPOWER
AC-OPF slučaja**, već konvertovane mreže sa eksplicitno navedenim
ograničenjima. **Nije dokazano** da ta razlika objašnjava sve neuspehe
pri uspostavljanju fizičke izvodljivosti.

Pozitivno: **264/264** nedvosmislena originalna/konvertovana
generatorska para imaju identičnih svih šest polja PG, PMIN,
PMAX, QMIN, QMAX, VG; sve **1888/1888** naponske granice i
nominalni kV odgovaraju originalnom izvoru. Za 17 preostalih
generatorskih sabirnica mapiranje je složenije. Original ima 298
redova generatora, 291 aktivan. Ova iteracija je **statički audit,
sa 0 fizičkih AC proračuna**, ne novo algoritamsko poboljšanje.

[Izveštaj](ITERATION9_REPORT_SR.md) ·
[Pre-registracija](ITERATION9_PROTOCOL.md) ·
[Potpuni JSON](results/rte1888_iteration9_source_generator_conversion_audit_20261021.json) ·
[298 izvornih gen redova](results/rte1888_iteration9_original_matpower_generator_rows_2019.csv) ·
[1888 izvornih bus redova](results/rte1888_iteration9_original_matpower_bus_rows_2019.csv) ·
[Uspešan CI #39624498771](https://github.com/owlCoder/gadapt/actions/runs/39624498771).

---

# NOVO — Iteracija 8: reaktivno-naponski screening RTE1888 (21.10.2026)

Završeno je novo, **eksploratorno** fizičko merenje sa osam
dodatnih generatorskih naponskih setpointa (izabranih deterministički
blizu referentno narušenih sabirnica) uz source-rated `RATE_A`
formulaciju iz iteracije 7. [GitHub Actions #39619997942](https://github.com/owlCoder/gadapt/actions/runs/39619997942):
**17/17 stvarnih AC proračuna konvergiralo**, najmanji rezidual
pao je sa **1,091786** na **1,055456**, ali **0/17 kandidata
nije potpuno izvodljivo**. Nema originalnog superiornog
algoritma niti punog OPF rezultata. U referenci je
11 generatora na Qmin, 14 na Qmax, bez eksplicitnih Q
prekoračenja; izvorna verifikacija Q granica ostaje otvorena.

[Izveštaj](ITERATION8_REPORT_SR.md) ·
[Zamrznuti protokol pre AC testa](ITERATION8_PROTOCOL.md) ·
[CSV svih 17 poziva](results/rte1888_iteration8_reactive_screen_20261021.csv) ·
[JSON sa Q statistikama i selekcijom kontrola](results/rte1888_iteration8_reactive_screen_20261021.json) ·
[Izvršni kod](iteration8_reactive_screen.py).

---

# NOVO — Iteracija 7: revizija izvodljivosti RTE1888 (21.10.2026)

Izvršena je nezavisna provera stvarnog porekla termičkih
ograničenja iz originalnog MATPOWER `case1888rte`.
**455/2531 izvorne grane imaju `RATE_A=0`, što znači
da MATPOWER ne propisuje termičku MVA granicu za te grane.**
Mapirane su na 233 transformatora i 222 voda u pandapower.
Konkretno, istorijski „209% opterećen trafo404“ ima
`sn_mva=99,999` u konvertovanom modelu, ali njegov
izvorni MATPOWER branch453→1699 ima `RATE_A=0`.

Prethodni stres-test iteracije 6 (0/12 fizički izvodljivih)
bio je ispravno izmeren **za istorijsku formulaciju sa
našim nametnutim 100% granicama**, ali ne može biti dokaz
neizvodljivosti izvorne francuske test-mreže.
Uslovni radijalni dokazi 14 preopterećenih transformatora
važe samo pod veštački dodatom MVA granicom;
ta pretpostavka nije ispunjena u izvoru.
Ovaj rezultat je značajan **negativan metodološki nalaz**,
ne algoritamska superiornost.

Nova verzionisana formulacija koristi originalni RATE_A
u MVA na oba kraja grane i nema termičke granice kada
je RATE_A=0. U 17 stvarnih AC evaluacija nominalne
reference i 16 okolnih vektora:
- 0 stvarnih prekoračenja pozitivnih izvornih MVA limita
  u referentnom stanju;
- početni zbir naponskih povreda **1,091786 p.u.**,
  na 120 sabirnica;
- 17/17 proračuna konvergira, ali 0/17 potpuno
  izvodljivih kandidata, minimum naponskog reziduala
  **1,079486 p.u.**.
Na 110% opterećenja je 17/17 AC proračuna bilo nekonvergentno,
bez tvrdnje da ne postoji matematičko rešenje.

**Završni algoritamski pilot** na ispravljenoj formulaciji:
5 metoda (GAdapt-penalitet, GAdapt-feasibility-first, SLSQP,
fiksni hibrid i DE) × 3 semena (350–352) × 72 stvarne AC
simulacije = **15 pokretanja, 1.080 stvarnih PF evaluacija**.
Sve metode imaju 0/3 fizički izvodljiva pokretanja. Medijalni
minimumi mera kršenja: GAdapt 1,073343, feasibility-first 1,073343,
SLSQP 1,078234, fiksni hibrid 1,078234, DE 1,073555.
Nema valjanog uporednog MW cilja među izvodljivima.
Holm-korigovan sign test četiri poređenja prema GAdapt: p=1,0
svuda; uz n=3 ovo NIJE statistička potvrda ekvivalencije.
Ostao je naponski problem i problem suviše uskog
kontrolnog prostora, ne izvorni termički overload.
[Sirova optimizaciona tabela](results/rte1888_iteration7_source_rated_pilot_20261021.csv),
[statistika](results/rte1888_iteration7_source_rated_stats_20261021.json),
[SVG grafikon](figures/rte1888_iteration7_source_rated_violation.svg),
[GitHub Actions 1080 AC](https://github.com/owlCoder/gadapt/actions/runs/39608967519).

Svi dokazi i sirovi podaci su na `owlCoder/gadapt:main`;
[izveštaj](ITERATION7_REPORT_SR.md),
[protokol](ITERATION7_PROTOCOL.md),
[34 stvarna AC poziva](https://github.com/owlCoder/gadapt/actions/runs/39608593545),
[2531 izvorna granica](results/rte1888_matpower_original_branch_ratings_2019.csv).
Nov metod zasnovan na poznatoj feasibility-first ideji
ne može biti predstavljen kao originalni doprinos doktoratu.
Nema potvrde industrijske pouzdanosti ili globalnog optimuma.

---

## NOVO — Iteracija 6: IEEE118 i francuski RTE1888, 21. oktobar 2026

**Ovo su završeni stvarni AC-eksperimenti, a ne planirani rezultati.**
Fiksni istraživački protokol: [ITERATION6_PROTOCOL.md](ITERATION6_PROTOCOL.md).
Potpun izveštaj: [ITERATION6_REPORT_SR.md](ITERATION6_REPORT_SR.md).

IEEE118, dva opterećenja, šest novih uparenih semena, tačno 180 stvarnih
Newton–Raphson AC proračuna po metod–seme–opterećenje slučaju:

| Metod | Medijalni izvodljivi gubici 100% | Medijalni izvodljivi gubici 110% |
|---|---:|---:|
| Originalni GAdapt | 131,841563 MW | 172,760037 MW |
| **Samostalni SLSQP** | **131,553953 MW** | **172,554719 MW** |
| Fiksni GAdapt→SLSQP | 131,720128 MW | 172,675001 MW |
| Adaptivni GAdapt→SLSQP | 131,677102 MW | 172,695446 MW |
| SciPy DE | 131,834761 MW | 172,812701 MW |
| CMA-ES | 131,960103 MW | 172,949908 MW |

Novi kontroler je unapred propisanim signalima odlučivao između 30%,
55% i 75% GA budžeta; zabeleženo je po četiri `feasible_stalled` i
dve `feasible_improving` odluke po opterećenju. Ipak, adaptivni
hibrid imao je samo 1/6 pobeda nad fiksnim pri 100% i 2/6 pri 110%.
Samostalni SLSQP je pobedio originalni GAdapt u 6/6 pokretanja, ali
sa pet Holm-korigovanih poređenja p=0,15625.
**Nema potvrđene prednosti adaptivnog hibrida**. Svi metodi našli su
fizički izvodljiv rezultat 6/6, što uz Wilson 95% interval
[0,6097; 1] nije dokaz visoke industrijske pouzdanosti.

RTE1888, četiri metode × tri semena × 72 stvarna AC proračuna:
**nula fizički izvodljivih rešenja u svih 12 pokretanja.**
Fiksni model sa samo osam upravljivih napona ne eliminiše
početna prekoračenja termičkih granica: minimum ukupnog kršenja
oko 16,24–16,27. Nema legitimiteta tvrditi ostvareni izvodljivi
optimum gubitaka ove RTE formulacije.

Sirovi podaci, statistika i SVG/PNG grafikoni su sačuvani direktno
u `owlCoder/gadapt:main`. 
[IEEE118 test](https://github.com/owlCoder/gadapt/actions/runs/39582074680),
[RTE test](https://github.com/owlCoder/gadapt/actions/runs/39582153291),
[nezavisna verifikacija statistike](https://github.com/owlCoder/gadapt/actions/runs/39583243300).

**Naučna preporuka:** nastaviti istraživanje formulacije i restauracije
fizičke izvodljivosti (kontrolni resursi, ograničenja, OPF), pre
dodavanja novih heurističkih pragova. Trenutna adaptivna strategija
nije dokazani originalni doktorski doprinos.

---

## NOVO — Iteracija 5, 21. oktobar 2026: provera ostvarive preciznosti IEEE14

Završena je opširnija studija na stvarnom GAdapt paketu i PYPOWER AC solveru.
Za dve instance (100% i 110% opterećenja), 12 novih uparenih semena
(100–111) i 360 stvarnih AC evaluacija po metodi postignuto je sledeće:

| Metod | Medijalni gubici 100% | Medijalni gubici 110% |
|---|---:|---:|
| Originalni GAdapt | 14,318710 MW | 17,735386 MW |
| Affine GAdapt | 14,458830 MW | 17,875307 MW |
| SLSQP (više početaka) | **13,497284 MW** | **16,792139 MW** |
| GAdapt→SLSQP | 13,497333 MW | 16,792250 MW |
| SciPy DE | 13,651538 MW | 17,529568 MW |
| CMA-ES | 13,498865 MW | 16,794541 MW |

SLSQP, GAdapt→SLSQP i CMA-ES imaju 12/12 pobeda naspram originalnog
GAdapt-a za oba opterećenja; egzaktno sign p=0,00048828125,
Holm p=0,00244140625 po opterećenju za pet primarnih poređenja.
To je snažan **problem-specifičan** signal, ali SLSQP samostalno daje
bar jednako kvalitetna rešenja kao GAdapt→SLSQP, pa to NIJE
originalan doprinos genetskom algoritmu.

Odvojena pretraga sa 3600 fizičkih evaluacija po opterećenju, uz
još jedan nezavisan AC proračun po najboljem kandidatu, ostvarila je
13,497263522715254 MW (100%) i 16,791946841097882 MW (110%).
Oba rešenja ispunjavaju implementirane tolerancije. To su
**najbolje ostvarene izvodljive vrednosti, NE dokazani globalni optimumi**
ili garantovano minimalne vrednosti za kompletnu AC-OPF formulaciju.
Postojeća šira literatura optimizuje i tapove, šantove ili drugi aktivni
dispečing, pa njeni gubici nisu direktno uporedivi sa našom užom
petodimenzionalnom formulacijom.

Na GÉANT planiranju sa 44 već poznate vremenske matrice (8 semena,
360 pravih evaluacija) GAdapt→diskretna koordinatna pretraga imao je
medijalni trošak 194.553 prema 197.526 kod originalnog GAdapt-a,
ali najgori 219.202 prema 206.526, uz 5:3 pobeda/poraza i
Holm p=0,7265625. Dakle nema statistički potvrđene koristi niti
poboljšanja repa distribucije.

Naučni zaključak: u IEEE14 sa pet promenljivih GAdapt ne koristi
lokalnu strukturu kao jaki standardni optimizatori; prosto dodavanje
SLSQP-a kao poslednje faze poznata je memetička tehnika, ne doktorat.
Originalni doprinos još mora biti razvijen i proveren na većim,
nezavisnim infrastrukturnim zadacima, sa korektno uračunatim budžetima.

Detalji i sirovi CSV: [ITERATION5_REPORT_SR.md](ITERATION5_REPORT_SR.md).
Prijavljen validiran CI sa statistikama/grafikonima:
https://github.com/owlCoder/gadapt/actions/runs/39579649231

---

# GAdapt — istraživački status za mentora (21. oktobar 2026)

**Radni naslov:** Unapređenje stabilnosti, pouzdanosti i tačnosti GAdapt algoritma za optimizaciju infrastrukturnih sistema.

**Repozitorijum:** `owlCoder/gadapt`; razvojna grana `research/robust-diversity-baseline`. Originalni `bpzoran/gadapt` i `owlCoder/gadapt:main` nisu menjani.

**Važno:** Ovo su rezultati početnih istraživačkih iteracija i nisu dokaz završenog doktorskog doprinosa, globalne superiornosti, industrijske spremnosti niti bezbednosti za upravljanje kritičnom infrastrukturom.

## Istraživački problemi i kod koji je nastao

1. **Osetljivost mere raznovrsnosti na prevođenje i skaliranje funkcije cilja.** Originalna logaritamska mera menja odluke adaptacije kada se ciljna funkcija zameni ekvivalentnom pozitivnom afino transformacijom. Razvijena je opciona mera `cost_diversity_metric="affine_invariant"`. Podrazumevani originalni režim ostaje aktivan; nova mera rešava matematičku osetljivost, ali je relativno osetljiva na ekstremne vrednosti.
2. **Degenerisana početna populacija.** Originalna referentna mera može da ostane na nultom normalizovanom koeficijentu čak i kada se naknadno pojavi raznovrsnost. Nova mera prepoznaje povratak nenulte raznovrsnosti.
3. **Stagnacija.** Dodata je opciona metoda `adaptive_immigration_patience`, `adaptive_immigration_percentage`, `adaptive_immigration_diversity_threshold`: osvežavanje dela populacije samo pri stagnaciji i niskoj raznovrsnosti. Ova ideja je poznatog tipa u evolucionoj optimizaciji; novost i korist tek treba dokazati.

## Validacija stvarnog GAdapt koda (ne prototip)

### IEEE14 AC elektroenergetska mreža

Standardizovan IEEE14 model sa AC tokovima snaga, ograničenjima napona, reaktivne snage i raspoloživim termičkim ograničenjima. Svaka od tri metode koristi 240 evaluacija; 12 pokretanja po metodi i scenariju.

| Opterećenje | Metod | Uspešnost (izvodljivo rešenje) | Medijalni gubici među uspešnima |
|--|--|--:|--:|
| 100% | original | 12/12 | 14,343501 MW |
| 100% | afino-invarijantni | 12/12 | 14,378624 MW |
| 100% | SciPy DE | 12/12 | 14,305458 MW |
| 110% | original | 11/12 | 17,961366 MW |
| 110% | afino-invarijantni | 11/12 | 18,196904 MW |
| 110% | SciPy DE | 10/12 | 17,436417 MW |

Adaptivno osvežavanje na 110% dalo je 11/12 i medijanu 17,939863 MW (ograničen pilot). **Nema opšteg poboljšanja preciznosti nove mere.** Izvor: https://github.com/owlCoder/gadapt/actions/runs/39549392997 i https://github.com/owlCoder/gadapt/actions/runs/39550594130.

### Telekomunikaciona mreža GÉANT — stvarni objavljeni podaci

SNDlib objavljuje topologiju (22 čvora, 36 linkova), 462 zahteva, kapacitetne module i planske cene. Postavljen je istraživački problem diskretnih težina ruta i nabavke modula; to je **naš optimizacioni model na javnim istorijskim podacima**, ne proizvodna mreža. 30 pokretanja, 360 evaluacija po metodu.

| Metod | Medijalni planski trošak | Najgori zabeleženi |
|--|--:|--:|
| original GAdapt | 134.391,5 | 138.412 |
| afino-invarijantni GAdapt | 134.677 | 138.293 |
| afino-invarijantni + osvežavanje | 134.784,5 | 137.552 |
| SciPy DE | 136.867,5 | 141.331 |
| nasumična pretraga | 140.639 | 143.018 |

Upareni test nova mera naspram originalne: 17 pobeda nove, 11 pobeda stare, 2 nerešena; medijalna uparena razlika -129, bootstrap 95% interval [-517, 181], Wilcoxon p=0,600457 (**nema ubedljive statističke razlike**). Izvori: https://github.com/owlCoder/gadapt/actions/runs/39550042217 i https://github.com/owlCoder/gadapt/actions/runs/39550510560.

### GÉANT — vremenska merenja

Pribavljena arhiva 11.460 petnaestominutnih istorijskih matrica saobraćaja, SHA256 `92d72a808d6de9d26be66844c098d3f32d5b9bb6c69af170e82b73118faef0df`. Četiri uzorka (maj, jun, jul, avgust 2005) su numerički proverena. Originalna skala saobraćaja je degenerisana za velike module, pa je kreiran *poseban* i jasno označen inženjerski stres-scenario: jedan zajednički faktor 49,56981612 određen **samo na osnovu ranijeg razvojnog perioda** do nivoa objavljene SNDlib vršne matrice. Time se čuvaju vremenski obrasci, ali se ne može tvrditi da su apsolutne vrednosti stvarna proizvodna opterećenja. Avgustovski uzorak je ranije pregledan radi kontrole kvaliteta, zato **nije** potpuno netaknut završni test.

Osam pokretanja po metodu, 180 evaluacija:
| Metod | Medijalni razvojni planski trošak | Medijalni trošak plana za 4 perioda |
|--|--:|--:|
| original | 176.178 | 182.980 |
| nova mera | 176.682,5 | 177.718,5 |
| nova mera + osvežavanje | 176.682,5 | 177.718,5 |
| SciPy DE | 176.976,5 | 178.894,5 |
| nasumično | 180.256 | 182.855,5 |

Preliminarna prednost nove mere u trošku plana kroz sve periode zahteva proširene testove i korekciju za višestruka poređenja. Izvor: https://github.com/owlCoder/gadapt/actions/runs/39551823748.

## Neuspeh na velikom RTE reperu: rezultat koji se ne sme prikriti

Raniji kratak test na offline francuskom `case1888rte` (samo jedna slučajna inicijalizacija i četiri generacije) nije pronašao strogo izvodljivo rešenje nijednom metodom. To je **neuspešan smoke test**, ne dokaz da metoda na velikoj mreži ne može raditi. RTE podaci su objavljeni za proveru matematičkih metoda, ne za planiranje/upravljanje stvarnim evropskim mrežama. Izvor: https://github.com/owlCoder/gadapt/actions/runs/39550318045.

## Zaključak za mentorovu evaluaciju

- Dokazana je uska matematička slabost izvornog mehanizma i razvijena kompatibilna opciona alternativa.
- Povećanje univerzalne tačnosti **nije dokazano**; na IEEE14 alternativna mera uglavnom zaostaje.
- Statistički opravdano poboljšanje pouzdanosti i prenosivost na različite realne infrastrukturne probleme **nisu još dokazani**.
- Dosadašnje izmene su istraživačke ablacione komponente, ne kompletan originalni metod za disertaciju.

**Sledeća istraživačka hipoteza:** razvoj mehanizma izbora mutacionih operatora zasnovanog na njihovoj **izmerenoj koristi za poboljšanje izvodljivosti i kvaliteta rešenja**, uz korekciju za otklon i generalizaciju na neviđene uslove. Pre tvrdnje o naučnoj novini neophodno je proveriti literaturu o adaptivnom izboru operatora (AOS), bandit metodama, JADE/SHADE i algoritmima sa ograničenjima.

**Zahtevi pre disertacione tvrdnje:** unapred definisan statistički protokol; odvojeni razvojni i zaista netaknuti testni podaci; upareni budžeti stvarnih evaluacija; najmanje 50–100 ponavljanja kada se proučavaju retki neuspehi; kvantili najgorih ishoda i intervali pouzdanosti; nova nezavisna infrastruktura; domenski optimizator kao dodatna referenca; stručno potvrđena ograničenja; kod, logovi i sirovi rezultati dostupni za reprodukciju.

Izvori osnovnih podataka:
- https://sndlib.put.poznan.pl/geant.overview.action
- https://sndlib.put.poznan.pl/download/geant-rm.txt
- https://matpower.org/docs/ref/matpower6.0/case1888rte.html
- https://github.com/owlCoder/gadapt/blob/research/robust-diversity-baseline/research/DISSERTATION_PROTOCOL.md
