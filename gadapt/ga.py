"""
The main genetic algorithm module
"""

import inspect
import sys
import warnings
from typing import List, Optional, Callable

import gadapt.ga_model.definitions as definitions
import gadapt.utils.ga_utils as ga_utils
from gadapt.adapters.validation.common_options_validator import CommonOptionsValidator
from gadapt.execution.ga_executor import GAExecutor
from gadapt.factory.ga_base_factory import BaseGAFactory
from gadapt.factory.ga_factory import GAFactory
from gadapt.ga_model.decision_variable import DecisionVariable
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.ga_results import GAResults
import copy

# Parameter names used before allele/gene/chromosome/cross diversity were renamed to
# variable value/decision variable/candidate solution/variable columnar diversity.
# They are still accepted by the GA constructor and as GA properties, but emit a
# DeprecationWarning.
DEPRECATED_PARAMETER_NAMES = {
    "number_of_mutation_chromosomes": "number_of_mutation_candidate_solutions",
    "percentage_of_mutation_chromosomes": "percentage_of_mutation_candidate_solutions",
    "parent_diversity_mutation_chromosome_sampling": "parent_diversity_mutation_candidate_solution_sampling",
    "chromosome_mutation": "candidate_solution_mutation",
    "gene_mutation": "decision_variable_mutation",
    "number_of_mutation_genes": "number_of_mutation_decision_variables",
    "percentage_of_mutation_genes": "percentage_of_mutation_decision_variables",
    "cross_diversity_mutation_gene_sampling": "variable_columnar_diversity_mutation_decision_variable_sampling",
    "cross_diversity_mutation_decision_variable_sampling": "variable_columnar_diversity_mutation_decision_variable_sampling",
}

# Option values (the comma-separated tokens of population_mutation,
# candidate_solution_mutation, decision_variable_mutation and crossover) that were
# renamed. They are still accepted, but replaced by the new value with a DeprecationWarning.
DEPRECATED_OPTION_VALUES = {
    "cross_diversity": definitions.VARIABLE_COLUMNAR_DIVERSITY,
}


def _warn_deprecated(message: str) -> None:
    # Point the warning at the first frame outside this module (the user's code),
    # whether it was reached through the constructor, a setter or an alias property.
    level, frame = 2, sys._getframe(1)
    while frame is not None and frame.f_globals.get("__name__") == __name__:
        frame, level = frame.f_back, level + 1
    warnings.warn(message, DeprecationWarning, stacklevel=level)


def _warn_deprecated_name(old_name: str) -> None:
    _warn_deprecated(f"'{old_name}' is deprecated, use '{DEPRECATED_PARAMETER_NAMES[old_name]}' instead")


def _migrate_deprecated_values(value, parameter_name: str):
    """
    Replaces deprecated tokens in a comma-separated option string with their current names.
    """
    if not isinstance(value, str):
        return value
    tokens = value.split(definitions.PARAM_SEPARATOR)
    for i, token in enumerate(tokens):
        new_token = DEPRECATED_OPTION_VALUES.get(token)
        if new_token is not None:
            _warn_deprecated(
                f"The value '{token}' of '{parameter_name}' is deprecated, use '{new_token}' instead"
            )
            tokens[i] = new_token
    return definitions.PARAM_SEPARATOR.join(tokens)


