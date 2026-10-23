# Does the optimizer do what it says? A black-box audit of evaluation integrity in 21 Python optimization libraries

*Manuscript draft, 23 October 2026. Every experiment was preregistered before code was written and run once. Code,
inputs, raw outputs and protocols are in `owlCoder/gadapt`, directory `research/` (Section 10).*

## Abstract

Comparisons of black-box optimizers rest on two assumptions:
- each optimizer evaluates the cost function the way its documentation says;
- each optimizer reports what it actually found.

In engineering applications such as power-flow-based dispatch, every hidden, repeated or out-of-budget evaluation
costs real compute. Every inconsistent report can change the conclusion of a comparison.

We present a library-independent black-box audit that records every call to the cost function and checks three
things:
- call-level integrity: out-of-box, over-budget and post-return evaluations, plus repeated points;
- consistency of the reported result with the recorded calls;
- reproducibility under a fixed seed, both within one process and between fresh processes.

The audit is validated on planted faults. We applied it to 21 Python libraries in two preregistered studies: nine
popular libraries, and twelve libraries drawn by an external rule from GitHub topics and a recent framework review.
- Integrity problems other than corner evaluations occurred in 8 of 21 libraries (Clopper–Pearson 95% CI 18–62%).
- Behaviour that contradicts the libraries' own documentation occurred in 4 of 21 (5–42%).
- The audit found two previously unreported defects: SMAC 2.4.1 results depend on `PYTHONHASHSEED` despite a fixed
  seed, and Gradient-Free-Optimizers 1.13.0 reports the minimized cost with a flipped sign. It also identified the
  root cause of a long-standing Nevergrad reproducibility issue that affects its default `NGOpt` optimizer.
- All three were reproduced on the latest releases and disclosed to the maintainers. Nevergrad and GFO were also
  reproduced on the development branch; for SMAC we checked that the code on the development branch is unchanged.
- A preregistered measure, "corner evaluations", proved non-specific. We report this negative methodological result
  and its consequence for prevalence estimates.

We recommend running such an audit before any optimizer comparison on an expensive cost function, and checking
reproducibility across processes, not only within one.

## 1. Introduction

Benchmarking practice in evolutionary computation counts function evaluations carefully: COCO (Hansen et al. 2021)
and IOHexperimenter (de Nobel et al. 2024) wrap the objective and record every call. Practitioners who compare
optimizers on their own expensive models rarely use such platforms. They call libraries directly through the
library's own budget, seed and result interfaces, and trust that:
1. the budget parameter bounds the number of evaluations;
2. every evaluation happens inside the declared box and during the search;
3. the returned solution and cost are the best evaluated pair;
4. a fixed seed reproduces the run.

When any of these fails silently, the comparison is wrong in a way that no statistical test reveals.

The work started from a concrete case. In our own library, GAdapt, input validation evaluated the cost function at
the all-lower and all-upper corners of the box. On a binary route-choice problem, the all-lower corner is the trivial
first-path solution. Most likely, these two hidden evaluations made a validation probe look like a search result in
an earlier experiment (Section 7.1). The original raw data of that experiment are no longer available, so this
remains the most plausible reading, not a verified fact. This raised a general question: how often do optimization libraries evaluate, count,
reproduce or report differently from what their users assume?

**Contributions:**
1. A black-box, library-independent audit with explicit call classes and result-consistency checks. Its
   cross-process reproducibility check (D3x) exposes seed failures that within-process checks miss.
2. Validation of the audit on planted faults, including faults that are only visible across processes.
3. Two preregistered prevalence studies on 21 Python libraries, one of them drawn by an external sampling rule,
   and a third study that adds cross-process reproducibility to the first sample.
4. Three diagnosed defects with minimal reproducers, causal patch tests where applicable, and disclosure to the
   maintainers.
5. A negative methodological result: a natural "probe" measure is not specific, which changes the prevalence
   estimate.
6. A practitioner command-line tool with a five-step checklist.

## 2. Related work

