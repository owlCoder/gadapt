# I65 — instrumentation validation (isolated reference tests, 2026-11-01)

**Scope:** The original repository was not modified during this initial validation. An isolated `i65/` package contained a byte-identical copy of GitHub's `research/i64/e_common.py` (Git blob SHA `3aab99773a7e4a95b7972a3c8061c50bd471618d`), a reference stagnation state machine and unit tests. The original `Budget` and a separately proposed stagnation monitor were tested, **not all GAdapt/DE/CMA/COCO integration paths**. These are not confirmatory results or independent human review.

**Execution:** `python -m pytest -q test_i65_instrumentation.py`, in `research/i65/`.

**Outcome:** `12 passed, 2 xfailed` (intentionally expected-failing regression cases). No optimization experiments were run and no GitHub commits/pushes were made at the time of this initial report.

| Check | Outcome | What was checked / limitation |
|---|---|---|
| `Budget`: B/B+1 | PASS | The Bth evaluation is allowed; B+1 is rejected. `BudgetReached` derives from `BaseException`. |
| Physical probes, duplicates, callbacks | PASS (direct test) | Every successful invocation through the wrapper was counted. This does not demonstrate that all real library callbacks use that wrapper. |
| Invalid `nan/±inf`, ties | PASS | Nonfinite values are counted but cannot become the best finite witness; on equal costs the first input remains. |
| `deepcopy` | PASS | The wrapper returns the same object instance, relevant when GAdapt clones its objects. |
| STAGNATION after exactly 20 generations | PASS — reference | A stagnation event fires only after 20 **completed** generations, not during an incomplete generation. |
| Strict `delta > eps_abs+eps_rel*max(1,abs(previous))` | PASS — reference | A tie is not significant; significant improvement resets the counter. |
| Restart, global incumbent, variable generation lengths | PASS — reference | Restart resets the stagnation counter but retains the global incumbent; events record the actual `nfev`. |
| Seed replay of the reference state machine | PASS — reference | The same seed yields the same event hash. This does not cover real `GA.execute()` or SciPy runs. |
| Original call counter on exceptions | **XFAIL — discovered gap** | `Budget.__call__` computes `v=float(self.g(y))` before `self.n+=1`. A raised exception leaves the actual physical attempt unrecorded. Without fail-safe behavior resources might be reused. |
| Original witness with mutable input | **XFAIL — discovered gap** | `best_y` is copied only after `g(y)`. An evaluator that mutates the input can change the recorded witness. There is no evidence this affected the previously used I64/COCO-style functions. |

## Proposed remedies — not implemented in the production repository at the time of this report

1. Reserve an `attempt_id` and increment `attempted_physical_evaluations` **before** calling the evaluator. Separately count `returned_finite`, `returned_nonfinite`, `raised_exception`, `invalid_decoding`, and `completed`. Every attempted call consumes budget B even if an external solver raises or stops. In batched/asynchronous evaluation, require idempotency and unique probe IDs.
2. Snapshot the input `x_pre` before invocation. Save that exact candidate and its cost for the incumbent; independently verify cost by a second evaluation path. Physical validation/witness calls must use a reserved slot within B, or be explicitly counted as a separate disclosed verification budget, never hidden inside a claimed `B=12k` result.
3. Instrument a real GAdapt *completed-generation* event in an adapter (the default `exit_check` is not equivalent). Use SciPy DE's `callback(intermediate_result=...)` without an additional `func(x)`, or count any such callback evaluation. Perform CMA `ask/tell` only after a fully evaluated batch. A partially evaluated generation at the B boundary is not a completed generation for stagnation purposes. Library `success=True` is not a substitute for validated solution quality.
4. Before FREEZE, add real integration tests for GAdapt/DE/CMA, including B−1/B/B+1, `max_calls=1`, no improvement, negative/nonfinite costs, mutated witnesses, callbacks, two-process deterministic replay, restart population initialization, independent witness and default behavior bit-identity hash. `cocoex` and `cma` were not installed in the available sandbox; these gates were therefore **not satisfied**.

## What was not established

There was no independent code review, no integration test of a real algorithm switch, no official COCO f21/f24 instance evaluation, and no replay of prior I64 results in this session. The status remained **NO-FREEZE / NO-RUN** for major confirmation. The two XFAIL cases do not establish that earlier scientific findings were compromised, but they are blockers that must be addressed before a new confirmatory experiment.
