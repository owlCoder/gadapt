# I64-E4: Opt-in compensatory mutation (`compensatory_mutation`) with controls — generated report

Specification: [ITERATION64_E4_SPEC.md](ITERATION64_E4_SPEC.md), frozen at `226c757`, amendment A1 at `6368959`. Paired with archived E results by (cell, seed): 63 cells × 100 seeds, 12,000 actual objective calls.

## 1. Hypothesis decisions — one simultaneous family of seven contrasts (α = 0.05, t* = 2.665, 20,000 replicates)

- **H64k1** (closing the gap to GAdapt-M under rotation): **undecided**.
- **H64k2** (tolerable harm on original+shift): **supported**.
- **H64k3** (gated method better than randomly permuted-partner control under rotation): **undecided**.
- **H64k4** (gated method better than Bouter-style resampling control): **undecided**.
- **H64k5** (noninferiority to IPOP, margin 0.05): **opposite**.
- Core (k1–k4) supported: **False**; C_rot(GAdapt-M) = 0.0300.

| Contrast | Estimate | Lower | Upper |
|---|---|---|---|
| dA_rot(G-M) | 0.01403 | 0.005221 | 0.02284 |
| 0.8*CVaR_rot(M)-CVaR_rot(G) | -0.003166 | -0.006589 | 0.0002576 |
| dA_nonrot(G-M) | 0.003022 | -0.00108 | 0.007123 |
| 1.5*CVaR_nonrot(M)-CVaR_nonrot(G) | 0.0008672 | 0.0005319 | 0.001202 |
| dA_rot(G-permuted) | -0.002892 | -0.01235 | 0.00657 |
| dA_rot(G-resample) | -0.00292 | -0.01137 | 0.005534 |
| dA_rot(G-IPOP) | -0.1322 | -0.142 | -0.1224 |

## 2. Aggregates by transformation

Equal weighting of functions and dimensions within functions. The median gap is the weighted mean of cell medians of normalized gap; CVaR is the weighted mean of cell CVaR₀,₉(L).

**Original (orig)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.7022 | 0.0026 | 0.00101 |
| gadapt_cg | 0.7022 | 0.0029 | 0.00151 |
| gadapt_cu | 0.6790 | 0.0044 | 0.00163 |
| gadapt_cp | 0.6836 | 0.0047 | 0.00193 |
| gadapt_cr | 0.6762 | 0.0040 | 0.0017 |
| ipop | 0.7765 | 0.0122 | 0.00568 |
| cma | 0.7554 | 0.0156 | 0.0102 |
| bipop | 0.7717 | 0.0135 | 0.00594 |
| de | 0.6522 | 0.0082 | 0.00584 |

**Shifted (shift)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.7007 | 0.0025 | 0.0011 |
| gadapt_cg | 0.7067 | 0.0031 | 0.00134 |
| gadapt_cu | 0.6821 | 0.0043 | 0.00204 |
| gadapt_cp | 0.6915 | 0.0046 | 0.00182 |
| gadapt_cr | 0.6798 | 0.0041 | 0.0023 |
| ipop | 0.7701 | 0.0147 | 0.00855 |
| cma | 0.7697 | 0.0134 | 0.00749 |
| bipop | 0.7712 | 0.0140 | 0.00709 |
| de | 0.6542 | 0.0082 | 0.00578 |

**Orthogonally transformed (rot)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.6167 | 0.0300 | 0.0108 |
| gadapt_cg | 0.6308 | 0.0272 | 0.0134 |
| gadapt_cu | 0.6286 | 0.0278 | 0.0118 |
| gadapt_cp | 0.6337 | 0.0292 | 0.0107 |
| gadapt_cr | 0.6337 | 0.0292 | 0.0121 |
| ipop | 0.7630 | 0.0158 | 0.00913 |
| cma | 0.7603 | 0.0145 | 0.00996 |
| bipop | 0.7636 | 0.0151 | 0.00889 |
| de | 0.6124 | 0.0391 | 0.0335 |

## 3. Cautious post-hoc interpretation

The small A gain relative to GAdapt-M under Q (ΔA ≈ +0.014) is not distinguishable from either the randomly permuted partner or Bouter-style resampling control (intervals include zero), so it **cannot be attributed to exploiting elite correlations**. A CVaR reduction of at least 20% was not established (the relevant contrast includes zero). On original+shift only the tolerable margins were supported (H64k2); point-estimated CVaR increases by about 16%. The gap to IPOP remains large. The option is documented, disabled by default, and not recommended. The `permuted` arm compared whole regimes (Codex 092), while the `resample` arm was corrected and rerun under amendment A1. Originality and industrial advantage were not established.
