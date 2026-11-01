# I64-E3: GAdapt → CMA-ES hybrid (global search followed by local refinement) — generated report

Specification: [ITERATION64_E3_SPEC.md](ITERATION64_E3_SPEC.md), frozen at `f228044`. Paired against archived E records by (cell, seed): 63 cells × 100 seeds, 12,000 physical objective calls per run.

## 1. Hypothesis decisions — one simultaneous family of five contrasts (α = 0.05, t* = 2.558, 20,000 replicates)

- **H64g1** (closing the rotation gap relative to GAdapt-M): **supported**.
- **H64g2** (tolerable harm on original+shift): **opposite**.
- **H64g3** (noninferiority to IPOP, margin 0.05): **undecided**.
- Overall supported: **False**; C_rot(GAdapt-M) = 0.0300.

| Contrast | Estimate | Lower | Upper |
|---|---|---|---|
| dA_rot(H-M) | 0.1029 | 0.09264 | 0.1132 |
| 0.8*CVaR_rot(M)-CVaR_rot(H) | 0.01212 | 0.009443 | 0.01479 |
| dA_nonrot(H-M) | 0.06535 | 0.06073 | 0.06996 |
| 1.5*CVaR_nonrot(M)-CVaR_nonrot(H) | -0.0006964 | -0.001109 | -0.0002838 |
| dA_rot(H-IPOP) | -0.04335 | -0.05189 | -0.03482 |

## 2. Aggregates by transformation

Functions and dimensions within functions have equal weights. "Median gap" is the weighted mean of cell medians of normalized gap; CVaR is the weighted mean of cell CVaR₀,₉(L).

**Original (orig)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.7022 | 0.0026 | 0.00101 |
| gadapt_hyb | 0.7628 | 0.0048 | 0.00216 |
| ipop | 0.7765 | 0.0122 | 0.00568 |
| cma | 0.7554 | 0.0156 | 0.0102 |
| bipop | 0.7717 | 0.0135 | 0.00594 |
| de | 0.6522 | 0.0082 | 0.00584 |

**Shifted (shift)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.7007 | 0.0025 | 0.0011 |
| gadapt_hyb | 0.7708 | 0.0043 | 0.00219 |
| ipop | 0.7701 | 0.0147 | 0.00855 |
| cma | 0.7697 | 0.0134 | 0.00749 |
| bipop | 0.7712 | 0.0140 | 0.00709 |
| de | 0.6542 | 0.0082 | 0.00578 |

**Orthogonally transformed (rot)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.6167 | 0.0300 | 0.0108 |
| gadapt_hyb | 0.7196 | 0.0119 | 0.00443 |
| ipop | 0.7630 | 0.0158 | 0.00913 |
| cma | 0.7603 | 0.0145 | 0.00996 |
| bipop | 0.7636 | 0.0151 | 0.00889 |
| de | 0.6124 | 0.0391 | 0.0335 |

## 2b. Equal-weight average across all three transformations (descriptive)

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.6732 | 0.0117 | 0.00429 |
| gadapt_hyb | 0.7511 | 0.0070 | 0.00293 |
| ipop | 0.7699 | 0.0142 | 0.00779 |
| cma | 0.7618 | 0.0145 | 0.00921 |
| bipop | 0.7688 | 0.0142 | 0.00731 |
| de | 0.6396 | 0.0185 | 0.015 |

## 3. Interpretation

The hybrid is **not GAdapt alone**: CMA-ES consumes the last 70% of the budget. This evaluates a practical recipe of global exploration followed by refinement, not a standalone GAdapt property. No new-method claim is justified (hybrid optimizers are established prior art). Frozen decisions yielded a mixed outcome (Section 1). Descriptively, post hoc on the same archive, the hybrid has higher original/shift CVaR than GAdapt-M and preset, but lower CVaR than the shown CMA configurations. Under orthogonal transformation its A is below IPOP; noninferiority was not established. This experiment alone did not identify each phase's independent contribution without a dedicated ablation.
