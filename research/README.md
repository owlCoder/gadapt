# Research: robust cost-diversity baseline

This branch contains a deliberately **opt-in** change to GAdapt:

```python
from gadapt.ga import GA

ga = GA(cost_function=my_cost_function, cost_diversity_metric="affine_invariant")
```

The default remains `log_relative`. The new `affine_invariant` metric:

* calculates the half-range of **finite** population costs;
* compares it to the initial generation's half-range and clamps to [0,1];
* is invariant to addition of a constant and multiplication by a positive
  constant, modulo floating-point representability;
* returns 0 when all costs are identical; if the initial spread is zero,
  it recovers to 1 when nonzero diversity subsequently appears;
* raises a `ValueError` for nonfinite costs in the diversity calculation.

**Limitation:** Invariance of a metric is not a proof of better optimizer
accuracy. The range is sensitive to outliers; a zero initial range loses
relative magnitude information. Whether this is an improvement for any
class of objective functions must be measured in full GAdapt runs.

## Reproduce

Run tests from the repository root:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run exploratory seeded benchmarks on the full package:

```bash
python research/benchmark_affine.py --runs 30 --generations 150 --output affine_results.csv
```

For a defensible dissertation, the next experiments must compare the
unchanged baseline, the opt-in metric, and independent optimizers under
controlled objective-evaluation budgets across multiple dimensions,
replicates, transformations, noise levels and constraint scenarios.
Statistical inference must use paired seeds and multiplicity corrections.
Do not compare results of differently scaled cost values without undoing
the affine transform. Use engineering cases with independently verified
feasibility before making infrastructure or industrial claims.

## Repositories / provenance

Based on owlCoder/gadapt fork of bpzoran/gadapt at
`8825da180377cb231d4751c08108a8149269ffc1` (2026-10-17).
The upstream repository is not modified by this research branch.
