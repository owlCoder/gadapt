# I65 — Supervisor / independent reviewer decision delta (2026-11-03)

**Decision status:** UNSIGNED / NO-FREEZE / COCO NOT_RUN / OPTIMIZER NOVELTY NOT_ESTABLISHED. No decisions, registration states, or archived measurements have been altered.

## What was actually added today

| Evidence type | What was independently checked | Key result | What remains *unproven* |
|---|---|---|---|
| I64-R function-family sensitivity | All 21 per-pair variant/configuration ECDF means from the original pinned compressed analysis; exact original weights and four contrasts reconstructed | Registered c4 = +0.07079. Excluding all Rastrigin pairs gives post hoc point +0.04087; original H64r3 unchanged | No valid new LOO CI; generalization to new function families/Q matrices |
| I64-I2 single-run outcome audit | 16 pinned compressed I/I2 per-cell archives; 8 cells × 30 seeds × 3 selected algorithms = 720 archived run outcomes; four point contrasts reconstructed | Original IPOP–hybrid CVaR contrast = −0.12530676. One cell, `case39/j=3`, contributes −0.125; removal yields 7-cell point −0.00035058 | No new bootstrap CI or physical-witness validation; untested grid/model generalization |
| ORPD failure provenance | Historical `ok`, `calls`, best feasible outcome, seed indices, archived witness flag | Hybrid no-feasible seeds `68003015`, `68003018`, `68003028`; GAdapt no-feasible `68003023`; IPOP none for that cell | Mechanistic reason for no feasible witness; no new PF or optimizer replay |
| Diagnostics of saturation | Original per-cell CVaR and feasibility recomputed | `case39/j=4`: all three CVaRs = 1 despite feasible counts M 0/30, hybrid 1/30, IPOP 5/30 | A single aggregate tail statistic does not identify mechanism or industrial viability |

## Requested human decisions (not implied by this report)

**Statistical reviewer (M5):** Confirm that the manuscript explicitly labels both influence analyses as post hoc and reports original confidence intervals only for original registered estimands. Assess whether prospective multi-function/multi-Q and multi-network uncertainty quantification is necessary before *any* generalization claim. No retrospective redefining of weights, outcomes or alpha thresholds.

**Supervisor (M6/C1):** Decide whether a strictly scoped empirical/measurement-integrity dissertation can be justified from these carefully bounded results. No new optimizer novelty is demonstrated by either sensitivity analysis. Existing E3 / I2 negative results and all counterexamples must remain visible.

**Infrastructure reviewer (M3/C2–C5):** Interpret the `case39/j=3` feasibility failures only within the archived, fixed network/model and existing witness policy. A stored `witness_checked=true` is evidence of the original study's check, *not* proof that a second independent physical model has been validated in this review.

**Data/freeze reviewer (M1/M4/C6):** If further work is authorized, preserve the original source blobs and complete cheap full-clone replay. A future held-out COCO protocol needs its own pre-freeze, budgeting and human sign-off; none was granted here.

## Specific decision question

> May the two draft papers proceed to external technical review with these limitations and negative findings explicit, or is a prospectively designed robustness study on new objective families, independent orthogonal matrices and independent infrastructure cases required before submission?

A response to this memo does not itself constitute permission to change the original registered hypotheses, publish a novelty claim or execute new optimization/COCO/OPF experiments. Such permissions require separate, explicit documented decisions.
