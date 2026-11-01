"""I38 source SNDlib temporal joint-capacity model + exact restricted MILP.

Previously frozen: research/ITERATION38_PROTOCOL.md. NOT the original SNDlib
comprehensive routing model: single fixed path per directed demand pair,
TWO lexicographically tie-broken least-hop candidate paths, one installed
capacity option on an undirected shared-capacity edge for ALL time matrices.
"""
import hashlib
import heapq
import io
import math
import re
import tarfile
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, vstack

SOURCE_NETWORK_URL = (
    "https://sndlib.put.poznan.pl/download/sndlib-networks-native/nobel-germany.txt")
SOURCE_OVERVIEW_URL = "https://sndlib.put.poznan.pl/nobel-germany.overview.action"
EXPECTED_NODES, EXPECTED_LINKS, EXPECTED_MATRICES = 17, 26, 288


@dataclass(frozen=True)
class SourceLink:
    name: str
    u: str
    v: str
    base: float
    base_cost: float
    routing_cost: float
    setup_cost: float
    options: tuple


class _Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.anchors.append((self.href, " ".join(self.text).lower()))
            self.href = None


def _get(url, max_bytes=4_000_000):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "sndlib.put.poznan.pl":
        raise ValueError("Only official SNDlib HTTPS sources are permitted")
    with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "GAdapt-I38-source-audit/1.0"}),
            timeout=40) as r:
        data = r.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("SNDlib source exceeded declared safety limit")
    return data


