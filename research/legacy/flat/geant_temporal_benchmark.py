"""Chronological optimization study on measured/scaled GEANT traffic snapshots.

Training: 3 published 15-minute traffic matrices in May/June/July 2005.
Evaluation only: an August snapshot. The August matrix was previously read
only for a quality-control probe, so this is out-of-period development
validation, NOT a pristine final holdout. Traffic is archived anonymized,
sampled and scaled; capacities/costs use the original SNDlib network.

Planning model: fixed integer link-routing weights; one installed capacity
plan covers the per-link worst demand from selected measured snapshots.
No assumptions of live deployment or utility/operator approval.
"""
import argparse
import copy
import csv
import hashlib
import io
import math
import statistics
import tarfile
import urllib.request

from research.geant_capacity import GeantCapacity, evaluate_method
from research.geant_dynamic_probe import ARCHIVE, TIMESTAMPS, parse_demand_matrix

EXPECTED_ARCHIVE_SHA256 = "92d72a808d6de9d26be66844c098d3f32d5b9bb6c69af170e82b73118faef0df"


def load_scenarios():
    request = urllib.request.Request(
        ARCHIVE, headers={"User-Agent": "GAdapt-research/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        raw = response.read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("Archived SNDlib measured traffic bytes changed")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        members = [m for m in archive.getmembers() if m.isfile()]
        snapshots = {}
        for stamp in TIMESTAMPS:
            target = [m for m in members if stamp in m.name]
            if len(target) != 1 or target[0].size > 1000000:
                raise ValueError("Unexpected number or size of timestamp "+stamp)
            with archive.extractfile(target[0]) as f:
                observations = parse_demand_matrix(f.read().decode("utf-8-sig"))
            if len(observations) < 100 or not math.isfinite(sum(x[2] for x in observations)):
                raise ValueError("Invalid observed traffic sample " + stamp)
            snapshots[stamp] = observations
    return snapshots


class ChronologicalCapacity:
    def __init__(self, base, demand_series):
        self.series = []
        for key, measured in demand_series.items():
            scenario = copy.copy(base)
            scenario.demands = list(measured)
            if not all(a in scenario.graph and b in scenario.graph for a,b,_ in scenario.demands):
                raise ValueError("Observed source/target outside published GEANT topology")
            self.series.append((key, scenario))
        self.edges = base.edges
        self.bounds = base.bounds
        self.n = base.n

    def evaluate(self, weights):
        module_vectors = []
        for _, problem in self.series:
            module_vectors.append(problem.evaluate(weights)["modules"])
        # One static installation must cover the peak on EACH edge across
        # different times, not merely the worst total traffic timestamp.
        peak_by_edge = [max(vec[i] for vec in module_vectors)
                        for i in range(self.n)]
        total_cost = sum(n*edge[2] for n, edge in zip(peak_by_edge, self.edges))
        return dict(cost=float(total_cost), modules=peak_by_edge,
                    max_modules=max(peak_by_edge))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=12)
    parser.add_argument("--budget", type=int, default=240)
    parser.add_argument("--output", default="geant_temporal.csv")
    parser.add_argument("--raw-volumes", action="store_true",
                        help="Use published anonymized measured Mbps unchanged; default scales to the published SNDlib peak matrix")
    args = parser.parse_args()
    published = GeantCapacity.download()
    obs = load_scenarios()
    training = {timestamp: obs[timestamp] for timestamp in TIMESTAMPS[:-1]}
    # The published default SNDlib GÉANT matrix is explicitly a scaled
    # directed peak matrix (~3 Tbit/s). Absolute 15-minute traffic records
    # are anonymized/scaled differently. In a stress DESIGN scenario, bring
    # the largest TRAINING observed sum to the published peak; apply ONE
    # fixed factor to all timestamps, with no information from August.
    published_peak = sum(d[2] for d in published.demands)
    training_max = max(sum(d[2] for d in demand) for demand in training.values())
    factor = 1.0 if args.raw_volumes else published_peak / training_max
    if not math.isfinite(factor) or factor <= 0:
        raise ValueError("Invalid traffic calibration from archived data")
    normalized = {stamp: [(a, b, demand * factor) for a, b, demand in matrix]
                  for stamp, matrix in obs.items()}
    training = {timestamp: normalized[timestamp] for timestamp in TIMESTAMPS[:-1]}
    heldout = {TIMESTAMPS[-1]: normalized[TIMESTAMPS[-1]]}
    train = ChronologicalCapacity(published, training)
    out_of_period = ChronologicalCapacity(published, heldout)
    validation_all = ChronologicalCapacity(published, normalized)
    print("DATA", "train=", list(training), "validation=", list(heldout),
          "archive_sha256=", EXPECTED_ARCHIVE_SHA256,
          "published_peak_mbps=", round(published_peak, 3),
          "training_peak_mbps=", round(training_max, 3),
          "applied_scaling=", round(factor, 8),
          "scenario=", ("anonymized_measured_raw" if args.raw_volumes else
                        "measured_pattern_calibrated_to_published_peak"),
          flush=True)

    # Baselines use the same admissible integer weight bounds as optimizers.
    prices = [edge[2] for edge in published.edges]
    low, high = min(prices), max(prices)
    reference = {
        "uniform": [1]*published.n,
        "cost_weighted": [1+round(24*(v-low)/(high-low)) for v in prices],
    }
    for name, vector in reference.items():
        print("BASELINE", name, "train=", train.evaluate(vector)["cost"],
              "evaluation_august=", out_of_period.evaluate(vector)["cost"],
              "all_four=", validation_all.evaluate(vector)["cost"], flush=True)
    rows = []
    for seed in range(args.runs):
        for method in ("log_relative", "affine_invariant", "affine_restart",
                       "scipy_de", "random_search"):
            # In order to evaluate a training-selected design out of period,
            # evaluate_method needs to return its BEST CONTROL VECTOR.
            # The dedicated Recorder in this benchmark captures it below.
            # Run original method but capture the chosen design for evaluation
            # through a minimal wrapper that tracks each objective evaluation.
            original_evaluate = train.evaluate
            best = {"cost": float("inf"), "weights": None}
            def tracked(weights):
                info = original_evaluate(weights)
                if info["cost"] < best["cost"]:
                    best["cost"] = info["cost"]
                    best["weights"] = tuple(int(round(v)) for v in weights)
                return info
            train.evaluate = tracked
            try:
                result = evaluate_method(train, method, seed, args.budget, population=36)
            finally:
                train.evaluate = original_evaluate
            if best["weights"] is None:
                raise RuntimeError("Optimizer did not evaluate a training candidate")
            validation = out_of_period.evaluate(best["weights"])
            total = validation_all.evaluate(best["weights"])
            row = dict(method=method, seed=seed, scenario_scale=factor,
                       train_cost=result["cost"],
                       august_cost=validation["cost"], all_four_cost=total["cost"],
                       objective_evaluations=result["evaluations"],
                       seconds=result["seconds"],
                       selected_weight_signature="-".join(map(str,best["weights"])))
            rows.append(row)
            print("RUN", method, seed, "train=",row["train_cost"],
                  "august=",row["august_cost"], "all_four=",row["all_four_cost"],
                  flush=True)
    with open(args.output, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for method in ("log_relative", "affine_invariant", "affine_restart",
                   "scipy_de", "random_search"):
        selected = [r for r in rows if r["method"] == method]
        print("SUMMARY", method,
              "train_median=",statistics.median(r["train_cost"] for r in selected),
              "august_median=",statistics.median(r["august_cost"] for r in selected),
              "all_four_median=",statistics.median(r["all_four_cost"] for r in selected),
              "worst_all_four=",max(r["all_four_cost"] for r in selected),
              flush=True)
    assert all(r["objective_evaluations"] == args.budget for r in rows), "Budget mismatch"


if __name__ == "__main__":
    main()
