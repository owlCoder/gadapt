# Iteration 6 — larger AC network and evaluation-budget controller
**Registered: 2026-10-21, before benchmark code and performance measurements.**
Owner-authorized development: `owlCoder/gadapt:main`, NEVER `bpzoran/gadapt`.

## Preliminary feasibility audit (separate from optimization)
[Verified CI diagnostic](https://github.com/owlCoder/gadapt/actions/runs/39580915103):
`pandapower==2.14.11`, public `case118` with first eight `net.gen`
voltage setpoints (0.95–1.08 p.u.), load multipliers 1.0 and 1.1.
Published generator setpoints and three low-amplitude seeded perturbations
were all independently convergent and feasible (voltage/thermal criteria
implemented by `GridProblem`): initial losses 132.5253 and 173.4263 MW.
French `case1888rte` converged at 100% load but had pre-existing
severe normalized violations (~16.27, peak loading ~209%). This test case
cannot be used to assert full feasibility without addressing baseline
violations / missing control freedoms; report violations separately.

## Hypothesis and prior art
Known memetic algorithms and adaptive local-search budget allocation
preclude claiming that switching from GA to SLSQP is a new general
algorithm. The following *experimental heuristic* is one transparent
progress/feasibility-aware budget controller, NOT yet an original
doctoral algorithm:

Start actual GAdapt on 25% of the evaluation budget, which is inspected
only at generation boundaries. At the end of its first generation AFTER
that threshold:
- no physically feasible individual found so far -> permit GAdapt to
  consume 75% of total budget, leaving 25% for local search;
- feasible found AND relative feasibility-conditioned progress from the
  12.5% checkpoint is >= 0.002 -> target GAdapt 55%, local 45%;
- feasible but progress < 0.002 -> stop GAdapt at 30%, give remaining
  70% to local search.

If the GA generation crosses its target, stop at the next generation
boundary; **actual PF calls** (not planned shares) define the final
split. All subsequent SLSQP calls must be charged to the total budget
without hidden physics or imputed post-budget scores.
When the GA cannot produce a feasible vector, local search starts from
the *best physically evaluated penalized candidate*. An independent
feasible-best recorder tracks every actual physical call including
local tests, never a wrapped post-budget sentinel. Method names:
`gadapt_legacy`, `slsqp_multistart`, `hybrid_fixed_half`,
`hybrid_adaptive`, `scipy_de`, `cma_es`. Adaptive fraction is
frozen here, with no tuning to IEEE118 outcomes.

## Frozen larger-model pilot
- `GridProblem(case="ieee118")`, 8 continuous PV generator setpoints,
  actual pandapower Newton-Raphson AC powerflow with reactive limits
  enforced, bus voltage and thermal constraints independently checked
  for each physical call.
- Two load multipliers: 1.0 and 1.1.
- Seeds 200..205 (6 paired seeds), 180 genuine PF evaluations per
  optimizer run, population 24. These are **new seeds** versus the
  earlier 100..111 IEEE14 runs; IEEE118 is still a public reference
  benchmark, not operational data.
- Fixed hybrid: 90 true GA evaluations then 90 true SLSQP evaluations.
  Adaptive controller obeys frozen 25%-probe / 30%-55%-75% split.
- CMA-ES: popsize=8, sigma=0.035, initial published voltage vector,
  existing package `cma>=4,<5`. SciPy DE popsize >=5, polish=False,
  no local `polish` outside budget.
- All methods use identical fixed-box bounds (0.95, 1.08), objective
  penalizing physical violation by 1e5, and **exactly 180 genuine**
  pandapower PF calls. Each requested but rejected cost function call
  is tracked and cannot update best solutions. If an algorithm stops
  early, charge leftover evaluations to clearly labeled random fills.
  Each candidate's feasibility is checked from actual PF output, not
  inferred from the penalty value.
- Outcome priority: fraction of runs with a physically feasible
  incumbent (failures included), then median loss MW conditional on
  feasibility, 90th percentile and worst observed. Report minimum
  violation when no feasible candidate exists. Paired ranking:
  feasible beats infeasible; less physically feasible loss wins; both
  infeasible tie. Compare each of five methods against original GAdapt;
  exact sign p and Holm correction, Wilson feasibility CIs, paired
  medians and bootstrap uncertainty. Also compare adaptive vs fixed
  and vs SLSQP explicitly (secondary, labeled exploratory).
- n=6 is a MECHANISTIC feasibility/transfer pilot, **not
  confirmatory significance or tail-risk reliability evidence**. No
  threshold adjustment based on evaluation data before a future
  independent confirmatory replication.
- Published `case118` is standardized with some data corrections;
  it does not imply production-grade operating limits, N-1 security,
  optimal active dispatch, or a certified OPF solution.
- RTE1888 is reserved for a clearly labeled separate stress test
  of measured residual infeasibility; first fix/characterize infeasible
  baseline and constraints before claiming feasible optimization.

Relevant sources:
- https://pandapower.readthedocs.io/en/v2.14.11/networks/power_system_test_cases.html
- https://doi.org/10.23919/CSMS.2024.0006 (existing adaptive memetic methods)
- https://doi.org/10.1016/j.swevo.2024.101694 (existing learning-based memetic methods)

## Frozen RTE1888 stress-only addendum (before experiment)
Because the published French network is already severely infeasible
under the pre-existing first-eight-setpoint model and nominal load,
run a **minimal, purely exploratory constraint-reduction stress check**:
same `GridProblem("rte1888",1.0)`, methods `gadapt_legacy`,
`slsqp_multistart`, `hybrid_adaptive`, `scipy_de`,
seeds 300–302, population 12, 72 actual pandapower AC PF solver calls
per method-seed. This probes whether any method even finds independently
feasible voltages from only these 8 control variables. Record minimum
physical violation, best feasible MW only if one exists, all AC solver
failure counts, incumbent vectors, and explicitly that the baseline is
infeasible. Compare minimum violation *descriptively* if none is feasible;
doing so is NOT a feasible optimal solution or an independent
validated industrial OPF. This RTE subset has pre-existing line overload,
so the measured violation may represent unrepairable structural
constraints under voltage-only changes.

## Post-experiment reproducibility amendment — NOT a method change

After the **original unpinned** experiments were completed and reported,
a second independently successful workflow execution with identical source
and paired seeds produced *different final numerical values* despite
identical physical-call counts and identical adaptive decision classes.
Across two 72-trial executions, all 12 per-method IEEE118 feasible-loss
measurements changed to some degree: ~1e-12 MW for CMA-ES, <0.0003 MW
for SLSQP, but up to ~0.1–0.25 MW for GA/DE/hybrids. These facts preclude
bitwise reproducibility claims for the original unpinned workflows.
The original `research/results/ieee118_allocation_20261021.csv` and
original Actions run are kept immutable as provenance.

An independent diagnostic,
https://github.com/owlCoder/gadapt/actions/runs/39584533666,
pinned `PYTHONHASHSEED=0` plus `OPENBLAS_NUM_THREADS=1`,
`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`NUMEXPR_NUM_THREADS=1`. With identical package versions, it verified
matching SHA256 of the actual first 16 public IEEE118 AC inputs/results
and first 48 actual GA-proposed inputs/physics results
**across two independent GitHub Actions runners and within fresh
Python processes**. This local deterministic observation does not
prove the whole algorithm universally deterministic.

We therefore RETAIN the original hypotheses, objective, physical
limits, method family, sample size, seed list, paired statistical tests
and evaluation budget unchanged but repeat the *entire same experiment*
under the independently validated environmental controls.
The new raw CSV will be versioned separately, rather than silently
replacing any original trial, and results described as a reproducibility
sensitivity check, not a pristine independent data split.
French RTE1888 is repeated under the same controls; violation remains
the primary honest outcome when physical feasibility is absent.
