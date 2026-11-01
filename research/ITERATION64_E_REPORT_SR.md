# I64-E: Equal 12,000-call budgets on shifted and orthogonally transformed functions with stronger competitors — generated report

Specification: [ITERATION64_E_SPEC.md](ITERATION64_E_SPEC.md), frozen at `c015730`, amended by A1 before outcomes were inspected. Analysis: `research/i64/e_analysis.py` (output `analysis_v2`). Raw outputs: `research/results/iteration64_e/`. 63 cells × nine configurations × 100 seeds. Development-selected hyperparameters: `{'cma': {'sigma0': 0.2}, 'ipop': {'sigma0': 0.3}, 'bipop': {'sigma0': 0.5}, 'es11': {'sigma0': 0.3, 'up': 1.5, 'stagnation': 100}}`.

## 1. H64a: GAdapt-M against eight competitors (16 simultaneous contrasts, α = 0.02) — **opposite**

Flags: `{'finite': True, 'zero_variance': False, 'blocked': False}`. t* = 3.587; 20,000 bootstrap replicates.

| Competitor | ΔA (GAdapt − competitor) | Lower | Upper | ΔM (competitor − GAdapt) | Lower | Upper |
|---|---|---|---|---|---|---|
| gadapt_preset | 0.003782 | -0.001086 | 0.00865 | 0.0001162 | -0.001477 | 0.001709 |
| pygad_random | 0.05881 | 0.05192 | 0.06571 | 0.01048 | 0.009009 | 0.01195 |
| pygad_adaptive | 0.1207 | 0.1141 | 0.1272 | 0.02253 | 0.02084 | 0.02422 |
| de | 0.03358 | 0.02789 | 0.03928 | 0.01075 | 0.009308 | 0.01219 |
| cma | -0.0886 | -0.09529 | -0.08192 | 0.004919 | 0.002984 | 0.006855 |
| ipop | -0.09666 | -0.1034 | -0.08997 | 0.003497 | 0.00167 | 0.005324 |
| bipop | -0.09561 | -0.1023 | -0.08895 | 0.003017 | 0.001542 | 0.004492 |
| es11 | 0.02572 | 0.01633 | 0.03511 | 0.02592 | 0.02396 | 0.02788 |

ΔA > 0 means higher evaluation efficiency for GAdapt (larger ECDF area through 12,000 calls). ΔM > 0 means better GAdapt accuracy (lower weighted median normalized gap). Simultaneous intervals use the maximum standardized deviation.

## 2. Aggregates (1/9 per function, equal dimension and transformation weights)

| Configuration | ECDF area A | CVaR₀,₉(L) | Median gap | P(g≤1e−2) | P(g≤1e−4) | P(g≤1e−6) | Runs with L > 0.5 |
|---|---|---|---|---|---|---|---|
| gadapt | 0.6732 | 0.0117 | 0.00429 | 0.898 | 0.776 | 0.647 | 0 |
| gadapt_preset | 0.6694 | 0.0121 | 0.0044 | 0.896 | 0.771 | 0.654 | 0 |
| pygad_random | 0.6144 | 0.0216 | 0.0148 | 0.825 | 0.683 | 0.613 | 0 |
| pygad_adaptive | 0.5525 | 0.0335 | 0.0268 | 0.773 | 0.658 | 0.577 | 0 |
| de | 0.6396 | 0.0185 | 0.015 | 0.850 | 0.757 | 0.717 | 0 |
| cma | 0.7618 | 0.0145 | 0.00921 | 0.868 | 0.815 | 0.814 | 0 |
| ipop | 0.7699 | 0.0142 | 0.00779 | 0.879 | 0.839 | 0.837 | 0 |
| bipop | 0.7688 | 0.0142 | 0.00731 | 0.881 | 0.840 | 0.839 | 0 |
| es11 | 0.6475 | 0.0449 | 0.0302 | 0.761 | 0.714 | 0.651 | 0 |

## 3. H64b — preset versus GAdapt-M

R₀ = CVaR(GAdapt-M) = 0.0117, R_preset = 0.0121. Point estimates [0.8·R₀ − R_preset, Δreach(1e−2), Δreach(1e−4), Δreach(1e−6)] = [−0.0027, −0.0019, −0.0052, 0.0073]; simultaneous lower bounds = [−0.0039, −0.0083, −0.0122, −0.0031]. t* = 3.032; flags `{'finite': True, 'zero_variance': False, 'blocked': False}`.

**H64b supported: False.** Required conditions: R₀ > 0; lower bound of 0.8·R₀ − R_preset at least zero; each reach-difference lower bound at least −0.05.

