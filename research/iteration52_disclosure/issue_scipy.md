`differential_evolution` evaluates a better point during polishing, then returns a worse one. With the default `polish=True`, the L-BFGS-B result is accepted only if `result.success` is true. When L-BFGS-B ends with `ABNORMAL` or reaches its evaluation limit, a polished point that is better and inside the bounds is discarded. The returned `res.x`/`res.fun` can then be much worse than a point the solver itself evaluated.

```python
import numpy as np
from scipy.optimize import differential_evolution

calls = []


def f(x):
    value = float(np.sum((x - 0.3) ** 2) + 1e5 * max(0.0, np.sum(x) - 2.0))
    calls.append((value, x.copy()))
    return value


res = differential_evolution(f, [(-5, 5)] * 10, maxiter=3, rng=1)
best_value, best_x = min(calls, key=lambda c: c[0])
print("res.fun        =", res.fun)
print("best evaluated =", best_value, "| inside bounds:", bool(np.all(np.abs(best_x) <= 5)))
print("res.nfev =", res.nfev, "| res.message =", res.message)
```

Output with SciPy 1.18.1 and with the nightly `2.0.0.dev0+git20261021.3f3cfc3`:

```
res.fun        = 22.973600733006375
best evaluated = 1.101685819126364 | inside bounds: True
res.nfev = 1260 | res.message = Maximum number of iterations has been exceeded.
```

The polishing `minimize` call returns `fun=1.1017`, `success=False`, `message='ABNORMAL: '`, `nfev=660`. The condition in `_differentialevolution.py` (`result.fun < DE_result.fun and result.success and <within bounds>`) then rejects it.

This is not limited to toy functions. On an AC economic-dispatch cost (pypower `runpf` on MATPOWER `case118`, 53 variables, `maxiter` sized for about 1000 evaluations), polishing used 15,444 evaluations and stopped at L-BFGS-B's `maxfun` (`'STOP: TOTAL NO. OF F,G EVALUATIONS EXCEEDS LIMIT'`). It reached 143,102, and `res.fun` was 271,061. It happened in 5 of 15 runs (MATPOWER case14, case39 and case118, 5 seeds each).

The `polish` documentation says polishing "can improve the minimization slightly". It does not say that an improvement found by an unsuccessful polish is thrown away. That leaves users with a result worse than one their own budget already paid for, often after polishing has used most of the evaluations.

Would it make sense to accept the polished point whenever it is better and within bounds (and feasible for constrained problems), and to keep `success` and `message` reporting the polish status? If the current behaviour is intended, could the `polish` docstring state that unsuccessful polishing results are discarded?

Environment: SciPy 1.18.1 and 2.0.0.dev0+git20261021.3f3cfc3, NumPy 2.5.4, Python 3.14.3, macOS (arm64).
