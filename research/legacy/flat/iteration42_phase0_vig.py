"""I42 Faza 0: structural VIG pretest for partition crossover (H1).

Previously frozen: research/ITERATION42_PROTOCOL.md (commit 01b3c52). Graph computation
only: no GA, no cost function, no LP/MILP. Inputs: archived topohub v1.5.1 SNDlib JSONs.
"""
import hashlib
import heapq
import json
import os
import platform
import sys
import time

import networkx as nx
import numpy as np
import scipy
from scipy.sparse import csr_matrix

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "data", "topohub_v1.5.1_sndlib")
P_VALUES = (0.05, 0.10, 0.20)
SAMPLES = 1000
BASE_SEED = 42
MIN_GENES = 20
MAX_POPS = 2_000_000
TIME_LIMIT_SECONDS = 30 * 60
DECISION_P = 0.10
MIN_EVALUABLE = 10


class PopLimitExceeded(RuntimeError):
    pass


def two_paths(graph, start, end, max_pops=MAX_POPS):
    """I38 `two_paths` (least hops, lexicographic tie-break, loopless) with a pop cap.

    Returns None when fewer than two distinct loopless paths exist.
    """
    frontier = [(0, (start,))]
    choices = []
    pops = 0
    while frontier and len(choices) < 2:
        hops, path = heapq.heappop(frontier)
        pops += 1
        if pops > max_pops:
            raise PopLimitExceeded(f"{start}->{end}")
        if path[-1] == end:
            choices.append(path)
            continue
        for next_node in sorted(graph[path[-1]]):
            if next_node not in path:
                heapq.heappush(frontier, (hops + 1, path + (next_node,)))
    return tuple(choices) if len(choices) == 2 else None


def load_instance(path):
    with open(path) as handle:
        data = json.load(handle)
    graph = nx.node_link_graph(data, edges="edges")
    demands = [(int(u), int(v)) for u, row in data["graph"]["demands"].items()
               for v, value in row.items() if float(value) > 0]
    return graph, demands


def link_sets(graph, demands, max_pops=MAX_POPS):
    """Per gene: links on which its two paths differ (D_e membership). Fixed demands dropped."""
    edge_ids = {frozenset(e): i for i, e in enumerate(sorted(tuple(sorted(e)) for e in graph.edges))}
    genes, fixed = [], 0
    for a, b in demands:
        paths = two_paths(graph, a, b, max_pops)
        if paths is None:
            fixed += 1
            continue
        used = [{edge_ids[frozenset(h)] for h in zip(p, p[1:])} for p in paths]
        genes.append(tuple(sorted(used[0] ^ used[1])))
    return genes, fixed, len(edge_ids)


def components(gene_links, subset):
    """Connected components of the VIG induced on `subset` (union-find over shared links)."""
    parent = {g: g for g in subset}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    anchor = {}
    for g in subset:
        for e in gene_links[g]:
            if e in anchor:
                ra, rb = find(g), find(anchor[e])
                if ra != rb:
                    parent[ra] = rb
            else:
                anchor[e] = g
    sizes = {}
    for g in subset:
        r = find(g)
        sizes[r] = sizes.get(r, 0) + 1
    return len(sizes), max(sizes.values())


def vig_stats(gene_links, num_links):
    n = len(gene_links)
    rows = [g for g, links in enumerate(gene_links) for _ in links]
    cols = [e for links in gene_links for e in links]
    incidence = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, num_links))
    adjacency = (incidence @ incidence.T).tocsr()
    adjacency.setdiag(0)
    adjacency.eliminate_zeros()
    edges = adjacency.nnz // 2
    sizes = np.asarray(incidence.sum(axis=0)).ravel()
    return dict(vig_edges=int(edges),
                vig_density=float(edges / (n * (n - 1) / 2)) if n > 1 else 0.0,
                max_D_e=int(sizes.max()) if len(sizes) else 0)


def subset_size(p, n):
    return max(2, int(round(p * n)))


