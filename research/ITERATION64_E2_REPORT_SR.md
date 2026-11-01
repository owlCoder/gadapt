# I64-E2: Differential crossover under an orthogonal transformation — generated report

Specification: [ITERATION64_E2_SPEC.md](ITERATION64_E2_SPEC.md), frozen at `aeff985`. Paired against archived E records by (cell, seed): 63 cells × 100 seeds, 12,000 actual objective calls per run.

## 1. Hypothesis decisions — one simultaneous family of five contrasts (α = 0.05, t* = 2.559, 20,000 replicates)

- **H64e1** (closing the rotation gap relative to GAdapt-M): **opposite**.
- **H64e2** (tolerable harm on original+shift): **undecided**.
- **H64e3** (noninferiority to IPOP, margin 0.05): **opposite**.
- Overall supported: **False**; C_rot(GAdapt-M) = 0.0300.

| Contrast | Estimate | Lower | Upper |
|---|---|---|---|
| dA_rot(D-M) | -0.03619 | -0.04722 | -0.02516 |
| 0.8*CVaR_rot(M)-CVaR_rot(D) | -0.02534 | -0.02941 | -0.02126 |
| dA_nonrot(D-M) | -0.04215 | -0.04611 | -0.0382 |
| 1.5*CVaR_nonrot(M)-CVaR_nonrot(D) | 9.15e-05 | -0.000238 | 0.000421 |
| dA_rot(D-IPOP) | -0.1824 | -0.192 | -0.1728 |

## 2. Aggregates by transformation

Functions and dimensions within functions are equally weighted. "Median gap" is the weighted mean of cell medians of normalized gap; CVaR is the weighted mean of cell CVaR₀,₉(L).

**Original (orig)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.7022 | 0.0026 | 0.00101 |
| gadapt_diff | 0.6597 | 0.0038 | 0.00187 |
| ipop | 0.7765 | 0.0122 | 0.00568 |
| cma | 0.7554 | 0.0156 | 0.0102 |
| bipop | 0.7717 | 0.0135 | 0.00594 |
| de | 0.6522 | 0.0082 | 0.00584 |

**Shifted (shift)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.7007 | 0.0025 | 0.0011 |
| gadapt_diff | 0.6588 | 0.0037 | 0.00174 |
| ipop | 0.7701 | 0.0147 | 0.00855 |
| cma | 0.7697 | 0.0134 | 0.00749 |
| bipop | 0.7712 | 0.0140 | 0.00709 |
| de | 0.6542 | 0.0082 | 0.00578 |

**Orthogonally transformed (rot)**

| Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|
| gadapt | 0.6167 | 0.0300 | 0.0108 |
| gadapt_diff | 0.5805 | 0.0494 | 0.0252 |
| ipop | 0.7630 | 0.0158 | 0.00913 |
| cma | 0.7603 | 0.0145 | 0.00996 |
| bipop | 0.7636 | 0.0151 | 0.00889 |
| de | 0.6124 | 0.0391 | 0.0335 |

## 3. Conclusion

The opt-in differential crossover **does not close** GAdapt's orthogonal-transformation gap. A is lower under Q and across original+shift (the simultaneous intervals for ΔA are below zero); individual variant results descriptively follow the same direction, and the rotated tail is worse. The option remains documented, disabled by default, and **not recommended**. This preregistered negative result was not rerun using another F. The underlying failure mechanism was not isolated: differential crossover is rotation-equivariant only as an unconstrained step; the mutation operators remain coordinate-based.
