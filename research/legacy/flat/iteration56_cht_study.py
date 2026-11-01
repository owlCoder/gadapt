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
POPULATION_SIZE = 32  # GAdapt default


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
        self.initial = []  # genotypes of the initial population (first population_size evaluations)
        self.errors = 0

    @property
    def done(self):
        return self.calls >= self.budget

    def __call__(self, values):
        try:
            return self._call(values)
        except Exception:
            self.errors += 1  # GAdapt swallows cost-function exceptions; the run is then an execution failure
            raise

    def _call(self, values):
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
        if len(self.initial) < POPULATION_SIZE:
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
        # v_fractions: nominal population mutation only (first decision-selector call per individual);
        # sigmas: ALL Gaussian mutations, including repairs (protocol §5: "po svim Gausovim mutacijama")
        self.population_events, self.v_fractions, self.sigmas = [], [], []
        self.repair_mutations = 0  # uniqueness retries inside population mutation
        self.crossover_repairs, self.crossover_repair_variables = 0, []

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

    def install_repair(self, crossover):
        """Duplicate repair in crossover uses its own selector; counted separately from nominal mutations."""
        instrument = self
        mutator = crossover._mutator
        original = mutator.mutate

        def repair(c, n):
            original(c, n)
            instrument.crossover_repairs += 1
            instrument.crossover_repair_variables.append(len(c.mutated_variables_id_list))

        mutator.mutate = repair

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

    def _get_crossover(self):
        crossover = super()._get_crossover()
        if self.instrument is not None:
            self.instrument.install_repair(crossover)
        return crossover

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
    """Structured wrapper: an exception becomes an execution-failure record (retried once by execute())."""
    import traceback
    try:
        return _run(task)
    except Exception:
        return dict(task={k: v for k, v in task.items() if k != "instrument"}, ok=False, complete=False,
                    error=traceback.format_exc()[-2000:], T=None)


def _run(task):
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
    complete = evaluator.calls >= task["budget"]
    record = dict(task={k: v for k, v in task.items() if k != "instrument"}, calls=evaluator.calls,
                  complete=complete, success=bool(result.success), errors=evaluator.errors,
                  ok=complete and bool(result.success) and evaluator.errors == 0,
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
                                    repair_mutations=instrument.repair_mutations,
                                    crossover_repairs=instrument.crossover_repairs,
                                    crossover_repair_variables=instrument.crossover_repair_variables)
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


# ------------------------------------------------------------------ stages (§5–§7, §10)

GADAPT_CHTS = ("SP", "AP", "FR", "EC")
FXT_GRID = [(a, b, sigma) for a in (0.25, 0.5, 0.75) for b in (0.1, 0.2, 0.4) for sigma in (0.02, 0.05, 0.15)]
FXM_SEEDS, REHEARSAL_SEEDS = (1, 2, 3), (11, 12, 13, 14, 15)  # development streams (purpose 2), disjoint
TEST_ARMS = ([(c, a) for c in ("SP", "AP", "EC") for a in ("AD-N", "AD-C", "FX-M", "FX-T")]
             + [("FR", a) for a in ("AD-N", "FX-M", "FX-T")] + [("SPT", "AD-N")])


def instances(kind):
    """(network, R, scenario_index, scenario) with a successful OPF; failures are reported (§2)."""
    from iteration56_orpd import ScenarioError
    scenarios = DEV_SCENARIOS if kind == "dev" else TEST_SCENARIOS
    offset = 0 if kind == "dev" else 2
    valid, excluded = [], []
    for network in NETWORKS:
        for j, scenario in enumerate(scenarios):
            try:
                ORPD(network, RESOLUTIONS[0], scenario[0], SPREAD, scenario[1])
            except ScenarioError:
                excluded.append([network, list(scenario)])
                continue
            for resolution in RESOLUTIONS:
                valid.append((network, resolution, offset + j, scenario))
    return valid, excluded


def path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def save(name, data):
    import gzip
    with gzip.open(path(name + ".gz"), "wt") as f:
        json.dump(data, f)


def load(name):
    import gzip
    with gzip.open(path(name + ".gz"), "rt") as f:
        return json.load(f)


def references(name):
    """L* per (network, R, scenario_index) = best feasible f over the reference runs."""
    best = {}
    for r in load(name)["records"]:
        t = r["task"]
        if not r["ok"]:
            continue  # execution failures never supply calibration data (reported in the JSON)
        key = f"{t['network']}|{t['resolution']}|{t['scenario_index']}"
        value = r["best_feasible"] if r["best_feasible"] is not None else math.inf
        best[key] = min(best.get(key, math.inf), value)
    for r in load(name)["records"]:  # an instance whose reference runs all failed: no reference (§6 fallback)
        t = r["task"]
        best.setdefault(f"{t['network']}|{t['resolution']}|{t['scenario_index']}", math.inf)
    return {k: (v if math.isfinite(v) else None) for k, v in best.items()}


