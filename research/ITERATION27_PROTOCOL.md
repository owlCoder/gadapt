# Iteracija 27 — prvi pravi AC test nove GAdapt scenario-feasibility opcije protiv jakih kontrola

**Pre-registracija 21.10.2026 PRE ijednog novog I27 AC PF proračuna.** Fork owlCoder/gadapt:main; upstream bpzoran/gadapt ostaje nedirnut. Novi opt-in `mutation_operator_credit='scenario_feasibility'` implementiran u I26 (core GAdapt, testovi Python 3.10–3.12), uz priznanje da UCB/AOS, feasibility rules i sensitivity-aware constraint-handling već postoje u literaturi. **Ovo je mali in-sample/narrow control pilot, NE dokaz originalnog doktoratskog algoritma.**

## Zamrznuti, zajednički originalni IEEE118 fizički zadatak

Javni izvorni `pypower.case118()`, 118 bus, 54 aktivnih gen i 186 branches. Izvorni PG/VG/PMIN/PMAX/QMIN/QMAX, VMIN/VMAX, pozitivni RATE_A MVA obostrano, taps, shunts, topology, originalni polynomial gencost ostaju isti; jedine promene scenarija su **PD i QD svakog originalnog bus pomnoženi sa (0.98,1.00,1.02)**. Svaki upravljački 6D vektor je isti preko sva tri load scenarija (bez adaptacije po scenariju), **PG svih 54 izvorno fiksan osim AC slack output**. `PYPOWER runpf` Newton–Raphson, PF_ALG=1, PF_DC=0, PF_TOL=1e-8, PF_MAX_IT=40, ENFORCE_Q_LIMS=0; Q se obavezno proverava naknadno iz 54 originalna generator Q limitiranja.

**Isti šestodimenzionalni generator VG za SVAKI metod**: originalni BUS103/gen46, BUS32/gen15, BUS34/gen16, BUS92/gen43, BUS19/gen9 iz I24 lokalnog petodimenzionalnog centar/box `center±0.005 p.u.` (istorijski I23 fizički-informed centar), plus **BUS74, gen34 (originalni source VG=0.958, bound [0.948,0.968])**, uveden pre novih eksperimenata na osnovu predregistrovanog I25 holdout Q failure BUS74 pri load 0.98. Ovo je **data-informed representation / kalibracioni eksperiment**, ne nezavisna validacija na neviđenoj mreži. Šesti gen mora biti PV source type 2, originalni PG ostaje. Nijedna prethodna I23/24/25 AC proba nije besplatno iskorišćena kao nova feasible GA tačka.

**Jedan objektivni upit = TAČNO 3 fizička runpf poziva**, po jedan za faktor 0.98,1.00,1.02, redom, uključujući numerički neuspešan AC. Budžet proveriti **pre celog batch-a**, nema delimično evaluiranih kandidata. Za N stvarnih AC maksimalno `cost_function` može da završi N/3 kompletnih vektora. Sve metode potpuno isti trošak: arithmetic mean 3 izvorna economic costs + `1e5 * sum(source normalized physical violation)` po tri scenarija; source violation = 0 isključivo ako su svi izvorni individualni PG/QG, bus V, pozitivni rated terminal MVA i kompleksni KCL ispunjeni u tom scenariju; inače iz originalne `physics_118` metrike. Originalni individualni source feasible cash-price je srednja cena preko 3 režima **samo** ako svaki od tri stvarna PF scenarija zadovolji SVE source limitacije. `success=True` nije isto što i `feasible=True`. Ako bilo koji PF numerički fail: svi preostali load scenariji se i dalje stvarno pozivaju, score = 1e12 i feedback `None`. Posle budžeta: sentinel 1e12 bez fizičkog poziva ili operator credit.

## Fiksirano šest metoda i budžeti

Metode:
1. `gadapt_legacy` default originalna mutation, log_relative;
2. `gadapt_ucb_objective`, već implementiran UCB sa objective reward;
3. `gadapt_ucb_scalar_feasibility`, već postojeći scalar violation feedback = max 3 scenario raw source normalized violations;
4. `gadapt_ucb_scenario_feasibility`, **I26 novi in-core** UCB reward po celom vektoru 3 scenario kršenja, pun kredit samo ako sva 3 source-feasible; stvarni fizički brojač obavezno tačno +3 po credited offspring;
5. `scipy_de`, differential_evolution, `polish=False,tol=0,atol=0,popsize>=5`;
6. `bounded_powell`, `scipy.optimize.minimize` Powell x0=common informed center, `maxfev=60,xtol=1e-5,ftol=1e-7`. Powell je determinističan za isti centar i njegova tri seed-a nisu tri nezavisne stohastičke putanje.

Za sve metode `seeds 2026, 2027, 2028`, svaki run novi model i RNG; GAdapt pop12, isti fixed `exit_function=lambda:real_AC_calls>=180`, mutation default `decision_variable_mutation='variable_columnar_diversity,random'` (identično odabran u svim GA režimima), `population_mutation='cost_diversity,parent_diversity'`, `timeout=240`. Svaki run **najviše 180 stvarnih AC = 60 kompletnih po-tri scenarijska fitness kandidata**, 18 run-ova, ukupno **najviše 3240 pravih AC**. Ne popunjavati ranije završeni run naknadnim fiktivnim podacima. DE/GA optimizer zahtevi post-budget idu u sentinel, nikada nisu AC. Controller callback je cached/pure, ne izvršava nikakav real AC; ako nema rezultat tri stvarna scenarija vraća None i credit se odbacuje. Za sve prave AC, validirati originalne source PG/QG svih 54, V svih 118, positive rated RATE_A MVA oba kraja i kompleksni KCL (prag P/Q/MVA 1e-3, V 1e-5, KCL 1e-3 MVA). `RATE_A=0` nije termički limit.

## Primary/secondary real metrics i naučne zabrane

Primarno `runs_with_at_least_one_all_3_scenarios_feasible`, zatim `best_all_scenario_feasible_mean_original_economic_cost_or_null`, `first_all_scenario_feasible_TRUE_AC_call_id`, `feasible_3scenario_batches`, `budget_true_ac_calls`. Sekundarno: `per_scenario_only_feasible_counts`, najmanji penalizovani score (ne feasible cena), cache feedback observations i withheld, solver failure, postbudget requests, operator-selection summary, source true detailed Q/P/V/terminal/KCL. Sve 18 sirovih metoda-seme kombinacija prikazati. **Bez p-vrednosti i statističkog dokaza sa tri semena**, bez cherry-pick-a samo najbolji; bez “drži se source real industry” tvrdnje. Nema dokaza novog algoritma sve dok ne postoji dovoljno jaka multi-domen validacija i novelty pregled.

## Pre-execution fail-closed regression

Testovi bez AC: originalni gen identitet BUS74 gen#34, 5+1 source PV bounds, brojanje **tačno 3 true simulator calls per scored individual** uključujući neuspeh, odbijanje nepotpune batch i sentinel without feedback, re-read I26 unit/regressions. CI green. Zatim arhivirati tačan CSV/JSON iz logova i srpski izveštaj bez prikrivanja negativnih rezultata. Python 3.12, pypower==5.1.19, scipy==1.13.1, pandas==2.2.3, pandapower==2.14.11, single-thread BLAS/OMP.

**Zaključak je unapred NEPOZNAT**: scenario-robust feasible pojedinac može izostati kod svih metoda, posebno zbog više originalnih Q ograničenja. Takav negativan rezultat je važan i ne sme se prevoditi u “novi GAdapt dokazano dobar”.
