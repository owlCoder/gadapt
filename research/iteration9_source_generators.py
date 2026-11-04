"""Iteration 9: independent static audit of original MATPOWER generator and bus
limits against the converted pandapower RTE1888 model. Zero AC calls.
Preregistered in ITERATION9_PROTOCOL.md. Original numeric source is CC BY 4.0.
"""
import argparse
from collections import Counter, defaultdict
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import scipy

ROOT = "research/results/"
GEN_CSV = ROOT + "rte1888_iteration9_original_matpower_generator_rows_2019.csv"
BUS_CSV = ROOT + "rte1888_iteration9_original_matpower_bus_rows_2019.csv"
PINNED_COMMIT = "80b6e16f760f58721ad31221c7287c28259cd4ad"
SRC_FIELDS = ("pg_mw", "pmin_mw", "pmax_mw", "qmin_mvar",
              "qmax_mvar", "vg_pu")
PP_FIELDS = ("p_mw", "min_p_mw", "max_p_mw", "min_q_mvar",
             "max_q_mvar", "vm_pu")


def read_sources(gen_path=GEN_CSV, bus_path=BUS_CSV):
    def load(path):
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    gens, buses = load(gen_path), load(bus_path)
    expected_gen = {"source_row_1based", "gen_bus", "pg_mw", "qg_mvar",
        "qmax_mvar", "qmin_mvar", "vg_pu", "mbase_mva", "gen_status",
        "pmax_mw", "pmin_mw"}
    expected_bus = {"bus_id", "bus_type", "pd_mw", "qd_mvar", "gs_mw",
        "bs_mvar", "area", "vm_pu", "va_deg", "base_kv", "zone",
        "vmax_pu", "vmin_pu"}
    if len(gens) != 298 or len(buses) != 1888:
        raise ValueError("Unexpected source case size")
    if set(gens[0]) != expected_gen or set(buses[0]) != expected_bus:
        raise ValueError("Source CSV schema mismatch")
    raw_gen = []
    for i, row in enumerate(gens, 1):
        v = {k: float(x) for k, x in row.items()}
        if not all(math.isfinite(x) for x in v.values()):
            raise ValueError("Nonfinite source generator data")
        if int(v["source_row_1based"]) != i:
            raise ValueError("Source generator row order mismatch")
        if v["gen_status"] not in (0, 1):
            raise ValueError("Unexpected generator status")
        if v["pmin_mw"] > v["pmax_mw"] or v["qmin_mvar"] > v["qmax_mvar"]:
            raise ValueError("Invalid source generator limits")
        raw_gen.append(v)
    original_buses = {}
    for row in buses:
        v = {k: float(x) for k, x in row.items()}
        if not all(math.isfinite(x) for x in v.values()):
            raise ValueError("Nonfinite bus source data")
        name = int(v["bus_id"])
        if name in original_buses or v["vmin_pu"] > v["vmax_pu"]:
            raise ValueError("Duplicate/invalid source bus")
        original_buses[name] = v
    if len(original_buses) != 1888:
        raise ValueError("Duplicate source bus ids")
    if not all(int(z["gen_bus"]) in original_buses for z in raw_gen):
        raise ValueError("Generator points to missing original bus")
    return raw_gen, original_buses


def index_converted_bus_ids(net):
    ids = {}
    for pp_index, raw in net.bus["name"].items():
        if pd.isna(raw) or not math.isfinite(float(raw)):
            raise ValueError("Unmapped converted bus")
        label = float(raw)
        if not label.is_integer():
            raise ValueError("Noninteger original bus name")
        original = int(label) + 1
        if original in ids:
            raise ValueError("Duplicate converted source bus ID")
        ids[original] = int(pp_index)
    if len(ids) != len(net.bus):
        raise ValueError("Incomplete converted bus ID mapping")
    return ids


def active_element_buses(net, original_ids):
    reverse = {converted: original for original, converted in original_ids.items()}
    result = {}
    for kind in ("gen", "sgen", "ext_grid"):
        frame = getattr(net, kind)
        collection = defaultdict(list)
        for idx, row in frame.iterrows():
            if "in_service" in row and not bool(row["in_service"]):
                continue
            bus = int(row["bus"])
            if bus not in reverse:
                raise ValueError("Unmapped active "+kind+" element")
            collection[reverse[bus]].append((int(idx), row))
        result[kind] = collection
    return result


