# ITERATION50: prihvatljivost, konfiguracije i dokumentacioni citati (ZAMRZNUTO PRE GLAVNOG POKRETANJA)

**Datum:** 2026-10-23.
- Protokol: [ITERATION50_PROTOCOL.md](ITERATION50_PROTOCOL.md) (`c3598f6`).
- Snimak okvira: [results/iteration50/frame_snapshot.tsv](results/iteration50/frame_snapshot.tsv) (62 repozitorijuma).
- Do ovog trenutka nije pogledan nijedan obrazac poziva na pravoj funkciji. Gledani su samo završetak i trajanje smoke
  testova sa konstantnom funkcijom.

## 1. Odluke po kriterijumima (protokol §2)

**Kriterijum 1 (biblioteka opšte namene), isključeni:**
- **Tutorijal ili knjiga:** ML-From-Scratch, MorvanZhou/Evolutionary-Algorithm, dissecting-reinforcement-learning,
  Grokking-Artificial-Intelligence-Algorithms.
- **Aplikacija:** eiten, gaps, py-ga-VRPTW, FeatureSelectionGA, Circle-Evolution, EvoSkeleton.
- **AutoML, NAS ili ML cevovod:** auto-sklearn, FEDOT, devol, OCTIS, Sklearn-genetic-opt, modAL (aktivno učenje),
  PySR (simbolička regresija), RandOpt, evorl (RL), syne-tune („Hyperparameter and Architecture Optimization“,
  trening skripte i backend), HpBandSter (distribuirani multi-fidelity HPO sa nameserverom i workerima; README:
  „Not Maintained Anymore“).
- **LLM agenti i evolucija koda:** openevolve, evo, AntOmniEvo, CORAL, OpenAlpha_Evolve, LLM4AD_Next, LoongFlow, reevo,
  evo-memory, promptimal.
- **Kriterijum 4 (nema realne kutije):** ALNS je za kombinatoriku (destroy/repair).

**Kriterijum 2 (arhiviran):** nni, scikit-optimize, tune-sklearn.

**Već u I49 ili kontrola:** DEAP, Nevergrad, pymoo, PyGAD (GeneticAlgorithmPython), pyswarms.

**Kriterijum 3 (instalacija na Python 3.14 sa NumPy 2.x, bez ručnog kompajliranja):**
- **Simple:** nema PyPI paket (README: „place Simple.py in the same working directory“).
- **MEALPY 3.0.3:** zahteva `numpy<=1.26.0`.
- **pygmo 2.19.0:** nema wheel za 3.14; izvorni paket nema `setup.py` ni `pyproject.toml`.
- **geatpy 2.4.0:** build wheel-a ne uspeva.
- **swarmlib 0.14.1:** razrešavanje zavisnosti daje NumPy 1.26.4.

**Kriterijum 5 (smoke: konstantna funkcija, N = 2, budžet 20; pravilo primenjeno strogo):**
- **Hyperactive 5.0.4:** `ModuleNotFoundError: No module named 'packaging'` (zavisnost nije deklarisana).
- **google-vizier 0.1.24:** `AttributeError: module 'jax.core' has no attribute 'Primitive'` (nekompatibilno sa
  instaliranim JAX-om).
- **gaft 0.5.7:** `ZeroDivisionError` u `RouletteWheelSelection` kada su sve vrednosti jednake. Verovatno je
  posledica baš konstantne funkcije, ali pravilo je zadato unapred.
- **solidpy 0.1:** Python 2 sintaksa (`print self`).

**Uzorak (N = 12):** baybe, bayes_opt, bofire, cmaes, emukit, EvoloPy, evotorch, evox, GFO, NiaPy, scikit-opt, SMAC.
Ima ih ≤ 25, pa ograničenje po zvezdicama nije primenjeno. Hyperactive je isključen, pa unapred zadata analiza
osetljivosti Hyperactive/GFO otpada.

**Tehnička provera pune veličine** (posle prihvatljivosti; ne menja je): konstantna funkcija, N = 10, budžet 200.
Gledani su samo završetak i trajanje. Rezultat je u §4.

## 2. Konfiguracije (protokol §3; zamrznute)
Budžet je 200 evaluacija. Za generacijske biblioteke broj generacija je ⌊200/pop⌋ − 1 (početna populacija + generacije).

