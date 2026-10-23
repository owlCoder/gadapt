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