def official_source():
    data = _get(SOURCE_NETWORK_URL)
    return data.decode("utf-8-sig"), dict(
        url=SOURCE_NETWORK_URL, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def official_matrices():
    h = _Anchors()
    h.feed(_get(SOURCE_OVERVIEW_URL).decode("utf-8", errors="replace"))
    matches = [(u, title) for u, title in h.anchors if
               "native" in title and "tgz" in title and "585" in title]
    if len(matches) != 1:
        raise ValueError("Could not uniquely identify official 288-matrix native archive")
    u = urllib.parse.urljoin(SOURCE_OVERVIEW_URL, matches[0][0])
    if not u.endswith(".tgz") and not u.endswith(".tar.gz"):
        raise ValueError("Unexpected official archive extension")
    data = _get(u, max_bytes=4_000_000)
    out = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as ar:
        files = [m for m in ar.getmembers() if m.isfile()]
        if len(files) > 350:
            raise ValueError("Unexpectedly many archive members")
        for member in files:
            if member.size > 2_000_000 or member.size < 0:
                raise ValueError("Oversized temporal matrix")
            raw = ar.extractfile(member).read()
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError as e:
                raise ValueError("Non-text matrix in source archive") from e
            if re.search(r"(?m)^\s*DEMANDS\s*\(", text):
                out.append((member.name, text))
    # Natural sort handles both timestamp names and numeric frame indices.
    def natural(item):
        return [int(x) if x.isdigit() else x.lower()
                for x in re.findall(r"\d+|\D+", item[0])]
    out.sort(key=natural)
    if len(out) != EXPECTED_MATRICES or len({name for name, _ in out}) != len(out):
        raise ValueError("Official native archive MUST contain exactly 288 unique matrices")
    return out, dict(url=u, sha256=hashlib.sha256(data).hexdigest(),
                     bytes=len(data), first_name=out[0][0],
                     last_name=out[-1][0], matrix_count=len(out))


def _section(text, name):
    m = re.search(r"(?ms)^\s*" + name +
                  r"\s*\(\s*\n(.*?)^\s*\)\s*$", text)
    if m is None:
        raise ValueError("Missing SNDlib section: " + name)
    return [line.split("#", 1)[0].strip() for line in m.group(1).splitlines()
            if line.split("#", 1)[0].strip()]


def parse_nodes(text):
    names = []
    for line in _section(text, "NODES"):
        m = re.match(r"^(\S+)\s+\(", line)
        if m is None:
            raise ValueError("Invalid node line")
        names.append(m.group(1))
    if len(set(names)) != len(names):
        raise ValueError("Duplicate SNDlib nodes")
    return tuple(names)


def parse_network(text):
    nodes = parse_nodes(text)
    links = []
    pattern = re.compile(
        r"^(\S+)\s+\(\s*(\S+)\s+(\S+)\s*\)\s+"
        r"(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\(\s*([^)]*)\)")
    for line in _section(text, "LINKS"):
        m = pattern.match(line)
        if not m:
            raise ValueError("Malformed source SNDlib link row")
        name, u, v, *other = m.groups()
        if u == v or u not in nodes or v not in nodes:
            raise ValueError("Invalid source link endpoints")
        scalars = [float(x) for x in other[:4]]
        rawopts = [float(x) for x in other[4].split()]
        if len(rawopts) % 2 or not rawopts:
            raise ValueError("Source link module options absent or malformed")
        options = tuple(zip(rawopts[::2], rawopts[1::2]))
        if any(not math.isfinite(q) or q < 0 for q in scalars + rawopts):
            raise ValueError("Nonfinite or negative source link input")
        if any(cap <= 0 for cap, _ in options):
            raise ValueError("Nonpositive module capacity unsupported")
        links.append(SourceLink(name, u, v, *scalars, options))
    if len(set(x.name for x in links)) != len(links):
        raise ValueError("Duplicate source link name")
    if len({frozenset((x.u, x.v)) for x in links}) != len(links):
        raise ValueError("Parallel edges require a different explicit formulation")
    return nodes, tuple(links)


def parse_demands(text, nodes):
    rows = {}
    pattern = re.compile(
        r"^\S+\s+\(\s*(\S+)\s+(\S+)\s*\)\s+"
        r"(\S+)\s+(\S+)\s+(\S+)")
    for line in _section(text, "DEMANDS"):
        m = pattern.match(line)
        if not m:
            raise ValueError("Malformed source demand")
        u, v, unit, amount, _ = m.groups()
        if u not in nodes or v not in nodes or u == v:
            raise ValueError("Invalid demand endpoints")
        q = float(unit) * float(amount)
        if not math.isfinite(q) or q < 0:
            raise ValueError("Negative/nonfinite source traffic")
        key = (u, v)
        rows[key] = rows.get(key, 0.0) + q
    return rows


def temporal_array(files, nodes):
    data = []
    for name, raw in files:
        if parse_nodes(raw) != nodes:
            raise ValueError("Temporal matrix has different source node order")
        data.append(parse_demands(raw, nodes))
    pairs = tuple(sorted(set().union(*(set(d) for d in data))))
    if not pairs or len(data) != EXPECTED_MATRICES:
        raise ValueError("Missing temporal demand pairs or matrix")
    q = np.zeros((len(data), len(pairs)), dtype=float)
    indices = {p: i for i, p in enumerate(pairs)}
    for t, row in enumerate(data):
        for pair, amount in row.items():
            q[t, indices[pair]] = amount
    if not np.all(np.isfinite(q)) or np.any(q < 0):
        raise ValueError("Nonfinite temporal load")
    return pairs, q


def two_paths(graph, start, end):
    frontier = [(0, (start,))]
    choices = []
    while frontier and len(choices) < 2:
        hops, path = heapq.heappop(frontier)
        if path[-1] == end:
            choices.append(path)
            continue
        for next_node in sorted(graph[path[-1]]):
            if next_node not in path:
                heapq.heappush(frontier, (hops + 1, path + (next_node,)))
    if len(choices) != 2:
        raise ValueError("Each demand must have two distinct loopless source paths")
    return tuple(choices)


class JointCapacityProblem:
    def __init__(self, nodes, links, pairs, traffic):
        self.nodes, self.links, self.pairs = tuple(nodes), tuple(links), tuple(pairs)
        self.q = np.asarray(traffic, dtype=float)
        if (self.q.ndim != 2 or self.q.shape[1] != len(self.pairs)
                or not len(self.q) or np.any(self.q < 0)
                or not np.all(np.isfinite(self.q))):
            raise ValueError("Invalid nonnegative temporal matrix")
        graph = nx.Graph()
        graph.add_nodes_from(self.nodes)
        edge_ids = {}
        for i, link in enumerate(self.links):
            graph.add_edge(link.u, link.v)
            edge_ids[frozenset((link.u, link.v))] = i
        if not nx.is_connected(graph):
            raise ValueError("Disconnected source topology")
        n, e = len(self.pairs), len(self.links)
        self.paths = tuple(two_paths(graph, a, b) for a, b in self.pairs)
        self.incidence = np.zeros((2, n, e), dtype=float)
        for d in range(n):
            for which in (0, 1):
                path = self.paths[d][which]
                for a, b in zip(path, path[1:]):
                    self.incidence[which, d, edge_ids[frozenset((a, b))]] = 1.0
        self.delta = self.incidence[1] - self.incidence[0]
        self.base = self.q @ self.incidence[0]
        self.route_cost = np.array([x.routing_cost for x in self.links])
        self.base_cap = np.array([x.base for x in self.links])

    @property
    def n(self):
        return len(self.pairs)

    def evaluate(self, choices):
        z = np.asarray(choices, dtype=float)
        if z.shape != (self.n,) or not np.all(np.isfinite(z)):
            raise ValueError("Invalid route choice length or nonfinite entry")
        if not np.all((abs(z) < 1e-7) | (abs(z - 1.0) < 1e-7)):
            raise ValueError("Every route decision must be binary")
        z = np.rint(z).astype(int)
        loads = self.base + self.q @ (self.delta * z[:, None])
        peaks = np.max(loads, axis=0)
        capacity = np.array(self.base_cap)
        options_chosen = []
        cost = sum(x.base_cost + (x.setup_cost if x.base > 0 else 0)
                   for x in self.links)
        feasible = True
        for i, link in enumerate(self.links):
            need = peaks[i] - link.base
            if need <= 1e-8:
                options_chosen.append(None)
                continue
            available = [(price, cap, k) for k, (cap, price)
                         in enumerate(link.options) if cap + 1e-8 >= need]
            if not available:
                feasible = False
                options_chosen.append(None)
                continue
            price, cap, k = min(available)
            options_chosen.append(k)
            capacity[i] += cap
            cost += price + (link.setup_cost if link.base == 0 else 0)
        routing = float(np.mean(loads, axis=0) @ self.route_cost)
        if feasible:
            cost += routing
        return dict(feasible=feasible, cost=float(cost) if feasible else None,
                    max_required_capacity=[float(v) for v in peaks],
                    installed_capacity=[float(v) for v in capacity],
                    selected_options=options_chosen,
                    worst_excess=float(np.max(np.maximum(0., peaks - capacity))),
                    bad_time_slices=int(np.sum(np.any(loads > capacity[None, :] + 1e-7,
                                                  axis=1))))

    def validate_plan(self, choices, installed_capacity, matrix):
        q = np.asarray(matrix, dtype=float)
        if q.ndim != 2 or q.shape[1] != self.n:
            raise ValueError("Holdout demand columns mismatch")
        z = np.rint(np.asarray(choices, dtype=float)).astype(int)
        if (z.shape != (self.n,) or np.any((z != 0) & (z != 1))):
            raise ValueError("Holdout route has invalid binary choice")
        loads = q @ (self.incidence[0] + self.delta * z[:, None])
        cap = np.asarray(installed_capacity, dtype=float)
        excess = np.maximum(0., loads - cap[None, :])
        return dict(slices=len(q),
                    violating_slices=int(np.sum(np.any(excess > 1e-7, axis=1))),
                    max_source_unit_excess=float(np.max(excess)),
                    all_snapshots_feasible=bool(np.max(excess) <= 1e-7))


def solve_milp(problem, time_limit=180.0):
    """Exact finite MILP; returns incumbent AND dual bound; never claims a false optimum."""
    if not isinstance(problem, JointCapacityProblem):
        raise TypeError("Need frozen restricted JointCapacityProblem")
    n, e, t = problem.n, len(problem.links), len(problem.q)
    opt = [(i, k, cap, price) for i, link in enumerate(problem.links)
           for k, (cap, price) in enumerate(link.options)]
    m = len(opt)
    obj = np.zeros(n + m)
    c0 = (problem.q.mean(axis=0) @ problem.incidence[0]) @ problem.route_cost
    obj[:n] = (problem.q.mean(axis=0)[:, None] * problem.delta) @ problem.route_cost
    const = float(c0 + sum(x.base_cost + (x.setup_cost if x.base > 0 else 0)
                           for x in problem.links))
    for k, (i, _, cap, price) in enumerate(opt):
        obj[n + k] = price + (problem.links[i].setup_cost
                             if problem.links[i].base == 0 else 0)
    # Link-time rows and a separate <=1 option-choice row per link.
    rr, cc, vv = [], [], []
    upper = np.empty(e * t + e)
    for i in range(e):
        active = np.flatnonzero(problem.delta[:, i])
        edge_opts = [(k, cap) for k, (ix, _, cap, _) in enumerate(opt) if ix == i]
        for ti in range(t):
            row = i * t + ti
            upper[row] = problem.base_cap[i] - problem.base[ti, i]
            for d in active:
                coefficient = problem.q[ti, d] * problem.delta[d, i]
                if coefficient:
                    rr.append(row); cc.append(int(d)); vv.append(float(coefficient))
            for k, cap in edge_opts:
                rr.append(row); cc.append(n + k); vv.append(-float(cap))
        row = e * t + i
        upper[row] = 1.
        for k, _ in edge_opts:
            rr.append(row); cc.append(n + k); vv.append(1.)
    mat = coo_matrix((vv, (rr, cc)), shape=(e*t+e, n+m)).tocsr()
    solution = milp(
        c=obj, integrality=np.ones(n+m),
        bounds=Bounds(np.zeros(n+m), np.ones(n+m)),
        constraints=LinearConstraint(mat, -np.inf, upper),
        options=dict(time_limit=float(time_limit), mip_rel_gap=.01, presolve=True))
    result = dict(status=int(solution.status),
                  message=str(solution.message),
                  mip_gap=(float(solution.mip_gap)
                           if getattr(solution, "mip_gap", None) is not None else None),
                  dual_bound=(float(solution.mip_dual_bound) + const
                              if getattr(solution, "mip_dual_bound", None) is not None
                              else None),
                  solver_objective=(float(solution.fun) + const
                                    if solution.fun is not None else None),
                  incumbent=None, binary_variables=n+m,
                  constraints=e*t+e)
    if solution.x is not None:
        z = [int(round(x)) for x in solution.x[:n]]
        val = problem.evaluate(z)
        if not val["feasible"]:
            raise RuntimeError("MILP incumbent did not pass independent source model validation")
        if (result["solver_objective"] is not None and
                val["cost"] > result["solver_objective"] + 1e-4):
            raise RuntimeError("Independent module selection more expensive than solver incumbent")
        result["incumbent"] = dict(choices=z, **val)
    if result["dual_bound"] is not None and result["incumbent"] is not None:
        if result["dual_bound"] > result["incumbent"]["cost"] + 1e-4:
            raise RuntimeError("MILP lower bound exceeds independently validated incumbent")
    return result
