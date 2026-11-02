# I65 — independently implemented numerical Newton AC power flow validated against PYPOWER

**Date:** 2026-11-02. **Software result:** **PASS on one preregistered, non-held-out, fixed-midpoint I58 case30/j1 development case**. No optimization search, held-out COCO or scientific-method freeze was performed.
**Source commit:** `13938263110c239b8ee14e2e60739a8ffdb0839e`, `owlCoder/gadapt/main`.  
**GitHub Actions:** [run #41413792862](https://github.com/owlCoder/gadapt/actions/runs/41413792862), `completed / success`.  
**Artifact:** [i65-independent-newton-41413792862](https://github.com/owlCoder/gadapt/actions/runs/41413792862/artifacts/13127200204), ZIP SHA-256 `52f7e63a6c4c3fc2be735e214a93831adf0d576aac95f050f98adcb9adcb7817`.  
**Original smoke SHA-256:** `00b39399f40797105fcb7e6e950f4515aa91bb59eb3ea50e9e5ccc6542c90a5a`; [byte-identical raw `smoke.json`](I65_INDEPENDENT_NEWTON_SMOKE_2026-11-02.json) also preserved in Git (blob `91b26ec5de4f550aea2ac066f9a12c8955ed6b04`).

## Preregistered direct numerical PF comparison

See the [pre-run mathematical model and fixed tolerances](I65_INDEPENDENT_NEWTON_PREFLIGHT_2026-11-02.md), committed *before* CI execution. A separately written [NumPy-only polar Newton solver](i65/independent_ac_newton.py) built its own Ybus, selected REF/PV/PQ equations and **solved from a flat initial angle and 1.0-pu PQ voltage** for a fixed I58 development-case grid midpoint. It did not import PYPOWER, read any PYPOWER result, use PYPOWER as a warm-start, perform candidate selection or run an optimizer. Only after its independent solve did the diagnostic call **one** `pypower.api.runpf` to produce the existing-solver numerical reference.

| Parameter | Preregistered criterion | Observed | Verdict |
|---|---:|---:|---|
| Analytic/failure-mode unittest | 16/16 | **16/16 PASS** | PASS |
| Independent Newton convergence | 20 iterations max, mismatch at most 1e-9 pu | **3 iterations**, residual `1.3362914314397933e-10 pu` | PASS |
| Maximum difference of 30 bus voltage magnitudes | at most `5e-4 pu` | **`3.1086244689504383e-15 pu`** | PASS |
| Maximum wrapped difference of 30 bus voltage angles | at most `5e-3°` | **`5.684341886080802e-14°`** | PASS |
| Difference of total active **branch** losses | at most `5e-3 MW` | **`1.141309269314661e-13 MW`** | PASS |
| PYPOWER actual solution | must converge | **converged** | PASS |
| PYPOWER API budget | one scenario OPF and one witness PF; no optimizer search | **1 `runopf` setup / 1 `runpf` witness / 0 search** | PASS |

The independent solver reported branch active loss `3.114081587468852 MW` versus PYPOWER `3.114081587468966 MW`. Its separate numerical residual ledger recorded **325 evaluations of the independently implemented mismatch function**, including central-difference Jacobian and line search calls. These are not interchangeable with the PYPOWER API attempt ledger or a physically charged I65 candidate-evaluation budget. It solved one 30-bus model with 5 PV buses and 24 PQ buses.

The 16 standalone tests included separate **two-bus resistive, exact 0.4 MW branch loss** and a separate **three-bus PQ/PV/REF** case with known voltages; additional tests check phase shifters, line charging, shunts, bad bus types, missing online slack, conflicting generator voltage setpoints and disconnected/singular cases. An explicitly chosen 5-MW conductance shunt proved that the new solver reports **branch loss 0.4 MW separately from net active injection 5.4 MW**, avoiding false loss comparisons.

## Byte-level provenance, independently checked

The raw artifact ZIP SHA-256 was recomputed and matched GitHub's own digest. Recomputed each of the **4/4** SHA-256 file hashes listed in the original `hashes.sha256`:

| File | Verified SHA-256 |
|---|---|
| `restore.log` | `b30a798b89b330808732f7473c8db60eeba02c2665c0ed53de7ebcf6f7f7278a` |
| `unit.log` | `edca7dbc675abbf81935beedc60bd24a22188dfbee75e35cc152f4cbcd2fa2f0` |
| `smoke.json` | `00b39399f40797105fcb7e6e950f4515aa91bb59eb3ea50e9e5ccc6542c90a5a` |
| `commit.txt` | `88dcac003c0da0ee007bf6b4a32e1ea2efcda3b908d6c0e5763f0a745cc01974` |

The original `smoke.json` embedded a solver API event-trace hash, independently recomputed after removing the hash member and reserializing in canonical compact sorted-key JSON. Its recorded SHA-256 `8d372ca753d6a75584519a6a712e01b23e3df43df555d56267cddc641938935f` matched exactly.

Git blob SHA identities from that actual raw smoke were independently compared with committed sources:

| Source | Verified Git blob SHA |
|---|---|
| Frozen `research/legacy/flat/iteration56_orpd.py` | `43f2f279f7e6362250dc9277e58e0d939a98c12f` |
| Frozen `research/legacy/flat/iteration58_validation.py` | `9747faea9c31526a163bd8439c74708214c07a3c` |
| Independent `research/i65/independent_ac_newton.py` | `268d0406a90fe7d314d4e01311ea2f4376084b2b` |

The full Git ancestry and all **341** legacy-root aliases were hash-verified and restored before testing, and no GAdapt package default or frozen historical result was changed.

## What has and has not been resolved

**Closed narrow gate:** **second, independently implemented numerical solution of the same classical AC PF model** on one preselected development scenario, independently reproduced voltages, angles and losses numerically to far better than preregistered tolerances. This strengthens the independence of the numerical-software cross-check compared with merely checking AC equations on a PYPOWER-supplied state.

**Still NOT proven or approved:** independent physical data/network model, independent measured grid truth, all ORPD scenarios, general solver correctness outside tests, new I65 optimizer method or its novelty, generator Q-limit enforcement, PV↔PQ switching under Q limits, allocation of individual QG among parallel generators, stochastic budget accounting across internal Newton residual evaluations, physically independent OPF/AC feasibility, complete operational feasibility, and confirmatory COCO f21/f24. The previously observed development midpoint remains **reactively infeasible** (`I56 reactive component=0.5991137833375748`) despite both PF solvers converging: PF convergence ≠ ORPD feasibility.

**NEXT STEP:** prepare for supervisor M1–M6 decision on whether numerical software-independence plus rigorous evaluation-integrity tooling meets the required dissertation contribution. Formalize the resource cost definitions for candidate objective attempts, PYPOWER PF/OPF API entries, **internal Newton residual calls**, rejected candidates, failures, setup, interstage and terminal witnesses in a prospective protocol; do not equate those counts. Without novelty and budget approval, candidate-C methods and held-out COCO remain `NO-FREEZE / NOT_RUN`.