def measure(gene_links, instance_index):
    n = len(gene_links)
    out = {}
    for j, p in enumerate(P_VALUES):
        rng = np.random.default_rng(np.random.SeedSequence([BASE_SEED, instance_index, j]))
        size = subset_size(p, n)
        ks, largest = np.empty(SAMPLES, dtype=int), np.empty(SAMPLES)
        for s in range(SAMPLES):
            subset = rng.choice(n, size=size, replace=False).tolist()
            k, big = components(gene_links, subset)
            ks[s], largest[s] = k, big / size
        out[f"{p:.2f}"] = dict(
            subset_size=size, median_k=float(np.median(ks)),
            p10_k=float(np.percentile(ks, 10)), p90_k=float(np.percentile(ks, 90)),
            frac_k_ge_3=float(np.mean(ks >= 3)), mean_largest_fraction=float(largest.mean()))
    return out


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def decide(instances):
    evaluable = [x for x in instances if x["status"] == "evaluable"]
    low = [x["name"] for x in evaluable if x["phases"][f"{DECISION_P:.2f}"]["median_k"] <= 2]
    if len(evaluable) < MIN_EVALUABLE:
        verdict = "INCONCLUSIVE"
    elif 3 * len(low) >= 2 * len(evaluable):
        verdict = "H1_NO_GO"
    else:
        verdict = "PASS"
    return dict(verdict=verdict, evaluable=len(evaluable), median_k_le_2=len(low),
                median_k_le_2_instances=low,
                rule="NO-GO iff median k(p=0.10) <= 2 on >= 2/3 of evaluable instances; "
                     "INCONCLUSIVE if < 10 evaluable")


def run(output):
    start = time.monotonic()
    files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".json"))
    instances = []
    for i, name in enumerate(files):
        path = os.path.join(DATA_DIR, name)
        record = dict(name=name[:-5], index=i, sha256=sha256(path))
        if time.monotonic() - start > TIME_LIMIT_SECONDS:
            record["status"] = "not_evaluated_time_limit"
            instances.append(record)
            continue
        graph, demands = load_instance(path)
        record.update(nodes=graph.number_of_nodes(), links=graph.number_of_edges(),
                      demands=len(demands))
        try:
            gene_links, fixed, num_links = link_sets(graph, demands)
        except PopLimitExceeded as exc:
            record.update(status="not_evaluated_pop_limit", detail=str(exc))
            instances.append(record)
            continue
        record.update(genes=len(gene_links), fixed_demands=fixed, **vig_stats(gene_links, num_links))
        if len(gene_links) < MIN_GENES:
            record["status"] = "not_evaluable_too_few_genes"
        else:
            record["status"] = "evaluable"
            record["phases"] = measure(gene_links, i)
        record["seconds"] = round(time.monotonic() - start, 2)
        instances.append(record)
        print(name, record["status"], record.get("phases", {}).get("0.10", {}).get("median_k"),
              flush=True)
    here = os.path.abspath(__file__)
    result = dict(
        protocol="research/ITERATION42_PROTOCOL.md", protocol_commit="01b3c52",
        source_sha256={os.path.basename(here): sha256(here)},
        data_dir="research/data/topohub_v1.5.1_sndlib",
        environment=dict(python=sys.version.split()[0], platform=platform.platform(),
                         numpy=np.__version__, scipy=scipy.__version__, networkx=nx.__version__),
        parameters=dict(p_values=P_VALUES, samples=SAMPLES, base_seed=BASE_SEED,
                        min_genes=MIN_GENES, max_pops=MAX_POPS, decision_p=DECISION_P),
        instances=instances, decision=decide(instances),
        total_seconds=round(time.monotonic() - start, 2))
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w") as handle:
        json.dump(result, handle, indent=1)
    return result


if __name__ == "__main__":
    res = run(sys.argv[1] if len(sys.argv) > 1 else "research/results/iteration42/phase0.json")
    print(json.dumps(res["decision"], indent=1))
