# Iteration 4 — physically charged paired mutation credit (2026-10-21)

**Disposition: experimental scaffold, NOT an established improved algorithm.**
All work performed on `owlCoder/gadapt:main`, as explicitly authorized.
Previously Draft PR [#1](https://github.com/owlCoder/gadapt/pull/1) and
[#2](https://github.com/owlCoder/gadapt/pull/2) were merged to main after
their existing regression CI results were inspected. Upstream
`bpzoran/gadapt` was not modified.

## Rationale / literature

Earlier UCB reward assigned a mutated offspring's entire fitness gain over
the population median to whichever mutation operators it used. Because
parents, crossover, and mutation jointly determine that offspring,
this reward cannot identify the incremental mutation benefit.
Literature already recognizes the credit-vs-choice issue, including
[dynamic strategy credit](https://link.springer.com/article/10.1007/s00500-016-2126-x),
[test-and-apply](https://doi.org/10.1016/j.swevo.2021.101013),
[operator fairness](https://doi.org/10.1016/j.matcom.2025.01.007)
and [normalizing credit on scaled problems](https://doi.org/10.1080/0305215X.2025.2466119).
Therefore **paired before/after credit is not claimed to be a novel algorithm**.

New opt-in `mutation_credit_assignment="paired"` evaluates exactly the
offspring BEFORE it is mutated, then evaluates its single-gene mutant via
ordinary GAdapt. Both objective calls consume *the same actual solver budget*
and require a real monotonically incremented `mutation_evaluation_counter`.
A control/mutant pair not physically evaluated twice does not get rewarded.
When a physical constraint-violation callback exists, the reward is the
change in normalized physical violation and, only for already feasible
controls, an objective improvement that preserves feasibility.

The method addresses a **local attribution problem** but NOT a controlled
between-operator causal comparison, and it sacrifices objective budget on
pre-mutation controls. Pre-mutation baselines are included in the *external*
recorder's best physically evaluated score, but not inserted into GAdapt's
survivor population. This distinction matters when interpreting the
algorithms' best-ever-evaluated incumbent.

## Actual implementation

- `gadapt/ga.py`: optional `mutation_credit_assignment="offspring"|"paired"`
  (default `offspring`); `mutation_evaluation_counter` is required in paired
  mode. Paired mode requires `ensure_unique_individuals=False`,
  `number_of_mutation_decision_variables=1`, and
  `candidate_solution_mutation="random"`. Any other configuration is rejected.
- `gadapt/ga_model/ga_options.py`, `gadapt/factory/ga_factory.py`: wire
  these settings into the real installed GAdapt.
- `gadapt/operations/mutation/population_mutation/base_candidate_solution_mutation_selector.py`:
  physically evaluate the same offspring before mutation.
- `gadapt/operations/cost_finding/elitism_cost_finder.py`: assign a mutated
  candidate's reward only when the external objective counter verifies that
  this physical post-mutation evaluation occurred.
- `gadapt/operations/mutation/decision_variable_mutation/credit_based_decision_variable_mutator.py`:
  track actual control and incomplete-pair counts, calculate normalized
  paired local rewards and support optional feasibility-relative reward.
- `tests/test_paired_operator_credit.py`: real-GAdapt regression tests and
  guards; matrix ran successfully on GitHub Actions Python 3.10–3.12.
- Experiment scripts, raw rows, plots and statistics are tracked below.
  Default `GA()` behavior is unchanged.

## IEEE14 PYPOWER real GAdapt AC reference-system pilot

**Source:** [successful run 39571520975](https://github.com/owlCoder/gadapt/actions/runs/39571520975).
[Canonical zipped raw CSV+logs+paired statistics](https://github.com/owlCoder/gadapt/actions/runs/39571520975/artifacts/12332572868).
Committed numeric observations: `research/results/paired_ieee14_20261021.csv`
(128 trial rows), extracted verbatim as numeric fields from structured
`RUN {...}` lines; canonical Actions CSV remains the precise original.
Plots: `research/figures/paired_ieee14_load100.svg`,
`research/figures/paired_ieee14_load110.svg`.

8 paired seeds per method per load, population 24, **240 true physical
PYPOWER AC solver calls per run**; optimizer errors and nonfeasible runs
remain in reliability totals. Values below are median MW loss *only among
runs that found at least one independently verified feasible AC design*:

| Method | 100% load feasible | median MW | 110% load feasible | median MW |
|---|---:|---:|---:|---:|
| legacy original | 8/8 | 14.251895 | 8/8 | 17.826047 |
| legacy single-gene affine control | 8/8 | 14.144322 | 8/8 | 18.277361 |
| uniform unpaired offspring credit | 8/8 | 14.161402 | 8/8 | 17.868493 |
| UCB unpaired offspring credit | 8/8 | 14.152858 | 8/8 | 17.880445 |
| uniform paired physical credit | 8/8 | 14.177879 | 8/8 | 17.876944 |
| UCB paired physical objective credit | 8/8 | **14.110662** | 8/8 | **17.768363** |
| UCB paired independent feasibility credit | 8/8 | 14.290257 | 8/8 | 17.928615 |
| SciPy differential evolution | 8/8 | 14.255971 | 6/8 | 17.446616 |

Compared to `legacy_single`, at 100% load UCB paired had 5 paired wins /
3 losses; exact sign p=0.7265625, Holm p=1.0 over 7 comparisons; median
paired MW difference -0.070668 and percentile-bootstrap 95% CI
[-0.112626, 0.143767]. At 110% load: 6 wins / 2 losses, exact sign
p=0.2890625, Holm p=1.0; median paired difference -0.186728 MW,
bootstrap 95% [-0.625194, 0.153859].
These effects are statistically **unconfirmed**. 8/8 reliable completions
correspond to Wilson 95% interval only [0.6756,1.0] for true reliability.
The visibly lower median of paired UCB objective does not establish
worst-case reliability or generalization. The independent feasibility
signal did not improve median loss in this setting.

The paired modes spent ~67.5–68 actual extra pre-mutation physical controls
*per run* (median), rather than spending those evaluations on additional
distinct offspring. This is explicitly included in the fixed 240 budget.
Actual median wall times were roughly 1.45–1.58 s per run on one runner;
not evidence of improved computational speed.
One first execution [run 39571326455](https://github.com/owlCoder/gadapt/actions/runs/39571326455)
**failed before the benchmark** because a pre-existing script-only
import did not work under module execution. We fixed the shared import
and reran with `set -o pipefail`. That failed run has no valid numbers.

## GÉANT chronological scenario — cross-domain **non-independent** check

**Source:** [successful run 39571835401](https://github.com/owlCoder/gadapt/actions/runs/39571835401).
[Canonical raw artifact](https://github.com/owlCoder/gadapt/actions/runs/39571835401/artifacts/12332128721).
Committed numeric rows:
`research/results/paired_geant_44_20261021.csv` (56 method-seed rows).
Plot: `research/figures/paired_geant_44.svg`.

Published SNDlib topology, 22 nodes/36 edges and historical anonymized
traffic, assumed shortest-path routing + installed capacity modules,
12 old May–July development matrices + 32 old August matrices.
Traffic was rescaled by the TRAINING-only calibration
`49.569816117149394` as a deliberately labeled stress engineering
scenario. This **reuses exactly the previously inspected August block**,
so is NOT a fresh temporal holdout or independent industrial validation.
The model has no independently justified hard installed-capacity limit;
therefore feasibility credit was not applied.

8 seeds × 7 methods × 240 actual development cost evaluations.
56/56 runs completed. Metric below: installed-capacity plan investment
cost covering **all 44 demand matrices** in SNDlib model units:

| Method | median model cost | worst model cost |
|---|---:|---:|
| legacy | 204067.0 | 221859.0 |
| legacy single-gene affine control | 207428.5 | 220895.0 |
| uniform unpaired offspring | 203574.0 | 224739.0 |
| UCB unpaired offspring | **198470.5** | 224616.0 |
| uniform paired physical credit | 202417.5 | 224328.0 |
| UCB paired physical credit | 201350.0 | 218782.0 |
| SciPy DE | 201612.5 | 218773.0 |

UCB paired vs `legacy_single`: **3 wins / 4 losses / 1 tie**,
two-sided exact sign p=1.0 and Holm p=1.0 across six method comparisons;
median paired difference +194 cost units, bootstrap 95%
[-3996, 1669], conditional Wilcoxon p=0.6875. Not superior.
Relative to UCB unpaired, paired UCB has a *worse* observed median.
The paired UCB algorithm used 402 true pre-mutation control evaluations
across the 8 runs (~50/run) within the 240-per-run budget.
Median runtime was roughly 3.0–3.1 s per run, subject to runner conditions.

## Adjudication

Both physics-based and public historical planning results are exploratory.
The new approach is methodologically better measured *locally*, but provides
**no statistically confirmed improvement in global optimizer performance**
and its extra control evaluations reduce the budget left for exploration.
A positive subset result from IEEE14 does not override the negative/mixed
cross-domain result. No claimed originality or industrial readiness.

The next scientifically defendable direction is an operator-level
randomized comparison *with known selection propensities* and a strict
evaluation budget, or to compare alternative cheaper parent-based credit
baselines as existing AOS controls, **before** costly large-scale tuning.
For any dissertation-level conclusion still required: at least 50–100+
powered independent trials after a preregistered analysis,
JADE/SHADE/CMA-ES/domain OPF baselines, IEEE118/RTE and another truly
independent infrastructure class, high-quantile failure and feasibility
intervals, uninspected chronological holdout, and explicit resource cost.
There is presently no statistically or theoretically defensible new
GAdapt algorithm claimed in this iteration.

**Decision:** retain paired evaluation as an optional diagnostic ablation,
do not promote it to the default policy.
