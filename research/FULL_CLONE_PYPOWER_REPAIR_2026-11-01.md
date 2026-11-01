# GAdapt I65 — second real full-clone regression, missing PYPOWER dependency

**Date:** 2026-11-01. **Scope:** real Python 3.12 GitHub Actions migrated-clone compatibility, not held-out COCO or new optimizer experiments.

## Actual repaired workflow result

- **Run:** [#41358375382](https://github.com/owlCoder/gadapt/actions/runs/41358375382)
- **Commit:** `ff3e1e5b5d6863f70a4dcacbf3c0df2f2d72db8f` on `main`.
- **Status:** `completed / failure`, stopped at **step 9 of 11**.
- **Artifact:** [gadapt-repaired-full-clone-41358375382](https://github.com/owlCoder/gadapt/actions/runs/41358375382/artifacts/13104635829), ZIP SHA-256 `d4d9550caea9404fabcc27e9bc3a5f7f5845ad897032308eb6fb7c87083e37b6`. Each of the **nine** individual archived step-log SHA-256 digests was checked against `gate.json`: **9/9 match**.

| Actual step on GitHub's full Git checkout | Result |
|---|---|
| 1. Compatibility unit tests | PASS |
| 2. Historical committed-tree provenance | PASS (341/341) |
| 3. Legacy source hash preflight | PASS (341/341) |
| 4. Restore old root symlinks | PASS (341 created) |
| 5. Restore idempotence | PASS (341 existing) |
| 6. Real `from gadapt.ga import GA` | **PASS** |
| 7. Python-3.12 installed dependencies and freeze | **PASS** |
| 8. Real historical I41 tests | **11 passed** |
| 9. Real historical I63 tests | **16 passed / 1 failed** |
| 10. I64 tests | NOT_RUN (fail-fast) |
| 11. I65 tests | NOT_RUN (fail-fast) |

The I63 failing case was `Wrapper.test_scenario_signature` at `research/test_iteration63_replication.py:153`. Its call to `m._make61("case30", 0)` constructs a real I58 `BusORPD` object that requires `from pypower.idx_gen import GEN_BUS`, but `pypower` had not been installed: **`ModuleNotFoundError: No module named 'pypower'`**. This is an explicitly missing test dependency, **not** a discovered failed physical ORPD optimization result. No frozen I56/I58/I61/I63 source was edited.

## First infrastructure fix verified

The earlier base-Python symlink resolution defect is demonstrably fixed: `gate.json` now records each command using `.../gadapt/.venv/bin/python` rather than `/opt/hostedtoolcache/.../python3.12`. The real GA import passed and the frozen environment reports Python 3.12, `numpy==1.26.4`, `scipy==1.16.3`, `cma==4.5.0` with a successful `pip check`. This is an independently observed improvement, not a synthetic claim.

## Next minimal dependency repair

Install a declared, test-only `PYPOWER==5.1.19` **inside the virtualenv**; the official PyPI project confirms the version and its distribution (https://pypi.org/project/PYPOWER/5.1.19/). Preserve exact NumPy and SciPy constraints. No changes to the library's public setup metadata, algorithms, frozen scientific implementations or historical raw results. The package is needed to *construct* original I63 scenarios; this gate still does not run held-out scientific comparisons.

A second one-shot `workflow_run` event is restricted to the previous repair run ID `41358375382`, attempt 2, to validate the fixed **new default-branch commit** without enabling unrelated push CI. Retrying the previous run uses its old original commit and must **not** be mistaken for a test of the new dependency repair. Only the new one-shot run's `gate.json` and SHA-256 logs determine the verdict.

## Remaining independent research gates

No claim about a physically independent power-flow reference/oracle, correct counts of *nested* AC solver calls, official COCO f21/f24 evaluation correctness or candidate-C novelty is supported by this compatibility test. I65 remains `novelty not established / DRAFT / NO-FREEZE / NOT_RUN`.
