# GAdapt: Repository Instructions for Coding and Research Agents

These instructions apply to work in `owlCoder/gadapt`. For specialized workflows, use the repository skills in `.agents/skills/`:

- `literature-auditor`: independent, read-only review of prior art and novelty.
- `math-reviewer`: read-only proof and mathematical assumption checks.
- `implementation-engineer`: implementation and validation only after a research protocol is approved.

Read each skill's `SKILL.md` when its workflow is needed. All research gates and repository constraints in this document remain in effect.

## Resume protocol (every new session, after crash/power loss)
1. Read `research/PHD_PROGRESS.md` — the single source of truth for where work stopped. Continue from its "NEXT STEP".
2. Update `research/PHD_PROGRESS.md` after every meaningful research step. During an explicitly authorized ongoing
   research session, commit progress LOCALLY for crash recovery. For one-off changes, only commit when requested.
   Push only with authorization, in batches (end of a phase/session or when asked): pushes to `main` can trigger
   `robustness-tests.yml` and consume CI minutes.
3. The established research workflow uses `main` of `owlCoder/gadapt` (local clone: `~/Desktop/gadapt`);
   do not create feature branches or pull requests unless the maintainer changes this workflow. Record changes accurately.
4. Python: `.venv/bin/python` (numpy, scipy, networkx, hypothesis, pytest). Tests: `.venv/bin/python -m pytest -q research/test_iteration41_*.py`.
5. If reasoning effort is configurable, use at most `high`. Delegate sparingly, mainly for substantial independent literature reviews.

## Objective
Produce a defensible original scientific contribution to GAdapt for infrastructure optimization.
Research validity is more important than experiment count, positive results, or code volume.

## Mandatory research gates
1. Read the latest handoff and research history (`research/PHD_PROGRESS.md`, latest ITERATION* docs).
2. Search relevant prior art before proposing novelty.
3. Identify the exact mathematical difference from prior work.
4. State a falsifiable hypothesis and strong baselines.
5. Freeze protocol, datasets, metrics, seeds and budgets (commit BEFORE code/runs).
6. Only then run real experiments.
7. Archive inputs, source hashes, raw outputs and negative results.

## Hard constraints
- Never modify upstream `bpzoran/gadapt` (its push URL is disabled in this clone).
- GitHub write actions (issues, PRs, comments, reactions) ONLY on the user's own repo `owlCoder/gadapt`. Never on
  third-party repos (user, 2026-10-24). Reading their issues is fine; upstream report drafts go to `research/` for the user.
- Never claim originality from implementation alone. Never invent citations: verify every DOI.
- Never invent or reconstruct missing research data (e.g. the lost SNDlib temporal TGZ, SHA `2c3ca706…`).
- Never tune methods using held-out results. Never repeat an experiment until it becomes positive.
- Separate synthetic validation from real infrastructure evidence.
- Preserve existing GAdapt behavior unless explicitly authorized (new behavior = opt-in, default bit-identical).
- Do not run physical/expensive CI workflows automatically.

## Required output for every research proposal
Research question · closest known prior art with DOI · precise novelty claim or "not established" ·
formal assumptions and proposed theorem · strongest baselines · falsification experiment ·
computational budget · GO / NO-GO. If novelty is not established, STOP before implementation.

---

# GAdapt

Self-adaptive genetic algorithm library (Python 3.10+, NumPy only), published on PyPI as `gadapt`.
Pure Python, no compiled code. `README.md` is also the PyPI long description.

## Running and verifying
- The library does not have a comprehensive package-level test suite, but research tests exist. Verify relevant changes
  using the README examples (`from gadapt.ga import GA`), applicable research tests, and,
  for changes affecting search behaviour or speed, paired-seed benchmarks. `benchmarks/std_dev_floor.py` is a template
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
- `GA.execute()` validation calls the cost function on all-min and all-max values (2 real evaluations, not part of the search).
  Budget wrappers count them; with binary route choice all-min is exactly the trivial "first path" solution (see research I43).
  `probe_cost_function=False` (opt-in) skips them.
- `VariableColumnarDiversityDecisionVariableMutationRateDeterminator` raises the UPPER LIMIT of mutated decision variables to
  at least round(N/5), ignoring `number_of_mutation_decision_variables`; the actual count is then drawn uniformly from 1 to that limit; `strict_mutation_decision_variable_limit=True`
  (opt-in) caps it. Crossover duplicate repair (`BaseCrossover`) mutates separately with an attempt-based limit.
- `ga_utils.average_difference` averages adjacent gaps of the sorted values, which telescopes to (max - min)/(n - 1): the default
  cost diversity (log-shifted costs, ratio to generation 0) is a normalized log-RANGE of survivor costs, insensitive to interior
  costs (one outlier keeps it high and the cost-diversity mutation low).
- Columnar diversity is measured on log((v - min) + 1) by default: NOT invariant to units / position in the range
  (optimum near the upper bound of a large-range variable is reached ~10^3-10^4 worse, research I46 notes).
  `columnar_diversity_metric="linear"` (opt-in) is invariant.
- Bit-identity check for library changes: seeded call-sequence hashes (every argument vector and cost) before/after.
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
- For ad-hoc work, do not commit or push unless asked. For explicitly authorized ongoing research, follow the local crash-safety commit protocol above; push only with permission. Never bump the package version without explicit approval.
