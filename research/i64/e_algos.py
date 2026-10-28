"""I64 stage E/R: the eleven configurations on [0,1]^D under an exact call budget (protocol §4). Each runner(g, d, seed, params)
returns when the budget wrapper raises BudgetReached (caught by the driver) or when the budget is not reached after the
unit's own restart policy ends (then a fresh restart with the remaining budget, never a stagnation stop).
Parameters are explicit arguments; the values used in the study are chosen on development data only and frozen separately.
"""
import math
import random

import numpy as np

from e_common import BudgetReached


def _native(g, lo, hi):
    """Objective on the native domain [lo, hi]^D (GAdapt, PyGAD and DE run in the mentor's original units; GAdapt's columnar diversity is
    not unit invariant, so unit-cube normalisation would change the method under test). CMA family and (1+1)-ES stay on the unit cube."""
    w = hi - lo
    if lo == 0.0 and hi == 1.0:
        return g
    return lambda x: g((np.asarray(x, float) - lo) / w)


def _restart_loop(single_run, seed, budget=None):
    """Calls single_run(rng, k) repeatedly until the budget wrapper raises BudgetReached (shared remaining budget).
    Guard: a restart that made no objective call twice in a row would loop forever, so it is an error."""
    k, idle = 0, 0
    while True:
        before = getattr(budget, "n", None)
        single_run(np.random.default_rng([seed, k]), k)
        idle = idle + 1 if (before is not None and budget.n == before) else 0
        if idle >= 2:
            raise RuntimeError("runner restarted twice without any objective call")
        k += 1


def cma_runner(g, d, seed, sigma0=0.3, popsize=None, incfactor=1):
    """CMA-ES with restarts of the same population (incfactor=1) or IPOP (incfactor=2). Margins are not used (continuous benchmark)."""
    import cma

    def single(rng, k):
        pop = (popsize or (4 + int(3 * math.log(d)))) * int(incfactor ** k)
        es = cma.CMAEvolutionStrategy(rng.uniform(0, 1, d), sigma0,
                                      {"bounds": [0, 1], "popsize": pop, "seed": int(rng.integers(1, 2 ** 31)), "verbose": -9})
        while not es.stop():
            xs = es.ask()
            es.tell(xs, [g(x) for x in xs])
    _restart_loop(single, seed, g)


def bipop_runner(g, d, seed, sigma0=0.3, popsize=None):
    """BIPOP-CMA-ES via pycma's own restart scheduler (large/small regimes); BudgetReached propagates out of cma.fmin."""
    import cma
    x0 = np.random.default_rng(seed).uniform(0, 1, d)
    cma.fmin(g, x0, sigma0, {"bounds": [0, 1], "popsize": popsize or (4 + int(3 * math.log(d))), "seed": seed + 1, "verbose": -9,
                              "maxfevals": 10 ** 9, "tolfun": 1e-11}, restarts=10 ** 6, bipop=True, incpopsize=2, restart_from_best=False)


def es11_runner(g, d, seed, sigma0=0.3, up=1.5, stagnation=1000):
    """(1+1)-ES with the 1/5th success rule, reflection at the bounds, restart from a fresh uniform point after sigma < 1e-12 or `stagnation` fails."""
    def single(rng, k):
        x = rng.uniform(0, 1, d)
        fx = g(x)
        sigma, fails = sigma0, 0
        while sigma > 1e-12 and fails < stagnation:
            y = x + sigma * rng.standard_normal(d)
            y = np.where(y < 0, -y, y)
            y = np.where(y > 1, 2 - y, y)
            y = np.clip(y, 0, 1)
            fy = g(y)
            if fy <= fx:
                x, fx, fails = y, fy, 0
                sigma *= up  # success: grow by `up`; failure: shrink by up**(-1/4) => stationary at a 1/5 success rate
            else:
                fails += 1
                sigma *= up ** (-0.25)
    _restart_loop(single, seed, g)


