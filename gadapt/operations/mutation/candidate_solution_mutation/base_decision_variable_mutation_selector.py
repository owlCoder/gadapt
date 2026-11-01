from abc import ABC, abstractmethod

from gadapt.ga_model.variable_value import VariableValue
from gadapt.operations.mutation.candidate_solution_mutation.base_decision_variable_mutation_rate_determinator import (
    BaseDecisionVariableMutationRateDeterminator,
)
from gadapt.operations.mutation.decision_variable_mutation.base_decision_variable_mutator import BaseDecisionVariableMutator


class BaseDecisionVariableMutationSelector(ABC):
    """
    Provides a framework for selecting and mutating decision variables in a candidate solution.
    """

    def __init__(
        self,
        decision_variable_mutation_rate_determinator: BaseDecisionVariableMutationRateDeterminator,
        decision_variable_mutator: BaseDecisionVariableMutator,
    ):
        """
        Args:
            decision_variable_mutation_rate_determinator: determines the number of decision variables to mutate
            decision_variable_mutator: mutates the value of a selected decision variable
        """
        self.candidate_solution = None
        self._decision_variable_mutation_rate_determinator = decision_variable_mutation_rate_determinator
        self._decision_variable_mutator = decision_variable_mutator
        self.number_of_mutation_decision_variables = -1
        self.focus = None  # a MutationFocus, if the late-stage mutation focus is on

    def mutate(self, c, number_of_mutation_decision_variables: int):
        """
        Selects and mutates decision variables in the candidate solution
        Args:
            c: Candidate solution to mutate
            number_of_mutation_decision_variables: Number of mutation decision variables
        """
        self.candidate_solution = c
        if self.focus is not None:
            self.focus.begin_candidate_solution()
        if number_of_mutation_decision_variables > len(c):
            self.number_of_mutation_decision_variables = len(c)
        else:
            self.number_of_mutation_decision_variables = number_of_mutation_decision_variables
        self._before_mutated()
        self._mutate_candidate_solution()
        self._candidate_solution_mutated()

    @abstractmethod
    def _mutate_candidate_solution(self):
        pass

    def _mutate_decision_variable(self, g: VariableValue):
        self._decision_variable_mutator.mutate(g)
        self._decision_variable_mutated(g)

    def _decision_variable_mutated(self, g):
        self.candidate_solution.mutated_variables_id_list.append(g.decision_variable.variable_id)

    def _candidate_solution_mutated(self):
        self.candidate_solution.is_mutated = True
        if self.candidate_solution.first_mutant_generation == 0:
            self.candidate_solution.first_mutant_generation += 1
        self.candidate_solution.last_mutant_generation = 1
        self.candidate_solution.set_candidate_solution_string_none()
        self.candidate_solution.reset_hash_cache()

    def _before_mutated(self):
        self.candidate_solution.mutated_variables_id_list.clear()
