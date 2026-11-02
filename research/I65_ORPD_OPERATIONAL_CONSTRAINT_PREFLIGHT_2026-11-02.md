# I65 — independent I56-compatible operational-constraint gate (preflight)

**Date:** 2026-11-02. **Baseline:** `owlCoder/gadapt/main` at `1cf8f8f0493cc699b7fe6c250783ff6a67543409`.  
**Decision:** small deterministic *research instrumentation* **GO**; novel optimizer / frozen policy / confirmatory COCO **NO-GO**.  
**At preregistration:** **15/15 local analytic tests PASS**; live Python 3.12 I56 comparison **NOT_RUN**. No GAdapt core or frozen I56/I58 sources were modified.

## Research question and exact scope

The previous [real NumPy AC residual check](I65_AC_EQUATION_RESIDUAL_RESULT_2026-11-02.md) confirmed nodal power balance and line-flow consistency for one PYPOWER-generated I58 `case30,j=1` operating point, but did not check the four historical I56 constraint aggregates. Can we *independently reproduce those exact aggregates*, and does a one-candidate real I56 run agree numerically, without changing historical outcomes or running an optimizer?

Added [`orpd_operational_witness.py`](i65/orpd_operational_witness.py): NumPy-only implementation from **solved** `bus/gen/branch` arrays. It first demands that the separately written [`ac_residual_witness.py`](i65/ac_residual_witness.py) passes its AC balance and branch-flow residual, then independently sums four components using the historical I56 convention:

- **Voltage:** `sum_i [max(VM_i - VMAX_i, 0) + max(VMIN_i - VM_i, 0)]` (per unit).
- **Reactive:** `sum_online_g [max(QG_g - QMAX_g, 0) + max(QMIN_g - QG_g, 0)] / baseMVA`.
- **Slack/reference active:** the same positive violation formula for `PG_g` versus `PMAX/PMIN`, restricted to online generators on a bus with `BUS_TYPE=3`, divided by `baseMVA`. This is **not** a check on every non-reference active generator; that is the original I56 metric's limited scope.
- **Thermal:** for each branch with **positive** `RATE_A`, `max(max(hypot(PF,QF), hypot(PT,QT)) - RATE_A, 0) / baseMVA`, summed. A **zero rating means no active limit**, following historical I56, not zero transfer capacity. Thermal flows are read from the solver state *after* the independently recomputed AC branch-flow residual has passed; the checker does not independently solve AC power flow.

The four aggregates have their historically mixed units; their numerical `I56-compatible` feasibility label means **each component ≤ 1e-6**, not externally certified AC feasibility. The code rejects nonfinite/incomplete solved arrays, inverted PG/QG/VM limits, negative branch ratings, noninteger bus types, absent online reference generator, and invalid tolerances. For an AC residual failure the only status is `AC_RESIDUAL_FAIL` with `components=null` and `i56_compatible_feasible=null`: no spurious PASS or false feasibility certificate.

## Actual cheap preflight

Executed **15/15** Python standard-library `unittest` tests on the exact I65 code copy under local Python `3.13.5`, NumPy `2.3.5`, using the *SHA-matched existing AC verifier* (Git blob `8e6bb1b4cf78578c15315be3b4cff127bc2c8036`). The tests include hand-constructed 2-bus examples with a physically consistent `20.0 MW/-19.6 MW` branch flow, a `10 MVA` thermal limit yielding dimensionless `0.1` violation, both signs of bound excursions, multiple reference generators, inactive-generator exclusion, and simultaneous violations of all four categories. They explicitly falsify generation injections, recorded branch flow, source shape and input limits. There is **no** PYPOWER import or optimization run in these unit tests.

[Actual archived local unittest console](I65_ORPD_CONSTRAINT_LOCAL_TEST_LOG_2026-11-02.txt) (byte-for-byte Git blob `e353f84f1f9c1f6731509f63bed057d6aa6c249f`). Local actual test console SHA-256: `993c1f164a783601deabc609c73d51ee1c2ce8ab426e7be51ec75635a3f13961`. The source and tests have the exact executed Git blob identifiers:

| Program | Git blob | SHA-256 |
|---|---|---|
| `orpd_operational_witness.py` | `120244c35c610ac48b515df4ef86791eb6466e3f` | `4c55bbc90f881e81974445d0d84a6e22faa9dcc940243df5b04a9c7aa64fd47d` |
| `test_orpd_operational_witness.py` | `510fed1723f9a817e4a823b83d45cf1b39e2f28b` | `1915ede339c1e26cd05ce905248c7ba94b07ee1954eefc398bd117f6180ede5a` |
| `smoke_orpd_operational_constraints.py` | `71e777f14f1ca37ae91fb1793e1d55befdc5bf82` | `17b67b8bf255b6684605d8e99e56cd051781d70ea90abdbac9a9ed693bffeee5` |

