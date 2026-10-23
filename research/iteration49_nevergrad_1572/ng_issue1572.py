# reproducer from nevergrad#1572 (kvdblom), reduced to the failing case
import ioh
import nevergrad as ng
from nevergrad.optimization.optimizerlib import ParametrizedMetaModel, CmaFmin2

f = ioh.get_problem(11, instance=1, dimension=25, problem_class=ioh.ProblemClass.REAL)
param = ng.p.Array(shape=(25,)).set_bounds(-5, 5)
param.random_state.seed(1)
opt = ParametrizedMetaModel(multivariate_optimizer=CmaFmin2)(parametrization=param, budget=200)
print(opt.minimize(f).value[:3])
del opt
