from typing import List, Tuple, Optional

import gadapt.ga_model.message_levels as message_levels
from gadapt.ga_model.candidate_solution import CandidateSolution
from gadapt.adapters.ga_logging.logging_settings import init_logging
from gadapt.factory.ga_factory import BaseGAFactory
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.ga_results import GAResults
from gadapt.ga_model.population import Population


class GAExecutor:
    """
    Executor for the genetic algorithm

    Args:
        ga_options (GAOptions): Options for GA execution
        factory (GAFactory): Factory for objects creation
    """

    def __init__(self, ga_options: GAOptions, factory: BaseGAFactory) -> None:
        self.population: Optional[Population] = None
        if ga_options is not None:
            self.ga_options = ga_options
        self.factory = factory
        self.candidate_solution_mutator = self.factory.get_decision_variable_mutation_selector()
        self.population_mutator = self.factory.get_candidate_solution_mutation_selector()
        self.exit_checker = self.factory.get_exit_checker()
        self.cost_finder = self.factory.get_cost_finder()
        self.population_immigrator = self.factory.get_population_immigrator()
        self.candidate_solution_immigrator = self.factory.get_candidate_solution_immigrator()
        self.selector = self.factory.get_parent_selector()
        self.crossover = self.factory.get_crossover()
        self.decision_variable_updater = self.factory.get_decision_variable_updater()
        self.population_updater = self.factory.get_population_updater()
        self.candidate_solution_updater = self.factory.get_candidate_solution_updater()
        self.decision_variable_mutator = self.factory.get_decision_variable_mutator()
        self.ga_options.operator_credit_controller = (
            self.decision_variable_mutator if hasattr(self.decision_variable_mutator, "begin_generation") else None
        )
        self.initial_population: Optional[Population] = None

    def execute(self) -> GAResults:
        """
        Executes the genetic algorithm
        """
        self.population = Population(self.ga_options)
        self.ga_options.cost_diversity_coefficient_function = lambda: self.population.get_relative_cost_diversity_coefficient()
        self.ga_options.stagnation_generations_function = lambda: self.population.generations_without_improvement
        if self.population is None:
            raise Exception("population object is None!")
        results = GAResults()
        results.initial_population = self.population.clone()
        try:
            init_logging(self.ga_options.logging)
        except Exception as ex:
            results.messages.append(
                (
                    message_levels.WARNING,
                    "Logging failed. Error message: {exc}".format(exc=str(ex)),
                )
            )
            self.ga_options.logging = False
        try:
            self.find_costs()
            self.candidate_solution_updater.cost_diversity_in_initial_population = (
                self.population.absolute_cost_diversity_in_first_population)
            while not self.exit():
                self.immigrate()
                self.mate()
                self.mutate()
                self.find_costs()
            if self.population.timeout_expired:
                results.messages.append((message_levels.WARNING, "Timeout expired!"))
            best_individual = self.population.best_individual
            results.min_cost = self.population.min_cost
            results.number_of_iterations = self.population.population_generation
            results.min_cost_per_generation = self.population.min_cost_per_generation
            for g in best_individual:
                results.result_values[g.decision_variable.variable_id] = g.value
        except Exception as ex:
            results.success = False
            results.messages.append((message_levels.ERROR, str(ex)))
        if self.ga_options.operator_credit_controller is not None:
            results.operator_credit_summary = self.ga_options.operator_credit_controller.summary()
        return results

    def exit(self) -> bool:
        """
        Check exit from the GA
        """
        if self.population is None:
            raise Exception("population object must not be None!")
        self.population.population_generation += 1
        return self.exit_checker.check(self.population)

    def find_costs(self):
        """
        Finds costs for candidate solutions
        """
        self.population.previous_avg_cost = self.population.avg_cost
        self.population.previous_min_cost = self.population.min_cost
        self.cost_finder.find_costs(self.population)
        self.population.update_generations_without_improvement()
        self.decision_variable_updater.update_decision_variables(self.population)
        self.population_updater.update_population(self.population)

    def immigrate(self):
        """
        Immigrates new candidate solutions
        """
        self.population_immigrator.immigrate(self.population)

    def mate(self):
        """
        Mates candidate solutions
        """
        candidate_solution_pairs = self.select_mates()
        self.crossover.mate(candidate_solution_pairs, self.population)

    def mutate(self):
        """
        Mutates candidate solutions in the population
        """
        if self.ga_options.operator_credit_controller is not None:
            self.ga_options.operator_credit_controller.begin_generation(self.population)
        self.population_mutator.mutate(self.population)

    def select_mates(self) -> List[Tuple[CandidateSolution, CandidateSolution]]:
        """
        Selects mates for pairing
        """
        return self.selector.select_mates(self.population)
