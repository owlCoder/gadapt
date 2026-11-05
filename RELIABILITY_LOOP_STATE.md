# Reliability development loop state

This file records **engineering progress**, not optimizer benchmark results.

- Scope: `owlCoder/gadapt`; original research archive and upstream untouched.
- Goal: improve the rate of feasible, problem-specific acceptable outcomes under a fixed, correctly counted evaluation budget.
- Scheduled cadence: hourly (Europe/Belgrade); automation is managed in ChatGPT.
- Scheduled cycles completed: **6**.
- Additional engineering-cycle goal requested 2026-11-05: **1,000 new verified cycles**, excluding the first four scheduled cycles.
- Additional verified cycles completed after that request: **3 / 1,000** (one user-triggered, two scheduled).
- Additional verified cycles remaining: **997**.
- Consecutive scheduled cycles without verified progress: **0**.
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
