import numpy as np
import nevergrad as ng


def run(seed):
    param = ng.p.Array(shape=(10,), lower=-5.0, upper=5.0)
    param.random_state.seed(seed)
    opt = ng.optimizers.NGOpt(parametrization=param, budget=1000)
    print(opt.optim.name)  # ParametrizedMetaModel(multivariate_optimizer=CmaFmin2)
    return opt.minimize(lambda x: float(np.sum(x ** 2))).value


print(run(0)[:3])
print(run(0)[:3])
