# Evaluation-integrity audit for black-box optimizers

Run this audit before you compare optimizers on an expensive cost function such as a power-flow or network model.
It shows whether your optimizer evaluates, counts, reproduces and reports what you assume it does. No code reading
is needed.

## Use

1. Write an adapter for your optimizer:

   ```python
   def run(f, lower, upper, budget, seed):
       ...                     # your optimizer: call f(x) with x in [lower, upper], at most `budget` times
       f.search_done()         # optional: the optimizer's main call has returned (enables check C5)
       ...                     # extract the result the way your code does
       return x_best, f_best   # what your code reports, or None if it reports nothing
   ```

2. Run the audit in the optimizer's environment:

   ```
   python research/integrity_audit_tool.py my_adapter.py:run --python /path/to/env/bin/python
   ```

Options:
- `--budget` sets the evaluation budget (default 200).
- `--dims` sets the problem dimensions (default 2 10).
- `--seeds` sets the number of seeds (default 3).
- `--json out.json` writes every call-level flag.

The exit code is 1 if an integrity problem is found, so the audit can run in CI.

Working examples for GFO and SMAC are in [integrity_audit_examples.py](integrity_audit_examples.py).

## What it checks

The optimizer runs on a shifted sphere, Rastrigin and a floor plateau. Every call is recorded. Each run is repeated
in the same process and in two fresh processes with different `PYTHONHASHSEED`.

| Class | Problem | Example found in practice |
|---|---|---|
| C3 | evaluations outside the box | DEAP without a bounds decorator |
| C4 | more evaluations than the budget | cma: up to 1011 for `maxfevals` 1000 |
| C5 | evaluations after the optimizer returned | PyGAD `best_solution()` without `pop_fitness` |
| R1 | the reported solution was never evaluated | — |
| R2 | the reported cost differs from the recorded cost | GFO with `optimum="minimum"`: sign flipped |
| R3 | the reported solution is worse than the best evaluated one | scikit-opt DE; SciPy `differential_evolution` when L-BFGS-B polishing reports `success=False` (up to 89% worse on AC dispatch) |
| D3 | same seed, different run within one process | Nevergrad `NGOpt` |
| D3x | same seed, different run between processes | SMAC 2.4.1 (depends on `PYTHONHASHSEED`) |

The audit also reports two measures that are not integrity problems:
- **Waste:** the share of repeated evaluations. For example, geneticalgorithm 41.5% and scikit-opt DE 47%.
- **Corner evaluations:** points at the all-lower or all-upper corner. Inspect them before concluding anything. They
  can be a validation probe, as in GAdapt with the default `probe_cost_function=True`, or a legitimate point of an
  algorithm that clips to the bounds.

## Evidence

- The tool is validated on planted faults: [test_integrity_audit_tool.py](test_integrity_audit_tool.py) covers 8
  classes, a clean runner and a corner probe.
- It reuses the classifier of research iterations I49 and I50, which audited 21 Python libraries
  ([I49](ITERATION49_REPORT_SR.md), [I50](ITERATION50_REPORT_SR.md)).
- In those audits, integrity problems other than corner evaluations appeared in 8 of 21 libraries.
- Findings were reported to maintainers: [SMAC #1380](https://github.com/automl/SMAC3/issues/1380),
  [GFO #106](https://github.com/gfo-project/Gradient-Free-Optimizers/issues/106) and
  [Nevergrad #1572](https://github.com/facebookresearch/nevergrad/issues/1572) and
  [SciPy #26479](https://github.com/scipy/scipy/issues/26479).
- Test functions do not reveal everything. The SciPy defect appeared only on a real AC-dispatch cost function
  ([I52](ITERATION52_PROTOCOL.md)), so audit with your own cost function as well.
