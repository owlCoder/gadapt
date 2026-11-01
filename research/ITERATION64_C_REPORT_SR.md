# I64-C: Coefficient signature of GAdapt's loss under an orthogonal transformation — generated report

Specification: [ITERATION64_C_SPEC.md](ITERATION64_C_SPEC.md). The experiment compares `shift` with `rotm` (the same shift, using Q from E's rotated variant) on 21 function–dimension pairs, 30 seeds, the first 1,200 calls of GAdapt-M. Columnar-diversity (log-relative) coefficients were recorded passively for each generation.

- Weighted mean Δ (drop in CV coefficients, shift − rotm): **0.0132** [−0.0466, 0.0709] (Bonferroni α/3 = 0.0167); Δ_k was positive in 14 of 21 nonzero pairs (binomial p = 0.0946).
- Spearman ρ(Δ_k, ΔA_k): **0.274** [−0.085, 0.618]; baseline ρ(E_k, ΔA_k) = 0.578; their difference = −0.304 [−0.721, 0.148].

- **H64c1** (coefficient homogenization): **undecided**.
- **H64c2** (association with loss of A): **undecided**.
- **H64c3** (stronger marginal rank association than the baseline): **undecided**.
- Predicted coefficient signature supported: **False**; stronger marginal association than the baseline: **False**.

Leave-one-function-out Spearman ρ(Δ_k, ΔA_k), descriptive:

| Omitted function | ρ |
|---|---|
| sphere | 0.230 |
| rosenbrock | 0.257 |
| rastrigin | 0.342 |
| ackley | 0.298 |
| griewank | 0.288 |
| styblinski_tang | 0.329 |
| beale | 0.247 |
| himmelblau | 0.236 |
| booth | 0.208 |

By function–dimension pair:

| Pair | Δ_k | ΔA_k | E_k |
|---|---|---|---|
| sphere|2 | -0.0165 | -0.0002 | -0.0387 |
| sphere|7 | 0.0007 | 0.0034 | 0.1774 |
| sphere|20 | 0.0068 | -0.0008 | 0.0203 |
| rosenbrock|2 | -0.1985 | -0.0872 | -0.5757 |
| rosenbrock|7 | 0.1358 | -0.0029 | 0.1129 |
| rosenbrock|20 | 0.0382 | 0.0472 | 0.1381 |
| rastrigin|2 | -0.0178 | 0.3857 | 3.1824 |
| rastrigin|7 | 0.1014 | 0.5259 | 0.3654 |
| rastrigin|20 | 0.1150 | 0.0132 | 0.2650 |
| ackley|2 | 0.0363 | 0.0009 | -0.0431 |
| ackley|7 | 0.0156 | 0.0270 | 0.1792 |
| ackley|20 | 0.0264 | 0.1298 | 0.0942 |
| griewank|2 | 0.0276 | 0.0320 | -0.1166 |
| griewank|7 | 0.0967 | 0.0188 | 0.1578 |
| griewank|20 | 0.0011 | 0.0950 | -0.0003 |
| styblinski_tang|2 | -0.0844 | 0.0146 | 0.5078 |
| styblinski_tang|7 | -0.0715 | 0.5057 | 1.3865 |
| styblinski_tang|20 | 0.1449 | 0.2709 | 0.1668 |
| beale|2 | 0.1676 | 0.0693 | 1.2414 |
| himmelblau|2 | -0.1449 | 0.0037 | 0.4426 |
| booth|2 | -0.0234 | -0.0047 | -1.4315 |

## Limitations

This correlation study uses 21 fixed cells from nine functions and measures only the log-relative coefficient, not a covariance diagonal. Neither an intervention nor a mediation analysis was conducted, so causality is not established. No incremental predictive value is claimed. Results apply to GAdapt-M, the native domain, 1,200 calls, and the examined cells; they do not extend to discrete ORPD problems, which are not rotated. The bootstrap samples seeds and function choices, but does not resample Q or shift vectors.
