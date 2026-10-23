import tempfile

from ConfigSpace import ConfigurationSpace
from smac import HyperparameterOptimizationFacade, Scenario

space = ConfigurationSpace({"x0": (-5.0, 5.0), "x1": (-5.0, 5.0)}, seed=0)
scenario = Scenario(space, deterministic=True, n_trials=40, seed=0,
                    output_directory=tempfile.mkdtemp())
smac = HyperparameterOptimizationFacade(
    scenario, lambda config, seed=0: config["x0"] ** 2 + config["x1"] ** 2,
    overwrite=True, logging_level=40)
incumbent = smac.optimize()
print(dict(incumbent))
