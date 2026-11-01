# I65 — terminal witness lifecycle and exception fail-closed gate

**Date:** 2026-11-01  
**Review baseline:** `f27f418cd19d8688c5b91b2294e00e333ed9ddb2` (`owlCoder/gadapt` `main`).  
**Scope:** `research/i65/audited_budget.py` only; research-only software instrumentation, **no new optimizer policy, COCO confirmation, GAdapt default change or archived result rewrite**.  
**Verdict:** **PASS** for isolated terminal-witness lifecycle and the complete I65-only Python regression; full-clone and scientific I65 gates remain **NOT_TESTED / NO-FREEZE**.

## Red test — defects reproduced in the exact baseline source

Verified the original local file with `git hash-object audited_budget.py` = `6c2c930ea006e0bc0bd6bdcaba1c181c1dba39e1`. A deterministic adversarial case used `B=6`, first search objective `f([2])=4`, and a separate lambda returning the same objective. After `verify()` returned `VALIDATED_WITNESS` at physical attempt **2**, `b([1])` was erroneously allowed at attempt **3**, changing `b.best` from `4` to `1`. This violated the semantic boundary of a *final* independently checked candidate and could contaminate a final validated result if consumers continued using the same evaluator.

A second case: when a charged witness callback raised `BudgetReached`, the existing `evaluate()` correctly logged a physical failed attempt but `verify()` only caught `Exception`; since `BudgetReached` inherits `BaseException`, it escaped without `INVALID_RESULT` classification. In contrast, ordinary `ArithmeticError` was handled. **New lifecycle regression before the fix: 12 failed, 2 passed** (not a full optimizer benchmark).

## Narrow fix

- **Seal search as soon as any witness/recheck physical call has begun**, including an early valid witness, mismatched witness, nonfinite witness, ordinary exception or internal `BudgetReached` exception. All non-`recheck` phases now raise the existing `BudgetReached` control signal **without consuming another call** once `self.checked` is true. The complete trace hash, incumbent and `best_at` remain stable. The witness itself counts as a physical attempt within B.
- Inside `verify()`, catch `(Exception, BudgetReached)` and return `INVALID_RESULT / recheck_exception` with `error_type`. This does **not** catch `KeyboardInterrupt` or `SystemExit`, and preserves the outer driver's `BudgetReached(BaseException)` boundary on normal budget exhaustion.
- Failed *preflight* (bad bounds, invalid evaluator, etc.) does not invoke a witness and does not seal search. `reserve_witness=False` continues to allow exactly B ordinary search calls.
- A caller who bypasses `verify()` and manually calls `evaluate(phase='recheck', evaluator=...)` still gets a charged raw value and a sealed ledger, **not** an independently `VALIDATED_WITNESS` status. Only `verify()` performs the comparison/status step. No claim of independent physical-model provenance is made merely from callable identity.

Source Git blob **after** fix: `01a7defc70fadb6253de312cb46c07cd885139c9`. New adversarial test module blob: `cd83d13a036ccf2f796475ac868aa1c5c9b268b7`. Both new GitHub blobs were independently checked against `git hash-object` of the exact locally executed files.

## Local green test — actual isolated execution

Temporary SHA-matched `research/i65` sources; **not a complete migrated GAdapt clone**. Python `3.13.5`, NumPy `2.3.5`, SciPy `1.17.0`, pytest `9.0.2`. Command:

```sh
python -m pytest -q -rx test_audited_budget.py test_audited_budget_preflight.py \
    test_audited_budget_lifecycle.py test_i65_instrumentation.py \
    test_scipy_de_adapter.py test_stagnation_checked.py
```

**88 passed, 3 xfailed in 2.03 s**. This is a **14-test increase** over the prior isolated `74 passed / 3 xfailed` suite, not performance evidence. The exact short console log is archived at [I65 witness lifecycle test log](I65_WITNESS_TERMINAL_TEST_LOG_2026-11-01.txt), SHA-256 `6aef1f9d9ff214ae711e103475973df84fbad15f4598190131c62957bfec73c5`. SHA-256 of the patched `audited_budget.py` = `cdeb6d4165d57fc05d62c4d323fb01f57910c0de8779d3d512c0783a3029d9ce`; test file = `0466b29369703636b5fe0e7678b2f4e5e68cf405ef6c36eddb51054cbed5cda3`.

Three pre-existing **expected negative** reference tests persist, unchanged: old monitor permits nonmonotone timestamps; historical I64 budget undercounts callback exceptions and records mutated vectors after the call. No optimizer experiment, `make_gate_fixtures.py`, CI workflow, or COCO held-out evaluation was run.

## Scientific boundary and next gate

The I65 DRAFT specifies a *final* independent recheck, including early stopping for policy A. The fix ensures a terminal `verify()` cannot be followed by more search using the same ledger. **Unresolved interaction for proposed policy C:** the DRAFT also mentions a *validated GAdapt warm start* before switching to CMA. That must **not** reuse this final/terminal witness without an explicitly specified separately charged *inter-stage* oracle call and budget/accounting rules. Do not implement it or claim a validated switch until a reviewed protocol makes this distinction. A different callable is not automatically an independent ORPD/COCO evaluator.

The correct next physical execution gate is still a **pinned Python 3.12 full clone**, running the committed Git-tree provenance check, 341-alias opt-in restore and inexpensive I41/I63/I64 tests plus a full I65 rerun. The sandbox still cannot resolve `github.com` for `git clone` and lacks `cma/cocoex`, so **full migrated runtime, official f21/f24 oracle, actual nested power-flow solver-call accounting and scientific contribution novelty are NOT_TESTED/NOT ESTABLISHED**. The I65 policy-C experiment remains **DRAFT / NO-FREEZE / NOT_RUN**.
