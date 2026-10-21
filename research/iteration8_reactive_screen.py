"""Iteration 8: preregistered exploratory voltage/Q screening on RTE1888.

No optimization, novelty, OPF or independent statistical significance claims.
Reuses the corrected source RATE_A evaluator from Iteration 7.
See research/ITERATION8_PROTOCOL.md.
"""
import argparse
from collections import defaultdict, deque
import csv
import json
import math
import platform

import numpy as np
import pandapower as pp
import pandas as pd
import scipy

from research.iteration7_rte_source_physics import SourceRatedRTEGrid


def _finite(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def network_adjacency(net):
    """Unweighted bus graph of in-service line and two-winding trafo edges."""
    graph = defaultdict(set)
    active_buses = {
        int(i) for i in net.bus.index
        if ("in_service" not in net.bus.columns or bool(net.bus.at[i, "in_service"]))
    }
    for kind, ends in (("line", ("from_bus", "to_bus")),
                       ("trafo", ("hv_bus", "lv_bus"))):
        for _, edge in getattr(net, kind).iterrows():
            if "in_service" in edge and not bool(edge["in_service"]):
                continue
            a, b = int(edge[ends[0]]), int(edge[ends[1]])
            if a in active_buses and b in active_buses:
                graph[a].add(b)
                graph[b].add(a)
    return graph, active_buses


def distance_from(graph, start):
    dist = {int(start): 0}
    queue = deque([int(start)])
    while queue:
        point = queue.popleft()
        for neighbor in sorted(graph.get(point, ())):
            if neighbor not in dist:
                dist[neighbor] = dist[point] + 1
                queue.append(neighbor)
    return dist


def eligible_controls(net, excluded):
    """Conservative screening subset; Q bounds and local V interval must exist."""
    _, buses = network_adjacency(net)
    candidates = {}
    for gen_id, item in net.gen.iterrows():
        gen_id = int(gen_id)
        bus = int(item["bus"])
        if gen_id in excluded or bus not in buses:
            continue
        if "in_service" in item and not bool(item["in_service"]):
            continue
        qlo, qhi = _finite(item.get("min_q_mvar")), _finite(item.get("max_q_mvar"))
        vm = _finite(item.get("vm_pu"))
        if qlo is None or qhi is None or qlo > qhi or vm is None:
            continue
        vlo = _finite(net.bus.at[bus, "min_vm_pu"]) if "min_vm_pu" in net.bus else None
        vhi = _finite(net.bus.at[bus, "max_vm_pu"]) if "max_vm_pu" in net.bus else None
        lo = max(0.95, vlo if vlo is not None else 0.95)
        hi = min(1.08, vhi if vhi is not None else 1.08)
        if hi < lo or not lo - 1e-10 <= vm <= hi + 1e-10:
            continue
        candidates[gen_id] = {
            "gen_id": gen_id, "gen_bus": bus, "reference_vm_pu": vm,
            "vm_lower": lo, "vm_upper": hi, "q_lower_mvar": qlo,
            "q_upper_mvar": qhi,
        }
    return candidates


def select_nearest_controls(net, voltage, lower, upper, excluded, n=8):
    if n < 0:
        raise ValueError("Control selection count must be nonnegative")
    bus_ids = [int(x) for x in net.bus.index]
    voltages = np.asarray(voltage, float)
    low = np.asarray(lower, float)
    high = np.asarray(upper, float)
    if not (len(bus_ids) == len(voltages) == len(low) == len(high)):
        raise ValueError("Bus voltage and bounds lengths disagree")
    if not np.all(np.isfinite(voltages)):
        raise ValueError("Cannot screen from non-finite baseline voltages")
    offenders = []
    for pos, bus in enumerate(bus_ids):
        violation = max(low[pos]-voltages[pos], 0.0,
                        voltages[pos]-high[pos])
        if violation > 1e-8:
            offenders.append((float(violation), bus))
    offenders.sort(key=lambda x: (-x[0], x[1]))

    graph, _ = network_adjacency(net)
    choices = eligible_controls(net, set(excluded))
    selected = []
    for size, bus in offenders:
        if len(selected) == n or not choices:
            break
        distances = distance_from(graph, bus)
        reachable = [x for x in choices.values() if x["gen_bus"] in distances]
        if not reachable:
            continue
        picked = min(reachable, key=lambda x: (distances[x["gen_bus"]], x["gen_id"]))
        record = dict(picked)
        record.update(target_bus=bus, target_violation_pu=size,
                      graph_distance=distances[record["gen_bus"]])
        selected.append(record)
        del choices[picked["gen_id"]]
    return selected, len(offenders)


def q_limit_summary(net, tol_mvar=1e-3):
    """Diagnostic only: does NOT attest to whole-system AC-OPF feasibility."""
    required = ("min_q_mvar", "max_q_mvar")
    if any(c not in net.gen for c in required) or "q_mvar" not in net.res_gen:
        raise ValueError("Generator Q limit / result columns absent")
    indices = net.gen.index
    data = net.gen.loc[indices]
    q = net.res_gen.loc[indices, "q_mvar"].to_numpy(float)
    lower = pd.to_numeric(data.min_q_mvar, errors="coerce").to_numpy(float)
    upper = pd.to_numeric(data.max_q_mvar, errors="coerce").to_numpy(float)
    online = (data.in_service.to_numpy(dtype=bool)
              if "in_service" in data else np.ones(len(data), bool))
    valid = online & np.isfinite(lower) & np.isfinite(upper) & (upper >= lower) & np.isfinite(q)
    below = valid & (q < lower - tol_mvar)
    above = valid & (q > upper + tol_mvar)
    at_low = valid & (np.abs(q-lower) <= tol_mvar)
    at_high = valid & (np.abs(q-upper) <= tol_mvar)
    excess = np.zeros(len(q), float)
    excess[valid] = np.maximum.reduce((
        lower[valid]-q[valid], q[valid]-upper[valid], np.zeros(int(valid.sum()))
    ))
    return {
        "generators_online": int(online.sum()),
        "generators_with_valid_q_bounds_and_results": int(valid.sum()),
        "q_at_lower_count": int(at_low.sum()),
        "q_at_upper_count": int(at_high.sum()),
        "q_below_min_count": int(below.sum()),
        "q_above_max_count": int(above.sum()),
        "q_max_excess_mvar": float(np.max(excess)) if len(excess) else 0.0,
        "q_total_excess_mvar": float(np.sum(excess)),
    }


def json_safe(obj):
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, (float, np.floating)):
        return float(obj) if math.isfinite(float(obj)) else None
    if isinstance(obj, np.integer):
        return int(obj)
    return obj


