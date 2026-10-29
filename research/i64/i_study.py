"""I64-I: the nine E configurations on the discrete ORPD (BusORPD, R = 17) under an exact budget of real power-flow calls.
Spec: research/ITERATION64_I_SPEC.md (+ amendment). Stages (create-once; own process):  run [workers] | analyse

Variables are the grid INDICES normalised to [0,1] (k/(R-1)); every configuration sees the same objective g(y): y -> grid point -> AC power flow ->
f + 1000*V (the I56 'SP' scalar; failed power flow = 2*r + 1000*10 exactly as the frozen I56 evaluator). GAdapt and PyGAD use the grid directly
(step = 1/(R-1)); DE, CMA family and (1+1)-ES are continuous on the cube and the objective snaps to the nearest grid point.
"""
import gzip, hashlib, json, math, os, random, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
MBENCH = os.environ.get("MBENCH", "")
for p in (HERE, os.path.join(REPO, "research"), MBENCH, REPO):
    if p and p not in sys.path: sys.path.insert(0, p)
import numpy as np
import e_algos, e_common as ec
import iteration56_cht_study as i56
import iteration63_replication as m63        # I63 scenarios (j = 2,3,4), roster hashes, normalizers (module-level patches are the I63 ones)
import iteration61_replication as i61

OUT = os.environ.get("I_OUT", os.path.join(REPO, "research", "results", "iteration64_i"))
B = int(os.environ.get("I_B", "12000")); N_SEEDS = int(os.environ.get("I_SEEDS", "30")); R = 17
CONFIGS = ("gadapt", "gadapt_preset", "pygad_random", "pygad_adaptive", "de", "cma", "ipop", "bipop", "es11")
SEED_BASE = 68_000_000
SRC63 = os.path.join(REPO, "research", "results", "iteration63")        # frozen I63 roster/normalizers (read only, hash-checked)
E_FREEZE = os.path.join(REPO, "research", "results", "iteration64_e", "freeze.json.gz")


def sha(path):
    with open(path, "rb") as fh: return hashlib.sha256(fh.read()).hexdigest()


def cells():
    with gzip.open(os.path.join(SRC63, "roster.json.gz"), "rt") as fh: roster = json.load(fh)
    return [tuple(x) for x in roster["test"]], roster["scenario_hashes"]


def seed_of(ci, s): return SEED_BASE + 1000 * ci + s


class InfraBudget:
    """Exact call budget on the real power flow; tracks the best FEASIBLE loss (witness vector) and the strictly improving feasible events."""
    def __init__(self, problem, limit):
        self.p, self.limit, self.n = problem, limit, 0
        self.best_f, self.best_x, self.events, self.failures = math.inf, None, [], 0
        self.f_ref = problem.opf_losses
    def __deepcopy__(self, memo): return self
    @property
    def best(self): return self.best_f
    def __call__(self, y):
        if self.n >= self.limit: raise ec.BudgetReached()
        y = np.clip(np.asarray(y, float), 0.0, 1.0)
        x = self.p.lo + y * (self.p.hi - self.p.lo)
        info = self.p.evaluate(x)
        self.n += 1
        if not info["converged"]:
            self.failures += 1; return 2.0 * self.f_ref + i56.SP_WEIGHT * i56.V_FAIL
        v = float(sum(max(0.0, c - i56.TOL) for c in info["violations"].values()))
        f = float(info["losses"])
        if v == 0.0 and f < self.best_f:
            self.best_f, self.best_x = f, [float(t) for t in self.p.snap(x)]
            self.events.append((self.n, f))
        return f + i56.SP_WEIGHT * v


def gadapt_runner(g, d, seed, preset=False):
    from gadapt.ga import GA
    def single(rng, k):
        random.seed(int(rng.integers(1, 2 ** 31))); np.random.seed(int(rng.integers(1, 2 ** 31)))
        kw = dict(normal_distribution_mutation_min_std_dev=1e-4, normal_distribution_mutation_min_std_dev_decay_generations=2.5) if preset else {}
        ga = GA(cost_function=g, population_size=64, population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                candidate_solution_mutation="variable_columnar_diversity, random", decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
                percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60, exit_check="generations", number_of_generations=10 ** 6,
                keep_elitism_percentage=50, parent_selection="roulette_wheel", crossover_probability=0.5, immigration_number=0, crossover="blending",
                ensure_unique_individuals=False, logging=False, timeout=10 ** 7, **kw)
        for _ in range(d): ga.add(min_value=0.0, max_value=1.0, step=1.0 / (R - 1))
        res = ga.execute()
        if not res.success: raise RuntimeError("GA.execute() returned success=False")
    e_algos._restart_loop(single, seed, g)


