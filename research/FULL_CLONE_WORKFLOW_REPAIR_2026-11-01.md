# GAdapt full-clone workflow #41357664531: verified failure and remediation

**Date:** 2026-11-01. **Target:** `owlCoder/gadapt`.  
**Run:** https://github.com/owlCoder/gadapt/actions/runs/41357664531  
**Head SHA:** `2af909634f62f1d5801dc113058531e2c15c90b5`.  
**Conclusion:** `completed / failure` after six of eleven core gate steps; **do not classify full I41/I63/I64/I65 integration PASS**.  
**Artifact:** https://github.com/owlCoder/gadapt/actions/runs/41357664531/artifacts/13103952516; ZIP SHA-256 `6a1831a0a93757f8aaf7e697569c40de164769ffe0efd553ee4a6358cce84e0d`. Individual `gate.json` log SHA-256 fields were validated against all six real archived logs (6/6 match).

## Verified concrete results — real 3.12 clone, not synthetic

- Checkout with complete original Git history **PASS**. Python `3.12.15` installed by `setup-python`.
- `01_compat_synthetic.log`: **25/25 unittest PASS** (including 341-scale synthetic Git tests and restoration tool validation). This is the result from the actual GitHub Actions runner.
- `02_git_tree.log`: **341/341 original-blob / canonical-blob / curated-symlink provenance PASS**, Git tree original `0e7cacda` and HEAD `2af90963`.
- `03_restore_preflight.log`: **341 checked, 341 planned, 0 created**, all hash verification enabled.
- `04_restore_apply.log`: **341 checked, 341 newly created**, hash verification enabled.
- `05_restore_idempotence.log`: **341 checked, 0 created, 341 existing**, hash verification enabled.
- `06_import_smoke.log`: **FAIL** with `ModuleNotFoundError: No module named 'numpy'`, triggered by use of the **system Python interpreter outside .venv**.

The report archive's `gate.json` explicitly confirms the first five PASS steps and import smoke FAIL. Actual historical I41/I63/I64 and I65 tests were **not yet reached**.

## Root cause (two independent defects)

**Runner interpreter:** `run_full_clone_gate.py` converted the requested `$GITHUB_WORKSPACE/.venv/bin/python` path using `Path.resolve()`. Because `.venv/bin/python` is a symlink to an underlying `/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3.12`, that call silently switched to the base executable and therefore lost access to installed virtualenv site packages. The run log proves the incorrect `/opt/hostedtoolcache/.../python3.12` path in all six command records, including the resulting NumPy import failure.

**Dependency conflict:** the existing `setup.py` declares `numpy==1.26.4`; a later separate pip transaction fetched NumPy `2.5.4` for SciPy `1.18.1`, with the explicit pip warning: `gadapt 0.5.5 requires numpy==1.26.4`. Thus merely fixing the interpreter symlink without pinning NumPy would still leave an incompatible full-clone environment.

## Narrow repair

- Replace the executor's `.resolve()` on interpreter path with `.absolute()` to retain `.venv/bin/python` symlink semantics. Add an explicit prerequisite probe that rejects an interpreter not inside a virtualenv, not on Python `3.12`, or with NumPy different from `1.26.4`.
- Force `numpy==1.26.4` **in the same pip transaction** as `scipy>=1.15,<1.17` and the cheap unit-test dependencies, plus `pip check`. GAdapt core, `setup.py`, historical results and scientific objectives remain untouched.
- Add two fast local failure-mode regression checks: actual symlinked virtualenv retains `sys.prefix != sys.base_prefix` and explicit rejection of a system interpreter or NumPy 2.x. Existing fail-closed orchestration and 341-alias tests are preserved.

**Execution policy:** user authorized autonomous future workflow tests on the owned `owlCoder/gadapt` repo. A **single-run follow-up workflow**, scoped to GitHub run ID `41357664531`, attempt `2`, will test the corrected HEAD after the original failed job is rerun. The one-shot follow-up does **not** trigger from push, PR, schedule, or its own completion, and caps execution at 15 minutes. The original rerun retains its old SHA; its test result is **not** validation of the repair. Only the follow-up run's own `gate.json` can establish repaired real-clone regression.

## Still outside the gate

Passing the full-clone compatibility gate does not certify real ORPD nested physical solver invocation counting, model-independent witness verification, official COCO optimum access or algorithmic novelty. I65 remains `novelty not established / NO-FREEZE / NOT_RUN`. For meaningful scientific review, separately observe the true number of AC/power-flow calls per Python objective, including failed solver calls and any witness invocation, with an externally checkable trace.
