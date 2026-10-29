"""GAdapt-PCA (E3): one-shot adaptive encoding around GAdapt (Hansen 2008, 10.1007/978-3-540-87700-4_20: the idea is known; this is an engineering test).
Phase 1: GAdapt-M (mentor configuration) on the original coordinates for `frac` of the call budget. Phase 2: the covariance of the best `elite` share of
ALL phase-1 evaluations gives a rotated, whitened frame y = c + V (s o z), z in [-Z, Z]^D (s_i = max(sqrt(lambda_i), 1e-3 sqrt(lambda_max))); GAdapt-M runs on z
for the remaining budget (restarts allowed); y is reflected into the unit cube. Exact total budget: both phases count against the same Budget."""
import math
import random

import numpy as np

import e_algos
from e_common import BudgetReached


class SubBudgetReached(BaseException):
    pass


class _Recorder:
    """Wraps the outer budget for phase 1: stops phase 1 after `limit` calls and keeps every evaluated (y, f)."""
    def __init__(self, g, limit):
        self.g, self.limit, self.n, self.pts = g, limit, 0, []
    def __deepcopy__(self, memo): return self
    def __call__(self, y):
        if self.n >= self.limit: raise SubBudgetReached()
        v = self.g(y); self.n += 1; self.pts.append((np.array(y, float), v)); return v


def _reflect(y):
    y = np.abs(np.asarray(y, float)) % 2.0
    return np.where(y > 1.0, 2.0 - y, y)


def gadapt_pca_runner(g, d, seed, lo=0.0, hi=1.0, frac=0.2, elite=0.05, Z=4.0):
    from gadapt.ga import GA
    total = getattr(g, "limit", 12000)
    rec = _Recorder(g, int(frac * total))
    gx1 = e_algos._native(rec, lo, hi)

    def ga_run(cost, dd, lo_, hi_, rseed):
        random.seed(rseed); np.random.seed(rseed)
        ga = GA(cost_function=cost, population_size=64, population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                candidate_solution_mutation="variable_columnar_diversity, random", decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
                percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60, exit_check="generations", number_of_generations=10 ** 6,
                keep_elitism_percentage=50, parent_selection="roulette_wheel", crossover_probability=0.5, immigration_number=0, crossover="blending",
                ensure_unique_individuals=False, logging=False, timeout=10 ** 7)
        for _ in range(dd): ga.add(min_value=float(lo_), max_value=float(hi_), step=None)
        res = ga.execute()
        if not res.success: raise RuntimeError("GA.execute() returned success=False")

    rng0 = np.random.default_rng([seed, 0])
    try:                      # phase 1 (restarts inside the sub-budget are allowed)
        k = 0
        while True:
            ga_run(gx1, d, lo, hi, int(np.random.default_rng([seed, 1, k]).integers(1, 2 ** 31))); k += 1
    except SubBudgetReached:
        pass
    pts = rec.pts
    fs = np.array([p[1] for p in pts]); Y = np.array([p[0] for p in pts])
    m = max(d + 2, int(elite * len(pts)))
    idx = np.argsort(fs)[:m]
    E = Y[idx]; c = E.mean(axis=0); C = np.cov(E.T) if d > 1 else np.array([[np.var(E)]])
    C = np.atleast_2d(C)
    lam, V = np.linalg.eigh(C); lam = np.maximum(lam, 0.0)
    s = np.sqrt(lam); s = np.maximum(s, 1e-3 * (s.max() if s.max() > 0 else 1.0)); s = np.where(s > 0, s, 1e-6)

    def gz(z):
        return g(_reflect(c + V @ (s * np.asarray(z, float))))
    k = 0
    while True:               # phase 2: rotated + whitened frame; BudgetReached of the outer budget ends it
        ga_run(gz, d, -Z, Z, int(np.random.default_rng([seed, 2, k]).integers(1, 2 ** 31))); k += 1


def gadapt_cma_runner(g, d, seed, lo=0.0, hi=1.0, frac=0.5, sigma0=0.05):
    """Hybrid: GAdapt-M for `frac` of the budget, then CMA-ES (restarting, same budget wrapper) started at the best point found with a small step."""
    import cma
    total = getattr(g, "limit", 12000)
    rec = _Recorder(g, int(frac * total))
    gx1 = e_algos._native(rec, lo, hi)
    from gadapt.ga import GA

    def ga_run(cost, rseed):
        random.seed(rseed); np.random.seed(rseed)
        ga = GA(cost_function=cost, population_size=64, population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                candidate_solution_mutation="variable_columnar_diversity, random", decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
                percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60, exit_check="generations", number_of_generations=10 ** 6,
                keep_elitism_percentage=50, parent_selection="roulette_wheel", crossover_probability=0.5, immigration_number=0, crossover="blending",
                ensure_unique_individuals=False, logging=False, timeout=10 ** 7)
        for _ in range(d): ga.add(min_value=float(lo), max_value=float(hi), step=None)
        res = ga.execute()
        if not res.success: raise RuntimeError("GA.execute() returned success=False")
    try:
        k = 0
        while True:
            ga_run(gx1, int(np.random.default_rng([seed, 1, k]).integers(1, 2 ** 31))); k += 1
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
