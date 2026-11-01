# I65 — full isolated Python regression after evaluator preflight hardening

**Date:** 2026-11-01  
**Working tree boundary:** a temporary directory holding SHA-matched I65 Python files only; **NOT** a full cloned `owlCoder/gadapt` checkout.  
**Source commit inspected:** `be0ecfea3b9a16d7dad52e3e4f8970cb68a76ce5` on `main`.  
**Decision:** **PASS for the complete I65-only pytest collection; NOT_TESTED for real-clone and optimizer-integrated gates.**  
**I65 research status:** `novelty not established / DRAFT / NO-FREEZE / COCO NOT_RUN`.

## What actually ran

After a bounded set of 35 local input/preflight and SciPy DE tests, we added the original SHA-identical `stagnation_checked.py` and its original tests: **49 passed** in the intermediate run, including the seeded 1,000-reference-trace recurrence check. We then reconstructed all nine Python dependencies/test modules needed by the `research/i65/test_*.py` suite from GitHub. For each local file, `git hash-object` matched its GitHub blob SHA at the inspected commit:

| Local file | Git blob SHA |
|---|---|
| `audited_budget.py` | `6c2c930ea006e0bc0bd6bdcaba1c181c1dba39e1` |
| `e_common_snapshot.py` | `3aab99773a7e4a95b7972a3c8061c50bd471618d` |
| `stagnation_checked.py` | `985b7fa6bd1e834219fa7867dbd00e87e418cb19` |
| `stagnation_reference.py` | `2177f8844245114ea69f6ece86a7ab5307f5edbd` |
| `test_audited_budget.py` | `d7d713eed5325f287ec00069ae354c5fe3f25de5` |
| `test_audited_budget_preflight.py` | `a1cd77c2ceda49e2f458e73f0e677bcd20b6a595` |
| `test_i65_instrumentation.py` | `d7e3b16161aa57fa65f2113f3b8804eb9769062b` |
| `test_scipy_de_adapter.py` | `fe22edbe0a0530bef44c7da0f4fcbd49d3678e68` |
| `test_stagnation_checked.py` | `fc9ecca100157bdfe7b59afe6645721e8239b2e4` |

Command run in the temporary I65 directory (not in the full repository):

```sh
python -m pytest -q -rx \
  test_audited_budget.py test_audited_budget_preflight.py \
  test_i65_instrumentation.py test_scipy_de_adapter.py test_stagnation_checked.py
```

**Result:** `74 passed, 3 xfailed in 2.07s`; no failure and no unexpected pass. The three expected failures are *valuable preserved negative evidence*, not opt-in fixes:

1. `test_original_monitor_rejects_nonmonotone_timestamp`: the old `StagnationMonitor` reference omits a monotonic timestamp check. The newer `CheckedStagnation` does validate it.
2. `test_original_budget_counts_failed_evaluation_attempts`: the old I64 `Budget` increments after the callback returns, thus undercounts exceptions; `AuditedBudget` reserves before invoking the objective.
3. `test_original_budget_snapshots_witness_before_evaluation`: the old I64 `Budget` snapshots input after a mutating callback, which can record the wrong candidate; `AuditedBudget` snapshots before invocation.

This is a **20-pass increase** from the archived original `54 passed / 3 xfailed` suite following the added adversarial input/witness tests; it is not evidence of optimization performance improvement.

## Reproducibility and trace archive

- Runtime: Python `3.13.5`, NumPy `2.3.5`, SciPy `1.17.0`, pytest `9.0.2`.
- [Original complete console output and file hashes](I65_ISOLATED_REGRESSION_TEST_LOG_2026-11-01.txt) (short test log with all three xfail reasons, file SHA map, and exact executed command).
- SHA-256 of log file: `1f373248e34a285a5750e3f4ca7ccd7ecdd5df36880c6f7f19ba26690ce9be7b`.
- No optimizer benchmark was executed. The SciPy DE smoke tests exercise real SciPy code on trivial synthetic objectives; they do not constitute physical ORPD or COCO validation.
- This proof applies to the SHA-matched source files listed above; it does **not** imply that omitted scripts or packaged dependencies of the full repository work. `make_gate_fixtures.py` was not executed because it writes an archived fixture file and is not part of pytest collection. One extra exploratory `test_preflight_adversarial.py` was run locally during the intermediate 49-pass check, but **it is not a tracked I65 test file and is excluded from the reported 74/3 suite**.

## Still required before any scientific claim

The environment cannot resolve `github.com` from `git clone` / `git ls-remote`, has no full repository checkout, uses Python 3.13 instead of pinned 3.12, and lacks `cma` and `cocoex`. Therefore **the 341-alias physical restore, legacy I41/I56/I61/I63/I64 regression, actual GAdapt generation callbacks, CMA ask/tell, COCO f21/f24 optimum and strong independent ORPD witness remain NOT_TESTED**.

On the project's locked Python 3.12 real clone: (1) run [Git-tree gate](compat/check_migration_git_tree.py), (2) run opt-in [legacy-root restore](compat/README.md), (3) run cheap legacy checks, (4) rerun `python -m pytest -q -rx research/i65` and store `pip freeze`/exact commit and logs, and (5) seek independent supervisor review of novelty and statistical protocol.

**Do not** modify frozen historical reference implementations solely to eliminate their expected-negative tests, and do not launch held-out COCO, expensive experiments or CI while I65 is `NO-FREEZE`.
