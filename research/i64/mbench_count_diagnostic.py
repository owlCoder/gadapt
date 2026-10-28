"""Real cost-function call counts per run for the mentor's four configurations (their classes/operators, their parameters).
Scratch diagnostic (not a study): sphere, a few runs."""
import sys, os, math, random
M = os.environ["MBENCH"]; sys.path.insert(0, M)
import numpy as np, pygad
from gadapt.ga import GA
from scipy.optimize import differential_evolution
from research_experiments.functions.sphere import sphere_func
from research_experiments.plugins.pygad.pygad_blending_crossover import blend_crossover_pygad
from research_experiments.plugins.pygad.pygad_roulette_wheel_selection import get_pygad_parent_selection
from research_experiments.runners.scipy_de_experiment import FitnessTracker, NoImprovementStopper

D = int(sys.argv[1]); RUNS = int(sys.argv[2]); POP = 64; SAT = 20; GENS = 600; LO, HI = -5.12, 5.12
class Counter:
    def __init__(self): self.n = 0
    def __call__(self, x):
        self.n += 1; return sphere_func(x)
    def __deepcopy__(self, memo): return self  # GA.execute() deep-copies the GA; keep one shared counter
out = {}
# GAdapt (mentor's diversity mutation config)
c = Counter(); res = []
for r in range(RUNS):
    random.seed(r); np.random.seed(r); c.n = 0
    ga = GA(cost_function=c, population_size=POP, population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
            candidate_solution_mutation="variable_columnar_diversity, random", decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
            percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60, exit_check="min_cost",
            keep_elitism_percentage=50, max_attempt_no=SAT, number_of_generations=GENS, parent_selection="roulette_wheel", crossover_probability=0.5,
            immigration_number=0, crossover="blending", ensure_unique_individuals=False, logging=False)
    for _ in range(D): ga.add(LO, HI, None)
    rr = ga.execute(); res.append((c.n, rr.number_of_iterations, rr.min_cost))
out["gadapt"] = res
# PyGAD random / adaptive
sel = get_pygad_parent_selection("roulette_wheel")
for name, kw in (("pygad_random", dict(mutation_type="random", mutation_probability=0.1)), ("pygad_adaptive", dict(mutation_type="adaptive", mutation_probability=[0.6, 0.1]))):
    res = []
    for r in range(RUNS):
        random.seed(r); np.random.seed(r); c = Counter()
        g = pygad.GA(num_generations=1000, num_parents_mating=32, parent_selection_type=sel, sol_per_pop=POP, num_genes=D, gene_type=float,
                     gene_space=[{"low": LO, "high": HI}] * D, fitness_func=lambda inst, s, i: 0 - c(s), suppress_warnings=True, keep_elitism=32,
                     stop_criteria=f"saturate_{SAT}", crossover_type=blend_crossover_pygad, random_seed=r, **kw)
        g.on_generation = lambda inst, inst2=None: ("stop" if g.generations_completed >= GENS - 1 else None)
        g.run(); res.append((c.n, g.generations_completed + 1, -g.best_solutions_fitness[-1]))
    out[name] = res
# SciPy DE
res = []
pm = max(1, POP // D)
for r in range(RUNS):
    tr = FitnessTracker(sphere_func); st = NoImprovementStopper(cost_function=tr, patience=SAT, number_of_generations=GENS)
    rr = differential_evolution(tr, [(LO, HI)] * D, strategy="best1exp", popsize=pm, maxiter=10000, mutation=(0.5, 1), recombination=0.7, tol=1e-7,
                                polish=False, disp=False, callback=st, seed=r)
    res.append((len(tr.all_values), rr.nit, rr.fun))
out["de"] = res
for k, v in out.items():
    calls = [x[0] for x in v]; gens = [x[1] for x in v]; fit = [x[2] for x in v]
    print(f"{k:15s} D={D} calls/run mean={np.mean(calls):9.0f} min={min(calls)} max={max(calls)}  gens={np.mean(gens):6.1f}  calls/gen={np.mean(calls)/np.mean(gens):6.1f}  mean_final={np.mean(fit):.3e}")
