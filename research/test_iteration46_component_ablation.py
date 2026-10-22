"""Synthetic checks for I46 (ITERATION46_PROTOCOL.md §5). No topohub data is used."""
import random
import subprocess
import unittest

import networkx as nx
import numpy as np

from gadapt.ga_model.ga_options import GAOptions
from research.iteration43_budget_operator_diagnostic import RouteChoiceCost
from research.iteration44_mutation_mechanism import ValidatorFree
from research.iteration46_component_ablation import ARMS, make_ga


def synthetic_cost():
    graph = nx.random_regular_graph(4, 16, seed=5)
    for e in graph.edges:
        graph.edges[e]["dist"] = 1.0 + e[0]
    rng = np.random.default_rng(2)
    demands = [(a, b, float(rng.integers(1, 9))) for a in graph for b in graph
               if a != b and rng.random() < 0.3]
    return RouteChoiceCost(graph, demands)


class Iteration46Test(unittest.TestCase):
    def test_every_arm_runs_with_validator_exclusion(self):
        f = synthetic_cost()
        for arm in ARMS:
            random.seed(1)
            np.random.seed(1)
            cost = ValidatorFree(f, f.n)
            cost.budget = 400
            result = make_ga(cost, f.n, arm).execute()
            self.assertTrue(result.success, (arm, result.messages))
            self.assertEqual((cost.skipped, cost.calls), (2, 400), arm)

    def test_elitism_keep_numbers(self):
        f = synthetic_cost()
        cost = ValidatorFree(f, f.n)
        self.assertEqual(GAOptions(make_ga(cost, f.n, "A0")).keep_number, 12)
        self.assertEqual(GAOptions(make_ga(cost, f.n, "A3")).keep_number, 1)

    def test_gadapt_library_untouched(self):
        diff = subprocess.run(["git", "diff", "--stat", "HEAD", "--", "gadapt/"],
                              capture_output=True, text=True, check=True).stdout
        self.assertEqual(diff.strip(), "")


if __name__ == "__main__":
    unittest.main()
