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
