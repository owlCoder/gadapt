# Dijagnostika samoadaptivnog genetskog algoritma na infrastrukturnim optimizacionim problemima: jednaki budžeti, skrivene evaluacije, invarijantnost i deficit intenzifikacije

*Nacrt poglavlja / rada — 23. oktobar 2026. Svi eksperimenti su preregistrovani pre koda i izvršeni jednom; kod, ulazi
(sa SHA-256) i sirovi izlazi su u `owlCoder/gadapt` (`research/`).*

## Sažetak (nacrt)
Ispitujemo GAdapt, samoadaptivni genetski algoritam sa mehanizmima zasnovanim na raznovrsnosti (raznovrsnost
troškova, roditelja i kolona promenljivih), na infrastrukturnim problemima: binarnom izboru ruta u modularnom
dimenzionisanju mreža (26 SNDlib topologija) i kontinualnom AC ekonomskom dispečingu (MATPOWER 14–118 sabirnica).
Poredimo ga sa jakim kontrolama pri **jednakom broju stvarnih evaluacija**.

Rezultati:
- **Binarni izbor ruta:** (1+1)-EA je značajno bolji od GAdapt-a na 14 od 18 topologija, a fiksni udžbenički GA na
  5 od 6. Nijedna pojedinačna GAdapt opcija ne objašnjava razliku.
- **Kontinualni dispečing:** CMA-ES je pri istom budžetu 3–5 redova veličine bliži najboljem rešenju.
- **Uzrok:** mehanizmi raznovrsnosti sprečavaju intenzifikaciju oko najboljeg rešenja.
- **Dva metodološka problema u merenju:** validacija biblioteke troši dve skrivene evaluacije, koje u vrednovanju
  izgledaju kao rezultat pretrage. Mera kolonske raznovrsnosti nije invarijantna na jedinice promenljivih.
- **Doprinos je metodološki i empirijski:** protokol jednakog budžeta sa udžbeničkim kontrolama i računovodstvom
  skrivenih evaluacija, kao i opt-in ispravke biblioteke, uz podrazumevano ponašanje bit-identično.
- **Revizija integriteta (I49, I50):** u 21 Python biblioteci, problemi integriteta koji nisu ugaoni pozivi javljaju
  se u 8/21 (CI 18–62%), a protivrečnost dokumentaciji u 4/21. Alat je otkrio dve nove greške (SMAC, GFO), koje su
  prijavljene održavaocima.
- **Multimodalni valve-point dispečing sa sertifikovanim optimumima (I48):** razlika prema IPOP-CMA-ES se smanjuje na
  faktor 1,3–1,5, ali IPOP ostaje značajno bolji na 2/3 instance. GAdapt je bolji od SciPy DE na 2/3.

## 1. Uvod i pitanja
- **P1.** Da li je GAdapt konkurentan jakim kontrolama pri jednakom broju stvarnih evaluacija?
- **P2.** Ako nije, koja komponenta ili svojstvo to uzrokuje?
- **P3.** Da li postoje artefakti merenja koji su ranije izveštavani kao rezultat pretrage?
- **P4.** Da li GAdapt-ova raznovrsnost donosi prednost na multimodalnim problemima? *(I48: ne, ali razlika je mala)*
- **P5.** Koliko su česti problemi integriteta evaluacija u Python bibliotekama za black-box optimizaciju? *(I49, I50)*

## 2. Metodologija (zajednička)
- **Preregistracija:** protokol, instance, semena, budžet i kriterijumi odluke komitovani su pre koda.
  Dodaci protokolu dozvoljeni su samo pre pokretanja i dokumentuju se (I43-A1, I44-A1).
- **Jednak budžet:** svaka metoda dobija tačno B stvarnih evaluacija. Validacioni pozivi GAdapt-a su isključeni
  i provereni (I44 i dalje).
- **Statistika:** uparena semena, dvostrani Wilcoxon, Holm po porodici, unapred definisani pragovi broja instanci.
- **Nezavisne instance:** svaka nova hipoteza testira se na instancama koje ranije nisu viđene (I44, I45). Razvojni
  skup je eksplicitno označen (I46).
- **Bit-identičnost:** svaka izmena biblioteke se proverava hešom celog niza poziva funkcije troška pre i posle izmene.

## 3. Binarni izbor ruta (I42–I46)
| Iteracija | Pitanje | Ishod |
|---|---|---|
| I42 | Strukturna dekompozicija (partition crossover)? | NO-GO: medijana komponenti ≤ 2 na 23/25 topologija |
| I43 | Budžet ili operatori? | UNRESOLVED (3/6 deficit, 0/6 budžet); otkriven validacioni artefakt |
| I44 | Intenzitet mutacije? | Opovrgnuto (0/6); deficit repliciran na novim instancama bez artefakta (5/6) |
| I45 | Specifično za GAdapt ili generički? | Specifično: udžbenički GA bolji na 5/6, (1+1)-EA bolji od GAdapt-a na 6/6 |
| I46 | Koja komponenta? | Nijedna pojedinačna; ni kombinacija; eksplorativno: nema intenzifikacije |

