"""I64-I2: the GAdapt -> CMA-ES hybrid (E3 recipe, frac = 0.3 from the E3 development) on the 8 ORPD cells of I64-I, paired with the I64-I records.
Same objective, cells, seeds, budget and independent witness check as i_study.py. Spec: research/ITERATION64_I2_SPEC.md.   run [workers] | analyse"""
import gzip, json, math, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import numpy as np
import i_study as I
import e_algos, e_common as ec
import e3_algo

OUT = os.environ.get("I2_OUT", os.path.join(REPO, "research", "results", "iteration64_i2"))
FRAC = 0.3


def hybrid_runner(g, d, seed):
    """Phase 1: GAdapt-M on the grid (step 1/(R-1)) for FRAC of the budget (sub-budget with restarts); phase 2: CMA-ES from the best phase-1 point (sigma0 = 0.05), restarts from random points (sigma0 = 0.3); the objective snaps to the grid."""
    import cma
    from gadapt.ga import GA
    rec = e3_algo._Recorder(g, int(FRAC * g.limit))

    def ga_run(rseed):
        random.seed(rseed); np.random.seed(rseed)
        ga = GA(cost_function=rec, population_size=64, population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                candidate_solution_mutation="variable_columnar_diversity, random", decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
                percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60, exit_check="generations", number_of_generations=10 ** 6,
                keep_elitism_percentage=50, parent_selection="roulette_wheel", crossover_probability=0.5, immigration_number=0, crossover="blending",
                ensure_unique_individuals=False, logging=False, timeout=10 ** 7)
        for _ in range(d): ga.add(min_value=0.0, max_value=1.0, step=1.0 / (I.R - 1))
        res = ga.execute()
        if not res.success: raise RuntimeError("GA.execute() returned success=False")
    try:
        k = 0
        while True:
            ga_run(int(np.random.default_rng([seed, 1, k]).integers(1, 2 ** 31))); k += 1
    except e3_algo.SubBudgetReached:
        pass
    best = min(rec.pts, key=lambda p: p[1])[0]
    k = 0
    while True:
        x0 = best if k == 0 else np.random.default_rng([seed, 3, k]).uniform(0, 1, d)
        sg = 0.05 if k == 0 else 0.3
        es_ = cma.CMAEvolutionStrategy(x0, sg, {"bounds": [0, 1], "seed": int(np.random.default_rng([seed, 4, k]).integers(1, 2 ** 31)), "verbose": -9})
        while not es_.stop():
            xs = es_.ask(); es_.tell(xs, [g(x) for x in xs])
        k += 1


def run_task(task):
    import traceback
    try:
        net, j = task["net"], task["j"]
        p = I.m63._make61(net, j)
        if I.m63.signature63(p) != I.cells()[1][f"{net}|{j}"]: raise RuntimeError("scenario differs from the frozen I63 roster")
        b = I.InfraBudget(p, I.B); b.limit = I.B; t0 = time.time()
        try:
            hybrid_runner(b, p.d, task["seed"])
            return dict(task=task, ok=False, error="runner returned without exhausting the budget", calls=b.n)
        except ec.BudgetReached:
            pass
        if b.best_x is not None:
            q = I.i61.independent_check((net, j, b.best_x))
            if not (q.get("valid") and q.get("converged") and q.get("feasible") and math.isclose(q["losses"], b.best_f, rel_tol=1e-8, abs_tol=1e-8)):
                raise RuntimeError(f"independent witness check failed {q}")
        return dict(task=task, ok=b.n == I.B, witness_checked=b.best_x is not None, calls=b.n, best_feasible=(b.best_f if math.isfinite(b.best_f) else None),
                    best_x=b.best_x, events=b.events, failures=b.failures, r=p.opf_losses, seconds=time.time() - t0)
    except Exception:
        return dict(task=task, ok=False, error=traceback.format_exc()[-1500:], calls=None)


def path(n): os.makedirs(OUT, exist_ok=True); return os.path.join(OUT, n + ".json.gz")
def save(n, d):
    with gzip.open(path(n), "wt") as fh: json.dump(d, fh)
def load(n):
    with gzip.open(path(n), "rt") as fh: return json.load(fh)


def stage_run(workers):
    from multiprocessing import Pool
    if os.path.exists(path("run")): raise SystemExit("EXISTS: run exists (create-once)")
    cs, _ = I.cells(); allrecs = []
    for ci, (net, j) in enumerate(cs):
        part = f"run2_part_{ci}"
        if os.path.exists(path(part)):
            old = load(part)["records"]
            if len(old) != I.N_SEEDS or not all(r["ok"] and r["calls"] == I.B for r in old): raise SystemExit(f"STOP: stored part {part} incomplete")
            allrecs.extend(old); continue
        tasks = [dict(config="gadapt_hyb", net=net, j=j, seed=I.seed_of(ci, s), s=s, ci=ci) for s in range(1, I.N_SEEDS + 1)]
        with Pool(workers, maxtasksperchild=1) as pool: recs = list(pool.imap(run_task, tasks, chunksize=1))
        for i, r in enumerate(recs):
            if not r.get("ok"):
                with Pool(1, maxtasksperchild=1) as pool: again = pool.apply(run_task, (tasks[i],))
                again["rerun"], again["first_attempt"] = True, r; recs[i] = again
        save(part, dict(records=recs))
        bad = [r for r in recs if not r.get("ok")]
        if bad: raise SystemExit(f"STOP: {len(bad)} runs failed twice in {net} {j}: {bad[0].get('error')}")
        allrecs.extend(recs); print("cell", net, j, "done", flush=True)
    save("run", dict(records=allrecs, frac=FRAC, i_run_sha256=I.sha(os.path.join(I.OUT, "run.json.gz")) if os.path.exists(os.path.join(I.OUT, "run.json.gz")) else None))


