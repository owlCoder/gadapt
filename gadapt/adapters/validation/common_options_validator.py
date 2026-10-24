import gadapt.ga_model.definitions as definitions
from gadapt.adapters.validation.base_options_validator import BaseOptionsValidator
from gadapt.utils.constraint_handling import parse_pair


class CommonOptionsValidator(BaseOptionsValidator):
    """
    Common class for options validation
    """

    def __init__(self, options) -> None:
        super().__init__(options)
        self._validation_messages = []

    def _validate_options(self):
        self.success &= self._check_nones_types_and_values()
        self.success &= self._check_decision_variables()
        self.success &= self._check_constraint_handling()
        self.success &= self._check_cost_function()

    def _check_decision_variables(self) -> bool:
        if self.options._decision_variables is None:
            return False
        rslt = True
        for v in self.options._decision_variables:
            if v.min_value is None or v.max_value is None:
                self._add_message(
                    "Min value and max value must not be\
                        None! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            elif (
                not (isinstance(v.min_value, float) or isinstance(v.min_value, int))
                or not (isinstance(v.max_value, float) or isinstance(v.max_value, int))
                or not (v.step is None or isinstance(v.step, float) or isinstance(v.step, int))
            ):
                self._add_message(
                    "Min value, max value and step must be float or int\
                        values! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            elif v.min_value > v.max_value:
                self._add_message(
                    "Min value must be less or equal than max value!\
                        (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            elif v.step is not None and v.step <= 0.0:
                self._add_message(
                    "Step must be positive float value! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            elif v.min_value + (v.step if v.step is not None else 0) > v.max_value:
                self._add_message(
                    "Invalid step value! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            if v.decimal_places < -1:
                self._add_message(
                    "Invalid number of decimal places! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
        return rslt

    def _check_cost_function(self):
        if self.options.cost_function is None:
            self._add_message("Cost Function must not be None!")
            return False
        elif not callable(self.options.cost_function):
            self._add_message("Cost Function must be callable!")
            return False
        if not self.options.probe_cost_function:
            return True
        argsmin = []
        argsmax = []
        for v in self.options._decision_variables:
            argsmin.append(v.min_value)
            argsmax.append(v.max_value)
        try:
            func_result_min = self.options.cost_function(argsmin)
            func_result_max = self.options.cost_function(argsmax)
            if getattr(self.options, "constraint_handling", None) is not None:
                try:
                    parse_pair(func_result_min)
                    parse_pair(func_result_max)
                    pairs = True
                except ValueError:
                    pairs = False
            elif not isinstance(func_result_min, float) or not isinstance(
                func_result_max, float
            ):
                self._add_message("The function must return float value!")
                return False
        except KeyError:
            self._add_message(
                "Inadequate number of parameters for the passed function!"
            )
            return False
        except Exception as ex:
            self._add_message(
                "An exception raised on the function call: {exc}".format(exc=str(ex))
            )
            return False
        if getattr(self.options, "constraint_handling", None) is not None and not pairs:
            self._add_message("With constraint_handling, the function must return (objective, violation)!")
            return False
        return True

    def _check_constraint_handling(self) -> bool:
        technique = getattr(self.options, "constraint_handling", None)
        if technique is None:
            return True
        if self.options.mutation_operator_policy != "legacy":
            self._add_message("constraint_handling cannot be combined with mutation_operator_policy!")
            return False
        if technique == "epsilon" and not (isinstance(self.options.number_of_generations, int)
                                           and self.options.number_of_generations > 0):
            self._add_message("constraint_handling='epsilon' needs number_of_generations > 0!")
            return False
        return True

    def _check_nones_types_and_values(self) -> bool:
        rslt = True
        population_size = 0
        if self.options.population_size is None:
            self._add_message("Population size must not be None!")
            rslt &= False
        elif not isinstance(self.options.population_size, int):
            self._add_message("Population size type must be int!")
            rslt &= False
        elif self.options.population_size < 4 or self.options.population_size > 65536:
            self._add_message("Population size must be an int between 4 and 65536!")
            rslt &= False
        else:
            population_size = self.options.population_size
        keep_elitism_percentage = self.options.keep_elitism_percentage
        if not (0 <= self.options.keep_elitism_percentage <= 100):
            self._add_message("Elitism percentage value must be between 0 and 100!")
            rslt &= False
        immigration_number = 0
        if self.options.immigration_number is None:
            self._add_message("Immigration Number must not be None!")
            rslt &= False
        elif not isinstance(self.options.immigration_number, int):
            self._add_message("Immigration Number must be type int!")
            rslt &= False
        elif (
            population_size > 0
            and self.options.immigration_number > population_size - 1
        ):
            self._add_message(
                "Immigration Number must not be type same or greater\
                    than population size!"
            )
            rslt &= False
        elif self.options.immigration_number < 0:
            self._add_message("Immigration Number must ne eqals or greather than 0!")
            rslt &= False
        else:
            immigration_number = self.options.immigration_number
        if (
            self.options.number_of_mutation_candidate_solutions is None
            and self.options.percentage_of_mutation_candidate_solutions is None
        ):
            self._add_message(
                "Number of Mutation Candidate Solutions or Percentage of Mutation\
                    Candidate Solutions must not be None!"
            )
            rslt &= False
        elif not isinstance(
            self.options.number_of_mutation_candidate_solutions, int
        ) and not isinstance(self.options.percentage_of_mutation_candidate_solutions, float):
            self._add_message(
                "Number of Mutation Candidate Solutions must be type int or Percentage\
                    of Mutation Candidate Solutions must be float!"
            )
            rslt &= False
        else:
            if (
                (self.options.number_of_mutation_candidate_solutions is not None)
                and (isinstance(self.options.number_of_mutation_candidate_solutions, int))
                and (self.options.number_of_mutation_candidate_solutions > 0)
            ):
                if (
                    population_size > 0
                    and self.options.number_of_mutation_candidate_solutions
                    > round(population_size * (keep_elitism_percentage / 100))
                    - immigration_number
                ):
                    self._add_message(
                        "Invalid number of mutation candidate solutions: {0}".format(
                            str(self.options.number_of_mutation_candidate_solutions)
                        )
                    )
                    rslt &= False
            elif (self.options.percentage_of_mutation_candidate_solutions is None) or (
                not isinstance(self.options.percentage_of_mutation_candidate_solutions, float)
            ):
                self._add_message(
                    "Number of Mutation Candidate Solutions must have int\
                        value >=0 or Percentage of\
                        Mutation Candidate Solutions must have float (0.0-100.0) value! "
                )
                rslt &= False
            elif (
                self.options.percentage_of_mutation_candidate_solutions < 0.0
                or self.options.percentage_of_mutation_candidate_solutions > 100.0
            ):
                self._add_message(
                    "Invalid percentage of mutation candidate solutions: {0} and number\
                        of mutation candidate solutions: {1}".format(
                        str(self.options.percentage_of_mutation_candidate_solutions),
                        str(self.options.number_of_mutation_candidate_solutions),
                    )
                )
                rslt &= False
        if self.options._decision_variables is None:
            self._add_message("Decision Variables must not be None!")
            rslt &= False
        num_of_decision_variables = len(self.options._decision_variables)  # type: ignore
        if num_of_decision_variables < 1:
            self._add_message("At least one decision variable must be added!")
            rslt &= False
        if (
            self.options.number_of_mutation_decision_variables is None
            and self.options.percentage_of_mutation_decision_variables is None
        ):
            self._add_message(
                "Number Of Mutation Decision Variables or Percentage Of\
                    Mutation Decision Variables must not be None!"
            )
            rslt &= False
        elif not isinstance(
            self.options.number_of_mutation_decision_variables, int
        ) and not isinstance(self.options.percentage_of_mutation_decision_variables, float):
            self._add_message(
                "Number Of Mutation Decision Variables must have int value >=0 or Percentage of\
                    Mutation Decision Variables must have float (0.0-100.0) value!"
            )
            rslt &= False
        elif (
            (self.options.number_of_mutation_decision_variables is not None)
            and isinstance(self.options.number_of_mutation_decision_variables, int)
            and (self.options.number_of_mutation_decision_variables > 0)
        ):
            if (
                num_of_decision_variables > 0
                and self.options.number_of_mutation_decision_variables > num_of_decision_variables
            ):
                self._add_message(
                    "Invalid number of mutation decision variables: {0}".format(
                        str(self.options.number_of_mutation_decision_variables)
                    )
                )
                rslt &= False
        elif (self.options.percentage_of_mutation_decision_variables is None) or (
            not isinstance(self.options.percentage_of_mutation_decision_variables, float)
        ):
            self._add_message(
                "Number of Mutation Decision Variables must have int value or Percentage\
                    of Mutation Decision Variables must have float value! "
            )
            rslt &= False
        elif (
            self.options.percentage_of_mutation_decision_variables < 0.0
            or self.options.percentage_of_mutation_decision_variables > 100.0
        ):
            self._add_message(
                "Invalid percentage of mutation decision variables: {} and number of\
                    mutation decision variables: {}".format(
                    str(self.options.percentage_of_mutation_decision_variables),
                    str(self.options.number_of_mutation_decision_variables),
                )
            )
            rslt &= False
        if self.options.max_attempt_no is None:
            self._add_message("Max Attempt No must not be None!")
            rslt &= False
        elif not isinstance(self.options.max_attempt_no, int):
            self._add_message("Max Attempt No must be type int!")
            rslt &= False
        elif self.options.max_attempt_no < 1 or self.options.max_attempt_no > 65536:
            self._add_message("Max Attempt No must be type an int between 1 and 65536!")
            rslt &= False
        if (
            self.options.candidate_solution_mutation == definitions.VARIABLE_COLUMNAR_DIVERSITY
            or definitions.VARIABLE_COLUMNAR_DIVERSITY in self.options.candidate_solution_mutation
        ):
            if self.options.variable_columnar_diversity_mutation_decision_variable_sampling is None:
                self._add_message(
                    "Variable Columnar Diversity Mutation Decision Variable Sampling must not be None!"
                )
                rslt &= False
            elif not isinstance(
                self.options.variable_columnar_diversity_mutation_decision_variable_sampling, str
            ):
                self._add_message(
                    "Variable Columnar Diversity Mutation Decision Variable Sampling must be type str!"
                )
                rslt &= False
        if self.options.candidate_solution_mutation is None:
            self._add_message("Candidate Solution Mutation must not be None!")
            rslt &= False
        elif not isinstance(self.options.candidate_solution_mutation, str):
            self._add_message("Candidate Solution Mutation must be type str!")
            rslt &= False
        elif definitions.PARAM_SEPARATOR in self.options.candidate_solution_mutation:
            mutator_strings = [
                ms.strip()
                for ms in self.options.candidate_solution_mutation.split(
                    definitions.PARAM_SEPARATOR
                )
            ]
            for mutator_string in mutator_strings:
                if mutator_string not in definitions.CANDIDATE_SOLUTION_MUTATION_STRINGS:
                    self._add_message(
                        "Invalid value of Candidate Solution Mutation:\
                            {0}. Allowed values: {1}".format(
                            mutator_string,
                            self._get_allowed_values(
                                definitions.CANDIDATE_SOLUTION_MUTATION_STRINGS
                            ),
                        )
                    )
                    rslt &= False
        elif (
            self.options.candidate_solution_mutation
            not in definitions.CANDIDATE_SOLUTION_MUTATION_STRINGS
        ):
            self._add_message(
                "Invalid value of Candidate Solution Mutation: {0}. Allowed values: {1}".format(
                    self.options.candidate_solution_mutation,
                    self._get_allowed_values(definitions.CANDIDATE_SOLUTION_MUTATION_STRINGS),
                )
            )
            rslt &= False
        if self.options.exit_check is None:
            self._add_message("Exit Check must not be None!")
            rslt &= False
        elif not isinstance(self.options.exit_check, str):
            self._add_message("Exit Check must be type str!")
            rslt &= False
        elif self.options.exit_check not in definitions.EXIT_CRITERIA_STRINGS:
            self._add_message(
                "Invalid value of Exit Check: {0}. Allowed values: {1}".format(
                    self.options.exit_check,
                    self._get_allowed_values(definitions.EXIT_CRITERIA_STRINGS),
                )
            )
            rslt &= False
        if self.options.candidate_solution_mutation == definitions.VARIABLE_COLUMNAR_DIVERSITY:
            if self.options.variable_columnar_diversity_mutation_decision_variable_sampling is None:
                self._add_message(
                    "Variable Columnar Diversity Mutation Decision Variable Selection must not be None!"
                )
                rslt &= False
            elif not isinstance(
                self.options.variable_columnar_diversity_mutation_decision_variable_sampling, str
            ):
                self._add_message(
                    "Variable Columnar Diversity Mutation Decision Variable Selection must be type str!"
                )
                rslt &= False
            elif not self._validate_selection(
                self.options.variable_columnar_diversity_mutation_decision_variable_sampling,
                "Variable Columnar Diversity Mutation Decision Variable Selection",
                self.options.number_of_mutation_decision_variables,
                "Group Size for Variable Columnar Diversity Mutation Decision Variable Selection must be below\
                    or equal than the number of mutation decision variables!",
            ):
                rslt &= False
        if self.options.logging is None:
            self._add_message("Logging must not be None!")
            rslt &= False
        elif not isinstance(self.options.logging, bool):
            self._add_message("Logging must be type bool!")
            rslt &= False
        if self.options.must_mutate_for_same_parents is None:
            self._add_message("Must Mutate For Same Parents must not be None!")
            rslt &= False
        elif not isinstance(self.options.must_mutate_for_same_parents, bool):
            self._add_message("Must Mutate For Same Parents must be type bool!")
            rslt &= False
        if (
            self.options.population_mutation == definitions.COST_DIVERSITY
            or definitions.PARENT_DIVERSITY in self.options.population_mutation
        ):
            if self.options.parent_diversity_mutation_candidate_solution_sampling is None:
                self._add_message(
                    "Parent Diversity Mutation Candidate Solution Sampling must not be None!"
                )
                rslt &= False
            elif not isinstance(
                self.options.parent_diversity_mutation_candidate_solution_sampling, str
            ):
                self._add_message(
                    "Parent Diversity Mutation Candidate Solution Sampling must be type str!"
                )
                rslt &= False
            elif not self._validate_selection(
                self.options.parent_diversity_mutation_candidate_solution_sampling,
                "Parents Diversity Mutation Candidate Solution Sampling",
                round(population_size * (keep_elitism_percentage / 100)) - self.options.immigration_number,  # type: ignore
                "Group Size for Parents Diversity Mutation Candidate Solution\
                Sampling cannot have the value below half population!",
            ):
                rslt &= False
        if self.options.population_mutation is None:
            self._add_message("Population Mutation must not be None!")
            rslt &= False
        elif not isinstance(self.options.population_mutation, str):
            self._add_message("Population Mutation must be type str!")
            rslt &= False
        elif definitions.PARAM_SEPARATOR in self.options.population_mutation:
            mutator_strings = [
                ms.strip()
                for ms in self.options.population_mutation.split(
                    definitions.PARAM_SEPARATOR
                )
            ]
            for mutator_string in mutator_strings:
                if mutator_string not in definitions.POPULATION_MUTATION_STRINGS:
                    self._add_message(
                        "Invalid value of Population Mutation:\
                            {0}. Allowed values: {1}".format(
                            mutator_string,
                            self._get_allowed_values(
                                definitions.POPULATION_MUTATION_STRINGS
                            ),
                        )
                    )
                    rslt &= False
        elif (
            self.options.population_mutation
            not in definitions.POPULATION_MUTATION_STRINGS
        ):
            self._add_message(
                "Invalid value of Population Mutation: {0}. Allowed values: {1}".format(
                    self.options.population_mutation,
                    self._get_allowed_values(definitions.POPULATION_MUTATION_STRINGS),
                )
            )
            rslt &= False
        if self.options.decision_variable_mutation is None:
            self._add_message("Decision Variable Mutation must not be None!")
            rslt &= False
        elif not isinstance(self.options.decision_variable_mutation, str):
            self._add_message("Decision Variable Mutation must be type str!")
            rslt &= False
        elif definitions.PARAM_SEPARATOR in self.options.decision_variable_mutation:
            mutator_strings = [
                ms.strip()
                for ms in self.options.decision_variable_mutation.split(definitions.PARAM_SEPARATOR)
            ]
            for mutator_string in mutator_strings:
                if mutator_string not in definitions.DECISION_VARIABLE_MUTATION_STRINGS:
                    self._add_message(
                        "Invalid value of Decision Variable Mutation:\
                            {0}. Allowed values: {1}".format(
                            mutator_string,
                            self._get_allowed_values(definitions.DECISION_VARIABLE_MUTATION_STRINGS),
                        )
                    )
                    rslt &= False
        elif self.options.decision_variable_mutation not in definitions.DECISION_VARIABLE_MUTATION_STRINGS:
            self._add_message(
                "Invalid value of Decision Variable Mutation: {0}. Allowed values: {1}".format(
                    self.options.decision_variable_mutation,
                    self._get_allowed_values(definitions.DECISION_VARIABLE_MUTATION_STRINGS),
                )
            )
            rslt &= False
        if self.options.parent_selection is None:
            self._add_message("Parent Selection must not be None!")
            rslt &= False
        elif not isinstance(self.options.parent_selection, str):
            self._add_message("Parent Selection must be type str!")
            rslt &= False
        elif not self._validate_selection(
            self.options.parent_selection,
            "Parent Selection",
            round(population_size * (keep_elitism_percentage / 100)) - self.options.immigration_number,  # type: ignore
            "Group Size for parent selection cannot have\
            the value below half population!",
        ):
            rslt &= False
        if self.options.requested_cost is None:
            self._add_message("Requested Cost must not be None!")
            rslt &= False
        elif not isinstance(self.options.requested_cost, float):
            self._add_message("Requested Cost must be type float!")
            rslt &= False
        decay_generations = self.options.normal_distribution_mutation_min_std_dev_decay_generations
        if decay_generations is not None and (
            isinstance(decay_generations, bool)
            or not isinstance(decay_generations, (int, float))
            or not decay_generations > 0
        ):
            self._add_message(
                "Normal Distribution Mutation Min Std Dev Decay Generations must be None or a positive number!"
            )
            rslt &= False
        if self.options.timeout is None:
            self._add_message("Timeout must not be None!")
            rslt &= False
        elif not isinstance(self.options.timeout, int):
            self._add_message("Timeout must be type int!")
            rslt &= False
        elif self.options.timeout < 1:
            self._add_message(
                "Invalid timeout value: {0}".format(str(self.options.timeout))
            )
            rslt &= False
        return rslt

    def _validate_selection(
        self,
        selection_string,
        selection_type,
        comparing_number,
        group_size_error_message,
    ) -> bool:
        selection_strings = selection_string.split(definitions.PARAM_SEPARATOR)
        if len(selection_strings) > 2 or (
            len(selection_strings) > 1
            and selection_strings[0] != definitions.TOURNAMENT
        ):
            self._add_message(
                "Invalid {0} value: {1}".format(selection_type, selection_string)
            )
            return False
        if (
            selection_strings[0] == definitions.TOURNAMENT
            and len(selection_strings) > 1
        ):
            group_size = selection_strings[1]
            n_group_size = -1
            try:
                n_group_size = int(group_size)
            except Exception:
                self._add_message(
                    "Invalid {0} value: {1}".format(selection_type, selection_string)
                )
                return False
            if n_group_size < 2:
                self._add_message(
                    "Invalid {0} value: {1}. Minimal group size is 2.".format(
                        selection_type, selection_string
                    )
                )
                return False
            if not isinstance(n_group_size, int):
                self._add_message(
                    "Invalid value for {0}: {1}".format(
                        selection_type, selection_string
                    )
                )
                return False
            elif int(n_group_size) > comparing_number:
                self._add_message(group_size_error_message)
                return False
        if selection_strings[0] not in definitions.SELECTION_STRINGS:
            self._add_message(
                "Invalid {0} value: {1}. Allowed values: {2}".format(
                    selection_type,
                    selection_string,
                    self._get_allowed_values(definitions.SELECTION_STRINGS),
                )
            )
            return False
        return True

    def _get_allowed_values(self, s_list):
        rslt = ""
        for s in s_list:
            rslt += s + ", "
        return rslt[:-2]
