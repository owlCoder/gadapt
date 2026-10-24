"""I59: modular telecom capacity planning (TopoHub SNDlib, static demands) — FR vs penalty in GAdapt.

Frozen protocol: research/ITERATION59_PROTOCOL.md (frozen before any development measurement). This module holds the
instance model, the deterministic elastic-routing LP evaluator with residual and full-demand checks, and the MILP
reference. Stages are added separately.
"""
import json
import math
import os
import random
import warnings
from collections import deque

import numpy as np
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "topohub_v1.5.1_sndlib")
INSTANCES = ("abilene", "pdh", "polska", "nobel-germany", "nobel-us", "geant")
DEVELOPMENT, CONFIRMATION = ("abilene", "pdh"), ("polska", "nobel-germany", "nobel-us")
MAX_MODULES = 16
LP_OPTIONS = dict(presolve=True, dual_feasibility_tolerance=1e-8, primal_feasibility_tolerance=1e-8, time_limit=30.0,
                  simplex_dual_edge_weight_strategy="devex", threads=1)
# forwarded verbatim to HiGHS by SciPy 1.18.1 with an "unrecognized ... passed verbatim" warning (Codex 040)
MILP_VERBATIM = ("threads", "mip_abs_gap")
RESIDUAL_TOL, ZERO_V = 1e-7, 1e-8


