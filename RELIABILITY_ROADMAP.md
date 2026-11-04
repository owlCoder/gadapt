# GAdapt reliability-first development roadmap

**Status:** design and engineering plan only, 2026-11-04. No new optimizer,
benchmark, PF/AC/OPF, or COCO evaluation has been authorized or run here.

## Product objective

Make GAdapt return a **valid, sufficiently good solution as reliably as
possible within a fixed and auditable objective-evaluation budget**.
A stochastic optimizer cannot guarantee success on all possible problems.
Optimize the failure rate and the worst-tail quality before chasing record
best-case performance.

Success must be specified **per problem**: objective threshold, feasibility
tolerance, and evaluation/time limits. An exception-free GA execution,
`GAResults.success=True`, a warning-only timeout, or a historically recorded
`witness_checked` are not themselves evidence that the quality target was met.

## First engineering tasks (no new expensive experiments)

1. Inspect `gadapt/ga.py` defaults and `gadapt/operations/exit_check`.
   As archived, `exit_check=avg_cost`, `max_attempt_no=2`,
   `immigration_number=0`, `adaptive_immigration_patience=None` and
   `mutation_focus_generations=None`. The default exit may stop after
   two consecutive stalled average-cost checks. **This is a hypothesis,
   not a demonstrated cause of catastrophic outcomes.**
2. Define deterministic **unit and integration tests** for: unsuccessful
   objective evaluations; nonfinite values; feasible incumbent survival;
   stagnation and early termination; budget exhaustion; timeout;
   explicit output-status distinction; and exact accounting of every
   expensive evaluation, including objective validation probes.
3. Design an **opt-in** `reliability_mode` (name subject to review):
   fail-closed result status, always preserve best *evaluated* feasible
   incumbent, controlled stagnation detection, restart/immigration while
   retaining the incumbent, and an optional fallback strategy under the
   **same total** budget. These mechanisms are proposals, not existing
   verified features. Do not silently change legacy defaults or consume
   extra evaluations.
4. Evaluate reliability **only after** specifying problems, thresholds,
   baselines, paired seeds and budgets in advance, with user approval.
   Report `P(feasible and acceptable)`, failure rate, worst 10% gap,
   90th-percentile loss, tail/CVaR, anytime quality and cost. Compare
   against original GAdapt and strong reference algorithms at exactly
   equal true evaluation budgets. Audit random-seed independence and
   never select favorable seeds post hoc.

## Prior archived risk — not a universal GAdapt failure rate

On an earlier **fixed ORPD/I64-I2 historical comparison**, a selected
`case39/j=3` hybrid cell had three archived no-feasible runs among 30,
versus zero for IPOP. This was selected post hoc and is not general
evidence that the current package default fails 10% of the time.
Independent power-system feasibility review and the original R raw
source remain unavailable. See the preserved archive branch.

## Protected baseline and scope

As of this cleanup the untouched original research repository is preserved
at branch `archive/pre-reliability-cleanup-2026-11-04`, exact commit
`02ed2261397edb0b279f82f6e7af1271564ff579`.
Historical research, reproducibility receipts, frozen protocols and negative
results are **not destroyed**, just removed from the active `main` checkout.
No new experiment, physical solver, bootstrap, novelty claim, scientific
freeze or mentor signature was produced by this cleanup.

## Prospective benchmark proposal — NOT APPROVED, NOT RUN

The following is a **pre-run protocol proposal**, not observed performance.
Freeze it (including thresholds and source revisions) only after explicit
user approval. No benchmark objective, physical solver or held-out COCO
evaluation is authorized by this document.

All listed problems are deterministic minimizations. Accept iff a *real*
objective evaluation returned a finite value <= threshold, decision variables
are within bounds, and every specified violation is <= 1e-9. For the current
pair API, report nonnegative violation as 0 only when within that tolerance.
Budget B is an **upper bound on actual objective invocations**, including
validation probes, exceptions and all attempted candidates.

| ID | Exact problem, bounds | Acceptable threshold | B |
|---|---|---:|---:|
| R10 | 10D Rastrigin, each x in [-5.12, 5.12] | f <= 30 | 4,096 |
| A10 | 10D Ackley, each x in [-32.768, 32.768] | f <= 5 | 4,096 |
| RB10 | 10D Rosenbrock, each x in [-3, 3] | f <= 50 | 8,192 |
| L2 | 2D f=(x-2)^2+(y-1)^2, x,y in [-3,3], x+y<=2 | f <= 0.65 | 2,048 |
| C2 | 2D f=(x-0.8)^2+(y-0.8)^2, x,y in [-2,2], (x+0.5)^2+(y+0.5)^2 <= 0.09 | f <= 2.75 | 4,096 |
| F4 | 4D f=sum((x_i-0.25)^2), x_i in [-1,1]; objective deliberately raises on x_0<0, probe_cost_function=False | f <= 1.0 | 4,096 |

For L2 and C2, return `(f, max(0, constraint_residual - 1e-9))`
to `constraint_handling="feasibility_rules"`; independently log raw
constraint residual to prevent tolerance-adjustment mistakes.

**Preselected paired seeds:** integers 2026110400 through 2026110449
inclusive, all 50, with no replacements. For every configuration seed
Python's `random` and NumPy RNG; ensure independent program RNG state
per run, consistent problem instance and matching implementation settings.

**Fixed comparisons:**
1. Untouched GAdapt at cleanup commit `2a702a877e3fdece3af7bea1c0a3888fc5ff81ae`,
   with an externally enforced B-call wrapper and its original exit behavior.
2. GAdapt with `reliability_mode=True`, `max_evaluations=B`,
   `acceptable_cost=threshold`, other search settings unchanged.
3. Same reliability mode + the existing explicit
   `adaptive_immigration_patience=5`,
   `adaptive_immigration_percentage=20`,
   `adaptive_immigration_diversity_threshold=0.25` (ablation).
4. SciPy differential evolution, externally budget-limited, on all six.
5. CMA-ES with a fixed population-size rule and explicit bound repair on
   R10/A10/RB10/F4 only. No arbitrary penalty comparison for constrained
   problems.

Run each at exactly the same **maximum** call budget B, report **actual
spent calls** (early exit may spend less), and mark errors, timeout,
missing-feasible outcomes and prematurely exhausted bounds. Stop early at
the target where the algorithm supports it. All implementations must use
the same raw objective and independent instrumented reporting wrapper.
For F4 do not count an exception as a successful evaluation.

**Primary metric:** fraction of seeds meeting both strict feasibility and
the predeclared acceptable threshold, with paired differences and uncertainty
intervals. **Tail metrics:** no-feasible rate; catastrophic rate (not
acceptable); worst 10% of feasible objective gaps; 90th-percentile loss;
CVaR90 (mean of worst 10% losses); evaluation-count distribution and anytime
acceptable-rate curves. Predeclare a censored quality-loss convention for
no-feasible runs before running, and always report those events separately
so a finite imputation cannot conceal failures. Preserve all 50 individual
seed records, including negatives, and do not select seeds or tune thresholds
after seeing results.

In this first phase **no such runs have taken place**. This suite is a
candidate protocol; benchmark methodology and thresholds require user approval.
