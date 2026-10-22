"""I38 one-source planning benchmark: 12 actual GAdapt GA runs + MILP.

Run ONLY after the preregistered official-data gate; no fabricated matrices.
The archived output keeps complete original source provenance, MI(L)P status,
all GA runs and holdout validity of one shared static installed network plan.
"""
import argparse
import json
import math
import os
import platform
import random
import time

import numpy as np
import scipy
from gadapt.ga import GA
from research.iteration38_joint_capacity_model import (
    EXPECTED_NODES, EXPECTED_LINKS, EXPECTED_MATRICES,
    JointCapacityProblem, official_source, official_matrices, parse_network,
    parse_demands, temporal_array, solve_milp,
)

SEEDS = tuple(range(3800, 3812))
BUDGET = 360
TRAIN, HOLDOUT = 192, 96


def source_data_gate():
    source, provenance = official_source()
    nodes, links = parse_network(source)
    if (len(nodes) != EXPECTED_NODES or len(links) != EXPECTED_LINKS or
            len(parse_demands(source, nodes)) != 121):
        raise RuntimeError("Source SNDlib network topology/default demand drift")
    files, archive = official_matrices()
    if len(files) != EXPECTED_MATRICES:
        raise RuntimeError("Temporal source archive length drift")
    pairs, traffic = temporal_array(files, nodes)
    if traffic.shape != (TRAIN + HOLDOUT, len(pairs)):
        raise RuntimeError("Invalid native temporal file parsing")
    return nodes, links, pairs, traffic, dict(
        source_network=provenance, source_matrices=archive,
        matrix_names=[name for name, _ in files],
        training_indices=[0, TRAIN-1],
        heldout_indices=[TRAIN, TRAIN+HOLDOUT-1],
        temporal_rows=len(files),
        directed_demand_pairs=len(pairs),
        node_count=len(nodes), link_count=len(links),
        readme="https://sndlib.put.poznan.pl/download/nobel-germany-rm.txt",
        model_is_restricted_research_interpretation_NOT_source_optimum=True)


class PaidJointCapacityCost:
    def __init__(self, problem):
        self.problem = problem
        self.calls = 0
        self.over_budget_requests = 0
        self.infeasible_trials = 0
        self.failures = []
        self.best = None
        self.trace = []

    def __call__(self, values):
        if self.calls >= BUDGET:
            self.over_budget_requests += 1
            return 1e15
        self.calls += 1  # REAL whole-training-panel capacity evaluation attempt.
        try:
            out = self.problem.evaluate(values)
        except (ValueError, ArithmeticError) as e:
            self.failures.append(dict(call=self.calls, reason=str(e)[:150]))
            return 1e14
        if not out["feasible"]:
            self.infeasible_trials += 1
            score = 1e12 + 1e7 * out["worst_excess"]
        else:
            score = out["cost"]
            if self.best is None or score < self.best["cost"] - 1e-8:
                self.best = dict(call=self.calls,
                                 choices=[int(round(v)) for v in values],
                                 **out)
        if self.calls == 1 or self.calls % 30 == 0:
            self.trace.append(dict(call=self.calls,
                                   incumbent_source_cost=(
                                       self.best["cost"] if self.best else None)))
        return float(score)


def ga_run(problem, seed):
    random.seed(seed)
    np.random.seed(seed)
    cost = PaidJointCapacityCost(problem)
    algo = GA(
        cost_function=cost, population_size=24,
        cost_diversity_metric="log_relative",
        population_mutation="cost_diversity,parent_diversity",
        exit_check="generations", number_of_generations=128,
        exit_function=lambda:cost.calls >= BUDGET,
        timeout=240)
    for _ in range(problem.n):
        algo.add(0., 1., 1.)
    start = time.monotonic()
    status, detail = None, None
    try:
        result = algo.execute()
        status = bool(result.success)
        detail = str(result.messages)[:400]
    except Exception as error:
        status = False
        detail = (type(error).__name__ + ": " + str(error))[:400]
    if cost.calls > BUDGET:
        raise RuntimeError("Violation of preregistered true network evaluation budget")
    return dict(
        seed=seed, actual_full_train_panel_evaluations=cost.calls,
        over_budget_objective_requests_with_NO_domain_call=cost.over_budget_requests,
        infeasible_train_plans=cost.infeasible_trials,
        numerical_or_input_errors=cost.failures, optimizer_success_flag_NOT_feasibility=status,
        optimizer_stop=detail, wall_seconds=round(time.monotonic()-start, 5),
        best_train_feasible_common_plan=cost.best, observed_progress=cost.trace)