class Instance:
    """Canonical graph (numeric ids sorted, edges (min, max) sorted), demands each entry once, SP design."""

    def __init__(self, name, raw=None):
        if raw is None:
            with open(os.path.join(DATA, name + ".json")) as f:
                raw = json.load(f)
        self.name = name
        self.nodes = sorted(int(n["id"]) for n in raw["nodes"])
        index = {n: i for i, n in enumerate(self.nodes)}
        edges = sorted((min(int(e["source"]), int(e["target"])), max(int(e["source"]), int(e["target"])),
                        float(e["dist"])) for e in raw["edges"])
        self.edges = [(index[a], index[b], d) for a, b, d in edges]
        self.demands = sorted((index[int(s)], index[int(t)], float(v)) for s, row in raw["graph"]["demands"].items()
                              for t, v in row.items() if float(v) > 0 and int(s) != int(t))
        self.cost = np.array([1.0 + d / 1000.0 for _, _, d in self.edges])
        self.sp_load = self._shortest_path_loads()
        self.q = float(self.sp_load.max()) / 8.0
        self.x_sp = np.ceil(self.sp_load / self.q)
        self.c_sp = float(self.cost @ self.x_sp)
        self._build_lp()

    def _neighbours(self):
        adjacency = {i: [] for i in range(len(self.nodes))}
        for e, (a, b, _) in enumerate(self.edges):
            adjacency[a].append((b, e))
            adjacency[b].append((a, e))
        for i in adjacency:
            adjacency[i].sort()
        return adjacency

    def _shortest_path(self, s, t, adjacency):
        """Minimal hop count, then the lexicographically smallest node sequence (BFS over sorted neighbours keeps
        the lexicographically smallest predecessor chain among shortest paths)."""
        best = {s: (s,)}
        frontier = deque([s])
        while frontier:
            node = frontier.popleft()
            for nxt, _ in adjacency[node]:
                candidate = best[node] + (nxt,)
                if nxt not in best:
                    best[nxt] = candidate
                    frontier.append(nxt)
                elif len(candidate) == len(best[nxt]) and candidate < best[nxt]:
                    best[nxt] = candidate
        path = best[t]
        edge_of = {(a, b): e for a, nbrs in adjacency.items() for b, e in nbrs}
        return [edge_of[(path[i], path[i + 1])] for i in range(len(path) - 1)]

    def _shortest_path_loads(self):
        adjacency = self._neighbours()
        load = np.zeros(len(self.edges))
        for s, t, v in self.demands:
            for e in self._shortest_path(s, t, adjacency):
                load[e] += v
        return load

    def _build_lp(self):
        """Variables: y[k, arc] (arc 2e: a->b, 2e+1: b->a), then u[k]; conservation rows drop the last node."""
        n, m, k = len(self.nodes), len(self.edges), len(self.demands)
        arcs = 2 * m
        self.h = np.array([v for _, _, v in self.demands]) / self.q
        rows, cols, vals = [], [], []
        b_full = np.zeros(k * (n - 1))
        for c, (s, t, _) in enumerate(self.demands):
            base = c * (n - 1)
            for e, (a, b, _) in enumerate(self.edges):
                for arc, (tail, head) in ((2 * e, (a, b)), (2 * e + 1, (b, a))):
                    col = c * arcs + arc
                    if tail < n - 1:
                        rows.append(base + tail); cols.append(col); vals.append(1.0)
                    if head < n - 1:
                        rows.append(base + head); cols.append(col); vals.append(-1.0)
            for node, sign in ((s, 1.0), (t, -1.0)):
                if node < n - 1:
                    rows.append(base + node); cols.append(k * arcs + c); vals.append(sign)  # + u_k(e_s - e_t)
                    b_full[base + node] = sign * self.h[c]
        self.n_y, self.n_u = k * arcs, k
        # full balances at EVERY node (the LP drops one row per demand; checks must not)
        f_rows, f_cols, f_vals = [], [], []
        self.b_all = np.zeros(k * n)
        for c, (s, t, _) in enumerate(self.demands):
            base = c * n
            for e, (a, b, _) in enumerate(self.edges):
                for arc, (tail, head) in ((2 * e, (a, b)), (2 * e + 1, (b, a))):
                    f_rows += [base + tail, base + head]; f_cols += [c * arcs + arc] * 2; f_vals += [1.0, -1.0]
            for node, sign in ((s, 1.0), (t, -1.0)):
                f_rows.append(base + node); f_cols.append(k * arcs + c); f_vals.append(sign)
                self.b_all[base + node] = sign * self.h[c]
        self.A_all = sparse.csr_matrix((f_vals, (f_rows, f_cols)), shape=(k * n, k * arcs + k))
        self.A_eq = sparse.csr_matrix((vals, (rows, cols)), shape=(k * (n - 1), self.n_y + self.n_u))
        self.b_eq = b_full
        cap_rows, cap_cols = [], []
        for c in range(k):
            for e in range(m):
                for arc in (2 * e, 2 * e + 1):
                    cap_rows.append(e); cap_cols.append(c * arcs + arc)
        self.A_cap = sparse.csr_matrix((np.ones(len(cap_rows)), (cap_rows, cap_cols)), shape=(m, self.n_y + self.n_u))
        self.objective = np.concatenate([np.zeros(self.n_y), np.ones(k) / self.h.sum()])
        self.bounds = [(0, None)] * self.n_y + [(0, float(h)) for h in self.h]

    def check_x(self, x):
        x = np.asarray(x, float)
        if x.shape != (len(self.edges),) or not np.all(np.isfinite(x)) or np.any(np.abs(x - np.rint(x)) > 0) \
                or x.min() < 0 or x.max() > MAX_MODULES:
            raise ValueError("module counts must be finite integers in [0, 16], one per edge")
        return x

    def witness_ok(self, y, u, x):
        """Elastic witness: complete node balances, capacities, bounds (all to 1e-7), finite values."""
        z = np.concatenate([y, u])
        if not np.all(np.isfinite(z)):
            return False
        return (np.max(np.abs(self.A_all @ z - self.b_all)) <= RESIDUAL_TOL
                and np.max(self.A_cap @ z - x) <= RESIDUAL_TOL and y.min() >= -RESIDUAL_TOL
                and u.min() >= -RESIDUAL_TOL and np.max(u - self.h) <= RESIDUAL_TOL)

    def meets_full_demands(self, y, x):
        z = np.concatenate([y, np.zeros(self.n_u)])
        return (np.all(np.isfinite(y)) and np.max(np.abs(self.A_all @ z - self.b_all)) <= RESIDUAL_TOL
                and np.max(self.A_cap @ z - x) <= RESIDUAL_TOL and y.min() >= -RESIDUAL_TOL)

    def evaluate(self, x):
        """dict(f, V, C) for module counts x; raises RuntimeError on a solver failure (a failed evaluation)."""
        x = self.check_x(x)
        with warnings.catch_warnings():  # only the expected verbatim-forwarding notice for threads=1
            warnings.filterwarnings("ignore", message=r"Unrecognized options detected: \{'threads': 1\}")
            res = linprog(self.objective, A_ub=self.A_cap, b_ub=x, A_eq=self.A_eq, b_eq=self.b_eq, bounds=self.bounds,
                          method="highs-ds", options=LP_OPTIONS)
        if res.status != 0 or res.x is None:
            raise RuntimeError(f"LP failed: status {res.status} {res.message}")
        y, u = res.x[:self.n_y], res.x[self.n_y:]
        if not self.witness_ok(y, u, x):
            raise RuntimeError("LP witness residual above tolerance")
        V = float(res.fun)
        if V <= ZERO_V and self.meets_full_demands(y, x):
            V = 0.0
        return dict(f=float(self.cost @ x) / self.c_sp, V=V, C=float(self.cost @ x))

    def milp_reference(self, time_limit=3600.0):
        """Integer modules x and continuous flows, no shortage (full demands); returns C*, status, gap."""
        k, m = len(self.demands), len(self.edges)
        A_y = self.A_eq[:, :self.n_y]
        n_rows = A_y.shape[0]
        A_eq = sparse.hstack([A_y, sparse.csr_matrix((n_rows, m))])
        A_cap = sparse.hstack([self.A_cap[:, :self.n_y], -sparse.identity(m)])
        c = np.concatenate([np.zeros(self.n_y), self.cost])
        integrality = np.concatenate([np.zeros(self.n_y), np.ones(m)])
        lb = np.zeros(self.n_y + m)
        ub = np.concatenate([np.full(self.n_y, np.inf), np.full(m, MAX_MODULES)])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            res = milp(c, constraints=[LinearConstraint(A_eq, self.b_eq, self.b_eq),
                                       LinearConstraint(A_cap, -np.inf, 0)],
                       integrality=integrality, bounds=Bounds(lb, ub),
                       options=dict(time_limit=time_limit, mip_rel_gap=0.0, presolve=True, threads=1, mip_abs_gap=0.0))
        messages = [str(w.message) for w in caught]
        unexpected = [m for m in messages if not any(o in m for o in MILP_VERBATIM)]
        out = dict(status=int(res.status), message=str(res.message), fun=None if res.x is None else float(res.fun),
                   gap=getattr(res, "mip_gap", None), dual_bound=getattr(res, "mip_dual_bound", None),
                   warnings=messages, x=None, y=None, C=None, certified=False)
        if res.x is None:
            return out
        y, xr = res.x[:self.n_y], res.x[self.n_y:]
        x = np.rint(xr)
        checks = (np.max(np.abs(xr - x)) <= 1e-6 and x.min() >= 0 and x.max() <= MAX_MODULES
                  and self.meets_full_demands(y, x) and abs(float(self.cost @ x) - float(res.fun)) <= 1e-6 * max(1.0, abs(res.fun)))
        out.update(x=x.tolist(), y=y.tolist(), C=float(self.cost @ x), witness_checks=bool(checks),
                   certified=bool(res.status == 0 and checks and not unexpected))
        return out