- **Evaluation accounting and benchmarking platforms.** COCO (Hansen et al. 2021) and IOHexperimenter (de Nobel et
  al. 2024) count evaluations and log performance. They are designed for benchmark functions inside the platform,
  not for auditing what an arbitrary library does with a user's objective.
- **Invariance and structural bias.** Kudela (2022) showed that many metaheuristics exploit the centre of the search
  space. BIAS (Vermetten et al. 2022) detects structural bias from final positions. Invariance testing is an
  established principle (Hansen et al. 2011). We use invariance only as a secondary property and claim no novelty
  for it.
- **Comparing frameworks.** Ravber et al. (2025) compared six algorithms across 13 frameworks and found large
  performance differences between implementations of the "same" algorithm. They noted that many frameworks lack
  evaluation-based stopping. They do not classify individual calls or check reported results against evaluations.
- **Metamorphic testing** has been applied to genetic algorithms (Rounds and Kanewala 2018) and to industrial
  optimisation software (Duque-Torres et al. 2025a, 2025b). It checks relations between runs and is closest in
  spirit to our seed and documentation checks. Its targets are algorithm or application properties, not the
  evaluation contract between a library and its user.

**Our claim is narrow.** No component (counting, invariance, seeding) is new in isolation. What is new is a
validated, library-independent black-box audit that classifies every call, checks reported results against
recorded calls, and checks documented relations, including cross-process reproducibility. A second contribution is
its prevalence measurement on an externally sampled set of libraries.

## 3. The audit

A recorder wraps the user's cost function and stores, for every call, the point x, the value f and a phase: search,
or post, meaning after the optimizer's main call returned. Each library is run through a small adapter that uses only
its documented interfaces for budget, seed, bounds and result.

| Class | Definition | Integrity? |
|---|---|---|
| C1 | x equals the all-lower or all-upper corner of the box | preregistered as integrity; see Section 6.3 |
| C2 | x bit-identical to an earlier evaluated point | waste (reported as a share) |
| C3 | some coordinate of x outside [lower, upper] | yes |
| C4 | more calls than a documented maximum (only where one is documented) | yes |
| C5 | calls after the optimizer's main call returned | yes |
| R1 | reported x\* was never evaluated (tolerance 1e-12) | yes |
| R2 | reported f\* differs from the recorded f(x\*) (relative 1e-9) | yes |
| R3 | reported f\* worse than the best value evaluated during search | yes |
| D2 | reported evaluation count differs from the recorded count | yes |
| D3 | same seed, different call sequence on a rerun in the same process | yes |
| D3x | same seed, different call sequence in two fresh processes with different `PYTHONHASHSEED` | yes |

The call sequence is compared through a SHA-256 hash over (x, f, phase) for all calls. R1–R3 are not applicable
when a library returns no result, as in ask-and-tell interfaces. For libraries that work in float32, the recorder
stores the value the library actually receives, so that rounding is not counted as R2.

**Test problems:**
- shifted sphere, with the optimum at 0.37 of the range;
- Rastrigin;
- the floor plateau Σ⌊x_i⌋;

in N ∈ {2, 10}, on the box [−5, 5]^N, with seeds 6000–6004. This gives 30 cells per library.

## 4. Validation of the audit

Before each study, a reference random search was run with exactly one planted fault per mutant. Faults covered:
- a corner probe;
- a re-evaluated duplicate;
- one call over the budget;
- reporting an unevaluated point;
- reporting a wrong value;
- seeding from `hash()`, visible only across processes;
- seeding from the clock.

The audit had to flag exactly the planted class and nothing on the clean reference. GAdapt with its default input
validation had to produce C1, and without it had to produce none. All checks passed: 8/8 in Study 1 and 11/11 in
Study 2. The practitioner tool repeats these checks in its test suite.

## 5. Studies

Both protocols, including the decision thresholds and the documentation-classification rule of Study 2, were
committed before any code was written.

**Study 1 (I49).** Nine popular libraries:
- pymoo GA;
- DEAP `eaSimple`;
- PyGAD;
- geneticalgorithm;
- Nevergrad `NGOpt`;
- Optuna TPE;
- PySwarms;
- cma `fmin2`;
- SciPy `differential_evolution`.

