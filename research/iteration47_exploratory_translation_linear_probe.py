"""EXPLORATORY: columnar diversity as a linear std ratio (monkeypatched; library untouched)."""
import statistics as stat, random, numpy as np
from gadapt.operations.decision_variable_update.variable_columnar_diversity_decision_variable_updater import ColumnarDiversityDecisionVariableUpdater as U
from gadapt.ga import GA

def linear(self):
    vals = {}
    for c in self.population:
        if c.is_immigrant: continue
        for g in c: vals.setdefault(g.decision_variable, []).append(g.value)
    for g, v in vals.items():
        if len(set(v)) <= 1:
            g.stacked = True; g.columnar_diversity_coefficient = 0.0; continue
        g.stacked = False
        s = stat.stdev(v) / (g.max_value - g.min_value)
        if g.initial_st_dev < 0: g.initial_st_dev = s
        g.columnar_diversity_coefficient = 0.0 if g.initial_st_dev == 0 else max(0.0, min(1.0, s / g.initial_st_dev))
U._update_decision_variables = linear

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
    print(f"LINEAR optimum at {c:6.1f}: median {np.median(g):.2e}  worst {max(g):.2e}")