# ------------------------------------------------------------------ evaluation wrapper and GAdapt runs

EPSILONS = (0.05, 0.10, 0.20)
BUDGETS = (3000, 10000, 30000)
SELECTION_PAIRS, VALIDATION_PAIRS, CONFIRMATION_PAIRS = 10, 10, 15
POPULATION_SIZE = 32
OUT = os.path.join(HERE, "results", "iteration59")


def seed_of(p, name, s):
    return 59000000 + 100000 * p + 1000 * INSTANCES.index(name) + s


class Evaluator:
    """Counts every LP call (no cache, no early stop); records the first feasible call reaching each target level
    C <= (1 + eps) C*, its genotype, the best feasible design and the initial population."""

    def __init__(self, instance, budget, c_star):
        self.instance, self.budget, self.c_star = instance, budget, c_star
        self.calls = self.errors = 0
        self.hits = {eps: None for eps in EPSILONS}
        self.hit_x = {eps: None for eps in EPSILONS}
        self.best_C, self.best_x = math.inf, None
        self.initial = []

    @property
    def done(self):
        return self.calls >= self.budget

    def __call__(self, values):
        try:
            return self._call(values)
        except Exception:
            self.errors += 1
            raise

    def _call(self, values):
        self.calls += 1
        x = np.rint(np.asarray(values, float))
        out = self.instance.evaluate(x)
        if len(self.initial) < POPULATION_SIZE:
            self.initial.append(x.tolist())
        if out["V"] == 0.0:
            if out["C"] < self.best_C:
                self.best_C, self.best_x = out["C"], x.tolist()
            if self.c_star is not None:
                for eps in EPSILONS:
                    if self.hits[eps] is None and out["C"] <= (1 + eps) * self.c_star + 1e-9:
                        self.hits[eps], self.hit_x[eps] = self.calls, x.tolist()
        return out


