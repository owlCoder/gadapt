import math
import random
import sys

from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.operations.candidate_solution_update.base_candidate_solution_updater import (
    BaseCandidateSolutionUpdater,
)
from gadapt.operations.crossover.base_crossover_probability_determinator import BaseCrossoverProbabilityDeterminator
from gadapt.operations.mutation.candidate_solution_mutation.base_decision_variable_mutation_selector import BaseDecisionVariableMutationSelector


class BlendingCrossover(BaseCrossover):
    """
    Blending Crossover combines
    variable values from the two parents into new variable values in offsprings.
    One value of the offspring variable comes from a combination of the two
    corresponding values of the parental decision variables
    """

    def __init__(self, candidate_solution_updater: BaseCandidateSolutionUpdater, mutator: BaseDecisionVariableMutationSelector, crossover_rate_determinator: BaseCrossoverProbabilityDeterminator):
        super(BlendingCrossover, self).__init__(candidate_solution_updater, mutator, crossover_rate_determinator)
        self._current_decision_variable_number = -1

    def _combine(self):
        decision_variable = self._father_variable_value.decision_variable
        val_father = self._father_variable_value.value
        val_mother = self._mother_variable_value.value
        if hasattr(decision_variable, "step") and decision_variable.step is not None and decision_variable.step > 0 and decision_variable.step > sys.float_info.min:
            val1, val2 = self._combine_with_step(decision_variable, val_father, val_mother)
        else:
            val1, val2 = self._combine_without_step(decision_variable, val_father, val_mother)
        return val1, val2

    def _combine_with_step(self, decision_variable, val_father, val_mother):
        x = 1
        if val_mother > val_father:
            x = -1
        # An extremely fine, positive step can overflow the binary64
        # ratio even when the declared bounds and both parent values are
        # finite. The old round(inf) aborted the whole GA run. Only this
        # previously failing case uses bounded continuous blending; retain
        # existing discrete behavior for every finite step ratio.
        step_count = abs((val_father - val_mother) / decision_variable.step)
        if not math.isfinite(step_count):
            return self._combine_without_step(decision_variable, val_father, val_mother)
        beta_steps = random.randint(0, round(step_count))
        val1 = round(
            val_father - (beta_steps * x) * decision_variable.step,
            decision_variable.decimal_places,
        )
        val2 = round(
            val_mother + (beta_steps * x) * decision_variable.step,
            decision_variable.decimal_places,
        )
        return val1, val2

    def _combine_without_step(self, decision_variable, val_father, val_mother):
        # --- Continuous case (no step defined) ---
        alpha = random.random()  # uniform in [0,1]
        val1 = alpha * val_father + (1 - alpha) * val_mother
        val2 = alpha * val_mother + (1 - alpha) * val_father
        return val1, val2
