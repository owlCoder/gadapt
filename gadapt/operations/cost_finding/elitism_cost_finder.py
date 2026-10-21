import math
from typing import List

from gadapt.adapters.ga_logging.logging_settings import gadapt_log_info
from gadapt.ga_model.candidate_solution import CandidateSolution
from gadapt.operations.cost_finding.base_cost_finder import BaseCostFinder


class ElitismCostFinder(BaseCostFinder):
    """
    Finds costs for the new candidate solutions and keeps only the best ones in the population
    (the number is determined by keep_elitism_percentage)
    """

    def _find_costs_for_population(self):
        if self.population is None:
            raise Exception("population must not be null!")
        candidate_solutions_for_execution: List[CandidateSolution] = [
            c
            for c in self.population
            if (math.isnan(c.cost_value))
            or (
                c.is_immigrant
                and c.population_generation == self.population.population_generation
            )
        ]
        for c in candidate_solutions_for_execution:
            self._execute_function(self.population.options.cost_function, c)
            controller = getattr(self.population.options, "operator_credit_controller", None)
            if controller is not None:
                controller.observe(c)
        if not any(getattr(c, "_succ", False) for c in self.population):
            raise ValueError("All evaluated candidate costs were invalid or nonfinite")
        better_candidate_solutions: List[CandidateSolution] = self.population.get_sorted(
            key=lambda x: x.cost_value
        )
        better_candidate_solutions = better_candidate_solutions[:self.population.options.keep_number]
        self.population.best_individual = better_candidate_solutions[0]
        self.population.min_cost = (
            min(better_candidate_solutions, key=lambda x: x.cost_value)
        ).cost_value
        better_candidate_solutions_without_immigrants = better_candidate_solutions[
            : self.population.options.keep_number
            - self.population.options.immigration_number
        ]
        self.population.avg_cost = sum(
            [c.cost_value for c in better_candidate_solutions_without_immigrants]
        ) / len(better_candidate_solutions_without_immigrants)
        self._log_population()
        self.population.clear_and_add_candidate_solutions(better_candidate_solutions)

    def _log_population(self):
        if self.population.options.logging:
            gadapt_log_info(str(self.population))
