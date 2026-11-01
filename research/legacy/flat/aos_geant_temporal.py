"""Frozen chronological SNDlib GÉANT AOS pilot on the *real GAdapt* package.

The August evaluation period is out-of-period but NOT a pristine independent
test of the entire SNDlib archive (earlier research inspected other August
samples). Model uses historical anonymized/scaled traffic, with an engineered
capacity-module purchasing objective, not actual network provisioning.
Timestamp choices were frozen in research/AOS_ITERATION_PROTOCOL.md BEFORE
writing this experiment.
"""
import argparse
import csv
import hashlib
import io
import math
import random
import statistics
import tarfile
import time
import urllib.request

import numpy as np
from scipy.optimize import differential_evolution

from gadapt.ga import GA
from research.geant_capacity import GeantCapacity
from research.geant_dynamic_probe import ARCHIVE, parse_demand_matrix
from research.geant_temporal_benchmark import ChronologicalCapacity

SHA256 = "92d72a808d6de9d26be66844c098d3f32d5b9bb6c69af170e82b73118faef0df"
TRAIN_DATES = ("20050505", "20050615", "20050720")
TRAIN_HOURS = (0, 6, 12, 18)
TEST_DATES = ("20050820", "20050822", "20050824", "20050826")
TEST_HOURS = tuple(range(0, 24, 3))
METHODS = ("legacy", "affine", "uniform_objective", "ucb_objective", "scipy_de")


def timestamps(dates, hours):
    return tuple(f"{date}-{hour:02d}00" for date in dates for hour in hours)


TRAIN_STAMPS = timestamps(TRAIN_DATES, TRAIN_HOURS)
TEST_STAMPS = timestamps(TEST_DATES, TEST_HOURS)


def archived_traffic():
    req = urllib.request.Request(ARCHIVE, headers={"User-Agent": "GAdapt-research/1.0"})
    with urllib.request.urlopen(req, timeout=150) as response:
        data = response.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != SHA256:
        raise ValueError(f"Historical archive SHA mismatch: {actual}")
    chosen = TRAIN_STAMPS + TEST_STAMPS
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = [m for m in archive.getmembers() if m.isfile()]
        for stamp in chosen:
            matches = [m for m in members if stamp in m.name]
            if len(matches) != 1 or matches[0].size > 1000000:
                raise ValueError(f"Missing/ambiguous/large frozen matrix {stamp}: {len(matches)}")
            with archive.extractfile(matches[0]) as src:
                matrix = parse_demand_matrix(src.read().decode("utf-8-sig"))
            if len(matrix) < 100 or not math.isfinite(sum(d for _, _, d in matrix)):
                raise ValueError("Malformed archived traffic "+stamp)
            result[stamp] = matrix
    if len(result) != len(chosen):
        raise ValueError("Frozen timestamp count mismatch")
    return result


class Recorder:
    """Counts *true* evaluations and keeps the best development design."""
    def __init__(self, problem, budget):
        self.problem = problem
        self.budget = budget
        self.evaluations = 0
        self.requests = 0
        self.best = float("inf")
        self.vector = None

    def __call__(self, x):
        self.requests += 1
        if self.evaluations >= self.budget:
            return 1e12
        self.evaluations += 1
        values = tuple(float(v) for v in x)
        result = self.problem.evaluate(values)
        cost = float(result["cost"])
        if not math.isfinite(cost):
            return 1e12
        if cost < self.best:
            self.best = cost
            self.vector = tuple(int(round(v)) for v in values)
        return cost


