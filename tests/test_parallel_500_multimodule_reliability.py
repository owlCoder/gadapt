"""500 parallel independent deterministic checks across GAdapt reliability modules.

Source-contract checks only: no GA optimizer runs, objective callbacks, or
benchmark evaluations. Thread tasks use isolated model/monitor instances.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import math
import statistics
import unittest
from types import SimpleNamespace

from gadapt.execution.discrete_certification import discrete_grid_axes
from gadapt.execution.reliability import ReliabilityMonitor
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.variable_value import VariableValue
from gadapt.operations.decision_variable_update.variable_columnar_diversity_decision_variable_updater import (
    ColumnarDiversityDecisionVariableUpdater,
)
from gadapt.operations.population_update.cost_diversity_population_updater import (
    CostDiversityPopulationUpdater,
)
from gadapt.utils.affine_cost_diversity import affine_cost_diversity


class Candidate(list):
    is_immigrant = False


class Population(list):
    pass


def columnar(metric, values, low, high):
    variable = DecisionVariable(0)
    variable.min_value = low
    variable.max_value = high
    population = Population(
        Candidate([VariableValue(variable, number)]) for number in values
    )
    population.options = SimpleNamespace(reliability_monitor=object())
    ColumnarDiversityDecisionVariableUpdater(metric).update_decision_variables(
        population
    )
    return variable


def check_case(case):
    """One independently constructed deterministic assertion, no shared state."""
    family, index = case

    if family == "affine-wide":
        # 50 distinct binary exponents, spanning very small to very large.
        exponent = -300 + index * 20
        extent = math.ldexp(1.0, exponent)
        coefficient, spread = affine_cost_diversity([-extent, extent])
        assert coefficient == 1.0 and spread == extent
    elif family == "affine-half":
        exponent = -500 + index * 20
        extent = math.ldexp(1.0, exponent)
        _, reference = affine_cost_diversity([-extent, extent])
        coefficient, _ = affine_cost_diversity(
            [-extent * 0.5, extent * 0.5], reference
        )
        assert coefficient == 0.5, coefficient
    elif family == "affine-recovery":
        exponent = -300 + index * 20
        extent = math.ldexp(1.0, exponent)
        tied, reference = affine_cost_diversity([extent, extent])
        resumed, reference_after = affine_cost_diversity(
            [-extent, extent], reference
        )
        converged, _ = affine_cost_diversity([extent, extent], reference_after)
        assert (tied, resumed, converged) == (0.0, 1.0, 0.0)
    elif family == "linear-extreme":
        # The values remain finite while their declared span overflows binary64.
        variable = columnar(
            "linear", [-1e308, 1e308], -1e308, 1e308
        )
        assert variable.columnar_diversity_coefficient == 1.0
        assert math.isclose(variable.initial_st_dev, math.sqrt(0.5), rel_tol=1e-13)
        # Repeat with a strictly interior, distinct location for each index.
        candidate = -1e308 + (index + 1) * 1e306
        variable = columnar("linear", [-1e308, candidate], -1e308, 1e308)
        assert variable.initial_st_dev > 0.0 and math.isfinite(variable.initial_st_dev)
    elif family == "linear-ordinary":
        extent = float(index + 1)
        variable = columnar(
            "linear", [-extent, 0.0, extent], -extent, extent
        )
        assert variable.columnar_diversity_coefficient == 1.0
        assert math.isclose(
            variable.initial_st_dev, statistics.stdev([0.0, 0.5, 1.0]),
            rel_tol=1e-13,
        )
    elif family == "log-columnar-extreme":
        upper = (index + 51) * 1e306
        variable = columnar(
            "log_relative", [-1e308, upper], -1e308, 1e308
        )
        assert variable.initial_st_dev > 0.0
        assert math.isfinite(variable.initial_st_dev)
        assert variable.columnar_diversity_coefficient == 1.0
    elif family == "log-cost-extreme":
        upper = (index + 51) * 1e306
        population = SimpleNamespace(
            options=SimpleNamespace(
                cost_diversity_metric="log_relative", reliability_monitor=object()
            ),
            candidate_solutions=[
                SimpleNamespace(cost_value=number) for number in (-1e308, upper)
            ],
            relative_cost_diversity_in_first_population=None,
        )
        updater = CostDiversityPopulationUpdater()
        updater.population = population
        coefficient = updater.calculate_coefficient_of_population_diversity()
        assert coefficient == 1.0
        assert math.isfinite(
            population.relative_cost_diversity_in_first_population
        )
    elif family == "discrete-grid":
        variable = DecisionVariable(0)
        variable.min_value = 0.0
        variable.max_value = (index + 2) / 8
        variable.step = 0.125
        axes = discrete_grid_axes([variable], max_points=1000)
        assert axes is not None
        assert len(axes) == 1 and len(axes[0]) == index + 3, axes
        assert axes[0][0] == 0.0 and axes[0][-1] == variable.max_value
        assert len(set(axes[0])) == len(axes[0])
    elif family == "bounds-large-int":
        low = 2**53 + index * 16
        upper = low + 2
        monitor = ReliabilityMonitor(
            lambda _: 1.0, 1, -1.0, constrained=False,
            decision_bounds=((low, upper),)
        )
        assert monitor._candidate_in_bounds([low + 1])
        assert not monitor._candidate_in_bounds([low - 1])
        assert not monitor._candidate_in_bounds([upper + 1])
        assert monitor.evaluations == 0
    elif family == "exact-cache-keys":
        left = 2**53 + 4 * index
        right = left + 1
        monitor = ReliabilityMonitor(
            lambda _: 1.0, 1, -1.0, constrained=False,
            cache_evaluations=True
        )
        first = monitor._cache_key((left,))
        second = monitor._cache_key((right,))
        assert first is not None and second is not None
        assert first != second
        assert monitor.evaluations == 0
    else:
        raise AssertionError("Unknown family: " + family)

    return {"family": family, "index": index, "passed": True}


class ParallelMultiModuleReliabilityContracts(unittest.TestCase):
    def test_500_deterministic_source_contracts_in_parallel(self):
        families = (
            "affine-wide", "affine-half", "affine-recovery",
            "linear-extreme", "linear-ordinary", "log-columnar-extreme",
            "log-cost-extreme", "discrete-grid", "bounds-large-int",
            "exact-cache-keys",
        )
        cases = [(family, index) for family in families for index in range(50)]
        self.assertEqual(len(cases), 500)
        self.assertEqual(len(set(cases)), 500)

        def checked(case):
            try:
                return check_case(case)
            except Exception as exc:
                return {"family": case[0], "index": case[1],
                        "passed": False, "error": f"{type(exc).__name__}: {exc}"}

        with ThreadPoolExecutor(max_workers=32) as executor:
            results = list(executor.map(checked, cases))

        counts = Counter(row["family"] for row in results if row["passed"])
        failures = [row for row in results if not row["passed"]]
        print(f"PARALLEL_500_SUMMARY: executed={len(results)} "
              f"passed={len(results)-len(failures)} failed={len(failures)} "
              f"families={dict(counts)} workers=32")
        self.assertEqual(failures, [], "A deterministic source contract failed")
        self.assertEqual(set(counts.values()), {50})


if __name__ == "__main__":
    unittest.main()
