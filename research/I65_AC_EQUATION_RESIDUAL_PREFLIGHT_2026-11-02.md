# I65 — independent AC-equation residual witness, pre-runtime gate

**Date:** 2026-11-02. **Baseline:** `owlCoder/gadapt/main` at `16ae5cb4d2b40644a7b9040902f501f269d9152f`.
**Scientific status:** `novelty not established / DRAFT / NO-FREEZE / held-out COCO NOT_RUN`.
**Gate status:** **15 synthetic/analytic tests PASS; real PYPOWER development-case comparison NOT_RUN at document creation.** No new optimizer, frozen-source change, or benchmark.

## Mathematical object and independence claim

Given **already solved** MATPOWER-format `bus/gen/branch` numeric arrays and `baseMVA`, a new research-only [`ac_residual_witness.py`](i65/ac_residual_witness.py) builds complex network admittance directly with NumPy, without importing PYPOWER or calling `runpf`/`makeYbus`:

- For each in-service branch, `y=1/(r+jx)`, tap `a=t exp(j theta)` (with `t=1` if omitted), charging `b`, build `Yff=(y+j b/2)/|a|²`, `Yft=-y/conj(a)`, `Ytf=-y/a`, `Ytt=y+j b/2`. Add shunts `(GS+j BS)/baseMVA` to Ybus's diagonal.
- For the supplied bus complex voltages `V_i=VM_i exp(j VA_i pi/180)`, compute injection `S_i=baseMVA*V_i*conj((Ybus V)_i)` and compare with `sum(online PG+jQG)_i - (PD+jQD)_i` in MVA. `max |S_i-S_spec_i|` must not exceed the **predeclared 0.001 MVA** tolerance for the planned development-case comparison.
- Compute `S_from=baseMVA*V_from*conj(Yff V_from+Yft V_to)` and similarly `S_to`, compare each complex branch flow to supplied `PF/QF/PT/QT` with **predeclared 0.00001 MVA** absolute complex tolerance. Report separate active losses `sum(real(S_from+S_to))` and their difference versus the reported sum of PF+PT.
- Reject malformed dimensions, nonfinite inputs/flow outputs, duplicate bus IDs, missing active endpoints, nonpositive voltages, zero series impedance, invalid taps and tolerances. The `AC_RESIDUAL_PASS` code is explicitly **not** a physical `VALIDATED_WITNESS` claim.

For the AC branch formulas, compare the official [MATPOWER `makeYbus` reference](https://matpower.org/docs/ref/matpower7.0/lib/makeYbus.html), lines 48–71. This is separately written implementation of the same **model equations**; it is not a second numerical AC PF/OPF solver, not an independent data source, and not proof of all ORPD constraints. The original I58 checker still shares PYPOWER. AC residual `PASS` is a necessary consistency check of a *provided solved state*, not an independent physical model or sufficient proof of network operational feasibility, I65 novelty, or optimizer performance.

## Completed low-cost falsification

Fifteen [`test_ac_residual_witness.py`](i65/test_ac_residual_witness.py) standard-library unittest cases **15/15 PASS** under Python 3.13.5 and NumPy 2.3.5 (no PYPOWER required), including:

- A hand-derived **2-bus resistive** example with `V1=1`, `V2=0.98`, `r=0.1 pu`, `baseMVA=100`: from-end `20.0 MW`, to-end `-19.6 MW`, resulting `0.4 MW` loss, all matched to numerical tolerance.
- A falsified 0.4-MW loss budget, 1-MW generation perturbation, wrong reported line flow, tap/phase shift perturbation, wrong/nonfinite tolerances, duplicate bus ID, missing branch bus, nonfinite angles, in-service zero impedance, incomplete solved line data, shunt reactive sign and open-line conditions.
- Git blob SHA of code: `8e6bb1b4cf78578c15315be3b4cff127bc2c8036`; tests: `70c1faa5db2d936749d012d525decc04dc588acf`. Local code was byte-for-byte verified before publication. No historical experiment re-run.

## Bounded real-case falsification plan (not yet evidence)

Added opt-in [`smoke_ac_residual_witness.py`](i65/smoke_ac_residual_witness.py) (blob `1f51f95f288b55f3f37cb9c31d75c4151df21562`), which uses only the already documented I58 development scenario `case30,j=1,R=17`. Restore the original research-root aliases, instantiate the historical I58 problem (one `runopf` setup), construct a fixed grid-midpoint candidate **without running any optimizer**, execute one PYPOWER `runpf` call to obtain a solved operating point, and independently recompute all 30 bus balance residuals, 41 branch flows, and losses. In memory only, falsify the solved generator `PG` by 1 MW **without another solver call** and demand `AC_RESIDUAL_FAIL`.

Predeclared API-entrypoint expectations: `setup: runopf=1`, `witness: runpf=1`, **zero search calls**, with the 15 fast unit tests separate. The script records exact source Git hashes, both residual outcomes and typed solver-entrypoint events. Its one-shot [manual rerun-linked GitHub workflow](../.github/workflows/research-i65-ac-residual-one-shot.yml) runs on Python 3.12/PYPOWER 5.1.19, has no push/PR/schedule trigger and an 8-minute cap; all logs are SHA-256 hashed.

**Falsification rule:** if the real PF solution does not meet the *already fixed* 0.001 MVA nodal mismatch and 0.00001 MVA branch-flow difference, report a **negative** result and investigate assumptions; do not tune thresholds merely to pass. Nonconvergence or different solver counts also FAIL the gate. The audit does **not** seek low objective loss, feasibility improvement or scientifically novel algorithm policy.

## Separate unsolved research budget/oracle decision

Do not identify the historical `Evaluator.calls` count, the wrapper `AuditedBudget.attempts`, the number of numerical solver **API entrypoints**, or internal PF/OPF Newton iterations as equal quantities. A future protocol must explicitly name its budget resource and include setup, exception attempts and witness charges consistently. This separate accounting decision has **not** been approved by a supervisor (M1–M6), and this residual check cannot certify true model-independence. COCO confirmation, actual optimizer coupling and performance tests remain **NOT_RUN / NO-FREEZE**.

## CI activation correction (2026-11-02)

The initial one-shot workflow pointed to the already third-level `workflow_run` job `#41385833963` attempt 2. That chained attempt completed successfully, **but this fourth-level downstream job did not start**: GitHub Actions explicitly forbids chaining more than three `workflow_run` levels (GitHub Docs: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows). This is a **CI trigger limitation**, not evidence that the AC residual check passed or failed.

The new workflow is instead scoped to the *original root manual* job `#41357664531`, **attempt 3**, as the new first-level downstream child. That historical root job at its old SHA is known to fail due to a pre-fixed virtualenv bug: its result is **NOT** used as evidence of the new residual checker and **does not need to pass**. The child checks out the **latest main commit**, validates that the independent residual source is present, and only its own unit/smoke logs can determine PASS/FAIL. No push-trigger or optimization experiment was introduced.
