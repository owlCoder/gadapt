"""I64-N development probe (EXPLORATORY, not preregistered): does GAdapt depend on the arbitrary order of nominal-variable labels?
Potts-like nominal problem: N variables with K categories, cost = sum over graph edges of an iid random table C_e[a][b]. A relabelling pi (per variable)
gives an equivalent problem. Label-free methods are invariant in distribution; GAdapt-M (blending crossover, Gaussian/columnar mutation) treats labels as numbers.
  python research/i64/n_explore.py run [workers] | report
Results go to research/results/iteration64_n_dev (labelled development; no confirmatory claim)."""
import gzip, json, math, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(os.path.dirname(HERE), "results", "iteration64_n_dev")
N, K, EDGES, B, P, R, S = 10, 8, 20, 3000, 12, 16, 4  # problems, relabellings, seeds
METHODS = ("gadapt_M", "gadapt_free", "hillclimb", "random")


class Stop(BaseException):
    pass


def problem(p):
    rng = np.random.default_rng([73, p])
    edges = set()
    while len(edges) < EDGES:
        a, b = sorted(rng.choice(N, 2, replace=False))
        edges.add((int(a), int(b)))
    edges = sorted(edges)
    tables = rng.normal(size=(len(edges), K, K))
    return edges, tables


def make_cost(p, perm):
    edges, tables = problem(p)

    def cost(x):  # x: sequence of N reals in [0, K-1]; category = perm[v][int(round(x_v))]
        c = [perm[v][min(K - 1, max(0, int(round(x[v]))))] for v in range(N)]
        return float(sum(tables[i, c[a], c[b]] for i, (a, b) in enumerate(edges)))
    return cost


def run_one(task):
    p, r, s, m = task
    rng = np.random.default_rng([73, p, 1000 + r])
    perm = [rng.permutation(K) for _ in range(N)] if r > 0 else [np.arange(K) for _ in range(N)]
    cost = make_cost(p, perm)
    best, n = [math.inf], [0]

    def f(x):
        if n[0] >= B:
            raise Stop()
        v = cost(x)
        n[0] += 1
        best[0] = min(best[0], v)
        return v
    seed = 7_300_000 + 1000 * p + 100 * r + 10 * s + METHODS.index(m)
    try:
        if m.startswith("gadapt"):
            from gadapt.ga import GA
            random.seed(seed); np.random.seed(seed)
            if m == "gadapt_M":
                kw = dict(population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                          candidate_solution_mutation="variable_columnar_diversity, random",
                          decision_variable_mutation="variable_columnar_diversity,cost_diversity, random", crossover="blending")
            else:  # label-free variant of the same library: uniform crossover, uniform re-sampling mutation
                kw = dict(population_mutation="cost_diversity, random", candidate_solution_mutation="random", decision_variable_mutation="random", crossover="uniform")
            while True:
                ga = GA(cost_function=lambda x: f(x), population_size=64, percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60,
                        exit_check="generations", number_of_generations=10 ** 6, keep_elitism_percentage=50, parent_selection="roulette_wheel",
                        crossover_probability=0.5, immigration_number=0, ensure_unique_individuals=False, logging=False, timeout=10 ** 7, **kw)
                for _ in range(N):
                    ga.add(min_value=0, max_value=K - 1, step=1)
                ga.execute()
        elif m == "hillclimb":
            g = np.random.default_rng(seed)
            x = g.integers(0, K, N).astype(float); fx = f(x)
            while True:
                y = x.copy(); y[g.integers(0, N)] = g.integers(0, K); fy = f(y)
                if fy <= fx:
                    x, fx = y, fy
        else:
            g = np.random.default_rng(seed)
            while True:
                f(g.integers(0, K, N).astype(float))
    except Stop:
        pass
    return dict(task=task, best=best[0], calls=n[0])


def stage_run(workers):
    from multiprocessing import Pool
    os.makedirs(OUT, exist_ok=True)
    tasks = [(p, r, s, m) for p in range(P) for r in range(R) for s in range(S) for m in METHODS]
    with Pool(workers, maxtasksperchild=50) as pool:
        recs = list(pool.imap(run_one, tasks, chunksize=8))
    with gzip.open(os.path.join(OUT, "run.json.gz"), "wt") as fh:
        json.dump(recs, fh)
    print("done", len(recs))


def stage_report():
    recs = json.load(gzip.open(os.path.join(OUT, "run.json.gz"), "rt"))
    assert all(r["calls"] == B for r in recs)
    ref = {}
    for r in recs:
        p = r["task"][0]
        ref[p] = min(ref.get(p, math.inf), r["best"])
    L = ["# I64-N razvojna sonda (EKSPLORATIVNO, nije preregistrovano): zavisnost GAdapt-a od proizvoljnog redosleda oznaka nominalnih promenljivih\n"]
    L.append(f"Potts-slučaj: {N} promenljivih × {K} kategorija, {EDGES} grana, B = {B}; {P} problema × {R} preimenovanja × {S} semena po metodi. Jaz = (best − ref)/|ref|, ref = najbolja nađena vrednost po problemu (nije sertifikovani optimum).\n")
    L.append("| metoda | srednji jaz | std između preimenovanja (po problemu, prosek) | std semena unutar preimenovanja (prosek) | odnos između/unutar |\n|---|---|---|---|---|")
    for m in METHODS:
        gaps, btw, wit = [], [], []
        for p in range(P):
            means = []
            for r in range(R):
                v = [(x["best"] - ref[p]) / abs(ref[p]) for x in recs if x["task"][0] == p and x["task"][1] == r and x["task"][3] == m]
                means.append(np.mean(v)); wit.append(np.std(v, ddof=1))
                gaps.extend(v)
            btw.append(np.std(means, ddof=1))
        sb, sw = float(np.mean(btw)), float(np.mean(wit))
        L.append(f"| {m} | {np.mean(gaps):.4f} | {sb:.4f} | {sw:.4f} | {sb / (sw / math.sqrt(S)):.2f} |")
    L.append("\nOdnos između/unutar ≈ 1 znači da preimenovanje ne menja ishod više od šuma semena (invarijantnost); znatno > 1 znači da proizvoljan redosled oznaka utiče na rezultat.")
    open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "research", "ITERATION64_N_DEV_NOTE_SR.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": lambda: stage_run(int(sys.argv[2]) if len(sys.argv) > 2 else 8), "report": stage_report}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
