# Preregistered scientific validation plan — GAdapt infrastructure robustness

Status: **research protocol / not a dissertation result**.
Repository base: `bpzoran/gadapt@8825da180377cb231d4751c08108a8149269ffc1`.
Branch: `research/robust-diversity-baseline`.

## Research question

Can a diversity-guided evolutionary optimizer be made significantly more
stable, more reproducible, and more reliable at finding *feasible* solutions
on infrastructure optimization tasks, under matched computation budgets?

The first candidate improvement is a positive-affine-invariant cost spread
metric. It addresses two documented numerical pathologies of a baseline
diversity signal, but is **not sufficient by itself** to claim a new
state-of-the-art evolutionary method.

## Target properties and falsifiable claims

H1: Holding fixed the same initial population and random seed, changing
`f(x)` to `a * f(x) + b`, with `a > 0`, does not materially change
the optimization trajectory for the affine metric. Test with exactly
representable and ordinary floating-point transforms; record numeric error.

H2: The affine metric can recover a positive diversity value when
the initial generation has identical costs and a later generation
contains different finite costs. This is a unit-level property.

H3 (not yet established): On original GAdapt, the candidate metric
has lower 90th/95th-percentile optimization regret or failure risk
than the unchanged baseline on sufficiently many held-out cases.

H4 (not yet established): On independent network powerflow test cases
and load conditions, a modified GAdapt achieves at least the baseline
physical feasibility rate, subject to similar objective evaluation count.

H5 (not yet established): Improvements generalize to a second
infrastructure domain (e.g. telecommunications traffic routing or
water distribution), without parameter re-tuning on the test cases.

## Required independent data and out-of-domain testing

1. Reproduce known mathematical benchmark behaviour (COCO/BBOB or CEC)
   at 2, 7, 20, 40+ dimensions. Mark these as optimization benchmarks,
   NOT direct industrial validation.
2. Validate grid physics using AC solver(s) on published IEEE14/118 cases.
   Report exact solver versions, controls, voltage/thermal limits.
3. Validate on documented RTE-origin offline snapshots
   (`case1888rte`, preferably multiple snapshots if feasible).
   These datasets are unsuitable for operating real grids.
4. Obtain independently sourced operational logs/telemetry from a real
   infrastructure operator under suitable authorization. Separate
   training / tuning / test by time period and site. No deployed claim
   without this.
5. Reserve at least one wholly unseen infrastructure problem family
   for the final test; never optimize parameters using held-out results.

## Experimental design (to be executed; do not report as done)

- Baseline: unchanged GAdapt; ablations: new cost diversity only,
  constraint-handling only, robustness/restart only, and combinations.
- Competitors: SciPy DE, CMA-ES when applicable, and a mathematical
  industry-standard solver for each constrained task.
- Independent seeds: target 50–100 per (task, condition, optimizer),
  with a preregistered power analysis for rare failures.
- Match *actual* objective calls including validation/setup calls,
  or compare at explicit fixed evaluation budgets on every curve.
  Separately compare wall-clock time.
- No silent discard of failures: count non-convergence, NaNs, timeouts,
  physical violations, and complete optimizer failures in denominators.
- Record bounds, load factor, generator availability, constraint
  tolerances, baseline feasibility, and exact numerical solver settings.
- The final candidate must be re-simulated with the optimization output
  outside the optimizer's fitness/penalty cache.
- For each case: median regret, worst-decile regret, failure probability,
  median time/evaluations to hit target, feasibility rate, and constraint
  violation. Report confidence intervals.
- Compare paired seeds with Wilcoxon sign-rank when justified and use
  Holm adjustment for multiple comparisons; report practical effect sizes
  and negative results.
- Evaluate scenario/shift/noise sensitivity on independent held-out sets.
- Prevent leakage: tune parameters only on development cases;
  freeze parameter configuration before final held-out evaluation.

## Baseline system limitations to study

- Legacy log-based cost diversity depends on additive cost offsets.
- Initial zero cost spread makes the relative legacy signal unusable
  once later cost spread is nonzero.
- The opt-in half-range alternative is sensitive to outliers,
  floating-point cancellation at huge offsets, and the inability to
  set a relative scale if the initial spread is zero.
- Original `GA` does not expose a general hard-constraint API.
- Direct callback exceptions and nonfinite objective outputs require
  standardized error classes, telemetry and fail-safe handling.
- The public API has no explicit per-run seed; global RNG resets
  are not safe for concurrent industrial applications.
- 'Successful optimization' is not the same as a validated feasible
  electrical or telecommunications operating state.
- Some original experiment comparisons match *generations*, not
  exact number of objective function evaluations.

## Engineering acceptance gates

A. Deterministic reproducibility within recorded software versions,
   logging of every run and reason for failed output.

B. Software checks: CI on >=3 Python versions, numerical edge tests,
   independent AC simulator validation, meaningful negative cases.

C. Statistical evidence: no regression in held-out feasibility and
   meaningful robustness improvement versus unchanged baseline.
   Thresholds/alpha and failure definition fixed *before* seeing results.

D. Deployment safety: operator review, domain simulator cross-check,
   monitoring, safe fallback, time/resource budget and rollback plan.

**Passing A and B alone does NOT establish C or D. No model should
directly control critical infrastructure based on these tests.**

## Published-source provenance

- GitHub project: https://github.com/bpzoran/gadapt
- MATPOWER RTE data description:
  https://matpower.org/docs/ref/matpower6.0/case1888rte.html
- Josz et al., AC Power Flow Data in MATPOWER and QCQP Format:
  iTesla, RTE Snapshots, and PEGASE (2016), arXiv:1603.01533
- pandapower published power-system test networks:
  https://pandapower.readthedocs.io/en/stable/networks/power_system_test_cases.html
- COCO benchmarking: https://coco-platform.org/
