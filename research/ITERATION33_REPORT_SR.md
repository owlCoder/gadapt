# Iteracija 33 — novi domen GÉANT, 8.580 STVARNO izvršenih routing/modularnih evaluacija (22.10.2026)

**Status: kompletno završena i audirana preregistrirana serija.** Koraci 1–5: [source/model audit](ITERATION33_GEANT_MODEL_AUDIT_SR.md), [pre-registered protocol](ITERATION33_PROTOCOL.md), [implementacija](iteration33_geant_routing_budget.py) i [zero-real-routing testovi](test_iteration33_geant_routing_budget.py), [originalni uspešni Actions eksperiment](https://github.com/owlCoder/gadapt/actions/runs/39689108919), [svi sirovi podaci + Holm](results/geant_iteration33_12seeds_6arms_8580_true_routings_20261022.json), [precizan naučni prior art i naredna hipoteza](ITERATION33_PRIOR_ART_AND_NEXT_HYPOTHESIS_SR.md).

## Fizička/metodološka istinitost pre rezultata

Ovo **NIJE** elektroenergetski AC/OPF test. Upotrebljena je originalna javna SNDlib **GÉANT** mreža, 22 čvora, 36 linkova, 462 usmerena zahteva, izvorni `geant.txt` potvrđen originalnim `SHA256 ff316c23220ff4485deafcb8701d49c353db0c80072152df3ed4b4f4ff`. Svaki `TRUE_ROUTE` je stvarna **NetworkX Dijkstra ruting + 462 nesplit zahteva + račun broja izvornih SNDlib kapacitetnih modula i njihovih izvornim cenama**, ne fizička AC simulacija, ne stvarni operatorov paketni eksperiment. Originalni GAdapt optimizer i I29 sequential evaluator NISU izmenjeni.

- `nominal`: originalna javna matrica; `odd_source_heavy` i `even_source_heavy` su **NOVI VEŠTAČKI** profili odlaznih zahteva 1,08/0,92 puta po paritetu leksikografskog indeksa izvornog čvora. **Nisu** nove originalno merene/nezavisne vremenske matrice.
- **VIŠE NE POSTOJI originalna fizička mrežna feasibility granica u osnovnom GÉANT modelu** jer su moduli neograničeno kupivi. Test uvodi **NAŠ HIPOTETIČKI budžet 145.000 SNDlib planskih cenovnih jedinica PO SCENARIJU**, fiksiran i komitovan pre ikakvih I33 evaluacija. Zato je `verified_feasible` u izveštaju uvek **isključivo izvodljivost po hipotetičkom finansijskom uslovu** i ne sme se nazivati izvorno fizički-feasible planom. Niti je 145.000 originalna cena instalacije operatera.
- Isti vektor 36 celobrojnih routing weights 1–25 odlučuje sve tri scene. Modulna kupovina se **posebno obračunava za svaku scenu**; objektiv je prosta srednja vrednost njihove 3 scene-specific modulne nabavke (**recourse model**). To NIJE trošak jednog trajnog robust postavljenog kapacitetnog plana koji pokriva maksimum po linku.
- Svaka pozitivna tro-scenarijska izvodljivost stvarno je proverena u **SVA 3** ruting evaluatora; nepokrenuti scenariji nisu smatrani uspešnim ili neuspešnim. Neuspešni NR/route exception bio bi status unknown, ne matematički budget fail. U ovom eksperimentu **0 numeričkih unknown**. Preflight testovi jesu sintetički i NISU uključeni u 8.580 realnih poziva.

## Glavna tabela — 12 uparenih NOVIH seedova 2200–2211, 120 stvarnih ruta po metodi/seedu

| I33 metod, ORIGINALNI GAdapt ili DE | Seedova sa ≥1 **stvarno u sva 3 scenarija verified cap-feasible** planom (12) | Broj stvarno trostruko verified kandidata* | Realno izvršenih routing evaluacija | Najniži potpuno verified mean modulni scenario cost |
|---|---:|---:|---:|---:|
| Originalni GAdapt **full_true** | **3/12** | 4 | **1.440** | 140.481 |
| GAdapt **full_censored** (svi scenariji stvarno plaćeni; isti selekcioni fitness kao fixed) | **2/12** | 2 | **1.440** | 141.665 |
| **GAdapt stop_fixed** (first measured cap failure) | **10/12** | **54** | **1.423** | **137.497** |
| **GAdapt stop_adaptive** (empirijski failure-rate redosled) | **11/12** | **59** | **1.421** | **137.497** |
| SciPy DE **full_true** | **5/12** | 5 | **1.440** | 140.484,666667 |
| SciPy DE **stop_fixed** | **6/12** | 10 | **1.416** | 140.275,666667 |

*Brojevi kandidata 54/59 nisu broj nezavisnih statističkih ponavljanja; zavisne su jedinke iste algoritamske putanje. **Inferencijalna statistika koristi n=12 nezavisnih seed-runova po metodi.** Njihovi `best_verified_robust_mean_economic_cost` služe samo kao zaista izmerene mean source-price vrednosti potpuno 3-scenario hypothetical-cap-feasible ruta. To nisu source-OPF troškovi, niti garantovani globalni optimumi.

**Pri skoro jednakom stvarnom budžetu (1.440 prema 1.423), GAdapt `stop_fixed` je izvršio 1.224 objektivna zahteva prema 600 kod `full_censored`, od kojih su neki postbudget zahtevi vratili sentinel bez novog rutinga.** Potpuno plaćenih kandidata u `full_censored` bilo je 480, a u `stop_fixed` 54 (svi izvodljivi), dok je dodatnih **1.107** kandidata GAdapt `stop_fixed` rano odbio zbog stvarno izmerene hipotetičke budžetske povrede; za njih je tačno **2.060** ruta ostalo **neizvršeno**. `stop_adaptive`: 1.118 dokazanih screen odbijanja, 2.110 **neizvršenih** preostalih scena. DE fixed: 1.350 odbijanja, 2.664 neizvršenih scena. **Sve su to različite putanje i ne predstavljaju stvarno uparen per-genome speed-up merenje.**

Zbir: **72 optimizaciona pokretanja**, `1440+1440+1423+1421+1440+1416=8580` pravih Dijkstra/module-price poziva od unapred dozvoljenih **8.640**, tj. 60 planiranih rezervisanih poziva nije izvedeno. **Nula pravih elektroenergetskih AC poziva**, nula simuliranih duplih rezultata i 0 route exceptions.

## Primarna paired seed statistika — egzaktna dvostrana + unapred fiksiran Holm za 5 poređenja

| Prva : druga metoda | Obe uspešne | Samo prva | Samo druga | Nijedna | Exact p (uncorrected) | **Holm p (5)** |
|---|---:|---:|---:|---:|---:|---:|
| GA `full_true` : GA `full_censored` | 1 | 2 | 1 | 8 | 1,000000 | 1,000000 |
| **GA `full_censored` : GA `stop_fixed`** | **2** | **0** | **8** | **2** | **0,0078125** | **0,0390625** |
| GA `stop_fixed` : GA `stop_adaptive` | 10 | 0 | 1 | 1 | 1,000000 | 1,000000 |
| GA `stop_fixed` : DE `stop_fixed` | 4 | 6 | 2 | 0 | 0,2890625 | 1,000000 |
| GA `full_true` : DE `full_true` | 3 | 0 | 2 | 7 | 0,500000 | 1,000000 |

**Važan pozitivan, ali usko ograničen nalaz:** pri identičnoj *cenzurisanoj* oceni i uporedivo plaćenom budžetu, GAdapt `stop_fixed` je imao **10/12** uspešnih semena, dok **puna fizički plaćena cenzurisana kontrola samo 2/12**. To su 8 unapred parenih diskordantnih semena, nijedno u obrnutom smeru; egzaktni 2-sided p=0,0078125, **Holm adjusted p=0,0390625**. Statistički jeste značajno na 0,05 **unutar OVOG, umetnutog hipotetičkog investicionog cap-a i unapred zamrznutog eksperimenta**, NE dokazuje uzrok samo po sebi jer evolutivne trajektorije imaju različite brojeve kandidata, NE dokazuje originalnost first-fail ideje, realnu telekom mrežu, kvalitet rute pod QoS/ECMP ili jednak efekat na IEEE mrežama.

Samo menjati scoring `full_true` → `full_censored` **nije dalo uspešniji GA** (3/12 naspram 2/12). Adaptivni redosled `stop_adaptive` je ovde imao 11/12 naspram 10/12 fixed, ali jedino jedno seme je različito, p=1 i nijedna dodatna naučna prednost adaptivnog redosleda nije dokazana.

**Izvorni ekonomski kvalitet:** Najbolji found mean modular cost 137.497 jednak je za GA fixed i GA adaptive, ali iz različitih ili delom istih optimizacionih putanja. Medijane *samo među seme-uspesima* su 140.997,333333 za fixed GA i 139.681,333333 za adaptive. **Ne koristiti medijane uslovljene uspehom kao generalnu dominantnost**, jer su neuspešna semena izbačena. DE nije dominirao, ali dokaz njegove inferentne inferiornosti pod 5 unapred definisanih kontrasta NE postoji.

## Reproduktivni trag

- **[Originalni potpuno zeleni GitHub Actions #39689108919](https://github.com/owlCoder/gadapt/actions/runs/39689108919)**: `preflight-no-routing` i `measured-sndlib-geant` oba uspešni. Originalni fizički domen job **119530765246**, jedno analitičko izvršavanje 72 runova (ne 12 novih ako tehnički rerun).
- Originalni neizmenjeni GitHub Actions [ZIP artifacts 12386884323](https://github.com/owlCoder/gadapt/actions/runs/39689108919/artifacts/12386884323), ZIP SHA256 `726de0d72a2b1404b23c462c1d7e92dd02ea72ebc36a4584ebf309866fc81187`, CI source SHA256 napred naveden.
- [Sva 72 realna JSON reda + individualne fizikalno računovodstvene metrike](results/geant_iteration33_12seeds_6arms_8580_true_routings_20261022.json); [kompletni union-schema CSV](results/geant_iteration33_12seeds_6arms_8580_true_routings_20261022.csv), oba rekonstruisana direktno iz `I33_TRUE_ROUTE` pojedinačnih originalnih stdout redova **bez nove routing evaluacije**; audit je proverio unique seed/method ključeve, zbir svih 3-scenario slotova i individualnih realnih poziva, 0 unknown, svaku fully-paid kontrolu i tačan primarni Holm test.
- [I33 originalno pre-registrirani zahtevi pre solvera](ITERATION33_PROTOCOL.md), [tehnički audit problematične izvornosti cap-a](ITERATION33_GEANT_MODEL_AUDIT_SR.md) i [granica naučne originalnosti i preporuka](ITERATION33_PRIOR_ART_AND_NEXT_HYPOTHESIS_SR.md).

## Šta ovo znači za doktorat — pozitivno, ali ne proizvoditi naučnu novinu

I31 na IEEE118 (7/12 `full_censored` prema 11/12 `stop_fixed`, p=0,125) i I32 na IEEE14 (9/12 prema 12/12, p=0,25) pokazuju **isti smer ali nisu pojedinačno statistički značajni**; I33 na drugoj domeni daje **2/12 prema 10/12**, corrected p=0,0391. To je **obrazac koji zaslužuje sledeću rigoroznu naučnu studiju**, ali nije dokaz sveopšte primenljivosti: sva tri sistema koriste samo javne ranije poznate modele, veštački definisane scenarije, a I33 je plus namerno izmislio investicioni cap. IEEE pravih AC je potpuno druga kategorija evaluacije od GÉANT networkx routing procene. Ne sabirati njihove pozive kao „AC“.

**Dokazano kao inženjerski nalaz**: pod tačno deklarisanim uslovima i budžetima GAdapt first-failure screening sa cenzurisanim fitnesom pronalazi verificirane kapom ograničene diskretne rute u više uparenih seedova nego potpuno plaćena kontrola sa identičnim selekcionim fitnesom; to je poznata vrsta metode, ne samostalno nov doktorski algoritam.

**Sledeći odbranjiv doktoratski rad**, uz mentorovo odobrenje: izučiti i predregistrirati *censor-aware cost-normalized credit for mutation operators* koji ne tretira unknown/missing source scenarije kao nulu i ne podstiče algoritam da namerno pravi jeftino propale jedinke; porediti sa prethodnim I26 UCB credit (negativnim na I28), GA/DE, statičkim screeningom, scenario racing prior art i domenski snažnom lokalnom bazom. Potom **zaista slepi izvori** (druga javna mreža u svakom domenu ili nezavisni vremenski period) i dovoljno novih uparenih seedova. NIKADA ne tvrditi algoritamsku naučnu originalnost bez bibliografske provere i adekvatne nezavisne validacije.
