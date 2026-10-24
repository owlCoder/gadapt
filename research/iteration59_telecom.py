"""I59: modular telecom capacity planning (TopoHub SNDlib, static demands) — FR vs penalty in GAdapt.

Frozen protocol: research/ITERATION59_PROTOCOL.md (frozen before any development measurement). This module holds the
instance model, the deterministic elastic-routing LP evaluator with residual and full-demand checks, and the MILP
reference. Stages are added separately.
"""
import json
import math
import os
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