def gadapt_run(task, c_star):
    from gadapt.ga import GA
    instance = Instance(task["instance"])
    evaluator = Evaluator(instance, task["budget"], c_star)
    random.seed(task["seed"])
    np.random.seed(task["seed"])
    if task["arm"] == "G0":
        def cost(values):
            if evaluator.done:
                return 1e300
            out = evaluator(values)
            return out["f"] + 1000.0 * out["V"]
        kwargs = {}
    else:
        def cost(values):
            if evaluator.done:
                return 0.0, 1e150
            out = evaluator(values)
            return out["f"], out["V"]
        kwargs = dict(constraint_handling="feasibility_rules")
    ga = GA(cost_function=cost, probe_cost_function=False, exit_check="generations", number_of_generations=10 ** 9,
            exit_function=lambda *a, **k: evaluator.done, timeout=10 ** 6, **kwargs)
    for _ in instance.edges:
        ga.add(0.0, float(MAX_MODULES), 1.0)
    result = ga.execute()
    returned = [result.result_values[i] for i in sorted(result.result_values)] if result.result_values else None
    return dict(task=task, ok=evaluator.calls == task["budget"] and bool(result.success) and evaluator.errors == 0,
                calls=evaluator.calls, errors=evaluator.errors, hits={str(e): h for e, h in evaluator.hits.items()},
                hit_x={str(e): v for e, v in evaluator.hit_x.items()}, best_C=None if evaluator.best_x is None
                else evaluator.best_C, best_x=evaluator.best_x, returned=returned, initial=evaluator.initial)


def run(task):
    import traceback
    try:
        return gadapt_run(task, task.get("c_star"))
    except Exception:
        return dict(task=task, ok=False, error=traceback.format_exc()[-2000:])


def save(name, data):
    import gzip
    os.makedirs(OUT, exist_ok=True)
    with gzip.open(os.path.join(OUT, name + ".gz"), "wt") as f:
        json.dump(data, f)


def load(name):
    import gzip
    with gzip.open(os.path.join(OUT, name + ".gz"), "rt") as f:
        return json.load(f)


def pool_run(tasks, workers):
    from multiprocessing import Pool
    with Pool(workers, maxtasksperchild=1) as pool:
        records = list(pool.imap(run, tasks))
    for i, r in enumerate(records):
        if not r["ok"]:
            with Pool(1, maxtasksperchild=1) as pool:
                again = pool.apply(run, (tasks[i],))
            again["rerun"], again["first_attempt"] = True, {k: v for k, v in r.items() if k != "initial"}
            records[i] = again
    pairs = {}
    for r in records:
        if r.get("ok"):
            pairs.setdefault((r["task"]["instance"], r["task"]["seed"]), {})[r["task"]["arm"]] = r["initial"]
    for key, p in pairs.items():
        if len(p) == 2 and (p["G0"] != p["G1"] or len(p["G0"]) != POPULATION_SIZE):
            raise SystemExit(f"STOP: G0/G1 initial populations differ for {key}")
    return records


def references(names, time_limit=3600.0):
    out = {}
    for name in names:
        ref = Instance(name).milp_reference(time_limit=time_limit)
        out[name] = ref
    return out


def attainment(records, name, budget, eps):
    rs = [r for r in records if r["task"]["instance"] == name and r["ok"]]
    return sum(1 for r in rs if r["hits"][str(eps)] is not None and r["hits"][str(eps)] <= budget) / len(rs)


def choose(records):
    """Smallest B, then smallest eps, with pooled G0/G1 attainment in [0.2, 0.8] on EVERY development network."""
    for budget in BUDGETS:
        for eps in EPSILONS:
            if all(0.2 <= attainment(records, n, budget, eps) <= 0.8 for n in DEVELOPMENT):
                return budget, eps
    return None


