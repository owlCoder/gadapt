"""Synthetic checks for I44 (ITERATION44_PROTOCOL.md §5). No topohub data is used."""
import random
import subprocess
import unittest

import networkx as nx
import numpy as np

from gadapt.operations.mutation.candidate_solution_mutation import (
    base_decision_variable_mutation_selector as selector_module)
from research.iteration43_budget_operator_diagnostic import RouteChoiceCost
from research.iteration44_mutation_mechanism import ValidatorFree, run_ga


def synthetic_cost():
    graph = nx.random_regular_graph(4, 16, seed=5)
    for e in graph.edges:
        graph.edges[e]["dist"] = 1.0 + e[0]
    rng = np.random.default_rng(2)
    demands = [(a, b, float(rng.integers(1, 9))) for a in graph for b in graph
               if a != b and rng.random() < 0.3]
    return RouteChoiceCost(graph, demands)


class Iteration44Test(unittest.TestCase):
    def test_validator_calls_are_checked_and_not_counted(self):
        f = synthetic_cost()
        cost = ValidatorFree(f, f.n)
        cost(np.zeros(f.n))
        cost(np.ones(f.n))
        self.assertEqual((cost.skipped, cost.calls, cost.best), (2, 0, float("inf")))
        cost(np.zeros(f.n))
        self.assertEqual(cost.calls, 1)

    def test_validator_order_violation_raises(self):
        f = synthetic_cost()
        with self.assertRaises(RuntimeError):
            ValidatorFree(f, f.n)(np.ones(f.n))

    def _mutation_call_sizes(self, one_gene):
        f = synthetic_cost()
        sizes = []
        original = selector_module.BaseDecisionVariableMutationSelector.mutate

        def counting(self, c, number):
            before = len(c.mutated_variables_id_list)
            original(self, c, number)
            sizes.append((number, len(c.mutated_variables_id_list) - before))

        selector_module.BaseDecisionVariableMutationSelector.mutate = counting
        try:
            random.seed(3)
            np.random.seed(3)
            cost = ValidatorFree(f, f.n)
            cost.budget = 600
            run_ga(cost, f.n, one_gene)
        finally:
            selector_module.BaseDecisionVariableMutationSelector.mutate = original
        self.assertEqual(cost.skipped, 2)
        return sizes

    def test_one_gene_option_limits_each_mutation_call(self):
        # Every call honours the limit it is given: 1 from the population mutation, and the
        # attempt-based limit of the crossover duplicate repair (identical in both arms).
        one = self._mutation_call_sizes(True)
        self.assertTrue(all(size <= max(number, 1) for number, size in one))
        self.assertEqual(max(size for number, size in one if number == 1), 1)
        default = self._mutation_call_sizes(False)
        self.assertTrue(any(size > max(number, 1) or size > 1 for number, size in default))

    def test_gadapt_library_untouched(self):
        diff = subprocess.run(["git", "diff", "--stat", "HEAD", "--", "gadapt/"],
                              capture_output=True, text=True, check=True).stdout
        self.assertEqual(diff.strip(), "")


if __name__ == "__main__":
    unittest.main()
