# Iteracija 28 — NEZAVISAN test sa 12 novih uparenih semena: da li scenario-aware UCB u GAdapt-u zaista ponavlja uspeh?

**Unapred registrovano 21. oktobra 2026. pre svih novih I28 AC poziva i pre uvida u I28 rezultate.** Jedino `owlCoder/gadapt:main`; upstream `bpzoran/gadapt` ne dirati. Ova iteracija je NAMERNO test **ponovljivosti algoritamskog efekta na ISTOM prethodno kalibrisanom problemu**, NE validacija novih mrežnih stanja. Algoritamski izvor iz uspešno završene I27 se ZAMRZAVA; NE menjati mutation reward formule, UCB, objective, lokalni kontrolni box, PRNG engine, target load ili penal dok traje I28.

## Motivacija i prethodni, neponavljivi pilot

Prva direktna in-core izmena `mutation_operator_credit='scenario_feasibility'` iz I26 koristi fiksni reward za `N=3` stvarno izmerena originalna AC load režima (0.98,1.00,1.02) i UCB operator selection. I27 je unapred registrovani pilot na tri semena 2026–2028, šest metoda × 3 seed × 180 real native `runpf` = 3.240 AC; rezultat novog GAdapt moda **jedan** fizički trostruko izvodljiv kandidat u **samo jednom semenu**, ostali GAdapt/DE/Powell nula. Zbog malog broja uspeha i prethodno in-sample izabrane relevantne source PV reprezentacije to nije naučna potvrda metode. Zato sada **nema tuning-a, nema pomeranja topologije, nema cherry-picking seedova**, nego direktno reprodukujemo uparenim, novim seed-ovima.

## Precizni izvorni model, 3 stvarno plaćena AC po genomu

**Re-use unmodified** `research/iteration27_real_scenario_credit_benchmark.py` classes/function: originalni `pypower.case118()`, 118 bus/54 online gen/186 branch, source P/Q bounds za svaki gen, bus VMIN/VMAX, positive source RATE_A MVA dva terminala, KCL. **Fiksni izvorni PG (osim fizičkog AC slack izlaza)**, originalna potrošnja PD+QD uniformno skalirana na tri veštačka faktora **[0.98,1.00,1.02]**. Isti 6D source generator VG **BUS103, BUS32, BUS34, BUS92, BUS19, BUS74** i iste lokalne izvorno validne granice `center±.005` prvih pet, `[.948,.968]` BUS74 iz I27. Ove kontrole su prethodno izabrane na osnovu I19–I25, dakle nalaz ostaje *in-sample* i ne znači generalizaciju.

**1 pravac/fitness = 3 stvarna izvorna PYPOWER NR AC PF** uz strogo `runpf` brojanje na solver granici, bez besplatnog ponavljanja starih I27 primarnih tačaka, bez cache-eval izuzetaka ili postbudget nagrade. Ako scenario NR ne konvergira, i taj AC se broji; source `feasible` samo ako svaki od 54 PG/QG, 118 bus V i source positive RATE_A oba kraja + kompleksni KCL ispune I27 pragove *u svakom od tri* režima. Isti penalized score `mean(3 source gencost) + 1e5*sum(3 source normalized violation)` za SVE GA metode. Ni jedna metoda ne dobija drukčije izabran fizički kontrolni resurs niti centar, isti izlazni kriterijumi.

## I28 fiksirana matrica — 8640 stvarnih AC PF maksimalno

**Samo 4 stvarna core GAdapt moda** (bez nepotrebnog novog determinističkog Powell triplikata):
- `gadapt_legacy` (default originalne mutacije);
- `gadapt_ucb_objective` (postojeći UCB sa objective credit);
- `gadapt_ucb_scalar_feasibility` (postojeći UCB sa scalar worst-scenario source violation credit);
- `gadapt_ucb_scenario_feasibility` (novi I26 opt-in full-3-scenario reward).

**12 novih, nikad u I27 testiranih i sada zamrznutih semena 2040,2041,...,2051**, sva četiri metoda ispitana za SVAKO seme u I27 redosledu. **48 run-ova**, za svako 180 stvarnih AC najviše (**60 celih x tri scenarija**), ukupno **8.640 realnih AC gornji limit**. GAdapt pop=12, ne menjati `run_method`, UCB, random seed, objective/scorer, population mutation, exit options. Činjenica da algoritmi koriste istu numeričku vrednost seed-a ne garantuje identične genome/populacije nakon različitih random draw order-a: zovemo to *seed-paired design*, a ne “identični početni genomi”. Trajanje GitHub job max 40 min, Python 3.12, PYPOWER 5.1.19, SciPy 1.13.1, pandas 2.2.3, pandapower 2.14.11, single-thread BLAS.

## Primarni ishod, obavezna negativna kontrola

**Primarno:** za svako od 12 semena i svakog moda indikator `>=1 all-three physical feasible`; broj uspešnih seedova po modu /12 i upareni diskordantni parovi `new-yes/old-no`, `new-no/old-yes` po svakom od 3 kontrola. **Sekundarno:** broj kompletno source-feasible trostrukih batch-eva, srednja originalna source cena *samo feasible* ili `null`, prvi real AC poziv za izvodljivo, Q/P/V/thermal/KCL auditing, per-load pojedinačne feasibility counts, stvarni AC/requests after cap, UCB observations/selections i `withheld` koje NE smeju dobiti nagradu. Predodrediti rizik: **ako novi mehanizam daje 0/12 ili ne veći broj od starih modova, prethodni I27 uspeh ostaje moguća retka slučajnost.** Ako daje 1/12 ili samo mali nerobustan plus, nema tvrdnje superiornosti; navedite nesigurnost i kontra primere. NEMA p-hacking, naknadnog biranja boljih semena ili novih opsega. Nema nezavisne industrijske fizikalne validacije niti matematičke garancije za neizmerene load/kvarove.

Pored nominalnog uporednog prikaza dodati empirijski interval nesigurnosti (Wilson binomni po metodi, **samo deskriptivno**, mali n; isti seed-parovi zavisni, Wilson ne predstavlja upareni kontrast). Ne zaključivati sigurno da je operator causal source of success: crossover, GA selection i RNG nisu upareni counterfactual po jednom genu; čak i nađen broj uspeha nije dokaz originalnosti.

## Naredne faze ostaju odvojene

Nakon *potpunog* I28 rezultata i raw arhive, uraditi poseban **preregistrovani netestirani mrežni režim** sa lokalno različitim Q demand ili line opterećenjem (ne samo isti uniformni faktor) i literaturni novelty audit za scenario credit; tamo mora postojati predefinisan `feasibility` kriterijum, ne retuning na test. I28 je seed-holdout, nije scenario holdout.

## Dokazi

Preregistrovani protokol; posebni reproducibilni I28 runner čita nepromenjeni I27 evaluator; unit testovi bez AC dokazuju tačno 12 novih seed × četiri metode i stop/counter; CI izvodi realne 48 GA i arhivira CSV/JSON sa **SVIH** rezultata bez obzira na negativne ishode; srpski izveštaj i literature-risk matrica pre završetka. **Ne koristiti p-vrednost kao zamenu za nezavisan test sa više topologija/scenarija.**