Settings: default configuration, about 1000 evaluations, set through the documented parameter. GAdapt served as a
positive control.

**Study 2 (I50).** A new sample drawn by an external rule from a frozen snapshot:
- **Source A:** GitHub repositories in Python with at least 300 stars and one of 12 optimization topics.
- **Source B:** the Python frameworks in Ravber et al. (2025).
- **Eligibility:** general-purpose library, not archived, installable on Python 3.14 with NumPy 2.x, documented
  box-constrained single-objective API, and a smoke test with a constant cost function.

Of 62 candidates, 12 were eligible: baybe, bayes_opt, bofire, cmaes, emukit, EvoloPy, evotorch, evox,
Gradient-Free-Optimizers (GFO), NiaPy, scikit-opt and SMAC. The budget was 200 evaluations. Before the run, we froze
the configurations and the documentation quotes for budget, seed, result and bounds.

**Study 3 (I51).** D3x on the Study 1 sample, with the unchanged Study 1 adapters.

## 6. Results

### 6.1 Prevalence

| Outcome | Study 1 | Study 2 | Pooled |
|---|---|---|---|
| ≥ 1 finding, all classes (preregistered) | 4/9 (14–79%) | 11/12 (62–100%) | 15/21 (48–89%) |
| ≥ 1 finding excluding C1 (post hoc, Section 6.3) | 4/9 | 4/12 (10–65%) | 8/21 (18–62%) |
| ≥ 1 finding excluding C1 and design-caused C3 (post hoc) | 3/9 | 3/12 | 6/21 (11–52%) |
| Behaviour contradicting the library's documentation | 2/9 | 2/12 (2–48%) | 4/21 (5–42%) |

Clopper–Pearson 95% intervals are in parentheses.

**Cross-process reproducibility on all 21 libraries.** Study 3 found D3x in 1 of the 9 Study 1 libraries: Nevergrad,
in the same cells as D3. Over both samples, a fixed seed fails to reproduce the run for 2 of 21 libraries, Nevergrad
and SMAC. The SMAC case is visible only across processes.

**Waste.** The median share of repeated evaluations was 47% for scikit-opt DE, 41.5% for geneticalgorithm and 11.5%
for DEAP. With an expensive cost function, that is close to half of the budget.

![Figure 1](fig_integrity_matrix.png)

**Figure 1.** Runs with each finding class, per library. Dark outlines mark behaviour that contradicts the library's
documentation. C1 is shown apart (Section 6.3). The right column gives the median share of repeated evaluations.
Generated by `make_figure.py` from the raw outputs.

### 6.2 Findings and diagnoses

