With a fixed `Scenario(seed=...)`, SMAC 2.4.1 gives different results in different Python processes. Inside one process the results are reproducible. The cause is that iteration order over a `set` of `Configuration` objects depends on `PYTHONHASHSEED`, which Python randomizes per process by default.

The `Scenario` docstring says: "The seed is used to make results reproducible."

```python
import tempfile

from ConfigSpace import ConfigurationSpace
from smac import HyperparameterOptimizationFacade, Scenario

space = ConfigurationSpace({"x0": (-5.0, 5.0), "x1": (-5.0, 5.0)}, seed=0)
scenario = Scenario(space, deterministic=True, n_trials=40, seed=0,
                    output_directory=tempfile.mkdtemp())
smac = HyperparameterOptimizationFacade(
    scenario, lambda config, seed=0: config["x0"] ** 2 + config["x1"] ** 2,
    overwrite=True, logging_level=40)
incumbent = smac.optimize()
print(dict(incumbent))
```

Three plain runs (`python smac_min.py`) with Python's default hash randomization:

```
{'x0': 0.2810798266841, 'x1': -0.0316035692397}
{'x0': 0.4566685049749, 'x1': 0.1619993449515}
{'x0': 0.221594888561, 'x1': 0.0358273556006}
```

Fixing `PYTHONHASHSEED` gives a stable result per value. With `PYTHONHASHSEED` set to 1, 2, 3 and 1 again:

```
{'x0': 0.0475889294421, 'x1': 0.042622522022}
{'x0': 0.0013361641109, 'x1': 0.0810884653284}
{'x0': 0.0058697676316, 'x1': 0.020806992311}
{'x0': 0.0475889294421, 'x1': 0.042622522022}
```

**Cause.** `LocalSearch._get_initial_points` in `smac/acquisition/maximizer/local_search.py` returns `list(set(itertools.chain(...)))`. `Configuration.__hash__` is `hash(self.__repr__())`, a string hash, so the order of the local-search start points changes between processes. The local search then consumes the RNG in a different order. In a 2-D run with 200 trials, the sequences of evaluated configurations split at evaluation 20, the first model-based proposal after the initial design.

**Fix.** An order-preserving de-duplication removes the dependence. With it, the example gives the same incumbent for `PYTHONHASHSEED` 1, 2 and 3. In a larger check (10-D Rastrigin, 200 trials) the full sequence of evaluated configurations is identical for hash seeds 1 and 2, while unpatched 2.4.1 differs. The patch applies to current `main` (84148879), where this code is unchanged:

```diff
--- a/smac/acquisition/maximizer/local_search.py
+++ b/smac/acquisition/maximizer/local_search.py
@@ -298,13 +298,8 @@
         else:
             additional_start_points = []
 
-        init_points_as_set: set[Configuration] = set(
-            itertools.chain(
-                previous_configs_sorted_by_cost,
-                additional_start_points,
-            )
-        )
-        return list(init_points_as_set)
+        # order-preserving de-duplication: iterating a set of Configurations depends on PYTHONHASHSEED
+        return list(dict.fromkeys(itertools.chain(previous_configs_sorted_by_cost, additional_start_points)))
 
     def _search(
         self,
```

Other `set` iterations over configurations may exist elsewhere. I only checked this one, and it was sufficient for the cases above.

Environment: smac 2.4.1, ConfigSpace 1.2.2, NumPy 2.5.4, scikit-learn 1.9.1, Python 3.14.3, macOS.
