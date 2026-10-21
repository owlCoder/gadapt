"""Iteration 7: preregistered RTE1888 structural feasibility and control audit.

No optimization and no novelty claim. See ITERATION7_PROTOCOL.md.
All calls go through the *unchanged iteration-6 GridProblem* evaluator.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import scipy
import pandapower as pp
from research.ieee_grid_benchmark import GridProblem, GEN_VOLTAGE_BOUNDS


def finite_values(frame, column):
    if column not in frame.columns:
        return np.array([], dtype=float)
    arr = pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype=float)
    return arr[np.isfinite(arr)]


def field_summary(frame, column):
    vals = finite_values(frame, column)
    return {
        "column_exists": column in frame.columns,
        "non_null_finite": len(vals),
        "positive": int(np.count_nonzero(vals > 0)),
        "zero": int(np.count_nonzero(vals == 0)),
        "negative": int(np.count_nonzero(vals < 0)),
        "minimum": float(np.min(vals)) if len(vals) else None,
        "median": float(np.median(vals)) if len(vals) else None,
        "maximum": float(np.max(vals)) if len(vals) else None,
    }


def controls(net):
    tap = net.trafo
    numeric = lambda c: pd.to_numeric(tap[c], errors="coerce").to_numpy(float) if c in tap else np.full(len(tap), np.nan)
    tap_min, tap_max, tap_step = numeric("tap_min"), numeric("tap_max"), numeric("tap_step_percent")
    legal = np.isfinite(tap_min) & np.isfinite(tap_max) & (tap_max > tap_min) & np.isfinite(tap_step) & (tap_step != 0)
    return {
        "counts": {name: int(len(getattr(net, name))) for name in
                   ("bus", "line", "trafo", "trafo3w", "gen", "ext_grid",
                    "sgen", "shunt", "impedance", "load")},
        "first_eight_gen_ids": [int(i) for i in net.gen.index[:8]],
        "first_eight_gen_buses": [int(i) for i in net.gen.bus.iloc[:8]],
        "first_eight_gen_voltages": [float(i) for i in net.gen.vm_pu.iloc[:8]],
        "all_generator_voltage_distinct_buses": int(net.gen.bus.nunique()),
        "transformers_with_numeric_tap_range_and_step": int(np.sum(legal)),
        "line_current_limits_ka": field_summary(net.line, "max_i_ka"),
        "line_opf_loading_limits_percent": field_summary(net.line, "max_loading_percent"),
        "transformer_nominal_mva": field_summary(net.trafo, "sn_mva"),
        "transformer_opf_loading_limits_percent": field_summary(net.trafo, "max_loading_percent"),
        "generator_min_q_mvar": field_summary(net.gen, "min_q_mvar"),
        "generator_max_q_mvar": field_summary(net.gen, "max_q_mvar"),
        "generator_min_p_mw": field_summary(net.gen, "min_p_mw"),
        "generator_max_p_mw": field_summary(net.gen, "max_p_mw"),
        "shunt_q_mvar": field_summary(net.shunt, "q_mvar"),
        "shunt_step": field_summary(net.shunt, "step"),
        "shunt_max_step": field_summary(net.shunt, "max_step"),
        "bus_lower_vm_pu": field_summary(net.bus, "min_vm_pu"),
        "bus_upper_vm_pu": field_summary(net.bus, "max_vm_pu"),
    }


def components(grid, result):
    if result["solver_failed"]:
        return {"voltage_under_pu": None, "voltage_over_pu": None,
                "line_excess_per_unit_sum": None, "trafo_excess_per_unit_sum": None,
                "line_overloads_count": None, "trafo_overloads_count": None,
                "bus_voltage_violations_count": None, "max_line_loading_percent": None,
                "max_trafo_loading_percent": None, "q_at_lower_limit_count": None,
                "q_at_upper_limit_count": None}
    net = grid.net
    v = net.res_bus.vm_pu.to_numpy(float)
    line = net.res_line.loading_percent.to_numpy(float)
    trafo = net.res_trafo.loading_percent.to_numpy(float)
    low, high = np.maximum(grid.v_lower-v, 0), np.maximum(v-grid.v_upper, 0)
    qlo = pd.to_numeric(net.gen["min_q_mvar"], errors="coerce").to_numpy(float) if "min_q_mvar" in net.gen else np.full(len(net.gen), np.nan)
    qhi = pd.to_numeric(net.gen["max_q_mvar"], errors="coerce").to_numpy(float) if "max_q_mvar" in net.gen else np.full(len(net.gen), np.nan)
    q = net.res_gen.q_mvar.to_numpy(float)
    return {
        "voltage_under_pu": float(np.sum(low)),
        "voltage_over_pu": float(np.sum(high)),
        "line_excess_per_unit_sum": float(np.maximum(line-100, 0).sum()/100),
        "trafo_excess_per_unit_sum": float(np.maximum(trafo-100, 0).sum()/100),
        "line_overloads_count": int(np.sum(line>100+1e-8)),
        "trafo_overloads_count": int(np.sum(trafo>100+1e-8)),
        "bus_voltage_violations_count": int(np.sum((low+high)>1e-8)),
        "max_line_loading_percent": float(np.max(line)) if len(line) else 0.,
        "max_trafo_loading_percent": float(np.max(trafo)) if len(trafo) else 0.,
        "q_at_lower_limit_count": int(np.sum(np.isfinite(qlo) & (q<=qlo+1e-5))),
        "q_at_upper_limit_count": int(np.sum(np.isfinite(qhi) & (q>=qhi-1e-5))),
    }


def largest_offenders(net, n=15):
    offenders = []
    for kind, elements, results in (("line", net.line, net.res_line),
                                    ("trafo", net.trafo, net.res_trafo)):
        if not len(elements):
            continue
        for idx, loading in results.loading_percent.items():
            if not math.isfinite(float(loading)) or loading <= 100:
                continue
            element = elements.loc[idx]
            data = {"type": kind, "element_id": int(idx),
                    "loading_percent": float(loading),
                    "excess_percent_points": float(loading-100),
                    "from_bus": int(element["from_bus"] if kind=="line" else element["hv_bus"]),
                    "to_bus": int(element["to_bus"] if kind=="line" else element["lv_bus"])}
            for field in (("max_i_ka", "max_loading_percent") if kind=="line"
                          else ("sn_mva", "max_loading_percent", "tap_pos", "tap_min", "tap_max")):
                if field in elements:
                    value=element[field]
                    data[field]=float(value) if pd.notna(value) and isinstance(value,(float,int,np.number)) else (str(value) if pd.notna(value) else None)
            offenders.append(data)
    return sorted(offenders, key=lambda x:x["excess_percent_points"], reverse=True)[:n]


def audit(load):
    grid = GridProblem("rte1888", load)
    metadata = controls(grid.net)
    metadata["reference_within_eight_dimensional_box"] = bool(
        np.all(np.asarray(grid.reference)>=GEN_VOLTAGE_BOUNDS[0]) and
        np.all(np.asarray(grid.reference)<=GEN_VOLTAGE_BOUNDS[1]))
    lo, hi = GEN_VOLTAGE_BOUNDS
    reference = np.asarray(grid.reference, float).copy()
    candidates=[("reference", -1, 0., reference)]
    for i in range(grid.dimension):
        for sign in (-1, 1):
            test=reference.copy()
            test[i]=np.clip(test[i]+sign*0.02,lo,hi)
            candidates.append(("voltage_perturbation", i, sign*0.02, test))
    rows=[]
    baseline_top = []
    for label, i, displacement, vector in candidates:
        result=grid.evaluate(vector)
        details=components(grid, result)
        if label=="reference" and not result["solver_failed"]:
            baseline_top=largest_offenders(grid.net)
        row={"load_factor":load,"trial":label,"generator_offset":i,
             "requested_vm_delta_pu":displacement,
             "actual_vm_delta_pu":float(vector[i]-reference[i]) if i>=0 else 0.,
             "physical_ac_call":grid.calls,
             "voltage_vector": ";".join(f"{x:.9f}" for x in vector),
             "converged":not result["solver_failed"], "physical_feasible":result["feasible"],
             "loss_mw":result["loss"], "normalized_violation":result["violation"],
             "maximum_loading_percent":result["maximum_loading"],
             "solver_error":result["solver_error"],**details}
        rows.append(row)
        print("AC",load,label,i,displacement,"call",grid.calls,
              "converged",row["converged"],"violation",row["normalized_violation"],
              "line_overloads",row["line_overloads_count"],
              "trafo_overloads",row["trafo_overloads_count"],flush=True)
    expected=1+2*grid.dimension
    if grid.calls!=expected or len(rows)!=expected:
        raise RuntimeError(f"Expected {expected} real AC calls, got {grid.calls}")
    baseline=rows[0]["normalized_violation"]
    for row in rows[1:]:
        row["delta_violation_vs_reference"] = (row["normalized_violation"]-baseline
              if math.isfinite(row["normalized_violation"]) and math.isfinite(baseline) else "")
    rows[0]["delta_violation_vs_reference"]=0
    metadata["reference_top_thermal_offenders"]=baseline_top
    metadata["requested_ac_calls"]=expected
    metadata["actual_ac_calls"]=grid.calls
    metadata["solver_failures"]=sum(not r["converged"] for r in rows)
    metadata["min_violation_17_probes"]=min(r["normalized_violation"] for r in rows)
    metadata["feasible_probes"]=sum(r["physical_feasible"] for r in rows)
    metadata["reference_violation"]=baseline
    return rows,metadata


def json_safe(value):
    """Preserve missing/failed AC observations as JSON null, not Infinity."""
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k,v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    return value


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--loads",nargs="+",type=float,default=[1.,1.1])
    parser.add_argument("--csv",default="rte1888_audit.csv")
    parser.add_argument("--json",default="rte1888_audit.json")
    args=parser.parse_args()
    if not args.loads or any(not math.isfinite(x) or x<=0 for x in args.loads):
        parser.error("loads must be positive finite values")
    metadata={"python":platform.python_version(),"pandapower":pp.__version__,
              "scipy":scipy.__version__,"pandas":pd.__version__,
              "protocol":"research/ITERATION7_PROTOCOL.md", "loads":{}}
    allrows=[]
    for load in args.loads:
        rows,info=audit(load)
        allrows.extend(rows)
        metadata["loads"][str(load)]=info
    with open(args.csv,"w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(allrows[0]))
        writer.writeheader()
        writer.writerows(allrows)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(json_safe(metadata),f,indent=2,sort_keys=True,allow_nan=False)
    print("AUDIT",json.dumps({
        factor: {"ac_calls":info["actual_ac_calls"],
                 "reference_violation":info["reference_violation"],
                 "min_probe_violation":info["min_violation_17_probes"],
                 "baseline_top_offenders":info["reference_top_thermal_offenders"][:5],
                 "available_controls":info["counts"]}
        for factor,info in metadata["loads"].items()}),flush=True)


if __name__=="__main__":
    main()
