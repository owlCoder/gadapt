# I64-N: Exploratory nominal-label-ordering probe — NOT preregistered

This development-only probe tested whether GAdapt depends on arbitrary label ordering for nominal variables. The Potts case comprised 10 variables with eight categories each, 20 graph edges, a budget of B = 3,000, and 12 problems × 16 label permutations × four seeds per method.

The gap is defined as (best − ref)/|ref|, where `ref` is the best value found for a problem, **not** a certified global optimum.

| Method | Mean gap | SD across label permutations (mean across problems) | Within-permutation seed SD (mean) | Between/within ratio |
|---|---|---|---|---|
| gadapt_M | 0.0896 | 0.0338 | 0.0609 | 1.11 |
| gadapt_free | 0.0876 | 0.0331 | 0.0607 | 1.09 |
| hillclimb | 0.1590 | 0.0460 | 0.0921 | 1.00 |
| random | 0.3789 | 0.0267 | 0.0501 | 1.07 |

A between/within ratio close to 1 indicates that label permutation has no discernible effect beyond seed noise; a ratio materially above 1 would indicate sensitivity to arbitrary label ordering. In the tested synthetic probe the ratios were near 1, so no meaningful defect requiring a Graph-GAdapt intervention was demonstrated. This was exploratory evidence, not a preregistered confirmatory test.
