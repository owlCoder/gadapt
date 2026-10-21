# Iteracija 34 — stvarni GAdapt sa *censor-safe per-true-call mutation credit*: 7.126 originalnih GÉANT rutiranja

**ZAVRŠENO 22. oktobra 2026** — [pre-registracija pre ijednog novog I34 rutiranja](ITERATION34_PROTOCOL.md), [izveštaj core izmene](ITERATION34_IMPLEMENTATION_REPORT_SR.md), originalni [uspešni GitHub Actions CI #39691941881](https://github.com/owlCoder/gadapt/actions/runs/39691941881). **60 od 60 stvarnih uparenih runova**, 12 NOVIH semena **2300–2311**, pet varijanti pravog `gadapt.ga.GA`, 7.126 stvarnih GÉANT networkx Dijkstra + source SNDlib module-price evaluacija od max7.200, **0 pravih elektroenergetskih AC**, nula numerički unknown. Svi originalni `I34_TRUE_ROUTE` redovi su audirani, bez numeričkog dopunjavanja neizmerenih scenarija.

## Fizička/industrijska granica — ne sme se preskočiti

To NIJE nova nezavisna infrastrukturna mreža niti industrijski test. I34 ponavlja istu istorijski javnu GÉANT mrežu **22 čvora, 36 linkova, 462 zahteva** i iste I33 **sintetičke** tražnje (nominal, odd_source_heavy, even_source_heavy, ×1,08 / ×0,92). Izvorni geant.txt SHA256 `ff316c23220ff4485deafcb8701d49c353db0c80072152df3ed9023ed4b4f4ff`. **NOV/NEIZVORNI hipotetički investicioni limit 145.000 source-model cenovnih jedinica PO SCENARIJU** već je izabran u prethodnom I33 eksperimentu i nije ponovo kalibrisan. Osnovni izvorni module network može da kupi neograničen broj modula; **ovde je „verified feasible” strogo samo zadovoljenje našeg veštačkog price cap-a u sva 3 stvarno izmerena scenarija**, ne operaterov izvorni fizički/QoS/availability kapacitetni limit. `mean module cost` je tri odvojene recourse kupovine, NE jedan jedinstveni trajni mrežni plan. Nijedan elektroenergetski AC proračun nije izvršen.

## Šta je novo u SOFTWARE kodu

Dodali smo opt-in `mutation_operator_credit="censored_verified_per_cost"` direktno u originalni GAdapt core, kao stvarni `uniform/ucb` selector, bez menjanja podrazumevanog ponašanja. Svaka mutaciona ocena dobija samo već stvarno plaćen `1..3` poslednji scenario observation event preko callbacka koji **NE POKREĆE NOVI ROUTING**. Strogi counter delta, individualne izmerene scenarije, finite source/cap violation i callback/counter konzistentnost proverava sam core. Potpuna trostruko potvrđena izvodljivost dobija reward `1/3`; stvarno izmerena delimična ili potpuna budžetska neizvodljivost **0**, numerički unknown ili nedostatak poziva **bez nagrade**. Ovo uklanja jedno jasno pogrešno signalisanje (jeftin fail != operator uspeh), ali poznate ideje feasibility reward, cost-aware credit, AOS/UCB i cenzurisano multi-scenario merenje znače da **naučna originalnost ovoga NIJE dokazana**. Videti [precizan I34 implementacioni opis](ITERATION34_IMPLEMENTATION_REPORT_SR.md).

**Preflight proces:** prvobitni [CI #39691771826](https://github.com/owlCoder/gadapt/actions/runs/39691771826) je pao **pre prvog stvarnog I34 solver poziva** zbog čiste Python sintakse u izveštajnom `dict` polju. Skript ispravljen bez promene I34 protokola i ponovljen na [CI #39691941881](https://github.com/owlCoder/gadapt/actions/runs/39691941881). Novi i stari GA regression tests svi uspešni, zatim 60/60 pravi GÉANT run-ovi uspešni. Ne prikazivati prvobitni CI kao uspešan, ali niti dodavati lažne realne evaluacije njegovoj preflight fazi.

## Glavni rezultati (za svako seme najviše 120 STVARNIH GÉANT rutina)

| Pravi GAdapt metod | Semena sa bar jednim dokazano trostruko hipotetički cap-feasible kandidatom (od 12) | Trostruko realno izmerenih cap-feasible kandidata* | Realno izvršenih domain routing poziva | Najniži u metodi potpuno verificirani mean source module cost |
|---|---:|---:|---:|---:|
| `legacy_fixed` — originalni GA + I29 fixed first-failure screening | **11/12** | 62 | 1.423 | **136.143** |
| `ucb_objective_fixed` — stari UCB, heuristic censored-score objective feedback | **9/12** | 57 | 1.422 | 136.143 |
| `uniform_censor_safe_fixed` — NOVI feedback, ali uniformno birani operatori | **11/12** | 58 | 1.421 | 136.143 |
| **`ucb_censor_safe_fixed` — NOVI GAdapt opt-in UCB, strict verified-per-call credit** | **12/12** | **60** | **1.420** | **136.143** |
| `ucb_scenario_full` — stari I26 scenario-feasibility UCB, ali MORA platiti sva 3 scenarija | **3/12** | 3 | 1.440 | 139.593 |

*Brojevi pronađenih evolutivnih kandidata su zavisni unutar 12 runova, **nisu** 60 nezavisnih ponavljanja. Prazni `best_cost` u neuspešnim semеnima ostaju **null**. GA `result.success` nije dokaz fizičke ili hipotetičke investicione izvodljivosti. Neizvršene scene cenzurisanih jedinki ostaju unobserved, ne „feasible”. Najbolja zaista potvrđena mean cena **136.143** je ista za SVE četiri fixed-screening GA metode, dakle novi policy **nije ostvario niži najbolji ekonomski cost od legacy**. Medijana troška **samo uspešnih semena** novog moda je **141.729,5**, a legacy **140.931,666667**, tako da ne postoje ni elementarni dokazi o boljem tipičnom srednjem trošku; različite stope neuspeha onemogućavaju bezuslovan zaključak iz ovih conditional medijana.

**Opaženi core mutation-credit** ukupno kroz 12 semena:

| Metod | Izabrani operatori | Stvarno obrađeni feedback događaji (per-mutated variable) | Pozitivno nagrađeni događaji |
|---|---:|---:|---:|
| Originalni GA legacy | N/A | N/A | N/A |
| UCB objective | 1.376 | 1.331 | 180 |
| Uniform novi feedback | 1.055 | 986 | 32 |
| **UCB novi feedback** | **1.182** | **1.124** | **55** |
| UCB I26 scenario full | 329 | 75 | 75 |

Broj pozitivno nagrađenih mutacija **ne mora** biti jednak broju robustly feasible kandidata (neki su nastali bez mutacije, više mutacija po kandidatu, kao i postojeći GA selekcioni/elitistički put). Ovo NIJE kauzalni efekat operatora. Promena broja operator izbora zavisi i od generacijske evolutivne putanje pod fizičkim budžetom.

## Sva pet primarna/sekundarna paired poređenja — PRE-rеgistrovana 12-seed Holм porodica

| Prvi : drugi metod | Obe seed uspešne | Samo prvi | Samo drugi | Nijedan | Exact two-sided p | **Holm(5) p** |
|---|---:|---:|---:|---:|---:|---:|
| **Novi UCB : originalni legacy** (PRIMARY) | **11** | **1** | **0** | **0** | **1,000000** | **1,000000** |
| Novi UCB : stari objective-UCB fixed | 9 | 3 | 0 | 0 | 0,250000 | 1,000000 |
| Novi UCB : novi uniform policy | 11 | 1 | 0 | 0 | 1,000000 | 1,000000 |
| Novi UCB fixed : **stari I26 UCB `full` sa sva 3 poziva** | 3 | 9 | 0 | 0 | **0,00390625** | **0,01953125** |
| Stari objective-UCB fixed : legacy fixed | 9 | 0 | 2 | 1 | 0,500000 | 1,000000 |

**NAJVAŽNIJI ISKREN REZULTAT:** na *primarnom* uparenom poređenju novog UCB-a sa originalnim GAdapt-om koji ima isti I29 `stop_fixed` model i iste 12 seedova, uspesi su **12/12 prema 11/12**, samo JEDAN diskordantan par: **exact p=1 i Holm p=1**. **NIJE statistički dokazana prednost novih operator kredit signala nad već poznatom metodom**, takođe nema poboljšanja najboljeg stvarnog module-cost rezultata.

Jedino značajno `p=0,0195` poređenje je novi `UCB stop_fixed` prema **I26 UCB full** koji TROŠI sve tri ruting evaluacije i drugačije rangira potpuno vrednovane kandidate. Ovo menja BROJ obrađenih kandidata i FITNESS, uz operator reward. **Nije izolovan kauzalni uticaj nove operator-credit ideje**. Dodatno, taj I26 režim prethodno nije razvijen kao optimalna poredbena politika za GÉANT hipotetički cap model.

Smerovi tri projekta: I31 originalni IEEE118, I32 originalni IEEE14, I33 GÉANT prenose sugestivan benefit **starog, jednostavnog** screening-a naspram punog ocenjivanja, ali **I34 NIJE potvrdio da dodatna AOS operator kredit adaptacija povećava uspešnost nad legacy fixed**. Ovo je istinski negativan/neutralan naučni nalaz i ne treba ga maskirati.

## Data / protokol / CI

- [I34 originalni protokol](ITERATION34_PROTOCOL.md) komitovan pre svih domen evaluacija i pre novih core izmena.
- [I34 in-core modifikacija](ITERATION34_IMPLEMENTATION_REPORT_SR.md), [core zero-solver regressions](../tests/test_censored_verified_per_cost_credit.py), [zero-domain adapter tests](test_iteration34_censor_credit_geant.py), [60-run live-domain benchmark](iteration34_censor_credit_geant.py).
- [Sva 60 individualna realna routing JSON izvoda](results/geant_iteration34_12seeds_5arms_7126_actual_routing_20261022.json) i [CSV](results/geant_iteration34_12seeds_5arms_7126_actual_routing_20261022.csv) iz neizmenjenih `I34_TRUE_ROUTE` log redova, ukupno 7.126 realnih poziva, 0 AC.
- [Originalni uspešni CI #39691941881](https://github.com/owlCoder/gadapt/actions/runs/39691941881) i [originalni ZIP artifact id12389156362](https://github.com/owlCoder/gadapt/actions/runs/39691941881/artifacts/12389156362), digest SHA256 `b9fe52ff686f49849de09c0e78f5469cda1878ea79fc5c0023c8c53684a31acd`.
- [Prvi neuspešan CI #39691771826](https://github.com/owlCoder/gadapt/actions/runs/39691771826) pre stvarnih domen solvera: sintaksna greška ispravljena i sačuvana, bez novih semena, score tuning-a ili dodatnih fizičkih proba.

## Posledica za doktorat

**Ovaj posao jeste konkretna nova izvedena softverska sposobnost pravog GAdapt-a**: dokazivo bezbednija obrada nepotpunih fizičkih evaluacija i realnog budžeta bez naučne tvrdnje o originalnom algoritmu. U trenutnom eksperimentu n=12 ne izdvojeno pokazuje originalnu naučnu superiornost AOS-a. Prosto nazvati `verified_per_cost` „novim doprinosom doktoratu” pre pregledа cost-sensitive AOS i scenario-racing literature bilo bi metodološki neprihvatljivo.

**Sledeći racionalni korak:** ne tuning na istom GÉANT kao pozitivnom referentnom domenu. Prebaciti problem ili hipotezu na **drugu source topologiju / slepo realno industrijsko mrežno opterećenje**, uporediti sa već postojećim constraint-aware UCB/bandit i feasibility-first strategijama; opredeliti se da li disertacija treba da dokazuje originalno novo upravljanje cenzurisanim troškom operatora ili da razvija generalni metod verifikacije i upravljanja fizičkim budžetom evolutivnih algoritama. Do tada **NO CLAIM naučne originalnosti ili realnog operativnog kvaliteta**.
