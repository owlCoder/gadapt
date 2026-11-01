"""Synthetic checks for I42 Faza 0 (ITERATION42_PROTOCOL.md §6). No topohub data is used."""
import itertools
import unittest

import networkx as nx
from hypothesis import given, settings, strategies as st

from research.iteration38_joint_capacity_model import two_paths as i38_two_paths
from research.iteration42_phase0_vig import (
    PopLimitExceeded, components, decide, link_sets, subset_size, two_paths)


def _adjacency(graph):
    return {u: set(graph[u]) for u in graph}


class Phase0VigTest(unittest.TestCase):
    def test_disjoint_link_sets_give_one_component_per_gene(self):
        genes = [(0,), (1,), (2,), (3,)]
        self.assertEqual(components(genes, [0, 1, 2, 3]), (4, 1))

    def test_shared_link_gives_one_component(self):
        genes = [(0, 5), (1, 5), (2, 5)]
        self.assertEqual(components(genes, [0, 1, 2]), (1, 3))

    def test_common_genes_are_removed_before_components(self):
        # 0-1 and 1-2 interact; without gene 1 the pair 0,2 is separate.
        genes = [(0,), (0, 1), (1,)]
        self.assertEqual(components(genes, [0, 2])[0], 2)

    def test_two_paths_matches_i38_on_cycle_and_grid(self):
        for graph in (nx.cycle_graph(6), nx.grid_2d_graph(3, 3), nx.petersen_graph()):
            adj = _adjacency(graph)
            for a, b in itertools.permutations(sorted(graph.nodes), 2):
                self.assertEqual(two_paths(graph, a, b), i38_two_paths(adj, a, b))

    def test_bridge_demand_is_fixed(self):
        graph = nx.path_graph(3)
        genes, fixed, links = link_sets(graph, [(0, 2), (2, 0)])
        self.assertEqual((genes, fixed, links), ([], 2, 2))

    def test_pop_limit(self):
        with self.assertRaises(PopLimitExceeded):
            two_paths(nx.complete_graph(8), 0, 7, max_pops=3)

    def test_subset_size_and_decision_rule(self):
        self.assertEqual(subset_size(0.05, 20), 2)
        self.assertEqual(subset_size(0.10, 272), 27)
        inst = [dict(name=str(i), status="evaluable", phases={"0.10": {"median_k": k}})
                for i, k in enumerate([1] * 8 + [5] * 4)]
        self.assertEqual(decide(inst)["verdict"], "H1_NO_GO")
        inst[0]["phases"]["0.10"]["median_k"] = 3
        self.assertEqual(decide(inst)["verdict"], "PASS")
        self.assertEqual(decide(inst[:9])["verdict"], "INCONCLUSIVE")

    @settings(max_examples=300, deadline=None)
    @given(st.integers(2, 9), st.integers(0, 2**31 - 1), st.data())
    def test_components_equal_networkx_on_random_instances(self, n, seed, data):
        graph = nx.gnm_random_graph(n, min(n * (n - 1) // 2, n + 3), seed=seed)
        if not nx.is_connected(graph):
            return
        demands = [(a, b) for a in graph for b in graph if a != b]
        genes, _, _ = link_sets(graph, demands)
        if len(genes) < 2:
            return
        subset = data.draw(st.lists(st.integers(0, len(genes) - 1), min_size=2,
                                    max_size=len(genes), unique=True))
        vig = nx.Graph()
        vig.add_nodes_from(subset)
        for g, h in itertools.combinations(subset, 2):
            if set(genes[g]) & set(genes[h]):
                vig.add_edge(g, h)
        expected = nx.number_connected_components(vig)
        largest = max(len(c) for c in nx.connected_components(vig))
        self.assertEqual(components(genes, subset), (expected, largest))


if __name__ == "__main__":
    unittest.main()
