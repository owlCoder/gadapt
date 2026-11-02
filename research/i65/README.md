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

## Four independently recomputed I56 operating-constraint aggregates (2026-11-02)

A separate [research-only NumPy verifier](orpd_operational_witness.py)
recomputes I56 voltage, reactive generator, slack-reference PG and branch
thermal penalties **only after** the previously independently written AC
equations validate the supplied solved state. The 15 analytical/adversarial
[unit tests](test_orpd_operational_witness.py) all passed locally (exact
[console](../I65_ORPD_CONSTRAINT_LOCAL_TEST_LOG_2026-11-02.txt)); originals
are untouched. A [single-development-case smoke](smoke_orpd_operational_constraints.py)
is preregistered at **1 setup OPF, 1 original-I56 PF, 1 witness PF**, with
absolute `1e-8` aggregate-difference tolerance and four limit-only
falsifications. See [scope, formulas and hard gates](../I65_ORPD_OPERATIONAL_CONSTRAINT_PREFLIGHT_2026-11-02.md).
A real PYPOWER comparison is **NOT_RUN at this initial preflight**, so the
local 15/15 must not be called a physical feasibility test or result.

## First real I56 four-constraint comparison and negative finding

[Run #41406369109](https://github.com/owlCoder/gadapt/actions/runs/41406369109)
**FAILED the additional reactive-tamper assertion**, but the 15 initial
unit tests passed and the four independently recomputed constraint values
matched frozen I56 **exactly**, with **zero** differences. The original
fixed development candidate was **infeasible** due to reactive component
`0.5991137833375748` (other components 0); this is NOT an optimizer
benchmark result. The false input lowered `QMIN`, masking an existing
violation; exact original [negative JSON](../I65_ORPD_OPERATIONAL_FIRST_NEGATIVE_2026-11-02.json)
and [analysis](../I65_ORPD_OPERATIONAL_FIRST_NEGATIVE_REPORT_2026-11-02.md)
are archived.

The tamper has been mathematically strengthened to exceed the entire
previous violation total, with two new analytic tests; **17/17 LOCAL PASS**.
The physical CI verification of this strengthened tamper is **not yet
established** at this repair commit. None of the original four I56 metrics,
numerical thresholds or historical sources were changed.

## Final measured I56 constraints: exact agreement, infeasible midpoint retained

[GitHub Actions run #41407293845](https://github.com/owlCoder/gadapt/actions/runs/41407293845)
completed **SUCCESS**, with **17/17** analytic tests and one real development
`case30/j1` comparison. All four I56-style constraints agree with frozen
`ORPD.evaluate` **exactly** (0.0 absolute difference). The original fixed
candidate is **NOT feasible**: reactive component `0.5991137833375748`,
while voltage, slack and thermal components are zero. Four controlled
limit-only falsifications now all register their violations; the original
failed reactive-tamper [run #41406369109](https://github.com/owlCoder/gadapt/actions/runs/41406369109)
and raw negative outcome remain archived without modification.

Source/JSON/ZIP and **4/4 SHA-256** evidence are in the [complete result](../I65_ORPD_OPERATIONAL_CONSTRAINT_SUCCESS_2026-11-02.md)
and [raw successful JSON](../I65_ORPD_OPERATIONAL_SUCCESS_2026-11-02.json).
This closes a *single-development-case operational arithmetic replication*
gate, not a complete independent AC solver or proof of scientific novelty.

## Independent numerical AC PF diagnostic — 2026-11-02

A new [independently written, NumPy-only Newton numerical PF solver](independent_ac_newton.py)
solves *input* REF/PV/PQ AC equations from a **flat start** with central
finite differences, a 20-step cap, explicit numerical residual accounting
and conservative rejection of unsupported inputs. Unlike previous AC
residual and I56 constraint checks, this **actually computes new bus
voltages and angles**, without using PYPOWER's solved point. It has
**16/16 standalone analytic/negative tests PASS locally** (exact
[console](../I65_INDEPENDENT_NEWTON_LOCAL_TEST_LOG_2026-11-02.txt)),
including known 0.4 MW two-bus loss and PV/PQ/REF three-bus cases.

A strictly bounded [development-only comparison smoke](smoke_independent_ac_newton.py)
is preregistered against the original I58 `case30/j1` fixed midpoint
with fixed voltage/angle/branch-loss tolerances; it is NOT_RUN at
initial publication. See [the preflight and limitations](../I65_INDEPENDENT_NEWTON_PREFLIGHT_2026-11-02.md).
It reimplements a standard numerical method, **not** a novel optimizer or
independent physical grid model; it does not enforce generator reactive
limits, and the earlier original candidate remains reactively infeasible.

## Confirmed independent numerical Newton cross-solver check (2026-11-02)

[Actual Python 3.12 GitHub run #41413792862](https://github.com/owlCoder/gadapt/actions/runs/41413792862)
**PASS**, 16/16 unit tests and independent, flat-start NumPy Newton
solution on the single non-held-out I58 `case30/j1` midpoint. Newton
converged in **3 iterations / 325 mathematical residual evaluations**.
Against PYPOWER: maximum voltage-magnitude deviation
`3.1086244689504383e-15 pu`, wrapped angle deviation
`5.684341886080802e-14°`, branch-loss difference
`1.141309269314661e-13 MW`; each below preregistered thresholds.
Archive ZIP/4/4 log digests, internal solver trace SHA, exact source blobs
and [byte-preserved smoke JSON](../I65_INDEPENDENT_NEWTON_SMOKE_2026-11-02.json)
were independently verified. See [the verified report](../I65_INDEPENDENT_NEWTON_RESULT_2026-11-02.md).

Unlike earlier residual checks, this is **an independently coded numerical
AC PF solver**, not a PYPOWER-supplied solved-state checker. It is still
the **same classical model/data**, not independent physical measurements,
OPF or an original I65 algorithm. The original fixed midpoint remains
**reactively infeasible**. [Physical-cost decision memo](../I65_PHYSICAL_COST_ACCOUNTING_DECISION_DRAFT_2026-11-02.md)
is DRAFT and requires supervisor decisions before any method freeze.

## Independent generator and operational-dispatch reconstruction — 2026-11-02

A [research-only NumPy module](independent_ac_dispatch.py) takes the
**original unsolved case** and an independently computed Newton voltage
state; reconstructs PV/REF `QG`, reference `PG`, line-end complex
flows, AC nodal residuals and all four historical I56 violation sums.
It does **not** import PYPOWER or use its solved state. The module
requires one online generator per controlled bus and rejects ambiguous
multiple-generator Q allocation rather than fabricating individual
injections. Its [14 analytic/negative unit tests](test_independent_ac_dispatch.py)
passed locally, with an [exact logged transcript](../I65_INDEPENDENT_DISPATCH_LOCAL_TEST_LOG_2026-11-02.txt).

The [one-case30 development test](smoke_independent_ac_dispatch.py) and
[bounded one-shot Python 3.12 workflow](../../.github/workflows/research-i65-independent-dispatch-one-shot.yml)
are preregistered with fixed PG/QG/flow/constraint tolerances, and have
**NOT_RUN** at this preflight. The independent numerical algorithm uses
the **same standard mathematical AC model and network data**, not
external physical observations; PF convergence can still leave the
midpoint **reactively infeasible**. See the
[formal preflight](../I65_INDEPENDENT_DISPATCH_PREFLIGHT_2026-11-02.md).

## Verified independent generator dispatch reconstruction (2026-11-02)

The [bounded GitHub Actions #41419711114](https://github.com/owlCoder/gadapt/actions/runs/41419711114)
**PASS**, Python 3.12.15 with **47/47** old and new analytic tests.
For one original non-held-out fixed I58 `case30/j1` case, the
independent Newton and [dispatch reconstruction](independent_ac_dispatch.py)
derived REF/PV generator `QG`, REF `PG`, both-end branch flows and all
four I56 constraints independently of PYPOWER output.
The max generator `QG` error was `6.71e-12 MVAr`, REF `PG` error
`8.88e-13 MW`, and both-end branch flows below `6.01e-12 MVA`.
The crucial original negative is preserved: reactive violation from the
independent solver `0.5991137833375704`, vs PYPOWER
`0.5991137833375748`; **both label the original midpoint infeasible**.

Original CI ZIP and **6/6 individual log digests**, internal trace hash,
and six source Git blobs were independently checked. See the
[complete result](../I65_INDEPENDENT_DISPATCH_RESULT_2026-11-02.md)
and [byte-preserved raw JSON](../I65_INDEPENDENT_DISPATCH_SUCCESS_2026-11-02.json).
This is independent numerical software on the **same mathematical AC
model/input**, not independent physical grid evidence or optimizer novelty.
Multi-generator Q allocation and Q-limit-enforcing PF remain unsupported.

## Public case30 model provenance and synthetic input lineage (2026-11-02)

The [precommitted source audit](../I65_CASE30_SOURCE_PROVENANCE_PREFLIGHT_2026-11-02.md)
distinguishes PYPOWER/MATPOWER's modified six-generator `case30` academic
benchmark from `case_ieee30` IEEE Common Data Format data. Neither
represents independent measured validation of I65. The original I56/I58
development case transforms `PD/QD` by a seeded 10% perturbation at
load factor 1.00, transfers `PG` from **one setup OPF**, then snaps
and applies only `VG/TAP/BS` controls.

A [NumPy-only lineage auditor](input_provenance_audit.py) stores four
canonical numeric SHA-256 fingerprints and rejects unauthorized
changes; [17 synthetic tests](test_input_provenance_audit.py) and a
[one-OPF, zero-PF case30 diagnostic](smoke_input_provenance_audit.py)
are preregistered. **Real Python 3.12 outcome NOT_RUN** at this initial
preflight. PYPOWER case data are excluded from its BSD software
license, so no full case arrays are copied into this repository.

## Real source case and scenario transformation audit (2026-11-02)

[GitHub Actions #41422248142](https://github.com/owlCoder/gadapt/actions/runs/41422248142)
**PASS** on one original I58 development `case30,j1,R17`:
**17/17** synthetic adversarial tests; only **one OPF setup call**;
raw/scaled/post-OPF/controlled numeric input hashes pass exact change
allowlists. The archived installed **PYPOWER 5.1.19 `case30.py` SHA** is
`f7f8c565be22f30d4ba9facab8707072ef5dc3bacb6ea9ef57245c11e0bde9f6`.
The source's **raw input numeric fingerprint** is
`3b4e587cd94f2cfefc8cec384b3fec692eb74a75f38c9f757800d261d4b28c9c`.
Original I56 control selection measured **6 VG, 0 TAP, 2 BS**
variables: the case cannot, by itself, validate any controllable
transformer tap optimization. The seed-302 ±10% load change is synthetic.
PYPOWER's installed API did **not** expose `case_ieee30`, so its numeric
side-by-side identity with `case30` was NOT_VERIFIED; both are
academically sourced, not independently observed field data.

See [complete archive, real evidence hashes and limitations](../I65_CASE30_SOURCE_PROVENANCE_RESULT_2026-11-02.md),
[byte-preserved smoke JSON](../I65_CASE30_INPUT_LINEAGE_SUCCESS_2026-11-02.json)
and [unsigned supervisor decisions](../I65_SUPERVISOR_DECISION_PACKAGE_2026-11-02.md).
No physical-model independence, algorithm novelty or confirmatory-run
authorization is implied.
