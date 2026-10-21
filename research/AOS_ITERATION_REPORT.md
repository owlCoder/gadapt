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

Source: https://github.com/owlCoder/gadapt/actions/runs/39563682707
SHA of this run: `135bdc23419b7d16b7a628bdf4272c73cc5a891c`
(its feasibility callback originally returned a large finite penalty for
post-budget candidates; later code now uses `None` to explicitly withhold
credit for those non-evaluations; rerun should replace these numbers as the
final implementation's pilot).

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
median computation time ranged roughly 2.02–2.14 sec and the recorder
reports additional *post-budget objective requests* (GA 16 aggregated per
condition vs SciPy DE 280 per condition). These requests returned a sentinel
without physical solve: they are distinguished from actual PF calls.
Feasibility callback attempted to read 9 uncached samples at 100% and 8
at 110% in the initial pilot. This is a **real measurement-accounting
defect**, now explicitly skipped in the implementation; cannot claim
clean feasibility learning from the older run.

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
