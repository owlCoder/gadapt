import random

from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (
    RandomDecisionVariableMutator,
)
from gadapt.utils.ga_utils import get_rand_bool, get_rand_bool_with_probability


# *** Obsolete ***
class ExtremePointedDecisionVariableMutator(RandomDecisionVariableMutator):
    def _make_mutated_value(self):
        return self._make_mutation()

    def _make_rounded_random_value_below_or_above(self):
        return round(
            self._make_random_value_below_or_above(),
            self.variable_value.decision_variable.decimal_places,
        )

    def _make_random_value_below_or_above(self):
        if get_rand_bool():
            return self._make_random_value_above()
        return self._make_random_value_below()

    def _make_random_value_below(self):
        if self.variable_value.value == self.variable_value.decision_variable.min_value:
            return self.variable_value.decision_variable.make_random_value()
        number_of_steps = random.randint(
            0,
            round(
                (self.variable_value.value - self.variable_value.decision_variable.min_value)
                / self.variable_value.decision_variable.step
            ),
        )
        return (
            self.variable_value.decision_variable.min_value + number_of_steps * self.variable_value.decision_variable.step
        )

    def _make_random_value_above(self):
        if self.variable_value.value == self.variable_value.decision_variable.max_value:
            return self.variable_value.decision_variable.make_random_value()
        number_of_steps = random.randint(
            0,
            round(
                (self.variable_value.decision_variable.max_value - self.variable_value.value)
                / self.variable_value.decision_variable.step
            ),
        )
        return (
            self.variable_value.value + number_of_steps * self.variable_value.decision_variable.step
        )

    def _get_mutate_func(self):
        # Extreme-point step arithmetic is only defined on an effective
        # discrete mesh. Missing or ultra-fine steps are continuous in the
        # standard value generator; fall back to its bounded random value
        # rather than divide by None or create billions of step positions.
        if not self.variable_value.decision_variable.is_discrete:
            return super()._make_mutated_value
        prob = self.variable_value.decision_variable.columnar_diversity_coefficient
        if prob > 1.0:
            prob = 1.0
        should_mutate_random = get_rand_bool_with_probability(prob)
        if should_mutate_random:
            return super()._make_mutated_value
        else:
            return self._make_rounded_random_value_below_or_above

    def _make_mutation(self):
        f = self._get_mutate_func()
        return f()
