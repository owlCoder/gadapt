# Reliability development loop state

This file records **engineering progress**, not optimizer benchmark results.

- Scope: `owlCoder/gadapt`; original research archive and upstream untouched.
- Goal: improve the rate of feasible, problem-specific acceptable outcomes under a fixed, correctly counted evaluation budget.
- Scheduled cadence: hourly (Europe/Belgrade); automation is managed in ChatGPT.
- Scheduled cycles completed: **11**.
- Additional engineering-cycle goal requested 2026-11-05: **1,000 new verified cycles**, excluding the first four scheduled cycles.
- Additional verified cycles completed after that request: **11 / 1,000** (four user-triggered, seven scheduled; reviews count only when actually completed and documented).
- Additional verified cycles remaining: **989**.
- Consecutive scheduled cycles without verified progress: **1**.
- Strategy-change threshold: **10** consecutive non-progress cycles.
- Current strategy: identify and fix one measurable reliability defect per cycle; back it with deterministic regressions and full Python 3.10–3.12 CI.
- Evidence required for progress: verified bug fix, green regression, or relevant new reproducible technical finding. A commit alone is not progress.
- At threshold: stop repeating fixes in the same family, explicitly record why attempts failed, and adopt a different technical hypothesis.
- Never run optimizer benchmarks, PF/AC/OPF, held-out COCO, or unapproved objective experiments. Follow `AGENTS.md`.

## Cycle journal

Use one dated entry per scheduled run: verified change/commit, test/CI URL, result (`progress` or `no_progress`), and updated consecutive no-progress count. Do not claim experimental optimizer superiority from synthetic unit tests.

### 2026-11-05 — scheduled cycle 1

- Finding: the optional deterministic evaluation cache used `float(value).hex()` for all `Real` inputs. Distinct integers `2**53` and `2**53 + 1` convert to the same binary64 float, potentially returning the wrong cached objective without a physical evaluation. Extended-precision NumPy scalars can have the same issue.
- Fix: exact keys for built-in integers, floats (hex preserves signed zero), and booleans; bypass caching for other scalar types instead of using a lossy conversion. Legacy defaults and the opt-in nature of caching are unchanged.
- Regression: test distinct >53-bit integers and extended-precision scalar bypass, plus the full deterministic suite. No optimizer benchmarks or unauthorized evaluations.
- Pull request: https://github.com/owlCoder/gadapt/pull/24
- CI: https://github.com/owlCoder/gadapt/actions/runs/41931528105 (all three Python versions green).
- Result: **progress**, verified green CI on Python 3.10–3.12 and merged as `c9ae851e4919d78963913dd1c627200e9d133509`; consecutive no-progress cycles: **0**. This is a correctness fix, not evidence of improved optimizer success rate.

### 2026-11-05 — scheduled cycle 2

- Finding: `ReliabilityMonitor.__call__` forwarded user callback exceptions of types `AcceptableTargetReached` and `EvaluationBudgetExhausted` unchanged. Because cost finders and executor use those same classes as internal control signals, a callback could impersonate a verified acceptance or a genuine monitor budget stop.
- Fix: catch these two types specifically at the user-callback boundary, count the physical attempt as invalid, and translate them to a regular `ValueError` for the cost finder. Monitor-generated control signals outside the callback remain untouched. Legacy defaults and archive unchanged.
- Regression: deterministic integration tests for spoofed acceptance (unconstrained) and spoofed exhaustion (constrained), checking no false acceptance, exact attempted-call count, exhausted budget and no-valid-result status. No optimization benchmarks or unapproved objective experiments.
- Pull request: https://github.com/owlCoder/gadapt/pull/26
- Branch CI: https://github.com/owlCoder/gadapt/actions/runs/41939892985 (Python 3.10, 3.11, 3.12 green).
- Result: **progress**, verified CI and merged as `35577531f1e140cc976b4f876159fd61240f2e14`; consecutive no-progress cycles: **0**. This is a correctness and reporting fix, not measured optimization success improvement.

### 2026-11-05 — scheduled cycle 3

