"""I64 stage E/R building blocks (protocol §2, §4): transformed objectives on [0,1]^D, the exact-budget call wrapper, normalisers.

Variants: 'orig' f(l + w y); 'shift' f(x* + w (y - o)); 'rot' f(x* + w Q^T (y - o)), w = u - l, o in [0.25, 0.75]^D, Q orthogonal
(Haar via QR of a Gaussian matrix, sign-fixed). The minimiser of every variant lies at y = o (in the unit cube); for 'orig' at (x* - l)/w.
"""
import math

import numpy as np

# minimiser x* per function (before any transformation), as used by the mentor's domains
def x_star(name, d):
    if name in ("sphere", "rastrigin", "ackley", "griewank"):
        return np.zeros(d)
    if name == "rosenbrock":
        return np.ones(d)
    if name == "styblinski_tang":
        a = min(r.real for r in np.roots([4, 0, -32, 5]) if abs(r.imag) < 1e-12)
        return np.full(d, a)
    if name == "beale":
        return np.array([3.0, 0.5])
    if name == "himmelblau":
        return np.array([3.0, 2.0])
    if name == "booth":
        return np.array([1.0, 3.0])
    raise ValueError(name)


def transform(name, d, lo, hi, variant, rng):
    """Returns (g, info): g maps y in [0,1]^D to the original function value; info archives o, Q, x*."""
    w = hi - lo
    xs = x_star(name, d)
    if variant == "orig":
        o = (xs - lo) / w
        Q = np.eye(d)
        shift = False
    else:
        o = rng.uniform(0.25, 0.75, size=d)
        if variant == "shift":
            Q = np.eye(d)
        elif variant == "rot":
            A = rng.standard_normal((d, d))
            Q, R = np.linalg.qr(A)
            Q = Q * np.sign(np.diag(R))
        else:
            raise ValueError(variant)
        shift = True
    return (Q, o, xs, w, lo, shift), dict(o=o.tolist(), Q=Q.tolist(), x_star=xs.tolist(), w=w, variant=variant)


def make_objective(f, tf):
    Q, o, xs, w, lo, shift = tf

    def g(y):
        y = np.asarray(y, float)
        if not shift:
            return float(f(lo + w * y))
        return float(f(xs + w * (Q.T @ (y - o))))
    return g


class BudgetReached(BaseException):
    """Raised before call B+1; caught only by the outer driver (BaseException: library `except Exception` cannot swallow it)."""


class Budget:
    """Exact-budget call wrapper: call B executes fully and is returned; call B+1 raises. Keeps events and the best vector."""

    def __init__(self, g, limit):
        self.g, self.limit, self.n, self.best, self.best_y, self.events = g, limit, 0, math.inf, None, []

    def __deepcopy__(self, memo):
        return self

    def __call__(self, y):
        if self.n >= self.limit:
            raise BudgetReached()
        v = float(self.g(y))
        self.n += 1
        if math.isfinite(v) and v < self.best:
            self.best, self.best_y = v, [float(t) for t in y]
            self.events.append((self.n, v))
        return v
