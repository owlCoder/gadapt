import sys
import math
from numbers import Real
import traceback
from abc import ABC, abstractmethod
from typing import Optional

from gadapt.execution.reliability import EvaluationBudgetExhausted
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
        except EvaluationBudgetExhausted:
            raise
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            c.succ = False
            c.cost_value = sys.float_info.max

    def _restore_monitored_incumbent(self):
        """Rescue one *already evaluated* candidate when the entire cohort fails.

        Validation probes (or an earlier generation) may have produced a valid
        value. Restoring its exact cached objective never calls the user function.
        This is opt-in and cannot hide a run with no valid evaluation at all.
        """
        monitor = getattr(self.population.options, "reliability_monitor", None)
        if monitor is None or monitor.best is None or not self.population.candidate_solutions:
            return False
        objective, violation, values = monitor.best
        variables = sorted(self.population.options.decision_variables, key=lambda v: v.variable_id)
        if len(variables) != len(values):
            return False

        candidate = CandidateSolution(self.population.population_generation)
        candidate.candidate_solution_generation = 1
        for variable, value in zip(variables, values):
            candidate.add_variable_value(variable, value)
        candidate.succ = True
        candidate.objective_value = objective
        candidate.violation_value = violation
        # Constrained cost finders re-compute the scalar after updating the
        # handler; objective is only a temporary, finite placeholder.
        candidate.cost_value = objective
        candidate.candidate_solution_id = self.population.last_candidate_solution_id
        self.population.last_candidate_solution_id += 1
        self.population.candidate_solutions[-1] = candidate
        self.population.register_candidate_solution(candidate)
        return True

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
