import math
from typing import List

from gadapt.ga_model.candidate_solution import CandidateSolution
from gadapt.operations.cost_finding.elitism_cost_finder import ElitismCostFinder
from gadapt.utils.constraint_handling import ConstraintHandler, parse_pair


class ConstraintHandlingCostFinder(ElitismCostFinder):
    """
    Cost finder for constraint_handling: the cost function returns (objective, violation). Each generation it
    (1) evaluates the new candidate solutions, (2) updates the technique's parameters from the completed history,
    (3) recomputes the scalar cost of ALL candidate solutions and the previous generation's minimal and average
    cost under the current parameters (so improvement checks compare like with like), and only then (4) sorts by the
    technique's key and keeps the best ones. It also tracks the best evaluated solution of the run: the feasible one
    (violation 0) with the smallest objective, otherwise the one with the smallest violation.
    """

    def __init__(self, handler: ConstraintHandler, number_of_generations: int = -1):
        super().__init__()
        self.handler = handler
        self.number_of_generations = number_of_generations
        self._previous_best = None
        self.best = None  # (objective, violation, values) of the best evaluated solution of the run

    def _execute_function(self, cost_function, c: CandidateSolution):
        sorted_variable_values = list(sorted(c, key=lambda vv: vv.decision_variable.variable_id))
        values = [a.value for a in sorted_variable_values]
        try:
            c.objective_value, c.violation_value = parse_pair(cost_function(values))
            c.succ = True
        except Exception as ex:
            print(ex)
            c.objective_value, c.violation_value = None, math.inf
            c.succ = False
            return
        if self._better_for_report(c.objective_value, c.violation_value):
            self.best = (c.objective_value, c.violation_value,
                         {vv.decision_variable.variable_id: vv.value for vv in sorted_variable_values})

    def _better_for_report(self, objective, violation):
        if self.best is None:
            return True
        best_objective, best_violation, _ = self.best
        if violation == 0 or best_violation == 0:
            return violation == 0 and (best_violation != 0 or objective < best_objective)
        return violation < best_violation

    def _progress(self) -> float:
        """Elapsed share of the run (epsilon schedule); 0 without a generation limit."""
        if self.number_of_generations is None or self.number_of_generations <= 0:
            return 0.0
        return min(1.0, self.population.population_generation / self.number_of_generations)

    def _scalar_costs(self, candidates):
        finite = [self.handler.cost(c.objective_value, c.violation_value) for c in candidates
                  if c.objective_value is not None]
        failure_cost = max(finite) if finite else None
        return [self.handler.cost(c.objective_value, c.violation_value, failure_cost) for c in candidates]

    def _find_costs_for_population(self):
        if self.population is None:
            raise Exception("population must not be null!")
        incumbents = [c for c in self.population if not math.isnan(c.cost_value) and not (
            c.is_immigrant and c.population_generation == self.population.population_generation)]
        for c in self.population:
            if math.isnan(c.cost_value) or (
                c.is_immigrant and c.population_generation == self.population.population_generation
            ):
                self._execute_function(self.population.options.cost_function, c)
        if not any(getattr(c, "_succ", False) for c in self.population):
            raise ValueError("All evaluated candidate costs were invalid or nonfinite")
        pairs = [(c.objective_value, c.violation_value) for c in self.population]
        self.handler.start_generation(self._previous_best, pairs, self._progress())
        for c, cost in zip(self.population, self._scalar_costs(list(self.population))):
            c.cost_value = cost
        if incumbents:
            # the previous generation's references under the current parameters (adaptive penalty, epsilon)
            kept = sorted(incumbents, key=lambda c: self.handler.key(c.objective_value, c.violation_value))
            costs = [c.cost_value for c in kept]
            self.population.previous_min_cost = costs[0]
            n = max(1, self.population.options.keep_number - self.population.options.immigration_number)
            without_immigrants = costs[:n]
            self.population.previous_avg_cost = sum(without_immigrants) / len(without_immigrants)
        better: List[CandidateSolution] = sorted(
            self.population, key=lambda c: self.handler.key(c.objective_value, c.violation_value))
        better = better[: self.population.options.keep_number]
        self.population.best_individual = better[0]
        self.population.min_cost = better[0].cost_value
        without_immigrants = better[: self.population.options.keep_number - self.population.options.immigration_number]
        self.population.avg_cost = sum(c.cost_value for c in without_immigrants) / len(without_immigrants)
        self._log_population()
        self.population.clear_and_add_candidate_solutions(better)
        best = self.population.best_individual
        self._previous_best = (best.objective_value, best.violation_value)
