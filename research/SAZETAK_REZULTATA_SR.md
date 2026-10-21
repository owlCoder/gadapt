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