## 4. By transformation and function (descriptive ECDF area A / median gap; equal cell weights within groups)

| Variant | gadapt | gadapt_preset | pygad_random | pygad_adaptive | de | cma | ipop | bipop | es11 |
|---|---|---|---|---|---|---|---|---|---|
| orig (A / med. gap) | 0.629 / 0.0013 | 0.629 / 0.0013 | 0.534 / 0.014 | 0.454 / 0.031 | 0.564 / 0.0075 | 0.689 / 0.013 | 0.716 / 0.0073 | 0.710 / 0.0076 | 0.539 / 0.044 |
| shift (A / med. gap) | 0.626 / 0.0014 | 0.624 / 0.0016 | 0.540 / 0.014 | 0.462 / 0.028 | 0.567 / 0.0074 | 0.707 / 0.0096 | 0.708 / 0.011 | 0.710 / 0.0091 | 0.575 / 0.036 |
| rot (A / med. gap) | 0.523 / 0.014 | 0.521 / 0.014 | 0.490 / 0.028 | 0.429 / 0.045 | 0.514 / 0.043 | 0.696 / 0.013 | 0.701 / 0.012 | 0.701 / 0.011 | 0.570 / 0.036 |

## 4b. Cell counts where GAdapt-M has greater A / lower median gap (21 cells per transformation)

| Variant | Competitor | Larger A: GAdapt / competitor | Lower median gap: GAdapt / competitor / tie |
|---|---|---|---|
| orig | gadapt_preset | 9 / 12 | 4 / 15 / 2 |
| orig | pygad_random | 19 / 2 | 8 / 11 / 2 |
| orig | pygad_adaptive | 20 / 1 | 13 / 6 / 2 |
| orig | de | 17 / 4 | 7 / 12 / 2 |
| orig | cma | 7 / 14 | 8 / 11 / 2 |
| orig | ipop | 7 / 14 | 7 / 12 / 2 |
| orig | bipop | 7 / 14 | 7 / 12 / 2 |
| orig | es11 | 11 / 10 | 11 / 9 / 1 |
| shift | gadapt_preset | 12 / 9 | 7 / 12 / 2 |
| shift | pygad_random | 20 / 1 | 9 / 10 / 2 |
| shift | pygad_adaptive | 20 / 1 | 13 / 6 / 2 |
| shift | de | 17 / 4 | 7 / 12 / 2 |
| shift | cma | 7 / 14 | 7 / 12 / 2 |
| shift | ipop | 7 / 14 | 8 / 11 / 2 |
| shift | bipop | 7 / 14 | 7 / 12 / 2 |
| shift | es11 | 11 / 10 | 10 / 10 / 1 |
| rot | gadapt_preset | 10 / 10 | 3 / 16 / 2 |
| rot | pygad_random | 16 / 4 | 7 / 13 / 1 |
| rot | pygad_adaptive | 17 / 3 | 11 / 9 / 1 |
| rot | de | 14 / 6 | 8 / 12 / 1 |
| rot | cma | 4 / 16 | 8 / 12 / 1 |
| rot | ipop | 4 / 16 | 7 / 13 / 1 |
| rot | bipop | 4 / 16 | 7 / 13 / 1 |
| rot | es11 | 8 / 12 | 8 / 12 / 1 |

## 4c. Mean CVaR₀,₉(L) by transformation (equal cell weights)

| Variant | gadapt | gadapt_preset | pygad_random | pygad_adaptive | de | cma | ipop | bipop | es11 |
|---|---|---|---|---|---|---|---|---|---|
| orig | 0.0033 | 0.0031 | 0.0205 | 0.0372 | 0.0105 | 0.0200 | 0.0157 | 0.0174 | 0.0619 |
| shift | 0.0033 | 0.0032 | 0.0196 | 0.0342 | 0.0105 | 0.0172 | 0.0188 | 0.0180 | 0.0540 |
| rot | 0.0386 | 0.0400 | 0.0429 | 0.0578 | 0.0502 | 0.0186 | 0.0203 | 0.0194 | 0.0566 |

## 5. Prespecified limitations

Only classical functions, not CEC/BBOB, with optima inside the defined domains. One hundred seeds are insufficient for reliable estimates of rare failures; CVaR bootstrap becomes nonsmooth when roughly 10% of runs fail, hence the additional number of runs with L > 0.5. L-SHADE/jDE were omitted; CMA-with-margins was not tested. GAdapt/PyGAD/DE operated on the native domain, CMA/ES on a unit cube. GAdapt was taken from the repository (0.5.2+), not the PyPI 0.5.0 package. Hyperparameters were developed using separate seeds on rotated cells.
