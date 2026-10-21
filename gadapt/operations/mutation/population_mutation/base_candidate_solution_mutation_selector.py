import math
from abc import ABC, abstractmethod
from typing import List

from gadapt.ga_model.candidate_solution import CandidateSolution
from gadapt.operations.mutation.population_mutation.base_candidate_solution_mutation_rate_determinator import (
    BaseCandidateSolutionMutationRateDeterminator,
)
from gadapt.operations.mutation.candidate_solution_mutation.base_decision_variable_mutation_selector import (
    BaseDecisionVariableMutationSelector,
)


class BaseCandidateSolutionMutationSelector(ABC):
    """
    Selects and mutates the candidate solutions in the population based on a specified number of mutated candidate solutions.
    """

    def __init__(
        self,
        candidate_solution_mutation_rate_determinator: BaseCandidateSolutionMutationRateDeterminator,
        decision_variable_mutation_selector: BaseDecisionVariableMutationSelector,
    ) -> None:
        """
        Base class for selecting candidate solutions in the population to be mutated
        Args:
            candidate_solution_mutation_rate_determinator: candidate solution mutation rate determinator
            decision_variable_mutation_selector: selector which mutates decision variables
                inside each selected candidate solution
        """
        super().__init__()
        self.population = None
        self._candidate_solution_mutation_rate_determinator = (
            candidate_solution_mutation_rate_determinator
        )
        self.number_of_mutation_candidate_solutions = -1
        self._decision_variable_mutation_selector = decision_variable_mutation_selector

    @abstractmethod
    def _get_candidate_solutions_for_mutation(self) -> List[CandidateSolution]:
        pass

    def mutate(self, population):
        """
        Mutates candidate solutions in the population
        Args:
            population: Population to mutate
        """
        self.population = population
        max_number_of_mutated_candidate_solutions = (
            population.options.number_of_mutation_candidate_solutions
        )
        self.number_of_mutation_candidate_solutions = self._candidate_solution_mutation_rate_determinator.get_number_of_mutation_candidate_solutions(
            self.population, max_number_of_mutated_candidate_solutions
        )
        candidate_solutions_for_mutation = self._get_candidate_solutions_for_mutation()
        candidate_solutions_for_mutation = [c for c in candidate_solutions_for_mutation if not c.is_mutated]
        self._mutate_population(candidate_solutions_for_mutation)

    def _mutate_population(self, candidate_solutions_for_mutation:  List[CandidateSolution]):

        for c in candidate_solutions_for_mutation:
            number_of_attempts = 0
            candidate_solutions_added = False
            while (not candidate_solutions_added) and number_of_attempts < 10:
                number_of_attempts += 1
                controller = getattr(self.population.options, "operator_credit_controller", None)
                if controller is not None and getattr(controller, "assignment", None) == "paired":
                    # A physical baseline evaluation is deliberately charged to
                    # the SAME objective counter/budget as the mutated offspring.
                    controller.before_candidate_mutation(
                        c, self.population.options.cost_function
                    )
                self._decision_variable_mutation_selector.mutate(
                    c, self.population.options.number_of_mutation_decision_variables
                )
                if (not self.population.options.ensure_unique_individuals) or (not self.population.contained_candidate_solution(c)):
                    candidate_solutions_added = True
            self.population.register_candidate_solution(c)
        return len(candidate_solutions_for_mutation)

    def mutate_candidate_solution(self, c: CandidateSolution, number_of_mutated_candidate_solutions: int):
        self._decision_variable_mutation_selector.mutate(c, number_of_mutated_candidate_solutions)

    def _get_unallocated_candidate_solutions(self, sort_key_function=None) -> List[CandidateSolution]:
        def unallocated_candidate_solutions_condition(c: CandidateSolution) -> bool:
            return (
                math.isnan(c.cost_value)
                and (not c.is_immigrant)
                and c.population_generation == self.population.population_generation
                and not c.is_mutated
            )

        lst = [c for c in self.population if (unallocated_candidate_solutions_condition(c))]
        if sort_key_function is not None:
            lst.sort(key=sort_key_function)
        return lst
