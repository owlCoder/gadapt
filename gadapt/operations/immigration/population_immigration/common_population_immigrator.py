import math
from typing import List

from gadapt.ga_model.candidate_solution import CandidateSolution
from gadapt.operations.immigration.population_immigration.base_population_immigrator import (
    BasePopulationImmigrator,
)


class CommonPopulationImmigrator(BasePopulationImmigrator):
    """
    Common class for the population immigration.
    In the kept part of the population, the lowest ranked candidate solutions are replaced with immigrants
    """

    def _immigration_count(self):
        """Return scheduled immigration count, preserving the fixed baseline.

        Only trigger adaptive immigrants at an integer multiple of patience,
        after stagnation AND low diversity. This prevents an expensive
        population reset at every stagnant generation. The elite survives.
        """
        options = self.population.options
        fixed = options.immigration_number
        patience = options.adaptive_immigration_patience
        if patience is None or options.adaptive_immigration_percentage <= 0:
            return fixed
        stagnant = self.population.generations_without_improvement
        if stagnant < patience or stagnant % patience != 0:
            return fixed
        diversity = self.population.get_relative_cost_diversity_coefficient()
        if (not math.isfinite(diversity) or
                diversity >= options.adaptive_immigration_diversity_threshold):
            return fixed
        available = max(0, options.keep_number - 1)
        suggested = max(1, math.ceil(options.keep_number *
                                     options.adaptive_immigration_percentage / 100))
        return max(fixed, min(suggested, available))

    def _immigrate_population(self):
        immigration_count = self._immigration_count()
        if immigration_count < 1:
            return
        keep_number = self.population.options.keep_number
        candidate_solution_list: List[CandidateSolution] = list(
            self.population.get_sorted(key=lambda c: c.cost_value)
        )[:keep_number]
        candidate_solution_list = sorted(
            candidate_solution_list, key=lambda c: (-c.cost_value, -c.candidate_solution_id)
        )[: immigration_count]
        for c in candidate_solution_list:
            self._candidate_solution_immigrator.immigrate(c)
            c.population_generation = self.population.population_generation
