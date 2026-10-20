import math

from gadapt.operations.population_update.base_population_updater import (
    BasePopulationUpdater,
)
from gadapt.utils import ga_utils
from gadapt.utils.affine_cost_diversity import affine_cost_diversity


class CostDiversityPopulationUpdater(BasePopulationUpdater):
    """
    Updates the cost diversity of the population: the absolute cost diversity and the relative
    cost diversity coefficient (1.0 for the first population, approaching 0.0 as the costs converge).
    """

    def _calculate_absolute_cost_diversity(self):
        allocated_values = [
            c.cost_value
            for c in self.population.candidate_solutions
            if c.cost_value is not None and not math.isnan(c.cost_value)
        ]
        if allocated_values:
            return ga_utils.average_difference(allocated_values)
        return float("NaN")

    def _calculate_relative_cost_diversity(self):
        # 1. Extract valid cost values
        allocated_values = [
            c.cost_value
            for c in self.population.candidate_solutions
            if c.cost_value is not None and not math.isnan(c.cost_value)
        ]

        if not allocated_values:
            return float("NaN")

        # 2. Calculate the Absolute Average Difference (average difference between the costs)
        abs_diff = ga_utils.average_difference(allocated_values)

        # 3. Calculate the current scale (Mean of absolute values)
        # Using absolute values ensures this works even if costs are negative
        mean_magnitude = sum(abs(v) for v in allocated_values) / len(allocated_values)

        # 4. Normalize: Handle the case where the entire population is at 0
        if mean_magnitude == 0:
            return 0.0

        # This value represents diversity relative to the current cost scale
        relative_diversity = abs_diff / mean_magnitude

        return relative_diversity

    def _get_coefficient_of_population_diversity_(self):
        allocated_values = [
            c.cost_value
            for c in self.population.candidate_solutions
            if c.cost_value is not None and not math.isnan(c.cost_value)
        ]

        if not allocated_values or len(allocated_values) < 2:
            return 0.0

        # 1. Current Absolute Difference
        abs_diff = ga_utils.average_difference(allocated_values)

        # 2. Current Mean (Magnitude)
        mean_val = sum(abs(v) for v in allocated_values) / len(allocated_values)

        if mean_val == 0:
            return 0.0

        # 3. Current Relative Diversity
        current_rel_div = abs_diff / mean_val

        # 4. Capture or Apply Benchmark
        if self.population.relative_cost_diversity_in_first_population is None or math.isnan(self.population.relative_cost_diversity_in_first_population) :
            # This is the first generation
            self.population.relative_cost_diversity_in_first_population = current_rel_div
            return 1.0

        # Calculate ratio compared to the start
        normalized_score = current_rel_div / self.population.relative_cost_diversity_in_first_population

        # Cap at 1.0 (in case diversity momentarily increases) and bottom at 0.0
        return max(0.0, min(1.0, normalized_score))

    def calculate_coefficient_of_population_diversity(self) -> float:
        if self.population.options.cost_diversity_metric == "affine_invariant":
            costs = [c.cost_value for c in self.population.candidate_solutions]
            initial = self.population.relative_cost_diversity_in_first_population
            if initial is None or math.isnan(initial):
                initial = None
            coefficient, initial = affine_cost_diversity(costs, initial)
            self.population.relative_cost_diversity_in_first_population = initial
            return coefficient
        return self._calculate_log_relative_cost_diversity()

    def _calculate_log_relative_cost_diversity(self) -> float:
        """
        Calculates diversity in log-space.
        1.0 = Same relative diversity as Generation 0.
        0.0 = Population has converged to identical costs.
        """
        # 1. Extract and Filter
        # Note: Logarithms require values > 0.
        # If the lowest cost is below 1.0, all values are shifted so that the lowest becomes 1.0.
        raw_values = [
            c.cost_value
            for c in self.population.candidate_solutions
            if c.cost_value is not None and not math.isnan(c.cost_value)
        ]

        if not raw_values:
            return 0.0

        # Shift all values so the minimum becomes 1.0 (safe for log)
        min_val = min(raw_values)
        shift = 1.0 - min_val if min_val < 1.0 else 0.0
        allocated_values = [math.log(v + shift) for v in raw_values]

        if len(allocated_values) < 2:
            return 0.0

        # 2. Calculate average difference in log-space
        # This measures the average 'order of magnitude' spread
        current_log_diff = ga_utils.average_difference(allocated_values)

        # 3. Handle the Benchmark (Generation 0)
        if self.population.relative_cost_diversity_in_first_population is None or math.isnan(self.population.relative_cost_diversity_in_first_population):
            self.population.relative_cost_diversity_in_first_population = current_log_diff
            return 1.0

        if self.population.relative_cost_diversity_in_first_population == 0:
            return 0.0

        # 4. Map to 0-1 range
        normalized_score = current_log_diff / self.population.relative_cost_diversity_in_first_population

        return max(0.0, min(1.0, normalized_score))

    def _update_population(self):
        self.population.absolute_cost_diversity = (
            self._calculate_absolute_cost_diversity()
        )
        self.population.relative_cost_diversity_coefficient = (
            self.calculate_coefficient_of_population_diversity()
        )
        if math.isnan(self.population.absolute_cost_diversity_in_first_population):
            self.population.absolute_cost_diversity_in_first_population = (
                self.population.absolute_cost_diversity
            )
