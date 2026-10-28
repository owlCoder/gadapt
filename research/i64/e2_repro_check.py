"""E2 pre-run gate: (1) archived E GAdapt-M traces are reproduced bit-exactly by the current library/environment on 2 seeds per cell;
(2) GA.execute() never returns success=False in a diagnostic replica of the GAdapt-M runner (63 cells x 2 seeds)."""
import os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.environ["MBENCH"], os.path.dirname(os.path.dirname(HERE))):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
import e_algos, e_common as ec, e_study as es
from multiprocessing import Pool


def repro(task):
    r = es.run_task(task)
    return task["cell"], task["seed"], r["ok"], r["calls"], r["best_f"], r["events"]


def success_probe(task):
    from gadapt.ga import GA
    name, d, v = es.CELLS[task["cell"]]
    lo, hi = es.bounds_of(name)
    tf, info = es.cell_transform(task["cell"], "run")
    b = ec.Budget(ec.make_objective(es.func_of(name), tf), es.B)
    gx = e_algos._native(b, lo, hi)
    fails, execs = 0, 0
    k = 0
    try:
        while True:
            rng = np.random.default_rng([task["seed"], k]); k += 1
            random.seed(int(rng.integers(1, 2 ** 31))); np.random.seed(int(rng.integers(1, 2 ** 31)))
            ga = GA(cost_function=gx, population_size=64, population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                    candidate_solution_mutation="variable_columnar_diversity, random", decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
                    percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60, exit_check="generations",
                    number_of_generations=10 ** 6, keep_elitism_percentage=50, parent_selection="roulette_wheel", crossover_probability=0.5,
                    immigration_number=0, crossover="blending", ensure_unique_individuals=False, logging=False, timeout=10 ** 7)
            for _ in range(d): ga.add(min_value=float(lo), max_value=float(hi), step=None)
            res = ga.execute(); execs += 1
            if not res.success: fails += 1
    except ec.BudgetReached:
        pass
    return task["cell"], task["seed"], execs, fails


if __name__ == "__main__":
    tasks = [dict(config="gadapt", params=None, cell=ci, seed=es.seed_of("run", ci, s), purpose="run") for ci in range(len(es.CELLS)) for s in (1, 2)]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 8, maxtasksperchild=1) as pool:
        out = pool.map(repro, tasks, chunksize=1)
        probe = pool.map(success_probe, tasks, chunksize=1)
    mism = []
    for ci, seed, ok, calls, best, ev in out:
        arch = next(r for r in es.load(f"run_part_{ci}")["records"] if r["task"]["config"] == "gadapt" and r["task"]["seed"] == seed)
        if not (ok and calls == arch["calls"] and best == arch["best_f"] and [tuple(e) for e in ev] == [tuple(e) for e in arch["events"]]):
            mism.append((ci, seed))
    print(json.dumps(dict(reproduced=len(out) - len(mism), total=len(out), mismatches=mism[:10], executes=sum(p[2] for p in probe),
                          success_false=sum(p[3] for p in probe), restarts_gt1=sum(1 for p in probe if p[2] > 1))))
