# I65 — adversarial preflight validation of research-only evaluation budget

**Date:** 2026-11-01  
**Status:** isolated instrumentation defect reproduced and locally tested; `I65 DRAFT / NO-FREEZE / NOT_RUN`.  
**Scope:** research-only `research/i65/audited_budget.py`, **not** `gadapt/`, official COCO, CMA switching, or any new optimizer experiment.  
**Baseline GitHub `main`:** `34aa515c1c3c224d602ab92fd9338130b0fc2ce0`.  
**Baseline audited evaluator Git blob:** `cc3a6e78f8b2d1e5b043e5d6216826368d6d495e`.  
**Validated patched evaluator Git blob:** `6c2c930ea006e0bc0bd6bdcaba1c181c1dba39e1`.  
**New regression test Git blob:** `a1cd77c2ceda49e2f458e73f0e677bcd20b6a595`.  
**Existing SciPy DE smoke-test blob, unmodified:** `fe22edbe0a0530bef44c7da0f4fcbd49d3678e68`.

## 1. Motivation: reproduce first, repair second

The published isolated sequential evaluator was reconstructed as a local **byte-identical Git blob** (`git hash-object` matched `cc3a6e78`). An adversarial preflight tested finite input, valid box bounds, and finite nonnegative `atol`/`rtol`. **10 of 13 initial parameterized checks failed on the unmodified source.** Those failures are software-validation findings, not COCO benchmark data.

Specifically:

1. `_snapshot()` accepted `NaN`/`±Inf` decision coordinates. An objective returning a finite value at such an invalid coordinate could generate a search incumbent and (if box checking did not catch it) a purported `VALIDATED_WITNESS`. Invalid coordinates could also make `trace_hash()` reject the non-JSON-compliant trace.
2. `verify()` compared bounds without a finite/shape/order check. `NaN` bounds can make comparisons silently false; extra dimensions may broadcast, and `[-Inf, +Inf]` passes without certifying finite domain limits. In the original source, several such cases produced `VALIDATED_WITNESS`.
3. `verify()` accepted `rtol=Inf` (and some invalid other tolerances), allowing incorrect independent values to appear close. Tolerances are now validated before performing a physical witness attempt.

These were **not** demonstrated on the historical I64 objectives or actual ORPD data; they cannot be used to retroactively invalidate previous scientific findings.

## 2. Narrow research-only fix

- Reject all nonfinite decision coordinates before invoking any objective. Invalid API input therefore does **not** consume a physical evaluation, while an actual invoked callback still reserves an attempt *before* calling it.
- Require a box `bounds=(lo,hi)` to have exact candidate dimension, finite endpoints and `lo ≤ hi`. Invalid boxes yield `INVALID_RESULT / invalid_bounds`, before consuming the reserved independent-witness attempt.
- Require finite, nonnegative numeric `atol` and `rtol`; invalid values raise `ValueError` before witness execution.
- Preserve the existing finite-input optimization trace, witness comparison for valid inputs, one-slot reservation, `BudgetReached` semantics and exception accounting. No GAdapt default, algorithm, SciPy baseline, frozen source, historical result or CI workflow was edited.

**Important boundary:** `verify()` still checks only that the witness is a distinct callable, not an independently certified simulator or physical oracle. Full independence, domain-specific feasibility and nested real power-flow solver-call accounting remain separate unresolved gates.

## 3. Actual local test execution (not a full repository clone)

Environment: container Python **3.13.5** (the project declares Python 3.12), `numpy 2.3.5`, `scipy 1.17.0`, `pytest 9.0.2`. `cma` and `cocoex` are **not installed**.

The following **SHA-matched** source was tested in an isolated local directory:

- Modified `audited_budget.py`, Git blob `6c2c930e`.
- New `test_audited_budget_preflight.py`, Git blob `a1cd77c2`.
- Existing unchanged `test_scipy_de_adapter.py`, Git blob `fe22edbe`.

Command:

```sh
python -m pytest -q test_audited_budget_preflight.py test_scipy_de_adapter.py
# 22 passed in 0.36s
python -m compileall -q audited_budget.py test_audited_budget_preflight.py
# exit 0
```

**22/22 PASS** consists of 20 parameterized adversarial/preflight regression cases plus two existing real SciPy DE smoke tests (initial population/partial generation and charged callback/replay). The original full `54 passed / 3 xfailed` I65 historical report is not a new execution result and is **not claimed to have been rerun** in this environment.

## 4. Remaining blockers and reproducibility gate

A complete local repository checkout was **not obtainable**: `git ls-remote https://github.com/owlCoder/gadapt.git HEAD` returned `Could not resolve host: github.com`. Consequently all of the following remain **NOT_TESTED** in this session: 341-path physical restore, legacy I41/I63/I64 tests, full I65 suite, pinned Python 3.12 runtime, GAdapt completed-generation integration, CMA ask/tell, official COCO f21/f24/optimum verification and independent ORPD feasibility oracles. No expensive CI or confirmatory optimizer benchmark ran.

On a real pinned local checkout, run the [read-only Git-tree checker](compat/check_migration_git_tree.py), then opt-in root-alias restoration according to [compatibility instructions](compat/README.md), then the historical inexpensive test suite. Specifically add:

```sh
python -m pytest -q -rx research/i65/test_*.py
```

Preserve the original `xfail` findings as such; on an unexpected regression record a BLOCKED gate, not fabricated success. Obtain independent review of the source and the tests before approving I65 freeze.

**Decision:** research-only input/witness-preflight unit gate **PASS in the isolated test environment**; full-clone regression and true independent oracle **NOT_TESTED**. Candidate C originality `novelty not established`, I65 `NO-FREEZE / NOT_RUN`.
