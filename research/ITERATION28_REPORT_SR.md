# Iteracija 28 — 12 novih semena NIJE POTVRDILA prethodnu naznaku prednosti scenario-aware UCB GAdapt-a

**Datum:** 21.10.2026. **Repo:** `owlCoder/gadapt:main`. **Status:** I28 U CELINI ZAVRŠEN, 48/48 realnih GAdapt run-ova, **8.640 stvarnih originalnih IEEE118 AC NR PF poziva u PRE-REGISTROVANOJ ANALITIČKOJ SERIJI**, nula numeričkih AC failure. Uspešan prvi kompletan [GitHub Actions #39666171453](https://github.com/owlCoder/gadapt/actions/runs/39666171453). Zbog izmene isključivo fluktuirajućih testnih asercija, GitHub Actions je automatski izvršio i **drugu fizičku CI replikaciju #39666251610** sa još **8.640 stvarnih originalnih AC**; oba skupa 48 run-ova dala su **bitno identične sirove numeričke ishode/physical fitness/opportunity operator selections** (razlikuje se samo runtime). Dakle, **ukupno 17.280 stvarno izvršenih I28 AC PF poziva u dva CI izvršavanja**, ali statistička/primarna analiza uključuje SAMO **jednu** unapred registrovanu seriju od 8.640 AC sa **12 jedinstvenih semena**. NIKAD ne brojati drugi CI kao još 12 nezavisnih seeds ili asimptotski veći dokaz.

**Glavni zaključak: NOVI I26 SCENARIO-AWARE UCB CREDIT NEMA PONOVLJIVU PREDNOST U I28.** Ovaj negativni nalaz pobija raniju, isuviše slabu I27 nadu iz jednog dobijenog kandidata; nije dokaz da je novi operator uopšte bezvredan na svim problemima, nego da **njegova empirijska superiornost NIJE pokazana** na ovom unapred fiksiranom istom IEEE118 zadatku.

## 1. Pre-registrovani originalni zadatak, bez tuniranja posle I27

[I28 protokol](ITERATION28_PROTOCOL.md) commit `c5dfc0e5c86a47f30322ab5a07ad3613dc0917cb` sačuvan pre I28 stvarnih AC. Nijedna promjena core `gadapt/ga.py`, UCB policy, `scenario_feasibility` reward, originalni `research/iteration27_real_scenario_credit_benchmark.py` solver, fitness, box i source režimi između I27 i I28. Samo su testirane postojeće metode na novim RNG semенima.

- Originalni javni `PYPOWER case118()`, originalni izvorni 118 bus / 54 aktivna gen / 186 branch; originalni individualni source PG/PMIN/PMAX i QG/QMIN/QMAX, bus VMIN/VMAX svih 118, source-positive RATE_A oba terminala, complex AC KCL svih sabirnica. Q nije forsiran `ENFORCE_Q_LIMS=0`, ali se originalna individualna Q izvodljivost obavezno proverava naknadno.
- **Tri veštačka javna source load režima:** originalni PD/QD za sve bus pomnoženi sa **0.98, 1.00, 1.02**; isti kontrolni VG primenjen u sva tri. Svaka fitness evaluacija je **3 STVARNA PYPOWER runpf** i 0 dodatnih besplatnih simulacija.
- **Isti već kalibrisan IEEE118 6D originalni PV upravljački prostor** za sve metode: BUS103/32/34/92/19/74, prvih 5 `center±0.005 p.u.` iz prethodnih I19–I24 dijagnostika i BUS74 `[0.948,0.968]` iz I25 Q stres nalaza. Ovo JE informisan isti problem, **NIJE nezavisni mrežni scenario holdout niti industrijski test**.
- **Tačno 12 NOVIH prethodno netestiranih semena 2040–2051**, isto seme za svaku od 4 metode, ne mešati sa I27 exploratory seeds 2026–2028. Population 12, maksimum i ostvareno **180 pravih AC = 60 trostruko fizički validiranih fitness** po metodi i semenu. **48 pravih run-ova × 180 = 8.640 AC**, izbrojano direktno na solver granici (u prvoj seriji). Nije korišćen ni jedan `runopf`.
- Četiri stvarne core GAdapt metode: `gadapt_legacy` (originalni), `gadapt_ucb_objective` (već postojeći), `gadapt_ucb_scalar_feasibility` (već postojeći worst scenario Q/P/V/rated normalizovani violation), i naš I26 `gadapt_ucb_scenario_feasibility`. Sve koriste identičan `cost_function` i source physics; poslednje tri razlikuju samo operator reward signal.

## 2. Rezultati PO METODI — sva 12 nova semena, ne cherry-pick

| Stvarna GAdapt varijanta | Semena sa ≥1 izvodljivim za SVA 3 režima (od 12) | All-three feasible kompletnih 3-AC kandidata (od 720) | Realnih AC | Najbolji source all-three-feasible mean economic cost |
|---|---:|---:|---:|---:|
| **Originalni legacy GAdapt** | **8/12 (66,7%)** | **73** | **2160** | 131.311,282048 |
| Postojeći UCB objective reward | **6/12 (50,0%)** | **65** | 2160 | 131.311,385721 |
| Postojeći UCB scalar-worst source-feasibility | **6/12 (50,0%)** | **70** | 2160 | 131.311,338609 |
| **NOVI UCB scenario-feasibility** | **6/12 (50,0%)** | **70** | 2160 | **131.311,052008** |

**Dokaz nije da je originalni GAdapt statistički dokazano bolji**: samo 12 RNG seedova na **istoj** jednoj ranije kalibrisanoj originalnoj mrežnoj fizici. Deskriptivni 95% *marginalni Wilson* interval za legacy 8/12 je približno **[39,1%, 86,2%]**, a za svaki od UCB modova 6/12 **[25,4%, 74,6%]**. Ovi intervali predstavljaju grubu nesigurnost success-rate svake pojedinačne metode, **NISU validni nezavisni upareni intervali razlike** i nemaju objavljenu `p` vrednost.

**Novi mode je imao najniži pojedinačni poznati mean feasible cost 131311.052008**, ali **to je jedan minimum iz selektovanih 12 pokretanja**, ne superiorna prosečna metoda. Na istom pitanju legacy ima više uspešnih seedova, dok novi nema veću frequency izvodljivih uzoraka od scalar UCB (oba 70/720 trostrukih kandidata). Na 100%-load single-scenario fizikalnim ocenama legacy 164, novi 157 u ukupnih 720 batch-eva; na 98%-load legacy 77, novi 75; na 102%-load legacy 198, novi 181. Ne prikazivati zbir single-load uspeha kao zajedničku robust izvodljivost.

## 3. Najvažniji U PARENIM semеnima dokaz

Za isto seme, `new_mode / legacy`:
- **oba pronalaze all-three feasible** na **6/12** seedova;
- **nijedan** na **4/12**;
- **legacy DA, new NE** na **2/12**;
- **new DA, legacy NE** na **0/12**.

Za **oba** kontrolna UCB moda, `objective` i `scalar_feasibility`, **svih 12 binarnih success/failure ishoda bili su IDENTIČNI novom scenario-UCB modu** (6 oba uspešna, 6 oba ne): **0 seedova** u kojima je naš novi operator imao jedinstven novi uspeh. To je mnogo stroži kriterijum za falsifikaciju tvrdnje da nova signalna komponenta povećava stopu uspešnih run-ova.

Nova varijanta ima **70** uspešnih stvarnih kompletnih source 3-scenario kandidata naspram **70** kod već postojećeg scalar source-feasibility moda; broj nije nezavisnih 70 RNG eksperimenata, jer ih više potiče iz istih evolutivnih putanja unutar 12 seedova. Na pojedinačnim semenima novi može imati više ili manje complete-feasible kandidata, ali ukupni signali **nisu sistematski bolji**.

**Bitna dodatna indikacija confounding-a:** na semenu **2040** čak i legacy, objective UCB i scalar UCB i novi scenario-UCB svi nalaze prvi robust-feasible **već na stvarnom AC pozivu #24** (osmi trostruki fitness kandidat), tj. unutar početne population=12 evaluacije. **Nijedan mutacioni operator kredit nije mogao uzrokovati taj prvi uspeh.** Zato pozitivni slučajevi (posebno rani) ne dokazuju dodatnu algoritamsku vrednost mutation credit-a.

## 4. Replikacija, testna greška i pošteno brojanje fizike

- Prvi workflow [#39665768668](https://github.com/owlCoder/gadapt/actions/runs/39665768668) zaustavio se na Python unittest **pre ijednog AC**: jedna Wilson asercija zahtevala je egzaktno 0 umesto floating point ~2.8e-17, druga postojeća kratka stohastička GA integracija je nerazumno zahtevala makar jednu mutaciju pre isteka budžeta. **Ispravke su bile SAMO u testovima**: tolerancija na aritmetičko zaokruživanje i uklanjanje neispravne pretpostavke da mutacija mora da se desi u kratkom testu. **Nijedna nova source fizička mrežna evaluacija niti promena algoritma/scenario reward/box/budžeta nije nastala pre prvog uspešnog workflowa.**
- Pošto GitHub automatski pokreće workload na više commitova koji menjaju test ili workflow, [prva uspešna analitička I28 serija CI #39666171453](https://github.com/owlCoder/gadapt/actions/runs/39666171453) izvršila je **8640 realnih AC**, a [druga redundantna uspešna proverа #39666251610](https://github.com/owlCoder/gadapt/actions/runs/39666251610) još **8640 realnih AC**. Reanalizom sve **48 istovetnih metoda-seed parova** oba raw loga dobijeni su **identični kompletni brojevi AC, AC-feasible success, cost, prva izvodljivost, po-scenarijska fizika, kazne, UCB selections/observations i izvorni PV vektori**. Razlika je samo vreme izvršavanja. **Nije reč o drugoj, nezavisnoj 12-seed replikaciji.**
- Prva zeleni CI serija je **unapred određena kao zvanična primarna**, svi podaci bez filtriranja u [raw JSON](results/ieee118_iteration28_12_newseed_4_GAdapt_credit_8640_real_AC_20261021.json) i [raw CSV](results/ieee118_iteration28_12_newseed_4_GAdapt_credit_8640_real_AC_20261021.csv). Drugi workflow ostavljen kao javni log tehničke reproduktivnosti, ne kao dodatni statistički dokaz. Dakle, postoji **17.280 fizičkih AC poziva ukupno u I28 GitHub CI istoriji**, dok prikazana inferencijalna/statistička serija koristi **8640**, ne izmišljeni 17.280 nezavisnih AC slučajeva.

## 5. Naučna implikacija — šta da promenimo u nastavku

**I27 pozitivni pilot (1/3 novi UCB, 0/3 ostali) bio je prerano mali da bi podržao bilo kakvu tvrdnju efikasnosti. I28 sa 12 novih uparenih seeds ne podržava superiornost novog reward-a i na primarnom uspehu više ide u korist legacy GA (8/12 vs 6/12), bez statističke potvrde razlike.** Zato nastavak **NE SME** biti još 10 iteracija dotjerivanja heurističkih nagradnih težina na istom IEEE118 slučaju i onda proglašenje publikabilnosti. Nova opcija ostaje funkcionalni, potpuno opt-in **negativno testirani istraživački prototip** u fork-u.

[Preliminarni pregled literature i matrica preklapanja](ITERATION28_LITERATURE_NOVELTY_AUDIT_SR.md) dodatno otkriva **vrlo slične prethodne radove**: već 2008. AOS+MAB, 2024. DRL operator selection sa feasibility stanjem, 2026. DRL-AEOSF adaptivno ograničena evolucija; opšti scenario-aware reward u GAdapt-u **nije odbranjivo originalan samo zato što se pojavio kao novo ime u našem kodu**.

Predlog za mentora: predstaviti I27 kao HIPOTEZU, I28 kao negativnu, unapred registrovanu proveru; zatim **pre bilo kakvog novog optimizator-reward tuninga** posebno formulisati stvarno novu, falsifikabilnu ideju, mogućno **evaluaciono-budžetski adaptivno scenario sampling** ili **fizički uparen pre/post mutation credit** sa punom real AC cenom, uz literaturnu proveru. Tek zatim potpuno unapred registrovani drugi izvorni slučajevi (IEEE14/IEEE118 drugačije source PD/QD prostorne promene i nezavisni telecom/infrastructure), minimum više novih RNG semena i fer strong Powell/DE/SLSQP reference. Ako to ne daje gain, pošten naučni zaključak je da ova vrsta operator-credit signala ne dodaje praktičnu vrednost.

**Nema tvrdnje originalnog doktoratskog doprinosa niti industrijskog deployment-a.** Više rada sada znači bolje definisanu negativnu naučnu evidenciju, a ne dokazan poboljšani GAdapt.

## Linkovi

- [I28 unapred zamrznuti protokol](ITERATION28_PROTOCOL.md)
- [I28 neizmenjeni evaluator + novi seed replication harness](iteration28_newseed_scenario_credit_replication.py)
- [I28 unit testovi pairinga i real-AC budžeta (0 AC)](test_iteration28_newseed_replication.py)
- [Raw JSON — 48 complete GA runova, 8640 fizikalnih AC](results/ieee118_iteration28_12_newseed_4_GAdapt_credit_8640_real_AC_20261021.json)
- [Raw CSV — svi kandidati po GA-run zbirnim source metrikama](results/ieee118_iteration28_12_newseed_4_GAdapt_credit_8640_real_AC_20261021.csv)
- [Zvanični prvi zeleni full-real-AC CI #39666171453](https://github.com/owlCoder/gadapt/actions/runs/39666171453)
- [Identičan dodatni fizički CI #39666251610](https://github.com/owlCoder/gadapt/actions/runs/39666251610)
- [I27 originalni single-seed pilot i njegove stroge fizičke provere](ITERATION27_REPORT_SR.md)
- [Matrica literature i neproverene originalnosti](ITERATION28_LITERATURE_NOVELTY_AUDIT_SR.md)

**Jedna rečenica za izveštaj:** „Unapred registrovana replikacija na 12 novih uparenih semena (po 180 stvarnih AC PF po run-u) nije pokazala poboljšanje robusne izvodljivosti novog scenario-aware UCB GAdapt mutation-credit mehanizma u odnosu na legacy i postojeće UCB kontrolne varijante; zbog toga preliminarni rezultat jednog uspešnog I27 semena ne predstavlja potvrđen algoritamski doprinos.“
