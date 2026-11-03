# I65 — exact archived I64-I2 bootstrap replay and adversarial ORPD cell-dropout audit

**Date:** 2026-11-03. **Status:** supplementary, read-only verification for the two doctoral manuscript DRAFTS. **Scientific status unchanged:** `NO-FREEZE`, `COCO NOT_RUN`, originality `NOT_ESTABLISHED`, M6/C1 independent review unsigned. This work **did not run any optimizer, power-flow, OPF or new stochastic experiment**. It re-sampled **existing I64-I/I2 outcomes** as a reproducibility check.

## 1. Source, transfer and validation

The same frozen data underlying [`I64-I2`](../../ITERATION64_I2_REPORT_SR.md) comprises 8 ORPD cells × 30 paired seeds × 3 algorithms = **720 archived outcomes**. For each cell, the pre-existing original `research/results/iteration64_i/run_part_{ci}.json.gz` and `iteration64_i2/run2_part_{ci}.json.gz` were fetched through GitHub at the original archived blob IDs pinned in [`i64_i2_cell_influence.py`](i64_i2_cell_influence.py). They were decompressed and read using independent ZIP/DEFLATE handling in the connector session, then transferred as 720 little-endian IEEE-754 double-precision loss values. Exactly the original scalar transform was applied: a missing independently witnessed feasible candidate maps to `L=1, P=0`; otherwise `G=max((best_feasible-r)/r,0)`, `L=G/(1+G)`, `P=1`. All seeds, task labels and physical call counts were checked at extraction.

The transformed 8×3×30 arrays were independently validated against **all four original I64-I2 point contrasts**, agreeing with the frozen source to within approximately `1e-16`. This blocks unnoticed transfer corruption in the chosen contrasts, although point agreement alone would not guarantee equality of all individual losses. The original I64-I2 analysis file is Git blob `2b38375126a43128dba37aaf7966b92eb6df8691`; see [`i64_i2_bootstrap_replay.py`](i64_i2_bootstrap_replay.py) for the full-clone raw-archive reproduction alternative. The portable derived array was used locally to execute the following audit; it is **not** described as the original compressed source.

## 2. Exact independent replay of the PRECOMMITTED eight-cell simultaneous inference

Ran the previously prepared `i64_i2_bootstrap_replay.py` with **20,000** bootstrap iterations, `numpy.random.default_rng(68)`, common resampling indices per source cell across all algorithms, an equal-weight average over all eight fixed ORPD cells, `CVaR_0.9` as the mean of the three largest losses from 30 seeds, and a simultaneous studentized max statistic with 97.5th percentile in line with the archived I2 script. Both feasibility fallback cases and all four contrasts follow the frozen original code.

**13 of 13 comparisons against the original archived numbers were EXACT (max absolute difference = 0.0):** 4 estimates, 8 simultaneous bounds and critical `t*=3.4133099733799344`.

| Frozen contrast | Estimate | Simultaneous lower | Simultaneous upper |
|---|---:|---:|---:|
| CVaR(M) − CVaR(H) | −0.0798917083 | −0.2656240619 | +0.1058406452 |
| P(H) − P(M) | −0.0041666667 | −0.0354803240 | +0.0271469907 |
| **CVaR(IPOP) − CVaR(H)** | **−0.1253067611** | **−0.2502239068** | **−0.0003896154** |
| P(H) − P(IPOP) | −0.0291666667 | −0.0642794190 | +0.0059460856 |

This meaningfully **closes the exact archived statistical bootstrap reproduction gap for I64-I2**. It does **not** independently replicate the original physical AC model, solver, optimization trajectories, or feasibility witness. Frozen decisions remain `H64h1=UNDECIDED`, `H64h2=OPPOSITE`.

## 3. Exploratory seven-cell bootstrap after deleting the identified influential cell

The original eight-cell IPOP-minus-hybrid CVaR contrast of `−0.1253067611` has a signed contribution of `−0.125` from `case39/j=3`. The three hybrid infeasible seeds in that cell are **68003015, 68003018, 68003028**; IPOP has 0 infeasible runs in this cell (30/30 successes). This cell alone contributes ~**99.755%** of the negative signed aggregate. It was selected for deletion **because of its observed influence**, so the following is **post hoc** and **not** a preregistered contrast/decision family. Selection multiplicity is **not adjusted** and all confidence bounds are descriptive seed-only diagnostics for the seven fixed retained cells.

With those seven fixed cells, re-ran 20,000 matched-seed bootstrap replicates, same seed 68 and 97.5% max-t procedure, now renormalizing the retained cells to weights 1/7. The critical value is **`t*=2.8301833981661795`**.

| Exploratory contrast after excluding `case39/j=3` | Point | Lower | Upper |
|---|---:|---:|---:|
| CVaR(M) − CVaR(H) | +0.003933286 | +0.002046149 | +0.005820422 |
| P(H) − P(M) | +0.004761905 | −0.008407627 | +0.017931437 |
| **CVaR(IPOP) − CVaR(H)** | **−0.000350584** | **−0.001306191** | **+0.000605023** |
| P(H) − P(IPOP) | −0.019047619 | −0.043938133 | +0.005842895 |

**Interpretation:** Removing the dominant source cell changes the estimand (the set of eight ORPD conditions is no longer represented). The exploratory interval for the IPOP tail contrast now includes zero. The post hoc seven-cell GAdapt-minus-hybrid CVaR contrast is positive in this resampling exercise, but must **not** be reported as a new confirmatory validation of the hybrid or a replacement for registered H64h1/H64h2.

The retained `case39/j=4` has an all-method CVaR saturation at 1.0 while feasibility differs. Across all eight cells, the hybrid has **7 fewer feasible hits out of 240** than IPOP, of which **4** are attributable to `case39/j=4` and **3** to `case39/j=3` (net differences). A tail statistic alone hides the former deficit.

## 4. Thesis relevance and next decision

The confirmed scientific issue is **concentration of tail risk under feasibility failure**, in a limited fixed grid of ORPD tasks. The conceptual point is useful for an empirical robustness/evaluation-integrity thesis, not a new GA/CMA theorem. Reporting only a significant aggregate would hide the three-seed failure mode; reporting only the seven-cell sensitivity would hide the original adverse frozen verdict. Report both. Prospective mechanism/novelty tests require actual approved preregistration, independent physics validation and independent prior-art adjudication; no new COCO/PF or optimizer study is authorized by this review.

## 5. Reproduction commands

On a complete checkout of `owlCoder/gadapt` containing the original frozen results, from the `research/i65/archive_review/` directory:

```sh
python i64_i2_bootstrap_replay.py --repo-root ../../../ --output exact_i2_bootstrap_replay.json
python i64_i2_posthoc_dropout_bootstrap.py --repo-root ../../../ --output exploratory_i2_cell_dropout.json
python -m pytest -q test_i64_i2_posthoc_dropout_bootstrap.py
```

The original Git blobs remain unchanged. **Do not** mistake this source replay and exploratory interval for a new infrastructure validation or signed supervisor approval.
