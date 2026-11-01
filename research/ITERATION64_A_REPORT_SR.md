# I64-A: GAdapt → CMA-ES hybrid ablation — generated report

Specification: [ITERATION64_A_SPEC.md](ITERATION64_A_SPEC.md). H denotes the archived E3 hybrid (GAdapt-M for the first 30% of the budget, then CMA-ES); R replaces the GAdapt stage with random sampling for 30%, followed by the same CMA stage. The experiment paired 63 cells × 100 seeds, with 12,000 physical objective calls per run.

Simultaneous intervals for four contrasts (α = 0.05, 20,000 bootstrap replicates, seed 71), t* = 2.5028.

| Contrast | Estimate | Lower | Upper |
|---|---|---|---|
| c1 dA_rot(H-R) | 0.1313 | 0.1237 | 0.1389 |
| c2 dA_nonrot(H-R) | 0.1779 | 0.1735 | 0.1822 |
| c3 CVaR_rot(R)-CVaR_rot(H) | 0.0055 | 0.0041 | 0.0070 |
| c4 CVaR_nonrot(R)-CVaR_nonrot(H) | 0.0134 | 0.0124 | 0.0144 |

- **H64a1** (effect on ECDF area A under rotation of replacing the first 30% GAdapt stage with uniform sampling, at least 0.02): **supported**.
- **H64a2** (corresponding effect on the combined original and shifted functions): **supported**.
- Aggregate `contribution_supported`: **True**.

Results by variant:

| Variant | Configuration | A | CVaR₀,₉ | Median gap |
|---|---|---|---|---|
| orig | H | 0.7628 | 0.0048 | 0.00216 |
| orig | R | 0.5876 | 0.0184 | 0.01132 |
| shift | H | 0.7708 | 0.0043 | 0.00219 |
| shift | R | 0.5903 | 0.0176 | 0.00891 |
| rot | H | 0.7196 | 0.0119 | 0.00443 |
| rot | R | 0.5884 | 0.0174 | 0.00911 |

## Limitations

The estimand is the replacement effect of the first 30% phase by uniform random samples **in this fixed hybrid configuration**. The study does not establish that standalone GAdapt beats random sampling, identify a mechanism, or generalize to other phase fractions, budgets, initial step sizes σ₀, or CMA variants. Bootstrap uncertainty reflects algorithmic seed variation only. A possible confound is that the CMA phase starts from the best random point with σ₀ = 0.05, chosen for the GAdapt-initialized hybrid and potentially a poor initialization after random sampling. Because σ₀ was not varied, this is not a pure, configuration-independent measure of the first GAdapt phase's quality.
