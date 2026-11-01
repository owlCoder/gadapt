# I65 — Final instrumentation technical gate (research sandbox)

**Date:** 2026-11-01. **Status:** the restricted local instrumentation gate passed; the integration/freeze gate **was not completed**. New confirmatory optimization results: **0**. This work did not modify the GAdapt library, `owlCoder/gadapt` or upstream `bpzoran/gadapt` at the time of this report.

## Executed tests: raw fixtures and verifiable traces

Running `python -m pytest -q -rx` under `research/i65/` (Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2) produced **54 passed, 3 xfailed**; log: `I65_GATE_TEST_LOG.txt`. This includes new and earlier I65 tests dated 2026-11-01, with no GAdapt/CMA/COCO optimizer evaluations. `I65_INSTRUMENTATION_FIXTURES.json` holds small deterministic traces for exact-budget accounting, exceptions, mutable inputs and 20-generation stagnation. Every synthetic objective in the fixtures serves only to test instrumentation.

### Confirmed limitations of the old I64 reference code

1. **Evaluator raising an exception:** `research/i64/e_common.py` reserves/increments a call **after** the objective returns successfully. In a synthetic test, two actual attempted calls that raise `ArithmeticError` leave `Budget.n == 0`. This is a physical-call accounting defect in the presence of exceptions, **not evidence that such exceptions occurred in earlier I64 optimizer experiments**.
2. **Mutation of the input vector:** with an objective that mutates its argument, the old I64 `Budget` records the already-mutated input (`[999]` instead of `[2]`). There is no evidence that the studied functions actually mutated their inputs, but instrumentation must retain the original candidate even when the objective is impure.
3. **Monotonicity of `nfev` in the early I65 reference stagnation monitor:** the original `StagnationMonitor` accepted a decreasing evaluation count. This is a defect in an isolated I65 reference, **not in `gadapt/`**.

All three are covered by intentionally expected-failing regression tests (`xfail(strict=True)`); an accidental change to the historical test semantics requires review.

## Implemented exclusively in the research sandbox

- `audited_budget.py`: `AuditedBudget` reserves `attempts` **before** a physical invocation; snapshots the candidate before possible mutation; separates `finite/nonfinite/exception` outcomes; records `init/search/probe/callback/restart/polish/recheck` phases; retains the global incumbent with a real call count; `BudgetReached(BaseException)` prevents a hidden B+1; reserves one unit of B for a distinct final independent evaluator. A witness call **does not modify** the search incumbent or time-to-target trace.
- `stagnation_checked.py`: exactly 20 **completed** generations without significant improvement; strict criterion `delta > eps_abs + eps_rel * max(1,abs(previous))`; monotonic `nfev`; no repeated stagnation event until a significant improvement or restart. Restart does not delete the global incumbent.
- `test_scipy_de_adapter.py`: exercised an actual SciPy differential-evolution call with 12 initialization candidates, one additional evaluation before the search stops at B−1 (B=14), followed by one independent witness. An additional objective call from a callback is explicitly charged; deterministic replay with the same `rng` produced the same trace hash. SciPy's `tol` was **not** treated as a stagnation rule.
- `test_stagnation_checked.py`: compared 1,000 deterministic synthetic sequences against an independently written reference recurrence, with no discrepancies. This is **not** independent human code review or proof of a GAdapt integration.

## Mathematical budget-bound check

Let `n_0 = 0` and B be a finite positive integer. In a sequential evaluator, the algorithm checks `n < limit` before reserving an attempt. Only if the check succeeds is the call allocated index `n+1`; the objective is called afterward. Induction over admitted attempts gives `0 <= n <= limit <= B`, and no evaluator invocation occurs after reservation B. An exception does not roll the counter back. This reasoning applies to **sequential, one objective invocation = one physical evaluation**. It does not automatically apply to vectorized or parallel evaluators or to an objective that invokes multiple underlying power-flow solver calls.

## What the gate did not cover

- `gadapt`, `cma` and `cocoex` were unavailable in the local Python environment; no test covered a real GAdapt generation, a CMA `ask/tell` cycle or an official Gallagher/Lunacek instance. Installation from the network was unavailable. No default bit-identity replay of the GAdapt library was conducted.
- No independent code review was performed. `stagnation_checked.py` is a reference only, not an adapter to real optimizer generation boundaries. Underlying solver calls cannot be accounted for automatically without dedicated adapters.
- The `verify()` API can require a different Python callable but cannot by itself demonstrate independence of the simulation model; that needs two independent implementations/oracles or independent review.
- The stagnation detector intentionally does not count failed/incomplete generations. A GAdapt adapter must explicitly report a completed generation, rather than a generic callback that might run before completion.
- No success rate, COCO CVaR or ECDF can be scientifically calculated from these tests. Such quantities must be `NOT_MEASURED`.

**Decision:** **GO** for external instrumentation review; **NO-FREEZE / NO-CONFIRMATORY-RUN** for I65 until the formal `AGENTS.md` novelty gate, independent review and real integration tests are satisfied.