| Library | Finding | Cause | Status |
|---|---|---|---|
| DEAP | evaluations outside the box (30/30 runs) | bounds are the user's responsibility | design; previously noted (Ravber et al. 2025) |
| PyGAD | 21 evaluations after return | `best_solution()` without `pop_fitness` re-evaluates the population | documented |
| cma | up to 1011 evaluations for `maxfevals` = 1000 | the maximum is checked per iteration | known (pycma #195) |
| Nevergrad | `NGOpt` not reproducible under a fixed seed (D3, and D3x from the first evaluation) | `cma.fmin` called without a seed (pycma default `seed='time'`); the metamodel's inner optimizer is created without a seeded parametrization | known issue (#1572, open since 2023); **root cause and a 12-line patch are ours** |
| SMAC 2.4.1 | D3x in 30/30 runs, no D3 | `LocalSearch._get_initial_points` returns `list(set(...))` of `Configuration`, whose hash is a string hash | **new**; reported (#1380) |
| GFO 1.13.0 | R2 in 25/30 runs, R3 in 10/30 | with `optimum="minimum"`, the internal negation is not undone in `best_score` or `search_data` | **new**; reported (#106) |
| scikit-opt DE | R3 in 1/30 runs; 301 calls for a nominal 200 | after selection, `self.Y` holds only trial values, so a retained parent better than all trials is never seen as best; parents are re-evaluated every generation | related report without details (#187); not disclosed under our preregistered rule |
| evotorch SNES | evaluations outside the box | SNES does not support hard bounds; the README uses `initial_bounds` | design |
| bayes_opt | on the plateau, 7 of 200 requested evaluations | a repeated suggestion returns a cached value but consumes an iteration | documented in `TargetSpace.probe` |

**Causal checks:**
- **Nevergrad:** with our patch, the full call sequence was identical within and across processes in 16/16 cells,
  against 0/6 unpatched. The issue's original reproducer became deterministic.
- **SMAC:** order-preserving de-duplication made the sequence independent of `PYTHONHASHSEED`. With default hash
  randomization, three runs with `seed=0` gave three different incumbents.
- **GFO:** reproduced on the development branch; the proposed fix was not tested.

### 6.3 A negative result: corner evaluations are not specific

C1 was designed to catch input-validation probes such as GAdapt's. In Study 2 it fired for nine libraries, almost
always for legitimate reasons:
- clipping to the bounds in particle swarms;
- acquisition optima at the boundary in Bayesian optimization;
- deliberate vertex initialization (GFO `initialize={"vertices": 4}`);
- on the plateau, the lower corner is the region of the global optimum.

No Study 1 library had a C1-only finding, so the Study 1 estimate is unaffected.

The preregistered Study 2 verdict ("common", 11/12) is therefore driven by a non-specific class. Excluding C1, which
is a post hoc analysis, gives 4/12. Under the same thresholds this would be inconclusive: the lower bound of 9.9% is
just below the 10% threshold.

We report both and treat the C1-free estimate as the defensible one. The practitioner tool reports corner
evaluations as information, not as a problem.

## 7. Discussion

### 7.1 Why this matters for comparisons

Each defect class changes a typical comparison:
- **GAdapt case.** The hidden corner evaluations turned a validation probe into an apparent search result.
- **GFO.** Comparing GFO's `best_score` across minimizers would rank it as finding negative costs.
- **SMAC.** Seeded results cannot be reproduced by a reader who reruns the script, because Python randomizes string
  hashing per process.
- **scikit-opt DE and geneticalgorithm.** Spending nearly half the budget on repeated points halves the effective
  budget in an equal-budget comparison.
- **cma.** Over-budget evaluations make equal-budget comparisons slightly unequal.

### 7.2 Why cross-process checks

Within-process reruns did not detect the SMAC defect. Python's per-process hash randomization makes any iteration
over a set of hashable objects whose hash depends on strings a hidden source of randomness. The audit catches this
in one line of configuration: two subprocesses with different `PYTHONHASHSEED`.

## 8. Threats to validity

- **Sampling.** GitHub topics and star thresholds are incomplete, so we added an external source. Eligibility
  excluded several libraries for installation or packaging reasons, on Python 3.14 with NumPy 2.x. A strict
  smoke-test rule excluded gaft because it divides by zero on a constant cost function.
- **Sample selection.** The Study 1 sample was chosen by us. Only the Study 2 sample follows an external rule. The two
  studies also differ in budget (1000 against 200).
- **What counts as a problem.** C3 in DEAP and evotorch reflects missing bounds handling, which the libraries leave to
  the user or do not support. PyGAD's post-return evaluations are documented. These count under the preregistered
  definition. Excluding C1 and the two design cases of C3 leaves 6/21 libraries (11–52%). The strictest measure,
  behaviour that contradicts the documentation, gives 4/21.
- **Configuration.** We used default configurations through the documented interfaces and small budgets (200 or
  1000). Other usage may behave differently.
- **Applicability.** R1–R3 do not apply to libraries without a reported result. C4 applies only where a maximum is
  documented.
- **Post hoc analyses.** The C1 sensitivity analysis and the causal diagnoses were done after the runs and are
  labelled as such. The preregistered outcomes are reported unchanged.
- **Novelty.** All individual Study 1 findings were already known. The contribution of Study 1 is automated
  detection and prevalence.

## 9. Recommendations for practitioners

Before comparing optimizers on an expensive cost function:
1. Wrap the cost function in a recorder.
2. Check that the reported solution was evaluated, and that its reported cost matches the recorded one.
3. Count evaluations against the budget, including calls before and after the search.
4. Rerun with the same seed in two fresh processes.
5. Measure the share of repeated evaluations.

The tool `research/integrity_audit_tool.py` performs these steps for any optimizer through a small adapter. It
returns a non-zero exit code on a problem, for use in CI.

## 10. Data and code availability

All material is in `owlCoder/gadapt`, directory `research/`:
- protocols: `ITERATION49_PROTOCOL.md`, `ITERATION50_PROTOCOL.md`, `ITERATION51_PROTOCOL.md`;
- eligibility and documentation quotes: `ITERATION50_ELIGIBILITY.md`;
- code: `iteration49_integrity_audit.py`, `iteration50_integrity_audit.py`, `iteration51_d3x.py`;
- raw outputs, with `pip freeze` per library: `results/iteration49–51/`;
- disclosure drafts and patches: `iteration49_nevergrad_1572/`, `iteration50_disclosure/`;
- the practitioner tool and its tests.

## References (DOIs verified on Crossref, arXiv on arxiv.org, 2026-10-23)

- de Nobel, J., Ye, F., Vermetten, D., Wang, H., Doerr, C., Bäck, T. (2024). IOHexperimenter: Benchmarking platform
  for iterative optimization heuristics. *Evolutionary Computation*.
  [10.1162/evco_a_00342](https://doi.org/10.1162/evco_a_00342)
- Hansen, N., Auger, A., Ros, R., Mersmann, O., Tušar, T., Brockhoff, D. (2021). COCO: a platform for comparing
  continuous optimizers in a black-box setting. *Optimization Methods and Software*.
  [10.1080/10556788.2020.1808977](https://doi.org/10.1080/10556788.2020.1808977)
- Hansen, N., Ros, R., Mauny, N., Schoenauer, M., Auger, A. (2011). Impacts of invariance in search: When CMA-ES and
  PSO face ill-conditioned and non-separable problems. *Applied Soft Computing*. [10.1016/j.asoc.2011.03.001](https://doi.org/10.1016/j.asoc.2011.03.001)
- Kudela, J. (2022). A critical problem in benchmarking and analysis of evolutionary computation methods. *Nature
  Machine Intelligence*. [10.1038/s42256-022-00579-0](https://doi.org/10.1038/s42256-022-00579-0)
- Ravber, M., Šmid, M., Moravec, M., Mernik, M., Črepinšek, M. (2025). Performance comparison of single-objective
  evolutionary algorithms implemented in different frameworks. *Informatica*.
  [10.15388/25-INFOR603](https://doi.org/10.15388/25-INFOR603)
- Vermetten, D., van Stein, B., Caraffini, F., Minku, L., Kononova, A. (2022). BIAS: a toolbox for benchmarking
  structural bias in the continuous domain. *IEEE Transactions on Evolutionary Computation*.
  [10.1109/TEVC.2022.3189848](https://doi.org/10.1109/TEVC.2022.3189848)
- Duque-Torres, A., Klammer, C., Fischer, S., Pfahl, D., Ramler, R. (2025a). Assessing the strength of metamorphic
  testing applied to optimisation software: experience from industry. *Information and Software Technology*.
  [10.1016/j.infsof.2025.107807](https://doi.org/10.1016/j.infsof.2025.107807)
- Duque-Torres, A., Klammer, C., Fischer, S., Ramler, R., Pfahl, D. (2025b). Metamorphic testing for optimisation: a
  case study on PID controller tuning. *Information and Software Technology*.
  [10.1016/j.infsof.2025.107872](https://doi.org/10.1016/j.infsof.2025.107872)
- Rounds, J., Kanewala, U. (2018). Systematic testing of genetic algorithms: a metamorphic testing based approach.
  arXiv:1808.01033 (preprint, no DOI).
