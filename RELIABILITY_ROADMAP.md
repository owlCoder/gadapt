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