def make_task(network, resolution, j, scenario, cht, arm, purpose, s, budget, reference=None, fixed=None,
              instrument=False):
    return dict(network=network, resolution=resolution, scenario_index=j, scenario=list(scenario), cht=cht,
                arm=arm, seed=seed_of(purpose, network, resolution, j, s), budget=budget, reference=reference,
                fixed=list(fixed) if fixed else None, instrument=instrument)


def execute(tasks, workers):
    """Runs tasks; an early-terminated run is rerun once in a fresh process (§3)."""
    records = run_pool(tasks, workers)
    for i, r in enumerate(records):
        if not r["ok"]:
            again = run_pool([tasks[i]], 1)[0]
            again["rerun"] = True
            again["first_attempt"] = {k: v for k, v in r.items() if k not in ("trace", "instrument")}
            records[i] = again
    return records


def stage_dev_ref(workers):
    valid, excluded = instances("dev")
    tasks = [make_task(n, R, j, sc, c, "AD-N", "dev_ref", 1, REF_BUDGET) for n, R, j, sc in valid
             for c in GADAPT_CHTS]
    save("dev_ref.json", dict(excluded=excluded, records=execute(tasks, workers)))


def stage_dev_fxm(workers):
    refs = references("dev_ref.json")
    valid, _ = instances("dev")
    tasks = [make_task(n, R, j, sc, c, "AD-N", "dev", s, BUDGET, refs[f"{n}|{R}|{j}"], instrument=True)
             for n, R, j, sc in valid for c in GADAPT_CHTS for s in FXM_SEEDS]
    records = execute(tasks, workers)
    vectors = {}
    for c in GADAPT_CHTS:
        a_runs, b_runs, s_runs = [], [], []
        for r in records:
            if r["task"]["cht"] != c or not r["ok"]:
                continue
            inst = r["instrument"]
            fractions = [e["k"] / e["pool"] for e in inst["population_events"] if e["pool"] > 0]
            a_runs.append(float(np.median(fractions)) if fractions else 0.0)
            b_runs.append(float(np.median(inst["v_fractions"])) if inst["v_fractions"] else 0.0)
            s_runs.append(float(np.median(inst["sigmas"])) if inst["sigmas"] else 0.0)
        if not a_runs:
            raise SystemExit(f"STOP: no successful FX-M calibration run for {c}")
        vectors[c] = [float(np.median(a_runs)), float(np.median(b_runs)), float(np.median(s_runs))]
    save("dev_fxm.json", dict(vectors=vectors, records=records))


def stage_dev_fxt(workers):
    refs = references("dev_ref.json")
    valid, _ = instances("dev")
    tasks = [make_task(n, R, j, sc, c, "FX-T", "dev", s, BUDGET, refs[f"{n}|{R}|{j}"], fixed=g)
             for n, R, j, sc in valid if R == 17 for c in GADAPT_CHTS for g in FXT_GRID for s in FXM_SEEDS]
    records = execute(tasks, workers)
    chosen = {}
    for c in GADAPT_CHTS:
        groups = [[r["T"] for r in records if r["ok"] and r["task"]["cht"] == c and r["task"]["fixed"] == list(g)]
                  for g in FXT_GRID]
        if any(len(g) != len(groups[0]) or not g for g in groups):
            raise SystemExit(f"STOP: FX-T grid incomplete for {c} (failed runs); report before choosing")
        means = [float(np.mean(g)) for g in groups]
        chosen[c] = list(FXT_GRID[int(np.argmin(means))])  # argmin: ties -> lower grid index
    for r in records:
        r.pop("trace", None)
    save("dev_fxt.json", dict(chosen=chosen, records=records))


def contrast_tasks(units, refs, fxt, purpose, budget):
    tasks = []
    for n, R, j, sc, s in units:
        for c, a in (("FR", "AD-N"), ("FR", "FX-T"), ("SP", "AD-N"), ("SP", "FX-T")):
            tasks.append(make_task(n, R, j, sc, c, a, purpose, s, budget, refs[f"{n}|{R}|{j}"],
                                   fixed=fxt[c] if a == "FX-T" else None))
    return tasks


