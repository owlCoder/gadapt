# I65 independent AC generation/dispatch reconstruction — preregistered software cross-check

**Date:** 2026-11-02. **Baseline:** `owlCoder/gadapt/main` at `ea9cc85ea97b28582d4d2c7df7546d00c7d20296`.  
**Gate at publication:** **14/14 local analytic/adversarial tests PASS**. Real PYPOWER vs independently reconstructed generation/flows/constraints **NOT_RUN** until separately triggered. No optimizer, held-out COCO, source substitution or novelty claim.

## Objective and mathematical scope

Earlier [independent flat-start NumPy Newton](I65_INDEPENDENT_NEWTON_RESULT_2026-11-02.md) reproduced *30-bus voltages, angles and branch losses* under the exact same original input as PYPOWER, but did **not** reconstruct the solved generator outputs `QG` at PV/REF buses and `PG` at the REF bus. Those are outputs, not specified input values, in standard AC PF. Can we derive them without reading PYPOWER's solved state, then validate the original I56 voltage/reactive/reference/thermal violations, including its **previously observed reactive infeasibility**?

Prior-method grounding: [MATPOWER AC Power Flow documentation](https://matpower.app/manual/matpower/ACPowerFlow.html) says PV-bus `PG` and `VM` are inputs; reference-bus `PG` and PV/reference `QG` are determined by the remaining AC equations. Ordinary Newton PF does **not** enforce Q limits by default. See also [MATPOWER runpf documentation](https://matpower.org/docs/ref/matpower7.0/lib/runpf.html). The mathematics are established prior art; **novelty NOT established**.

## Research-only implementation

[`research/i65/independent_ac_dispatch.py`](i65/independent_ac_dispatch.py) accepts the **unsolved** original case and a **CONVERGED** result from the independently implemented NumPy Newton solver. It imports **no PYPOWER** and reconstructs:

1. Independent bus complex injections `S_i=baseMVA*V_i*conj((Ybus V)_i)`, where `Ybus` comes from independently coded AC case assembly.
2. At a **single online generator per controlled REF/PV bus**, `QG = imag(S_i) + QD_i`; at the reference generator also `PG = real(S_i) + PD_i`. All PV generator `PG` remain input-fixed.
3. Independent branch `PF,QF,PT,QT` from complex branch admittance, line charging, tap and phase shift; out-of-service branches report zero flow.
4. Independent checking of all AC nodal balances and branch flow residuals by the existing NumPy-only [equation verifier](i65/ac_residual_witness.py), and the four original I56-style [operational penalty aggregations](i65/orpd_operational_witness.py), including the **reactive infeasibility** result.

**Fail-closed domain**: only one online generator per REF/PV bus, no online PQ-bus generators, single REF, well-formed MATPOWER matrices, nonzero voltage magnitudes and bounded PF solver convergence. Multiple online generators on a shared bus require *additional assumptions* about individual reactive-power allocation; **do not invent an allocation or claim verification there**. No generator Q limits are enforced by this PF solver; it merely reports violations.

### Completed local tests

**14/14 actual Python 3.13.5 / NumPy 2.3.5 local unit tests PASS**, no PYPOWER imports or calls. Their SHA-256 console digest is `f3ae5994aa99d4237b9cb42a3e705bf8a0d96f619d73e50c9d2f557262b9a722`. The exact source Git blobs are:

- `independent_ac_dispatch.py`: `36aa3c819a6abde58153f27d7dd5efa5bcbf0ccc` (SHA-matched locally)
- `test_independent_ac_dispatch.py`: `2d6d6059bc5639bbf5fcf4e112cd5e66009893be` (SHA-matched locally)

Tests include the independently derived 2-bus `PG_ref=20.0 MW`, branch powers `20.0/-19.6 MW`, loss `0.4 MW`; a 19-MW PMAX cap correctly declares that numerically converged point **infeasible**; nonzero slack `QG` reconstruction, externally perturbed voltage vector rejection, no-mutated-input guarantee, offline generator, zero-flow offline branch, ambiguous multi-generator and PQ generator rejection, negative voltage, no convergence and voltage-limit violation.

## Precommitted, bounded *real* cross-solver diagnostic

A one-shot [Python 3.12 GitHub Actions workflow](../.github/workflows/research-i65-independent-dispatch-one-shot.yml) is bound to root manual workflow `#41357664531` **attempt 8**, no push/PR/schedule. Restores all historical source aliases with SHA verification and runs the **14 new tests + 16 previous Newton tests + 17 previous I56 constraint tests (47 expected)**; one fixed already used development I58 `case30,j=1,R=17` midpoint only, with:

- **One** `runopf` original scenario setup, **zero optimizer search**, **one** `runpf` as PYPOWER reference;
- Independently solve the original **unsolved** case *before* PYPOWER is called, then derive individual `QG`, slack `PG`, branch flows, AC residuals and all I56 constraints from that independent solution;
- Max `QG` difference between active generator rows **≤ 0.001 MVAr**; max reference `PG` difference **≤ 0.001 MW**; max complex branch end power difference **≤ 0.001 MVA** at each end; each I56 component difference **≤ 1e-6** (dimensionless original mixed-unit convention); all required inputs/outputs finite; original midpoint must remain `feasible=false` in **both** implementations;
- Solver same fixed Newton settings as the previous independent validated run (at most 20 iterations, 1e-9 pu residual, 1e-6 central finite-difference step); **120s smoke cap, 8-minute total job**, no additional optimization runs. Raw logs are hashed even on failure.

**Falsification rules:** any nonconvergence, unsupported generator topology, original PF mismatch, spurious `feasible=true`, changed source digest, or failed residual/constraint comparison is **FAIL** and preserved. Do not change these thresholds, candidate, or model inputs in response to real CI failure. The job is test infrastructure, not an I65 switch method or confirmatory scientific experiment.

## Limitations and no-freeze decision

Even after PASS, this would independently reconstruct REF/PV generation and line flows for **one pre-used development case under the same classical AC mathematical model and same case data**. It is not an independent real-world model, a complete OPF, physical measurements, Q-limit-enforcing PF, new I65 optimizer, general input-data certification or nested physical-solver-work budget. The prior fixed midpoint's reactive penalty `0.5991137833375748` was measured by I56 and its independent penalty arithmetic; it remains a **negative feasibility finding** until verified from this independent numerical reconstruction (not presumed).

**GO:** one low-cost falsification and source provenance comparison only.  
**NO-GO:** claims of independent physical truth, original optimizer method, frozen experimental protocol or held-out COCO confirmation. Supervisor M1–M6 and C1–C6 choices remain undecided; I65 `novelty not established / DRAFT / NO-FREEZE / COCO NOT_RUN`.