def run(train, heldout, combined, method, seed, budget, population):
    random.seed(seed)
    np.random.seed(seed)
    monitor = Recorder(train, budget)
    started = time.perf_counter()
    success, error = True, ""
    telemetry = []
    if method == "scipy_de":
        try:
            differential_evolution(
                monitor, train.bounds, popsize=1,
                maxiter=math.ceil(budget / train.n) + 2,
                integrality=[True]*train.n, tol=0, atol=0, polish=False,
                rng=np.random.default_rng(seed))
        except Exception as exc:
            success, error = False, str(exc)
    else:
        options = {
            "cost_diversity_metric": "log_relative" if method == "legacy"
                                     else "affine_invariant",
        }
        if method.startswith(("uniform", "ucb")):
            options["mutation_operator_policy"] = ("uniform" if method.startswith("uniform") else "ucb")
            options["mutation_operator_credit"] = "objective"
        ga = GA(
            cost_function=monitor, population_size=population,
            number_of_generations=math.ceil(3*budget/population)+10,
            exit_check="generations", timeout=240,
            exit_function=lambda: monitor.evaluations >= budget,
            population_mutation="cost_diversity,parent_diversity",
            **options)
        for lo, hi in train.bounds:
            ga.add(lo, hi, 1.0)
        try:
            result = ga.execute()
            success = bool(result.success)
            error = result.message if not success else ""
            telemetry = getattr(result, "operator_credit_summary", [])
        except Exception as exc:
            success, error = False, str(exc)
    if monitor.vector is None:
        success = False
        error = error or "No finite training candidate"
        test_cost = combined_cost = float("nan")
        worst_module = -1
    else:
        try:
            out_of_sample = heldout.evaluate(monitor.vector)
            all_periods = combined.evaluate(monitor.vector)
            test_cost = float(out_of_sample["cost"])
            combined_cost = float(all_periods["cost"])
            worst_module = int(all_periods["max_modules"])
        except Exception as exc:
            success = False
            error = str(exc)
            test_cost = combined_cost = float("nan")
            worst_module = -1
    return {
        "method": method, "seed": seed, "success": success,
        "development_cost": monitor.best,
        "late_august_cost": test_cost, "all_period_cost": combined_cost,
        "max_modules": worst_module,
        "objective_evaluations": monitor.evaluations,
        "objective_requests": monitor.requests,
        "seconds": round(time.perf_counter()-started, 4),
        "operator_selections": sum(o["selections"] for o in telemetry),
        "operator_observations": sum(o["observations"] for o in telemetry),
        "selected_vector": "-".join(str(x) for x in monitor.vector) if monitor.vector else "",
        "error": error,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=8)
    parser.add_argument("--budget", type=int, default=240)
    parser.add_argument("--population", type=int, default=36)
    parser.add_argument("--output", default="aos_geant_temporal.csv")
    args = parser.parse_args()
    if args.runs < 1 or args.budget < args.population:
        parser.error("runs must be >=1; budget >= population")
    base = GeantCapacity.download()
    samples = archived_traffic()
    published_volume = sum(amount for _, _, amount in base.demands)
    peak_train = max(sum(amount for _, _, amount in samples[t]) for t in TRAIN_STAMPS)
    if peak_train <= 0:
        raise ValueError("Invalid train volume")
    factor = published_volume / peak_train
    scaled = {
        t: [(a,b,amount*factor) for a,b,amount in sample]
        for t,sample in samples.items()
    }
    train = ChronologicalCapacity(base, {t:scaled[t] for t in TRAIN_STAMPS})
    heldout = ChronologicalCapacity(base, {t:scaled[t] for t in TEST_STAMPS})
    combined = ChronologicalCapacity(base, scaled)
    print("PROVENANCE", "archive_sha256",SHA256,"network_sha256",base.data_sha256,
          "train",TRAIN_STAMPS,"evaluation",TEST_STAMPS,
          "scale_from_development_only",repr(factor),
          "published_matrix_total_Mbps",published_volume,
          "train_max_total_Mbps",peak_train,
          flush=True)
    rows = []
    for seed in range(args.runs):
        for method in METHODS:
            row = run(train,heldout,combined,method,seed,args.budget,args.population)
            row["scenario_scale"] = factor
            rows.append(row)
            print("RUN",row,flush=True)
    with open(args.output,"w",newline="",encoding="utf-8") as file:
        writer = csv.DictWriter(file,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for method in METHODS:
        group = [r for r in rows if r["method"]==method]
        successful = [r for r in group if r["success"]]
        print("SUMMARY",method,"successful",len(successful),"/",len(group),
              "median_development",statistics.median(r["development_cost"] for r in successful) if successful else "NA",
              "median_late_august",statistics.median(r["late_august_cost"] for r in successful) if successful else "NA",
              "median_all_periods",statistics.median(r["all_period_cost"] for r in successful) if successful else "NA",
              "worst_all_periods",max(r["all_period_cost"] for r in successful) if successful else "NA",
              "median_seconds",statistics.median(r["seconds"] for r in group),flush=True)
    if any(r["objective_evaluations"] != args.budget for r in rows):
        print("WARNING: a method did not use the full TRUE evaluation budget",flush=True)
    if any(not r["success"] for r in rows):
        print("WARNING: method errors present and counted; no success-only inference",flush=True)


if __name__ == "__main__":
    main()
