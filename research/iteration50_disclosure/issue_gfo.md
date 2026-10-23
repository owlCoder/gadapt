With `optimum="minimum"`, `best_score` (and the `score` column of `search_data`) is returned negated. The `search()` docstring says:

> When set to `"minimum"`, the objective function's return value is negated internally so that the optimizer always maximizes. The reported `best_score` is in original (non-negated) units.

```python
from gradient_free_optimizers import HillClimbingOptimizer

opt = HillClimbingOptimizer({"x": (-5.0, 5.0)}, random_state=0)
opt.search(lambda p: p["x"] ** 2 + 1.0, n_iter=50, optimum="minimum", verbosity=False)
print("best_score =", opt.best_score, "| f(best_para) =", opt.best_para["x"] ** 2 + 1.0)
```

Output with 1.13.0 from PyPI, and also with current `main` (a3ef5471) installed from source:

```
best_score = -1.000034535452253 | f(best_para) = 1.000034535452253
```

The first rows of `opt.search_data` are negated in the same way (`score` -12.86 for `x` = 3.44).

`best_para` is correct. Only the reported scores keep the sign from the internal `_negate` wrapper in `search()`. `best_score` returns `self._data._best_score` from the `SearchTracker`, which records the negated value.

A possible fix is to undo the negation when `optimum == "minimum"` in `best_score` and when building `search_data`, or to have the tracker store original-unit scores. I have not checked whether `max_score` (documented as original units for minimization) has the same issue.

Environment: gradient-free-optimizers 1.13.0 and main a3ef5471, NumPy 2.5.4, Python 3.14.3, macOS.
