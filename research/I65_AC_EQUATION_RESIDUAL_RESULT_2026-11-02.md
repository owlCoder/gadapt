# I65 — independent NumPy AC residual check: real 30-bus development result

**Date:** 2026-11-02. **Verdict:** **PASS for one prespecified developmental AC operating-point residual; independent numerical solver and I65 scientific freeze remain NOT_ESTABLISHED.**  
**GitHub CI:** [#41395941943](https://github.com/owlCoder/gadapt/actions/runs/41395941943), `status=completed`, `conclusion=success`.  
**Exact tested HEAD:** `beae02c25618516c4b9f1950398728af3ed9445e`.  
**Artifact:** [i65-ac-residual-diagnostic-41395941943](https://github.com/owlCoder/gadapt/actions/runs/41395941943/artifacts/13119641253); **ZIP SHA-256:** `0c35fe30b07d8b5c3e78671d97a303f97f1a994e78f47d98dec50727136b9d83`.

## 1. Prespecified narrow falsification executed

The [pre-run scope and fixed tolerances](I65_AC_EQUATION_RESIDUAL_PREFLIGHT_2026-11-02.md) were committed before the CI execution. The one **non-held-out development** IEEE `case30`, `j=1`, `R=17` scenario used the frozen I58 scenario builder (one `runopf` for setup), one `pypower.api.runpf` for the midpoint control vector, and a **NumPy-only separately written AC equation evaluator** for the resulting operating point. No GAdapt, CMA, DE or COCO search or repeated-seed experiment was run.

| Precommitted check | Threshold / expectation | Actual observed result | Verdict |
|---|---|---|---|
| All 15 synthetic / analytic tests | 15/15 PASS | **15/15 PASS** | PASS |
| Nodal `max(abs(S_calc-S_spec))` | at most `1e-3 MVA` | **1.532843850089971e-08 MVA** | PASS |
| Max complex branch flow recomputation difference | at most `1e-5 MVA` | **4.0474535189761156e-13 MVA** | PASS |
| Independent formula branch active losses | comparison only, no tuned loss target | **3.1140815874688497 MW** | Reported |
| PYPOWER's published PF+PT active losses | comparison only | **3.114081587468966 MW** | Agreement |
| Loss recomputation minus PYPOWER | report exact difference | **-1.163513729807164e-13 MW** | Reported |
| In-memory false solved `PG` perturbation | `+1 MW` injection must FAIL residual | `AC_RESIDUAL_FAIL`, mismatch **1.000000000000064 MVA** | PASS |
| Solver API entrypoints | 1 `runopf` setup + 1 `runpf` witness, no search | **1 + 1**, no search | PASS |
| Source arrays / convergence | development `case30` / `j=1` | **30 buses, 41 branches, 6 active gens**, PF converged | PASS |

The fresh residual checker does not invoke PYPOWER, its `makeYbus` or its numerical power-flow solver. It reconstructs nodal admittances and complex branch powers using raw solved arrays and MATLAB/MATPOWER-formatted column indices, including line charging, bus shunts, transformer tap magnitude/phase angle and line status. The underlying mathematical identities agree with the documented [MATPOWER `makeYbus` equations](https://matpower.org/docs/ref/matpower7.0/lib/makeYbus.html). This is **independent implementation of power-flow equations**, NOT an independent nonlinear AC solver or independent-physics external oracle.

## 2. Byte-level evidence verification

Downloaded the real GitHub Actions ZIP artifact. Locally recomputed its SHA-256 and **all 4/4** individual archive file hashes from the signed `hashes.sha256` ledger:

| File | SHA-256 independently verified |
|---|---|
| `restore.log` | `b30a798b89b330808732f7473c8db60eeba02c2665c0ed53de7ebcf6f7f7278a` |
| `unit.log` | `45f4b7e53ead4c492d6ca4f789fa4664582ded2630751e6c2e8522c70af4aa3c` |
| `smoke.json` | `6f3390d06d3bc09d3194b555c50adc0149092a6691b50e994df0f0330a32641d` |
| `commit.txt` | `fb03e3e80494b2c38b5627ef27b7a41eeefb67a42d87c554d7e2f7ba5a712fe8` |

Recomputed the embedded `solver_api_entrypoints` evidence hash from compact sorted-key UTF-8 JSON (excluding the `sha256` field) and matched the original: `8d372ca753d6a75584519a6a712e01b23e3df43df555d56267cddc641938935f`.

The source Git blobs listed in `smoke.json` matched their immutable repository versions:
- Frozen historical I56 `iteration56_orpd.py`: `43f2f279f7e6362250dc9277e58e0d939a98c12f`
- Frozen I58 `iteration58_validation.py`: `9747faea9c31526a163bd8439c74708214c07a3c`
- New research-only `ac_residual_witness.py`: `8e6bb1b4cf78578c15315be3b4cff127bc2c8036`.

The logged `restore.log` said all **341** historical aliases were hash-verified and restored, the `unit.log` shows exactly **15/15 PASS** on Python `3.12.15` with `numpy==1.26.4` and `PYPOWER==5.1.19` installed by the workflow.

## 3. CI trigger correction preserved transparently

The first attempted one-shot followed a three-level nested `workflow_run` chain and GitHub correctly declined to start a fourth-level child. Per [GitHub's documented maximum of three chained levels](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), the new audit was re-scoped directly to original manual workflow `#41357664531`, **attempt 3**; this root old-code workflow fails for its previously documented virtualenv bug. Its result is **only a trigger**, not a pass criterion or scientific evidence. The new job checks out `beae02c2` on current `main` and independently passed all its own audit gates. Extra legacy one-shot listeners were correctly skipped by their exact-run guards.

## 4. Strict scientific boundary

**What this result now establishes:** one 30-bus development solution generated by PYPOWER obeys independently recomputed AC nodal balance and branch power equations within predeclared numeric tolerances, and a deliberately falsified +1-MW generator injection is rejected. This is new directly measured supporting **software/model equation consistency** evidence, not a new optimizer result.

**What remains NOT proven:** an independently implemented nonlinear AC solver, independent external data/model family, all operational constraints (voltage, thermal, reactive, slack feasibility), internal OPF/PF Newton steps and subsolves, stochastic search budgets/fitness, full I65/CMA integration, official COCO f21/f24 confirmation, algorithmic novelty and mentor M1–M6 approval.

**NEXT STEP:** independently recompute (and adversarially test) all operational constraints and compare against reported violations on a small development scenario **without generating new optimizer search results**; then decide whether a *separate* solver implementation and precisely frozen aggregate solver-call budget are required for scientific acceptance. The dissertation candidate remains `novelty not established / NO-FREEZE / COCO NOT_RUN`.
