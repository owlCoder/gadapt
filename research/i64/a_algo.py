"""I64-A: ablation of the E3 hybrid. Phase 1 (GAdapt-M, 30% of the budget) is replaced by uniform random sampling; phase 2 is identical to e3_algo.gadapt_cma_runner."""
import numpy as np

from e3_algo import _Recorder, SubBudgetReached


def rand_cma_runner(g, d, seed, frac=0.3, sigma0=0.05):
    import cma
    total = getattr(g, "limit", 12000)
    rec = _Recorder(g, int(frac * total))
    rng = np.random.default_rng([seed, 5])
    try:
        while True:
            rec(rng.uniform(0.0, 1.0, d))
    except SubBudgetReached:
        pass
    best = min(rec.pts, key=lambda p: p[1])[0]
    k = 0
    while True:
        x0 = best if k == 0 else np.random.default_rng([seed, 3, k]).uniform(0, 1, d)
        sg = sigma0 if k == 0 else 0.3
        es_ = cma.CMAEvolutionStrategy(x0, sg, {"bounds": [0, 1], "seed": int(np.random.default_rng([seed, 4, k]).integers(1, 2 ** 31)), "verbose": -9})
        while not es_.stop():
            xs = es_.ask(); es_.tell(xs, [g(x) for x in xs])
        k += 1
