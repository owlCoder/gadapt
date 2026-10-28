# GAdapt: Self-Adaptive Genetic Algorithm

A comprehensive and customizable genetic algorithm library.

## Table of Contents
- [Introduction](#introduction)
  - [What Innovations Does GAdapt Bring?](#what-innovations-does-gadapt-bring)
- [Installation](#installation)
- [Releases](#releases)
- [Source code](#source-code)
- [API Documentation](#api-documentation)
- [Usage](#usage)
  - [Parameter Settings](#parameter-settings)
  - [Parameters Description](#parameters-description)
  - [Previous Parameter Names](#previous-parameter-names)
  - [Adding Variables](#adding-variables)
  - [GA Execution and Optimisation Results](#ga-execution-and-optimisation-results)
- [GA Customisation](#ga-customisation)

## Introduction

[GAdapt](https://gadapt.com) is an open-source Python library for Genetic Algorithm optimization. Its distinguishing feature is **diversity-guided mutation**: instead of a fixed or time-based mutation rate, it measures how diverse the population is in every generation, and uses that to decide how much, where and how to mutate.

### What Innovations Does GAdapt Bring?

Evolutionary search is a trade-off between *exploration* (visiting new areas of the search space) and *exploitation* (fine-tuning existing solutions). Mutation influences both, and the best balance changes during a run. Fixed or time-dependent mutation rates, and schemes driven only by fitness, assume that convergence follows a predictable, often linear, path. That rarely holds for multimodal and high-dimensional problems, so mutation pressure ends up mismatched to the real state of the population: either wasted on redundant exploration, or too weak to avoid premature convergence.

Population diversity is a more direct signal of the convergence state. GAdapt tracks it at every generation and lets it regulate the whole mutation process: high diversity keeps mutation exploratory, and falling diversity shifts it towards exploitation.

#### Three complementary diversity measures

A single measure can be misleading. Candidate solutions with different decision variable values can have similar costs, and the variable values can converge while the costs still look diverse. GAdapt therefore combines three measures:

| Measure | What it measures | What it drives |
|---------|------------------|----------------|
| **Cost diversity** | Spread of the cost values in the population, relative to the initial population | The number of candidate solutions to mutate |
| **Parent diversity** | The distance between the two parents of a candidate solution: *structural* (difference of their variable values) or *cost* (difference of their costs). By default, one of the two is chosen at random in each generation | Which candidate solutions to mutate |
| **Variable columnar diversity** | Dispersion of the values of each decision variable (a column of the population) across the candidate solutions | The number of candidate solutions to mutate (using the average over all decision variables), how many and which decision variables to mutate, and how their values are altered |

Each measure is a coefficient between 0 and 1, where 0 means complete convergence and higher values mean more diversity. Cost diversity and variable columnar diversity are calculated on a logarithmic scale relative to the initial population, so they stay sensitive during the late, fine-tuning phase of the search.

#### Five mutation decisions, each guided by diversity

| Decision | Guided by | How | Parameter |
|----------|-----------|-----|-----------|
| How many candidate solutions to mutate | Cost diversity or variable columnar diversity | The lower the diversity, the more candidate solutions are mutated: none in the first generation, up to the user-defined maximum when the population has fully converged | *population_mutation* |
| Which candidate solutions to mutate | Parent diversity | Offspring of the most similar parents are preferred, since they bring the least new information | *population_mutation* |
| How many decision variables to mutate in each candidate solution | Variable columnar diversity | A random number up to a limit that shrinks as the population converges | *candidate_solution_mutation* |
| Which decision variables to mutate | Variable columnar diversity | The most converged decision variables (lowest diversity) are prioritized, probabilistically | *candidate_solution_mutation* |
| How the value of a decision variable is altered | Variable columnar diversity | A normally distributed change around the current value: its standard deviation follows the diversity, so it is practically unbiased while diversity is high, and a small, fine-tuning step as the variable converges. By default, each alteration is either this or a plain random draw, with equal probability | *decision_variable_mutation* |

#### How mutation changes during a run

- **Early in the run**, diversity is high, so few candidate solutions are mutated, but each one may change in many decision variables with unbiased values. This introduces substantial variation, with limited mutation pressure.
- **Later in the run**, as diversity falls, more candidate solutions are mutated, each in fewer decision variables (the most converged ones), with finer changes. Mutation becomes broad across the population, but gentle within each candidate solution.
- Optionally, while the best cost stagnates, the lower bound of the size of the changes shrinks (see *normal_distribution_mutation_min_std_dev_decay_generations*), so the mutation makes finer and finer adjustments exactly when the progress stalls.
- A constant share of plain random alterations is kept throughout the run, which preserves the ability to escape local optima even at deep convergence.

#### Choosing and combining the measures

- The parameters *population_mutation*, *candidate_solution_mutation* and *decision_variable_mutation* accept comma-separated combinations of these methods, see [Parameters Description](#parameters-description).
- Cost diversity works best when the convergence of costs is a reliable indicator of the convergence of decision variable values. For cost functions with many local minima of similar cost, parent diversity and variable columnar diversity are more informative. Variable columnar diversity has the most to offer with several decision variables, and with very few of them the other two measures carry more of the work.
- Every step (determining the rate, selecting candidate solutions and decision variables, altering values) is a separate component, so the diversity-guided components can be combined with other mutation approaches, see [GA Customisation](#ga-customisation).

#### Beyond mutation

GAdapt is a complete genetic algorithm library, and the diversity signals are not limited to mutation. The crossover probability can also be adaptive, following cost diversity or variable columnar diversity. Other supported features include elitism, "Random Immigrants", guaranteed uniqueness of candidate solutions, and optimization of both discrete and continuous variables. See [Parameters Description](#parameters-description) and [Adding Variables](#adding-variables).

## Installation

To install **GAdapt**, use **pip** with the following command:

```bash
pip install gadapt
```

GAdapt requires Python 3.10 or newer. [NumPy](https://numpy.org/) is installed automatically as a dependency.

## Releases
The latest releases of GAdapt can be found at the PyPI repository: [GAdapt on PyPI](https://pypi.org/project/gadapt/)

## Source Code
The source code is available on GitHub: [GAdapt on GitHub](https://github.com/bpzoran/gadapt/)

## API Documentation
For detailed API documentation, refer to: [GAdapt API Documentation](https://www.gadapt.com/api/)

## Usage
Below is an example optimizing variable values for a complex trigonometric function:
```python
from gadapt.ga import GA
import math

#trigonometric function definition
def trig_func(args):    
    return math.sqrt(abs(math.cos(args[0]))) + math.pow(math.cos(args[1]), 2) + math.sin(args[2]) + math.pow(args[3], 2) + math.sqrt(args[4]) + math.cos(args[5]) - (args[6]*math.sin(pow(args[6], 3)) + 1) + math.sin(args[0]) / (math.sqrt(args[0])/3 + (args[6]*math.sin(pow(args[6], 3)) + 1) ) / math.sqrt(args[4]) + math.cos(args[5])

#Instantiation of genetic algorithm for desired function
ga = GA(cost_function=trig_func)

#Adding variables (minimal value, maximal value and an optional step)
ga.add(1.0, 4.0, 0.01)
ga.add(37.0, 40.0, 0.01)
ga.add(78.0, 88.0, 0.1)
ga.add(-5.0, 4.0, 0.1)
ga.add(1.0, 100.0, 1)
ga.add(1.0, 4.0, 0.01)
ga.add(-1, -0.01, 0.005)

#Execution of the genetic algorithm
results = ga.execute()

#Printing results
print(results)
```

The possible output:
```
Min cost: -3.370583074871819
Number of iterations: 286
Parameter values:
0: 1.57
1: 39.27
2: 86.4
3: 0.0
4: 1.0
5: 3.14
6: -1.0
```

In this example, the genetic algorithm searches for the combination of seven parameters, bringing the lowest value for the passed function. The only mandatory attribute to the genetic algorithm is *cost_function*, and other attributes in this example took default values. Parameters to be optimized are added by the "add" method. There are seven parameters to be optimized in this example.
### Parameter Settings
GAdapt genetic algorithm can receive parameters through constructor, properties, or a combination of both. Below are the supported parameters:

Passing parameters through the class constructor:
```python
ga = GA(cost_function=trig_func,
    population_size=32,
    population_mutation="cost_diversity,parent_diversity",
    number_of_mutation_candidate_solutions=6,
    number_of_mutation_decision_variables=2,
    exit_check="min_cost",
    max_attempt_no=20,
    logging=True,
    timeout=3600)
```
Passing parameters through the class properties:
```python
ga = GA()
ga.cost_function = trig_func
ga.population_size=32
ga.population_mutation="cost_diversity,parent_diversity"
ga.number_of_mutation_candidate_solutions=6
ga.number_of_mutation_decision_variables=2
ga.exit_check="min_cost"
ga.max_attempt_no=20
ga.logging=True
ga.timeout=3600
```
Passing parameters through the class constructor and properties:
```python
ga = GA(cost_function=trig_func, population_size=32)
ga.population_mutation="cost_diversity,parent_diversity"
ga.number_of_mutation_candidate_solutions=6
ga.number_of_mutation_decision_variables=2
ga.exit_check="min_cost"
ga.max_attempt_no=20
ga.logging=True
ga.timeout=3600
```
### Parameters Description
**cost_function**=*None* - Custom function for the cost calculation (fitness). The optimisation goal is minimising the output of the cost function. *cost_function* must be the function with one argument - a list of values, where the index is the ordinal of adding parameters and the item is the parameter's value to be optimised. When adding parameters, there should be as many parameters as the function uses. The *cost_function* is the only mandatory parameter.

**population_size**=*32* - Number of candidate solutions in the population.

**keep_elitism_percentage**=*50* - The percentage of the best candidate solutions (by cost value) that are kept in the population from one generation to the next. The remaining candidate solutions are replaced by the offspring of the kept ones. For example, with *population_size* of 32 and *keep_elitism_percentage* of 50, the 16 best candidate solutions are kept and 16 new ones are created in each generation.

**number_of_crossover_parents**=*-1* - The number of candidate solutions in the mating pool, i.e. the number of parents selected for crossover in each generation. If its value is lower than 2, all kept candidate solutions (see *keep_elitism_percentage*) are used as parents.

**exit_check**=*"avg_cost"* - A criteria for the exit for the genetic algorithm.  
Supported values:
- *"avg_cost"* - The optimisation exit is triggered when the average cost of the kept part of the population (see *keep_elitism_percentage*) is not improved in the specified number of generations  
- *"min_cost"* - The optimisation exit is triggered when the minimal cost in the population is not improved in the specified number of generations  
- *"requested"* - The optimisation exit is triggered when the requested value reached
- *"generations"* - The optimisation exit requested number of generations defined by "number_of_generations" parameter is reached
    
**max_attempt_no**=*2* - This parameter only takes place when *exit_check* has value *"avg_cost"* or *"min_cost"*. It determines the number of generations in which there is no improvement in the average/minimal cost.

**requested_cost**=*sys.float_info.max* - This parameter only takes place when *exit_check* has value *"requested"*. It determines the requested value which causes the exit from the genetic algorithm

**number_of_generations**=*-1* - The maximal number of generations. The value *-1* means that the number of generations is not limited. When *exit_check* has value *"generations"*, it is the exit criterion: the genetic algorithm exits after this number of generations. When *exit_check* has value *"avg_cost"* or *"min_cost"*, it is an additional upper limit: the genetic algorithm exits when there is no improvement in *max_attempt_no* generations, or when this number of generations is reached, whichever comes first. The limit takes effect only if it is not lower than *max_attempt_no*. It does not apply when *exit_check* has value *"requested"*.

**timeout**=*600* - A number of seconds after which the genetic algorithm optimisation will exit, regardless of whether *exit_check* criteria is reached. When the timeout expires, *messages* in the results contain a warning.

**exit_function**=*None* - A function without arguments that is called in each generation. If it returns True, the genetic algorithm exits, regardless of the *exit_check* criteria. It can be used, for example, to stop the optimisation from the outside.

**parent_selection**=*"roulette_wheel"* - The algorithm for parent selection.  
Supported values:
- *"roulette_wheel"* - Roulette Wheel selection algorithm (also known as "Weighted Random Pairing"). The probabilities assigned to the candidate solutions in the mating pool are inversely proportional to their cost. A candidate solution with the lowest cost has the greatest probability of mating, while the candidate solution with the highest cost has the lowest probability of mating.  
- *"tournament"* - Tournament selection algorithm. It randomly picks small subsets (groups) of candidate solutions from the mating pool, and candidate solutions with the lowest cost in subsets become a parent. *"tournament"* can have an additional parameter separated from the *"tournament"* keyword by the comma. The other value represents a group size. For example, *"tournament,8"* means that the tournament parent selection algorithm is chosen, and each group contains up to 8 members. The default group size is 4.  
- *"from_top_to_bottom"* - From Top To Bottom selection algorithm starts at the top of the list and pairs the candidate solutions two at a time until the top kept candidate solutions are selected for mating. Thus, the algorithm pairs odd rows with even rows.  
- *"random"* - Random selection algorithm uses a uniform random number generator to select candidate solutions.  

**crossover**=*"blending"* - The crossover algorithm, optionally followed by a method for determining the crossover probability, separated by a comma.  
Supported crossover algorithms:
- *"blending"* - Blending crossover combines variable values from the two parents into new variable values in offsprings. One value of the offspring variable comes from a combination of the two corresponding values of the parental decision variables  
- *"uniform"* - Uniform crossover combines candidate solutions in a uniform way.
- *"differential"* - (opt-in) Differential crossover: each offspring is a parent plus a scaled difference of two other members of the population, applied to all decision variables together (scale in [0.5, 1.0]). Unlike *"blending"* and *"uniform"*, which treat every decision variable separately, it does not depend on the orientation of the coordinate axes, so it suits problems with strongly coupled decision variables. The crossover probability applies to the pair of parents. Example: `GA(cost_function=f, crossover="differential")`.

Supported methods for determining the crossover probability (the probability that the values of a decision variable are crossed between the two parents):
- *"fixed"* - The probability is defined by the *crossover_probability* parameter. This is used when no method is specified.  
- *"cost_diversity"* - The probability is adaptive. It lies between *crossover_min_probability* and *crossover_max_probability*, and it is higher when the diversity of costs in the population is higher.  
- *"variable_columnar_diversity"* - The probability is adaptive. It lies between *crossover_min_probability* and *crossover_max_probability*, and it is higher when the diversity of variable values in the population is higher.  

For example, *"blending,cost_diversity"* means that blending crossover is used, with the probability determined by the cost diversity. If more methods are specified, one of them is randomly chosen for each pair of parents.

**crossover_probability**=*0.5* - The probability for crossing the values of a decision variable between the two parents. It applies when the probability is determined by the *"fixed"* method (the default).

**crossover_min_probability**=*0.5* and **crossover_max_probability**=*1.0* - The lower and the upper bound for the adaptive crossover probability. They apply when the probability is determined by the *"cost_diversity"* or the *"variable_columnar_diversity"* method.
    
**percentage_of_mutation_candidate_solutions**=*50.0* - The percentage of mutated candidate solutions in the population. This value is applied to the *population_size* value and rounded to an integer value, giving the number of mutation candidate solutions. For example, if *population_size* has a value of 32, and *percentage_of_mutation_candidate_solutions* has a value of 10, the number of mutation candidate solutions will be 3. The calculated value is an upper bound - the actual number of mutated candidate solutions can vary from 1 to the calculated value. *percentage_of_mutation_candidate_solutions* only applies if *number_of_mutation_candidate_solutions* does not have a valid integer value equal to or higher than 0.

**number_of_mutation_candidate_solutions**=*-1* - The number of mutation candidate solutions in the population. In case it's value is equal to or higher than 0, it overrides *percentage_of_mutation_candidate_solutions*. This value is the upper bound - the actual number of mutated candidate solutions can vary from 1 to *number_of_mutation_candidate_solutions*.

**percentage_of_mutation_decision_variables**=*20* - The percentage of mutated decision variables in each candidate solution. It applies to the candidate solution size (number of decision variables in each candidate solution), and the calculated value rounds to an integer value. The calculated value is the upper bound - the actual number of mutated decision variables can vary from 1 to the calculated value. *percentage_of_mutation_decision_variables* only applies if *number_of_mutation_decision_variables* does not have a valid integer value equal to or higher than 0.

**number_of_mutation_decision_variables**=*-1* - The number of mutated decision variables in each candidate solution. In case it's value is equal to or higher than 0, it overrides *percentage_of_mutation_decision_variables*. This value is the upper bound - the number of mutated decision variables can vary from 1 to *number_of_mutation_decision_variables*.

**strict_mutation_decision_variable_limit**=*False* - By default, when *candidate_solution_mutation* contains *"variable_columnar_diversity"*, the number of mutated decision variables in a candidate solution can exceed *number_of_mutation_decision_variables* (or the value calculated from *percentage_of_mutation_decision_variables*): it is at least one fifth of the decision variables, and higher when the decision variables are diverse. If *True*, that value is a strict upper bound for every mutation of a candidate solution. This matters for problems with many binary or discrete decision variables, where changing one fifth of them at once is a large jump.

**columnar_diversity_metric**=*"log_relative"* - How the variable columnar diversity (the spread of the values of a decision variable in the population, compared with the initial spread) is measured. It drives the mutation when *"variable_columnar_diversity"* is used. By default (*"log_relative"*), the spread is measured on the logarithm of *(value - min_value) + 1*. Then it depends on the units of the decision variable and on where its values lie in the range: for a variable with a large range (for example, megawatts or kilometers), the diversity seems to vanish too early when the values gather near the upper bound, and the mutation stops before the optimum is reached precisely. *"linear"* measures the spread of the values relative to the range, so the search behaves the same in any units and anywhere in the range.

**population_mutation**=*"cost_diversity,variable_columnar_diversity,parent_diversity"* - A type of mutation for the entire population. Based on the value of this parameter, the number of mutation candidate solutions can be determined, along with how candidate solutions for the mutation will be selected.
Supported values:
- *"cost_diversity"* - It applies to the number of mutation candidate solutions. *"cost_diversity"* determines the number of mutated candidate solutions adaptively, using the diversity of costs in the population. Lower cost diversity means a higher number of mutated candidate solutions. The minimal value of mutated candidate solutions is 0, and the maximal value is determined by the value of *number_of_mutation_candidate_solutions* or *percentage_of_mutation_candidate_solutions* parameters. If *population_mutation* has a value other than *"cost_diversity"*, the number of mutation candidate solutions is a random value from 1 to *number_of_mutation_candidate_solutions* value (or to value determined by *percentage_of_mutation_candidate_solutions* value). *"cost_diversity"* means that the *"parent_diversity"* method is selected to select candidate solutions to be mutated. This method only determines the number of mutated candidate solutions, but not how candidate solutions are selected for the mutation.  
- *"variable_columnar_diversity"* - It applies to the number of mutation candidate solutions. Determines the number of mutated candidate solutions based on dispersion of variable values. The lower dispersion indicates the higher number of mutated candidate solutions. The minimal value of mutated candidate solutions is 0, and the maximal value is determined by the value of *number_of_mutation_candidate_solutions* or *percentage_of_mutation_candidate_solutions* parameters.
- *"parent_diversity"* - It applies to the way how mutation candidate solutions will be selected. *"parent_diversity"* selects candidate solutions to be mutated using the diversity of their parents. The more similar parents (lower parent diversity) mean a higher probability of mutation for the child. Based on the calculated parent diversity, candidate solutions may be selected by one of the selection methods, which is determined by the value of the *parent_diversity_mutation_candidate_solution_sampling* parameter.  
- *"random"* - It applies to the number of mutation candidate solutions and to the way how mutation candidate solutions will be selected. *"random"* selects candidate solutions to be mutated randomly, and randomly determines the number of mutated candidate solutions (with the upper bound of **number_of_mutation_candidate_solutions**)
- *"strict"* - It applies to the number of mutation candidate solutions. The strict number of candidate solutions will be mutated, determined by **number_of_mutation_candidate_solutions** parameter.

Population_mutation may have more values, separated by a comma. It means that more than one method can be chosen for the mutation of candidate solutions in the population. For example, *"cost_diversity,parent_diversity"* means that number of mutation candidate solutions will be determined by the cost diversity and the selection of candidate solutions to be mutated will be defined by parent diversity. *"cost_diversity,random"* means that the cost diversity will determine the number of mutation candidate solutions, and the selection of candidate solutions to be mutated will be chosen randomly.
    
**parent_diversity_mutation_candidate_solution_sampling**=*"roulette_wheel"* - The selection algorithm for mutating candidate solutions when *population_mutation* contains value *"parent_diversity"*. It only applies when *population_mutation* has value *"parent_diversity"*. It determines the way how candidate solutions are to be selected based on the diversity of their parents.  
Supported values:
- *"roulette_wheel"* - The Roulette Wheel selection algorithm (also known as "Weighted Random Pairing"). The probabilities assigned to the candidate solutions to be mutated are proportional to the similarity of their parents (inversely proportional to the parent diversity). A candidate solution with the lowest parent diversity has the greatest probability of mutation, while the candidate solution with the highest parent diversity has the lowest probability of mutation.  
- *"tournament"* - The Tournament selection algorithm. It randomly picks small subsets (groups) of candidate solutions, and candidate solutions with the lowest parent diversity (highest parent similarity) in subsets are chosen to be mutated. *"tournament"* can have an additional parameter separated from the *"tournament"* keyword by the comma. The other value represents a group size. For example, *"tournament,8"* means that the tournament mutation selection algorithm is chosen, and each group contains up to 8 members. The default group size is 4.  
- *"from_top_to_bottom"* - From Top To Bottom selection algorithm starts at the top of the list and selects candidate solutions for mutation.  
- *"random"* - Random selection algorithm uses a uniform random number generator to select candidate solutions for mutation. In this case, selection for mutation will not depend on parent diversity.  
    
**must_mutate_for_same_parents**=*True* - Indicates if completely the same parents must influence mutation for their children. In other words, each child will be mutated if it has parents with a diversity of value of 0. If *must_mutate_for_same_parents* has the value True, the number of mutated candidate solutions can outreach value determined by *number_of_mutation_candidate_solutions* or *percentage_of_mutation_candidate_solutions*

**candidate_solution_mutation**=*"variable_columnar_diversity,random"* - The type of decision variable selection in candidate solutions for mutation  
Supported values:
- *"variable_columnar_diversity"* - Considers the diversity of decision variables of the same type in the population. Lower diversity can mean that this decision variable approaches some local minimums, and therefore such decision variables increase the chance for mutation. Based on the calculated variable-columnar-diversity, candidate solutions may be selected by one of the selection methods, which is determined by the value of the *variable_columnar_diversity_mutation_decision_variable_sampling* parameter.  
- *"random"* - Decision variables are randomly selected for the mutation. Random number of decision variables for mutation is determined, up to *number_of_mutation_decision_variables*
- *"strict"* - Strict number of decision variables will be mutated, determined by *number_of_mutation_decision_variables* parameter.

**decision_variable_mutation**=*"variable_columnar_diversity,random"* - The type of assigning mutated values to decision variables
Supported values:
- *"normal_distribution"* - assigns normally distributed random number to the variable selected for mutation
- *"variable_columnar_diversity"* - assigns normally distributed random number to the variable selected for mutation, with standard deviation based on the variable-columnar-diversity coefficient
- *"cost_diversity"* - assigns normally distributed random number to the variable selected for mutation, with standard deviation based on the diversity of costs in the population. Higher cost diversity means a higher standard deviation.
- *"random"* - Random values are assigned to decision variables

**normal_distribution_mutation_min_std_dev**=*0.001* and **normal_distribution_mutation_max_std_dev**=*0.6* - The lower and the upper bound of the standard deviation of normally distributed mutated values. They apply when *decision_variable_mutation* contains *"variable_columnar_diversity"* or *"cost_diversity"*. The values are relative to the range of the variable (between 0 and 1), so 0.6 means 60% of the difference between the maximal and the minimal value of the variable. The maximum must be higher than the minimum. Otherwise, the default values are used. The lower bound limits how fine the adjustments of a converged decision variable can be, and for continuous variables, lowering it (for example to *0.0001*) often improves the final result. For discrete variables (with a step), the lower bound should not be below one step divided by the range of the variable, since a smaller standard deviation only rounds to the same value. See also *normal_distribution_mutation_min_std_dev_decay_generations*.

**normal_distribution_mutation_min_std_dev_decay_generations**=*None* - A number of generations, or *None*. By default (*None*), the lower bound of the standard deviation (*normal_distribution_mutation_min_std_dev*) is constant. If a number is set, the lower bound is divided by 10 for every such number of consecutive generations in which the minimal cost does not improve (down to *1e-9*), and it is restored as soon as the minimal cost improves. This way, the mutation makes finer and finer adjustments exactly when the progress stalls, and keeps larger steps as long as the optimization progresses. For discrete variables, the lower bound never goes below one step. A good starting point is *2.5*, together with *normal_distribution_mutation_min_std_dev* of *0.0001*. The optimization may then keep improving for longer, so it can use more cost function evaluations.

**variable_columnar_diversity_mutation_decision_variable_sampling**=*"roulette_wheel"* - the selection algorithm for mutating candidate solutions when *candidate_solution_mutation* has value *"variable_columnar_diversity"*. It only applies when *candidate_solution_mutation* has value *"variable_columnar_diversity"* . It determines the way how decision variables are to be selected based on the variable-columnar-diversity.  
Supported values:
- *"roulette_wheel"* - The Roulette Wheel selection algorithm (also known as "Weighted Random Pairing"). The probabilities assigned to the decision variables to be mutated are inversely proportional to their variable-columnar-diversity. A variable value with the lowest variable-columnar-diversity has the greatest probability of mutation, while the decision variable with the highest variable-columnar-diversity has the lowest probability of mutation.  
- *"tournament"* - The Tournament selection algorithm. It randomly picks small subsets (groups) of decision variables, and decision variables with the lowest variable-columnar-diversity in subsets are chosen to be mutated. *"tournament"* can have an additional parameter separated from the *"tournament"* keyword by the comma. The other value represents a group size. For example, *"tournament,3"* means that the tournament mutation selection algorithm is chosen, and each group contains up to 3 members. The default group size is 4.  
- *"from_top_to_bottom"* - From Top To Bottom selection algorithm starts at the top of the list and selects decision variables for mutation.  
- *"random"* - Random selection algorithm uses a uniform random number generator to select decision variables for mutation. In this case, selection for the mutation will not depend on the variable-columnar-diversity of the decision variable.  
    
**immigration_number**=*0* - Refers to the "Random Immigrants" concepts. This strategy introduces a certain number of individuals into the population during the evolution process. These new individuals are generated randomly and injected into the population.

**ensure_unique_individuals**=*None* - If this parameter has a True value, the genetic algorithm ensures that no two individuals have the same variable values: offspring and mutated candidate solutions that repeat values already seen during the optimisation are regenerated, so the cost function is not evaluated twice for the same values. Duplicates are only likely when the variables take values from a grid defined by the step, so the default (*None*) means *True* when all variables have a step, and *False* when any variable is continuous (added without a step). Set it explicitly to *True* or *False* to override this. Ensuring uniqueness adds some computation per generation, especially late in the optimisation, which is usually negligible compared to the cost function execution time.

**probe_cost_function**=*True* - Before the optimization, the parameter validation calls the cost function once with all minimal and once with all maximal values of the decision variables, to check that it returns a float. These two calls are real cost function evaluations, and they are not part of the search: their results are not added to the population. If the cost function is expensive, or if its evaluations are counted (for example, against a budget), set it to *False* to skip these two calls.

**constraint_handling**=*None* - How constraints are handled. With *None*, the cost function returns the cost, as in all examples above (constraints, if any, are the user's penalty inside the cost). With a technique name, the cost function returns a pair *(objective, violation)*, where *violation* is 0 for a feasible solution and positive otherwise (both finite, within ±10¹⁵⁰) (for example, the sum of the constraint violations), and GAdapt ranks the candidate solutions with that technique: *"penalty"* uses objective + *constraint_penalty_weight* · violation; *"adaptive_penalty"* starts from the same weight, doubles it after three generations in a row with an infeasible best candidate solution and divides it by 1.5 after three feasible ones; *"feasibility_rules"* puts every feasible solution before every infeasible one, compares feasible solutions by objective and infeasible ones by violation; *"epsilon"* works like *"feasibility_rules"*, but violations up to a level that decreases to 0 over the first half of *number_of_generations* count as feasible (it needs *number_of_generations* > 0; if the run stops earlier, the level may still be positive at the end). The survivors are chosen by the exact order of the technique; the adaptation (cost diversity, parent diversity), the parent selection and the immigration read a scalar of that order (*min_cost* reports it): the penalized cost clipped to ±10¹², or, for the rule-based techniques, a value in [1, 3] that saturates only far outside the scale of the initial objectives. The results then describe the best evaluated solution of the whole run: the feasible one with the smallest objective, or, if none is feasible, the one with the smallest violation (*best_objective*, *best_violation*, *feasible* and its *result_values*). It cannot be combined with a *mutation_operator_policy* other than *"legacy"*. With *probe_cost_function*, the two probe calls must return valid pairs.

```python
from gadapt.ga import GA

def objective_and_violation(args):
    x, y = args
    return (x - 2) ** 2 + (y - 1) ** 2, max(0.0, x + y - 2)  # minimize, subject to x + y <= 2

ga = GA(cost_function=objective_and_violation, constraint_handling="feasibility_rules",
        exit_check="generations", number_of_generations=80)
ga.add(-3.0, 3.0, 0.01)
ga.add(-3.0, 3.0, 0.01)
results = ga.execute()
print(results.best_objective, results.best_violation, results.result_values)
```

**constraint_penalty_weight**=*1000.0* - The weight of the violation for *constraint_handling="penalty"*, and the initial weight for *"adaptive_penalty"* (which then stays within a factor of 10⁶ of it). It must be positive, at most 10¹⁰⁰.

**logging**=*False* - If this parameter has a True value, the log file will be created in the current working directory. The log file contains the flow of genetic algorithm execution, along with values of candidate solutions, decision variables and cost functions in each generation

### Previous Parameter Names
In earlier versions, the terms *chromosome*, *gene*, *allele* and *cross diversity* were used. They are now called *candidate solution*, *decision variable*, *variable value* and *variable columnar diversity*. The previous *GA* parameter names are still accepted, both in the constructor and as properties, but they are deprecated: using them emits a *DeprecationWarning*, and they will be removed in a future release.

| Previous name | Current name |
|---|---|
| *number_of_mutation_chromosomes* | *number_of_mutation_candidate_solutions* |
| *percentage_of_mutation_chromosomes* | *percentage_of_mutation_candidate_solutions* |
| *parent_diversity_mutation_chromosome_sampling* | *parent_diversity_mutation_candidate_solution_sampling* |
| *chromosome_mutation* | *candidate_solution_mutation* |
| *gene_mutation* | *decision_variable_mutation* |
| *number_of_mutation_genes* | *number_of_mutation_decision_variables* |
| *percentage_of_mutation_genes* | *percentage_of_mutation_decision_variables* |
| *cross_diversity_mutation_gene_sampling*, *cross_diversity_mutation_decision_variable_sampling* | *variable_columnar_diversity_mutation_decision_variable_sampling* |

The same applies to the value *"cross_diversity"* of *population_mutation*, *candidate_solution_mutation*, *decision_variable_mutation* and *crossover*, which is now *"variable_columnar_diversity"*. The previous value is replaced by the current one and a *DeprecationWarning* is emitted.

```python
ga = GA(cost_function=trig_func, chromosome_mutation="cross_diversity,random")  # works, but emits DeprecationWarnings
ga.number_of_mutation_genes = 2                                                    # works, but emits a DeprecationWarning
```
Passing both a previous name and its replacement with different values raises a *TypeError*. Only the *GA* parameters and their option values have aliases: the module paths and class names used by custom factories (see *GA Customisation*) and the *value* property of a variable value (previously *variable_value*) changed without aliases.

### Adding Variables
Variables to be optimized are added by calling the *add* method of the *GA* object:
```
ga.add(min_value, max_value, step=None)
```
The minimum and maximum value determine the range of possible variable values, and both should always be given. The *step* is **optional**, and it determines what kind of variable is optimized:

| Call | Kind of variable | Possible values |
|------|------------------|-----------------|
| `ga.add(1.0, 4.0, 0.01)` | discrete (with a step) | 1.0, 1.01, 1.02, ..., 4.0 |
| `ga.add(1.0, 4.0)` | continuous (no step) | any real number between 1.0 and 4.0 |

**If the step is not defined, continuous optimization is performed for that variable.** Its values are not restricted to a grid, and they are not rounded: random values, crossover and mutation can produce any real number in the range, so the optimized value may look like `1.3701139890548797`. With a step, the values are taken from the grid defined by the minimum value and the step (`min_value + k * step`, never above the maximum), rounded to the number of decimal places of the step.

Some details:
- Leaving the step out is the same as passing `step=None`.
- The step must be positive. A step of `0` or a negative step is not a way to say "no step": it fails the validation with the message *Step must be positive float value!*. To get a continuous variable, leave the step out.
- A step so small that the range contains more than 10<sup>9</sup> steps is treated as no step, so such a variable is also continuous.
- Discrete and continuous variables can be mixed in the same *GA* object. The default of *ensure_unique_individuals* depends on it: it is *True* only when all variables have a step (see its description above).

For example:
```python
ga.add(1.0, 4.0, 0.01)
```
means that the corresponding parameter can have values between 1.0 and 4.0, and the step for changing variable values in optimization is 0.01, whereas
```python
ga.add(1.0, 4.0)
```
means that the corresponding parameter can have any value between 1.0 and 4.0.

A complete example with one discrete and one continuous variable:
```python
from gadapt.ga import GA

def sphere(args):
    return args[0] ** 2 + args[1] ** 2

ga_mixed = GA(cost_function=sphere)
ga_mixed.add(-5, 5, 1)    # args[0]: discrete, can be -5, -4, ..., 5
ga_mixed.add(-5.0, 5.0)   # args[1]: no step, so continuous, can be any real number between -5.0 and 5.0
print(ga_mixed.execute())
```

An example with all variables continuous, using the Rastrigin function, a standard multimodal benchmark function. Its global minimum is 0, at the point where all variables are 0:
```python
import numpy as np
from gadapt.ga import GA

def rastrigin(args):
    x = np.asarray(args)
    return 10 * len(x) + np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x))

ga_continuous = GA(cost_function=rastrigin)
for _ in range(5):
    ga_continuous.add(-5.12, 5.12)   # no step, so each of the five variables is continuous
print(ga_continuous.execute())
```

The possible output:
```
Min cost: 1.5554049042521e-05
Number of iterations: 231
Parameter values:
0: -3.6805571508315964e-08
1: -4.036152602508579e-06
2: 4.895884131551171e-07
3: -0.00027987533973038896
4: 7.337156119654347e-06
```
All optimized values are real numbers very close to 0. Since the variables are continuous, they are not restricted to a grid and are not rounded.

The order in which the variables are added must match the indices of the variables in the cost function. For example, for the given function:
```python
def some_func(args):
      return math.sqrt(abs(args[0])) + math.pow(args[1], 2)
```
and instantiation of the genetic algorithm object:
```python
ga = GA(cost_function=some_func)
```
, adding variables may look as it follows:
```python
ga.add(-25, 25, 1) # Refers to args[0]
ga.add(-5, 5, 0.1) # Refers to args[1]

```
### GA Execution and Optimisation Results
Genetic algorithm optimization executes by calling *execute* method, without parameters. This method returns the object of type *GAResults*, which contain following properties:
- **success**  - Indicates if genetic algorithm optimisation executed successfully.
- **min_cost** - The minimal cost for optimized variables
- **number_of_iterations** - The number of generations executed before the optimisation exited
- **result_values** - The dictionary that contains variables' optimized values. The key of this dictionary is the sequence number of variable adding, and also the argument index in the cost function. The value of this dictionary is the optimized value for the variable.
- **best_objective**, **best_violation**, **feasible** - With *constraint_handling*, the objective, the violation and the feasibility of the best evaluated solution of the run (*result_values* then holds its values and *min_cost* the internal ranking value of the final best candidate solution); otherwise NaN, NaN and None.
- **messages** - Additional messages of the optimizations. This is a tuple structure where first value is a message level ("INFO", "WARNING" or "ERROR"), and the second value is the message text.

For example, for the given function:
```python
def some_func(args):
      return math.sqrt(abs(args[0])) + math.pow(args[1], 2)
```
, instantiation of the genetic algorithm object:
```python
ga = GA(cost_function=some_func)
```
, and variables adding:
```python
ga.add(-25, 25, 1.0) # Refers to args[0]
ga.add(-5, 5, 0.1) # Refers to args[1]

```
, the genetic algorithm execution can return results as it follows:
```python
results = ga.execute()
if results.success: # indicates if the optimisation succeeded
    print("Minimal cost: " + str(results.min_cost))
    print("Number of iterations: " + str(results.number_of_iterations))
    print("Parameter values:")
    for x in results.result_values:
        print(str(x) + ": " + str(results.result_values[x]))               
else:
    print("Calculation not successful.")

for m in results.messages:
    print(m[0] + ": " + m[1])
```
The output may look like it follows:
```
Minimal cost: 0.0
Number of iterations: 19
Parameter values:
0: 0.0
1: 0.0
```
In the case of some inadequate setting, e.g. adding not enough parameters, the output might look like it follows:
```
Calculation not succesful.
ERROR: Inadequate number of parameters for the passed function!
```
Casting results to string returns a readable strings containing all relevant data. For example:
```python
s = str(results)
print(s)
```
might return the following output:
```
Min cost: 0.0
Number of iterations: 21
Parameter values:
0: 0.0
1: 0.0
```

## GA Customisation
GAdapt follows clean architecture and SOLID principles, allowing easy customization. Create new implementations of abstract classes and pass them to the genetic algorithm through a factory object.

The factory creates all objects used by the genetic algorithm (selectors, mutators, crossover, exit checker, etc.), based on the parameters of the *GA* object. To replace one of them, subclass *GAFactory* and override the corresponding *_get_...* method. The factory is initialized by the *GA* object when *execute* is called, so objects that depend on the *GA* parameters should be created inside the overridden method.

For example, customizing the candidate solution mutation selector:

```python
import math
from gadapt.factory.ga_factory import GAFactory
from gadapt.ga import GA
from gadapt.operations.mutation.population_mutation.base_candidate_solution_mutation_selector import BaseCandidateSolutionMutationSelector


class BottomMutationSelector(BaseCandidateSolutionMutationSelector):
    """
    Candidate solution mutation selector which selects mutating candidate solutions from the bottom of
    existing unallocated candidate solutions sorted by the cost function value
    """

    def _get_candidate_solutions_for_mutation(self):
        unallocated_candidate_solutions = self._get_unallocated_candidate_solutions(
            lambda candidate_solution: self.population.options.cost_function([g.value for g in candidate_solution])
        )
        return unallocated_candidate_solutions[len(unallocated_candidate_solutions) - self.number_of_mutation_candidate_solutions:]


class BottomMutationFactory(GAFactory):
    def _get_candidate_solution_mutation_selector(self):
        rate_determinator, _ = self._get_candidate_solution_mutation_rate_determinators()
        return BottomMutationSelector(rate_determinator, self.get_decision_variable_mutation_selector())


def some_func(args):
    return math.sqrt(abs(args[0])) + math.pow(args[1], 2)


ga = GA(cost_function=some_func, factory=BottomMutationFactory())
ga.add(-25, 25, 1)
ga.add(-5, 5, 0.1)

print(ga.execute())
```
