"""I40: train-only temporal capacity calibration with an exact containment proof.

All routes come only from FIT 128 original source frames. CAL 64 chooses
one network-wide conformal threshold. TEST 96 is read once for final audit.
A statistical coverage statement REQUIRES conditional score exchangeability;
temporally dependent 5-minute data do not establish that assumption.
See the frozen research/ITERATION40_PROTOCOL.md.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import time

import numpy as np
import scipy
from research.iteration38_joint_capacity_experiment import source_data_gate
from research.iteration39_source_modular_capacity import (
    ARCHIVE_SHA, NETWORK_SHA, ModularCommonPlan, exact_modular_milp,
)

FIT = 128
CAL = 64
TEST = 96
ALPHA = 0.10
METHODS = (
    "fit_only", "calibrated_90_relative", "calibrated_90_absolute",
    "calibration_max_relative", "fit_plus_cal_per_edge_max")
ROUTES = ("fixed_first_shortest_path", "fit_only_exact_source_milp")


def network_loads(problem, choice, matrices):
    """Computation only: same static I39 paths, no per-scenario rerouting."""
    z = np.asarray(choice, dtype=float)
    if (z.shape != (problem.n,) or
            not np.all(np.isfinite(z)) or
            not np.all((z == 0) | (z == 1))):
        raise ValueError("Static route vector must be an exact binary vector")
    q = np.asarray(matrices, dtype=float)
    if q.ndim != 2 or q.shape[1] != problem.n:
        raise ValueError("Traffic matrix must agree with original fixed pair order")
    mat = problem.incidence[0] + problem.delta * z[:, None]
    if np.any(mat < -1e-9):
        raise ValueError("Invalid source link path incidence")
    return q @ mat, np.any(mat > 0, axis=0)


def modular_cover(problem, required):
    """Price-minimal source-certified modular 20/40 capacity per edge."""
    req = np.asarray(required, dtype=float)
    if (req.shape != (len(problem.links),) or
            not np.all(np.isfinite(req)) or np.any(req < -1e-8)):
        raise ValueError("Invalid source link reserve")
    quanta = np.maximum(0, np.ceil(np.maximum(req, 0) / 20. - 1e-10)).astype(int)
    n20 = quanta % 2
    n40 = quanta // 2
    prices = np.asarray(problem.module_prices, dtype=float)
    installed = 20. * n20 + 40. * n40 + problem.base_cap
    cost = float(n20 @ prices[:, 0] + n40 @ prices[:, 1])
    if np.any(installed + 1e-7 < req):
        raise RuntimeError("Undercovered source link capacity due to rounding")
    return dict(
        cost=cost, installed_capacity=installed.tolist(),
        modules_20=n20.tolist(), modules_40=n40.tolist(),
        count_modules=int(n20.sum() + n40.sum()),
        total_installed_source_capacity=float(installed.sum()))


def order_stat_threshold(scores, alpha=ALPHA):
    s = np.asarray(scores, dtype=float)
    if s.ndim != 1 or not len(s) or np.any(s < 0) or not np.all(np.isfinite(s)):
        raise ValueError("Need nonnegative finite calibration scores")
    if not 0 < alpha < 1:
        raise ValueError("Invalid target marginal risk")
    k = math.ceil((len(s)+1) * (1-alpha))
    if k > len(s):
        return float("inf"), k
    return float(np.sort(s)[k-1]), k


def calibrated_policies(problem, choices, all_traffic, fit=FIT, cal=CAL,
                        alpha=ALPHA):
    q = np.asarray(all_traffic, dtype=float)
    if len(q) <= fit + cal:
        raise ValueError("Need a nonempty untouched chronological holdout")
    loads, used = network_loads(problem, choices, q)
    fitted = loads[:fit].max(axis=0)
    if not used.any() or np.any(fitted[~used] > 1e-8):
        raise ValueError("No used source edges or unused edge has measured flow")
    weights_relative = np.maximum(20.0, fitted)
    weights_absolute = np.ones_like(fitted)

    def scores(weight):
        return np.maximum(0., (loads[fit:fit+cal, used]-fitted[used]) /
                          weight[used]).max(axis=1)

    rel_scores, abs_scores = scores(weights_relative), scores(weights_absolute)
    rel_threshold, k = order_stat_threshold(rel_scores, alpha)
    abs_threshold, k_abs = order_stat_threshold(abs_scores, alpha)
    if k != k_abs or k != math.ceil((cal+1)*(1-alpha)):
        raise RuntimeError("Inconsistent preregistered quantile index")
    if not math.isfinite(rel_threshold) or not math.isfinite(abs_threshold):
        raise ValueError("No finite quantile for requested alpha/calibration")
    cal_max = float(np.max(rel_scores))
    methods = {
        "fit_only": fitted,
        "calibrated_90_relative": fitted + weights_relative * rel_threshold,
        "calibrated_90_absolute": fitted + weights_absolute * abs_threshold,
        "calibration_max_relative": fitted + weights_relative * cal_max,
        "fit_plus_cal_per_edge_max": loads[:fit+cal].max(axis=0)}
    observed = {}
    for method in METHODS:
        requested = np.where(used, methods[method], 0.)
        built = modular_cover(problem, requested)
        cap = built["installed_capacity"]
        metrics = {}
        for key, frame in (
            ("fit", q[:fit]), ("calibration", q[fit:fit+cal]),
            ("holdout", q[fit+cal:])):
            metrics[key] = problem.validate_plan(choices, cap, frame)
        if metrics["fit"]["violating_slices"] != 0:
            raise RuntimeError("Source modular network failed its FIT certificate")
        if method in ("calibration_max_relative", "fit_plus_cal_per_edge_max"):
            if metrics["calibration"]["violating_slices"]:
                raise RuntimeError("Claimed CAL robust plan fails directly observed calibration")
        if method in ("calibrated_90_relative", "calibrated_90_absolute"):
            # By the threshold containment theorem, >= k of CAL scores
            # must correspond to fully source-capacity-feasible frames.
            if metrics["calibration"]["violating_slices"] > cal - k:
                raise RuntimeError("Calibration containment/order-statistic theorem violated")
        observed[method] = dict(
            **built, evaluation=metrics,
            price_increase_over_fit_only=None,
            target_alpha=alpha if method.startswith("calibrated_90") else None,
            calibration_order_statistic_1_based=k if method.startswith("calibrated_90") else None,
            chosen_calibration_threshold=(
                rel_threshold if method == "calibrated_90_relative" else
                abs_threshold if method == "calibrated_90_absolute" else
                cal_max if method == "calibration_max_relative" else None))
    price0 = observed["fit_only"]["cost"]
    for obj in observed.values():
        obj["price_increase_over_fit_only"] = obj["cost"] - price0
    return dict(
        policies=observed, used_edge_count=int(used.sum()),
        calibration_score_summary=dict(
            relative_qhat=rel_threshold,
            absolute_qhat=abs_threshold, relative_max=cal_max,
            n_cal=cal, target_alpha=alpha, rank_k=k,
            nominal_exchangeable_marginal_coverage_lower_bound=k/(cal+1)),
        statistical_warning=("Coverage theorem is CONDITIONAL on exchangeability "
                             "of calibration and one future score given FIT; "
                             "NOT guaranteed on correlated 5-minute DFN traffic."))


def run(output, manifest_path):
    nodes, links, pairs, q, meta = source_data_gate()
    if (meta["source_network"]["sha256"] != NETWORK_SHA or
            meta["source_matrices"]["sha256"] != ARCHIVE_SHA or
            q.shape != (288, 272) or
            (FIT, CAL, TEST, ALPHA) != (128, 64, 96, 0.10)):
        raise RuntimeError("Frozen I40 source SHA, shape or temporal split changed")
    if list(METHODS) != ["fit_only", "calibrated_90_relative",
                         "calibrated_90_absolute", "calibration_max_relative",
                         "fit_plus_cal_per_edge_max"]:
        raise RuntimeError("I40 method preregistration drift")

    model = ModularCommonPlan(nodes, links, pairs, q[:FIT])
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(manifest_path, "w", encoding="utf8") as f:
        json.dump(meta, f, sort_keys=True, indent=2, allow_nan=False)
    print("I40_SOURCE_GATE", json.dumps(dict(
        network_sha=NETWORK_SHA, archive_sha=ARCHIVE_SHA,
        source_rows=len(q), source_pairs=len(pairs),
        original_link_menus_certified=len(model.module_prices)),
        sort_keys=True), flush=True)

    clock = time.monotonic()
    m = exact_modular_milp(model, seconds=180.)
    m["wall_seconds"] = round(time.monotonic() - clock, 5)
    print("I40_FIT_MILP", json.dumps({k:v for k,v in m.items() if k!="incumbent"},
                                   sort_keys=True, allow_nan=False), flush=True)
    routes = {"fixed_first_shortest_path": [0] * model.n}
    if m["incumbent"] is not None:
        routes["fit_only_exact_source_milp"] = m["incumbent"]["choices"]
    if tuple(routes) != ROUTES:
        raise RuntimeError("Missing valid FIT MILP route; skip rather than impute")
    comparisons = {}
    for label, z in routes.items():
        output_set = calibrated_policies(model, z, q)
        comparisons[label] = dict(routes=z, **output_set)
        for policy, obj in output_set["policies"].items():
            print("I40_POLICY", json.dumps(dict(
                route_source=label, policy=policy, source_price=obj["cost"],
                price_increase=obj["price_increase_over_fit_only"],
                fit_violations=obj["evaluation"]["fit"]["violating_slices"],
                cal_violations=obj["evaluation"]["calibration"]["violating_slices"],
                holdout_violations=obj["evaluation"]["holdout"]["violating_slices"],
                holdout_max_excess=obj["evaluation"]["holdout"]["max_source_unit_excess"],
                order_statistic=obj["calibration_order_statistic_1_based"],
                threshold=obj["chosen_calibration_threshold"],
            ), sort_keys=True, allow_nan=False), flush=True)
    result = dict(
        protocol="research/ITERATION40_PROTOCOL.md", original_source=meta,
        assumption="historical traffic Mbit/s and source module-unit numerical equality, NOT certified utility-scale operation",
        native_routing="I39 same two path fixed FIT-only choice for each original directed pair",
        fit_frames=FIT, cal_frames=CAL, test_frames=TEST, alpha=ALPHA,
        tested_method_order=list(METHODS),
        fit_only_original_source_milp=m,
        no_milp_retraining_using_cal_or_test=True,
        comparison=comparisons,
        python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)
    with open(output, "w", encoding="utf8") as f:
        json.dump(result, f, sort_keys=True, indent=2, allow_nan=False)
    print("I40_DONE", json.dumps(dict(
        methods_per_route=len(METHODS), routes=len(routes),
        network_source_name="SNDlib nobel-germany original DFN 2005",
        primary_fit_violations=comparisons["fit_only_exact_source_milp"]["policies"]["fit_only"]["evaluation"]["holdout"]["violating_slices"],
        primary_calibrated_violations=comparisons["fit_only_exact_source_milp"]["policies"]["calibrated_90_relative"]["evaluation"]["holdout"]["violating_slices"],
        primary_fit_source_price=comparisons["fit_only_exact_source_milp"]["policies"]["fit_only"]["cost"],
        primary_calibrated_source_price=comparisons["fit_only_exact_source_milp"]["policies"]["calibrated_90_relative"]["cost"],
        caveat="No marginal-coverage guarantee for temporally correlated one-day holdout"
    ), sort_keys=True), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    run(args.json, args.manifest)
