# I65 — research-only instrumentation and tests (UNFROZEN)

**2026-11-01 status:** `novelty not established`; `NO-FREEZE`; `COCO f21/f24 NOT_RUN`; `GAdapt/CMA integration NOT_TESTED`.

The Python files in this directory are **research-only** and do not modify GAdapt's library defaults:

- `audited_budget.py` — sequential physical-attempt accounting and a charged final witness.
- `stagnation_checked.py` — 20-completed-generation stagnation semantics.
- `e_common_snapshot.py`, `stagnation_reference.py` — comparison/reference sources.
- `make_gate_fixtures.py`, `test_*.py` — deterministic fixtures, regression and SciPy DE smoke tests.
- `test_audited_budget_preflight.py` — reject nonfinite coordinates, invalid bounds and unsafe witness tolerances before validation.
- `test_audited_budget_lifecycle.py` — terminal witness sealing and fail-closed recheck exceptions.

From the root of a clone with installed NumPy, SciPy and pytest:

```sh
python -m pytest -q -rx research/i65
python research/i65/make_gate_fixtures.py
```

The earlier archived **isolated** run recorded **54 passed, 3 xfailed** ([test log](../I65_GATE_TEST_LOG.txt)). Three intentional xfails relate to older reference instrumentation, not failed optimizer experiments. This is not the result of a full-clone migration regression. No held-out COCO benchmarks have been performed.

**New isolated gate (same date):** reproduced 10 failed cases in an adversarial preflight of the original research evaluator; after a narrow fix, **22/22 passed**, including the two existing SciPy DE smoke tests, under Python 3.13.5 / NumPy 2.3.5 / SciPy 1.17.0 / pytest 9.0.2. This was **not** the full historical I65 regression in a pinned checkout. Read the [detailed preflight report](../ITERATION65_BUDGET_PREFLIGHT_GATE_2026-11-01.md).

**Reproduced complete isolated I65 pytest suite (same date):** using all nine SHA-matched I65 Python modules/tests (not a full GAdapt clone), **74 passed, 3 xfailed**, with the three original reference defects preserved as expected negatives. No optimizer benchmarks. See [full isolated I65 gate](../ITERATION65_ISOLATED_REGRESSION_GATE_2026-11-01.md) and [raw log](../I65_ISOLATED_REGRESSION_TEST_LOG_2026-11-01.txt). This sentence records the status of that earlier isolated run; the subsequent **real Python 3.12 full-clone core regression PASSED** (details below).

**Terminal-witness lifecycle gate:** a reproducible early-witness and `BudgetReached` exception defect was fixed in the research-only wrapper; the complete reconstructed I65 collection now records **88 passed, 3 xfailed** (14 additional tests), with all prior expected reference failures preserved. See [terminal witness gate](../ITERATION65_WITNESS_TERMINAL_GATE_2026-11-01.md) and [actual test log](../I65_WITNESS_TERMINAL_TEST_LOG_2026-11-01.txt). The fix does **not** validate a mid-run switch from GAdapt to CMA or a real full-clone regression.

**Real full-clone gate now closed:** [run #41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925) independently verified **88 passed / 3 xfailed** for the complete I65 collection under Python 3.12 after restoration of all 341 aliases. The whole defined I41/I63/I64/I65 core gate is PASS; external PyGAD, independent real ORPD solver counting and COCO remain outstanding. See [full-clone report](../FULL_CLONE_REGRESSION_SUCCESS_2026-11-01.md) and [physical solver accounting audit](../I65_ORPD_SOLVER_CALL_BOUNDARY_2026-11-01.md).

- [I65 DRAFT](../ITERATION65_DRAFT_PROTOCOL_SR.md)
- [Prior-art audit](../ITERATION65_PRIOR_ART_AUDIT_DRAFT_SR.md)
- [Instrumentation gate](../ITERATION65_INSTRUMENTATION_GATE_REPORT_SR.md)
- [Raw **test** fixtures](../I65_INSTRUMENTATION_FIXTURES.json)
- [GitHub provenance](../ITERATION65_GITHUB_PROVENANCE_ADDENDUM_SR.md)
- [Research decision](../RESEARCH_DECISION_2026-11-01.md)
- [Supervisor decision package](../SUPERVISOR_DECISION_PACKAGE_2026-11-01.md)
- [Budget/witness preflight gate](../ITERATION65_BUDGET_PREFLIGHT_GATE_2026-11-01.md)
