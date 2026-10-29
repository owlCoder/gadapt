"""I64-G development: a cheap coupling index kappa of an objective, and its relation to the GAdapt-vs-CMA outcome on the E cells (post hoc DEVELOPMENT,
labelled as such). kappa = median over sample points of ||H - diag(H)||_F / ||H||_F, H = finite-difference Hessian in the unit cube (central differences)."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
for p in (HERE, os.environ["MBENCH"], REPO):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
import e_common as ec, e_study as es


def kappa(g, d, rng, points=20, h=1e-3):
    vals = []
    for _ in range(points):
        y = rng.uniform(0.2, 0.8, d)
        H = np.zeros((d, d)); f0 = g(y)
        for i in range(d):
            ei = np.zeros(d); ei[i] = h
            H[i, i] = (g(y + ei) - 2 * f0 + g(y - ei)) / h ** 2
            for j in range(i + 1, d):
                ej = np.zeros(d); ej[j] = h
                H[i, j] = H[j, i] = (g(y + ei + ej) - g(y + ei - ej) - g(y - ei + ej) + g(y - ei - ej)) / (4 * h ** 2)
        tot = np.linalg.norm(H)
        if tot > 1e-12:
            vals.append(np.linalg.norm(H - np.diag(np.diag(H))) / tot)
    return float(np.median(vals)) if vals else float("nan")


if __name__ == "__main__":
    out = {}
    for ci, (name, d, v) in enumerate(es.CELLS):
        tf, info = es.cell_transform(ci, "run")
        g = ec.make_objective(es.func_of(name), tf)
        out[ci] = dict(cell=[name, d, v], kappa=kappa(g, d, np.random.default_rng([65, ci])))
    json.dump(out, open(os.path.join(REPO, "research", "results", "iteration64_e", "kappa_cells.json"), "w"), indent=1)
    print({k: (v["cell"], round(v["kappa"], 3)) for k, v in list(out.items())[:12]})
