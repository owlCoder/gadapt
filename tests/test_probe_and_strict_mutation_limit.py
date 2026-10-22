"""Opt-in probe_cost_function and strict_mutation_decision_variable_limit.

Synthetic binary problem; the defaults are covered by a separate seeded call-sequence check.
"""
import random
import unittest

import numpy as np

from gadapt.ga import GA
from gadapt.operations.mutation.population_mutation import (
    base_candidate_solution_mutation_selector as population_module)

N = 40
WEIGHTS = np.random.RandomState(7).rand(N)


def _cost(values):
    return float(np.dot(WEIGHTS, np.asarray(values)) + 3 * abs(sum(values) - 20))


def _ga(cost, **kwargs):
    ga = GA(cost_function=cost, exit_check="generations", number_of_generations=30, **kwargs)
    for _ in range(N):
        ga.add(0., 1., 1.)
    return ga


class ProbeCostFunctionTest(unittest.TestCase):
    def _first_calls(self, probe):
        calls = []

        def cost(values):
            calls.append(list(values))
            return _cost(values)

        random.seed(1)
        np.random.seed(1)
        self.assertTrue(_ga(cost, probe_cost_function=probe).execute().success)
        return calls

    def test_default_probes_min_and_max(self):
        calls = self._first_calls(True)
        self.assertEqual(calls[0], [0.] * N)
        self.assertEqual(calls[1], [1.] * N)

    def test_disabled_probe_skips_both_calls(self):
        with_probe, without_probe = self._first_calls(True), self._first_calls(False)
        self.assertEqual(without_probe, with_probe[2:])

    def test_non_callable_still_rejected(self):
        with self.assertRaisesRegex(Exception, "callable"):
            _ga(5, probe_cost_function=False).execute()

    def test_type_is_checked(self):
        with self.assertRaises(ValueError):
            GA(cost_function=_cost, probe_cost_function="no")


class StrictMutationLimitTest(unittest.TestCase):
    def _population_mutation_sizes(self, strict):
        sizes = []
        original = population_module.BaseCandidateSolutionMutationSelector._mutate_population

        def recording(selector, candidate_solutions):
            before = [len(c.mutated_variables_id_list) for c in candidate_solutions]
            result = original(selector, candidate_solutions)
            sizes.extend(len(c.mutated_variables_id_list) - b
                         for c, b in zip(candidate_solutions, before))
            return result

        population_module.BaseCandidateSolutionMutationSelector._mutate_population = recording
        try:
            random.seed(2)
            np.random.seed(2)
            ga = _ga(_cost, number_of_mutation_decision_variables=2, ensure_unique_individuals=False,
                     strict_mutation_decision_variable_limit=strict)
            self.assertTrue(ga.execute().success)
        finally:
            population_module.BaseCandidateSolutionMutationSelector._mutate_population = original
        return sizes

    def test_default_can_exceed_the_limit(self):
        self.assertGreater(max(self._population_mutation_sizes(False)), 2)

    def test_strict_limit_is_respected(self):
        sizes = self._population_mutation_sizes(True)
        self.assertTrue(sizes)
        self.assertLessEqual(max(sizes), 2)


if __name__ == "__main__":
    unittest.main()
