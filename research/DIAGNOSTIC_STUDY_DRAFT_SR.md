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
- **Multimodalni valve-point dispečing sa sertifikovanim optimumima (I48):** razlika prema IPOP-CMA-ES se smanjuje na
  faktor 1,3–1,5, ali IPOP ostaje značajno bolji na 2/3 instance. GAdapt je bolji od SciPy DE na 2/3.

## 1. Uvod i pitanja
- **P1.** Da li je GAdapt konkurentan jakim kontrolama pri jednakom broju stvarnih evaluacija?
- **P2.** Ako nije, koja komponenta ili svojstvo to uzrokuje?
- **P3.** Da li postoje artefakti merenja koji su ranije izveštavani kao rezultat pretrage?
- **P4.** Da li GAdapt-ova raznovrsnost donosi prednost na multimodalnim problemima? *(I48: ne, ali razlika je mala)*

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

## 7. Diskusija
- Zašto raznovrsnost bez intenzifikacije gubi na skoro linearnim i glatkim pejzažima (Droste, Jansen, Wegener 2002;
  Witt 2013; Hansen i sar. 2011).
- Šta je primenljivo van GAdapt-a: protokol jednakog budžeta sa udžbeničkim kontrolama i provera skrivenih evaluacija
  u bibliotekama metaheuristika.

## 8. Ograde
- Cena kod izbora ruta je sintetička, nad stvarnim topologijama.
- AC dispečing ima fiksne napone (neizvodljivost na manjim slučajevima).
- Rezultati važe za proučene budžete.
- I39 podaci su izgubljeni.

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
