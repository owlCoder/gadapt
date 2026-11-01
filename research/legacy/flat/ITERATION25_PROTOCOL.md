# Iteracija 25 — držanje prethodno izvodljivih IEEE118 PV odluka pri novom opterećenju ±2%

**Pre-registracija 21.10.2026, pre ijednog NOVOG AC poziva I25.** Isključivo `owlCoder/gadapt:main`; upstream `bpzoran/gadapt` netaknut. Ovo je namerno mali **out-of-sample scenario fizičke ROBUSNOSTI pet ZAMRZNUTIH prethodno izvodljivih kontrolnih odluka**, NE optimizacija, NE ponovno treniranje, NE dokaz generalizacije GAdapt-a. Nijedna metoda ne dobija nove parametre posle evaluacije.

## Istorijski fiksirani kandidati i pravilo selekcije

Izvorno kalibrisani petodimenzionalni IEEE118 generator VG BUS103, BUS32, BUS34, BUS92, BUS19; originalni generator PG svih 54 fiksni osim fizičkog slack output BUS69. Za fiksne kontrolne kandidate uzeti:
1. Jedinstveni **I23 α=0.8** source-feasible vektor, koristeći samo prethodno arhivirani originalni source JSON `research/results/ieee118_iteration23_qbracket_4_real_ac_20261021.json` (prethodno objavljena izvodljiva ekonomska cena 131198.7975746236).
2. Tačno **četiri** izvorno fizički izvodljiva source najbolja vektora, po jedan za metod `gadapt_legacy, scipy_de, random_search, bounded_powell`, sa tri istorijska semena 2026/2027/2028, iz I24 već arhiviranog `research/results/ieee118_iteration24_legacy_gadapt_de_random_powell_20261021.json`. Selekcija je unapred definisana: **najniži originalno fizički izvodljivi economic cost po metodi**, tie break najmanje seme. Preflight mora potvrditi izvorno `real_ac_pf_calls=96`, `feasible_real_ac_candidates>0`, kompletan source fizički status u I24 JSON, originalni redosled kandidatskih PV BUS [103,32,34,92,19], 1152 broj stvarnih istorijskih AC i petizlazni izvorni vektor. Nema novog poziva za originalni 100%-load baseline — arhiva je već plaćena.

Nijedna od tih pet tačaka nije izabrana nakon stres merenja. Ne tvrditi da su nepobedivi najviši nivoi robusnosti; biramo sve četiri najbolje prethodno verifikovane metode i I23 fizičku referencu radi transparentnog audit-a.

## DVA testa pomerenog opterećenja, ukupno tačno deset stvarnih AC poziva

Neizmenjena originalna javna `pypower.case118()` mreža kao **osnova** (118 bus, 54 aktivnih gen, 186 branch, svih originalnih P/Q limits, VMIN/VMAX, RATE_A>0 terminala i originalnih `gencost`, GS/BS/tap/topologija). Za `load_factor ∈ [0.98,1.02]` skalirati **samo** aktivnu i reaktivnu sabirničku potrošnju `PD` i `QD` svih 118 bus za **isti** faktor. **Nijedan generator setpoint VG ili originalni PG nije tokom scenarija adaptiran**; slack PG/QG ostaje AC fizički izračunat i sve individualne source fizičke granice se moraju proveriti. Ovi `±2%` su NAMERNO VEŠTAČKI izmenjeni javni testni scenariji i **nisu originalni case118** ni stvarni industrijski podaci. Cene ostaju originalne polynomial gencost.

Tačan redosled pravih fizičkih poziva: najpre **0.98** opterećenje, kandidati: I23 α=0.8; GAdapt I24 best; DE I24 best; random I24 best; Powell I24 best. Zatim isti redosled za **1.02** opterećenje. **Tačno 10 ulaza u `pypower.runpf`**, PF_ALG=1, PF_DC=0, PF_TOL=1e-8, PF_MAX_IT=40, ENFORCE_Q_LIMS=0, VERBOSE=0, OUT_ALL=0, PYPOWER 5.1.19. Realni AC brojač pre ulaska u solver i na exception; na numeričkom neuspehu svi fizički metrički rezultati null. Nema dodatnih izmišljenih top-up AC ili pretrage za uspeh.

Za svaki fizički konvergiran stressed case, proveriti identičnim kodom kao I18–I24: individualne PG/QG granice **svih 54**, VMIN/VMAX svih 118 bus, originalne positive RATE_A MVA oba kraja, kompleksni AC KCL, originalna generatorska troškovna polinomna cena samo kao `feasible_economic_cost` ako SVA source ograničenja zadovoljavaju (inače su fizičke veličine numerički dijagnostičke, ne OPF optimum). `RATE_A=0` znači nedostajuću granicu, ne prisilni overload. Pragovi V=1e-5 pu, PG/QG=1e-3 MW/MVAr, rated MVA=1e-3 MVA, KCL=1e-3 MVA. Beležiti konkretne Q/P/V/thermal offending source BUS / generator IDs, plus konvergenciju i nul rezultat gde nije feasible.

**Glavni izlaz:** tabela izvodljivosti po 2 scenarija i 5 kandidata, sa stvarnim br. AC i komponentama povreda. Ne tvrditi statističku metodu na samo jednom plus i jednom minus stres scenariju. Naročito ne tvrditi da je ovo fer stohastičko poređenje GAdapt/DE/random/Powell na novoj potrošnji: nijedna metoda nije ponovo trenirana, a I24 kandidati su prethodno **izabrani na istim izvornim 100%-load podacima**.

## Zašto ovo naučno pomaže

Kada se `PD/QD` promene, originalni izvodljivi setpointi mogu izgubiti izvodljivost. To motiviše **scenario-aware constraint feasibility repair** i potonji test robustnog adaptivnog GAdapt-a, ali **pre nego što se izmisli novi operator**, treba proveriti literaturu o AC-OPF robust optimization, sensitivity-guided repair, feasibility-first evolutionary selection i adaptive operator selection. Ovaj mali scenario test nije nova naučna mehanika, nema statističke superiornosti ili dokaza da je sistem fizički moguć pod svakim stresom.

Pinovi: Python3.12, PYPOWER5.1.19, SciPy1.13.1, pandas2.2.3, pandapower2.14.11, single-thread BLAS/OMP. Posle pravog CI snimiti kod, unit testove, 10 raw JSON/CSV stanja i srpski izveštaj na main. **Ne raditi 11. AC bez novog protokola.**
