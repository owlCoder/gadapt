# GAdapt — mutation-credit AOS iteration 3: exploratory research report

**Date:** 2026-10-21
**Branch:** `research/feasibility-credit-aos`
**Base:** `research/robust-diversity-baseline@bd6bf78536e8026887f30288be5ff517303a5dc9`
**Status:** software research + small direct-GAdapt infrastructure pilots; **not a novel
proven algorithm or a dissertation-ready result**. Baseline branch and fork `main`
were not changed.

## Initial scientific question

Can choosing actual GAdapt mutation operators on the basis of *observed*
offspring utility and explicit physical violations improve reliability beyond
its fitness-spread/columnar-diversity heuristics?

Literature in `research/AOS_ITERATION_PROTOCOL.md` (AOS/UCB, dynamic bandits,
JADE, SHADE, constraint handling) demonstrates that reward-based operator
selection, success history and feasibility priorities are established
techniques. Our opt-in controller is a **diagnostic baseline, not a claim of
scientific originality**.

The original GAdapt composition randomly selects operators, but does not
measure their observed effects on subsequent feasibility or objective costs.
The range/affine-diversity correction alone did not transfer reliably between
IEEE14 and GÉANT. There are also confounders: crossover, parent quality,
partial mutations, near-duplicate solutions, and different numerical penalty
scales. Therefore, a calibrated, correctly attributed feasibility-aware
mechanism remains an OPEN *research* possibility, not an established
contribution.

## Exact changes

- `gadapt/ga.py`: optional `mutation_operator_policy` (default `legacy`;
  alternatives `uniform`, `ucb`), `mutation_operator_credit`
  (`objective` or `feasibility`), and
  `mutation_violation_function(values, penalized_cost)`.
  The callback is preserved by configuration clone. Legacy parameters remain
  unchanged.
- Factory/options/executor/cost finder integrate with real selected
  mutators, with trace reset before crossover, and credit assignment ONLY
  after evaluation. Trace and count operator selection, observation, positive
  credit, bounded 64-reward memory.
- `research/aos_ieee14_pilot.py`: PYPOWER full nonlinear AC powerflows,
  independent voltage/reactive/thermal feasibility checks and complete
  failure accounting, 240 *physical* evaluations for each algorithm.
  SciPy DE and four AOS-related ablations.
- `research/analyze_aos_ieee14.py`: Wilson 95%, conditional loss tails,
  paired wins/ties/losses, exact sign/McNemar, bootstrap interval and
  Holm adjustment. Infeasible trials are NOT removed from success rates or
  composite paired ranking.
- `research/aos_geant_temporal.py` and
  `research/analyze_aos_geant_temporal.py`: frozen 12+32 timestamp stress
  planning benchmark, archive hash-verified, development-only calibration.
  Objective-based AOS only; hard feasibility is *not fabricated* for a model
  whose capacity modules are unconstrained.
- Three-version regression tests and specialized CI; raw CSV/log/stat files
  stored as GitHub Actions artifacts.

## IEEE14 numerical pilot — actual completed run

Source (corrected no-physical-evaluation credit): https://github.com/owlCoder/gadapt/actions/runs/39564353477
Earlier uncorrected pilot: https://github.com/owlCoder/gadapt/actions/runs/39563682707
SHA of corrected run: `e51785314c650c2afda6717df2a468857b9d850b`
The first pilot returned a large violation for non-evaluated post-budget
requests. The corrected run instead returns `None` and withholds credit;
the output vectors and numeric medians were unchanged by this fix.

8 paired seeds × 2 loads × 6 methods × 240 physical PF solves.
Median loss is conditional on physically feasible runs only.

| Method | feasible at load 1.0 | median feasible MW | feasible at load 1.1 | median feasible MW |
|---|---:|---:|---:|---:|
| legacy | 8/8 | 14.251895 | 8/8 | 17.826047 |
| affine | 8/8 | 14.235920 | 7/8 | 18.196904 |
| uniform objective | 8/8 | 14.130644 | 8/8 | 17.546807 |
| UCB objective | 8/8 | 14.232898 | 8/8 | 17.875079 |
| UCB feasibility | 8/8 | 14.240617 | 8/8 | 17.986377 |
| SciPy DE | 8/8 | 14.255971 | 6/8 | 17.446616 |