## 4. Kontinualni dispečing (I5, I47)
- **I5 (raniji rad):** IEEE14 naponi; CMA-ES, SLSQP i DE bolji od GAdapt-a 12/12.
- **I47:**
  - linearna mera kolonske raznovrsnosti je tačno invarijantna na jedinice;
  - na AC dispečingu ne donosi značajno poboljšanje (0/5);
  - CMA-ES je 3–5 redova veličine bolji od GAdapt-a.

## 5. Artefakti merenja i ispravke biblioteke
1. **Skrivene evaluacije validatora** (`probe_cost_function`). Uticaj na I39 je najverovatnije reinterpretacija, jer
   izvorni podaci nisu dostupni.
2. **Ignorisana gornja granica broja mutiranih promenljivih** (`strict_mutation_decision_variable_limit`).
3. **Neinvarijantna mera raznovrsnosti** (`columnar_diversity_metric="linear"`).

## 6. Multimodalni dispečing (I48)
Stvarni javni sistemi sa sertifikovanim globalnim optimumima (Pedroso, Kubo, Viana): eld13@1800, eld13@2520 i
eld40@10500; B = 50.000; 25 semena ([izveštaj](ITERATION48_REPORT_SR.md)).

| Instanca | GAdapt | IPOP-CMA-ES | SciPy DE |
|---|---|---|---|
| eld13 @ 1800 | 7,3e-3 | **5,5e-3** | 1,9e-2 |
| eld13 @ 2520 | 4,2e-3 | 6,5e-3 | **5,0e-5** |
| eld40 @ 10500 | 6,1e-3 | **4,0e-3** | 3,7e-2 |

Vrednosti su medijane relativnog jaza. Ishod je DEFICIT_GADAPT (2/3). Odnos jaza prema IPOP-CMA-ES pada sa 10³–10⁵
(glatki dispečing, I47) na 1,3–1,5 (multimodalni dispečing). Raznovrsnost pomaže upravo tamo gde je pejzaž
multimodalan, ali ne nadoknađuje nedostatak intenzifikacije.

## 7. Revizija integriteta evaluacija u Python bibliotekama (H4, I49, I50)

### 7.1 Motivacija
Artefakt iz §5 (probni pozivi validatora koji izgledaju kao rezultat pretrage) postavlja opštije pitanje. Koliko
često biblioteke za black-box optimizaciju evaluiraju, broje ili prijavljuju drugačije nego što korisnik pretpostavlja?
Kod skupe funkcije troška, kakav je AC proračun, svaka skrivena ili ponovljena evaluacija troši budžet. Svaki
neusklađen rezultat menja zaključak poređenja.

### 7.2 Prior art i uska tvrdnja ([H4 audit](H4_PRIOR_ART_AUDIT_SR.md))
**Nije novo:**
- brojanje evaluacija (COCO, IOHexperimenter);
- testovi invarijantnosti i pristrasnosti ka centru (Kůdela 2022, BIAS);
- poređenje okvira po kvalitetu rešenja (Ravber i sar. 2025, 13 okvira).

**Novo** je biblioteka-nezavisan black-box alat koji:
- klasifikuje svaki poziv funkcije troška;
- proverava doslednost prijavljenog rezultata sa zabeleženim pozivima;
- proverava dokumentovane relacije (budžet, seme), uključujući reproduktivnost **između procesa**.

Uz alat ide validacija podmetnutim greškama i merenje rasprostranjenosti na dva uzorka.

### 7.3 Alat i validacija
Omotač beleži svaki poziv (x, f, faza). Klase su zadate pre merenja:

| Klasa | Šta meri |
|---|---|
| C1 | x je vektor svih donjih ili svih gornjih granica (namenjeno probnim pozivima) |
| C2 | bitski ponovljena evaluacija (prijavljuje se kao udeo rasipanja) |
| C3 | evaluacija van kutije |
| C4 | više evaluacija od dokumentovanog maksimuma |
| C5 | evaluacije posle povratka optimizatora |
| R1, R2, R3 | prijavljeno x\* nije evaluirano; prijavljeno f\* ≠ zabeleženo f(x\*); prijavljeno nije najbolje evaluirano |
| D2 | prijavljeni broj evaluacija ≠ stvarni |
| D3, D3x | isto seme daje drugačiji niz poziva u istom procesu (D3) ili u svežim procesima (D3x, uveden u I50) |

