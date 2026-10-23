import numpy as np
from sko.DE import DE


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


calls = []


def f(x):
    value = float(np.sum((x - 1.3) ** 2))
    calls.append(value)
    return value


for cls in (DE, FixedDE):
    found = 0
    for seed in range(200):
        calls.clear()
        np.random.seed(seed)
        _, best_y = cls(func=f, n_dim=10, size_pop=50, max_iter=3, lb=[-5] * 10, ub=[5] * 10).run()
        found += float(np.ravel(best_y)[0]) > min(calls) + 1e-9
    print(cls.__name__, found, "of 200")
