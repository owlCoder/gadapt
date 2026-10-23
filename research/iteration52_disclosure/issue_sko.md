`DE.run()` sometimes returns a `best_y` that is worse than a value the algorithm itself evaluated. In 10 of 200 seeds on a plain 10-D sphere, the returned value is worse than the best evaluated one.

```python
import numpy as np
from sko.DE import DE

calls = []


def f(x):
    value = float(np.sum((x - 1.3) ** 2))
    calls.append(value)
    return value


found = 0
for seed in range(200):
    calls.clear()
    np.random.seed(seed)
    best_x, best_y = DE(func=f, n_dim=10, size_pop=50, max_iter=3, lb=[-5] * 10, ub=[5] * 10).run()
    reported = float(np.ravel(best_y)[0])
    if reported > min(calls) + 1e-9:
        found += 1
        if found <= 3:
            print(f"seed {seed}: reported best_y = {reported:.4f}, best evaluated = {min(calls):.4f}")
print(f"{found} of 200 seeds report a value worse than the best evaluated one")
```

Output with scikit-opt 0.6.6 (the code is the same on `master`):

```
seed 25: reported best_y = 33.1271, best evaluated = 32.0991
seed 41: reported best_y = 28.4670, best evaluated = 20.7293
seed 47: reported best_y = 30.6744, best evaluated = 27.7645
10 of 200 seeds report a value worse than the best evaluated one
```

**Cause.** In `DE.selection()`, `self.Y` still holds the values of the trial vectors `U` after selection (the last `x2y()` call), not the values of the selected population. `run()` then picks `generation_best_index = self.Y.argmin()`. When a retained parent is better than every trial vector, it is never seen as the best, and in the last generation it is lost. `generation_best_X` can also pair a retained parent with a trial vector's value. The final `self.func(best_x)` call hides that mismatch.

**Fix.** Setting `self.Y` to the values of the selected population removes the problem. With the following subclass, the same check gives 0 of 200:

```python
class FixedDE(DE):
    def selection(self):
        X = self.X.copy()
        f_X = self.x2y().copy()
        self.X = U = self.U
        f_U = self.x2y()
        keep = (f_X < f_U).reshape(-1, 1)
        self.X = np.where(keep, X, U)
        self.Y = np.where(keep.ravel(), f_X.ravel(), f_U.ravel()).reshape(self.Y.shape)
        return self.X
```

A related cost: `selection()` re-evaluates the whole parent population every generation, although those values are already known. With `size_pop=50` and `max_iter=3`, `run()` makes 301 objective calls, of which about half repeat earlier points. For an expensive objective, reusing the stored parent values would halve the cost.

We also saw the wrong `best_y` on an AC economic-dispatch cost (MATPOWER cases via pypower), in 2 of 15 runs. The title-only issue #187 may be the same symptom.

Environment: scikit-opt 0.6.6, NumPy 2.5.4, Python 3.14.3, macOS (arm64).
