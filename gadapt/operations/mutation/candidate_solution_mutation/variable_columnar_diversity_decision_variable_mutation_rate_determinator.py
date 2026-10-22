from math import isnan

import gadapt.utils.ga_utils as ga_utils
from gadapt.adapters.ga_logging.logging_settings import gadapt_log_error
from gadapt.operations.mutation.candidate_solution_mutation.random_decision_variable_mutation_rate_determinator import (
    RandomDecisionVariableMutationRateDeterminator,
)


class VariableColumnarDiversityDecisionVariableMutationRateDeterminator(RandomDecisionVariableMutationRateDeterminator):
    """
    Determines the number of mutation decision variables in a candidate solution based on the variable columnar diversity coefficient of the decision variable.
    """

    def __init__(
        self,
        strict_limit: bool = False,
    ) -> None:
        """
        Args:
            strict_limit: If True, the number of mutation decision variables never exceeds
                the maximum passed to get_number_of_mutation_decision_variables.
        """
        super().__init__()
        self._strict_limit = strict_limit

    def _get_mutation_rate(self, decision_variables) -> float:
        avg_rsd = ga_utils.average([g.columnar_diversity_coefficient for g in decision_variables])
        if avg_rsd > 1:
            avg_rsd = 1
        if avg_rsd < 0:
            avg_rsd = 0
        return avg_rsd

    def _get_number_of_mutation_decision_variables(self) -> int:
        decision_variables = [g.decision_variable for g in self.candidate_solution]
        if any(
                g.columnar_diversity_coefficient is None
                or isnan(g.columnar_diversity_coefficient)
            for g in decision_variables
        ):
            gadapt_log_error("columnar_diversity_coefficient not set!")
            return super()._get_number_of_mutation_decision_variables()

        mutation_rate = self._get_mutation_rate(decision_variables)
        limit_number_of_mutation_decision_variables = mutation_rate * float(
            len(decision_variables)
        )
        limit_number_of_mutation_decision_variables_rounded = round(limit_number_of_mutation_decision_variables)
        preferred_number_of_mutation_decision_variables =  round(len(self.candidate_solution) / 5)
        if limit_number_of_mutation_decision_variables_rounded < preferred_number_of_mutation_decision_variables:
            limit_number_of_mutation_decision_variables_rounded = max(preferred_number_of_mutation_decision_variables, 1)
        if self._strict_limit:
            limit_number_of_mutation_decision_variables_rounded = min(
                limit_number_of_mutation_decision_variables_rounded,
                max(self.max_number_of_mutation_decision_variables, 1),
            )
        self.max_number_of_mutation_decision_variables = limit_number_of_mutation_decision_variables_rounded
        return super()._get_number_of_mutation_decision_variables()
