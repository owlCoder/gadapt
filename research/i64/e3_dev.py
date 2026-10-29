"""I64-E3 development: choose the share of the budget given to GAdapt before the CMA polish. Candidates (listed in advance): frac in {0.3, 0.5, 0.7};
21 ROT cells x 5 dev seeds (dev transforms, dev seeds); score = mean ECDF area A; ties -> first candidate. Writes results/iteration64_e3/freeze.json.gz."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
for p in (HERE, os.environ["MBENCH"], REPO):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
import e_common as ec, e_study as es, e3_algo as a
from multiprocessing import Pool
OUT = os.environ.get("E3_OUT", os.path.join(REPO, "research", "results", "iteration64_e3"))
CAND = (0.3, 0.5, 0.7)


def job(t):
    ci, frac, s = t
    name, d, v = es.CELLS[ci]; lo, hi = es.bounds_of(name)
    tf, _ = es.cell_transform(ci, "dev"); g = ec.make_objective(es.func_of(name), tf)
    b = ec.Budget(g, es.B)
    try: a.gadapt_cma_runner(b, d, es.seed_of("dev", ci, s), lo=lo, hi=hi, frac=frac, sigma0=0.05)
    except ec.BudgetReached: pass
    norm = es.load("normalizers"); n = norm[f"{name}|{d}"]
    gp = lambda f: max(0.0, (f - n["f_star"]) / n["s"])
    area = sum((es.B - next(c for c, f in b.events if gp(f) <= tau) + 1) / es.B for tau in es.TAUS if any(gp(f) <= tau for c, f in b.events)) / len(es.TAUS)
    return ci, frac, s, area


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(os.path.join(OUT, "freeze.json.gz")): raise SystemExit("EXISTS: freeze exists (create-once)")
    rot = [ci for ci, (n, d, v) in enumerate(es.CELLS) if v == "rot"]
    tasks = [(ci, f, s) for ci in rot for f in CAND for s in range(1, 6)]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4, maxtasksperchild=1) as pool: res = pool.map(job, tasks, chunksize=1)
    means = {f: float(np.mean([r[3] for r in res if r[1] == f])) for f in CAND}
    best = max(CAND, key=lambda f: (means[f], -CAND.index(f)))
    with gzip.open(os.path.join(OUT, "freeze.json.gz"), "wt") as fh: json.dump(dict(frac=best, means=means, candidates=list(CAND)), fh)
    print(means, "->", best)