def run_screen(n=8, delta=0.02):
    if not 0 <= n <= 8 or not math.isfinite(delta) or delta <= 0:
        raise ValueError("Screen requires 0..8 controls and positive delta")
    grid = SourceRatedRTEGrid(1.0)
    legacy_gen_ids = list(grid.gen_ids)
    old_reference = np.asarray(grid.reference, float).copy()

    def take_result(name, target=None, shift=0.0, vector=None):
        actual = grid.evaluate(old_reference if vector is None else vector)
        qdata = (q_limit_summary(grid.net) if not actual["solver_failed"]
                 else {name: None for name in (
                     "generators_online", "generators_with_valid_q_bounds_and_results",
                     "q_at_lower_count", "q_at_upper_count", "q_below_min_count",
                     "q_above_max_count", "q_max_excess_mvar", "q_total_excess_mvar")})
        record = {
            "trial": name, "ac_call": grid.calls,
            "gen_id": target["gen_id"] if target else None,
            "gen_bus": target["gen_bus"] if target else None,
            "target_bus": target["target_bus"] if target else None,
            "target_violation_pu": target["target_violation_pu"] if target else None,
            "graph_distance": target["graph_distance"] if target else None,
            "requested_shift_pu": shift,
            "effective_shift_pu": (float(vector[grid.gen_ids.index(target["gen_id"])]
                 - target["reference_vm_pu"]) if target is not None else 0.0),
            "solver_failed": actual["solver_failed"],
            "solver_error": actual["solver_error"],
            "source_rated_feasible": actual["feasible"],
            "source_rated_violation": actual["violation"],
            "voltage_under_pu": actual["voltage_under"],
            "voltage_over_pu": actual["voltage_over"],
            "line_excess": actual["source_line_excess"],
            "trafo_excess": actual["source_trafo_excess"],
            "loss_mw_not_feasible_optimum": actual["loss"],
            **qdata,
        }
        return record

    baseline = take_result("reference")
    if baseline["solver_failed"]:
        return [baseline], {
            "status": "baseline_pf_failed", "selected_controls": [],
            "legacy_controls": legacy_gen_ids, "actual_ac_calls": grid.calls,
            "expected_ac_calls": 1, "baseline_bus_violations": None,
        }

    selected, num_bad = select_nearest_controls(
        grid.net, grid.net.res_bus.vm_pu.to_numpy(float),
        grid.v_lower, grid.v_upper, set(legacy_gen_ids), n,
    )
    grid.gen_ids = [x["gen_id"] for x in selected]
    grid.reference = grid.net.gen.loc[grid.gen_ids, "vm_pu"].to_numpy(float)
    reference = np.asarray(grid.reference, float).copy()
    rows = [baseline]
    for target in selected:
        offset = grid.gen_ids.index(target["gen_id"])
        for shift in (-delta, delta):
            candidate = reference.copy()
            candidate[offset] = float(np.clip(
                reference[offset]+shift, target["vm_lower"], target["vm_upper"]
            ))
            rows.append(take_result("voltage_perturbation", target, shift, candidate))
            print("I8_AC", rows[-1], flush=True)
    expected = 1 + 2*len(selected)
    if grid.calls != expected or len(rows) != expected:
        raise RuntimeError("Unaccounted real AC calls")
    minima = [r["source_rated_violation"] for r in rows
              if not r["solver_failed"] and math.isfinite(r["source_rated_violation"])]
    metadata = {
        "status": "screen_completed", "protocol": "research/ITERATION8_PROTOCOL.md",
        "python": platform.python_version(), "pandapower": pp.__version__,
        "scipy": scipy.__version__, "pandas": pd.__version__,
        "source_rate_mapping": grid.source_rates and
            "research/results/rte1888_iteration7_matpower_to_pandapower_thermal_map_20261021.csv",
        "legacy_controls": legacy_gen_ids, "selected_controls": selected,
        "baseline_bus_violations": num_bad,
        "actual_ac_calls": grid.calls, "expected_ac_calls": expected,
        "nonconvergent_calls": sum(bool(r["solver_failed"]) for r in rows),
        "best_converged_violation": min(minima) if minima else None,
        "source_rated_feasible_calls": sum(bool(r["source_rated_feasible"]) for r in rows),
        "interpretation": ("Local exploratory data-dependent sensitivity only; "
                           "not full OPF nor independent statistics or optimality evidence"),
    }
    return rows, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="rte1888_iteration8_reactive_screen.csv")
    parser.add_argument("--json", default="rte1888_iteration8_reactive_screen.json")
    args = parser.parse_args()
    rows, metadata = run_screen()
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(json_safe({"metadata": metadata, "rows": rows}), f,
                  sort_keys=True, indent=2, allow_nan=False)
    print("I8_SUMMARY", json.dumps(json_safe(metadata), sort_keys=True,
                                   allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
