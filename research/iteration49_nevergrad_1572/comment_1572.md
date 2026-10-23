I can reproduce this on current `main` (55950f9) and on 1.0.12. It also affects plain `NGOpt`: on a bounded 10-D `Array` with budget 1000, `NGOpt` selects `ParametrizedMetaModel(multivariate_optimizer=CmaFmin2)`, and two runs with the same seed differ from the first evaluation on, both in one process and across processes.

```python
import numpy as np
import nevergrad as ng


def run(seed):
    param = ng.p.Array(shape=(10,), lower=-5.0, upper=5.0)
    param.random_state.seed(seed)
    opt = ng.optimizers.NGOpt(parametrization=param, budget=1000)
    print(opt.optim.name)  # ParametrizedMetaModel(multivariate_optimizer=CmaFmin2)
    return opt.minimize(lambda x: float(np.sum(x ** 2))).value


print(run(0)[:3])
print(run(0)[:3])  # differs from the line above
```

I found two unseeded sources:

1. `recastlib.py`, `CmaFmin2` branch: `cma.fmin(...)` is called without a `seed` option, and pycma's default is `seed='time'`. Restart points `x0` are also drawn from the global `np.random`. As a side effect, pycma reseeds the global `np.random` from the clock.
2. `metamodel.py`, `learn_on_k_best`: the inner `Powell`/`DE` is built with `parametrization=dimension`, so its random state is drawn from the global `np.random` on first use. This only matters once the surrogate is learnable (e.g. sphere, not a plateau). With fix 1 alone, some sphere runs still diverged at about evaluation 414.

This patch (against 55950f9) removes both:

```diff
--- a/nevergrad/optimization/metamodel.py
+++ b/nevergrad/optimization/metamodel.py
@@ -9,6 +9,7 @@ import time
 from . import utils
 from .base import registry
 from . import callbacks
+from nevergrad.parametrization import parameter as ng_p
 
 
 class MetaModelFailure(ValueError):
@@ -180,8 +181,14 @@ def learn_on_k_best(
         for cls in (
             (Powell, DE) if algorithm != "image" else (DiscreteLenglerOnePlusOne,)
         ):  # Powell excellent here, DE as a backup for thread safety.
+            inner_param: tp.Any = dimension
+            if para is not None and algorithm == "image":
+                inner_param = para
+            elif para is not None:
+                inner_param = ng_p.Array(shape=(dimension,))
+                inner_param.random_state = np.random.RandomState(para.random_state.randint(2**30))
             optimizer = cls(
-                parametrization=para if (para is not None and algorithm == "image") else dimension,
+                parametrization=inner_param,
                 budget=45 * dimension + 30,
             )
             # limit to 20s at most
--- a/nevergrad/optimization/recastlib.py
+++ b/nevergrad/optimization/recastlib.py
@@ -442,8 +442,9 @@ class _NonObjectMinimizeBase(recaster.SequentialRecastOptimizer):
                     else np.zeros(weakself.dimension)
                 )
                 num_calls = 0
+                rng = np.random.RandomState(weakself._rng.randint(2**30))
                 while budget - num_calls > 0:
-                    options = {"maxfevals": budget - num_calls, "verbose": -9}
+                    options = {"maxfevals": budget - num_calls, "verbose": -9, "seed": rng.randint(1, 2**30)}
                     if weakself._normalizer is not None and weakself._normalizer.fully_bounded:
                         # Tell CMA to work in [0, 1].
                         options["bounds"] = [0.0, 1.0]
@@ -456,9 +457,9 @@ class _NonObjectMinimizeBase(recaster.SequentialRecastOptimizer):
                     )
                     x0 = (
                         0.5
-                        + np.random.uniform() * np.random.uniform(low=-0.5, high=0.5, size=weakself.dimension)
+                        + rng.uniform() * rng.uniform(low=-0.5, high=0.5, size=weakself.dimension)
                         if weakself._normalizer is not None and weakself._normalizer.fully_bounded
-                        else np.random.randn(weakself.dimension)
+                        else rng.randn(weakself.dimension)
                     )
                     if res[1] < best_res:
                         best_res = res[1]
```

Checked with Python 3.14.3, NumPy 2.5.4 and cma 4.5.0 on macOS:

- The example above and the reproducer in this issue (BBOB f11, 25-D, budget 200) give identical results across three separate processes with the patch, and different results on unpatched `main`.
- On 10-D sphere and a floor plateau (budget 1000, 8 seeds each), the hash of the full sequence of evaluated points is identical within a process and across processes in 16/16 cases. Unpatched `main` matched in 0 of the 6 cases I checked.
- `pytest nevergrad/optimization/test_optimizerlib.py -k "CmaFmin2 or MetaModel or metamodel"`: 11 passed, 15 skipped.

Two caveats:

- pycma still sets the global `np.random` seed, but now deterministically.
- `learn_on_k_best` still has the 20 s wall-clock `EarlyStopping.timer`, so slow surrogates can remain machine-dependent.

`CmaFmin2`, `MetaModelFmin2` and `NGOpt$` might then come off `UNSEEDABLE` in `test_optimizerlib.py`. I did not regenerate the recorded recommendations.