def pygad_runner(g, d, seed, adaptive=False):
    import pygad
    from research_experiments.plugins.pygad.pygad_blending_crossover import blend_crossover_pygad
    from research_experiments.plugins.pygad.pygad_roulette_wheel_selection import get_pygad_parent_selection
    sel = get_pygad_parent_selection("roulette_wheel")
    mut = dict(mutation_type="adaptive", mutation_probability=[0.6, 0.1]) if adaptive else dict(mutation_type="random", mutation_probability=0.1)
    step = 1.0 / (R - 1)
    space = [dict(low=0.0, high=float(np.nextafter(1.0, np.inf)), step=step) for _ in range(d)]  # high just above 1.0 so that all R grid points are reachable

    def cross(parents, size, inst):
        return np.clip(blend_crossover_pygad(parents, size, inst), 0.0, 1.0)

    def single(rng, k):
        rs = int(rng.integers(1, 2 ** 31))
        np.random.seed(rs); random.seed(rs)
        ga = pygad.GA(num_generations=10 ** 6, num_parents_mating=32, parent_selection_type=sel, sol_per_pop=64, num_genes=d, gene_type=float,
                      gene_space=space, fitness_func=lambda inst, sol, idx: 0 - g(sol), suppress_warnings=True,
                      keep_elitism=32, crossover_type=cross, random_seed=rs, **mut)
        ga.run()
    e_algos._restart_loop(single, seed, g)


def runner(name, params):
    if name == "gadapt": return lambda g, d, s: gadapt_runner(g, d, s)
    if name == "gadapt_preset": return lambda g, d, s: gadapt_runner(g, d, s, preset=True)
    if name == "pygad_random": return lambda g, d, s: pygad_runner(g, d, s)
    if name == "pygad_adaptive": return lambda g, d, s: pygad_runner(g, d, s, adaptive=True)
    fn = e_algos.RUNNERS[name]
    return lambda g, d, s: fn(g, d, s, **(params.get(name) or {}))


def run_task(task):
    try:
        net, j = task["net"], task["j"]
        p = i61._make61(net, j) if hasattr(i61, "_make61") else m63._make61(net, j)
        want = cells()[1][f"{net}|{j}"]
        if m63.signature63(p) != want: raise RuntimeError("scenario differs from the frozen I63 roster")
        b = InfraBudget(p, B); t0 = time.time()
        try:
            runner(task["config"], task["params"])(b, p.d, task["seed"])
            return dict(task=task, ok=False, error="runner returned without exhausting the budget", calls=b.n)
        except ec.BudgetReached:
            pass
        if b.best_x is not None:  # independent witness check, outside the optimisation budget
            q = i61.independent_check((net, j, b.best_x))
            if not (q.get("valid") and q.get("converged") and q.get("feasible") and math.isclose(q["losses"], b.best_f, rel_tol=1e-8, abs_tol=1e-8)):
                raise RuntimeError(f"independent witness check failed {q}")
        return dict(task=task, ok=b.n == B, witness_checked=b.best_x is not None, calls=b.n, best_feasible=(b.best_f if math.isfinite(b.best_f) else None), best_x=b.best_x, events=b.events,
                    failures=b.failures, r=p.opf_losses, seconds=time.time() - t0)
    except Exception as exc:
        import traceback
        return dict(task=task, ok=False, error=traceback.format_exc()[-1500:], calls=None)


def path(n): os.makedirs(OUT, exist_ok=True); return os.path.join(OUT, n + ".json.gz")
def save(n, d):
    with gzip.open(path(n), "wt") as fh: json.dump(d, fh)
def load(n):
    with gzip.open(path(n), "rt") as fh: return json.load(fh)


