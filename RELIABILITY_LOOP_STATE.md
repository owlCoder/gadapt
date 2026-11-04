# Reliability development loop state

This file records **engineering progress**, not optimizer benchmark results.

- Scope: `owlCoder/gadapt`; original research archive and upstream untouched.
- Goal: improve the rate of feasible, problem-specific acceptable outcomes under a fixed, correctly counted evaluation budget.
- Scheduled cadence: hourly (Europe/Belgrade); automation is managed in ChatGPT.
- Scheduled cycles completed: **1**.
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