- Finding: for an unconstrained objective, a Python integer such as `10**400` satisfies `numbers.Real` but `float(result)` raises `OverflowError`. The monitor previously propagated this without recording an invalid result, stopping execution prematurely even with remaining evaluation budget.
- Fix: classify failed numeric conversion as an invalid charged attempt and let the existing cost finder handle the invalid output; opt-in reliability mode only, no legacy default changes.
- Regression: deterministic direct-monitor accounting test and an end-to-end recovery test where four overflowing results precede four valid results. Both verify exact budget accounting and no false incumbent. No optimizer benchmarks or unauthorized evaluations.
- Pull request: https://github.com/owlCoder/gadapt/pull/27
- Branch CI: https://github.com/owlCoder/gadapt/actions/runs/41940449771 (Python 3.10, 3.11, 3.12 green).
- Result: **progress**, verified branch CI and merged as `661ad3fd52d26ed65a4262e9c185eee305ef1619`; consecutive no-progress cycles: **0**. This is a correctness fix, not measured optimizer success improvement.

### 2026-11-05 — scheduled cycle 4

- Finding: Python `bool` subclasses `int` and satisfies `numbers.Real`. The opt-in monitor classified boolean objective returns as invalid, but returned the original boolean to the scalar cost finder, which accepted it as a finite numeric cost. This could falsely make an entirely invalid cohort look viable and prevent bounded invalid-population recovery.
- Fix: for boolean scalar objective results, return a nonfinite sentinel from the opt-in monitor while charging the attempted call as invalid. The existing scalar cost finder now rejects that candidate. Legacy execution remains unchanged.
- Regression: two deterministic end-to-end tests for an all-boolean fail-closed budget and recovery after four boolean returns, checking exact call counts and verified incumbent. No optimization benchmarks or unauthorized objective experiments.
- Pull request: https://github.com/owlCoder/gadapt/pull/28
- Branch CI: https://github.com/owlCoder/gadapt/actions/runs/41946740337 (all three Python versions green).
- Post-merge CI: https://github.com/owlCoder/gadapt/actions/runs/41946833100 (all three Python versions green).
- Result: **progress**, merged as `85a82439313256c0953160e4afe4a25b11e80fd2`; consecutive no-progress cycles: **0**. This is a correctness fix, not evidence of improved optimizer success rate.

### 2026-11-05 — user-triggered additional cycle 1/1000 (not a scheduled cycle)

- Finding: a finite favorable objective result could be reported as a feasible/acceptable solution even when the evaluated decision vector was outside the declared bounds, had nonfinite coordinates or the wrong dimensionality.
- Fix: opt-in monitor rejects illegal pre-callback decision-vector snapshots after charging the real objective attempt. Invalid candidates never become incumbents or deterministic cache entries. Reliability structural validation also rejects nonfinite bounds/step before validation probes; legacy behavior unchanged.
- Verification: four deterministic regression tests for unconstrained and constrained values, cache safety and invalid bound rejection. Full 136-test suite passed on Python 3.10, 3.11 and 3.12.
- Pull request: https://github.com/owlCoder/gadapt/pull/29
- CI: https://github.com/owlCoder/gadapt/actions/runs/41947800690 (all three jobs green after merge).
- Result: **progress**, merged as `66a0ec7c2e55ada9e323bd55a76ffbc043a9733b`. One additional verified cycle completed; original four scheduled cycles are not counted toward the new 1000-cycle target. Consecutive no-progress scheduled cycles: **0**. No optimizer benchmark or empirical success-rate claim.

### 2026-11-05 — scheduled cycle 5; additional verified cycle 2/1000

- Finding: the newly introduced opt-in decision-domain check used `float(value)` to compare the candidate to its declared bounds. Binary64 rounding can make distinct integers outside a bound appear equal to the bound, e.g. `float(2**54 + 1) == float(2**54)`. This could still admit an illegal candidate as an acceptable incumbent.
- Fix: use binary64 conversion only to reject nonfinite/overflowing coordinates, then compare the original `Real` coordinate directly against the original declared bounds, without precision loss. Legacy behavior, caching policy, and original research archive unchanged.
- Regression: two deterministic tests covering both sides of a large exact integer bound, constrained false feasibility, physical-call counts, and no invalid cache hits. The entire regression suite passed on Python 3.10, 3.11 and 3.12; no optimization benchmarks.
- Pull request: https://github.com/owlCoder/gadapt/pull/30
- Branch CI: https://github.com/owlCoder/gadapt/actions/runs/41953953562 (all three Python jobs green).
- Post-merge CI: https://github.com/owlCoder/gadapt/actions/runs/41954035396 (all three Python jobs green).
- Result: **progress**, merged as `f04a6bfd1414e4a5a11666362fda9c78cd9d4e0f`. Scheduled cycles: **5**; additional verified cycles: **2/1000**; consecutive scheduled cycles without progress: **0**. No empirical optimization-success claim.