def stage_analyse():
    if os.path.exists(path("analysis")): raise SystemExit("EXISTS: analysis exists (create-once)")
    d2 = load("run")["records"]
    if not os.path.exists(os.path.join(I.OUT, "run.json.gz")): raise SystemExit("STOP: the I64-I run is not complete")
    ref = I.load("run")["records"]; cs, _ = I.cells(); N = I.N_SEEDS
    def Lof(r):
        f = r["best_feasible"]
        if f is None: return 1.0, 0.0
        G = max((f - r["r"]) / r["r"], 0.0); return G / (1 + G), 1.0
    arr = {}
    for r in ref + d2:
        c = r["task"]["config"]
        if c not in ("gadapt", "ipop", "gadapt_hyb"): continue
        arr.setdefault((r["task"]["ci"], c), {})[r["task"]["s"]] = Lof(r)
    A = {k: np.array([v[s] for s in sorted(v)]) for k, v in arr.items()}
    for k, v in A.items(): assert len(v) == N, k
    cw = {ci: 1.0 / len(cs) for ci in range(len(cs))}
    def cv(c, ci, idx): return I.cvar(list(A[(ci, c)][idx[ci], 0]))
    def pf(c, ci, idx): return A[(ci, c)][idx[ci], 1].mean()
    def s_c(idx):
        S = lambda f: sum(cw[ci] * f(ci) for ci in cw)
        return np.array([S(lambda ci: cv("gadapt", ci, idx)) - S(lambda ci: cv("gadapt_hyb", ci, idx)), S(lambda ci: pf("gadapt_hyb", ci, idx)) - S(lambda ci: pf("gadapt", ci, idx)),
                         S(lambda ci: cv("ipop", ci, idx)) - S(lambda ci: cv("gadapt_hyb", ci, idx)), S(lambda ci: pf("gadapt_hyb", ci, idx)) - S(lambda ci: pf("ipop", ci, idx))])
    full = {ci: np.arange(N) for ci in cw}; point = s_c(full); rng = np.random.default_rng(68)
    R = int(os.environ.get("I2_BOOT", "20000")); boots = np.array([s_c({ci: rng.integers(0, N, N) for ci in cw}) for _ in range(R)])
    finite = bool(np.all(np.isfinite(point)) and np.all(np.isfinite(boots))); se = boots.std(axis=0, ddof=1) if finite else np.full(4, np.nan)
    lo, hi = np.full(4, -1.0), np.ones(4); t = float("nan")
    if finite:
        active = (se > 0) & (np.ptp(boots, axis=0) > 0)
        t = float(np.quantile(np.max(np.abs(boots[:, active] - point[active]) / se[active], axis=1), 0.975)) if active.any() else 0.0
        lo[active] = point[active] - t * se[active]; hi[active] = point[active] + t * se[active]
        u = 1 - (0.025 / 4) ** (1 / (len(cw) * N))
        for h, (a, b) in ((1, ("gadapt_hyb", "gadapt")), (3, ("gadapt_hyb", "ipop"))):
            if all(np.all(A[(ci, a)][:, 1] - A[(ci, b)][:, 1] == 0) for ci in cw): lo[h], hi[h] = -u, u
    names = ["CVaR(M)-CVaR(H)", "P(H)-P(M)", "CVaR(IPOP)-CVaR(H)", "P(H)-P(IPOP)"]
    con = {n: dict(estimate=float(p), lower=float(a), upper=float(b)) for n, p, a, b in zip(names, point, lo, hi)}
    tri = lambda sup, opp: "blocked" if not finite else ("supported" if sup else ("opposite" if opp else "undecided"))
    h1 = tri(con[names[0]]["lower"] > 0 and con[names[1]]["lower"] >= -0.05, con[names[0]]["upper"] < 0 or con[names[1]]["upper"] < -0.05)
    h2 = tri(con[names[2]]["lower"] > 0 and con[names[3]]["lower"] >= -0.05, con[names[2]]["upper"] < 0 or con[names[3]]["upper"] < -0.05)
    agg = {c: dict(P=float(sum(cw[ci] * A[(ci, c)][:, 1].mean() for ci in cw)), cvar90=float(sum(cw[ci] * I.cvar(list(A[(ci, c)][:, 0])) for ci in cw))) for c in ("gadapt", "gadapt_hyb", "ipop")}
    out = dict(H64h1=h1, H64h2=h2, tstar=t, alpha=0.05, bootstrap=R, contrasts=con, aggregate=agg)
    save("analysis", out); print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    if st == "run": stage_run(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    elif st == "analyse": stage_analyse()
    else: print(__doc__)
