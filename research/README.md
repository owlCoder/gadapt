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