All six methods used exactly 240 true PF evaluations in each run. Per-run
median computation time in the corrected run ranged roughly 1.31–1.39 sec and the recorder
reports additional *post-budget objective requests* (GA 16 aggregated per
condition vs SciPy DE 280 per condition). These requests returned a sentinel
without physical solve: they are distinguished from actual PF calls.
The corrected run logged 9 unscored feasibility callback requests at 100%
and 8 at 110%. The prior version's reward attribution was a **real measurement-accounting
defect**; those 17 physically missing post-budget observations now receive
no operator reward in the corrected run.

At 1.0, UCB feasibility vs legacy: 4 wins/4 losses; exact sign p=1.0,
Holm-adjusted p=1.0; conditional paired median difference -0.004794 MW,
bootstrap 95% [-0.135014, 0.185658] MW. No evidence of superiority.
At 1.1, UCB feasibility vs legacy: 4 wins/4 losses; exact sign p=1.0,
Holm-adjusted p=1.0; conditional paired median difference -0.011853 MW,
bootstrap 95% [-0.256865, 0.304904] MW. No evidence of superiority.

At 1.1, UCB objective vs legacy: 3 wins / 5 losses, exact sign p=0.726563,
Holm p=1.0. Uniform objective vs legacy: 5 wins / 3 losses, exact
sign p=0.726563, Holm p=1.0. Small pilot cannot establish tail reliability.
8/8 successes still give a wide 95% Wilson interval [0.6756, 1.0].
No cherry-picking: 'best-looking' uniform results are descriptive.

## CI process failure and research validity

One initial `Experimental IEEE14 mutation-credit AOS` Actions run at
https://github.com/owlCoder/gadapt/actions/runs/39563179818 was displayed
green even though its script crashed with `ModuleNotFoundError`:
the command piped output into `tee` and lacked `set -o pipefail`.
This is a **failed experiment** (zero valid pilot rows), *not* a success.
Fixes: sibling-module import, `pipefail`, require nonempty raw CSV, and
archive a separately generated statistical report.
A later temporary test-fixture error (mock missing `variable_id`) was
caught by regression CI and fixed; it does not imply a physical-model issue.
The current branch must be checked afresh for green regression runs.

## Pending independent engineering evidence

The 44-matrix chronological pilot is a separately frozen **within-archive**
time block. It cannot become an untouched, independent industrial-data
test merely because the evaluation timestamps differ from the earlier
August-15 sample. Archived traffic is anonymized and rescaled to engineering
modules using a single factor determined on earlier timestamps.

## Why this is not yet the dissertation result

The controller is an established AOS/UCB mechanism, and the observational
offspring reward confounds mutation effect with parent/crossover/other
operations. The negative/neutral small IEEE14 experiment gives no reason
to claim improved feasibility. Next: separate randomized mutation impact
from normal crossover in a fixed-evaluation experimental design (e.g.
assign mutator treatment by randomization to matched offspring; report
selection propensity and evaluate controls without budget inflation);
add consistent constraint-violation definitions per domain, alternative
credit scaling, nonstationary bandit comparator, JADE/SHADE, CMA-ES,
domain-specific AC-OPF, IEEE118/RTE multiple instances, true independent
temporal holdout and third infrastructure domain. Preregister independent
50–100+ paired runs/power analysis and worst-case quantiles before final
claim. No automatic critical-infrastructure control is justified.

**Current decision:** retain AOS as a *pilot research scaffold*. Neither
UCB-objective nor UCB-feasibility is a demonstrated replacement for the
original GAdapt. Any successor must be supported by stronger evidence or
the hypothesis must be rejected.


## Frozen GÉANT chronological pilot — actual completed run

Source: https://github.com/owlCoder/gadapt/actions/runs/39564291412
Benchmark SHA: `430bbeb0a746c0f9893c1b3d0a795bb6a30cf169`.
All 44 selected archive members were found, SHA256-verified and successfully
parsed: 12 development matrices from May/June/July plus 32 later August
evaluation matrices, frozen before execution. SNDlib historical archive SHA
`92d72a808d6de9d26be66844c098d3f32d5b9bb6c69af170e82b73118faef0df`;
network source SHA
`ff316c23220ff4485deafcb8701d49c353db0c80072152df3ed9023ed4b4f4ff`.
Calibration from development only: `49.569816117149394`.
The observed 15-minute traffic **is not original industry load in unscaled
absolute units**, nor is the modular plan an operator-approved engineering
design.

8 paired seeds × 5 methods × 240 true development objective calls.
All 40 method-runs completed successfully; all true evaluation counts=240.
Results below are in assumed SNDlib capacity-module *cost units*, not MW:

| Method | median training cost | median late-Aug cost | median 44-period plan cost | worst 44-period cost | median run time (s) |
|---|---:|---:|---:|---:|---:|
| legacy | 198585.0 | 159721.5 | 204067.0 | 221859.0 | 5.4822 |
| affine | 198329.5 | 159973.0 | 207516.5 | 224636.0 | 5.5065 |
| uniform objective | 194357.5 | 156292.5 | 195765.0 | 218723.0 | 5.5299 |
| UCB objective | 198997.0 | 157708.5 | 211204.0 | 222755.0 | 5.4868 |
| SciPy DE | 198974.5 | 158680.0 | 201612.5 | 218773.0 | 5.4327 |

Compared with paired legacy plans on 44-period cost:
- Affine: 2 wins, 4 losses, 2 ties; sign p=0.6875, Holm p=1.0.
- Uniform objective: **7 wins, 1 loss**; exact sign p=0.0703125,
  Holm p=0.28125. Median paired difference -2538.5, percentile-bootstrap
  95% [-16192, -934] cost units, secondary Wilcoxon p=0.078125.
  The bootstrap percentile interval excluding zero does **not** override
  the preregistered family of small-sample exact tests (bootstrap CI
  coverage at n=8 can be unreliable).
- UCB objective: **1 win, 7 losses**; exact sign p=0.0703125,
  Holm p=0.28125. Median paired difference +3174.0,
  bootstrap 95% [896, 9046], Wilcoxon p=0.1484375.
- SciPy DE: 3 wins, 5 losses; exact sign p=0.7265625, Holm p=1.0.

The **direction** of the UCB result is unfavorable on this frozen
historical scenario. An AOS policy using population-median offspring credit
is not validated and should *not* be proposed as a final replacement.
The uniform-control signal is worthy of independent replication, not
exploitation via post hoc cherry-picking. The model has no independent
hard feasibility criterion because capacity modules may increase without
bounds; thus only objective and temporal robustness are valid outcomes.

Benchmark objective budgets were identical, but the recorded count of
no-solver post-budget *requests* differed: 112 extra across 8 runs per GA
variant versus 960 for SciPy DE. They are NOT physical objective evaluations;
they must be reported whenever comparing computational overhead. The
holdout scoring itself entails additional independent evaluation of the
single selected plan against 32 archived matrices per run; it is identical
across methods and was not used for adaptation.

The correct scientific decision at the end of this iteration is
**not to accept UCB1 + observational offspring credit as an improvement**.
Future work should first isolate credit assignment causally or by randomized
matched offspring comparisons before adding further heuristics.

## Reproducible plots

The corrected GÉANT 44-period pilot was repeated with the plotting step and completed successfully at https://github.com/owlCoder/gadapt/actions/runs/39565100540 ; artifact https://github.com/owlCoder/gadapt/actions/runs/39565100540/artifacts/12329223499 includes raw CSV, console logs, statistical results, and `aos_geant_figure_all_44.png` / `aos_geant_figure_heldout_32.png`. All method medians and exact tests were reproduced; runtime medians on the second runner were ~2.83–2.92 s per method, versus ~5.43–5.53 s on the earlier runner. This reinforces that runner timings are hardware/noise dependent, **not** evidence of method speedup. Figure code is `research/plot_aos.py` and labels denominators explicitly.

## Archived primary results in the research fork

Authoritative original CI CSV, runtime logs, paired-statistics text and
graphical PNG distributions are in these successful Actions artifacts:
- [IEEE14, 96 trials and two labelled boxplots](https://github.com/owlCoder/gadapt/actions/runs/39565100519/artifacts/12329935661).
- [GÉANT, 40 trials and two labelled boxplots](https://github.com/owlCoder/gadapt/actions/runs/39565100540/artifacts/12329223499).

For protection against finite Actions artifact retention, all measured numeric
trial records were also committed in source control as
`research/results/aos_ieee14_20261021.csv` (96 records) and
`research/results/aos_geant_44_20261021.csv` (40 records). These were
recovered from the complete structured `RUN {...}` lines of the successful
corresponding CI logs and checked for correct run count, unique
method/seed/load keys, complete columns and exactly 240 true evaluations
per row. The original Actions CSV remains canonical for exact textual
reproduction (e.g., floating-number formatting); the committed copies
preserve the measured numeric values.

The plot-rendering CI was itself verified successful (with archive uploads),
including `aos_ieee14_figure_load_1p0.png`,
`aos_ieee14_figure_load_1p1.png`,
`aos_geant_figure_all_44.png`, and
`aos_geant_figure_heldout_32.png`.
