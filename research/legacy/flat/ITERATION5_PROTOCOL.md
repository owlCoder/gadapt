# Iteration 5 — budget-matched local refinement and near-optimality audit
Date: 2026-10-21. **Frozen before the experimental program was written/executed.**
Direct development in `owlCoder/gadapt:main` by explicit owner authorization. `bpzoran/gadapt` remains unchanged.

## Target research question
The previous credit-based UCB/paired-credit mechanisms were not demonstrably superior
and spent a large fraction of the *physical* evaluation budget on controls.
Test whether a simple, known **memetic** (GA + local search) approach provides
a better accuracy/reliability trade-off in an exactly counted IEEE14 nonlinear
AC generator-voltage setpoint benchmark. This is a strong existing-method
baseline, not proposed as an original dissertation contribution.

Published optimization research on IEEE14 reactive power dispatch reports
lower losses under *different control variables/constraints* (e.g. JAYA,
DEPSO). Those published MW figures must **not** be compared numerically to
this narrower 5-variable, fixed tap/shunt/active-generator IEEE14 problem.
A local minimum, even with tiny apparent improvement, is NOT a certified
global optimum. We do not use PYPOWER `runopf` as an interchangeable global
optimum because its decision variables/objective differ.

## Frozen comparison and resource budget
Reference: GAdapt real installed package + PYPOWER `case14`, PV/slack voltage
setpoints with the exact physical voltage, reactive power and existing RATE_A
constraints defined in `research/ieee14_voltage.py`. Load factors 1.00 and
1.10. Seeds 100–111 (12 fixed paired trials per method per load; distinct from
prior 0–7). Budget: exactly 360 *true PYPOWER runpf executions per trial*.
Population 24, GA->local hybrid split: 180 GA physical evaluations followed
by up to 180 local-search evaluations. One genuine PF call is one unit, even
when objective is queried repeatedly. If a solver stops early, the unused
allocation is spent on explicitly labelled restarts/random-search fills.
All post-budget solver requests are recorded, never run physically, and
cannot improve the physical incumbent.

Methods:
- `legacy_gadapt`: standard unmodified GAdapt with 360 PF evaluations.
- `affine_gadapt`: opt-in affine cost diversity only, 360 PF evaluations.
- `slsqp_multistart`: scipy.optimize.minimize(SLSQP) initialized from
  published reference plus seeded randomized restarts, bounded voltage
  setpoints, **penalized** objective and independent feasibility auditing.
  This is NOT an AC-OPF solver nor a feasibility-guaranteeing SLSQP.
- `hybrid_gadapt_slsqp`: original GAdapt for 180 PF calls, then starts
  SLSQP from the BEST physically evaluated feasible state if one exists,
  else from the best penalized state; seeded bounded restarts to exhaust
  the full 360-call total. GA and SLSQP see the same objective, constraints
  and physical counter; no hidden optimizer calls.
- `scipy_de`: differential evolution with 360 PF evaluations, polish off.

Primary exploratory outcome: physical feasibility fraction including all
failed/invalid run statuses; among successful physically feasible runs report
true loss MW, median and 90th percentile, worst observed. Paired outcomes:
feasible beats infeasible, lower feasible loss beats higher feasible loss, both
infeasible ties; exact sign test and Holm correction for 4 comparisons
against `legacy_gadapt` per load. Additional paired feasibility discordance
exact test, conditional paired median difference with bootstrap 95% interval.
Log physical solver count, total requests, time, restarts and wasted
post-budget calls, seed, environment. Report partial runs as failures.

**Predeclared decision rule:** n=12 is an exploratory mechanistic pilot.
No statistically confirmed superiority or rare-event reliability claim
will be made without an independent, adequately powered replication and
larger cases (IEEE118, RTE) plus non-grid domain. Full blown AC OPF / global
optimality certification is NOT addressed.

## Frozen secondary cross-domain probe: GÉANT (NOT a new holdout)
The archive had already been inspected in iterations 2–4. We use exactly
the prior 12 training and 32 later evaluation snapshots, with SHA256
verification and a scaling factor calibrated exclusively on earlier traffic.
Hence **no claim of independent temporal test**.

Methods: `legacy_gadapt`, `coordinate_multistart`,
`hybrid_gadapt_coordinate` and `scipy_de`; seeds 100–107, each
with 360 true objective evaluations, population 36; 180/180 split for hybrid.
The local search changes one published integer route weight by randomly
chosen +/-1, +/-2, +/-4, or +/-8 (clipped to bounds), accepts ONLY a strict
training-cost improvement, and restarts after 3*n unsuccessful attempts.
Control local search uses seeded random initial route-weight vectors.
This is a standard discrete coordinate hill climber, not novel.
All temporary objective calls and early stops are counted; postbudget
requests never improve the saved plan. Evaluate the physically recorded
best development plan on the unmodified test block only after optimization.
Primary exploratory metric: all-44-period installed capacity module
cost, failure counted; the held-out August cost is secondary and
previously inspected. Paired rank exact p with Holm across three
comparisons against legacy, n=8 no confirmatory superiority.

## Frozen non-comparable high-budget best-known-feasible reference
To measure *distance from a credible achieved reference*, independently
run one deterministic, reproducible 3600-solver-call search per IEEE14
load (1.00 and 1.10): 2000 true AC-PF calls with SciPy DE, then 1600
true AC-PF calls with multistart SLSQP initialized from the best
physically feasible control, or the best penalized vector when no feasible
control exists. Fixed seed `20261021`. Check the final chosen voltage
vector by a fresh independent PYPOWER solve **outside** the search budget,
report the extra verification call transparently. This returns only an
EMPIRICAL BEST-KNOWN FEASIBLE objective from these searches — NOT a lower
bound or globally certified optimum. Do not use the result for tuning any
earlier fixed-budget method; absolute loss gaps are descriptive only.

## Frozen CMA-ES supplemental benchmark (separate run)
Use public `pycma` ask/tell covariance matrix adaptation as a stronger
existing black-box baseline (CMA-ES is well established, NOT new).
For IEEE14 loads 1.00 and 1.10 use exactly the same 12 seeds (100–111)
and 360 real AC-PF calls per trial as the five-arm primary pilot.
Population lambda=8, initial standard deviation 0.035 p.u., initial mean
the published case generator-voltage vector clipped into declared bounds.
If the strategy terminates early, restart from best actually observed
penalized vector with sigma=0.035; any remaining evaluations are genuine
random physical samples, all explicitly marked. Objective, independent
feasibility and PF counter match original pilot. This is a separate
exploratory control, with no new claim of statistical validation.
