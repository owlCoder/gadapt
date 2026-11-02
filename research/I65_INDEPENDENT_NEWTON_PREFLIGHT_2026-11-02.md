# I65 independent numerical Newton AC power flow — preregistered development gate

**Date:** 2026-11-02. **Repository:** `owlCoder/gadapt`, baseline `0d93c2b754c60bb25ae31af8dd911d57934944e0`.  
**Gate status before real CI:** **16/16 local standalone tests PASS**, independently solved real I58 case30 **NOT_RUN**.  
**I65 research status unchanged:** `novelty not established / DRAFT / NO-FREEZE / held-out COCO NOT_RUN`.

## Research question, scope, and known prior work

Previous [NumPy-only AC residual verification](I65_AC_EQUATION_RESIDUAL_RESULT_2026-11-02.md) and [four operating-constraint aggregation tests](I65_ORPD_OPERATIONAL_CONSTRAINT_SUCCESS_2026-11-02.md) both checked **PYPOWER-supplied operating points**. These are not numerical-solver independence. Can a separate, self-written, standard Newton numerical solution of the *input* AC power-flow equations agree with PYPOWER on one **non-held-out** fixed development instance?

This is a **reproducibility/integrity tool, not a novel algorithmic contribution**. The method follows the standard polar Newton PF model: P equations at all non-reference PV/PQ buses, Q equations at PQ buses, fixed reference angle, voltage magnitude setpoints at REF/PV buses. References: [MATPOWER newtonpf](https://matpower.org/doc/ref-manual/legacy/functions/newtonpf.html), [MATPOWER AC PF reference](https://matpower.org/docs/MATPOWER-manual-6.0.pdf). No novelty claim is made for Newton, finite-difference Jacobians, or this arithmetic cross-check.

## New independent implementation

[`research/i65/independent_ac_newton.py`](i65/independent_ac_newton.py) is an independently implemented **NumPy-only numerical AC PF solver**. It does **not** import PYPOWER, its `runpf`, its Newton solver, GAdapt, or the earlier AC residual verifier. It creates its own complex Ybus including branch charging, transformer magnitude/phase shift, bus shunts; applies bus active-power equations for PV/PQ and reactive equations for PQ; and uses damped polar Newton with central finite differences, capped iterations and bounded backtracking. It starts with **flat voltage angles** (except the specified reference) and **1.0 pu PQ voltage magnitudes**, using only the *input* generator setpoints at PV/REF. **It does not consume, warm-start or fit a PYPOWER-solved state.** It provides deterministic residual-evaluation counts and separate **branch loss** versus **net injection** totals.

Implementation Git blob `268d0406a90fe7d314d4e01311ea2f4376084b2b`, SHA-256 `9692a0086a4b3a7b9986daf90b7a5608dbb727a53a8e677618a06a5f74e78205`. Tests Git blob `b37b1d094521c5d72e739e2c988c91ab45a615ef`, SHA-256 `6daf2dbbb226dce98d10f0cbb24a7b00374dd5742b284d13b097a1f16b920943`. Script for CI smoke Git blob `b36625edd69f7478219e5150a241e92018187262`, SHA-256 `e4bebfd1283b4163463476679e5e9a63aaba7f023aefc5ccdafb63344cbd9144`.

### Actual local deterministic testing

**16/16 tests PASS** under Python `3.13.5`, NumPy `2.3.5`, no PYPOWER import or numerical-optimizer execution. Analytic examples include a resistive 2-bus case with solved `V_PQ=0.98` pu and exactly `0.4 MW` branch loss; an analytically generated 3-bus **REF/PV/PQ** operating point recovered from a flat start; nonconsecutive bus IDs, line charging/transformer tap/phase shift and bus shunts; a separate 5 MW conductance shunt proving that *net injection* (5.4 MW) must not be mistaken for *branch loss* (0.4 MW). Negative gates reject unsupported bus types, duplicate REF generators, inactive reference, conflicting PV setpoints, zero-impedance lines, nonfinite input, nonexistent bus endpoints and invalid resource caps; disconnected networks return **NOT_CONVERGED / singular_jacobian** without fabricated voltages. Exact local test output SHA-256 `5153f5b8157cbb8a4d13d565d04675320ff1ccb74d3c2121547420837cad4f19`.

The first red local suite found an input-validation bug with mismatched generator and line array lengths (attempting to OR two differently sized vectors). This was fixed before publication, **not silently counted as a prior PASS**. A second small red iteration corrected a field-name mismatch after distinguishing branch loss from shunt-inclusive injection. Final **16/16** status applies only to the exact published files above.

## Fixed, bounded real-development comparison (NOT_RUN at registration)

[`research/i65/smoke_independent_ac_newton.py`](i65/smoke_independent_ac_newton.py) uses only one previously studied I58 `case30,j=1,resolution=17` *fixed snapped midpoint*; scenario setup is the original I56 `runopf` (one entry). It passes the **unmodified unsolved case** to the new NumPy Newton solver first, and only afterwards uses **one PYPOWER `runpf`** as a separate reference. Prespecified API entrypoints are:

| Phase | PYPOWER runopf | PYPOWER runpf |
|---|---:|---:|
| Historical scenario setup | 1 | 0 |
| Optimizer search | 0 | 0 |
| One independent comparison PF | 0 | 1 |

The self-written solver is limited to `max_iterations=20`, `jacobian_step=1e-6` (central difference), `tolerance_pu=1e-9` and `max_backtracks=14`. Its finite-difference residual evaluations are counted separately, not disguised as PYPOWER PF calls. The CI smoke is bounded with a **120-second** process timeout and an **8-minute** total job ceiling. It fails closed on either solver nonconvergence or any of these **preregistered absolute comparison thresholds**:

- Max bus voltage magnitude difference: **5e-4 pu**
- Max bus voltage angle difference after 360° wrap: **5e-3 degrees**
- Difference in *branch-only* active losses: **5e-3 MW**

No threshold, solver algorithm or selected candidate may be altered based on this one development result to manufacture a pass. The [one-shot workflow](../.github/workflows/research-i65-independent-newton-one-shot.yml) is scoped to the previously user-authorized root manual workflow `#41357664531` attempt **7**, directly avoiding multi-level `workflow_run` limits. It has no push, PR or schedule trigger, uses full Git history and the known compatible Python `3.12`/NumPy `1.26.4`/PYPOWER `5.1.19` stack, and archives raw stderr/stdout and SHA-256 file digests even on failure. The old root's known virtualenv installation bug is merely an event trigger; its outcome is not used as evidence.

## Exact no-GO boundary

Even a full PASS would demonstrate a **second independently coded numerical implementation of a familiar AC PF mathematical model** for one development network—not independent physical grid measurements, independent network input data, stochastic ORPD search correctness, full reactive QG allocation, generator Q-limit enforcement, PV↔PQ switching, multi-island networks, dynamic load models or complete ORPD feasibility. The new code explicitly does **not** enforce Q limits, so the already observed **reactively infeasible midpoint remains infeasible**: separate solver convergence must never be relabelled as acceptable operating constraints. Internal Newton residual evaluations are diagnostic mathematical work units, **not** interchangeable with an ORPD physical-solver-entry budget. No I65 switch candidate, official held-out COCO cell or new optimizational experiment is authorized.

**NEXT STEP:** review real one-shot `smoke.json` and byte-level hashes. Preserve any missing algorithm support, nonconvergence, disagreement or original negative data verbatim. Supervisor M1–M6 novelty/scope and an explicit unified physical cost model remain unresolved.
