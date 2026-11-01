# NAJNOVIJE I34 — prvi NOVI cenzurom zaštićeni operator-credit u core GAdapt, 7.126 STVARNIH GÉANT rutina; NIJE nadmašio legacy značajno (22.10.2026)

**NAUČNO BITNO:** realizovan je `GA(mutation_operator_policy="ucb", mutation_operator_credit="censored_verified_per_cost", mutation_scenario_count=3, mutation_evaluation_counter=..., mutation_violation_function=...)` **unutar samog GAdapt-a**, sa strogom poslednjom stvarnom 1–3 scenario evidencijom. Samo 3/3 stvarno pozvane i potpuno potvrđene source/hypothetical-cap izvodljive scene imaju `1/3` credit; 1/2/3 stvarno izmerene narušene scene reward `0`, numeric unknown i neizvršene scene **nemaju credit**. Izvorni default GA nije promenjen. **Poznate** AOS/credit/bandit/budget ideje nisu dokazano nove.

**PREREGISTROVAN, stvarno završen benchmark:** 5 GAdapt politika × 12 NOVIH uparenih seedova **2300–2311**, 120 stvarnih domen routing poziva po run plafon = **7.126/7.200 pravih Dijkstra+462 zahteva+module-price evaluacija**; **0 AC**, 0 numerički neuspešnih. Isti već viđeni javni GÉANT 22-node/36-edge/462-demand iz I33, isti **hipotetički ne-source cost cap 145000 po scenariju**, ista 3 **veštačka** spatial demand profila; ovo NIJE nezavisan operativni industrijski validation.

| GAdapt policy | Semena sa ≥1 stvarno 3-scenario cap-feasible | Potpuno potvrđeni kandidati | Prave ruting evaluacije |
|---|---:|---:|---:|
| **Legacy GA, postojeći fixed early stop** | **11/12** | **62** | 1423 |
| Existing objective-UCB, fixed stop | 9/12 | 57 | 1422 |
| Uniform NEW safe-credit, fixed stop | 11/12 | 58 | 1421 |
| **NEW cost-verified/censored-safe UCB, fixed stop** | **12/12** | **60** | **1420** |
| Existing I26 scenario-feasibility-UCB, FULL 3 routing | 3/12 | 3 | 1440 |

**Primarno novo naspram legacy:** 12/12 prema 11/12, samo **1 diskordantan seed**, **exact two-sided p=1, Holm p=1** — **nema potvrde superiornosti**. Jedino significant poređenje novog fixed naspram **starog full-scenario UCB** (12/12 prema 3/12), corrected p=0,01953125, **nije izolovan efekat novog reward-a** jer se istovremeno menja full vs stop broj kandidata i selekcioni fitness. Best verified mean module cost **136143 isti u sve četiri fixed politike**; novi UCB nije ostvario bolji best-source-recourse cost. Nužan novel literature and third unseen domain test.

