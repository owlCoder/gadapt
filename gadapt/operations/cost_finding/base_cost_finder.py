import sys
import math
from numbers import Real
import traceback
from abc import ABC, abstractmethod
from typing import Optional

from gadapt.ga_model.population import Population
from gadapt.ga_model.candidate_solution import CandidateSolution


class BaseCostFinder(ABC):
    """
    Base class for cost finding
    """

    def __init__(self):
        super().__init__()
        self.population: Optional[Population] = None

    def _execute_function(self, cost_function, c: CandidateSolution):
        """
        Executes the cost function

        Args:
            cost_function: Function to execute
            c (CandidateSolution): The candidate solution with
            decision variables containing values for the function execution.
        """
        sorted_variable_values = list(sorted(c, key=lambda vv: vv.decision_variable.variable_id))
        try:
            variable_values = [a.value for a in sorted_variable_values]
            value = cost_function(variable_values)
            if not isinstance(value, Real) or not math.isfinite(float(value)):
                raise ValueError("Cost function must return a finite real number")
            c.cost_value = float(value)
            c.succ = True
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            c.succ = False
            c.cost_value = sys.float_info.max

    @abstractmethod
    def _find_costs_for_population(self):
        pass

    def find_costs(self, population):
        """
        Finds costs for the population

        Args:
            population (Population): The population to find costs for each candidate solution
        """
        self.population = population
        self._find_costs_for_population()
        self.population.min_cost_per_generation.append(self.population.min_cost)
