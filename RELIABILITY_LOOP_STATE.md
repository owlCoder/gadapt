# Reliability development loop state

This file records **engineering progress**, not optimizer benchmark results.

- Scope: `owlCoder/gadapt`; original research archive and upstream untouched.
- Goal: improve the rate of feasible, problem-specific acceptable outcomes under a fixed, correctly counted evaluation budget.
- Scheduled cadence: hourly (Europe/Belgrade); automation is managed in ChatGPT.
- Scheduled cycles completed: **3**.
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