**Prvobitni preflight CI** [#39691771826](https://github.com/owlCoder/gadapt/actions/runs/39691771826) je imao samo Python sintaksnu grešku u reporteru PRE prvog domen solver poziva; ovo je ispravljeno bez menjanja semena i protokola. Novi zero-routing i svi stari regression testovi prošli; **[originalni uspešni I34 pravi domain job #39691941881](https://github.com/owlCoder/gadapt/actions/runs/39691941881)** sa 60/60 runova.

[I34 kompletan kritički izveštaj](ITERATION34_REPORT_SR.md) · [preregistracija](ITERATION34_PROTOCOL.md) · [core implementaciona revizija](ITERATION34_IMPLEMENTATION_REPORT_SR.md) · [60 sirovih stvarnih GÉANT JSON rezultata](results/geant_iteration34_12seeds_5arms_7126_actual_routing_20261022.json) · [CSV](results/geant_iteration34_12seeds_5arms_7126_actual_routing_20261022.csv) · [prethodni I33 GÉANT 8580 ruting benchmark](ITERATION33_REPORT_SR.md).

**Doktorski zaključak:** metodološka i inženjerska sposobnost i stroga fizička računovodstvena bezbednost su proširene, ali nova core operator-credit hipoteza **nije dokazano efikasnija** od već postojećeg originalnog GAdapt-a sa fiksnim ranim screeningom. Ne podešavati operator reward na istom domenu samo da postignemo pozitive. Sledeća potvrda mora biti slepa/nezavisna topologija i novo fizičko domensko ograničenje, uz pravi novelty gap.

---

# NAJNOVIJE I33 — drugi domen GÉANT: 8.580 STVARNIH routing evaluacija, jedno Holm-značajno poređenje SAMO pod hipotetičkim cap-om (22.10.2026)

**5 uzastopnih koraka na `main` završeno:** (1) revizija javnog GÉANT osnovnog modela i njegovih neograničenih kupovina modula; (2) protokol unapred pre realnih poziva; (3) implementacija stvarnog GAdapt/DE sa brojanjem NetworkX Dijkstra/modularnih routing evaluacija i sintetički no-route testovi; (4) uspešna 72-run CI serija na originalnom 22-node/36-link/462-demand SNDlib izvoru; (5) izvorni rezultati, statistika, 2013–2026 prior-art audit i naredna konkretna doktorska hipoteza.

**6 metoda × 12 novih uparenih semena 2200–2211 × max120 stvarnih ruting simulacija = 8.580/8.640** stvarno izvršenih evaluacija, **0 elektroenergetskih AC** i 0 numerical failure. **I33 hipotetičko, NE IZVORNO FINANSIJSKO OGRANIČENJE:** `cost ≤ 145000` SNDlib price units za svaku od 3 **veštačka** nominal/odd-source-heavy/even-source-heavy scenarija. Ovo NIJE stvarno ograničenje telekom operatera, a funkcija cilja mean 3 scenario-specific module purchases NIJE jedan trajni hardverski plan.

| GÉANT metod | Semena sa ≥1 potvrđeno feasible POD NAŠIM HIPOTETIČKIM cap-om | Potpuno provereni cap-feasible kandidati | Realno brojane ruting evaluacije |
|---|---:|---:|---:|
| Originalni GAdapt full true | 3/12 | 4 | 1440 |
| Originalni GAdapt full censored (sva tri scenarija stvarno plaćena) | 2/12 | 2 | 1440 |
| **GAdapt first-failure `stop_fixed`** | **10/12** | **54** | 1423 |
| GAdapt `stop_adaptive` | 11/12 | 59 | 1421 |
| DE full true | 5/12 | 5 | 1440 |
| DE first-failure `stop_fixed` | 6/12 | 10 | 1416 |

**Tačno jedan od pet unapred definisanih statističkih kontrasta je značajan:** `GA full_censored` **2/12** vs `GA stop_fixed` **10/12**, 8 discordantnih seedova u korist rane evaluacione uštede, nijedan u obrnutoj strani. **Egzaktni dvostrani p=0,0078125; Holm(5) p=0,0390625**. Ovo podržava rezultat **unutar našeg sintetičkog GÉANT cap modela**, ne potvrđuje univerzalnu superiornost, industrijski nivo izvodljivosti ili naučnu novinu first-failure metode. Adaptivni redosled ima 11/12 prema 10/12 fixed, p=1, **nema dokaza dodatne koristi**. Analogni I31 i I32 budžetsko-score kontrasti na drugim elektroenergetskim mrežama imaju isti smer, ali p=0,125 i p=0,25, statistički nisu značajni.

[Kompletan I33 izveštaj](ITERATION33_REPORT_SR.md) · [I33 originalni protokol](ITERATION33_PROTOCOL.md) · [audit izvornosti finansijskog limita](ITERATION33_GEANT_MODEL_AUDIT_SR.md) · [I33 svi 72 originalno stvarno rutirana JSON zapisa](results/geant_iteration33_12seeds_6arms_8580_true_routings_20261022.json) · [CSV](results/geant_iteration33_12seeds_6arms_8580_true_routings_20261022.csv) · [stvarno zeleni CI run](https://github.com/owlCoder/gadapt/actions/runs/39689108919) · [prior art i precizna otvorena hipoteza](ITERATION33_PRIOR_ART_AND_NEXT_HYPOTHESIS_SR.md).

**Doktorski sledeći naučni pravac:** tek sada testirati literaturom razlikovanu `censor-aware + cost-normalized mutation operator credit` metodu **unutar izvornog GAdapt-a** (sa neizmerеним scenarijima kao unknown, ne nulom), uz I26 negativne operator-baseline rezultate, snažne domenske bazne optimizatore, novu potpuno netaknutu mrežnu instancu i veći broj stvarno nezavisnih seedova. Ne praviti novost od običnog UCB, prve povrede ili proizvoljnog cap-a. Upstream `bpzoran/gadapt` NIJE menjan.

---

# I31 prethodni krug sada objedinjен na main (22.10.2026)

**Kontrolisana I31 ablacija IEEE118**: 48 stvarnih GA izvođenja i **8.611 realnih originalnih PYPOWER AC**, četiri evaluacione opcije, 12 uparenih semena. Uspešno i potpuno tri-scenario fizički izvodljiv kandidat na 9/12 originalnom GAdapt-u sa punom ocenom, 7/12 punom/cenzurisanom kontrolom, 11/12 GAdapt-u sa fiksnim ranim odbijanjem i 10/12 adaptivnom redosledu. Ključni upareni kontrast cenzurisanih punih troškova prema ranom prekidu p=0,125, **bez dokazane statističke superiornosti**. Originalni workflow fizički je bio FAILED samo pri CSV izvozu nakon 48 kompletiranih runova; svih 48 sirovih log redova i stvarni JSON/CSV su sačuvani na main *bez nove fizičke ponovne simulacije*.

[Potpuni I31 izveštaj](ITERATION31_REPORT_SR.md) · [preregistrovani I31 protokol](ITERATION31_PROTOCOL.md) · [I31 raw JSON 48 run-ova](results/ieee118_iteration31_12seeds_4arms_8611_real_AC_20261021.json) · [originalni fizički I31 job](https://github.com/owlCoder/gadapt/actions/runs/39681669407).

---

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

# NOVO — Iteracija 7: RTE1888 izvor ograničenja pre heuristike (21.10.2026)

**Presudna metodološka korekcija:** u ranijem RTE1888 modelu
proveravali smo svaki pandapower transformator i vod prema
`loading_percent <= 100`, ali originalni MATPOWER `case1888rte`
ima **455 grana sa `RATE_A=0` (bez zadatog MVA termičkog limita)**.
U njihovom skupu nalazi se **233 transformatora** i 222 voda.
Stoga raniji rezultat 0/12 izvodljivih kandidata iz iteracije 6
ostaje tačan **samo za staru dodatno ograničenu formulaciju**;
nije dokaz matematičke neizvodljivosti mreže sa izvornim limitima.

Napravljen je audit **svih 2531 grana**, uključujući paralelne
grane sa različitim rating-om. U početnom stanju pri 100% opterećenja
0 grana krši pozitivne izvorne RATE_A MVA granice, ali 120 sabirnica
krši naponske granice i zbir naponskih reziduala je **1,091786 p.u.**
Na 110% opterećenja svih 17 determinističkih pokušaja iz
izdvojenog AC audita bilo je nekonvergentno.
Pri nominalnom opterećenju 17/17 stvarnih AC poziva konvergira,
ali 0/17 daje potpuno izvodljiv vektor.

**Završen i preliminarni petometodni pilot** na novoj source-rated formulaciji:
5 metoda × 3 nova uparena semena × 72 stvarna AC poziva = **1.080 AC proračuna**.
Sve metode imaju **0/3 izvodljiva pokretanja**; feasibility-first
GAdapt nema potvrđenu prednost nad originalnim GAdapt-om.
Četiri Holm-korigovana uparena sign testa: **p=1,0**; n=3 je
nedovoljan za tvrdnje o superiornosti. Vidi
[sirovi pilot](results/rte1888_iteration7_source_rated_pilot_20261021.csv),
[nezavisnu statistiku](results/rte1888_iteration7_source_rated_stats_20261021.json),
[SVG grafikon](figures/rte1888_iteration7_source_rated_violation.svg),
[CI izvršavanje](https://github.com/owlCoder/gadapt/actions/runs/39608967519),
[bibliografiju](ITERATION7_LITERATURE.md).

**Doktorски algoritam sa potvrđenom originalnošću/superiornošću
još nije pronađen.** Revidirani eksperimentalni cilj i dalje
sadrži samo osam napona, nije puni AC-OPF niti potvrđena
industrijska formulacija. Ovde ne treba porediti rezultate
sa drugačijim formulacijama.

Detalji, izvori, uslovni matematički dokazi, limitacije i kod:
[Izveštaj iteracije 7](ITERATION7_REPORT_SR.md),
[zamrznut protokol](ITERATION7_PROTOCOL.md),
[izvorni MATPOWER rating](results/rte1888_matpower_original_branch_ratings_2019.csv),
[kompletno 2531 mapiranje](results/rte1888_iteration7_matpower_to_pandapower_thermal_map_20261021.csv),
[novi stvarni AC CSV](results/rte1888_iteration7_source_rated_ac_probe_20261021.csv),
[GitHub Actions stvarni AC](https://github.com/owlCoder/gadapt/actions/runs/39608593545).

Ovo ažuriranje **ne menja** sirove rezultate ni istorijske
zaključke o ponašanju optimizatora unutar stare formulacije.
Samo precizira da ona nije adekvatno predstavljala izvornu
termičku izvodljivost.

---

## Iteracija 6 — IEEE118 i RTE: stvarni fizički rezultati, bez lažnog optimuma

**Provera ponovljivosti (naknadna korekcija okruženja):** dva prvobitna
IEEE118 izvršavanja sa istim semenom nisu bila bitovski identična.
Nakon fiksiranja `PYTHONHASHSEED=0` i jednonitnog BLAS/OMP/MKL
okruženja, [dva ponovljena puna izvršavanja IEEE118](https://github.com/owlCoder/gadapt/actions/runs/39584858314)
postigla su tačno iste izvodljive MW vrednosti za GAdapt, SLSQP,
oba hibrida i DE (60/60 metoda-seme-opterećenje zapisa), a CMA-ES
se razlikovao maksimalno ~1,03e-11 MW.
[RTE ponavljanje](https://github.com/owlCoder/gadapt/actions/runs/39584806628)
potvrdilo je 0/12 izvodljivih kandidata.
[Nezavisna analiza iz trajno sačuvanog CSV i slike](https://github.com/owlCoder/gadapt/actions/runs/39586016114)
prošla je u CI. Originalni i pinovani sirovi CSV su odvojeni;
**ista semena ne broje se kao nezavisne replikacije**.
Detaljan metodološki dodatak nalazi se u
[ITERATION6_REPORT_SR.md](ITERATION6_REPORT_SR.md).



**Završeno i reprodukovano na `main`:**
[Izveštaj na srpskom](ITERATION6_REPORT_SR.md) ·
[Unapred fiksiran protokol](ITERATION6_PROTOCOL.md) ·
[Pravi IEEE118 benchmark](ieee118_allocation.py) ·
[Odvojeni RTE stres-test](iteration6_rte_stress.py).

IEEE118 (osam generatorskih napona, dva faktora opterećenja,
šest novih semena × šest metoda × 180 stvarnih AC evaluacija = **72 pokretanja**):
standardni samostalni SLSQP ostaje najbolji po medijalnim izvodljivim
gubicima (131,553953 MW na 100%, 172,554719 MW na 110%).
Fiksni i eksperimentalni adaptivni GAdapt→SLSQP daju samo mešovite
rezultate. Ni jedna primarna razlika nije statistički potvrđena posle
Holm korekcije (n=6). Nema dokaza da je unapred zamrznuti
adaptivni kontroler bolji od fiksnog hibrida.
[Verifikovan IEEE118 CI](https://github.com/owlCoder/gadapt/actions/runs/39582074680).

Francuski RTE1888, 12 metod–seme slučajeva × 72 stvarna NR poziva:
**0/12 fizički izvodljivih rešenja** u modelu koji menja samo osam napona;
prijavljeno je minimalno kršenje mrežnih ograničenja, a ne
nepostojeći optimum izvodljivih gubitaka.
[Verifikovan RTE1888 CI](https://github.com/owlCoder/gadapt/actions/runs/39582153291).

Sirovi CSV: `results/ieee118_allocation_20261021.csv` (72 reda),
`results/rte1888_stress_20261021.csv` (12 redova).
[Nezavisno uspešno ponovno analiziranje i SVG/PNG grafikoni](https://github.com/owlCoder/gadapt/actions/runs/39583243300)
validira broj pravih poziva, svih šest metoda, 12 RTE redova i
ne imputira izvodljive MW rezultate kada fizičke granice nisu zadovoljene.
Svi detalji u [ITERATION6_REPORT_SR.md](ITERATION6_REPORT_SR.md).
**Kontroler je eksperimentalni research modul, ne promena GAdapt podrazumevane metode.**

---

## Iteracija 5: provera najboljeg ostvarenog rešenja, ne dokaz globalnog optimuma

Pregled **izvršenih eksperimenata, 360 objektivnih AC evaluacija po metodi,
12 novih uparenih semena i CMA-ES baseline-a**:
[ITERATION5_REPORT_SR.md](ITERATION5_REPORT_SR.md).
Prethodno fiksiran protokol: [ITERATION5_PROTOCOL.md](ITERATION5_PROTOCOL.md).

Na javnom IEEE14 AC referentnom sistemu potvrđena su rešenja sa gubicima
13.497263522715254 MW (100% opterećenje) i 16.791946841097882 MW
(110% opterećenje). Obe vrednosti dobijene su jednom visoko-budžetnom
pretragom i ponovo proverene nezavisnim AC solve-om. **To nisu
matematički sertifikovani globalni optimumi**, a IEEE14 nije industrijski
operativni uzorak. Na jednakih 360 AC evaluacija SLSQP i CMA-ES
pokazali su preciznost znatno bolju od originalnog GAdapt-a na ovoj
konkretnoj niskodimenzionalnoj formulaciji. Sama hibridizacija nije
originalan naučni rezultat.

Reprodukcija iz `owlCoder/gadapt:main`:

```bash
python -m pip install -e . 'scipy>=1.11,<1.16' 'pypower>=5.1,<6' 'networkx>=3.2,<4' 'cma>=4,<5'
python -m research.ieee14_local_refinement --seeds 12 --seed-start 100 --budget 360 --output ieee14_local_refinement.csv
python -m research.ieee14_cma_es --seeds 12 --seed-start 100 --budget 360 --output ieee14_cma_es.csv
python -m research.ieee14_best_known_reference --budget 3600 --de-stage 2000 --output ieee14_best_known_reference.csv
python -m research.geant_local_refinement --seeds 8 --seed-start 100 --budget 360 --output geant_local_refinement.csv
python -m research.analyze_geant_local_refinement geant_local_refinement.csv
python -m research.analyze_ieee14_six_method_pilot
```

Uključene su trajno verzionisane sirove numeričke tablice
`research/results/ieee14_local_refinement_20261021.csv`,
`research/results/ieee14_cma_es_20261021.csv`,
`research/results/ieee14_reference_3600_20261021.csv`,
`research/results/geant_local_refinement_20261021.csv`,
SVG grafikoni u `research/figures/` i svi izlazi GitHub Actions.
Zapisi `True/False` očuvani su u Python CSV formatu radi
reproduktivne statistike. Vremenski GÉANT blok je ranije pregledan;
**nije nezavisan holdout**. Kodovi SLSQP/CMA-ES predstavljaju postojeće
referentne metode, ne korisnikov originalni doktorski algoritam.

---

## Paired physical mutation-credit experiment — current `main`

`mutation_credit_assignment="paired"` is a STRICT opt-in research setting
for full GAdapt. Unlike ordinary adaptive mutation, it evaluates the same
offspring once BEFORE a one-variable mutation and once AFTER. **Both solver
calls consume the optimization budget.** This is a local effect comparison,
not a proof of improved final optimization or a new AOS theorem. The callback
must report a monotonically increasing number of genuine physical evaluations;
post-budget sentinel objective calls must NOT advance that counter.

```python
ga = GA(
    cost_function=physical_objective,
    mutation_operator_policy="ucb",  # or "uniform"
    mutation_operator_credit="objective",  # or "feasibility"
    mutation_credit_assignment="paired",
    mutation_evaluation_counter=lambda: actual_simulator_calls,
    ensure_unique_individuals=False,
    number_of_mutation_decision_variables=1,
    candidate_solution_mutation="random",
)
# For feasibility mode, also set mutation_violation_function to a
# cached metadata reader returning >=0 normalized physical violation,
# and None if that particular physical evaluation never occurred.
```

Regenerate raw CSV and paired tests on *both* public infrastructure models:

```bash
python -m research.paired_credit_ieee14 --runs 8 --budget 240 --output paired_ieee14.csv
python -m research.analyze_paired_credit_ieee14 paired_ieee14.csv
python -m research.paired_credit_geant --runs 8 --budget 240 --output paired_geant.csv
python -m research.analyze_paired_credit_geant paired_geant.csv
```

The older GÉANT August block is **reused** (not a new independent holdout).
Full protocol: [PAIRED_CREDIT_PROTOCOL.md](PAIRED_CREDIT_PROTOCOL.md).
No method may be asserted scientifically superior on 8 seeds. Failures and
different counts of unscored objective wrapper requests remain reported.

---

## Experimental mutation-benefit AOS (branch `research/feasibility-credit-aos`)

**Do not interpret this as a dissertation-ready method.** The original
`GA()` behavior is unchanged; AOS is opt-in:

```python
from gadapt.ga import GA
ga = GA(cost_function=my_cost,
        mutation_operator_policy="ucb",
        mutation_operator_credit="objective")
# Add variables as usual, then ga.execute().
```

For physical feasibility credit, set `mutation_operator_credit="feasibility"`
and provide `mutation_violation_function=lambda values, penalized_cost: ...`.
This callback must return a finite nonnegative *normalized* violation (zero
if physically feasible), or `None` when an objective request did not receive
an actual physical evaluation because the hard budget expired. For rigorous
budget accounting, the callback should only read an evaluation cache; any
new simulations inside it must be separately counted. This API is research-only
and does not replace domain verification, nor provide a general hard-constraint
solver.

Replicate on the actual package:

```bash
python -m pip install -e . 'scipy>=1.11,<1.16' 'pypower>=5.1,<6' 'networkx>=3.2,<4'
python -m unittest discover -s tests -v
python research/aos_ieee14_pilot.py --runs 8 --budget 240 --output aos_ieee14_pilot.csv
python research/analyze_aos_ieee14.py aos_ieee14_pilot.csv
python -m research.aos_geant_temporal --runs 8 --budget 240 --output aos_geant_temporal.csv
python -m research.analyze_aos_geant_temporal aos_geant_temporal.csv
python research/plot_aos.py --kind ieee14 --csv aos_ieee14_pilot.csv --prefix aos_ieee14_figure
python research/plot_aos.py --kind geant --csv aos_geant_temporal.csv --prefix aos_geant_figure
```

- [AOS protocol: scientific prior art and frozen chronological timestamps](AOS_ITERATION_PROTOCOL.md)
- [AOS iteration report: numeric evidence, failures, limitations](AOS_ITERATION_REPORT.md)
- [Original dissertation protocol](DISSERTATION_PROTOCOL.md)

The IEEE14 case is a public AC reference model; GÉANT is archival
anonymized/scaled data with an assumed module planning model, not live
infrastructure. Archive SHA, software dependencies, true evaluations, extra
calls, failures and selection telemetry are captured in GitHub Actions.

---

# Research: robust cost-diversity baseline

This branch contains a deliberately **opt-in** change to GAdapt:

```python
from gadapt.ga import GA

ga = GA(cost_function=my_cost_function, cost_diversity_metric="affine_invariant")
```

The default remains `log_relative`. The new `affine_invariant` metric:

* calculates the half-range of **finite** population costs;
* compares it to the initial generation's half-range and clamps to [0,1];
* is invariant to addition of a constant and multiplication by a positive
  constant, modulo floating-point representability;
* returns 0 when all costs are identical; if the initial spread is zero,
  it recovers to 1 when nonzero diversity subsequently appears;
* raises a `ValueError` for nonfinite costs in the diversity calculation.

**Limitation:** Invariance of a metric is not a proof of better optimizer
accuracy. The range is sensitive to outliers; a zero initial range loses
relative magnitude information. Whether this is an improvement for any
class of objective functions must be measured in full GAdapt runs.

## Reproduce

Run tests from the repository root:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run exploratory seeded benchmarks on the full package:

```bash
python research/benchmark_affine.py --runs 30 --generations 150 --output affine_results.csv
```

For a defensible dissertation, the next experiments must compare the
unchanged baseline, the opt-in metric, and independent optimizers under
controlled objective-evaluation budgets across multiple dimensions,
replicates, transformations, noise levels and constraint scenarios.
Statistical inference must use paired seeds and multiplicity corrections.
Do not compare results of differently scaled cost values without undoing
the affine transform. Use engineering cases with independently verified
feasibility before making infrastructure or industrial claims.

## Repositories / provenance

Based on owlCoder/gadapt fork of bpzoran/gadapt at
`8825da180377cb231d4751c08108a8149269ffc1` (2026-10-17).
The upstream repository is not modified by this research branch.
