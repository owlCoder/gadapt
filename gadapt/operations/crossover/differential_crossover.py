import math
import random
import sys
from decimal import Decimal

from gadapt.ga_model.candidate_solution import CandidateSolution

from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.operations.candidate_solution_update.base_candidate_solution_updater import (
    BaseCandidateSolutionUpdater,
)
from gadapt.operations.crossover.base_crossover_probability_determinator import BaseCrossoverProbabilityDeterminator
from gadapt.operations.mutation.candidate_solution_mutation.base_decision_variable_mutation_selector import BaseDecisionVariableMutationSelector


class DifferentialCrossover(BaseCrossover):
    """
    Differential crossover (opt-in, crossover="differential").

    Each offspring is a parent plus a scaled difference of two other members of the population, applied to ALL decision
    variables together with the same scale factor (dithered in [0.5, 1.0] per offspring, as in differential evolution):
    offspring1 = mother + F1 * (a - b), offspring2 = father + F2 * (c - d), where a, b, c, d are distinct random members
    that are neither the mother nor the father. The proposed (unbounded) step is equivariant under rotations of the
    coordinate system, Q(m + F(a - b)) = Qm + F(Qa - Qb); unlike blending and uniform crossover it does not act on every
    decision variable separately. Reflection into the variable range, snapping to the grid, and the mutation operators
    are still coordinate-wise, so the whole algorithm is not rotation invariant.
    The crossover probability applies to the pair and is a single Bernoulli trial: with that probability the pair is
    combined, otherwise the offspring copy the parents (the probability is not raised until a crossover happens).
    If the population has fewer than four other members, the offspring are interpolated between the parents.
    """

    F_MIN = 0.5
    F_MAX = 1.0

    def __init__(self, candidate_solution_updater: BaseCandidateSolutionUpdater, mutator: BaseDecisionVariableMutationSelector, crossover_rate_determinator: BaseCrossoverProbabilityDeterminator):
        super(DifferentialCrossover, self).__init__(candidate_solution_updater, mutator, crossover_rate_determinator)
        self._population = None

    def _mate_pair(self, mother, father, population):
        """Like BaseCrossover._mate_pair, but the crossover probability is a single Bernoulli trial per pair."""
        self._population = population
        if len(mother) != len(father):
            raise Exception("Mother and father must have the same number of decision variables!")
        self._mother = mother
        self._father = father
        self._offspring1 = CandidateSolution(population.population_generation)
        self._offspring2 = CandidateSolution(population.population_generation)
        c_o_p = self._get_crossover_probability(population)
        if math.isnan(c_o_p):
            raise Exception("Crossover probability is not a number!")
        self._cross_genetic_material(c_o_p)
        self._offspring1.mother_id = self._mother.candidate_solution_id
        self._offspring2.mother_id = self._mother.candidate_solution_id
        self._offspring1.father_id = self._father.candidate_solution_id
        self._offspring2.father_id = self._father.candidate_solution_id
        self._all_decision_variables_crossed()
        self._increase_generation()
        return self._offspring1, self._offspring2

    def _combine(self):
        raise NotImplementedError("DifferentialCrossover combines whole candidate solutions")

    @staticmethod
    def _fit(decision_variable, value):
        low, high = decision_variable.min_value, decision_variable.max_value
        if high > low:
            span = high - low
            # reflect into [low, high]
            value = (value - low) % (2 * span)
            value = low + (value if value <= span else 2 * span - value)
        else:
            value = low
        step = getattr(decision_variable, "step", None)
        if step is not None and step > 0 and step > sys.float_info.min:
            k_max = math.floor((high - low) / step + 1e-9)
            k = min(max(int(round((value - low) / step)), 0), k_max)
            value = low + k * step
            decimals = max(0, -Decimal(repr(step)).normalize().as_tuple().exponent, -Decimal(repr(low)).normalize().as_tuple().exponent)
            value = round(value, decimals)
        return value

    def _cross_genetic_material(self, crossover_prob: float):
        self._candidate_solution_updater.candidate_solution_start_update()
        n = len(self._father)
        crossed = random.random() <= crossover_prob
        shifts1 = shifts2 = None
        if crossed:
            pool = [c for c in self._population.candidate_solutions
                    if len(c) == n and c is not self._mother and c is not self._father]
            if len(pool) >= 4:
                a, b, c, d = random.sample(pool, 4)
                f1 = random.uniform(self.F_MIN, self.F_MAX)
                f2 = random.uniform(self.F_MIN, self.F_MAX)
                shifts1 = [f1 * (a[i].value - b[i].value) for i in range(n)]
                shifts2 = [f2 * (c[i].value - d[i].value) for i in range(n)]
            else:  # too small a population: interpolate between the parents (F <= 1 never goes beyond them)
                f1 = random.uniform(self.F_MIN, self.F_MAX)
                shifts1 = [f1 * (self._father[i].value - self._mother[i].value) for i in range(n)]
                shifts2 = [-s for s in shifts1]
        for i in range(n):
            self._current_decision_variable_number = i
            self._mother_variable_value, self._father_variable_value = self._get_mother_father_variable_value()
            decision_variable = self._mother_variable_value.decision_variable
            self._decision_variable_crossed()
            if crossed:
                var1 = self._fit(decision_variable, self._mother_variable_value.value + shifts1[i])
                var2 = self._fit(decision_variable, self._father_variable_value.value + shifts2[i])
            else:
                var1, var2 = self._mother_variable_value.value, self._father_variable_value.value
            self._offspring1.add_variable_value(decision_variable, var1)
            self._offspring2.add_variable_value(decision_variable, var2)
        return crossed