def stage_development(workers):
    refs = references(DEVELOPMENT)
    if not all(refs[n]["certified"] for n in DEVELOPMENT):
        save("development.json", dict(references=refs, decision="NO-GO: development optimum not certified"))
        return
    tasks = [dict(instance=n, arm=a, seed=seed_of(0, n, s), budget=BUDGETS[-1], c_star=refs[n]["C"])
             for n in DEVELOPMENT for s in range(1, SELECTION_PAIRS + 1) for a in ("G0", "G1")]
    selection = pool_run(tasks, workers)
    chosen = choose(selection)
    validation, decision = None, None
    if chosen is None:
        decision = "NO-GO: no (B, eps) with 20-80% attainment on every development network"
    else:
        budget, eps = chosen
        tasks = [dict(instance=n, arm=a, seed=seed_of(1, n, s), budget=budget, c_star=refs[n]["C"])
                 for n in DEVELOPMENT for s in range(1, VALIDATION_PAIRS + 1) for a in ("G0", "G1")]
        validation = pool_run(tasks, workers)
        ok = all(0.2 <= attainment(validation, n, budget, eps) <= 0.8 for n in DEVELOPMENT)
        decision = "GO" if ok else "NO-GO: validation seeds outside 20-80%"
    save("development.json", dict(references=refs, chosen=chosen, decision=decision, selection=selection,
                                  validation=validation))


def stage_confirmation(workers):
    dev = load("development.json")
    if dev["decision"] != "GO":
        raise SystemExit(f"development decision: {dev['decision']}")
    budget, eps = dev["chosen"]
    refs = references(CONFIRMATION)
    trivial = {n: refs[n]["C"] is not None and not ((1 + eps) * refs[n]["C"] < Instance(n).c_sp) for n in CONFIRMATION}
    save("confirmation_refs.json", dict(references=refs, trivial=trivial, chosen=[budget, eps]))
    tasks = [dict(instance=n, arm=a, seed=seed_of(2, n, s), budget=budget, c_star=refs[n]["C"])
             for n in CONFIRMATION for s in range(1, CONFIRMATION_PAIRS + 1) for a in ("G0", "G1")]
    save("confirmation.json", dict(references=refs, trivial=trivial, chosen=[budget, eps],
                                   records=pool_run(tasks, workers)))


def analyse():
    data = load("confirmation.json")
    budget, eps = data["chosen"]
    certified = all(data["references"][n]["certified"] for n in CONFIRMATION)
    units = {}
    for r in data["records"]:
        units.setdefault((r["task"]["instance"], r["task"]["seed"]), {})[r["task"]["arm"]] = r
    def T(r):
        h = r["hits"][str(eps)]
        return min(h / budget, 1.0) if h is not None else 1.0
    complete = {k: u for k, u in units.items() if len(u) == 2 and all(r["ok"] for r in u.values())}
    persistent = [list(k) for k, u in units.items() if k not in complete]
    cells = {}
    for (n, seed), u in complete.items():
        cells.setdefault(n, []).append(T(u["G1"]) - T(u["G0"]))
    result = None
    if certified and not persistent and set(cells) == set(CONFIRMATION):
        rng = np.random.RandomState(59)
        values = {n: np.array(v) for n, v in cells.items()}
        draws = np.mean([v[rng.randint(0, len(v), (20000, len(v)))].mean(axis=1) for n, v in sorted(values.items())],
                        axis=0)
        estimate = float(np.mean([v.mean() for v in values.values()]))
        lo, hi = np.percentile(draws, [2.5, 97.5])
        result = dict(estimate=estimate, ci=[float(lo), float(hi)], supported=bool(hi < 0))
    out = dict(chosen=[budget, eps], certified=certified, trivial=data["trivial"], persistent_failures=persistent,
               H59=result, per_network={n: dict(mean_d=float(np.mean(v)), n=len(v)) for n, v in cells.items()})
    save("analysis.json", out)
    print(json.dumps(dict(H59=result, certified=certified, trivial=data["trivial"]), indent=1))


# ------------------------------------------------------------------ independent checker (no Instance code)

