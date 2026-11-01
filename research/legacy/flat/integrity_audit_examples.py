"""Example adapters for research/integrity_audit_tool.py (each runs in the library's own environment)."""
import tempfile


def gfo_hill_climbing(f, lower, upper, budget, seed):
    from gradient_free_optimizers import HillClimbingOptimizer
    keys = [f"x{i:02d}" for i in range(len(lower))]
    opt = HillClimbingOptimizer({k: (float(l), float(h)) for k, l, h in zip(keys, lower, upper)}, random_state=seed)
    opt.search(lambda p: f([p[k] for k in keys]), n_iter=budget, optimum="minimum", verbosity=False)
    f.search_done()
    return [opt.best_para[k] for k in keys], opt.best_score


def smac_hpo(f, lower, upper, budget, seed):
    from ConfigSpace import ConfigurationSpace
    from smac import HyperparameterOptimizationFacade, Scenario
    keys = [f"x{i:02d}" for i in range(len(lower))]
    space = ConfigurationSpace({k: (float(l), float(h)) for k, l, h in zip(keys, lower, upper)}, seed=seed)
    scenario = Scenario(space, deterministic=True, n_trials=budget, seed=seed, output_directory=tempfile.mkdtemp())
    smac = HyperparameterOptimizationFacade(scenario, lambda c, seed=0: f([c[k] for k in keys]),
                                            overwrite=True, logging_level=40)
    incumbent = smac.optimize()
    f.search_done()
    return [incumbent[k] for k in keys], None
