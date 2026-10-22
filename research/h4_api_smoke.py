"""API smoke only: can each library be driven by a callable objective with a small budget? Call logs NOT inspected."""
import warnings, numpy as np; warnings.filterwarnings("ignore")
f = lambda x: 1.0
lo, hi, d = np.zeros(3), np.ones(3), 3
res = {}
def run(name, fn):
    try: fn(); res[name] = "OK"
    except Exception as e: res[name] = f"FAIL {type(e).__name__}: {str(e)[:90]}"
def pymoo_():
    from pymoo.algorithms.soo.nonconvex.ga import GA; from pymoo.core.problem import ElementwiseProblem; from pymoo.optimize import minimize
    class P(ElementwiseProblem):
        def __init__(s): super().__init__(n_var=d, n_obj=1, xl=lo, xu=hi)
        def _evaluate(s, x, out, *a, **k): out["F"] = f(x)
    minimize(P(), GA(pop_size=10), ("n_evals", 50), seed=1, verbose=False)
def deap_():
    from deap import base, creator, tools, algorithms; import random
    creator.create("FM", base.Fitness, weights=(-1.0,)); creator.create("Ind", list, fitness=creator.FM)
    tb = base.Toolbox(); tb.register("a", random.random); tb.register("ind", tools.initRepeat, creator.Ind, tb.a, d)
    tb.register("pop", tools.initRepeat, list, tb.ind); tb.register("evaluate", lambda i: (f(i),))
    tb.register("mate", tools.cxBlend, alpha=0.5); tb.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2); tb.register("select", tools.selTournament, tournsize=3)
    algorithms.eaSimple(tb.pop(n=10), tb, 0.5, 0.2, 3, verbose=False)
def pygad_():
    import pygad
    pygad.GA(num_generations=3, num_parents_mating=4, fitness_func=lambda ga, s, i: -f(s), sol_per_pop=10, num_genes=d, init_range_low=0, init_range_high=1, suppress_warnings=True).run()
def ga_():
    from geneticalgorithm import geneticalgorithm as G
    G(function=f, dimension=d, variable_type="real", variable_boundaries=np.array([[0, 1]] * d), convergence_curve=False, progress_bar=False,
      algorithm_parameters={"max_num_iteration": 3, "population_size": 10, "mutation_probability": 0.1, "elit_ratio": 0.01, "crossover_probability": 0.5, "parents_portion": 0.3, "crossover_type": "uniform", "max_iteration_without_improv": None}).run()
def ng_():
    import nevergrad as ng
    ng.optimizers.NGOpt(parametrization=ng.p.Array(shape=(d,), lower=0, upper=1), budget=50).minimize(f)
def optuna_():
    import optuna; optuna.logging.set_verbosity(optuna.logging.ERROR)
    s = optuna.create_study(sampler=optuna.samplers.CmaEsSampler(seed=1)); s.optimize(lambda t: f([t.suggest_float(f"x{i}", 0, 1) for i in range(d)]), n_trials=20)
def ps_():
    import pyswarms as ps
    ps.single.GlobalBestPSO(n_particles=10, dimensions=d, options={"c1": 0.5, "c2": 0.3, "w": 0.9}, bounds=(lo, hi)).optimize(lambda X: np.array([f(x) for x in X]), iters=3, verbose=False)
def cma_():
    import cma; cma.fmin2(f, [0.5] * d, 0.3, {"bounds": [0, 1], "maxfevals": 50, "verbose": -9})
def de_():
    from scipy.optimize import differential_evolution; differential_evolution(f, [(0, 1)] * d, maxiter=2, polish=False, seed=1)
for n, fn in [("pymoo", pymoo_), ("deap", deap_), ("pygad", pygad_), ("geneticalgorithm", ga_), ("nevergrad", ng_), ("optuna", optuna_), ("pyswarms", ps_), ("cma", cma_), ("scipy_de", de_)]:
    run(n, fn)
for k, v in res.items(): print(f"{k:17s} {v}")