def de_runner(g, d, seed, popsize=64, lo=0.0, hi=1.0):
    """SciPy DE (best1exp, mentor settings) with an explicit initial population of 64 and restarts when SciPy converges."""
    from scipy.optimize import differential_evolution

    gx = _native(g, lo, hi)

    def single(rng, k):
        init = rng.uniform(lo, hi, (popsize, d))
        differential_evolution(gx, [(lo, hi)] * d, strategy="best1exp", popsize=max(1, popsize // d), maxiter=10 ** 6, mutation=(0.5, 1),
                               recombination=0.7, tol=0, atol=0, polish=False, init=init, rng=int(rng.integers(1, 2 ** 31)))
    _restart_loop(single, seed, g)


def gadapt_runner(g, d, seed, preset=False, lo=0.0, hi=1.0):
    """GAdapt with the mentor's configuration (pop 64, elitism 50%, mutations 60/60), no stagnation exit (generations only);
    `preset` adds the opt-in stability preset. Restart when the library returns before the budget is exhausted."""
    from gadapt.ga import GA
    gx = _native(g, lo, hi)

    def single(rng, k):
        random.seed(int(rng.integers(1, 2 ** 31)))
        np.random.seed(int(rng.integers(1, 2 ** 31)))
        kwargs = dict(normal_distribution_mutation_min_std_dev=1e-4, normal_distribution_mutation_min_std_dev_decay_generations=2.5) if preset else {}
        ga = GA(cost_function=gx, population_size=64,
                population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                candidate_solution_mutation="variable_columnar_diversity, random",
                decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
                percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60,
                exit_check="generations", number_of_generations=10 ** 6, keep_elitism_percentage=50,
                parent_selection="roulette_wheel", crossover_probability=0.5, immigration_number=0, crossover="blending",
                ensure_unique_individuals=False, logging=False, timeout=10 ** 7, **kwargs)
        for _ in range(d):
            ga.add(min_value=float(lo), max_value=float(hi), step=None)
        ga.execute()
    _restart_loop(single, seed, g)


def pygad_runner(g, d, seed, adaptive=False, mentor_dir=None, lo=0.0, hi=1.0):
    """PyGAD with the mentor's operators; keep_elitism 32, parents 32, restart at the library's own end (10^6 generations)."""
    import sys
    sys.path.insert(0, mentor_dir)
    import pygad
    from research_experiments.plugins.pygad.pygad_blending_crossover import blend_crossover_pygad
    from research_experiments.plugins.pygad.pygad_roulette_wheel_selection import get_pygad_parent_selection
    sel = get_pygad_parent_selection("roulette_wheel")
    gx = _native(g, lo, hi)
    mut = dict(mutation_type="adaptive", mutation_probability=[0.6, 0.1]) if adaptive else dict(mutation_type="random", mutation_probability=0.1)

    def single(rng, k):
        np.random.seed(int(rng.integers(1, 2 ** 31)))
        ga = pygad.GA(num_generations=10 ** 6, num_parents_mating=32, parent_selection_type=sel, sol_per_pop=64, num_genes=d, gene_type=float,
                      gene_space=[{"low": float(lo), "high": float(hi)}] * d, fitness_func=lambda inst, sol, idx: 0 - gx(sol), suppress_warnings=True,
                      keep_elitism=32, crossover_type=blend_crossover_pygad, **mut)
        ga.run()
    _restart_loop(single, seed, g)


RUNNERS = {"cma": cma_runner, "ipop": lambda g, d, s, **k: cma_runner(g, d, s, incfactor=2, **k), "bipop": bipop_runner, "es11": es11_runner,
           "de": de_runner, "gadapt": gadapt_runner, "gadapt_preset": lambda g, d, s, **k: gadapt_runner(g, d, s, preset=True, **k),
           "pygad_random": pygad_runner, "pygad_adaptive": lambda g, d, s, **k: pygad_runner(g, d, s, adaptive=True, **k)}