def independent_check(name, x):
    """Rebuilds the network from the raw JSON with networkx incidence matrices and checks a design: integer modules in
    [0, 16], cost, and whether the FULL demands can be routed (min total shortage LP = 0)."""
    import networkx as nx
    with open(os.path.join(DATA, name + ".json")) as f:
        raw = json.load(f)
    graph = nx.Graph()
    for e in raw["edges"]:
        graph.add_edge(int(e["source"]), int(e["target"]), dist=float(e["dist"]))
    edges = sorted(tuple(sorted(e)) for e in graph.edges())
    x = np.asarray(x, float)
    if x.shape != (len(edges),) or np.any(np.abs(x - np.rint(x)) > 0) or x.min() < 0 or x.max() > MAX_MODULES:
        return dict(valid=False)
    demands = [(int(s), int(t), float(v)) for s, row in raw["graph"]["demands"].items() for t, v in row.items()
               if float(v) > 0 and int(s) != int(t)]
    digraph = nx.DiGraph()
    for a, b in edges:
        digraph.add_edge(a, b)
        digraph.add_edge(b, a)
    nodes = sorted(digraph.nodes())
    arcs = list(digraph.edges())
    incidence = nx.incidence_matrix(digraph, nodelist=nodes, edgelist=arcs, oriented=True).toarray()  # -1 tail, +1 head
    load = {}
    for s, t, v in demands:
        path = min(nx.all_shortest_paths(graph, s, t))  # protocol rule: min hops, then lexicographically smallest
        for a, b in zip(path, path[1:]):
            load[tuple(sorted((a, b)))] = load.get(tuple(sorted((a, b))), 0.0) + v
    q = max(load.values()) / 8.0
    cost = sum((1 + graph.edges[a, b]["dist"] / 1000.0) * xe for (a, b), xe in zip(edges, x))
    k, n_arcs = len(demands), len(arcs)
    # variables: flows per demand and arc, then shortage per demand; minimize total shortage
    a_eq = np.zeros((k * len(nodes), k * n_arcs + k))
    b_eq = np.zeros(k * len(nodes))
    for c, (s, t, v) in enumerate(demands):
        a_eq[c * len(nodes):(c + 1) * len(nodes), c * n_arcs:(c + 1) * n_arcs] = -incidence  # out - in
        a_eq[c * len(nodes) + nodes.index(s), k * n_arcs + c] = 1.0
        a_eq[c * len(nodes) + nodes.index(t), k * n_arcs + c] = -1.0
        b_eq[c * len(nodes) + nodes.index(s)] = v / q
        b_eq[c * len(nodes) + nodes.index(t)] = -v / q
    a_ub = np.zeros((len(edges), k * n_arcs + k))
    for i, (a, b) in enumerate(arcs):
        e = edges.index(tuple(sorted((a, b))))
        for c in range(k):
            a_ub[e, c * n_arcs + i] = 1.0
    demand_h = np.array([v / q for _, _, v in demands])
    res = linprog(np.concatenate([np.zeros(k * n_arcs), np.ones(k)]), A_ub=a_ub, b_ub=x, A_eq=a_eq, b_eq=b_eq,
                  bounds=[(0, None)] * (k * n_arcs) + [(0, h) for h in demand_h], method="highs")
    shortage = float(res.fun) / demand_h.sum() if res.status == 0 else None
    return dict(valid=True, cost=float(cost), shortage=shortage, routable=shortage is not None and shortage <= ZERO_V)


def stage_check():
    """Independent re-check of returned designs and of every target witness (confirmation records)."""
    data = load("confirmation.json")
    eps = data["chosen"][1]
    rows, failures = [], 0
    for r in data["records"]:
        for kind, x in (("returned", r.get("returned")), ("target", (r.get("hit_x") or {}).get(str(eps))),
                        ("best", r.get("best_x"))):
            if x is None:
                continue
            c = independent_check(r["task"]["instance"], x)
            ok = c["valid"] and (kind == "returned" or c["routable"])
            if kind == "target" and ok:
                ok = c["cost"] <= (1 + eps) * data["references"][r["task"]["instance"]]["C"] + 1e-9
            rows.append(dict(task=r["task"], kind=kind, ok=bool(ok), check=c))
            failures += not ok
    for name, ref in data["references"].items():
        if ref.get("x") is not None:
            c = independent_check(name, ref["x"])
            rows.append(dict(task=dict(instance=name), kind="reference", ok=bool(c["valid"] and c["routable"]
                                                                               and abs(c["cost"] - ref["C"]) < 1e-6), check=c))
            failures += not rows[-1]["ok"]
    save("check.json", dict(rows=rows, failures=failures))
    print("checked", len(rows), "failures", failures)


if __name__ == "__main__":
    import sys
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    dict(development=lambda: stage_development(workers), confirmation=lambda: stage_confirmation(workers),
         analyse=analyse, check=stage_check).get(stage, lambda: print(__doc__))()