class GA:
    """
    The main genetic algorithm class
    """

    def __init__(
        self,
        cost_function=None,
        population_size=32,
        keep_elitism_percentage=50,
        number_of_crossover_parents=-1,
        exit_check=definitions.AVG_COST,
        exit_function: Callable = None,
        requested_cost=sys.float_info.max,
        number_of_generations=-1,
        max_attempt_no=2,
        parent_selection=definitions.ROULETTE_WHEEL,
        crossover=definitions.BLENDING,
        population_mutation="{0}{1}{2}{3}{4}".format(
            definitions.COST_DIVERSITY,
            definitions.PARAM_SEPARATOR,
            definitions.VARIABLE_COLUMNAR_DIVERSITY,
            definitions.PARAM_SEPARATOR,
            definitions.PARENT_DIVERSITY,
        ),
        number_of_mutation_candidate_solutions=-1,
        percentage_of_mutation_candidate_solutions=50.0,
        parent_diversity_mutation_candidate_solution_sampling=definitions.ROULETTE_WHEEL,
        must_mutate_for_same_parents=True,
        candidate_solution_mutation=f"{definitions.VARIABLE_COLUMNAR_DIVERSITY}{definitions.PARAM_SEPARATOR}{definitions.RANDOM}",
        decision_variable_mutation=f"{definitions.VARIABLE_COLUMNAR_DIVERSITY}{definitions.PARAM_SEPARATOR}{definitions.RANDOM}",
        number_of_mutation_decision_variables=-1,
        percentage_of_mutation_decision_variables=20.0,
        variable_columnar_diversity_mutation_decision_variable_sampling=definitions.ROULETTE_WHEEL,
        crossover_probability=0.5,
        crossover_min_probability=0.5,
        crossover_max_probability=1.0,
        immigration_number=0,
        ensure_unique_individuals: Optional[bool] = None,
        normal_distribution_mutation_max_std_dev: float = 0.6,
        normal_distribution_mutation_min_std_dev: float = 0.001,
        logging=False,
        timeout=600,
        factory: Optional[BaseGAFactory] = None,
        normal_distribution_mutation_min_std_dev_decay_generations: Optional[float] = None,
        cost_diversity_metric: str = "log_relative",
        mutation_operator_policy: str = "legacy",
        mutation_operator_credit: str = "objective",
        mutation_credit_assignment: str = "offspring",
        mutation_evaluation_counter: Optional[Callable] = None,
        mutation_violation_function: Optional[Callable] = None,
        mutation_scenario_count: Optional[int] = None,
        adaptive_immigration_patience: Optional[int] = None,
        adaptive_immigration_percentage: float = 20.0,
        adaptive_immigration_diversity_threshold: float = 0.25,
        **deprecated_kwargs,
    ) -> None:
        """
        The constructor of the GA class accepts all parameters required to
        create an instance of the GA class. It validates such parameters.

        Args:
            cost_function: Custom function for the cost calculation (fitness).
            The optimisation
            goal is minimising the output of the cost function.
                cost_function must be the function with one argument - a dictionary of
                values, where the key is an index (the ordinal of adding parameters)
                and the key is the parameter's value to be optimised.

                When adding parameters, there should be as
                many parameters as the function uses. The
                cost_function is the only mandatory parameter.

            population_size: Number of candidate solutions in the population.

            exit_check: A criteria for the exit for the genetic algorithm

            exit_function: A function that forces GA exit if returns True

            requested_cost: This parameter only takes place when exit_check
            has value “requested”. It determines the requested value
            which causes the exit from the genetic algorithm

            number_of_generations: This parameter only takes place when exit_check
            has value “generations”. It determines the number of generations
            after which the genetic algorithm exits

            max_attempt_no: This parameter only takes place when exit_check
            has value “avg_cost” or “min_cost”. It determines the number of
            generations in which there is no improvement in the average/minimal cost.

            parent_selection: The sampling algorithm in parent selection.

            population_mutation: A type of mutation for the entire population.

                Based on the value of this parameter, the number of mutation
                candidate solutions can be determined, along with how
                candidate solutions for the mutation will be selected.

            number_of_mutation_candidate_solutions: The number of
            mutation candidate solutions in the population.

                In case it's value is equal to or higher than 0,
                it overrides percentage_of_mutation_candidate_solutions.

                This value is the upper bound - the actual
                number of mutated candidate solutions
                can vary from 1 to number_of_mutation_candidate_solutions.

            percentage_of_mutation_candidate_solutions: The percentage of mutated candidate solutions
            in the population.
                This value is applied to the population_size value and rounded to an
                integer value, giving the number of mutation candidate solutions.

                For example, if population_size has a value of 32,
                and percentage_of_mutation_candidate_solutions has a value of
                10, the number of mutation candidate solutions will be 3.

                The calculated value is an upper bound - the actual
                number of mutated candidate solutions can vary from 1 to the calculated value.

                percentage_of_mutation_candidate_solutions only applies if
                number_of_mutation_candidate_solutions does not have a valid
                integer value equal to or higher than 0.

            parent_diversity_mutation_candidate_solution_sampling: The
            sampling algorithm for mutating candidate solutions when population_mutation
            contains value “parent_diversity”.
                It only applies when population_mutation has value
                “parent_diversity”. It determines the way how candidate solutions are to
                be selected based on the diversity of their parents.

            must_mutate_for_same_parents: Indicates if completely the same
            parents must influence mutation for their children.
                In other words, each child will be mutated if it has
                parents with a diversity value of 0.

                If must_mutate_for_same_parents has the value True, the
                number of mutated candidate solutions can outreach value
                determined by number_of_mutation_candidate_solutions or
                percentage_of_mutation_candidate_solutions

            candidate_solution_mutation: The type of mutation of decision variables in candidate solutions.

            decision_variable_mutation: The type of assigning values to decision variables in the mutation

            number_of_mutation_decision_variables: The number of mutated decision variables in each candidate solution.
                In case it's value is equal to or higher than 0, it overrides
                percentage_of_mutation_decision_variables.

                This value is the upper bound - the number of mutated decision variables
                can vary from 1 to number_of_mutation_decision_variables.

            percentage_of_mutation_decision_variables: The percentage of
            mutated decision variables in each candidate solution.
                It applies to the candidate solution size
                (number of decision variables in each candidate solution), and
                the calculated value rounds to an integer value.

                The calculated value is the upper bound - the actual number of
                mutated decision variables can vary from 1 to the calculated value.

                percentage_of_mutation_decision_variables only applies if
                number_of_mutation_decision_variables does not have a valid
                integer value equal to or higher than 0.

            variable_columnar_diversity_mutation_decision_variable_sampling: The sampling algorithm for
            mutating candidate solutions when candidate_solution_mutation has value “variable_columnar_diversity”.
                It only applies when candidate_solution_mutation has value
                “variable_columnar_diversity” . It determines the way how decision variables
                are to be selected based on the variable-columnar-diversity.
            ensure_unique_individuals: If this parameter has a True value, the genetic algorithm will ensure that all individuals in the population are unique. This means that no two individuals will have the same set of decision variables, promoting diversity within the population and potentially leading to better optimization results.
                If it is None (default), uniqueness is ensured when all variables have a step (values are taken from a grid, so duplicates are likely), and it is not ensured when any variable is continuous (no step), since identical individuals are then practically impossible.
            immigration_number: Refers to the “Random Immigrants”
            concepts. This strategy introduces a certain number of
            individuals into the population during the evolution process.
                These new individuals are generated randomly
                and injected into the population.

            logging: If this parameter has a True value, the log file
            will be created in the current working directory.
            The log file contains the flow of genetic algorithm execution,
            along with values of candidate solutions, decision variables and cost
            functions in each generation

            timeout: A number of seconds after which the genetic algorithm
            optimisation will exit, regardless of whether
            exit_check criteria is reached.

            factory: Factory for creating object

            normal_distribution_mutation_min_std_dev: The lower bound of the standard
                deviation (relative to the range of the decision variable) of the normal
                distribution mutation. A lower bound is what limits the fine adjustments at the
                end of the optimization. For continuous variables, 1e-4 is often better than the
                default. For discrete variables (with a step), it should not be below one step
                divided by the range of the variable.

            normal_distribution_mutation_max_std_dev: The upper bound of the standard
                deviation (relative to the range of the decision variable) of the normal
                distribution mutation.

            normal_distribution_mutation_min_std_dev_decay_generations: None (default)
                or a number of generations. If it is None, the lower bound of the standard
                deviation is constant. Otherwise, the lower bound is divided by 10 for every
                such number of consecutive generations in which the minimal cost does not improve
                (down to 1e-9), and it is restored when the minimal cost improves. Fine
                adjustments are then tried exactly when the progress stalls. For discrete
                variables, the lower bound never goes below one step. A good starting point is
                2.5, together with normal_distribution_mutation_min_std_dev of 1e-4.

            cost_diversity_metric: 'log_relative' (legacy default) or
                'affine_invariant' (experimental, scale/offset-invariant measure).
            adaptive_immigration_patience: None (disabled by default) or a
                positive number of stagnant generations between conditional
                population refreshes.
            adaptive_immigration_percentage: percentage of kept candidates
                to replace during an adaptive refresh (0-100, default 20).
            adaptive_immigration_diversity_threshold: refresh only when cost
                diversity coefficient is below this threshold (0-1).

            deprecated_kwargs: Previous names of the parameters (see
            DEPRECATED_PARAMETER_NAMES), e.g. number_of_mutation_chromosomes.
            They are still accepted, but emit a DeprecationWarning.
        """
        parameters = inspect.signature(GA.__init__).parameters
        arguments = locals()
        for old_name in deprecated_kwargs:
            new_name = DEPRECATED_PARAMETER_NAMES.get(old_name)
            if new_name is None:
                raise TypeError(f"GA.__init__() got an unexpected keyword argument '{old_name}'")
            if arguments[new_name] != parameters[new_name].default:
                raise TypeError(f"GA.__init__() got both '{old_name}' and its replacement '{new_name}'")
        self.cost_function = cost_function
        self.population_size = population_size
        self.keep_elitism_percentage = keep_elitism_percentage
        self.number_of_crossover_parents = number_of_crossover_parents
        self.exit_check = exit_check
        self.exit_function = exit_function
        self.requested_cost = requested_cost
        self.number_of_generations = number_of_generations
        self.max_attempt_no = max_attempt_no
        self.parent_selection = parent_selection
        self.crossover = crossover
        self.population_mutation = population_mutation
        self.must_mutate_for_same_parents = must_mutate_for_same_parents
        self.number_of_mutation_candidate_solutions = number_of_mutation_candidate_solutions
        self.percentage_of_mutation_candidate_solutions = percentage_of_mutation_candidate_solutions
        self.number_of_mutation_decision_variables = number_of_mutation_decision_variables
        self.percentage_of_mutation_decision_variables = percentage_of_mutation_decision_variables
        self.candidate_solution_mutation = candidate_solution_mutation
        self.decision_variable_mutation = decision_variable_mutation
        self.immigration_number = immigration_number
        self.crossover_probability = crossover_probability
        self.crossover_min_probability = crossover_min_probability
        self.crossover_max_probability = crossover_max_probability
        self.logging = logging
        self._decision_variables: List[DecisionVariable] = []
        self.variable_columnar_diversity_mutation_decision_variable_sampling = (
            variable_columnar_diversity_mutation_decision_variable_sampling
        )
        self.parent_diversity_mutation_candidate_solution_sampling = (
            parent_diversity_mutation_candidate_solution_sampling
        )
        self.ensure_unique_individuals = ensure_unique_individuals
        self.cost_diversity_metric = cost_diversity_metric
        if mutation_operator_policy not in ("legacy", "uniform", "ucb"):
            raise ValueError("mutation_operator_policy must be legacy/uniform/ucb")
        if mutation_operator_credit not in ("objective", "feasibility", "scenario_feasibility", "censored_verified_per_cost"):
            raise ValueError("mutation_operator_credit must be objective/feasibility/scenario_feasibility/censored_verified_per_cost")
        if mutation_operator_policy != "legacy" and mutation_operator_credit in ("feasibility", "scenario_feasibility", "censored_verified_per_cost") and not callable(mutation_violation_function):
            raise ValueError("feasibility credit needs mutation_violation_function")
        if mutation_operator_credit in ("scenario_feasibility", "censored_verified_per_cost"):
            if mutation_operator_policy == "legacy":
                raise ValueError("multi-scenario feasibility credit requires an active operator policy")
            if mutation_credit_assignment != "offspring":
                raise ValueError("multi-scenario feasibility credit currently supports offspring credit only")
            if type(mutation_scenario_count) is not int or mutation_scenario_count < 2:
                raise ValueError("multi-scenario feasibility credit requires mutation_scenario_count >= 2")
            if not callable(mutation_evaluation_counter):
                raise ValueError("multi-scenario feasibility credit requires a real physical evaluation counter")
        elif mutation_scenario_count is not None:
            raise ValueError("mutation_scenario_count is only valid for multi-scenario feasibility credit")
        if mutation_credit_assignment not in ("offspring", "paired"):
            raise ValueError("mutation_credit_assignment must be offspring/paired")
        if mutation_credit_assignment == "paired":
            if mutation_operator_policy == "legacy":
                raise ValueError("paired credit requires an active operator policy")
            if not callable(mutation_evaluation_counter):
                raise ValueError("paired credit needs mutation_evaluation_counter")
            if ensure_unique_individuals is not False:
                raise ValueError("paired credit requires ensure_unique_individuals=False")
            if number_of_mutation_decision_variables != 1:
                raise ValueError("paired credit requires number_of_mutation_decision_variables=1")
            if candidate_solution_mutation != "random":
                raise ValueError("paired credit requires candidate_solution_mutation='random'")
        self.mutation_credit_assignment = mutation_credit_assignment
        self.mutation_evaluation_counter = mutation_evaluation_counter
        self.mutation_operator_policy = mutation_operator_policy
        self.mutation_operator_credit = mutation_operator_credit
        self.mutation_violation_function = mutation_violation_function
        self.mutation_scenario_count = mutation_scenario_count
        if (adaptive_immigration_patience is not None and
                (type(adaptive_immigration_patience) is not int or
                 adaptive_immigration_patience < 1)):
            raise ValueError("adaptive_immigration_patience must be a positive int or None")
        if not (0.0 <= adaptive_immigration_percentage <= 100.0):
            raise ValueError("adaptive_immigration_percentage must be in [0, 100]")
        if not (0.0 <= adaptive_immigration_diversity_threshold <= 1.0):
            raise ValueError("adaptive_immigration_diversity_threshold must be in [0, 1]")
        self.adaptive_immigration_patience = adaptive_immigration_patience
        self.adaptive_immigration_percentage = float(adaptive_immigration_percentage)
        self.adaptive_immigration_diversity_threshold = float(adaptive_immigration_diversity_threshold)
        self.normal_distribution_mutation_max_std_dev = normal_distribution_mutation_max_std_dev
        self.normal_distribution_mutation_min_std_dev = normal_distribution_mutation_min_std_dev
        self.normal_distribution_mutation_min_std_dev_decay_generations = normal_distribution_mutation_min_std_dev_decay_generations
        self.timeout = timeout
        self._current_dv_id = 0
        self._factory = factory
        for old_name, value in deprecated_kwargs.items():
            _warn_deprecated_name(old_name)
            setattr(self, DEPRECATED_PARAMETER_NAMES[old_name], value)

    def execute(self) -> GAResults:
        """
        Executes genetic algorithm optimization base on the
        provided parameters and arguments.
        """
        validator = CommonOptionsValidator(self)
        validator.validate()
        if not validator.success:
            results = GAResults()
            results.success = False
            results.messages = validator.validation_messages
            return results
        ga_options = GAOptions(self.clone())
        factory: BaseGAFactory = self.get_factory()
        factory.initialize_factory(self, ga_options)
        return GAExecutor(ga_options, factory).execute()

    def get_factory(self) -> BaseGAFactory:
        if self._factory:
            return self._factory
        return GAFactory()

    @property
    def population_size(self) -> int:
        """
        Population size number
        """
        return self._population_size

    @population_size.setter
    def population_size(self, value: int):
        self._population_size = ga_utils.try_get_int(value)

    @property
    def keep_elitism_percentage(self) -> int:
        """
        Percentage number of candidate solutions to be kept in the population by the cost value
        """
        return self._keep_elitism_percentage

    @keep_elitism_percentage.setter
    def keep_elitism_percentage(self, value: int):
        self._keep_elitism_percentage = ga_utils.try_get_int(value)

    @property
    def number_of_crossover_parents(self) -> int:
        """
        Number of parents to be included in the mating pool
        """
        return self._number_of_crossover_parents

    @number_of_crossover_parents.setter
    def number_of_crossover_parents(self, value: int):
        self._number_of_crossover_parents = ga_utils.try_get_int(value)

    def add(
        self,
        min_value: float = -sys.float_info.max,
        max_value: float = sys.float_info.max,
        step: float = None,
    ):
        """
        Adds variables to be optimized.
        Args:
            min_value (float): lower bound of possible variable values
            max_value (float): upper bound of possible variable values
            step (float): the step that will be used in changing the
            variables values during the optimization
        """
        if (not isinstance(min_value, float) and not isinstance(min_value, int)) or (
            not isinstance(max_value, float) and not isinstance(max_value, int)
        ):
            raise Exception("min value, max value and step must be numerical values!")
        decision_variable = DecisionVariable(self._current_dv_id)
        decision_variable.min_value = min_value
        decision_variable.max_value = max_value
        decision_variable.step = step
        self._decision_variables.append(decision_variable)
        self._current_dv_id += 1

    @property
    def cost_function(self):
        """
        Custom function for the cost calculation (fitness). The optimisation goal
        is minimising the output of the cost function.
        cost_function must be the function with one argument -
        a dictionary of values, where the key is an index
        (the ordinal of adding parameters)
        and the key is the parameter's value to be optimised.
        When adding parameters, there should be as many parameters
        as the function uses. The cost_function is the
        only mandatory parameter.
        """
        return self._cost_function

    @cost_function.setter
    def cost_function(self, value):
        self._cost_function = value

    @property
    def number_of_mutation_decision_variables(self) -> int:
        """
        The number of mutated decision variables in each candidate solution.
        In case it's value is equal to or higher than 0, it overrides
        percentage_of_mutation_decision_variables.
        This value is the upper bound - the number of mutated decision variables
        can vary from 1 to number_of_mutation_decision_variables.
        """
        return self._number_of_mutation_decision_variables

    @number_of_mutation_decision_variables.setter
    def number_of_mutation_decision_variables(self, value: int):
        self._number_of_mutation_decision_variables = ga_utils.try_get_int(value)

    @property
    def percentage_of_mutation_decision_variables(self) -> float:
        """
        The percentage of mutated decision variables in each candidate solution.
        It applies to the candidate solution size (number of decision variables in each candidate solution),
        and the calculated value rounds to an integer value.
        The calculated value is the upper bound - the actual number of mutated
        decision variables can vary from 1 to the calculated value.
        percentage_of_mutation_decision_variables only applies if number_of_mutation_decision_variables
        does not have a valid integer value equal to or higher than 0.
        """
        return self._percentage_of_mutation_decision_variables

    @percentage_of_mutation_decision_variables.setter
    def percentage_of_mutation_decision_variables(self, value: float):
        self._percentage_of_mutation_decision_variables = ga_utils.try_get_float(value)

    @property
    def number_of_mutation_candidate_solutions(self) -> int:
        """
        The number of mutation candidate solutions in the population.
        In case it's value is equal to or higher than 0, it
        overrides percentage_of_mutation_candidate_solutions.
        This value is the upper bound - the actual number of
        mutated candidate solutions can vary from 1 to number_of_mutation_candidate_solutions.
        """
        return self._number_of_mutation_candidate_solutions

    @number_of_mutation_candidate_solutions.setter
    def number_of_mutation_candidate_solutions(self, value: int):
        self._number_of_mutation_candidate_solutions = ga_utils.try_get_int(value)

    @property
    def percentage_of_mutation_candidate_solutions(self) -> float:
        """
        The percentage of mutated candidate solutions in the population.

        This value is applied to the population_size value and
        rounded to an integer value, giving the number
        of mutation candidate solutions.

        For example, if population_size has a value of 32, and
        percentage_of_mutation_candidate_solutions has a value of 10,
        the number of mutation candidate solutions will be 3.

        The calculated value is an upper bound - the actual number of
        mutated candidate solutions can vary from 1 to the calculated value.
        percentage_of_mutation_candidate_solutions only applies
        if number_of_mutation_candidate_solutions
        does not have a valid integer value equal to or higher than 0.
        """
        return self._percentage_of_mutation_candidate_solutions

    @percentage_of_mutation_candidate_solutions.setter
    def percentage_of_mutation_candidate_solutions(self, value: float):
        self._percentage_of_mutation_candidate_solutions = ga_utils.try_get_float(value)

    @property
    def immigration_number(self) -> int:
        """
        Refers to the “Random Immigrants” concepts. This strategy introduces
        a certain number of individuals into the population
        during the evolution process.
        """
        return self._immigration_number

    @immigration_number.setter
    def immigration_number(self, value: int):
        self._immigration_number = ga_utils.try_get_int(value)

    @property
    def crossover_probability(self) -> float:

        return self._crossover_probability

    @crossover_probability.setter
    def crossover_probability(self, value: float):
        self._crossover_probability = ga_utils.try_get_float(value)

    @property
    def crossover_min_probability(self) -> float:

        return self._crossover_min_probability

    @property
    def crossover_max_probability(self) -> float:

        return self._crossover_max_probability

    @crossover_max_probability.setter
    def crossover_max_probability(self, value: float):
        self._crossover_max_probability = ga_utils.try_get_float(value)

    @crossover_min_probability.setter
    def crossover_min_probability(self, value: float):
        self._crossover_min_probability = ga_utils.try_get_float(value)

    @property
    def population_mutation(self) -> str:
        """
        A type of mutation for the entire population.

        Supported values:

        **"cost_diversity"** - It applies to the number of mutation candidate solutions.
        “cost_diversity” determines the number of mutated candidate solutions adaptively,
        using the diversity of costs in the population. Lower cost diversity
        means a higher number of mutated candidate solutions. The minimal value of
        mutated candidate solutions is 0, and the maximal value is determined by
        the value of number_of_mutation_candidate_solutions or
        percentage_of_mutation_candidate_solutions
        parameters. If population_mutation has a value other than
        “cost_diversity”, the number of mutation candidate solutions is a
        random value from 1 to number_of_mutation_candidate_solutions
        value (or to value determined by percentage_of_mutation_candidate_solutions value).
        “cost_diversity” means that the “parent_diversity” method is selected
        to select candidate solutions to be mutated. This method only determines
        the number of mutated candidate solutions, but not how
        candidate solutions are selected for the mutation.

        **"parent_diversity"** - It applies to the way how mutation
        candidate solutions will be selected. “parent_diversity” selects
        candidate solutions to be mutated using the diversity of their parents.
        The more similar parents (lower parent diversity) mean a higher
        probability of mutation for the child. Based on the calculated
        parent diversity, candidate solutions may be selected by one of the
        sampling methods, which is determined by the value of the
        parent_diversity_mutation_candidate_solution_sampling parameter.

        **"random"** - It applies to the number of mutation candidate solutions
        and to the way how mutation candidate solutions will be selected. “random”
        selects candidate solutions to be mutated randomly, and randomly
        determines the number of mutated candidate solutions (with the
        upper bound of number_of_mutation_candidate_solutions)
        """
        return self._population_mutation

    @population_mutation.setter
    def population_mutation(self, value: str):
        self._population_mutation = _migrate_deprecated_values(ga_utils.prepare_string(value), "population_mutation")

    @property
    def parent_diversity_mutation_candidate_solution_sampling(self) -> str:
        """
        The sampling algorithm for mutating candidate solutions when
        population_mutation contains value “parent_diversity”.
        It only applies when population_mutation has value
        “parent_diversity”. It determines the way how candidate solutions are
        to be selected based on the diversity of their parents.

        Supported values:

        **"roulette_wheel"** - The Roulette Wheel sampling algorithm
        (also known as “Weighted Random Pairing”). The probabilities
        assigned to the candidate solutions to be mutated are proportional
        to the similarity of their parents (inversely proportional
        to the parent diversity). A candidate solution with the lowest
        parent diversity has the greatest probability of
        mutation, while the candidate solution with the highest
        parent diversity has the lowest probability of mutation.

        **"tournament"** - The Tournament sampling algorithm.
        It randomly picks small subsets (groups) of candidate solutions,
        and candidate solutions with the lowest parent diversity (highest parent similarity)
        in subsets are chosen to be mutated. “tournament” can have an additional
        parameter separated from the “tournament” keyword by the comma.
        The other value represents a group size. For example, “tournament,8” means
        that the tournament mutation sampling algorithm is chosen, and
        each group contains up to 8 members. The default group size is 4.

        **"from_top_to_bottom"** - From Top To Bottom sampling
        algorithm starts at the top of the list and
        selects candidate solutions for mutation.

        **"random"** - Random selection algorithm uses a
        uniform random number generator to select
        candidate solutions for mutation. In this case,
        sampling for mutation will not depend
        on parent diversity.
        """
        return self._parent_diversity_mutation_candidate_solution_sampling

    @parent_diversity_mutation_candidate_solution_sampling.setter
    def parent_diversity_mutation_candidate_solution_sampling(self, value: str):
        self._parent_diversity_mutation_candidate_solution_sampling = ga_utils.prepare_string(
            value
        )

    @property
    def candidate_solution_mutation(self) -> str:
        """
        The type of mutation of decision variables in candidate solutions.

        Supported values:

        **"variable_columnar_diversity"** - Considers the diversity of decision variables of the same
        type in the population. Lower diversity can mean
        that this decision variable approaches some local
        minimums, and therefore such decision variables increase the
        chance for mutation. Based on the calculated
        variable-columnar-diversity, candidate solutions may be selected by
        one of the sampling methods, which is
        determined by the value of the
        variable_columnar_diversity_mutation_decision_variable_sampling parameter.

        **"random"** - Decision variables are randomly selected for the mutation
        """
        return self._candidate_solution_mutation

    @candidate_solution_mutation.setter
    def candidate_solution_mutation(self, value: str):
        self._candidate_solution_mutation = _migrate_deprecated_values(ga_utils.prepare_string(value), "candidate_solution_mutation")

    @property
    def decision_variable_mutation(self) -> str:
        """
        Way of assigning the value to the decision variable

        Supported values:

        **"normal_distribution"** - assigns normally distributed random number to the variable selected for mutation

        **"variable_columnar_diversity"** - assigns normally distributed random number to the variable selected
        for mutation, with standard deviation based on the variable-columnar-diversity coefficient

        **"cost_diversity"** - assigns normally distributed random number to the variable selected
        for mutation, with standard deviation based on the diversity of costs in the population.
        Higher cost diversity means a higher standard deviation.

        **"random"** - Random values are assigned to decision variables
        """
        return self._decision_variable_mutation

    @decision_variable_mutation.setter
    def decision_variable_mutation(self, value: str):
        self._decision_variable_mutation = _migrate_deprecated_values(ga_utils.prepare_string(value), "decision_variable_mutation")

    @property
    def variable_columnar_diversity_mutation_decision_variable_sampling(self) -> str:
        """
        The sampling algorithm for mutating candidate solutions when candidate_solution_mutation
        has value “variable_columnar_diversity”.
        It only applies when candidate_solution_mutation has value “variable_columnar_diversity” .
        It determines the way how decision variables are to be selected based on the variable-columnar-diversity.

        Supported values:

        **"roulette_wheel"** - The Roulette Wheel sampling algorithm
        (also known as “Weighted Random Pairing”). The probabilities
        assigned to the decision variables to be mutated are inversely
        proportional to their variable-columnar-diversity. A decision variable
        with the lowest variable-columnar-diversity has the greatest
        probability of mutation, while the decision variable with the
        highest variable-columnar-diversity has the lowest
        probability of mutation.

        **"tournament"** - The Tournament sampling algorithm. It randomly picks
        small subsets (groups) of decision variables, and decision variables with the lowest variable-columnar-diversity
        in subsets are chosen to be mutated. “tournament” can have
        an additional parameter separated from the “tournament”
        keyword by the comma. The other value represents a group size.
        For example, “tournament,3” means that the tournament
        mutation sampling algorithm is chosen, and each group
        contains up to 3 members. The default group size is 4.

        **"from_top_to_bottom"** - From Top To Bottom sampling
        algorithm starts at the top of the list and selects decision variables for mutation.

        **"random"** - Random sampling algorithm uses a
        uniform random number generator to select decision variables for mutation.
        In this case, sampling for the mutation will not
        depend on the variable-columnar-diversity of the decision variable.
        """
        return self._variable_columnar_diversity_mutation_decision_variable_sampling

    @variable_columnar_diversity_mutation_decision_variable_sampling.setter
    def variable_columnar_diversity_mutation_decision_variable_sampling(self, value: str):
        self._variable_columnar_diversity_mutation_decision_variable_sampling = ga_utils.prepare_string(value)

    @property
    def max_attempt_no(self) -> int:
        """
        This parameter only takes place when exit_check has value “avg_cost”
        or “min_cost”. It determines the number of generations
        in which there is no improvement in the average/minimal cost.
        """
        return self._max_attempt_no

    @max_attempt_no.setter
    def max_attempt_no(self, value: int):
        self._max_attempt_no = ga_utils.try_get_int(value)

    @property
    def exit_check(self) -> str:
        """
        A criteria for the exit for the genetic algorithm.

        Supported values:

        **"avg_cost"** - The optimisation exit is triggered when the
        average cost of the kept part of the population (see keep_elitism_percentage)
        is not improved in the specified number of generations

        **"min_cost"** - The optimisation exit is triggered when the minimal cost
        in the population is not improved in the specified number of generations

        **"requested"** - The optimisation exit is triggered when the
        requested value reached
        """
        return self._exit_check

    @exit_check.setter
    def exit_check(self, value: str):
        self._exit_check = ga_utils.prepare_string(value)

    @property
    def exit_function(self) -> Callable:
        return self._exit_function

    @exit_function.setter
    def exit_function(self, value: Callable):
        self._exit_function = value

    @property
    def number_of_generations(self) -> int:
        """
        This parameter only takes place when exit_check
        has value “generations”. It determines the number of generations
        after which the genetic algorithm exits
        """
        return self._number_of_generations

    @number_of_generations.setter
    def number_of_generations(self, value: int):
        self._number_of_generations = ga_utils.try_get_int(value)

    @property
    def parent_selection(self) -> str:
        """
        The sampling algorithm used for parent selection.

        Supported values:

        **"roulette_wheel"** - Roulette Wheel sampling algorithm
        (also known as “Weighted Random Pairing”).
        The probabilities assigned to the candidate solutions in the mating pool are
        inversely proportional to their cost. A candidate solution with the lowest
        cost has the greatest probability of mating, while the candidate solution
        with the highest cost has the lowest probability of mating.

        **"tournament"** - Tournament sampling algorithm. It randomly picks small
        subsets (groups) of candidate solutions from the mating pool, and candidate solutions
        with the lowest cost in subsets become a parent. “tournament”
        can have an additional parameter separated from the “tournament”
        keyword by the comma. The other value represents a group size.
        For example, “tournament,8” means that the tournament
        sampling algorithm for parent selection is chosen, and
        each group contains up to 8 members.
        The default group size is 4.

        **"from_top_to_bottom"** - From Top To Bottom sampling
        algorithm starts at the top of
        the list and pairs the candidate solutions two at a time until the top kept candidate solutions
        are selected for mating. Thus, the algorithm pairs odd rows with even rows.

        **"random"** - Random sampling algorithm uses a uniform random
        number generator to select candidate solutions.
        """
        return self._parent_selection

    @parent_selection.setter
    def parent_selection(self, value: str):
        self._parent_selection = ga_utils.prepare_string(value)

    @property
    def crossover(self) -> str:
        """
        The crossover algorithm

        Supported values:

        **"blending"** - combines variable values from the two parents into new variable values in offsprings.
        One value of the offspring variable comes from a combination of the two
        corresponding values of the parental decision variables

        **"uniform"** - Decision variables from parents' candidate solutions are combined in a uniform way.
        """
        return self._crossover

    @crossover.setter
    def crossover(self, value: str):
        self._crossover = _migrate_deprecated_values(ga_utils.prepare_string(value), "crossover")

    @property
    def requested_cost(self) -> float:
        """
        This parameter only takes place when exit_check has value “requested”.
        It determines the requested value which causes the
        exit from the genetic algorithm
        """
        return self._requested_cost

    @requested_cost.setter
    def requested_cost(self, value: float):
        self._requested_cost = ga_utils.try_get_float(value)

    @property
    def ensure_unique_individuals(self) -> Optional[bool]:
        return self._ensure_unique_individuals

    @ensure_unique_individuals.setter
    def ensure_unique_individuals(self, value: Optional[bool]):
        self._ensure_unique_individuals = ga_utils.try_get_bool(value)

    @property
    def cost_diversity_metric(self) -> str:
        return self._cost_diversity_metric

    @cost_diversity_metric.setter
    def cost_diversity_metric(self, value: str) -> None:
        if value not in ("log_relative", "affine_invariant"):
            raise ValueError(
                "cost_diversity_metric must be 'log_relative' or 'affine_invariant'"
            )
        self._cost_diversity_metric = value

    @property
    def normal_distribution_mutation_max_std_dev(self) -> float:
        return self._normal_distribution_mutation_max_std_dev

    @normal_distribution_mutation_max_std_dev.setter
    def normal_distribution_mutation_max_std_dev(self, value: float):
        self._normal_distribution_mutation_max_std_dev = ga_utils.try_get_float(value)

    @property
    def normal_distribution_mutation_min_std_dev(self) -> float:
        return self._normal_distribution_mutation_min_std_dev

    @normal_distribution_mutation_min_std_dev.setter
    def normal_distribution_mutation_min_std_dev(self, value: float):
        self._normal_distribution_mutation_min_std_dev = ga_utils.try_get_float(value)

    @property
    def normal_distribution_mutation_min_std_dev_decay_generations(self) -> Optional[float]:
        """
        None (default) or a number of generations. If it is None, the lower bound of the standard deviation
        of the normal distribution mutation (normal_distribution_mutation_min_std_dev) is constant.
        Otherwise, the lower bound is divided by 10 for every such number of consecutive generations without
        an improvement of the minimal cost (down to 1e-9), and restored when the minimal cost improves.
        For discrete variables, it never goes below one step.
        """
        return self._normal_distribution_mutation_min_std_dev_decay_generations

    @normal_distribution_mutation_min_std_dev_decay_generations.setter
    def normal_distribution_mutation_min_std_dev_decay_generations(self, value: Optional[float]):
        # a bool is kept as it is (float(True) would silently become 1.0), so that the validation rejects it
        self._normal_distribution_mutation_min_std_dev_decay_generations = (
            value if value is None or isinstance(value, bool) else ga_utils.try_get_float(value)
        )

    @property
    def logging(self) -> bool:
        return self._logging

    @logging.setter
    def logging(self, value: bool):
        """
        If this parameter has a True value, the log file will
        be created in the current working directory.
        The log file contains the flow of genetic algorithm execution,
        along with values of candidate solutions, decision variables and
        cost functions in each generation
        """
        self._logging = ga_utils.try_get_bool(value)

    @property
    def must_mutate_for_same_parents(self) -> bool:
        """
        Indicates if completely the same parents must influence
        mutation for their children.
        In other words, each child will be mutated if it has parents
        with a diversity value of 0.
        If must_mutate_for_same_parents has the value True, the number of
        mutated candidate solutions can outreach value determined
        by number_of_mutation_candidate_solutions
        or percentage_of_mutation_candidate_solutions
        """
        return self._must_mutate_for_same_parents

    @must_mutate_for_same_parents.setter
    def must_mutate_for_same_parents(self, value: bool):
        self._must_mutate_for_same_parents = ga_utils.try_get_bool(value)

    @property
    def timeout(self) -> int | str:
        """
        A number of seconds after which the genetic algorithm optimisation will\
            exit, regardless of whether exit_check criteria is reached.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: int | str) -> None:
        self._timeout = ga_utils.try_get_int(value)

    def clone(self):
        """Copy GA configuration without cloning external callback state.

        A bound cost function may point to an expensive/stateful simulator,
        database interface or objective-evaluation counter. Deep-copying
        such a bound method also deep-copies its owner, silently splitting
        the optimization from the original simulator.

        Deep-copy internal GA options and decision variables as before,
        but preserve the identities of the user-supplied callbacks.
        """
        new_instance = self.__class__.__new__(self.__class__)
        attributes = dict(self.__dict__)
        callbacks = {}
        for name in ("_cost_function", "_exit_function", "mutation_violation_function", "mutation_evaluation_counter"):
            if name in attributes:
                callbacks[name] = attributes.pop(name)
        new_instance.__dict__ = copy.deepcopy(attributes)
        new_instance.__dict__.update(callbacks)
        return new_instance


def _deprecated_alias(old_name: str) -> property:
    new_name = DEPRECATED_PARAMETER_NAMES[old_name]

    def getter(self):
        _warn_deprecated_name(old_name)
        return getattr(self, new_name)

    def setter(self, value):
        _warn_deprecated_name(old_name)
        setattr(self, new_name, value)

    return property(getter, setter, doc=f"Deprecated. Use {new_name}.")


for _old_name in DEPRECATED_PARAMETER_NAMES:
    setattr(GA, _old_name, _deprecated_alias(_old_name))
