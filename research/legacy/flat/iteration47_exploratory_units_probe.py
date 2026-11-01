"""EXPLORATORY: same normalized problem in different units (range R); default GAdapt."""
import random, numpy as np
from gadapt.ga import GA
def run(R, pos, seed, budget=3000):
    calls=[0]; best=[np.inf]; c=pos*R
    def f(a):
        calls[0]+=1
        if calls[0]>budget: return 1e30
        v=float(sum(((x-c)/R)**2 for x in a)); best[0]=min(best[0],v); return v
    random.seed(seed); np.random.seed(seed)
    ga=GA(cost_function=f, exit_check="generations", number_of_generations=10**6, exit_function=lambda: calls[0]>=budget, probe_cost_function=False)
    for _ in range(5): ga.add(0.0, R)
    ga.execute(); return best[0]
for pos in (0.5, 0.999):
    for R in (0.12, 1.0, 1000.0, 1e6):
        g=[run(R,pos,s) for s in range(8)]
        print(f"pos {pos} R={R:>9}: median {np.median(g):.2e} worst {max(g):.2e}")