| Biblioteka (verzija) | Optimizator i podešavanja | Budžet | Seme | Prijavljeni rezultat |
|---|---|---|---|---|
| bayes_opt (3.4.0) | `BayesianOptimization`; maksimizuje −f | `init_points=5`, `n_iter=195` | `random_state` | `max` |
| cmaes (0.13.1) | `CMA(mean=centar, sigma=0,3·opseg, bounds)`, ask/tell | petlja dok je n + λ ≤ 200 | `seed` | nema (ask/tell) |
| scikit-opt (0.6.6) | `sko.DE` (prvi u README quick start), `size_pop=50` | `max_iter=3` | nema → `random` i `numpy.random` | `run()` → (best_x, best_y) |
| GFO (1.13.0) | `HillClimbingOptimizer` (prvi u README), kontinualni opseg | `n_iter=200`, `optimum="minimum"` | `random_state` | `best_para`, `best_score` |
| NiaPy (2.7.1) | `ParticleSwarmAlgorithm` (prvi u README), podrazumevani parametri | `Task(max_evals=200)` | `seed` | `run()` → (best_x, best_fit) |
| EvoloPy (4.0.6) | `run_optimizer("PSO", callable)`, `population_size=30` | `iterations=5` | nema → `random` i `numpy.random` | `best_solution`, `best_fitness` |
| SMAC (2.4.1) | `HyperparameterOptimizationFacade` (README), `deterministic=True` | `n_trials=200` | `Scenario(seed)` | `optimize()` → incumbent (bez f) |
| evox (1.4.0) | `PSO(pop_size=100, lb, ub)` (README), `StdWorkflow` | `init_step` + 1 korak | `torch.manual_seed` | `EvalMonitor.get_best_solution/fitness` |
| evotorch (0.6.1) | `SNES` (README), `stdev_init=0,3·opseg`, podrazumevani popsize; samo `initial_bounds`, jer SNES odbija `bounds` | ⌊200/λ⌋ generacija | `Problem(seed)` | `status["best"]` |
| emukit (0.5.1, sa `[gpy]`) | `GPBayesianOptimization`, 5 početnih `RandomDesign` tačaka | `run_optimization(f, 195)` | nema → `numpy.random` | nema dokumentovan pristup (R nije primenljivo) |
| baybe (0.15.0) | `Campaign`, podrazumevani recommender, `NumericalTarget(minimize=True)` | 200 × `recommend(1)` | `set_random_seed` | nema (ask/tell) |
| bofire (0.5.0) | `SoboStrategy(qLogEI)` (README), 10 početnih `domain.inputs.sample` | 10 + 190 × `ask(1)` | `sample(seed)`, `make(seed)` | nema (ask/tell) |

**Pojašnjenja pre pokretanja** (ne menjaju mere iz protokola):
1. **R1–R3 nisu primenljivi** tamo gde biblioteka ne prijavljuje rezultat (ask/tell, emukit). Klasifikator iz I49 se
   ne menja; R zastavice se postavljaju na 0, a izveštaj navodi „R n/a“.
2. **float32 biblioteke** (evox, evotorch): zabeležena vrednost je ona koju biblioteka zaista prima, tj. f zaokruženo
   na float32. Tako se gubitak preciznosti ne meša sa R2.
3. **Neocenljiva biblioteka:** ako se svih 30 ćelija završi greškom, biblioteka se ne računa u N i prijavljuje se
   posebno. Ako su greške delimične, ocena se radi na završenim ćelijama.
4. **Seme kao obećanje reproduktivnosti:** za razvrstavanje (§6 protokola), dokumentovan parametar semena znači da se
   obećava reproduktivnost. Ako postoji citat o semenu, D3 ili D3x se razvrstava kao „protivreči dokumentaciji“.

## 3. Dokumentacioni citati (docstring instalirane verzije ili README; protokol §6)

