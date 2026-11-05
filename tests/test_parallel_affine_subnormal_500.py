"""500 independent, parallel, deterministic numerical contracts for opt-in affine diversity.

These run without GA optimization, objective callbacks, or physical solver calls.
They are engineering regression checks, not optimizer benchmarks.
"""
from concurrent.futures import ThreadPoolExecutor
import math
import unittest
from types import SimpleNamespace

from gadapt.operations.population_update.cost_diversity_population_updater import (
    CostDiversityPopulationUpdater,
)
from gadapt.utils.affine_cost_diversity import affine_cost_diversity


class ParallelAffineSubnormalContracts(unittest.TestCase):
    def test_smallest_subnormal_does_not_look_converged(self):
        ulp = math.ulp(0.0)
        score, reference = affine_cost_diversity([0.0, ulp])
        self.assertEqual(score, 1.0)
        self.assertEqual(reference, ulp)
        current, _ = affine_cost_diversity([0.0, ulp], reference)
        self.assertEqual(current, 1.0)
        converged, _ = affine_cost_diversity([ulp, ulp], reference)
        self.assertEqual(converged, 0.0)
        # Half-range is unchanged as soon as it is representable.
        self.assertEqual(affine_cost_diversity([0.0, 2 * ulp])[1], ulp)

    def test_real_population_updater_preserves_subnormal_diversity(self):
        ulp = math.ulp(0.0)
        population = SimpleNamespace(
            options=SimpleNamespace(cost_diversity_metric="affine_invariant"),
            candidate_solutions=[
                SimpleNamespace(cost_value=value) for value in (0.0, ulp)
            ],
            relative_cost_diversity_in_first_population=float("nan"),
        )
        updater = CostDiversityPopulationUpdater()
        updater.population = population
        self.assertEqual(updater.calculate_coefficient_of_population_diversity(), 1.0)
        self.assertGreater(population.relative_cost_diversity_in_first_population, 0.0)
        population.candidate_solutions = [
            SimpleNamespace(cost_value=ulp) for _ in range(2)
        ]
        self.assertEqual(updater.calculate_coefficient_of_population_diversity(), 0.0)

    def test_500_numerical_cases_in_parallel(self):
        ulp = math.ulp(0.0)
        cases = []
        # 125 distinct gaps at the subnormal representation limit.
        for k in range(1, 126):
            cases.append(("subnormal-separation", k, 0.0, k * ulp))
        # 125 exact powers spanning subnormal, normal, and huge values.
        for k in range(125):
            cases.append(("exponent-sweep", k, 0.0,
                          math.ldexp(1.0, -1074 + 16 * k)))
        # 125 two-sided domains, including values near the high exponents.
        for k in range(125):
            x = math.ldexp(1.0, -1000 + 16 * k)
            cases.append(("signed-range", k, -x, x))
        # 125 independent ratios between a generation and its half-spread.
        for k in range(125):
            x = math.ldexp(1.0, -1000 + 16 * k)
            cases.append(("half-spread-ratio", k, -x, x))

        self.assertEqual(len(cases), 500)

        def verify(item):
            family, index, low, high = item
            try:
                score, reference = affine_cost_diversity([low, high])
                if score != 1.0 or reference <= 0.0 or not math.isfinite(reference):
                    return f"{family}:{index}: false zero/nonfinite diversity"
                if family == "half-spread-ratio":
                    score_half, _ = affine_cost_diversity(
                        [low * 0.5, high * 0.5], reference
                    )
                    if not math.isclose(score_half, 0.5, rel_tol=1e-12, abs_tol=1e-12):
                        return f"{family}:{index}: ratio {score_half!r}"
            except Exception as exc:
                return f"{family}:{index}: {type(exc).__name__}: {exc}"
            return None

        with ThreadPoolExecutor(max_workers=32) as executor:
            failures = [reason for reason in executor.map(verify, cases)
                        if reason is not None]
        self.assertEqual(failures, [],
                         "Failures in the 500 deterministic parallel checks")


if __name__ == "__main__":
    unittest.main()