### 2026-11-05 — scheduled cycle 6; additional verified cycle 3/1000

- Finding: `parse_pair` converts constrained objective and violation values to binary64. A strictly positive finite `Fraction(1, 10**400)` violation becomes `0.0` after conversion; without an opt-in guard, an infeasible point could be reported as feasible and acceptable.
- Fix: the reliability monitor now compares the original positive violation to its converted value and rejects positive-to-zero underflow as an invalid charged attempt. The constrained cost finder receives a nonfinite sentinel and cannot record a false feasible incumbent. The legacy pair parser and GA defaults remain unchanged.
- Regression: deterministic direct-monitor and end-to-end GA tests verify false-feasibility prevention, physical-call counts, invalid classification, and bounded recovery. Full 140-test suite passed on Python 3.10, 3.11, and 3.12; no optimization benchmarks.
- Pull request: https://github.com/owlCoder/gadapt/pull/31
- Branch CI: https://github.com/owlCoder/gadapt/actions/runs/41959886004 (all three Python jobs green).
- Result: **progress**, merged as `13bd32afabbcb5bc1f540a72abb044817cdefaf2`; scheduled cycles: **6**; additional verified cycles: **3/1000**; consecutive scheduled no-progress cycles: **0**. This proves a correctness regression was fixed, not improved empirical optimizer success rate.

### 2026-11-05 — scheduled cycle 7; additional verified cycle 4/1000

- Finding: binary64 conversion can underflow a strictly positive scalar objective (or the objective component of a constrained pair), such as `Fraction(1, 10**400)`, to `0.0`. The opt-in monitor previously recorded this as a valid zero-cost incumbent and could falsely certify `acceptable_cost=0.0`.
- Fix: reject strictly positive objective-to-zero underflow as an invalid, charged evaluation in both monitored paths; preserve exact physical-call accounting, fail closed at the cost-finder boundary and exclude invalid results from the optional deterministic cache. No legacy default or original archive changes.
- Regression: three deterministic tests for unconstrained and constrained monitor acceptance/cache safety and bounded GA recovery. Full 143-test suite green on Python 3.10, 3.11 and 3.12.
- Pull request: https://github.com/owlCoder/gadapt/pull/32
- Branch CI: https://github.com/owlCoder/gadapt/actions/runs/41965761991 (all three Python jobs green).
- Result: **progress**, merged as `d03c3dc2613e5d0cd82bede8ccebf2379b201067`; scheduled cycles: **7**; additional verified cycles: **4/1000**; consecutive scheduled no-progress cycles: **0**. This is a correctness regression fix, not evidence of better empirical optimization success rate.

### 2026-11-05 — scheduled cycle 8; additional verified cycle 5/1000

- Finding: the positive-only objective-underflow guard added in scheduled cycle 7 did not cover a strictly negative nonzero Real such as `Fraction(-1, 10**400)`. Conversion to binary64 yields `-0.0`; the monitor previously recorded a fabricated zero-valued incumbent, distorting the reported objective, ranking, and optional cache. This is a distinct signed-underflow correctness issue, not evidence of any optimizer performance advantage.
- Fix: reject any **nonzero** exact objective converted to binary64 zero in both scalar and constrained opt-in reliability paths. Charge each real callback exactly once and exclude invalid outputs from the incumbent and cache. Legacy GA defaults, upstream and archived research remain unchanged.
- Regression: three deterministic tests for negative scalar and constrained underflow, cache exclusion, exact physical call counts, and bounded invalid-population recovery. Full **146-test** suite green on Python 3.10, 3.11 and 3.12.
- Pull request: https://github.com/owlCoder/gadapt/pull/33
- Branch CI: https://github.com/owlCoder/gadapt/actions/runs/41972090297 (all three jobs green).
- Post-merge CI: https://github.com/owlCoder/gadapt/actions/runs/41972169734 (all three jobs green).
- Result: **progress**, merged as `f7c6b567d98e0cd38a799ee19e3920b3570e279c`; scheduled cycles: **8**; additional verified cycles: **5/1000**; consecutive scheduled cycles without progress: **0**. No unapproved optimizer benchmarks or empirical optimization-success claims.

