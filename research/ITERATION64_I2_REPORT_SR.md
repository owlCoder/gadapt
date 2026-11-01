# I64-I2: GAdapt → CMA-ES hybrid on discrete ORPD — generated report

Specification: [ITERATION64_I2_SPEC.md](ITERATION64_I2_SPEC.md), frozen at `e0c0ed1` before examining I64-I. Paired with I64-I records by cell and seed: eight cells × 30 seeds, with 12,000 actual power-flow evaluations per run.

## 1. Decisions

One simultaneous family of four contrasts (α = 0.05, t* = 3.413, 20,000 replicates):

- **H64h1** (hybrid improves the tail versus GAdapt-M without reducing feasibility): **undecided**.
- **H64h2** (hybrid improves the tail versus IPOP without reducing feasibility): **opposite**.

| Contrast | Estimate | Lower | Upper |
|---|---|---|---|
| CVaR(M)-CVaR(H) | -0.07989 | -0.2656 | 0.1058 |
| P(H)-P(M) | -0.004167 | -0.03548 | 0.02715 |
| CVaR(IPOP)-CVaR(H) | -0.1253 | -0.2502 | -0.0003896 |
| P(H)-P(IPOP) | -0.02917 | -0.06428 | 0.005946 |

A positive CVaR(reference) − CVaR(H) favors the hybrid. P(H) − P(reference) ≥ −0.05 denotes a feasibility decrease of no more than five percentage points.

## 2. Equal-cell-weight aggregates

| Configuration | P(feasible) | CVaR₀,₉(L) |
|---|---|---|
| gadapt | 0.746 | 0.2973 |
| gadapt_hyb | 0.742 | 0.3772 |
| ipop | 0.771 | 0.2518 |

## 3. Interpretation

The hybrid's performance gain observed in E3 on synthetic functions was **not confirmed** on this ORPD sample. The hybrid was not shown to outperform GAdapt-M (H64h1 undecided), and its tail was worse than IPOP's (H64h2 opposite). The independent contribution of the GAdapt phase was not identified. Findings apply only to the eight cells and 30 seeds examined. No claim of industrial readiness follows.
