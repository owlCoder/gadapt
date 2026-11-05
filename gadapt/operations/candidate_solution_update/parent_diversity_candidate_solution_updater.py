from gadapt.ga_model.candidate_solution import CandidateSolution
from gadapt.ga_model.variable_value import VariableValue
from gadapt.utils import ga_utils
from gadapt.operations.candidate_solution_update.base_candidate_solution_updater import (
    BaseCandidateSolutionUpdater,
)


class ParentDiversityCandidateSolutionUpdater(BaseCandidateSolutionUpdater):
    """
    Updates candidate solution for the parent diversity purpose.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ParentDiversityCandidateSolutionUpdater, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._genetic_diversity = None
        self.cost_diversity_in_initial_population = float('NaN')

    def _get_genetic_diversity(self, mother_variable_value, father_variable_value) -> float:
        decision_variable = father_variable_value.decision_variable
        span = decision_variable.max_value - decision_variable.min_value
        if span == 0:
            # A fixed decision variable has no attainable genetic diversity.
            # Equal bounds are a valid model, not a reason to abort mating.
            return 0.0
        return abs(mother_variable_value.value - father_variable_value.value) / span

    def _get_parent_structural_diversity(self):
        return round(ga_utils.average(self._genetic_diversity), 8)

    def candidate_solution_prepare_update(self, mother_variable_value: VariableValue, father_variable_value: VariableValue):
        if mother_variable_value is None or father_variable_value is None:
            return
        self._genetic_diversity.append(
            self._get_genetic_diversity(mother_variable_value, father_variable_value)
        )

    def candidate_solution_update(self, offspring1: CandidateSolution, offspring2: CandidateSolution, mother: CandidateSolution, father: CandidateSolution):
        parent_structural_diversity = self._get_parent_structural_diversity()
        offspring1.parent_structural_diversity_coefficient = parent_structural_diversity
        offspring2.parent_structural_diversity_coefficient = parent_structural_diversity
        parent_cost_diversity_coefficient = self.calculate_parent_cost_diversity_coefficient(father, mother)
        offspring2.parent_cost_diversity_coefficient = parent_cost_diversity_coefficient
        offspring1.parent_cost_diversity_coefficient = parent_cost_diversity_coefficient

    def candidate_solution_start_update(self, *args, **kwargs):
        self._genetic_diversity = []

    def calculate_parent_cost_diversity_coefficient(self, father_candidate_solution: CandidateSolution, mother_candidate_solution: CandidateSolution):


        parents_avg_difference = ga_utils.average_difference([father_candidate_solution.cost_value, mother_candidate_solution.cost_value])
        if self.cost_diversity_in_initial_population is None or self.cost_diversity_in_initial_population == 0:
            return parents_avg_difference
        return min(parents_avg_difference / self.cost_diversity_in_initial_population, 1)