### 2026-11-05 — user-triggered emergency cycle; additional verified cycle 6/1000 (not scheduled)

- Trigger: user reported apparent five-hour lack of work. Automation audit confirmed the task ran successfully in its separate task history; its latest visible run was 05:07–05:09 UTC on 2026-11-05 (scheduled for 05:10 UTC). Automation delivery status was `unknown`, so no claim is made that notifications reached the user.
- Finding: high-precision `Real` objective values just above the declared acceptable threshold can round to the same binary64 value as the threshold, falsely marking an unacceptable result as accepted. Conversely, a later truly acceptable value can round to a tie and be overlooked.
- Fix: monitor tests quality using the original numeric result and the user's original declared threshold. Exact acceptance breaks ties between otherwise equal rounded objective values; physical-call budget and cached numeric result behavior stay unchanged. Legacy optimizer unchanged.
- Regression: 3 deterministic tests of precise scalar values, constrained values, exact threshold precision, cache safety, and end-to-end GA false acceptance. 149 tests green on Python 3.10, 3.11 and 3.12; no optimization benchmark.
- Pull request: https://github.com/owlCoder/gadapt/pull/34
- CI: https://github.com/owlCoder/gadapt/actions/runs/41978896396 (all three Python jobs green after merge).
- Result: **progress**; merged as `dfed0784381b368631e7f27492ea7fb15614b098`. Scheduled cycle count unchanged at **8**; additional verified cycles now **6/1000**; consecutive scheduled no-progress **0**. Objective reporting continues to use binary64 approximation, not exact rational objective serialization.

### 2026-11-05 — scheduled cycle 9; additional completed review cycle 7/1000

- Review: re-read `AGENTS.md`, `RELIABILITY_ROADMAP.md`, `ARCHIVE.md`, and current `main` state. Audited the just-merged exact-acceptance fix against the acceptance contract: rounded objectives are not exact acceptance certificates; cached early stopping depends on validated `_best_target_met` state; and equal binary64 objectives must not conceal a precisely acceptable incumbent. The new deterministic regressions cover these cases. No distinct new reproducible defect was established; PR #34 is counted as a fix only in the earlier emergency cycle, not again here.
- Evidence: https://github.com/owlCoder/gadapt/pull/34 merged at `dfed0784381b368631e7f27492ea7fb15614b098`; https://github.com/owlCoder/gadapt/actions/runs/41978896396 passed Python 3.10–3.12.
- Result: **no_progress** (completed technical review; no separate fix). Scheduled cycles **9**; additional completed review/fix cycles **7/1000**; consecutive scheduled cycles without verified progress **1**. Change strategy after 10 consecutive no-progress scheduled cycles. No unauthorized benchmarks or claims of empirically improved optimization success.

### 2026-11-05 — scheduled cycle 10; additional verified cycle 8/1000

- Reviewed current `main` and `AGENTS.md`, `RELIABILITY_ROADMAP.md`, `ARCHIVE.md`, and this ledger before the change.
- Finding: distinct precise finite `Real` values can narrow to identical binary64 floats. Even after the exact acceptance fix in PR #34, the reliability monitor still compared rounded values when choosing the best evaluated incumbent. It could therefore discard a strictly better feasible scalar/constrained objective, or a strictly smaller positive constraint violation, whenever both rounded to the same float.
- Fix: keep private original numeric objective and violation values for the incumbent ordering decision, while preserving the public binary64 result contract, deterministic cache and exact objective-call accounting. No change to legacy defaults, upstream, or archive.
- Regression: 3 deterministic tests covering scalar objective, constrained feasible objective and constrained infeasible violation, including a cache hit and physical evaluation counts. **152 tests** green on Python 3.10, 3.11 and 3.12; no optimizer benchmark.
- Pull request: https://github.com/owlCoder/gadapt/pull/35
- Branch CI: https://github.com/owlCoder/gadapt/actions/runs/41985757409 (all three Python jobs green).
- Post-merge CI: https://github.com/owlCoder/gadapt/actions/runs/41985850809 (all three Python jobs green).
- Result: **progress**, merged as `7ed65543a5b7568fc5c45dabc2c384340cba1036`; scheduled cycles: **10**, additional verified cycles: **8/1000**, consecutive scheduled no-progress cycles: **0**. Precise internal ordering does not make the public binary64 objective output exact and is not evidence of improved empirical optimization success rate.

