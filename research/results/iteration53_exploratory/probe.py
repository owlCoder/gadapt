"""Exploratory probe (not preregistered): GAdapt on a 10-D quadratic.
Translation dependence (f* = 0 vs 1e4) and step size vs distance of the best to x*."""
import json, random, sys
import numpy as np
sys.path.insert(0, "/Users/danijel/Desktop/gadapt")
from gadapt.ga import GA

D, LO, HI = 10, -5.0, 5.0
CONFIGS = {
    "default": {},
    "decay": {"normal_distribution_mutation_min_std_dev": 1e-4,
              "normal_distribution_mutation_min_std_dev_decay_generations": 2.5},
}

def run(seed, fstar, cfg):
    rng = np.random.default_rng(1000 + seed)
    xs = rng.uniform(-3, 3, D)
    log = []
    def f(args):
        x = np.asarray(args, float)
        v = fstar + float(np.sum((x - xs) ** 2))
        log.append((float(np.linalg.norm(x - xs)), v))
        return v
    random.seed(seed); np.random.seed(seed)
    ga = GA(cost_function=f, exit_check="generations", number_of_generations=400,
            probe_cost_function=False, **CONFIGS[cfg])
    for _ in range(D):
        ga.add(LO, HI)
    res = ga.execute()
    d = np.array([a for a, _ in log]); v = np.array([b for _, b in log])
    best_d = np.minimum.accumulate(np.where(v == np.minimum.accumulate(v), d, np.inf))
    # step proxy: distance of each new point to x* relative to best-so-far distance
    ratio = d[1:] / np.maximum(best_d[:-1], 1e-300)
    n = len(d)
    q = lambda a: float(np.median(a))
    return {"seed": seed, "fstar": fstar, "cfg": cfg, "evals": n,
            "gap": float(res.min_cost - fstar), "best_dist": float(best_d[-1]),
            "ratio_q4": [q(ratio[i * (n - 1) // 4:(i + 1) * (n - 1) // 4]) for i in range(4)]}

out = []
for cfg in CONFIGS:
    for fstar in (0.0, 1e4):
        for seed in range(6):
            r = run(seed, fstar, cfg); out.append(r)
            print(json.dumps(r), flush=True)
json.dump(out, open("probe.json", "w"), indent=1)