## Explicitly preregistered real development test

One **already used** I58 `case30, j=1, resolution=17` scenario and one fixed midpoint control vector, **no optimizer execution**, maximum **3** PYPOWER API entries:

| Phase | `runopf` | `runpf` |
|---|---:|---:|
| Scenario setup | 1 | 0 |
| Original I56 `ORPD.evaluate` on the chosen candidate | 0 | 1 |
| Separate solver-supplied operating point for NumPy equation check | 0 | 1 |

The [fixed smoke](i65/smoke_orpd_operational_constraints.py) compares every NumPy component with the original I56 `ORPD.evaluate` output using a **predeclared absolute tolerance of 1e-8** on the dimensionless I56 metrics, and demands an exactly matching I56-compatible feasible/infeasible label. It first checks the already frozen **1e-3 MVA** AC nodal and **1e-5 MVA** branch-flow residual tolerances, then checks four separate *in-memory limit-only falsifications* without any extra solver calls. It reports **the original feasibility label even if infeasible**; never force an optimization success.

A single GitHub Actions [bounded research audit](../.github/workflows/research-i65-orpd-operational-one-shot.yml), limited to 8 minutes, runs the 15 tests and this one candidate, with Python 3.12, NumPy 1.26.4, PYPOWER 5.1.19, full-history Git restoration and SHA-256 log archive. It is a **direct child** of original manually dispatched root run `41357664531` **attempt 4**, avoiding GitHub's three-level chained `workflow_run` limit. The root job on its older SHA is only an event source, not a test result. No push, PR, schedule, GA search, held-out cell, COCO, or confirmatory ORPD experiment is triggered.

## Independent-model and novelty boundary

This is an **independent reimplementation of four arithmetic aggregation rules conditioned on independently checked AC equations**, *not* a second solver. Like original I56, this limited check does not prove every OPF/ORPD operational constraint, does not certify an independent data/model source or the nested solver-call budget, and does not address candidate-C algorithmic originality. The existing closest baseline remains original I56/I58, so **scientific novelty not established**. No new theorem or research-method GO is asserted; this is a falsifiable diagnostic software gate only. The supervisory M1–M6 protocol/scope approval and any statistical protocol freeze remain outstanding.

## CI activation addendum (2026-11-02, before actual PYPOWER comparison)

The first one-shot workflow expression was syntactically malformed: its `if` condition had only one closing brace (`}`) after `${{`, rather than GitHub Actions' required `}}`. The root manual workflow was retried as attempt `4` and predictably failed on its old virtualenv bug, but this new invalid child never registered or ran. This **is not a failed scientific test**. The guard was repaired to use root run `41357664531` attempt **5**; checked that the three GitHub expression delimiters are paired and that the source of the AC/constraint tests, preregistered tolerances, and cap remain unchanged. Only the future child job's actual artifact establishes the physical test outcome.

## Actual first run and bounded falsifier repair (2026-11-02)

The original real development [CI run #41406369109](https://github.com/owlCoder/gadapt/actions/runs/41406369109) **FAILED** an auxiliary reactive bound-tamper assertion while all original I56 metric comparisons and AC residuals passed. The fixed midpoint candidate was **reactively infeasible** with component `0.5991137833375748`; see [unchanged negative source JSON](I65_ORPD_OPERATIONAL_FIRST_NEGATIVE_2026-11-02.json) and [full root-cause and repair report](I65_ORPD_OPERATIONAL_FIRST_NEGATIVE_REPORT_2026-11-02.md). The original 15 unit tests were followed by 2 new counterexample tests (17/17 locally passed). The fake bound mutation—not a physical objective, original script, baseline case, threshold or mathematical formula—was strengthened. The rerun will use direct-child root attempt **6** and can only be called green after independently reviewing its own logs.

## Measured final result following the preserved negative run

The strengthened falsifier passed in [actual Python 3.12 workflow #41407293845](https://github.com/owlCoder/gadapt/actions/runs/41407293845): **17/17** deterministic unit tests and exact four-component I56 agreement with 0.0 metric differences. The original midpoint **remains reactively infeasible** with penalty `0.5991137833375748`; the controlled reactive fake cap increased this to `0.8483733709301324`. See [the final real result, SHA-verified archive and limitations](I65_ORPD_OPERATIONAL_CONSTRAINT_SUCCESS_2026-11-02.md). Original [first FAIL](I65_ORPD_OPERATIONAL_FIRST_NEGATIVE_REPORT_2026-11-02.md) remains a separate immutable record.
