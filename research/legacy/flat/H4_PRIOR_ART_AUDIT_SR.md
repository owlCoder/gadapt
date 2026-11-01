# H4 — prior-art audit: automatska revizija integriteta evaluacija u optimizacionim bibliotekama

**23. oktobar 2026.** Pretragu je uradio `literature-auditor` agent, a dopunske provere sam uradio lično:
- svih 8 ključnih DOI-ja potvrđeno na Crossref-u;
- metodski deo Ravber i sar. 2025 pročitan u punom tekstu;
- pretraženi issue trackeri 9 ciljnih biblioteka.

Kontekst: korisnik je izabrao opciju 1 (studija I42–I48 kao poglavlje teze; mentor cilja promenu prakse u industriji).

## 1. Odluka: **GO, uski metodološki doprinos** (nije nova optimizaciona metoda)

| Deo H4 | Status | Najbliži prior art (DOI proveren) |
|---|---|---|
| (b) invarijantnost / pristrasnost ka centru | **Nije novo** | Kůdela 2022, [10.1038/s42256-022-00579-0](https://doi.org/10.1038/s42256-022-00579-0) i arXiv:2301.01984 (test pomeraja na 90 metoda iz mealpy-ja); BIAS, Vermetten i sar. 2022, [10.1109/TEVC.2022.3189848](https://doi.org/10.1109/TEVC.2022.3189848); Jian, Zhu 2021, [10.1016/j.ins.2021.06.062](https://doi.org/10.1016/j.ins.2021.06.062); Hansen i sar. 2011, [10.1016/j.asoc.2011.03.001](https://doi.org/10.1016/j.asoc.2011.03.001) |
| (d) tačno brojanje evaluacija | **Nije novo** | COCO, Hansen i sar. 2020, [10.1080/10556788.2020.1808977](https://doi.org/10.1080/10556788.2020.1808977); IOHexperimenter, de Nobel i sar. 2024, [10.1162/evco_a_00342](https://doi.org/10.1162/evco_a_00342) |
| (a) klasifikacija svakog poziva (probni pozivi na uglovima granica, duplikati, van granica, preko budžeta) i **doslednost prijavljenog rezultata** | **Delimično novo** | Ravber i sar. 2025, [10.15388/25-INFOR603](https://doi.org/10.15388/25-INFOR603): 13 okvira, kvalitet rešenja i odstupanja koda; konstatuju da mnogi nemaju zaustavljanje po evaluacijama. Nema klasifikacije poziva ni provere doslednosti rezultata. |
| (c) dokumentovani parametri naspram stvarnog ponašanja | **Delimično novo** | Metamorfno testiranje GA: Rounds, Kanewala 2018, arXiv:1808.01033; Duque-Torres i sar. 2025, [10.1016/j.infsof.2025.107807](https://doi.org/10.1016/j.infsof.2025.107807) i [10.1016/j.infsof.2025.107872](https://doi.org/10.1016/j.infsof.2025.107872) |

**Najuža odbranjiva tvrdnja:** automatizovan, biblioteka-nezavisan black-box alat koji:
- klasifikuje svaki poziv funkcije troška;
- proverava doslednost prijavljenog rezultata (da li je prijavljeno x* evaluirano, i da li je prijavljeno f* jednako
  zabeleženom f(x*) i najboljem evaluiranom);
- proverava dokumentovane relacije parametara (budžet, reproduktivnost uz seme).

Uz alat ide **studija rasprostranjenosti** na N popularnih Python biblioteka, sa zaključanim verzijama, i
**validacija alata** podmetnutim greškama.

Ovo je doprinos metodologiji benchmarkinga i softverskom inženjerstvu (moguća mesta objavljivanja: ACM TELO, IST, EMSE).
Za tezu se povezuje sa infrastrukturnim problemima kroz GAdapt nalaz iz I39/I43, gde je probni poziv bio pogrešno
prikazan kao rezultat.

## 2. Već poznati pojedinačni slučajevi (moraju se označiti kao „već prijavljeno“)
- **DEAP #162:** duplikati posle ukrštanja i mutacije se uvek evaluiraju
  ([link](https://github.com/DEAP/deap/issues/162)).
- **pycma #108 i #195:** `maxfevals` ponekad nije poštovan
  ([108](https://github.com/CMA-ES/pycma/issues/108), [195](https://github.com/CMA-ES/pycma/issues/195)).
- **pymoo #564:** RVEA ne dostiže zadati broj evaluacija
  ([link](https://github.com/anyoptimization/pymoo/issues/564)).
- **PyGAD #202 i #255:** broj evaluacija i ponovno računanje fitnesa
  ([202](https://github.com/ahmedfgad/GeneticAlgorithmPython/issues/202),
  [255](https://github.com/ahmedfgad/GeneticAlgorithmPython/issues/255)).
- **humpday #345 i #353:** prekoračenje budžeta pri inicijalizaciji (siva literatura).

## 3. Zahtevi za protokol (iz audita)
- Kriterijum izbora biblioteka i verzije su fiksirani unapred.
- Podrazumevana podešavanja, uz budžet zadat po dokumentaciji.
- Unapred definisane klase poziva i primarni ishod.
- **Validacija alata:** podmetnute greške u referentnom optimizatoru (osetljivost) i čista kontrola (specifičnost).
- GAdapt je pozitivna kontrola sa poznatim probnim pozivima.
- Svaki nalaz se razvrstava na grešku, dizajnersku odluku ili prazninu u dokumentaciji.
- Odgovorno obaveštavanje održavalaca pre objave. Prijava issue-a je spoljna radnja i traži odobrenje korisnika.
