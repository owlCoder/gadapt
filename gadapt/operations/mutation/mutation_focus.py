import math
import random


class MutationFocus:
    """
    Narrows the mutation while the minimal cost stagnates, so a converged population is refined
    by a few small changes instead of many large ones. It is shared by the components that decide
    how many decision variables are mutated and which mutator alters a value.

    The focus factor is 0.5 ** (generations without improvement / focus_generations): 1 while the
    optimization progresses, halved for every focus_generations consecutive generations without an
    improvement of the minimal cost, and restored when it improves. With the factor below 1,
    the number of mutated decision variables is scaled by it (at least one stays), and the
    random mutator (a new value anywhere in the range) is chosen with a probability scaled by it.

    To keep the randomness, a candidate solution is mutated without the focus (the factor is 1)
    with the probability exploration_probability, drawn once for each mutated candidate solution.
    """

    def __init__(self, focus_generations: float, exploration_probability: float, get_stagnation_generations_function):
        self.focus_generations = focus_generations
        self.exploration_probability = exploration_probability
        self.get_stagnation_generations_function = get_stagnation_generations_function
        self._exploring = False

    def begin_candidate_solution(self):
        """
        Called before the mutation of a candidate solution: decides if the candidate solution is mutated without the focus.
        """
        self._exploring = random.random() < self.exploration_probability

    @property
    def factor(self) -> float:
        if self._exploring:
            return 1.0
        stagnation_generations_function = self.get_stagnation_generations_function()
        if stagnation_generations_function is None:
            return 1.0
        return 0.5 ** (stagnation_generations_function() / self.focus_generations)

    def focus_count(self, number_of_mutation_decision_variables: int) -> int:
        """
        Scales the number of mutated decision variables by the focus factor. At least one remains.
        """
        factor = self.factor
        if factor >= 1.0 or number_of_mutation_decision_variables < 1:
            return number_of_mutation_decision_variables
        return max(1, math.ceil(number_of_mutation_decision_variables * factor))
