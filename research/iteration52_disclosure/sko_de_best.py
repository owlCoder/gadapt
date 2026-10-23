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
