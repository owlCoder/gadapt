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

## PYPOWER physical entrypoint audit (2026-11-02)

The successful Python 3.12 full-clone regression does not count the
historical ORPD scenario-setup OPF and I58 witness OPF/PF calls. A new,
**research-only** [sequential API-entrypoint tracer](orpd_solver_entry_audit.py)
counts `pypower.api.runopf/runpf` entries by setup/search/witness phase;
[its eight adversarial tests](test_orpd_solver_entry_audit.py) **passed
locally** with mocked PYPOWER, without running optimization.

The [single-case30/j1 smoke](smoke_orpd_solver_entrypoints.py) is opt-in,
requires restored historic symlinks, and predeclares one setup OPF, one
search PF, and a distinct witness OPF+PF. The actual PYPOWER smoke result
must be obtained from CI; it was **NOT_RUN** in the local environment.
See [the scope and falsification protocol](../I65_ORPD_SOLVER_ENTRY_AUDIT_2026-11-02.md).
This traces API entrypoints, not nested solver iterations or an
independent-model oracle, and does not establish I65 novelty.

## Measured PYPOWER audit result (2026-11-02)

[GitHub Actions #41385833963](https://github.com/owlCoder/gadapt/actions/runs/41385833963)
**PASS** on one I58 development `case30/j1` scenario. Eight new entrypoint
tests passed, and the real PYPOWER trace matched the prespecified four
entrypoint attempts: **setup OPF 1, search PF 1, witness OPF 1 + PF 1**,
while the historical candidate evaluator counted **one** search attempt.
Independent verification matched the ZIP SHA-256, **four of four** individual
log SHA-256 values, the event-trace SHA-256, and source Git blobs.
See [the result and scientific limitations](../I65_ORPD_SOLVER_ENTRY_AUDIT_RESULT_2026-11-02.md).

This is **solver API entrypoint accounting on one development case**, *not*
the internal number of Newton iterations, total physical B accounting on
new COCO/ORPD runs, a model-independent witness or a novel optimizer.

## Independent AC equation residual preflight (2026-11-02)

A separate [NumPy-only AC residual checker](ac_residual_witness.py) independently
computes nodal active/reactive balance, transformer/phase-shift line currents,
branch flows and active loss from a **supplied** AC PF operating point without
importing or invoking PYPOWER. Its **15 adversarial and analytic unit tests**
passed locally (including a hand-calculated 0.4 MW two-bus loss). Its
[development-only case30/j1 PYPOWER smoke](smoke_ac_residual_witness.py) has
predeclared tolerances and one OPF setup + one PF solve, **not yet run at this
documentation gate**. See [full mathematics, preflight and limits](../I65_AC_EQUATION_RESIDUAL_PREFLIGHT_2026-11-02.md).

This only checks the algebraic consistency of **the solver-supplied state**;
it is not a separately implemented numerical AC solver, not a validated
independent physical model, and not COCO/I65 novelty evidence.

## Real AC equation consistency on one historical development case

[GitHub Actions #41395941943](https://github.com/owlCoder/gadapt/actions/runs/41395941943)
**PASS** on a single `case30, j=1, R=17` I58 development operating
point: 15/15 tests, independent NumPy nodal AC mismatch
**1.53e-8 MVA** versus predeclared **1e-3 MVA**, branch-flow difference
**4.05e-13 MVA** versus **1e-5 MVA**, and independently calculated
losses **3.1140815874688497 MW** versus PYPOWER's **3.114081587468966 MW**.
A false +1-MW generator injection was rejected. The solver performed
one setup OPF and one witness PF, with no search calls. ZIP digest,
4/4 log digests, internal trace hash and source blobs were independently
verified. See [the complete result and limitations](../I65_AC_EQUATION_RESIDUAL_RESULT_2026-11-02.md).

This **does not constitute a second numerical AC solver or complete
operational-feasibility certificate**, and leaves scientific novelty,
I65 candidate-C validation and held-out COCO unapproved/unrun.
