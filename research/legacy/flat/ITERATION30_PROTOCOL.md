# Iteracija 30 — prostorni IEEE118 load scenario HOLDOUT za sekvencijalni AC evaluator (NIJE nova mreža)

**Pre-registracija 21.10.2026 pre svih NOVIH I30 AC solver poziva.** Samo `owlCoder/gadapt:main`, upstream `bpzoran/gadapt` netaknut. I29 pokazao poznati *early physical rejection* efikasnije nalazi source-feasible vektore uz isti stvarni AC limit, ali adaptivni redosled nije pomogao jer je uniforme 98% load gotovo uvek bio najteži. I30 isključivo proverava reproduktivnost TEHNIČKOG EVALUATORA na prethodno NETESTIRANIM prostorno raznolikim PD/QD scenarijima. **Ne tvrditi nezavisnu topologiju, industrijske field podatke, naučnu originalnost ili statističku superiornost iz 4 seeds.**

## Zamrznuta fizika, 3 potpuno nova unapred izabrana source stress režima

Originalni javni `pypower.case118()`, 118 originalnih buses / 54 online generatora / 186 branch; svi generator PG (osim stvarnog output slack BUS69), PMIN/PMAX, QMIN/QMAX, source bus VMIN/VMAX, positive `RATE_A` MVA oba kraja, complex AC nodal KCL, taps/shunts/topologija, source originalni gencost nepromenjeni. **Šest originalnih generator VG BUS103/32/34/92/19/74** i lokalni originalnim izvorima validan calibrated 6D box identičan I27–I29, isti za SVE metode. **Nema nove kontrole niti prilagođavanja mrežnim test rezultatima.**

Potpuno fiksni nova 3 load scenarija — skalirati **samo originalni PD i QD svake sabirnice**:
1. `nominal`: bus PD/QD `*1.00` (source case118).
2. `odd_bus_heavier`: za bus sa neparnim ORIGINALNIM `BUS_I` PD/QD `*1.02`, parni `*0.98`.
3. `even_bus_heavier`: za bus sa parnim ORIGINALNIM `BUS_I` PD/QD `*1.02`, neparni `*0.98`.

To NIJE globalni uniformni 98/100/102 load eksperiment I27–I29, nije nezavisna mreža, niti se oba scenarija tretiraju kao probabilistički reprezentativna stvarna neizvesnost. Ukupni PD/QD kroz originalnu mrežu neće biti tačno isti ako neparne/parne sabirnice nose različitu potrošnju; ta razlika se NE normalizuje posle rezultata. Koristi se isključivo izvorni bus `BUS_I` atribut; nijedan load/shunt/tap/PG osim PD/QD se ne menja. Sve tri scenario PF mora fizički naplatiti `pypower.runpf` iz jednog originalnog numeričkog solvera i proveriti originalne source P/Q/V/thermal/KCL granice.

## Pet evaluacionih metoda, bez dodatne prakse tuning-a

Evaluacioni `SequentialScenarioBudgetCost` iz I29 ostaje **NEIZMENJEN**: `full` (zaista tri PF i `mean real cost + 1e5*sum real violations`), `stop_fixed` (prekinuti samo nakon numerički konvergentno DOKAZANE originalne fizičke neizvodljivosti), `stop_adaptive` (redosled odabira zasnovan samo na STVARNO izmerenim ranijim fail frekvencijama po scenariju, smoothed `(fail+1)/(attempts+2)`, unobserved nisu izmereni). Cenzurisano `1e9+1e5*observed violation` NIKADA nije full source cost. Numerički neuspešan `runpf` može biti `unknown`, nikada dokaz fizičke neizvodljivosti. Ako 0<remaining physical calls<3, novi kandidat NE sme započeti i ne izmišljaju se source prijave.

Unapred fiksno **5 metoda**: `gadapt_full`, `gadapt_stop_fixed`, `gadapt_stop_adaptive`, `scipy_de_full`, `scipy_de_stop_fixed`. GA legacy default (ne novi reward), isti 6D box, pop12 i isti I29 GA options, DE SciPy polish false/popsize5. **Četiri nova seeds 2070,2071,2072,2073**, 20 run-ova po najviše 180 STVARNIH AC PF, ukupno najviše **3600** novih fizikalnih PF. Brojač pre svakog konkretnog `runpf`; svaki kandidat 1–3 realna AC u slučaju ranog dokazanog neuspeha, ali **3 realna AC obavezna za bilo koji report source all-three feasible i njegovu srednju ekonomsku cenu**. Ako se ne nađe nijedan tri-scenario feasible, originalna mreža se ne proglašava matematički neizvodljivom; samo ovaj limited PG-fixed originalni VG search nije uspeo u budžetu.

Glavni pokazatelji: po metodi broj runova sa stvarno all-3 feasible, broj full verified feasible, number screened with *partial known physical infeasibility*, real AC, actual AC by scenario, unobserved scenario count, number objective requests (nije isto AC); najbolji mean stvarne originalne ekonomske cene samo ako sva tri plaćena, first feasible real AC, test da je originalni load source `BUS_I` paritet tačno primenjen. Dodatno uporedni pokazatelj adaptive-vs-fixed izbor drugog scenarija, ali NE izmišljati dobitak. Nema p-hacking-a, nema novih seedova nakon rezultata ili drugog box-a.

## Fiksne reproduktivne procedure

Python3.12, pypower5.1.19, scipy1.13.1, pandas2.2.3, pandapower2.14.11, single-thread BLAS. **Pre bilo kakvog novog pravog AC**: nulti AC unit/protocol test originalnih BUS_I pariteta, identičnih originalnih gen V i PG vektora, scenario callback brojača, isti sintetički source source diagnostic; testovi ne pozivaju pravi `runpf`. Nakon toga real GitHub Actions sa čuvanjem 20 raw JSON/CSV i izveštaj na srpskom bez izostavljanja negativnih rezultata. Sva prividna originalnost ranog screeninga osporena prior art u [I29 auditu](ITERATION29_PRIOR_ART_SR.md).

**I30 ne dokazuje novu GAdapt teoriju; namenjen je odvojnoj proveri da li benefit od ranog sim-budget screeninga preživljava drugačiju prostornu raspodelu opterećenja.**
