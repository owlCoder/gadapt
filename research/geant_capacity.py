"""Real network topology/traffic engineering research on SNDlib GÉANT.

Source: https://sndlib.put.poznan.pl/download/sndlib-networks-native/geant.txt
SNDlib metadata: 2005, original observed traffic aggregated/scaled to a peak
demand matrix. 22 nodes, 36 links, 462 directed traffic demands. Module costs
and capacities are reference planning parameters, not measured installed links.

Research optimization model (OUR assumption): one link uses shared bidirectional
capacity; IP-like demand routes along shortest paths induced by 36 integer
link weights. Required modules = ceil(total undirected link load / module_size).
The objective is estimated investment cost (SNDlib module costs). This is an
engineering scenario, not a claimed production-routing implementation.
"""
import argparse
import csv
import hashlib
import math
import random
import re
import statistics
import time
import urllib.request

import networkx as nx
import numpy as np
from gadapt.ga import GA
from scipy.optimize import differential_evolution

SOURCE = "https://sndlib.put.poznan.pl/download/sndlib-networks-native/geant.txt"
EXPECTED_SHA256 = "ff316c23220ff4485deafcb8701d49c353db0c80072152df3ed9023ed4b4f4ff"


def extract_section(text, name):
    match = re.search(r"(?ms)^" + name + r"\s*\(\s*$" +
                      r"(.*?)^\)", text)
    if not match:
        raise ValueError("Invalid SNDlib: missing section " + name)
    return [line.strip() for line in match.group(1).splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


class GeantCapacity:
    def __init__(self, text):
        self.data_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if self.data_sha256 != EXPECTED_SHA256:
            raise ValueError("SNDlib GÉANT source changed; validate before rerunning")
        nodes = extract_section(text, "NODES")
        links = extract_section(text, "LINKS")
        demands = extract_section(text, "DEMANDS")
        self.graph = nx.Graph()
        self.graph.add_nodes_from(line.split()[0] for line in nodes)
        self.edges = []
        for line in links:
            m = re.fullmatch(
                r"\S+\s+\(\s*(\S+)\s+(\S+)\s*\)\s+"
                r"[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+"
                r"\(\s*([\d.]+)\s+([\d.]+)\s*\)", line)
            if m is None:
                raise ValueError("Unexpected SNDlib link format: " + line)
            a, b, capacity, cost = m.groups()
            a_b = tuple(sorted((a, b)))
            self.edges.append((a_b, float(capacity), float(cost)))
            self.graph.add_edge(a, b)
        self.demands = []
        for line in demands:
            m = re.fullmatch(
                r"\S+\s+\(\s*(\S+)\s+(\S+)\s*\)\s+"
                r"[\d.]+\s+([\d.]+)\s+\S+", line)
            if m is None:
                raise ValueError("Unexpected SNDlib demand format: " + line)
            a, b, mbps = m.groups()
            self.demands.append((a, b, float(mbps)))
        if (len(self.graph), len(self.edges), len(self.demands)) != (22, 36, 462):
            raise ValueError("Unexpected GÉANT network dimensions")
        if not nx.is_connected(self.graph):
            raise ValueError("Reference network is disconnected")
        self.index = {edge: index for index, (edge, _, _) in enumerate(self.edges)}
        self.bounds = [(1.0, 25.0)] * len(self.edges)
        self.n = len(self.edges)

    @classmethod
    def download(cls):
        request = urllib.request.Request(
            SOURCE, headers={"User-Agent": "GAdapt-research/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read().decode("utf-8-sig")
        return cls(text)

    def evaluate(self, weights):
        # Convert weights to discrete OSPF-like routing costs, preserving the
        # published network capacity module sizes and costs.
        weighted = self.graph.copy()
        for index, (edge, _, _) in enumerate(self.edges):
            weighted.edges[edge]["weight"] = int(round(float(weights[index])))
        routing = {}
        for source, _, _ in self.demands:
            if source not in routing:
                routing[source] = nx.single_source_dijkstra_path(
                    weighted, source, weight="weight")
        load = [0.0] * len(self.edges)
        for source, target, bandwidth in self.demands:
            path = routing[source][target]
            for a, b in zip(path, path[1:]):
                load[self.index[tuple(sorted((a, b)))]] += bandwidth
        total = 0.0
        max_modules = 0
        modules = []
        for traffic, (_, capacity, module_cost) in zip(load, self.edges):
            required = math.ceil(traffic / capacity - 1e-12)
            total += required * module_cost
            max_modules = max(max_modules, required)
            modules.append(required)
        return dict(cost=total, max_modules=max_modules, modules=modules,
                    max_link_load_mbps=max(load), routed_demands=len(self.demands))


class Recorder:
    def __init__(self, problem, budget):
        self.problem, self.budget = problem, budget
        self.count = 0
        self.best = float("inf")
        self.best_modules = None

    def __call__(self, x):
        if self.count >= self.budget:
            return 1e12
        self.count += 1
        info = self.problem.evaluate(x)
        if info["cost"] < self.best:
            self.best = info["cost"]
            self.best_modules = info["max_modules"]
        return float(info["cost"])


def evaluate_method(problem, method, seed, budget=360, population=36):
    monitor = Recorder(problem, budget)
    started = time.perf_counter()
    if method == "random_search":
        rng = np.random.default_rng(seed)
        for _ in range(budget):
            monitor(rng.integers(1, 26, size=problem.n))
        success = True
    elif method == "scipy_de":
        differential_evolution(
            monitor, problem.bounds, popsize=1,
            maxiter=math.ceil(budget / problem.n),
            integrality=[True]*problem.n, tol=0, atol=0, polish=False,
            rng=np.random.default_rng(seed))
        success = True
    else:
        random.seed(seed)
        np.random.seed(seed)
        extra = (dict(adaptive_immigration_patience=4,
                      adaptive_immigration_percentage=25.0,
                      adaptive_immigration_diversity_threshold=0.25)
                 if method == "affine_restart" else {})
        optimizer = GA(
            cost_function=lambda x: monitor([x[i] for i in range(problem.n)]),
            cost_diversity_metric=("affine_invariant" if method == "affine_restart" else method), population_size=population,
            number_of_generations=math.ceil(3*budget/population)+10,
            exit_check="generations", timeout=240,
            population_mutation="cost_diversity,parent_diversity",
            **extra,
        )
        for low, high in problem.bounds:
            optimizer.add(low, high, 1.0)
        result = optimizer.execute()
        success = bool(result.success)
    return dict(method=method, seed=seed, cost=monitor.best,
                max_modules=monitor.best_modules, evaluations=monitor.count,
                seconds=round(time.perf_counter()-started, 3), success=success)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--budget", type=int, default=360)
    parser.add_argument("--population", type=int, default=36)
    parser.add_argument("--output", default="geant_capacity.csv")
    args = parser.parse_args()
    if args.runs <= 0 or args.budget <= args.population:
        parser.error("Need runs > 0 and budget > population")
    problem = GeantCapacity.download()
    print("DATASET", "nodes=",len(problem.graph), "edges=",len(problem.edges),
          "demands=",len(problem.demands), "sha256=",problem.data_sha256, flush=True)
    raw_costs = [edge[2] for edge in problem.edges]
    minimum, maximum = min(raw_costs), max(raw_costs)
    cost_heuristic = [1 + round(24*(price-minimum)/(maximum-minimum))
                      for price in raw_costs]
    print("REFERENCE", "equal_weights=", problem.evaluate([1]*problem.n),
          "cost_weighted_in_bounds=", problem.evaluate(cost_heuristic),
          flush=True)
    rows = []
    for seed in range(args.runs):
        for method in ("log_relative", "affine_invariant", "affine_restart", "scipy_de", "random_search"):
            row = evaluate_method(problem, method, seed, args.budget, args.population)
            rows.append(row)
            print("RUN", row, flush=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for method in ("log_relative", "affine_invariant", "affine_restart", "scipy_de", "random_search"):
        found = [r["cost"] for r in rows if r["method"] == method]
        print("SUMMARY", method, "median=",statistics.median(found),
              "worst=",max(found), "best=",min(found),
              "n=",len(found), flush=True)
    if any(r["evaluations"] != args.budget for r in rows):
        print("WARNING: not all methods consumed the full evaluation budget", flush=True)


if __name__ == "__main__":
    main()
