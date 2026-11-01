# Exploratory (NOT preregistered): SciPy global optimizers tested with the execution-integrity audit tool

**Date:** 2026-10-23. Tool: `research/integrity_audit_tool.py`; call budget 1,000; N ∈ {2, 10}; three seeds; environment from `h4_requirements_lock.txt` (SciPy 1.18.1). Outputs are `<optimizer>.json` in this directory.

| Optimizer | Observation | Documentation | Classification |
|---|---|---|---|
| `dual_annealing` | C4 in 1/18 runs (at most 1,050 calls) | `maxfun`: "Soft limit ... will be exceeded ... just after the local search is done" | Documented |
| `shgo` | C4 in 18/18 runs (up to **5,131** calls for `maxfev` 1,000) | `maxfev` is exact only for some local methods; otherwise checked at global-iteration boundaries | Documented, but up to 5× |
| `direct` | C4 in 6/18 runs (at most 1,013 calls) | `maxfun`: "Approximate upper bound" | Documented |
| `basinhopping` | R3 in 3/18 runs, only on a plateau | "`lowest_optimization_result` will only be updated if a local minimization was successful." | Documented |

`basinhopping` uses the same policy as `differential_evolution`: a failed local minimization can invalidate an otherwise better solution, but `basinhopping` documents that behavior. This was added as a comment on [SciPy #26479](https://github.com/scipy/scipy/issues/26479); no new issue is needed. `basinhopping` has no direct evaluation-budget argument, so C4 does not apply to it.
