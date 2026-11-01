"""Exploratory dev-only pilot (not part of any frozen protocol): can GAdapt with a static penalty find discrete
feasible ORPD settings at 3000 power flows on the development scenarios?"""
import math, random, sys, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, "/Users/danijel/Desktop/gadapt"); sys.path.insert(0, "/Users/danijel/Desktop/gadapt/research")
from gadapt.ga import GA
from iteration56_orpd import ORPD
BUDGET = 3000

def run(task):
    case, lf, sseed, R, seed = task
    p = ORPD(case, R, lf, 0.1, sseed)
    state = dict(calls=0, best_feas=math.inf, first_feas=None)
    def cost(*args):
        x = np.array(args[0] if len(args) == 1 and hasattr(args[0], "__len__") else args, float)
        if state["calls"] >= BUDGET:
            return 1e12
        state["calls"] += 1
        e = p.evaluate(x)
        if not e["converged"]:
            return 1e9
        if e["feasible"]:
            state["best_feas"] = min(state["best_feas"], e["losses"])
            state["first_feas"] = state["first_feas"] or state["calls"]
        return e["losses"] + 1e3 * sum(e["violations"].values())
    random.seed(seed); np.random.seed(seed)
    ga = GA(cost_function=cost, probe_cost_function=False, exit_check="generations", number_of_generations=10**6,
            exit_function=lambda *a, **k: state["calls"] >= BUDGET, timeout=3600)
    for lo, hi, st in zip(p.lo, p.hi, p.step):
        ga.add(float(lo), float(hi), float(st))
    t = time.time(); ga.execute()
    return case, lf, R, seed, state["best_feas"], state["first_feas"], p.opf_losses, round(time.time() - t, 1)

if __name__ == "__main__":
    tasks = [(c, lf, ss, R, s) for c in ("case14", "case57", "case118") for lf, ss in ((0.95, 101),) for R in (9, 33)
             for s in (1, 2, 3)]
    with Pool(8) as pool:
        for r in pool.imap_unordered(run, tasks):
            print(*r, flush=True)