def single_unit_differences(source, converted, converted_index, tol=1e-4):
    """Compare only unambiguous one-source/one-converted-gen bus."""
    fields = {}
    for name, converted_name in zip(SRC_FIELDS, PP_FIELDS):
        actual = float(converted[converted_name])
        expected = float(source[name])
        if not math.isfinite(actual):
            raise ValueError("Nonfinite single generator property: "+converted_name)
        fields[name] = {
            "source": expected, "converted": actual,
            "difference": actual - expected,
            "absolute_difference": abs(actual-expected),
            "within_tolerance": abs(actual-expected) <= tol,
        }
    return {
        "source_row_1based": int(source["source_row_1based"]),
        "converted_gen_index": int(converted_index),
        "max_absolute_deviation": max(x["absolute_difference"] for x in fields.values()),
        "all_within_tolerance": all(x["within_tolerance"] for x in fields.values()),
        "fields": fields,
    }


def audit(net, source_gen, source_bus):
    converted = index_converted_bus_ids(net)
    if set(converted) != set(source_bus):
        raise ValueError("Source/converted bus ID sets differ")
    buses_stats = Counter()
    differences = []
    for bus_id in sorted(converted):
        bus = source_bus[bus_id]
        pos = converted[bus_id]
        for src_name, local_name in (
            ("vmin_pu", "min_vm_pu"), ("vmax_pu", "max_vm_pu"),
            ("base_kv", "vn_kv"),
        ):
            actual = float(net.bus.at[pos, local_name])
            source = bus[src_name]
            if not math.isfinite(actual):
                raise ValueError("Nonfinite converted bus field")
            diff = abs(source - actual)
            buses_stats[src_name+"_compared"] += 1
            if diff > 1e-5:
                buses_stats[src_name+"_mismatch"] += 1
                differences.append({
                    "bus_id": bus_id, "field": src_name,
                    "original": source, "converted": actual,
                    "absolute_difference": diff,
                })

    src_online = defaultdict(list)
    src_offline = defaultdict(list)
    for item in source_gen:
        (src_online if int(item["gen_status"]) == 1 else src_offline)[int(item["gen_bus"])].append(item)
    conv = active_element_buses(net, converted)
    subset = []
    classes = Counter()
    unaccounted = []
    ambiguous = []
    for bus_id, originals in sorted(src_online.items()):
        kinds = {kind: len(conv[kind].get(bus_id, [])) for kind in conv}
        label = "+".join(k for k, n in kinds.items() if n) or "none"
        classes[label] += 1
        if label == "none":
            unaccounted.append(bus_id)
        if (len(originals) == 1 and kinds["gen"] == 1 and
            kinds["sgen"] == 0 and kinds["ext_grid"] == 0):
            index, item = conv["gen"][bus_id][0]
            entry = single_unit_differences(originals[0], item, index)
            entry["bus_id"] = bus_id
            subset.append(entry)
        else:
            ambiguous.append({"source_bus_id": bus_id,
                "source_online_generators": len(originals), **kinds})
    subset.sort(key=lambda x: (-x["max_absolute_deviation"], x["bus_id"]))
    differences.sort(key=lambda x: (-x["absolute_difference"], x["bus_id"]))

    source_single_v_set = {
        k: sorted({float(x["vg_pu"]) for x in v})
        for k, v in src_online.items() if len(v) > 1
    }
    src_slack = [int(x) for x, z in source_bus.items() if int(z["bus_type"]) == 3]
    conv_slack = sorted(conv["ext_grid"])
    source_totals = {}
    for prop in ("pg_mw", "qg_mvar", "pmin_mw", "pmax_mw", "qmin_mvar", "qmax_mvar"):
        source_totals[prop+"_online"] = sum(float(x[prop]) for rows in src_online.values() for x in rows)
    counts = {"all":len(source_gen), "online":sum(len(v) for v in src_online.values()),
              "offline":sum(len(v) for v in src_offline.values()),
              "online_distinct_buses":len(src_online),
              "online_multiple_units_buses":sum(len(v)>1 for v in src_online.values()),
              "offline_distinct_buses":len(src_offline),
              "offline_fixed_q_limits":sum(z["qmin_mvar"] == z["qmax_mvar"]
                    for v in src_offline.values() for z in v),
              "online_fixed_q_limits":sum(z["qmin_mvar"] == z["qmax_mvar"]
                    for v in src_online.values() for z in v),
              "online_at_min_p_in_source":sum(abs(z["pg_mw"]-z["pmin_mw"])<=1e-4
                    for v in src_online.values() for z in v)}
    pp_counts = {}
    for kind in ("gen", "sgen", "ext_grid"):
        frame = getattr(net, kind)
        pp_counts[kind] = {
            "all_elements":len(frame),
            "active_elements":sum(len(x) for x in conv[kind].values()),
            "active_distinct_source_buses":len(conv[kind]),
            "missing_min_p":int(frame.get("min_p_mw", pd.Series(index=frame.index,dtype=float)).isna().sum()),
            "missing_max_p":int(frame.get("max_p_mw", pd.Series(index=frame.index,dtype=float)).isna().sum()),
            "missing_min_q":int(frame.get("min_q_mvar", pd.Series(index=frame.index,dtype=float)).isna().sum()),
            "missing_max_q":int(frame.get("max_q_mvar", pd.Series(index=frame.index,dtype=float)).isna().sum()),
        }
    return {
        "status": "static_generator_conversion_audit",
        "actual_ac_powerflow_calls": 0,
        "source": {"pinned_matpower_commit": PINNED_COMMIT,
                   "source_blob_sha": "820bd317167381baf819d67eab7d886013e8b05a",
                   "license": "CC BY 4.0; cannot be used to operate or plan real French/EU grid"},
        "runtime": {"python":platform.python_version(),
                    "pandapower_reported":pp.__version__,
                    "pandas":pd.__version__, "scipy":scipy.__version__},
        "bus": {"original":len(source_bus), "converted":len(converted),
                "original_slack_ids":src_slack,
                "converted_ext_grid_original_bus_ids":conv_slack,
                "counts":dict(buses_stats),
                "top_absolute_mismatches":differences[:20]},
        "source_generators": {"counts":counts, "sum":source_totals,
                 "original_online_multiunit_different_vg_bus_count":
                    sum(len(v)>1 for v in source_single_v_set.values())},
        "converted_elements":pp_counts,
        "crosswalk": {
            "original_online_bus_class_coverage":dict(sorted(classes.items())),
            "original_online_buses_without_converted_source":unaccounted,
            "source_online_buses_without_gen_but_with_sgen":
                sorted(set(src_online) & set(conv["sgen"]) - set(conv["gen"])),
            "one_to_one_compared_count":len(subset),
            "one_to_one_all_six_fields_match_count":sum(r["all_within_tolerance"] for r in subset),
            "one_to_one_any_mismatch_count":sum(not r["all_within_tolerance"] for r in subset),
            "one_to_one_top_20_mismatch_candidates":subset[:20],
            "many_to_one_or_ambiguous_bus_count":len(ambiguous),
            "many_to_one_or_ambiguous_examples":ambiguous[:25],
            "converted_gen_without_online_source_bus_count":
                len(set(conv["gen"]) - set(src_online)),
            "converted_sgen_without_online_source_bus_count":
                len(set(conv["sgen"]) - set(src_online)),
        },
        "caveat": ("One-to-one comparisons exclude all buses with multiple source or "
                    "converted generators/sgen/ext grid. No equivalence of AC equations "
                    "or full OPF constraints; not an optimizer benchmark."),
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="rte1888_iteration9_static_generator_audit.json")
    args=parser.parse_args()
    gens,buses=read_sources()
    result=audit(pn.case1888rte(),gens,buses)
    with open(args.output,"w",encoding="utf-8") as f:
        json.dump(result,f,sort_keys=True,indent=2,allow_nan=False)
    print("ITERATION9_STATIC_SUMMARY",json.dumps({
        "bus":result["bus"],"source_generators":result["source_generators"],
        "converted_elements":result["converted_elements"],
        "crosswalk": {k:v for k,v in result["crosswalk"].items()
                     if not isinstance(v,list)},
        "actual_ac_powerflow_calls":0,
    },sort_keys=True,allow_nan=False),flush=True)
    print("ITERATION9_REPORT_READY",args.output,flush=True)


if __name__=="__main__":
    main()
