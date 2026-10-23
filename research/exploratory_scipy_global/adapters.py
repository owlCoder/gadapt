"""EXPLORATORY (not preregistered): integrity-tool adapters for SciPy's other global optimizers."""
import numpy as np
from scipy import optimize


def dual_annealing(f, lower, upper, budget, seed):
    res = optimize.dual_annealing(f, list(zip(lower, upper)), maxfun=budget, rng=seed)
    f.search_done()
    return res.x, res.fun


def shgo(f, lower, upper, budget, seed):
    res = optimize.shgo(f, list(zip(lower, upper)), options={"maxfev": budget})
    f.search_done()
    return res.x, res.fun


def direct(f, lower, upper, budget, seed):
    res = optimize.direct(f, list(zip(lower, upper)), maxfun=budget)
    f.search_done()
    return res.x, res.fun


def basinhopping(f, lower, upper, budget, seed):
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(lower, upper)
    res = optimize.basinhopping(f, x0, niter=10, rng=seed,
                                minimizer_kwargs=dict(method="L-BFGS-B", bounds=list(zip(lower, upper))))
    f.search_done()
    return res.x, res.fun
