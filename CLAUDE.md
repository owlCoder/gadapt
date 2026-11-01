# GAdapt

Self-adaptive genetic algorithm library (Python 3.10+, NumPy only), published on PyPI as `gadapt`.
Pure Python, no compiled code. `README.md` is also the PyPI long description.

## Running and verifying
- There is **no test suite**. Verify a change by running the README examples (`from gadapt.ga import GA`) and,
  for anything that affects search behaviour or speed, by a paired-seed benchmark. `benchmarks/std_dev_floor.py` is a template
  (multiprocessing, the experiments' GA configuration, gap to the known optimum, Wilcoxon per cell); run it from a scratch directory.
- Use the repo's pyenv Python (`.python-version` = 3.12). Other interpreters on this machine lack NumPy.
- `logging=True` writes a `log/` folder into the current working directory (git-ignored). Run experiments
  from a scratch directory so it doesn't land in the repo.
- Results are stochastic. Seed **both** `random.seed(s)` and `numpy.random.seed(s)`, and compare over several
  seeds (6+) before concluding anything about speed or quality; per-run differences under ~10% are noise.
  Compare cost-function evaluations, not only wall-clock time: iteration counts vary between runs.

## Architecture
- `GA` (`gadapt/ga.py`) holds the user-facing parameters and validates them. `execute()` clones the GA, builds
  `GAOptions` from it, and runs `GAExecutor` with a factory. Defaults that depend on the added variables
  (e.g. `ensure_unique_individuals=None`) must be resolved in `GAOptions`, not in `GA.__init__`, because
  variables are added after construction.
- Each generation (`gadapt/execution/ga_executor.py`): exit check -> immigrate -> mate -> mutate -> find costs
  (the elitism cost finder keeps the best `keep_elitism_percentage`, then decision-variable and population stats are updated).
- `gadapt/operations/*` holds one package per step (selection, sampling, crossover, mutation, exit check, ...),
  each with a `base_*` abstract class. `GAFactory` (`gadapt/factory/ga_factory.py`) builds all of them from
  the options; users customise by subclassing it and overriding a `_get_*` method. The factory is only
  initialised inside `GA.execute()`, so don't create option-dependent objects before that.
- Mutation/crossover choices are comma-separated strings (`"cost_diversity,parent_diversity"`); the valid
  tokens live in `gadapt/ga_model/definitions.py`. `crossover` also carries the probability method
  (`"blending,cost_diversity"`).
- Model: `Population` -> `CandidateSolution` -> `VariableValue` (a value) -> `DecisionVariable` (bounds, step, shared by variable values).

## Behaviour to keep in mind
- `ga.add(min, max, step)`: the step is the value grid; no step means a continuous variable.
  Operators that produce values for a discrete variable must round them to `decision_variable.decimal_places`, so they are exact grid
  values (not `0.30000000000000004`) and compare equal to the other copies of the same grid value (the normal distribution mutator's nudge check relies on it).
- Uniqueness (`ensure_unique_individuals`): `Population` remembers value tuples in `_seen_candidate_solutions`.
  Anything that changes variable values after a candidate solution is added must call `population.register_candidate_solution(c)`.
  `add_candidate_solution` returns `False` (and silently drops the candidate solution) when the population is full.
  It is a real cost late in a run (many retries once the search converges), but it avoids repeated evaluations.
- Two coefficients are NaN unless the updater that computes them is created, and the factory creates each only when its token
  appears in a relevant option: `columnar_diversity_coefficient` (`ColumnarDiversityDecisionVariableUpdater`, token
  `variable_columnar_diversity` in a mutation **or crossover** option, see `_get_decision_variable_updater`) and
  `relative_cost_diversity_coefficient` (`CostDiversityPopulationUpdater`, token `cost_diversity` in `population_mutation` **or
  `crossover`**, see `_get_population_updater`). Anything new that reads one of them must be covered there. A NaN crossover
  probability used to hang `BaseCrossover._mate_pair` forever; it is now an error.
- `normal_distribution_mutation_min_std_dev_decay_generations` (default `None` = off) is an opt-in: the lower bound of the Gaussian mutation's
  standard deviation is divided by 10 per N consecutive generations without improvement of the minimal cost (`Population.generations_without_improvement`,
  the same count that drives the exit rule), floored at one step for discrete variables. With it off, results must stay bit-identical:
  check a seeded run before and after any change to the Gaussian mutators. Measured on the continuous benchmarks (see the benchmark script):
  min std dev 1e-4 + decay 2.5 gives ~1.8 orders of magnitude lower median gap for ~20% more evaluations; a fixed floor below one step
  hurts discrete variables, and a fixed floor <= 1e-5 hurts 20 variables (the 600-generation cap is reached before convergence).
- `mutation_focus_generations` (default `None` = off) is an opt-in `MutationFocus` (`operations/mutation/mutation_focus.py`) created by the factory and set as
  `.focus` on the decision-variable mutation selector, the rate determinators (main and helper) and every `ComposedDecisionVariableMutator`. While the minimal cost
  stagnates it scales the number of mutated decision variables and the weight of the random mutator by `0.5 ** (stagnation / N)`; with probability
  `mutation_focus_exploration_probability` per mutated candidate solution it is skipped. With it off no random numbers are drawn and results must stay
  bit-identical (compare seeded runs against `git archive HEAD`). Benchmark: `benchmarks/mutation_focus.py`.
- `ParentDiversityCandidateSolutionUpdater` is a singleton (`__new__`), so its state is shared across `GA` instances.
- Pure-Python per-decision-variable overhead dominates for cheap cost functions (~1 ms/generation at pop 32 x 10 decision variables,
  scaling linearly with population size and decision-variable count). For real cost functions, the number of evaluations
  per generation is what matters.

## Conventions
- Version lives only in `setup.py`; this project bumps the patch number per release (0.4.x).
- A new `GA` parameter needs: constructor argument, property + setter in `ga.py`, the field in `GAOptions`,
  a docstring entry, and an entry in the README "Parameters Description". Keep README code blocks runnable.
- Renaming a `GA` parameter: add the old name to `DEPRECATED_PARAMETER_NAMES` in `ga.py` (it gives the constructor kwarg and a
  warning property alias automatically) and to the README "Previous Parameter Names" table.
  Renaming an option value (a token like `"cost_diversity"`): add it to `DEPRECATED_OPTION_VALUES`.
- Known typo kept in sync with the README: "Calculation not succesful" (`ga_strings.py`).
- Don't commit, push or bump the version unless asked.
