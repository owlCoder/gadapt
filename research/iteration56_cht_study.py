"""I56: constraint-handling technique (CHT) x GAdapt self-adaptation on discrete ORPD.

Frozen protocol: research/ITERATION56_PROTOCOL.md (commit 3f09eb9). Instrument: research/iteration56_orpd.py.
The GAdapt library is not modified: CHTs, the common-signal arm and the fixed arms are research subclasses passed
through `GAFactory`. Every run executes in a fresh process (ParentDiversityCandidateSolutionUpdater is a singleton).

  python research/iteration56_cht_study.py validate
  python research/iteration56_cht_study.py <stage> [workers]      stage: dev_ref | dev_fxm | dev_fxt | rehearsal |
                                                                         test_ref | test
  python research/iteration56_cht_study.py analyse
"""
import hashlib
import json
import math
import os
import random
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for path in (REPO, HERE):
    if path not in sys.path:
        sys.path.insert(0, path)

import numpy as np  # noqa: E402

from gadapt.factory.ga_factory import GAFactory  # noqa: E402
from gadapt.ga import GA  # noqa: E402
from gadapt.operations.candidate_solution_update.parent_diversity_candidate_solution_updater import (  # noqa: E402
    ParentDiversityCandidateSolutionUpdater,
)
from gadapt.operations.cost_finding.elitism_cost_finder import ElitismCostFinder  # noqa: E402
from gadapt.operations.mutation.candidate_solution_mutation.base_decision_variable_mutation_selector import (  # noqa: E402,E501
    BaseDecisionVariableMutationSelector,
)
from gadapt.operations.mutation.decision_variable_mutation.composed_decision_variable_mutator import (  # noqa: E402
    ComposedDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_decision_variable_mutator import (  # noqa: E402,E501
    NormalDistributionDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.normal_distribution_variable_columnar_diversity_decision_variable_mutator import (  # noqa: E402,E501
    NormalDistributionVariableColumnarDiversityDecisionVariableMutator,
)
from gadapt.operations.mutation.decision_variable_mutation.random_decision_variable_mutator import (  # noqa: E402
    RandomDecisionVariableMutator,
)
from gadapt.operations.mutation.population_mutation.base_candidate_solution_mutation_selector import (  # noqa: E402
    BaseCandidateSolutionMutationSelector,
)
from gadapt.operations.population_update.cost_diversity_population_updater import (  # noqa: E402
    CostDiversityPopulationUpdater,
)
from iteration56_orpd import ORPD  # noqa: E402

OUT = os.path.join(HERE, "results", "iteration56")
NETWORKS = ("case14", "case57", "case118")
RESOLUTIONS = (9, 17, 33)
DEV_SCENARIOS = ((0.95, 101), (1.05, 102))
TEST_SCENARIOS = ((0.90, 201), (1.00, 202), (1.10, 203), (1.15, 204))
SPREAD = 0.1
BUDGET = 3000
REF_BUDGET = 30000
TOL = 1e-6
V_FAIL = 10.0
SP_WEIGHT = 1000.0
LAMBDA0 = 1000.0
EPS_PERCENTILE = 20
EPS_TC, EPS_CP = 0.5, 5
CHTS = ("SP", "AP", "FR", "EC", "SPT")
PURPOSE = dict(test=1, dev=2, test_ref=3, dev_ref=4)


def seed_of(purpose, network, resolution, scenario_index, s):
    """§2: collision-free; scenario_index: development 0, 1; test 2..5."""
    assert 1 <= s <= 99
    return (10 ** 7 * PURPOSE[purpose] + 10 ** 5 * NETWORKS.index(network) + 10 ** 3 * resolution
            + 10 ** 2 * scenario_index + s)


# ------------------------------------------------------------------ evaluation (§3)

class Raw:
    __slots__ = ("f", "V", "failed")

    def __init__(self, f, V, failed):
        self.f, self.V, self.failed = f, V, failed

    @property
    def feasible(self):
        return not self.failed and self.V == 0.0


class Shared:
    """GA.execute() deep-copies the GA (cost function and factory included); these objects must stay shared."""

    def __deepcopy__(self, memo):
        return self


class Evaluator(Shared):
    """Counts power flows, caches raw (f, V) by genotype, records outcomes from actual evaluations only."""

    def __init__(self, problem, budget, target):
        self.problem, self.budget, self.target = problem, budget, target
        self.f_ref = problem.opf_losses
        assert self.f_ref > 0
        self.calls = 0
        self.cache = {}
        self.best_feasible = math.inf
        self.first_feasible = None
        self.first_target = None
        self.failures = 0
        self.min_violation = math.inf
        self.sequence = hashlib.sha256()
        self.initial = []  # the first 64 evaluated genotypes (initial-population check)

    @property
    def done(self):
        return self.calls >= self.budget

    def __call__(self, values):
        key = tuple(values)
        if self.done:
            return 0.0  # post-budget: not recorded, not cached
        self.calls += 1
        info = self.problem.evaluate(np.asarray(values, float))
        if not info["converged"]:
            raw = Raw(2.0 * self.f_ref, V_FAIL, True)
            self.failures += 1
        else:
            v = float(sum(max(0.0, c - TOL) for c in info["violations"].values()))
            assert info["losses"] > 0
            raw = Raw(float(info["losses"]), v, False)
        self.cache[key] = raw
        if len(self.initial) < 64:
            self.initial.append(key)
        self.sequence.update(np.asarray(values, float).tobytes() + np.array([raw.f, raw.V], float).tobytes())
        self.min_violation = min(self.min_violation, raw.V)
        if raw.feasible:
            self.best_feasible = min(self.best_feasible, raw.f)
            if self.first_feasible is None:
                self.first_feasible = self.calls
            if self.first_target is None and self.target(raw.f):
                self.first_target = self.calls
        return raw.f + SP_WEIGHT * raw.V

    def raw_of(self, candidate):
        values = [vv.value for vv in sorted(candidate, key=lambda vv: vv.decision_variable.variable_id)]
        raw = self.cache.get(tuple(values))
        if raw is None:  # only after the budget: ranked last, never recorded
            return Raw(2.0 * self.f_ref, V_FAIL, True)
        return raw


# ------------------------------------------------------------------ CHTs (§4)

class CHT(Shared):
    def __init__(self, name, f_ref):
        assert name in CHTS
        self.name, self.f_ref = name, f_ref
        self.lam = LAMBDA0
        self.infeasible_streak = self.feasible_streak = 0
        self.eps0 = None
        self.eps = 0.0
        self.trace = []

    def u(self, f):
        return f / (f + self.f_ref)

    def update(self, generation, previous_best, initial_raws, tau):
        """Step (2): parameters from completed history; frozen until the next generation's step (2)."""
        if self.name == "AP" and previous_best is not None:
            if previous_best.feasible:
                self.feasible_streak += 1
                self.infeasible_streak = 0
            else:
                self.infeasible_streak += 1
                self.feasible_streak = 0
            if self.infeasible_streak >= 3:
                self.lam *= 2.0
                self.infeasible_streak = self.feasible_streak = 0
            elif self.feasible_streak >= 3:
                self.lam /= 1.5
                self.infeasible_streak = self.feasible_streak = 0
        if self.name == "EC":
            if self.eps0 is None:
                self.eps0 = float(np.percentile([r.V for r in initial_raws], EPS_PERCENTILE))
            self.eps = self.eps0 * (1 - tau / EPS_TC) ** EPS_CP if tau < EPS_TC else 0.0
        self.trace.append(dict(generation=generation, lam=self.lam, eps=self.eps, tau=tau))

    def merit(self, raw):
        if self.name in ("SP", "SPT", "AP"):
            weight = self.lam if self.name == "AP" else SP_WEIGHT
            p = raw.f + weight * raw.V
            return 1.0 + p / (p + self.f_ref) if self.name == "SPT" else p
        if raw.failed:
            return 3.0
        ok = raw.V == 0.0 if self.name == "FR" else raw.V <= self.eps
        return 1.0 + self.u(raw.f) if ok else 2.0 + raw.V / (1.0 + raw.V)


class CHTCostFinder(ElitismCostFinder):
    """§4 event order: (1) evaluate new, (2) update parameters, (3) re-scalarize ALL, (4) sort and truncate."""

    def __init__(self, evaluator, cht, log):
        super().__init__()
        self.evaluator, self.cht, self.log = evaluator, cht, log
        self.previous_best = None
        self.generation = 0

    def _find_costs_for_population(self):
        for c in self.population:
            if math.isnan(c.cost_value):
                self._execute_function(self.population.options.cost_function, c)
        raws = {id(c): self.evaluator.raw_of(c) for c in self.population}
        tau = self.evaluator.calls / self.evaluator.budget
        self.cht.update(self.generation, self.previous_best, list(raws.values()), tau)
        for c in self.population:
            c.cost_value = self.cht.merit(raws[id(c)])
        super()._find_costs_for_population()
        survivors = [self.evaluator.raw_of(c) for c in self.population]
        consistent = all(c.cost_value == self.cht.merit(r) for c, r in zip(self.population, survivors))
        self.previous_best = self.evaluator.raw_of(self.population.best_individual)
        self.log.append(dict(generation=self.generation, calls=self.evaluator.calls,
                             feasible_survivors=sum(r.feasible for r in survivors) / len(survivors),
                             min_merit=min(c.cost_value for c in self.population),
                             max_merit=max(c.cost_value for c in self.population), consistent=consistent))
        self.generation += 1


# ------------------------------------------------------------------ AD-C: common signal (§5)

class _SwappedCosts:
    """Temporarily replaces cost_value by the FR merit (the common signal) and restores it."""

    def __init__(self, candidates, evaluator, fr):
        self.candidates, self.evaluator, self.fr = list(candidates), evaluator, fr

    def __enter__(self):
        self.saved = [c.cost_value for c in self.candidates]
        for c in self.candidates:
            c.cost_value = self.fr.merit(self.evaluator.raw_of(c))

    def __exit__(self, *exc):
        for c, value in zip(self.candidates, self.saved):
            c.cost_value = value


class CommonSignalCostDiversityUpdater(CostDiversityPopulationUpdater):
    def __init__(self, evaluator, fr):
        super().__init__()
        self.evaluator, self.fr = evaluator, fr

    def _update_population(self):
        with _SwappedCosts(self.population.candidate_solutions, self.evaluator, self.fr):
            super()._update_population()


class CommonSignalParentDiversityUpdater(ParentDiversityCandidateSolutionUpdater):
    _instance = None
    evaluator = fr = None

    def calculate_parent_cost_diversity_coefficient(self, father_candidate_solution, mother_candidate_solution):
        with _SwappedCosts((father_candidate_solution, mother_candidate_solution), self.evaluator, self.fr):
            return super().calculate_parent_cost_diversity_coefficient(father_candidate_solution,
                                                                       mother_candidate_solution)


# ------------------------------------------------------------------ FX arms (§5)

class FixedSigmaNormalMutator(NormalDistributionDecisionVariableMutator):
    """GAdapt's Gaussian operator with only the standard deviation fixed."""

    def __init__(self, sigma, log):
        super().__init__()
        self.sigma, self.log = sigma, log

    def _calculate_normal_distribution_standard_deviation(self):
        self.log.append(self.sigma)
        return self.sigma


class FixedCountDecisionVariableMutationSelector(BaseDecisionVariableMutationSelector):
    """Exactly v decision variables, uniformly without replacement (no second draw)."""

    def __init__(self, v, mutator, log):
        super().__init__(None, mutator)
        self.v, self.log = v, log

    def _mutate_candidate_solution(self):
        variables = list(self.candidate_solution)
        random.shuffle(variables)
        v = min(len(variables), self.v)
        for g in variables[:v]:
            self._mutate_decision_variable(g)
        self.log.append(len(set(self.candidate_solution.mutated_variables_id_list)))
        return v


class FixedCountCandidateSolutionMutationSelector(BaseCandidateSolutionMutationSelector):
    """k = 0 for an empty pool, else min(|pool|, max(1, round(a·|pool|))); uniform without replacement."""

    def __init__(self, a, decision_variable_mutation_selector, log):
        super().__init__(None, decision_variable_mutation_selector)
        self.a, self.log = a, log

    def _get_candidate_solutions_for_mutation(self):
        return []

    def mutate(self, population):
        self.population = population
        pool = self._get_unallocated_candidate_solutions()
        k = 0 if not pool else min(len(pool), max(1, round(self.a * len(pool))))
        chosen = random.sample(pool, k) if k else []
        self.log.append(dict(pool=len(pool), k=k))
        self._mutate_population(chosen)


# ------------------------------------------------------------------ instrumentation of AD-N (for FX-M, §5)

class Instrument:
    """Logging-only wrappers; behaviour (and the RNG stream) is unchanged (tested)."""

    def __init__(self):
        self.population_events, self.v_fractions, self.sigmas = [], [], []
        self.repair_mutations = 0

    def install(self, selector, d):
        instrument = self
        seen = set()
        original_mutate = selector.mutate
        original_population = selector._mutate_population

        def mutate(population):
            selector.population = population
            seen.clear()
            pool = selector._get_unallocated_candidate_solutions()
            instrument._pool = len(pool)
            instrument._mutated = 0
            original_mutate(population)
            instrument.population_events.append(dict(pool=instrument._pool, k=instrument._mutated))

        def mutate_population(candidates):
            instrument._mutated = len(candidates)
            return original_population(candidates)

        selector.mutate = mutate
        selector._mutate_population = mutate_population
        decision_selector = selector._decision_variable_mutation_selector
        original_decision = decision_selector.mutate

        def decision_mutate(c, n):
            original_decision(c, n)
            if id(c) in seen:
                instrument.repair_mutations += 1
            else:
                seen.add(id(c))
                instrument.v_fractions.append(len(c.mutated_variables_id_list) / d)

        decision_selector.mutate = decision_mutate

    def sigma_hook(self):
        instrument = self
        original = NormalDistributionVariableColumnarDiversityDecisionVariableMutator.\
            _calculate_normal_distribution_standard_deviation

        def sigma(mutator):
            value = original(mutator)
            instrument.sigmas.append(float(value))
            return value

        NormalDistributionVariableColumnarDiversityDecisionVariableMutator.\
            _calculate_normal_distribution_standard_deviation = sigma


class StudyFactory(Shared, GAFactory):
    def __init__(self, evaluator, cht, arm, log, fixed=None, instrument=None):
        super().__init__()
        self.evaluator, self.cht, self.arm, self.log = evaluator, cht, arm, log
        self.fixed, self.instrument = fixed, instrument
        self.fx_log, self.sigma_log, self.v_log = [], [], []

    def _get_cost_finder(self):
        return CHTCostFinder(self.evaluator, self.cht, self.log)

    def _get_population_updater(self):
        if self.arm == "AD-C":
            return CommonSignalCostDiversityUpdater(self.evaluator, CHT("FR", self.evaluator.f_ref))
        return super()._get_population_updater()

    def get_candidate_solution_updater(self):
        if self.arm == "AD-C":
            updater = CommonSignalParentDiversityUpdater()
            CommonSignalParentDiversityUpdater.evaluator = self.evaluator
            CommonSignalParentDiversityUpdater.fr = CHT("FR", self.evaluator.f_ref)
            return updater
        return super().get_candidate_solution_updater()

    def _get_candidate_solution_mutation_selector(self):
        if self.arm in ("FX-M", "FX-T"):
            a, b, sigma = self.fixed
            d = self.evaluator.problem.d
            mutator = ComposedDecisionVariableMutator()  # same order as GAdapt's default: reset, then Gaussian
            mutator.append(RandomDecisionVariableMutator())
            mutator.append(FixedSigmaNormalMutator(sigma, self.sigma_log))
            v = min(d, max(1, round(b * d)))
            return FixedCountCandidateSolutionMutationSelector(
                a, FixedCountDecisionVariableMutationSelector(v, mutator, self.v_log), self.fx_log)
        selector = super()._get_candidate_solution_mutation_selector()
        if self.instrument is not None:
            self.instrument.install(selector, self.evaluator.problem.d)
        return selector


# ------------------------------------------------------------------ one run

def make_target(reference):
    """§6: V = 0 and f <= L*(1 + 0.01) + 0.01 MW; without a reference the target is feasibility."""
    if reference is None or not math.isfinite(reference):
        return lambda f: True
    return lambda f: f <= reference * 1.01 + 0.01


def run(task):
    """task: dict(network, resolution, scenario=(load_factor, scenario_seed), cht, arm, seed, budget,
    reference, fixed, instrument). Returns the outcome record (§3, §6)."""
    network, resolution = task["network"], task["resolution"]
    load_factor, scenario_seed = task["scenario"]
    problem = ORPD(network, resolution, load_factor, SPREAD, scenario_seed)
    evaluator = Evaluator(problem, task["budget"], make_target(task.get("reference")))
    cht = CHT(task["cht"], evaluator.f_ref)
    log = []
    instrument = Instrument() if task.get("instrument") else None
    factory = StudyFactory(evaluator, cht, task["arm"], log, task.get("fixed"), instrument)
    if instrument is not None:
        instrument.sigma_hook()
    random.seed(task["seed"])
    np.random.seed(task["seed"])
    ga = GA(cost_function=evaluator, probe_cost_function=False, exit_check="generations",
            number_of_generations=10 ** 9, exit_function=lambda *a, **k: evaluator.done, timeout=10 ** 6,
            factory=factory)
    for lo, hi, step in zip(problem.lo, problem.hi, problem.step):
        ga.add(float(lo), float(hi), float(step))
    result = ga.execute()
    first = evaluator.first_target
    record = dict(task={k: v for k, v in task.items() if k != "instrument"}, calls=evaluator.calls,
                  complete=evaluator.calls >= task["budget"], success=bool(result.success),
                  messages=[str(m) for m in result.messages][:3],
                  T=(first / task["budget"]) if first is not None else 1.0,
                  first_target=first, first_feasible=evaluator.first_feasible,
                  best_feasible=evaluator.best_feasible if math.isfinite(evaluator.best_feasible) else None,
                  min_violation=evaluator.min_violation, failures=evaluator.failures, generations=len(log),
                  sequence=evaluator.sequence.hexdigest(), initial=[list(k) for k in evaluator.initial],
                  trace=log, cht_trace=cht.trace)
    if instrument is not None:
        record["instrument"] = dict(population_events=instrument.population_events,
                                    v_fractions=instrument.v_fractions, sigmas=instrument.sigmas,
                                    repair_mutations=instrument.repair_mutations)
    if task["arm"] in ("FX-M", "FX-T"):
        record["fx"] = dict(population_events=factory.fx_log, sigmas=len(factory.sigma_log), v=factory.v_log)
    return record


def run_plain(task):
    """Plain GAdapt (default factory) on the SP scalar, the same evaluator and settings (bit-identity check)."""
    network, resolution = task["network"], task["resolution"]
    load_factor, scenario_seed = task["scenario"]
    problem = ORPD(network, resolution, load_factor, SPREAD, scenario_seed)
    evaluator = Evaluator(problem, task["budget"], make_target(task.get("reference")))
    random.seed(task["seed"])
    np.random.seed(task["seed"])
    ga = GA(cost_function=evaluator, probe_cost_function=False, exit_check="generations",
            number_of_generations=10 ** 9, exit_function=lambda *a, **k: evaluator.done, timeout=10 ** 6)
    for lo, hi, step in zip(problem.lo, problem.hi, problem.step):
        ga.add(float(lo), float(hi), float(step))
    ga.execute()
    return dict(calls=evaluator.calls, sequence=evaluator.sequence.hexdigest())


def run_pool(tasks, workers, function=None):
    with Pool(workers, maxtasksperchild=1) as pool:
        return list(pool.imap(function or run, tasks))


if __name__ == "__main__":
    print(__doc__)