### 2026-11-05 — user-triggered additional cycle 9/1000 (not a scheduled cycle)

- Finding: `ReliabilityMonitor` uses original precise `Real` values when choosing the best-ever evaluated objective/constraint violation, but its `completed_generation()` stagnation detector still compared binary64-rounded values. A strictly improving incumbent could be misclassified as stagnant, incrementing the refresh/restart debt and initiating disruptive reseeding unnecessarily.
- Fix: compute generation-level quality from the same original precise objective and violation values used by incumbent ranking. This is opt-in reliability behavior only; legacy defaults, original research archive, and upstream unchanged.
- Regression: two deterministic checks demonstrate reset of stagnant generation counters and refresh debt after strictly improving but identically rounded feasible objectives and infeasible violations. Full **154-test** suite green on Python 3.10, 3.11 and 3.12. No optimizer benchmark or external physical evaluation.
- PR: https://github.com/owlCoder/gadapt/pull/36
- CI: https://github.com/owlCoder/gadapt/actions/runs/41990717526 (all three Python jobs green after merge).
- Result: **progress**; merged as `f313265b01673e440bcc54ba84e754e8a430b683`. Scheduled cycles unchanged at **10**; additional verified cycles **9/1000**, consecutive scheduled no-progress **0**. This proves correctness only, not an empirical increase in optimization success rate.

### 2026-11-05 — scheduled cycle 11; additional completed review cycle 10/1000

- Inspected current `main` at `502edd8fabc3f84409fe06d9afd7e8cea91ee6ea` and re-read `AGENTS.md`, `RELIABILITY_ROADMAP.md`, `ARCHIVE.md` and this ledger. Reviewed the optional discrete-certification path (`gadapt/execution/discrete_certification.py`) against `DecisionVariable.make_random_value`, `ReliabilityMonitor` and `GAResults`.
- Concrete review: grid construction uses the same near-integer ratio rounding, upper-bound cap, and decimal rounding as the library's discrete random-value generator; duplicate or out-of-bounds rounded points fail closed to stochastic GA. Exhaustive absence is only marked when all grid points were attempted and the monitor recorded zero invalid evaluations; budget refusal and timeout do not certify absence. The grid's proof remains conditional on a stationary deterministic objective and correct declared domain. No separate reproducible defect was established in this review, so no implementation PR or duplicate fix was counted.
- Existing verification evidence: https://github.com/owlCoder/gadapt/actions/runs/41990861105 (154 tests green across Python 3.10, 3.11 and 3.12 on the current implementation before this ledger-only change). No new optimizer benchmark, objective evaluation or physical experiment was run. No algorithmic performance inference.
- Result: **no_progress** (completed technical review, not a new defect fix). Scheduled cycles **11**; additional completed review/fix cycles **10/1000**; consecutive scheduled cycles without verified progress **1**. Change technical strategy after 10 consecutive no-progress scheduled cycles. Legacy defaults, upstream and historical archive untouched.

### 2026-11-05 — user-triggered additional cycle 11/1000 (not a scheduled cycle)

- Finding: with default boundary validation probes, the first probe may already be a verified feasible solution at or below the acceptance threshold. The validator still performed the opposite-boundary objective call, unnecessarily spending one expensive physical evaluation even though the required quality was achieved.
- Fix: only in opt-in reliability mode, skip the second boundary objective probe if the first has already met the monitor's verified target; do not skip structural checks. The opposite boundary is still evaluated when the first probe is not acceptable. Legacy mode unchanged.
- Regression: four deterministic tests for unconstrained and constrained first-probe acceptance, continued probing when needed, and structural-invalid fail-closed. Updated previous two-probe assertion; full **158-test** suite green on Python 3.10, 3.11 and 3.12 after correcting one mistaken test expectation (invalid structural settings are rejected before any objective call).
- Pull request: https://github.com/owlCoder/gadapt/pull/37
- Post-merge CI: https://github.com/owlCoder/gadapt/actions/runs/41993441073 (all three Python jobs green).
- Result: **progress**, merged as `c1604ee21a6b06c8ed6695584cc03f1a594ab753`. Scheduled cycle count stays **11**; additional completed cycles become **11/1000**; scheduled no-progress streak stays **1** (only scheduled cycles change that counter). No optimizer performance benchmarks or empirical claims.
