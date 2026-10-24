"""
Results for the genetic algorithm execution
"""

from typing import List, Optional

import gadapt.adapters.string_operation.ga_strings as ga_strings
from gadapt.ga_model.population import Population


class GAResults:
    def __init__(self) -> None:
        """
        Results class for the genetic algorithm execution
        """
        self._success = True
        self.result_values = {}
        self._messages: List[str] = []
        self._min_cost_per_generation: List[float] = []
        self._initial_population: Optional[Population] = None
        self._min_cost = float("NaN")
        # with constraint_handling: objective and violation of the best evaluated candidate solution of the run
        # (min_cost is the scalar of the best candidate solution of the final population)
        self.best_objective = float("NaN")
        self.best_violation = float("NaN")
        self.feasible = None

    def __str__(self) -> str:
        return ga_strings.results_to_string(self)

    @property
    def result_values(self):
        """
        The dictionary that contains variables' optimized values.
        The key of this dictionary is the sequence number of variable adding, and\
            also the argument index in the cost function.
        The value of this dictionary is the optimized value for the variable.
        """
        return self._result_values

    @result_values.setter
    def result_values(self, value):
        self._result_values = value

    @property
    def min_cost(self) -> float:
        """
        Minimum cost found
        """
        return self._min_cost

    @min_cost.setter
    def min_cost(self, value: float):
        self._min_cost = value

    @property
    def min_cost_per_generation(self) -> List[float]:
        """
        Minimal costs for each generation
        """
        return self._min_cost_per_generation

    @min_cost_per_generation.setter
    def min_cost_per_generation(self, value: List[float]):
        self._min_cost_per_generation = value

    @property
    def number_of_iterations(self) -> float:
        """
        Number of iterations (generations)
        """
        return self._number_of_iterations

    @number_of_iterations.setter
    def number_of_iterations(self, value: float):
        self._number_of_iterations = value

    @property
    def success(self) -> bool:
        """
        Indicates if genetic algorithm optimization succeeded
        """
        return self._success

    @success.setter
    def success(self, value: bool):
        self._success = value

    @property
    def messages(self):
        """
        Messages from the optimization
        """
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    @property
    def message(self) -> str:
        """
        Messages from the optimization joined into one string
        """
        return self._get_message()

    @property
    def initial_population(self) -> Population:
        return self._initial_population

    @initial_population.setter
    def initial_population(self, value):
        self._initial_population = value

    def _get_message(self):
        return ga_strings.get_results_message(self)