def run(output, manifest):
    if SEEDS != tuple(range(3800, 3812)) or BUDGET != 360 or (TRAIN, HOLDOUT) != (192, 96):
        raise RuntimeError("Registered I38 experiment config changed")
    nodes, links, pairs, q, provenance = source_data_gate()
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2, allow_nan=False)
    print("I38_SOURCE_DATA_GATE", json.dumps({
        "nodes":len(nodes), "links":len(links), "directed_demand_pairs":len(pairs),
        "traffic_matrices":len(q), "source_sha256":provenance["source_network"]["sha256"],
        "archive_sha256":provenance["source_matrices"]["sha256"]}), flush=True)
    model = JointCapacityProblem(nodes, links, pairs, q[:TRAIN])
    baseline = model.evaluate(np.zeros(model.n, dtype=int))
    base_holdout = (model.validate_plan(
        np.zeros(model.n, dtype=int), baseline["installed_capacity"], q[TRAIN:])
                    if baseline["feasible"] else None)
    tic = time.monotonic()
    reference = solve_milp(model, time_limit=180)
    reference["wall_seconds"] = round(time.monotonic() - tic, 5)
    print("I38_MILP", json.dumps({k:v for k,v in reference.items() if k!="incumbent"},
                                allow_nan=False), flush=True)
    if reference["incumbent"] is not None:
        reference["holdout"] = model.validate_plan(
            reference["incumbent"]["choices"], reference["incumbent"]["installed_capacity"],
            q[TRAIN:])
    rows = []
    for seed in SEEDS:
        r = ga_run(model, seed)
        if r["best_train_feasible_common_plan"] is not None:
            found = r["best_train_feasible_common_plan"]
            new_eval = model.evaluate(found["choices"])
            if not new_eval["feasible"] or abs(new_eval["cost"]-found["cost"]) > 1e-6:
                raise RuntimeError("Independent source cost confirmation failed")
            r["holdout"] = model.validate_plan(
                found["choices"], found["installed_capacity"], q[TRAIN:])
            if reference["dual_bound"] is not None and reference["dual_bound"] > 0:
                r["certified_relative_gap_upper_bound_to_MILP_dual"] = (
                    found["cost"]-reference["dual_bound"])/reference["dual_bound"]
        rows.append(r)
        print("I38_GADAPT",json.dumps(r,sort_keys=True,allow_nan=False),flush=True)
    if len(rows) != len(SEEDS) or len(set(r["seed"] for r in rows)) != len(SEEDS):
        raise RuntimeError("I38 seeds lost")
    out = dict(
        protocol="research/ITERATION38_PROTOCOL.md",
        modeling_qualification="restricted TWO shortest paths + one shared installed capacity choice per link; no cost cap, no recourse",
        python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
        provenance=provenance, initial_shortest_path_baseline=baseline,
        initial_baseline_holdout=base_holdout, milp=reference,
        original_gadapt_runs=rows, total_true_panel_objective_calls=sum(
            r["actual_full_train_panel_evaluations"] for r in rows))
    with open(output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True, allow_nan=False)
    print("I38_DONE",json.dumps(dict(
        ga_runs=len(rows), milp_status=reference["status"],
        real_train_panel_objective_evaluations=out["total_true_panel_objective_calls"],
        train_feasible_ga_seeds=sum(r["best_train_feasible_common_plan"] is not None
                                   for r in rows))),flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()
    run(args.json, args.manifest)