| Biblioteka | Budžet | Seme | Rezultat | Granice |
|---|---|---|---|---|
| bayes_opt | `n_iter`: „Number of iterations where the method attempts to find the maximum value.“ `init_points`: „Number of random points to probe before starting the optimization.“ | `random_state`: „If the value is an integer, it is used as the seed for creating a numpy.random.RandomState.“ | `max`: „Get maximum target value found and corresponding parameters.“ | `pbounds`: „Dictionary with parameters names as keys and a tuple with minimum and maximum values.“ |
| cmaes | nema (petlju vodi korisnik) | `seed`: „A seed number (optional).“ | nema | `bounds`: „Lower and upper domain boundaries for each parameter (optional).“ |
| scikit-opt | nema (`max_iter` nije opisan) | nema | README: „best_x, best_y = de.run()“ | README: „0 <= x1, x2, x3 <= 5“ preko `lb`, `ub` (bez opisa garancije) → nema |
| GFO | `search`: „Evaluates objective_function up to n_iter times“ | `random_state`: „Seed for random number generation.“ | `best_score`: „Best score found during the search.“ `best_para`: „Parameters corresponding to the best score.“ | README: `"x": (-5.0, 5.0)  # continuous range` |
| NiaPy | `max_evals`: „Maximum number of function evaluations.“ | `seed`: „Starting seed for random generator.“ | `run`: „Best individuals components found in optimization process. Best fitness value found in optimization process.“ | `Problem(dimension, lower, upper)` → nema eksplicitne garancije |
| EvoloPy | `iterations`: „Maximum number of iterations“ (iteracije, ne evaluacije) | nema | „'best_solution': Best solution found“, „'best_fitness': Best fitness value“ | `lb`/`ub`: „Lower bound for variables“, „Upper bound for variables“ |
| SMAC | `n_trials`: „The maximum number of trials … to run.“ | `seed`: „The seed is used to make results reproducible.“ | README: `incumbent = smac.optimize()` (bez vrednosti) | `ConfigurationSpace({"C": (0.100, 1000.0)})` → nema eksplicitne garancije |
| evox | nema (koraci) | nema citata u API-ju | `get_best_solution`: „Get the best solution so far.“ `get_best_fitness`: „Get the best fitness value so far.“ | `lb`/`ub`: „The lower/upper bounds of the particle positions.“ |
| evotorch | nema (generacije) | `seed`: „to be used as the seed of the internal random number generator of the stored problem object.“ | nema citata | `initial_bounds`: „In which interval will the values of a new solution will be initialized.“ (inicijalizacija, ne granica) → nema |
| emukit | `num_iterations`: „The number of iterations to run the Bayesian optimization loop.“ | nema | nema | `ContinuousParameter(name, min, max)` → nema eksplicitne garancije |
| baybe | nema (petlju vodi korisnik) | `set_random_seed`: „Set the global random seed.“ | nema | `bounds`: „The bounds of the parameter.“ |
| bofire | nema (petlju vodi korisnik) | `seed` polje strategije, `sample(seed=...)` | nema | `bounds`: „A tuple that stores the lower and upper bound of the feature.“ |

**Primena pravila iz §6 protokola (unapred):**
- **C4 je primenljivo** samo za bayes_opt (init_points + n_iter), GFO („up to n_iter times“), NiaPy („Maximum number of
  function evaluations“) i SMAC („maximum number of trials“).
- **Protivrečnost za C3** važi gde citat granica opisuje granice domena ili položaja: bayes_opt, cmaes, GFO, EvoloPy,
  evox, baybe i bofire.
- **D3 ili D3x** je protivrečnost gde postoji citat semena: bayes_opt, cmaes, GFO, NiaPy, SMAC, evotorch, baybe i
  bofire.
- **R1–R3** su protivrečnost gde postoji citat „najbolje pronađeno“: bayes_opt, GFO, NiaPy, EvoloPy i evox.

## 4. Tehnička provera pune veličine (konstantna funkcija, N = 10, budžet 200)
| Biblioteka | Završeno | Trajanje (s) |
|---|---|---|
| baybe | da | 51.51 |
| bayes_opt | da | 24.62 |
| bofire | da | 38.53 |
| cmaes | da | 0.86 |
| emukit | da | 3.15 |
| evolopy | da | 1.76 |
| evotorch | da | 2.84 |
| evox | da | 2.21 |
| gfo | da | 0.96 |
| niapy | da | 0.76 |
| scikit_opt | da | 0.33 |
| smac | da | 52.62 |

Izvršavanje: svaka ćelija u svežem procesu (`python -I`), sa `OMP/OPENBLAS/MKL/VECLIB_*_THREADS=1`, do 4 ćelije
istovremeno po biblioteci. Vremena su sa konstantnom funkcijom i služe samo kao orijentacija.
