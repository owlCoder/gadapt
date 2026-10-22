from typing import Tuple, List

import gadapt.ga_model.definitions as definitions
from gadapt.factory.ga_base_factory import BaseGAFactory
from gadapt.operations.cost_finding.base_cost_finder import BaseCostFinder
from gadapt.operations.cost_finding.elitism_cost_finder import ElitismCostFinder
from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.operations.crossover.base_crossover_probability_determinator import BaseCrossoverProbabilityDeterminator
from gadapt.operations.crossover.columnar_diversity_crossover_probability_determinator import \
    ColumnarDiversityCrossoverProbabilityDeterminator
from gadapt.operations.crossover.composed_crossover_probability_determinator import \
    ComposedCrossoverProbabilityDeterminator
from gadapt.operations.crossover.cost_diversity_crossover_probability_determinator import \
    CostDiversityCrossoverProbabilityDeterminator
from gadapt.operations.crossover.fixed_crossover_probability_determinator import FixedCrossoverProbabilityDeterminator
from gadapt.operations.exit_check.avg_cost_exit_checker import AvgCostExitChecker
from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker
from gadapt.operations.exit_check.min_cost_exit_checker import MinCostExitChecker
from gadapt.operations.exit_check.requested_cost_exit_checker import (
    RequestedCostExitChecker,
)
from gadapt.operations.immigration.candidate_solution_immigration.base_candidate_solution_immigrator import (
    BaseCandidateSolutionImmigrator,
)
from gadapt.operations.immigration.candidate_solution_immigration.random_candidate_solution_immigrator import (
    RandomCandidateSolutionImmigrator,
)
from gadapt.operations.immigration.population_immigration.base_population_immigrator import (
    BasePopulationImmigrator,
)
from gadapt.operations.immigration.population_immigration.common_population_immigrator import (
    CommonPopulationImmigrator,
)
from gadapt.operations.mutation.candidate_solution_mutation.base_decision_variable_mutation_selector import (
    BaseDecisionVariableMutationSelector,
)
from gadapt.operations.mutation.candidate_solution_mutation.composed_decision_variable_mutation_rate_determinator import (
    ComposedDecisionVariableMutationRateDeterminator,
)
from gadapt.operations.mutation.candidate_solution_mutation.composed_decision_variable_mutation_selector import (
    ComposedDecisionVariableMutationSelector,
)
from gadapt.operations.mutation.candidate_solution_mutation.variable_columnar_diversity_decision_variable_mutation_rate_determinator import (
    VariableColumnarDiversityDecisionVariableMutationRateDeterminator,
)
from gadapt.operations.mutation.candidate_solution_mutation.variable_columnar_diversity_decision_variable_mutation_selector import (
    VariableColumnarDiversityDecisionVariableMutationSelector,
)
from gadapt.operations.mutation.candidate_solution_mutation.random_decision_variable_mutation_rate_determinator import (
    RandomDecisionVariableMutationRateDeterminator,
)
from gadapt.operations.mutation.candidate_solution_mutation.random_decision_variable_mutation_selector import (
    RandomDecisionVariableMutationSelector,
)
from gadapt.operations.mutation.candidate_solution_mutation.strict_decision_variable_mutation_rate_determinator import (
    StrictDecisionVariableMutationRateDeterminator,
)
from gadapt.operations.mutation.decision_variable_mutation.base_decision_variable_mutator import BaseDecisionVariableMutator
from gadapt.operations.mutation.decision_variable_mutation.credit_based_decision_variable_mutator import CreditBasedDecisionVariableMutator
from gadapt.operations.mutation.decision_variable_mutation.extreme_pointed_decision_variable_mutator import (
    ExtremePointedDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_cost_diversity_decision_variable_mutator import \
    NormalDistributionCostDiversityDecisionVariableMutator
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_decision_variable_mutator import (
    NormalDistributionDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (
    RandomDecisionVariableMutator,
)
from gadapt.operations.mutation.population_mutation.base_candidate_solution_mutation_selector import (
    BaseCandidateSolutionMutationSelector,
)
from gadapt.operations.mutation.population_mutation.composed_candidate_solution_mutation_rate_determinator import (
    ComposedCandidateSolutionMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.composed_candidate_solution_mutation_selector import (
    ComposedCandidateSolutionMutationSelector,
)
from gadapt.operations.mutation.population_mutation.cost_diversity_candidate_solution_mutation_rate_determinator import (
    CostDiversityCandidateSolutionMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.variable_columnar_diversity_candidate_solution_mutation_rate_determinator import (
    VariableColumnarDiversityCandidateSolutionMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.parent_cost_diversity_candidate_solution_mutation_selector import \
    ParentCostDiversityCandidateSolutionMutationSelector
from gadapt.operations.mutation.population_mutation.parent_structural_diversity_candidate_solution_mutation_selector import (
    ParentStructuralDiversityCandidateSolutionMutationSelector,
)
from gadapt.operations.mutation.population_mutation.random_candidate_solution_mutation_rate_determinator import (
    RandomCandidateSolutionMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.random_candidate_solution_mutation_selector import (
    RandomCandidateSolutionMutationSelector,
)
from gadapt.operations.mutation.population_mutation.strict_candidate_solution_mutation_rate_determinator import (
    StrictCandidateSolutionMutationRateDeterminator,
)
from gadapt.operations.parent_selection.base_parent_selector import BaseParentSelector
from gadapt.operations.parent_selection.sampling_parent_selector import (
    SamplingParentSelector,
)
from gadapt.operations.sampling.base_sampling import BaseSampling
from gadapt.operations.sampling.from_top_to_bottom_sampling import (
    FromTopToBottomSampling,
)
from gadapt.operations.sampling.random_sampling import RandomSampling
from gadapt.operations.sampling.roulette_wheel_sampling import RouletteWheelSampling
from gadapt.operations.sampling.tournament_sampling import TournamentSampling
from gadapt.operations.decision_variable_update.variable_columnar_diversity_decision_variable_updater import (
    ColumnarDiversityDecisionVariableUpdater,
)
from gadapt.operations.crossover.blending_crossover import BlendingCrossover
from gadapt.operations.crossover.uniform_crossover import UniformCrossover
from gadapt.operations.exit_check.number_of_generations_exit_checker import (
    NumberOfGenerationsExitChecker,
)
from gadapt.operations.mutation.decision_variable_mutation.composed_decision_variable_mutator import (
    ComposedDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_variable_columnar_diversity_decision_variable_mutator import (
    NormalDistributionVariableColumnarDiversityDecisionVariableMutator,
)
from gadapt.operations.mutation.population_mutation.base_candidate_solution_mutation_rate_determinator import (
    BaseCandidateSolutionMutationRateDeterminator,
)
from gadapt.operations.population_update.cost_diversity_population_updater import (
    CostDiversityPopulationUpdater,
)
from gadapt.operations.candidate_solution_update.base_candidate_solution_updater import (
    BaseCandidateSolutionUpdater,
)
from gadapt.operations.candidate_solution_update.parent_diversity_candidate_solution_updater import (
    ParentDiversityCandidateSolutionUpdater,
)
from gadapt.operations.decision_variable_update.base_decision_variable_updater import BaseDecisionVariableUpdater
from gadapt.operations.population_update.base_population_updater import (
    BasePopulationUpdater,
)


class GAFactory(BaseGAFactory):
    """
    Factory implementatiopn for creating  class instances based on GA options
    """

    def __init__(self):
        super().__init__()
        self.decision_variable_mutation_rate_determinator = None
        self.candidate_solution_mutation_rate_determinator = None

    def _get_cost_finder(self) -> BaseCostFinder:
        """
        Cost Finder instance
        """
        return ElitismCostFinder()

    def _get_population_immigrator(self) -> BasePopulationImmigrator:
        """
        Population Immigrator Instance
        """
        return CommonPopulationImmigrator(self.get_candidate_solution_immigrator())

    def _get_candidate_solution_immigrator(self) -> BaseCandidateSolutionImmigrator:
        """
        Candidate Solution Immigrator Instance
        """
        return RandomCandidateSolutionImmigrator()

    def _get_decision_variable_mutation_selector(self) -> BaseDecisionVariableMutationSelector:
        """
        Decision Variable Mutation Selector Instance
        """
        return self._get_decision_variable_mutation_selector_combined()

    def _get_crossover_probability_determinator(self) -> BaseCrossoverProbabilityDeterminator:
        return self._get_crossover_probability_determinator_combined()

    def _get_decision_variable_mutator_combined(self) -> BaseDecisionVariableMutator:
        if self._ga is None:
            raise Exception("_ga object must not be None!")
        mutator_strings = [
            gm.strip()
            for gm in self._ga.decision_variable_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        decision_variable_mutators: List[BaseDecisionVariableMutator] = []
        if definitions.RANDOM in mutator_strings:
            decision_variable_mutators.append(RandomDecisionVariableMutator())
        if definitions.EXTREME_POINTED in mutator_strings:
            decision_variable_mutators.append(ExtremePointedDecisionVariableMutator())
        if definitions.VARIABLE_COLUMNAR_DIVERSITY in mutator_strings:
            decision_variable_mutators.append(NormalDistributionVariableColumnarDiversityDecisionVariableMutator(self._options.normal_distribution_mutation_min_std_dev, self._options.normal_distribution_mutation_max_std_dev, self._options.normal_distribution_mutation_min_std_dev_decay_generations, self._options.get_stagnation_generations_function))
        if definitions.COST_DIVERSITY in mutator_strings:
            decision_variable_mutators.append(NormalDistributionCostDiversityDecisionVariableMutator(self._options.get_cost_diversity_coefficient_function, self._options.normal_distribution_mutation_min_std_dev, self._options.normal_distribution_mutation_max_std_dev, self._options.normal_distribution_mutation_min_std_dev_decay_generations, self._options.get_stagnation_generations_function))
        elif definitions.NORMAL_DISTRIBUTION in mutator_strings:
            decision_variable_mutators.append(NormalDistributionDecisionVariableMutator())
        if len(decision_variable_mutators) == 0:
            decision_variable_mutators.append(NormalDistributionDecisionVariableMutator())
            decision_variable_mutators.append(RandomDecisionVariableMutator())
        if self._options.mutation_operator_policy != "legacy":
            controller = CreditBasedDecisionVariableMutator(
                policy=self._options.mutation_operator_policy,
                credit=self._options.mutation_operator_credit,
                assignment=self._options.mutation_credit_assignment,
                evaluation_counter=self._options.mutation_evaluation_counter,
                violation_function=self._options.mutation_violation_function,
                scenario_count=self._options.mutation_scenario_count,
            )
            for operator in decision_variable_mutators:
                controller.append(operator)
            return controller
        if len(decision_variable_mutators) == 1:
            return decision_variable_mutators[0]
        else:
            main_decision_variable_mutator = ComposedDecisionVariableMutator()
            for mutator in decision_variable_mutators:
                main_decision_variable_mutator.append(mutator)
        return main_decision_variable_mutator

    def _get_decision_variable_mutator(self) -> BaseDecisionVariableMutator:
        """
        Decision Variable Mutator Instance
        """
        return self._get_decision_variable_mutator_combined()

    def _population_mutation_options_validation(self):
        """
        Validates population mutator options
        """
        mutator_strings = self._ga.population_mutation.split(
            definitions.PARAM_SEPARATOR
        )
        for s in mutator_strings:
            if s.strip() not in definitions.POPULATION_MUTATION_STRINGS:
                raise Exception(s + " is not defined as option for population mutation")

    def _make_candidate_solution_mutation_selector(
        self, population_mutator_string=None
    ) -> BaseCandidateSolutionMutationSelector:
        """
        Population Mutator Instance
        """
        self._population_mutation_options_validation()
        return self._get_candidate_solution_mutation_selector_combined()

    def _get_candidate_solution_mutation_selector(self) -> BaseCandidateSolutionMutationSelector:
        """
        Population Mutator Instance
        """
        return self._make_candidate_solution_mutation_selector()

    def _get_candidate_solution_mutation_rate_determinators(
        self,
    ) -> Tuple[
        BaseCandidateSolutionMutationRateDeterminator, BaseCandidateSolutionMutationRateDeterminator
    ]:
        if self._ga is None:
            raise Exception("_ga object must not be None!")
        if self.candidate_solution_mutation_rate_determinator is not None:
            return self.candidate_solution_mutation_rate_determinator
        mutator_strings = [
            ms.strip()
            for ms in self._ga.population_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        candidate_solution_mutation_rate_determinators: List[
            BaseCandidateSolutionMutationRateDeterminator
        ] = []

        if definitions.RANDOM in mutator_strings:
            candidate_solution_mutation_rate_determinators.append(
                RandomCandidateSolutionMutationRateDeterminator()
            )
        if definitions.STRICT in mutator_strings:
            candidate_solution_mutation_rate_determinators.append(
                StrictCandidateSolutionMutationRateDeterminator()
            )
        if definitions.VARIABLE_COLUMNAR_DIVERSITY in mutator_strings:
            candidate_solution_mutation_rate_determinators.append(
                VariableColumnarDiversityCandidateSolutionMutationRateDeterminator()
            )
        if definitions.COST_DIVERSITY in mutator_strings:
            candidate_solution_mutation_rate_determinators.append(
                CostDiversityCandidateSolutionMutationRateDeterminator()
            )
        if len(candidate_solution_mutation_rate_determinators) == 0:
            candidate_solution_mutation_rate_determinators.append(
                CostDiversityCandidateSolutionMutationRateDeterminator()
            )
        if len(candidate_solution_mutation_rate_determinators) == 1:
            main_candidate_solution_mutation_rate_determinator: (
                BaseCandidateSolutionMutationRateDeterminator
            ) = candidate_solution_mutation_rate_determinators[0]
        else:
            main_candidate_solution_mutation_rate_determinator = (
                ComposedCandidateSolutionMutationRateDeterminator()
            )
            for determinator in candidate_solution_mutation_rate_determinators:
                main_candidate_solution_mutation_rate_determinator.append(determinator)
        if (
            definitions.RANDOM in mutator_strings
            and definitions.PARENT_DIVERSITY in mutator_strings
        ):
            helper_candidate_solution_mutation_rate_determinator: (
                BaseCandidateSolutionMutationRateDeterminator
            ) = StrictCandidateSolutionMutationRateDeterminator()
        else:
            helper_candidate_solution_mutation_rate_determinator = (
                main_candidate_solution_mutation_rate_determinator
            )
        return (
            main_candidate_solution_mutation_rate_determinator,
            helper_candidate_solution_mutation_rate_determinator,
        )

    def _get_candidate_solution_mutation_selector_combined(
        self,
    ) -> BaseCandidateSolutionMutationSelector:
        """
        Population Mutator Instance - combined
        """
        if self._ga is None:
            raise Exception("_ga object must not be None!")
        mutator_strings = [
            ms.strip()
            for ms in self._ga.population_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        (
            main_candidate_solution_mutation_rate_determinator,
            helper_candidate_solution_mutation_rate_determinator,
        ) = self._get_candidate_solution_mutation_rate_determinators()
        candidate_solution_mutation_selectors: List[BaseCandidateSolutionMutationSelector] = []
        if definitions.RANDOM in mutator_strings:
            candidate_solution_mutation_selectors.append(
                RandomCandidateSolutionMutationSelector(
                    helper_candidate_solution_mutation_rate_determinator,
                    self._get_decision_variable_mutation_selector(),
                )
            )
        if definitions.PARENT_DIVERSITY in mutator_strings:
            candidate_solution_mutation_selectors.append(
                ParentStructuralDiversityCandidateSolutionMutationSelector(
                    helper_candidate_solution_mutation_rate_determinator,
                    self._get_decision_variable_mutation_selector(),
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_candidate_solution_sampling
                    ),
                )
            )
            candidate_solution_mutation_selectors.append(
                ParentCostDiversityCandidateSolutionMutationSelector(
                    helper_candidate_solution_mutation_rate_determinator,
                    self._get_decision_variable_mutation_selector(),
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_candidate_solution_sampling
                    ),
                )
            )
        if len(candidate_solution_mutation_selectors) == 0:
            candidate_solution_mutation_selectors.append(
                ParentStructuralDiversityCandidateSolutionMutationSelector(
                    helper_candidate_solution_mutation_rate_determinator,
                    self._get_decision_variable_mutation_selector(),
                    self._get_sampling_method(
                        self._ga.parent_diversity_mutation_candidate_solution_sampling
                    ),
                )
            )
        if len(candidate_solution_mutation_selectors) == 1:
            return candidate_solution_mutation_selectors[0]
        else:
            candidate_solution_mutation_selector = ComposedCandidateSolutionMutationSelector(
                main_candidate_solution_mutation_rate_determinator,
                self._get_decision_variable_mutation_selector(),
            )
            for selector in candidate_solution_mutation_selectors:
                candidate_solution_mutation_selector.append(selector)
        return candidate_solution_mutation_selector

    def _get_decision_variable_mutation_rate_determinators(self):
        if self.decision_variable_mutation_rate_determinator is not None:
            return (
                self.decision_variable_mutation_rate_determinator,
                self.decision_variable_mutation_rate_determinator,
            )
        mutator_strings = [
            ms.strip()
            for ms in self._ga.candidate_solution_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        decision_variable_mutation_rate_determinators = []

        if definitions.RANDOM in mutator_strings:
            decision_variable_mutation_rate_determinators.append(
                RandomDecisionVariableMutationRateDeterminator()
            )
        if definitions.STRICT in mutator_strings:
            decision_variable_mutation_rate_determinators.append(
                StrictDecisionVariableMutationRateDeterminator()
            )
        if definitions.VARIABLE_COLUMNAR_DIVERSITY in mutator_strings:
            decision_variable_mutation_rate_determinators.append(
                VariableColumnarDiversityDecisionVariableMutationRateDeterminator(
                    self._options.strict_mutation_decision_variable_limit
                )
            )
        if len(decision_variable_mutation_rate_determinators) == 0:
            decision_variable_mutation_rate_determinators.append(
                RandomDecisionVariableMutationRateDeterminator()
            )
            decision_variable_mutation_rate_determinators.append(
                VariableColumnarDiversityDecisionVariableMutationRateDeterminator(
                    self._options.strict_mutation_decision_variable_limit
                )
            )
        if len(decision_variable_mutation_rate_determinators) == 1:
            main_decision_variable_mutation_rate_determinator = decision_variable_mutation_rate_determinators[0]
        else:
            main_decision_variable_mutation_rate_determinator = (
                ComposedDecisionVariableMutationRateDeterminator()
            )
            for determinator in decision_variable_mutation_rate_determinators:
                main_decision_variable_mutation_rate_determinator.append(determinator)
        if (
            definitions.RANDOM in mutator_strings
            and definitions.COST_DIVERSITY in mutator_strings
        ):
            helper_decision_variable_mutation_rate_determinator = (
                StrictDecisionVariableMutationRateDeterminator()
            )
        else:
            helper_decision_variable_mutation_rate_determinator = (
                main_decision_variable_mutation_rate_determinator
            )
        return (
            main_decision_variable_mutation_rate_determinator,
            helper_decision_variable_mutation_rate_determinator,
        )

    def _get_crossover_probability_determinator_combined(self) -> BaseCrossoverProbabilityDeterminator:
        if self._ga is None:
            raise Exception("_ga object must not be None!")
        crossover_strings = [
            ms.strip()
            for ms in self._ga.crossover.split(definitions.PARAM_SEPARATOR)
        ]

        crossover_probability_determinator = ComposedCrossoverProbabilityDeterminator()
        if definitions.COST_DIVERSITY in crossover_strings:
            crossover_probability_determinator.append(CostDiversityCrossoverProbabilityDeterminator())
        if definitions.VARIABLE_COLUMNAR_DIVERSITY in crossover_strings:
            crossover_probability_determinator.append(ColumnarDiversityCrossoverProbabilityDeterminator())
        if definitions.FIXED in crossover_strings:
            crossover_probability_determinator.append(FixedCrossoverProbabilityDeterminator())
        if len(crossover_probability_determinator) == 0:
            crossover_probability_determinator.append(FixedCrossoverProbabilityDeterminator())
        return crossover_probability_determinator

    def _get_decision_variable_mutation_selector_combined(self) -> BaseDecisionVariableMutationSelector:
        """
        Decision Variable Mutation Selector Instance - combined
        """
        if self._ga is None:
            raise Exception("_ga object must not be None!")
        mutator_strings = [
            ms.strip()
            for ms in self._ga.candidate_solution_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        (
            main_decision_variable_mutation_rate_determinator,
            helper_decision_variable_mutation_rate_determinator,
        ) = self._get_decision_variable_mutation_rate_determinators()
        decision_variable_mutation_selectors = []
        if definitions.RANDOM in mutator_strings:
            decision_variable_mutation_selectors.append(
                RandomDecisionVariableMutationSelector(
                    helper_decision_variable_mutation_rate_determinator, self.get_decision_variable_mutator()
                ),
            )
        if definitions.VARIABLE_COLUMNAR_DIVERSITY in mutator_strings:
            decision_variable_mutation_selectors.append(
                VariableColumnarDiversityDecisionVariableMutationSelector(
                    helper_decision_variable_mutation_rate_determinator,
                    self.get_decision_variable_mutator(),
                    self._get_sampling_method(
                        self._ga.variable_columnar_diversity_mutation_decision_variable_sampling
                    ),
                )
            )
        if len(decision_variable_mutation_selectors) == 0:
            decision_variable_mutation_selectors.append(
                VariableColumnarDiversityDecisionVariableMutationSelector(
                    helper_decision_variable_mutation_rate_determinator,
                    self.get_decision_variable_mutator(),
                    self._get_sampling_method(
                        self._ga.variable_columnar_diversity_mutation_decision_variable_sampling
                    ),
                )
            )
        if len(decision_variable_mutation_selectors) == 1:
            decision_variable_mutation_selector = decision_variable_mutation_selectors[0]
        else:
            decision_variable_mutation_selector = self.get_composed_decision_variable_mutation_selector(
                main_decision_variable_mutation_rate_determinator,
                decision_variable_mutation_selectors,
                helper_decision_variable_mutation_rate_determinator,
            )
        return decision_variable_mutation_selector

    def get_composed_decision_variable_mutation_selector(
        self,
        main_decision_variable_mutation_rate_determinator,
        decision_variable_mutation_selectors,
        helper_decision_variable_mutation_rate_determinator,
    ):
        if not decision_variable_mutation_selectors:
            decision_variable_mutation_selectors.append(
                VariableColumnarDiversityDecisionVariableMutationSelector(
                    helper_decision_variable_mutation_rate_determinator,
                    self.get_decision_variable_mutator(),
                    self._get_sampling_method(
                        self._ga.variable_columnar_diversity_mutation_decision_variable_sampling
                    ),
                )
            )
            decision_variable_mutation_selectors.append(
                RandomDecisionVariableMutationSelector(helper_decision_variable_mutation_rate_determinator)
            )
        decision_variable_mutation_selector = ComposedDecisionVariableMutationSelector(
            main_decision_variable_mutation_rate_determinator, self.get_decision_variable_mutator()
        )
        for selector in decision_variable_mutation_selectors:
            decision_variable_mutation_selector.append(selector)
        return decision_variable_mutation_selector

    def _get_parent_selector(self) -> BaseParentSelector:
        """
        Parent Selector Instance
        """
        if self._ga is None:
            raise Exception("_ga object must not be None!")
        return SamplingParentSelector(
            self._get_sampling_method(self._ga.parent_selection)
        )

    def _get_sampling_method(self, str) -> BaseSampling:
        """
        Sampling Method Instance
        """
        str_value = str
        sampling_method_strings = str.split(definitions.PARAM_SEPARATOR)
        other_value = None
        if len(sampling_method_strings) > 1:
            str_value = sampling_method_strings[0]
            try:
                other_value = int(sampling_method_strings[1])
            except Exception:
                pass
        if str_value == definitions.TOURNAMENT:
            return TournamentSampling(other_value)
        elif str_value == definitions.FROM_TOP_TO_BOTTOM:
            return FromTopToBottomSampling()
        elif str_value == definitions.RANDOM:
            return RandomSampling()
        return RouletteWheelSampling()

    def _get_exit_checker(self) -> BaseExitChecker:
        """
        Exit Checker Instance
        """
        if self._ga is None:
            raise Exception("ga object must not be None!")
        if self._ga.exit_check == definitions.AVG_COST:
            return AvgCostExitChecker(self._ga.max_attempt_no, self._ga.number_of_generations, self._ga.exit_function)
        if self._ga.exit_check == definitions.MIN_COST:
            return MinCostExitChecker(self._ga.max_attempt_no, self._ga.number_of_generations, self._ga.exit_function)
        if self._ga.exit_check == definitions.GENERATIONS:
            return NumberOfGenerationsExitChecker(self._ga.number_of_generations, self._ga.exit_function)
        return RequestedCostExitChecker(self._ga.requested_cost, self._ga.number_of_generations, self._ga.exit_function)

    def _get_crossover(self) -> BaseCrossover:
        """
        Crossover Instance
        """
        if self._ga is None:
            raise Exception("ga object must not be None!")
        candidate_solution_updater = self.get_candidate_solution_updater()
        candidate_solution_mutation_selector = self._get_decision_variable_mutation_selector()
        crossover_probability_determinator = self._get_crossover_probability_determinator()
        crossover_strings = [
            ms.strip()
            for ms in self._ga.crossover.split(definitions.PARAM_SEPARATOR)
        ]
        if definitions.BLENDING in crossover_strings:
            return BlendingCrossover(candidate_solution_updater, candidate_solution_mutation_selector, crossover_probability_determinator)
        if definitions.UNIFORM in crossover_strings:
            return UniformCrossover(candidate_solution_updater, candidate_solution_mutation_selector, crossover_probability_determinator)
        return BlendingCrossover(candidate_solution_updater, candidate_solution_mutation_selector, crossover_probability_determinator)

    def _get_decision_variable_updater(self):
        """
        Decision Variable Updater Instance
        """
        population_mutator_strings = [
            ms.strip()
            for ms in self._ga.population_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        candidate_solution_mutator_strings = [
            ms.strip()
            for ms in self._ga.candidate_solution_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        decision_variable_mutator_strings = [
            ms.strip()
            for ms in self._ga.decision_variable_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        crossover_strings = [
            ms.strip()
            for ms in self._ga.crossover.split(definitions.PARAM_SEPARATOR)
        ]
        # The columnar diversity coefficients of the decision variables are also needed by the
        # crossover probability method. Without them they stay NaN, and so does the probability.
        all_strings = (
            population_mutator_strings
            + candidate_solution_mutator_strings
            + decision_variable_mutator_strings
            + crossover_strings
        )
        if definitions.VARIABLE_COLUMNAR_DIVERSITY in all_strings:
            return ColumnarDiversityDecisionVariableUpdater()
        return BaseDecisionVariableUpdater()

    def _get_candidate_solution_updater(self):
        return ParentDiversityCandidateSolutionUpdater()

    def get_candidate_solution_updater(self):
        population_mutator_strings = [
            ms.strip()
            for ms in self._ga.population_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        if (
            not population_mutator_strings
            or definitions.PARENT_DIVERSITY in population_mutator_strings
        ):
            return ParentDiversityCandidateSolutionUpdater()
        return BaseCandidateSolutionUpdater()

    def _get_population_updater(self):
        """
        Population Updater Instance
        """
        population_mutator_strings = [
            ms.strip()
            for ms in self._ga.population_mutation.split(definitions.PARAM_SEPARATOR)
        ]
        crossover_strings = [
            ms.strip()
            for ms in self._ga.crossover.split(definitions.PARAM_SEPARATOR)
        ]
        # The relative cost diversity coefficient is also needed by the crossover probability
        # method. Without the updater it stays NaN, and so does the probability.
        if (
            not population_mutator_strings
            or definitions.COST_DIVERSITY in population_mutator_strings
            or definitions.COST_DIVERSITY in crossover_strings
        ):
            return CostDiversityPopulationUpdater()
        return BasePopulationUpdater()
