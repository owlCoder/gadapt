"""NGOpt reproducibility check: same seed, same process vs separate processes (I49 D3 follow-up)."""
import hashlib
import random
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
import nevergrad as ng  # noqa: E402

FUNCS = {
    "plateau": lambda z: float(np.sum(np.floor(z))),
    "sphere": lambda z: float(np.sum((z - (-5 + 0.37 * 10)) ** 2)),
}


def run(func, d, seed, budget=1000):
    random.seed(seed)
    np.random.seed(seed)
    calls = []

    def f(x):
        x = np.array(x, float).ravel()
        calls.append(x.copy())
        return FUNCS[func](x)

    param = ng.p.Array(shape=(d,), lower=-5.0, upper=5.0)
    param.random_state = np.random.RandomState(seed)
    opt = ng.optimizers.NGOpt(parametrization=param, budget=budget)
    try:
        opt.minimize(f)
        err = None
    except Exception as e:  # report, do not hide
        err = f"{type(e).__name__}: {e}"[:120]
    h = hashlib.sha256(b"".join(c.tobytes() for c in calls)).hexdigest()[:12]
    return calls, h, err, getattr(opt, "optim", None).__class__.__name__ if hasattr(opt, "optim") else "?"


def first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if not np.array_equal(x, y):
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


if __name__ == "__main__":
    mode, func, d, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    c1, h1, e1, name = run(func, d, seed)
    if mode == "single":
        print(f"hash={h1} n={len(c1)} err={e1} chosen={name}")
    else:
        c2, h2, e2, _ = run(func, d, seed)
        print(f"run1={h1} run2={h2} same={h1 == h2} first_diff={first_diff(c1, c2)} n={len(c1)},{len(c2)} "
              f"err={e1}|{e2} chosen={name}")
