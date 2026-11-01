"""EXPLORATORY (not preregistered): does GAdapt's precision depend on where the optimum lies in the range?"""
import random, numpy as np
from gadapt.ga import GA
R = 1000.0
def run(c, seed, budget=3000):
    calls=[0]; best=[np.inf]
    def f(a):
        calls[0]+=1
        if calls[0]>budget: return 1e30
        v=float(sum(((x-c)/R)**2 for x in a)); best[0]=min(best[0],v); return v
    random.seed(seed); np.random.seed(seed)
    ga=GA(cost_function=f, exit_check="generations", number_of_generations=10**6, exit_function=lambda: calls[0]>=budget, probe_cost_function=False)
    for _ in range(5): ga.add(0.0, R)
    ga.execute(); return best[0]
for c in (1.0, 10.0, 100.0, 500.0, 900.0, 990.0, 999.0):
    g=[run(c,s) for s in range(8)]
    print(f"optimum at {c:6.1f}: median normalized sq. gap {np.median(g):.2e}  worst {max(g):.2e}")
