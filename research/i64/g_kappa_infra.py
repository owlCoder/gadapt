"""kappa of the 8 ORPD cells of I64-I (objective g(y) = f + 1000 V on the grid-index cube; central differences with h = 2 grid steps at interior grid points).
Computed WITHOUT looking at any I64-I result."""
import gzip, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
os.environ.setdefault("MBENCH", "")
for p in (HERE, os.path.join(REPO, "research"), REPO):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
import i_study as I


def kappa_cell(net, j, points=30, seed=1):
    p = I.m63._make61(net, j)
    assert I.m63.signature63(p) == I.cells()[1][f"{net}|{j}"]
    b = I.InfraBudget(p, 10 ** 9)
    d = p.d; step = 1.0 / (I.R - 1); h = 2 * step
    rng = np.random.default_rng([66, seed])
    vals = []
    for _ in range(points):
        y = (rng.integers(4, I.R - 4, d)) * step
        H = np.zeros((d, d)); f0 = b(y)
        for i in range(d):
            ei = np.zeros(d); ei[i] = h
            H[i, i] = (b(y + ei) - 2 * f0 + b(y - ei)) / h ** 2
            for k in range(i + 1, d):
                ek = np.zeros(d); ek[k] = h
                H[i, k] = H[k, i] = (b(y + ei + ek) - b(y + ei - ek) - b(y - ei + ek) + b(y - ei - ek)) / (4 * h ** 2)
        tot = np.linalg.norm(H)
        if tot > 1e-12: vals.append(np.linalg.norm(H - np.diag(np.diag(H))) / tot)
    return dict(kappa=float(np.median(vals)) if vals else None, d=d, points=len(vals), calls=b.n)


if __name__ == "__main__":
    out = {}
    for net, j in I.cells()[0]:
        out[f"{net}|{j}"] = kappa_cell(net, j); print(net, j, out[f"{net}|{j}"], flush=True)
    json.dump(out, open(os.path.join(REPO, "research", "results", "iteration64_i", "kappa_cells.json"), "w"), indent=1)