**Validacija pre svakog merenja:**
- referentna nasumična pretraga sa po jednom podmetnutom greškom daje tačno tu klasu (5/5);
- čista referenca ne daje nijednu klasu;
- GAdapt daje C1 samo sa uključenim probnim pozivima;
- za D3x, mutant sa semenom iz `hash()` daje samo D3x, a mutant sa semenom iz sata daje D3 i D3x (I50: 11/11 provera).

### 7.4 Uzorci
- **I49:** 9 popularnih biblioteka izabranih po kriterijumu protokola (pymoo, DEAP, PyGAD, geneticalgorithm, Nevergrad,
  Optuna, PySwarms, cma, SciPy DE). Budžet 1000, sfera, Rastrigin i plato, N ∈ {2, 10}, 5 semena.
- **I50:** novi uzorak izabran **spoljnim pravilom**: snimak GitHub repozitorijuma (Python, ≥ 300 zvezdica, 12 tema)
  i Python okviri iz Ravber i sar. 2025. Od 62 kandidata, unapred zadati kriterijumi prihvatljivosti ostavili su
  **12**: baybe, bayes_opt, bofire, cmaes, emukit, EvoloPy, evotorch, evox, GFO, NiaPy, scikit-opt, SMAC. Budžet 200,
  isti problemi. Konfiguracije i citati dokumentacije zamrznuti su pre pokretanja
  ([prihvatljivost](ITERATION50_ELIGIBILITY.md)).

### 7.5 Rezultati

| Ishod | I49 | I50 | Zajedno |
|---|---|---|---|
| Bar jedan nalaz (preregistrovano, sve klase) | 4/9 (14–79%) | 11/12 (62–100%) | 15/21 (48–89%) |
| Bar jedan nalaz bez C1 (post hoc, vidi 7.7) | 4/9 | 4/12 (10–65%) | **8/21 (18–62%)** |
| Nalaz koji protivreči dokumentaciji | 2/9 | 2/12 (2–48%) | **4/21 (5–42%)** |

U zagradama su Clopper–Pearson 95% intervali.
- **Rasipanje na duplikate** (medijana udela evaluacija): geneticalgorithm 41,5%, scikit-opt DE 47%, DEAP 11,5%. Kod
  skupe funkcije troška to je skoro pola budžeta.
- **Reproduktivnost:** D3 (isti proces) nije našao nijednu novu biblioteku u I50. D3x (između procesa) našao je SMAC.

### 7.6 Pojedinačni nalazi i prijave održavaocima

