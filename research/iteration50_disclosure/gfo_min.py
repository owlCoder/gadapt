from gradient_free_optimizers import HillClimbingOptimizer
import gradient_free_optimizers as g

opt = HillClimbingOptimizer({"x": (-5.0, 5.0)}, random_state=0)
opt.search(lambda p: p["x"] ** 2 + 1.0, n_iter=50, optimum="minimum", verbosity=False)
print(g.__version__, "best_score =", opt.best_score, "| f(best_para) =", opt.best_para["x"] ** 2 + 1.0)