def manifest():
    import platform
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.split()
    tree = {}
    for root, _, files in os.walk(os.path.join(REPO, "gadapt")):
        for f in sorted(files):
            if f.endswith(".py"): tree[os.path.relpath(os.path.join(root, f), REPO)] = sha(os.path.join(root, f))
    spec = os.path.join(REPO, "research", "ITERATION64_I_SPEC.md")
    return dict(python=platform.python_version(), pip_freeze=freeze, gadapt_tree=tree, mentor_head=subprocess.run(["git", "-C", MBENCH, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
                files={f: sha(os.path.join(HERE, f)) for f in ("i_study.py", "e_algos.py", "e_common.py")}, spec=sha(spec),
                i63_roster=sha(os.path.join(SRC63, "roster.json.gz")), e_freeze=sha(E_FREEZE), settings=dict(B=B, N=N_SEEDS, R=R, configs=CONFIGS, seed_base=SEED_BASE))


def stage_run(workers):
    from multiprocessing import Pool
    if os.path.exists(path("run")): raise SystemExit("EXISTS: run exists (create-once)")
    mf = manifest()
    if os.path.exists(path("manifest_pre")):
        if json.loads(json.dumps(load("manifest_pre"))) != json.loads(json.dumps(mf)): raise SystemExit("STOP: build differs from the pre-run manifest (resume refused)")
    else:
        save("manifest_pre", mf)
    cs, _ = cells()
    params = json.load(gzip.open(E_FREEZE, "rt"))["params"]
    allrecs = []
    for ci, (net, j) in enumerate(cs):
        part = f"run_part_{ci}"
        if os.path.exists(path(part)):
            old = load(part)["records"]
            keys = {(r["task"]["config"], r["task"]["s"]) for r in old}
            if len(old) != len(CONFIGS) * N_SEEDS or len(keys) != len(old) or not all(r["ok"] and r["calls"] == B for r in old):
                raise SystemExit(f"STOP: stored part {part} is incomplete or failed; controlled recovery required")
            allrecs.extend(old); continue
        tasks = [dict(config=c, params=params, net=net, j=j, seed=seed_of(ci, s), s=s, ci=ci) for s in range(1, N_SEEDS + 1) for c in CONFIGS]
        with Pool(workers, maxtasksperchild=1) as pool: recs = list(pool.imap(run_task, tasks, chunksize=1))
        for i, r in enumerate(recs):
            if not r.get("ok"):
                with Pool(1, maxtasksperchild=1) as pool: again = pool.apply(run_task, (tasks[i],))
                again["rerun"], again["first_attempt"] = True, r; recs[i] = again
        bad = [r for r in recs if not r.get("ok")]
        save(part, dict(records=recs))
        if bad: raise SystemExit(f"STOP: {len(bad)} runs failed technically twice in {net} {j}: {bad[0].get('error')}")
        allrecs.extend(recs); print("cell", net, j, "done", flush=True)
    save("run", dict(records=allrecs, e_freeze_sha256=sha(E_FREEZE), i63_roster_sha256=sha(os.path.join(SRC63, "roster.json.gz")),
                     git_head=subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()))


def cvar(v, share=0.1):
    k = max(1, int(math.ceil(share * len(v)))); return float(np.mean(sorted(v)[-k:]))


def stage_analyse():
    if os.path.exists(path("analysis")): raise SystemExit("EXISTS: analysis exists (create-once)")
    runs = load("run")["records"]; cs, _ = cells()
    assert len(runs) == len(cs) * len(CONFIGS) * N_SEEDS and all(r["ok"] and r["calls"] == B for r in runs)
    def stats_of(r, B_):
        f = None
        for c, ff in r["events"]:
            if c <= B_: f = ff
        if f is None: return 1.0, 0.0, math.inf       # (L, feasible, G)
        G = (f - r["r"]) / r["r"]; Gp = max(G, 0.0)
        return Gp / (1 + Gp), 1.0, G
    arr = {}
    for r in runs:
        arr.setdefault((r["task"]["ci"], r["task"]["config"]), {})[r["task"]["s"]] = {B_: stats_of(r, B_) for B_ in (3000, B)}
    for k, v in arr.items(): assert sorted(v) == list(range(1, N_SEEDS + 1)), k
    A = {(k, B_): np.array([arr[k][s][B_] for s in range(1, N_SEEDS + 1)]) for k in arr for B_ in (3000, B)}
    cw = {ci: 1.0 / len(cs) for ci in range(len(cs))}
    N = N_SEEDS
    comps = [c for c in CONFIGS if c != "gadapt"]
    def agg(idx, c, B_, what):
        if what == "P": return sum(cw[ci] * A[((ci, c), B_)][idx[ci], 1].mean() for ci in cw)
        if what == "CV": return sum(cw[ci] * cvar(list(A[((ci, c), B_)][idx[ci], 0])) for ci in cw)
    def s_c(idx):
        return np.array([agg(idx, c, B, "P") - agg(idx, "gadapt", B, "P") for c in comps] + [agg(idx, c, B, "CV") - agg(idx, "gadapt", B, "CV") for c in comps]
                        + [0.8 * agg(idx, "gadapt", B, "CV") - agg(idx, "gadapt_preset", B, "CV"), agg(idx, "gadapt_preset", B, "P") - agg(idx, "gadapt", B, "P")])
    full = {ci: np.arange(N) for ci in cw}; point = s_c(full); rng = np.random.default_rng(67)
    R_ = int(os.environ.get("I_BOOT", "20000")); boots = np.array([s_c({ci: rng.integers(0, N, N) for ci in cw}) for _ in range(R_)])
    finite = bool(np.all(np.isfinite(point)) and np.all(np.isfinite(boots))); se = boots.std(axis=0, ddof=1) if finite else np.full(len(point), np.nan)
    blocked = not finite
    lo, hi = np.full(len(point), -1.0), np.ones(len(point)); hi[16] = 0.8; t = float("nan")
    if finite:
        # alpha 0.025 for the active bootstrap contrasts, 0.025 for a conservative fallback of degenerate ones (Codex 088)
        active = (se > 0) & (np.ptp(boots, axis=0) > 0)
        t = float(np.quantile(np.max(np.abs(boots[:, active] - point[active]) / se[active], axis=1), 0.975)) if active.any() else 0.0
        lo[active] = point[active] - t * se[active]; hi[active] = point[active] + t * se[active]
        u = 1 - (0.025 / 36) ** (1 / (len(cw) * N))
        for h, c in list(enumerate(comps)) + [(17, "gadapt_preset")]:
            diff = np.concatenate([A[((ci, c), B)][:, 1] - A[((ci, "gadapt"), B)][:, 1] for ci in cw])
            if np.all(diff == 0): lo[h], hi[h] = -u, u
    names = [f"P({c})-P(G)" for c in comps] + [f"CVaR({c})-CVaR(G)" for c in comps] + ["0.8CVaR(G)-CVaR(preset)", "P(preset)-P(G)"]
    con = {n: dict(estimate=float(p), lower=float(a), upper=float(b)) for n, p, a, b in zip(names, point, lo, hi)}
    # H64c: GAdapt-M not worse than any competitor in feasibility (P(c)-P(G) upper <= 0.05) and better CVaR (CVaR(c)-CVaR(G) lower > 0) vs at least 4 of 8
    notworse = all(con[f"P({c})-P(G)"]["upper"] <= 0.05 for c in comps); better = sum(con[f"CVaR({c})-CVaR(G)"]["lower"] > 0 for c in comps)
    support = notworse and better >= 4
    oppose = sum(con[f"CVaR({c})-CVaR(G)"]["upper"] < 0 for c in comps) >= 4
    H64c = "blocked" if blocked else ("supported" if support and not oppose else ("opposite" if oppose and not support else "undecided"))
    cm = agg(full, "gadapt", B, "CV")
    H64d = "blocked" if blocked else ("supported" if (cm > 0 and con["0.8CVaR(G)-CVaR(preset)"]["lower"] >= 0 and con["P(preset)-P(G)"]["lower"] >= -0.05) else
                                      ("opposite" if (con["0.8CVaR(G)-CVaR(preset)"]["upper"] < 0) else "undecided"))
    desc = {}
    for ci, (net, j) in enumerate(cs):
        for c in CONFIGS:
            for B_ in (3000, B):
                a = A[((ci, c), B_)]
                med = float(np.median(a[:, 2]))
                Gs = [x for x in a[:, 2] if math.isfinite(x)]
                desc[f"{net}|{j}|{c}|{B_}"] = dict(P_feasible=float(a[:, 1].mean()), cvar90=cvar(list(a[:, 0])), median_G=(med if math.isfinite(med) else "inf"),
                                                   median_G_feasible_only=(float(np.median(Gs)) if Gs else None))
    out = dict(blocked=blocked, tstar=t, alpha=0.05, alpha_active=0.025, alpha_fallback=0.025, degenerate_contrasts=[names[i] for i in range(len(names)) if not ((se > 0) & (np.ptp(boots, axis=0) > 0))[i]] if finite else None, bootstrap=R_, contrasts=con, H64c=H64c, H64d=H64d, CVaR_G=float(cm), descriptive=desc)
    save("analysis", out); print(json.dumps({k: out[k] for k in ("blocked", "H64c", "H64d", "contrasts")}, indent=1)[:3500])


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    if st == "run": stage_run(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    elif st == "analyse": stage_analyse()
    else: print(__doc__)