| Biblioteka | Nalaz | Uzrok | Status |
|---|---|---|---|
| DEAP | evaluacije van granica | granice su na korisniku (dizajn) | poznato (Ravber i sar. 2025) |
| PyGAD | 21 evaluacija posle završetka | `best_solution()` ponovo računa fitnes | dokumentovano ([#160](https://github.com/ahmedfgad/GeneticAlgorithmPython/issues/160)) |
| cma | do 1011 evaluacija za `maxfevals` 1000 | provera po iteraciji | poznato ([pycma #195](https://github.com/CMA-ES/pycma/issues/195)) |
| Nevergrad | nereproduktivno uz seme; `NGOpt` je pogođen | pycma bez semena; unutrašnji optimizator metamodela bez semena | poznato ([#1572](https://github.com/facebookresearch/nevergrad/issues/1572)); **uzrok i zakrpa su naši** |
| SMAC | rezultat zavisi od `PYTHONHASHSEED` | `list(set(Configuration))` u lokalnoj pretrazi | **novo**, prijavljeno ([#1380](https://github.com/automl/SMAC3/issues/1380)), zakrpa od jedne linije |
| GFO | `best_score` negiran uz `optimum="minimum"` | negacija se ne poništava pri izveštavanju | **novo**, prijavljeno ([#106](https://github.com/gfo-project/Gradient-Free-Optimizers/issues/106)) |
| scikit-opt DE | prijavljeno lošije od najboljeg evaluiranog (1/30) | najbolje se bira samo iz probnih vektora | povezano ([#187](https://github.com/guofei9987/scikit-opt/issues/187), samo naslov); nije prijavljeno (pravilo §6) |
| evotorch | evaluacije van kutije | SNES ne podržava granice | dizajn |

Svaka nova dijagnoza ima minimalan primer:
- Nevergrad i GFO su pokrenuti i na glavnoj grani;
- za SMAC je provereno da je kod na `main` nepromenjen u odnosu na 2.4.1;
- zakrpe za Nevergrad i SMAC su uzročno proverene (reproduktivnost se vraća);
- za GFO je predložena ispravka, ali nije testirana.

### 7.7 Pretnje validnosti
- **C1 nije specifičan.** Kod BO i PSO algoritama tačka u uglu nastaje sečenjem na granici, namernom inicijalizacijom
  u uglovima (GFO `vertices`) ili zato što je ugao područje optimuma (plato). I50 je zato bez C1 analiziran post hoc.
  U I49 nijedna biblioteka nije imala samo C1. Sledeća verzija alata treba da ograniči C1 na pozive izvan pretrage.
- **Okvir uzorka:** GitHub teme i prag zvezdica nisu potpuni. Zato je dodat spoljni izvor B. Prihvatljivost je
  primenjena strogo: gaft je ispao zbog pada na konstantnoj funkciji.
- **Podrazumevana podešavanja i mali budžeti** (200 ili 1000) ne pokrivaju sve načine upotrebe.
- **Neprimenljive provere:** R1–R3 ne važe za ask/tell biblioteke bez prijavljenog rezultata. C4 važi samo tamo gde je
  dokumentovan maksimum.
- **Svi pojedinačni nalazi I49 bili su već poznati.** Doprinos I49 je automatsko pronalaženje i mera
  rasprostranjenosti, a ne nove greške.

### 7.8 Preporuka za praksu
Pre poređenja optimizatora na skupoj funkciji troška:
1. obmotati funkciju troška brojačem koji beleži svaki poziv;
2. proveriti da je prijavljeno rešenje evaluirano i da prijavljena vrednost odgovara zabeleženoj;
3. proveriti broj evaluacija prema budžetu, uključujući pozive pre i posle pretrage;
4. proveriti reproduktivnost sa istim semenom u **dva sveža procesa**;
5. izmeriti udeo ponovljenih evaluacija.

## 8. Diskusija
- Zašto raznovrsnost bez intenzifikacije gubi na skoro linearnim i glatkim pejzažima (Droste, Jansen, Wegener 2002;
  Witt 2013; Hansen i sar. 2011).
- Šta je primenljivo van GAdapt-a: protokol jednakog budžeta sa udžbeničkim kontrolama i provera skrivenih evaluacija
  u bibliotekama metaheuristika.
- Revizija integriteta je primenljiva na bilo koju biblioteku bez čitanja koda. Nove greške je našla baš provera
  koja se retko radi: reproduktivnost između procesa i znak prijavljene vrednosti.

## 9. Ograde
- Cena kod izbora ruta je sintetička, nad stvarnim topologijama.
- AC dispečing ima fiksne napone (neizvodljivost na manjim slučajevima).
- Rezultati važe za proučene budžete.
- I39 podaci su izgubljeni.
- Revizija integriteta: vidi §7.7.

## Reference (svi DOI provereni na Crossref-u)
- Droste, Jansen, Wegener 2002, [10.1016/S0304-3975(01)00182-7](https://doi.org/10.1016/S0304-3975(01)00182-7)
- Witt 2013, [10.1017/S0963548312000600](https://doi.org/10.1017/S0963548312000600)
- Doerr, Le, Makhmara, Nguyen 2017, [10.1145/3071178.3071301](https://doi.org/10.1145/3071178.3071301)
- Hansen, Ros, Mauny, Schoenauer, Auger 2011, [10.1016/j.asoc.2011.03.001](https://doi.org/10.1016/j.asoc.2011.03.001)
- Grahl, Bosman, Rothlauf 2006, [10.1145/1143997.1144071](https://doi.org/10.1145/1143997.1144071)
- Chicano, Whitley, Ochoa, Tinós 2024, arXiv:2407.06742
- Tinós, Whitley, Chicano 2015, [10.1145/2725494.2725497](https://doi.org/10.1145/2725494.2725497)
- Przewoźniczek i sar. 2025, [10.1145/3712256.3726410](https://doi.org/10.1145/3712256.3726410)
- Krasnogor, Smith 2005, [10.1109/TEVC.2005.850260](https://doi.org/10.1109/TEVC.2005.850260)
- Jurkiewicz 2023 (TopoHub), [10.1016/j.softx.2023.101540](https://doi.org/10.1016/j.softx.2023.101540)
- Pedroso, Kubo, Viana 2014, arXiv:1404.4944
- Li, Zhang, Lu 2019, [10.1109/ACCESS.2019.2927574](https://doi.org/10.1109/ACCESS.2019.2927574)
- Ravber, Šmid, Moravec, Mernik, Črepinšek 2025, [10.15388/25-INFOR603](https://doi.org/10.15388/25-INFOR603)
- Hansen i sar. 2020 (COCO), [10.1080/10556788.2020.1808977](https://doi.org/10.1080/10556788.2020.1808977)
- de Nobel i sar. 2024 (IOHexperimenter), [10.1162/evco_a_00342](https://doi.org/10.1162/evco_a_00342)
- Kůdela 2022, [10.1038/s42256-022-00579-0](https://doi.org/10.1038/s42256-022-00579-0)
- Vermetten i sar. 2022 (BIAS), [10.1109/TEVC.2022.3189848](https://doi.org/10.1109/TEVC.2022.3189848)