def unit_contrasts(records):
    """d_u = [T(AD-N,FR) - T(FX-T,FR)] - [T(AD-N,SP) - T(FX-T,SP)] per unit."""
    table = {}
    for r in records:
        t = r["task"]
        table.setdefault((t["network"], t["resolution"], t["scenario_index"], t["seed"]), {})[(t["cht"], t["arm"])] = r
    return table


def theta(cells, contrast):
    """Fixed weights: mean over blocks of the mean over scenarios of the mean over seeds (§7)."""
    blocks = {}
    for (n, R, j), units in cells.items():
        blocks.setdefault((n, R), []).append(np.mean([contrast(u) for u in units]))
    return float(np.mean([np.mean(v) for v in blocks.values()]))


def bootstrap(cells, contrast, reps=20000, seed=56):
    """Cell-stratified bootstrap of complete paired unit vectors; 95% percentile interval; capped p (§7)."""
    rng = np.random.RandomState(seed)
    keys = sorted(cells)
    blocks = {}
    for k in keys:
        values = np.array([contrast(u) for u in cells[k]], float)
        means = values[rng.randint(0, len(values), size=(reps, len(values)))].mean(axis=1)
        blocks.setdefault(k[:2], []).append(means)
    draws = np.mean([np.mean(v, axis=0) for v in blocks.values()], axis=0)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    p = 1.0 if np.all(draws == 0) else min(1.0, 2 * min(np.mean(draws <= 0), np.mean(draws >= 0)))
    return dict(estimate=theta(cells, contrast), ci=[float(lo), float(hi)], p=float(p))


def d_a(u, fx="FX-T", other="SP"):
    return (u[("FR", "AD-N")]["T"] - u[("FR", fx)]["T"]) - (u[(other, "AD-N")]["T"] - u[(other, fx)]["T"])


def stage_rehearsal(workers):
    refs = references("dev_ref.json")
    fxt = load("dev_fxt.json")["chosen"]
    valid, _ = instances("dev")
    units = [(n, R, j, sc, s) for n, R, j, sc in valid for s in REHEARSAL_SEEDS]
    records = execute(contrast_tasks(units, refs, fxt, "dev", BUDGET), workers)
    table = unit_contrasts(records)
    by_block = {}
    for (n, R, j, seed), u in table.items():
        if len(u) == 4 and all(r["ok"] for r in u.values()):
            by_block.setdefault((n, R), []).append(d_a(u))
    # power simulation (§7): bounded, per block shifted so that the clipped mean is 0.05
    rng = np.random.RandomState(56023)
    test_valid, _ = instances("test")
    cell_keys = sorted({(n, R, j) for n, R, j, _ in test_valid})
    D = 2 * (1 - 1 / BUDGET)
    shifted = {}
    for block, ds in by_block.items():
        r = np.array(ds) - np.mean(ds)
        lo_d, hi_d = -D - 1, D + 1
        for _ in range(200):  # bisection for delta
            mid = (lo_d + hi_d) / 2
            if np.mean(np.clip(r + mid, -D, D)) < 0.05:
                lo_d = mid
            else:
                hi_d = mid
        shifted[block] = np.clip(r + (lo_d + hi_d) / 2, -D, D)
    hits = 0
    for _ in range(500):
        cells = {k: [{"d": x} for x in rng.choice(shifted[k[:2]], 10)] for k in cell_keys}
        result = bootstrap(cells, lambda u: u["d"], reps=20000, seed=56)  # the final analysis, unchanged
        hits += result["ci"][0] > 0 or result["ci"][1] < 0
    power = hits / 500
    for r in records:
        r.pop("trace", None)
    save("rehearsal.json", dict(power=power, seeds_per_instance=10 if power >= 0.8 else 20,
                                block_contrasts={f"{k[0]}|{k[1]}": v for k, v in by_block.items()},
                                records=records))


def stage_test_ref(workers):
    valid, excluded = instances("test")
    tasks = [make_task(n, R, j, sc, c, "AD-N", "test_ref", s, REF_BUDGET) for n, R, j, sc in valid
             for c in GADAPT_CHTS for s in (1, 2)]
    save("test_ref.json", dict(excluded=excluded, records=execute(tasks, workers)))


def stage_test(workers):
    refs = references("test_ref.json")
    fxm = load("dev_fxm.json")["vectors"]
    fxt = load("dev_fxt.json")["chosen"]
    seeds = load("rehearsal.json")["seeds_per_instance"]
    valid, excluded = instances("test")
    tasks = []
    for n, R, j, sc in valid:
        for s in range(1, seeds + 1):
            for c, a in TEST_ARMS:
                fixed = fxm[c] if a == "FX-M" else fxt[c] if a == "FX-T" else None
                tasks.append(make_task(n, R, j, sc, c, a, "test", s, BUDGET, refs[f"{n}|{R}|{j}"], fixed=fixed))
    records = execute(tasks, workers)
    save("test.json", dict(excluded=excluded, seeds_per_instance=seeds, references=refs, records=records))


