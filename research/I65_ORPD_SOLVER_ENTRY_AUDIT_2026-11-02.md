# I65 — read-only PYPOWER solver API-entrypoint audit, pre-runtime gate

**Date:** 2026-11-02. **Source baseline:** `owlCoder/gadapt/main`, `a87027a8b22e95fef6d5ec4cd1c46f38a66c8dc3`.  
**Research decision:** bounded software-instrumentation validation **GO**, optimizer-method research and held-out COCO **NO-GO / NO-FREEZE / NOT_RUN**.

## Why a separate gate is necessary

The [full-clone compatibility PASS](FULL_CLONE_REGRESSION_SUCCESS_2026-11-01.md) (GitHub run [#41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925)) validates the defined unit-test suite and 341 original Git-source aliases. It does **not** establish that `Evaluator.calls` equals the sum of all actual OPF and PF solver invocations. The [source-only call graph](I65_ORPD_SOLVER_CALL_BOUNDARY_2026-11-01.md) finds:

- Original [`ORPD.__init__`](legacy/flat/iteration56_orpd.py) makes an OPF setup call to `pypower.api.runopf`.
- Original [`ORPD.evaluate`](legacy/flat/iteration56_orpd.py) calls `runpf` for each candidate that reaches the solver.
- Original I56 `Evaluator._call` reserves one Python candidate attempt, which may fail before its PF entrypoint.
- I58 `independent_check` recreates the scenario with another OPF and calls another PF entrypoint. The I58 checker is independently written Python logic but uses the **same PYPOWER library**; it is NOT an independent physical AC model.

## Research-only code and low-cost validation

Added [`research/i65/orpd_solver_entry_audit.py`](i65/orpd_solver_entry_audit.py), a sequential, in-process context manager wrapping exactly `pypower.api.runopf` and `pypower.api.runpf`, without editing the historical implementations. Its trace:

1. Requires explicit `setup`, `search`, or `witness` phase, and rejects unknown or nested phases;  
2. Reserves each API-entrypoint attempt **before** entering the callable;  
3. Distinguishes normal returns from `BaseException` (with exception type), restoring both originals even on error;  
4. Reports per-phase/per-entrypoint counts, ordered events and deterministic SHA-256-identified JSON evidence.

**Limitations by construction:** this is single-threaded and relies on runtime lookup of `pypower.api` functions, so previously bound imported function aliases are not intercepted. The trace counts **API entrypoints** only, not internal Newton steps/OPF subsolves or actual hardware/physical experiments. It does not turn a shared PYPOWER witness into an independent oracle.

Added eight inexpensive [mock-based Python unit tests](i65/test_orpd_solver_entry_audit.py), which **all passed locally** on Python 3.13.5 in an isolated test directory, with no PYPOWER installation and no solver/optimization run. The eight tests cover phase and kind counts, normal return, exception and `KeyboardInterrupt`, missing phase, invalid phase/kind, nested phase/trace, deterministic JSON, and out-of-trace rejection. The exact executed source and test module Git blob SHA are `241412cf61d3e210a66e755be873d040c5c45b6f` and `71fb25f4e17657ef2cea0f74dc6a94a22f22734f`, respectively.

Added **explicit opt-in** [`research/i65/smoke_orpd_solver_entrypoints.py`](i65/smoke_orpd_solver_entrypoints.py), which never executes a GA, CMA, DE, COCO benchmark or any multiple-seed optimization study. It uses one existing *development-only* I58 `case30`, scenario `j=1`, constructs one actual scenario, makes **one** admitted I56-style search evaluator call, and invokes one I58 witness check, all under three phase scopes. Expected **visible** calls are:

| Phase | `runopf` API attempts | `runpf` API attempts |
|---|---:|---:|
| Setup | 1 | 0 |
| Search | 0 | 1 |
| Witness | 1 | 1 |
| **Total** | **2** | **2** |

The script checks the observed count against this **predeclared expectation** and rejects any mismatch. It reports `evaluator.calls=1`, the exact Git blobs of each frozen source, the witness's vector-validation and convergence booleans **without asserting optimization feasibility**, and raw SHA-identified event trace. It refuses to run if the 341 historical root aliases were not explicitly restored. This is a tiny diagnostic, not a scientific confirmation run.

**Real PYPOWER execution remains `NOT_RUN` at the time of this initial report.** The local environment does not have PYPOWER. The bounded, one-shot GitHub Actions [API-entrypoint audit workflow](../.github/workflows/research-i65-orpd-entry-audit-one-shot.yml) is scoped exclusively to a deliberately authorized retry of completed source run #41358768925 attempt 2; it installs the already verified Python 3.12/NumPy 1.26.4/SciPy 1.16/PYPOWER 5.1.19 stack, runs eight unit tests and at most a single 120-second case30 scenario, and archives raw log files with SHA-256 checksums. It is not triggered by pushes, PRs or schedules.

## Falsification and interpretation

If `runopf` or `runpf` entrypoints are missing, repeated, or unclassified, **FAIL the instrumentation gate** and inspect the observed raw trace. If the witness vector is invalid, report failure rather than repair the candidate. If numeric PF fails to converge, preserve the `witness_converged=false` field rather than claim a validated solution. Even **PASS** would prove only the narrow PYPOWER **API entrypoint** count for the chosen deterministic development case.

The I65 scientific gate remains **NOT_CLOSED** until separate solver-internal call tracing, an independently implemented AC feasibility oracle, a reviewed joint budget policy (including setup and witness) and supervisory originality/scope decisions are available. No historical result or GAdapt default was modified.