def holm(pvalues):
    order = sorted(pvalues, key=pvalues.get)
    adjusted, running = {}, 0.0
    for i, name in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * pvalues[name]))
        adjusted[name] = running
    return adjusted


def analyse():
    """§7 analysis of test.json (written before any test run)."""
    data = load("test.json")
    table = unit_contrasts(data["records"])
    arms = set(TEST_ARMS)
    complete = {k: u for k, u in table.items() if set(u) == arms and all(r["ok"] for r in u.values())}
    excluded_units = sorted(set(table) - set(complete))
    cells = {}
    for (n, R, j, seed), u in complete.items():
        cells.setdefault((n, R, j), []).append(u)
    expected = {(t["network"], t["resolution"], t["scenario_index"]) for t in (r["task"] for r in data["records"])}
    empty = sorted(expected - set(cells))
    contrasts = dict(
        H56a=lambda u: d_a(u),
        H56b_signal_SP=lambda u: u[("SP", "AD-N")]["T"] - u[("SP", "AD-C")]["T"],
        AP_vs_SP=lambda u: (u[("AP", "AD-N")]["T"] - u[("AP", "FX-T")]["T"]) - (u[("SP", "AD-N")]["T"] - u[("SP", "FX-T")]["T"]),
        EC_vs_SP=lambda u: (u[("EC", "AD-N")]["T"] - u[("EC", "FX-T")]["T"]) - (u[("SP", "AD-N")]["T"] - u[("SP", "FX-T")]["T"]),
        H56a_FXM=lambda u: d_a(u, fx="FX-M"),
        encoding_SP_SPT=lambda u: u[("SP", "AD-N")]["T"] - u[("SPT", "AD-N")]["T"],
    )
    def infer(cell_map):
        out = {name: bootstrap(cell_map, f) for name, f in contrasts.items()}
        for k, v in holm({k: out[k]["p"] for k in contrasts if k != "H56a"}).items():
            out[k]["p_holm"] = v
        out["H56a"]["supported"] = out["H56a"]["ci"][0] > 0 or out["H56a"]["ci"][1] < 0
        return out

    results = infer(cells) if not empty else {}
    descriptive = {}
    for (n, R, j), units in cells.items():
        descriptive.setdefault(f"{n}|{R}", []).extend(d_a(u) for u in units)
    per_arm = {}
    for (c, a) in TEST_ARMS:
        rs = [u[(c, a)] for u in complete.values()]
        per_arm[f"{c}|{a}"] = dict(mean_T=float(np.mean([r["T"] for r in rs])),
                                   feasible=float(np.mean([r["best_feasible"] is not None for r in rs])),
                                   attained=float(np.mean([r["first_target"] is not None for r in rs])))
    sensitivity_needed = bool(empty) or len(excluded_units) > 0.05 * len(table)
    sensitivity = None
    if sensitivity_needed:
        # §3: restore excluded units, keep completed outcomes, T = 1 only for failed (or missing) runs
        failed = dict(T=1.0, ok=False)
        restored = {}
        for (n, R, j, seed), u in table.items():
            full = {arm: (u[arm] if arm in u and u[arm]["ok"] else failed) for arm in arms}
            restored.setdefault((n, R, j), []).append(full)
        sensitivity = infer(restored)
    out = dict(units=len(table), complete_units=len(complete), sensitivity=sensitivity, excluded_units=[list(map(str, k)) for k in excluded_units],
               empty_cells=[list(map(str, k)) for k in empty], excluded_instances=data["excluded"],
               no_reference=[k for k, v in data["references"].items() if v is None], results=results,
               median_d_by_block={k: float(np.median(v)) for k, v in descriptive.items()}, per_arm=per_arm,
               primary_available=not empty, sensitivity_needed=sensitivity_needed)
    save("analysis.json", out)
    print(json.dumps({k: out[k] for k in ("units", "complete_units", "primary_available", "results")}, indent=1))


STAGES = dict(dev_ref=stage_dev_ref, dev_fxm=stage_dev_fxm, dev_fxt=stage_dev_fxt, rehearsal=stage_rehearsal,
              test_ref=stage_test_ref, test=stage_test)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyse":
        analyse()
    elif len(sys.argv) > 1 and sys.argv[1] in STAGES:
        STAGES[sys.argv[1]](int(sys.argv[2]) if len(sys.argv) > 2 else 8)
    else:
        print(__doc__)
