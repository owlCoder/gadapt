"""Iteration 10: preregistered TWO genuine AC runs for alternative slack bus.

This is deliberately NOT a MATPOWER-equivalent AC-OPF model. The original
pandapower case's slack differs from the 2019 original MATPOWER case.
See ITERATION10_PROTOCOL.md and Iteration 9 exact source rows.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import pandapower as pp
import scipy

from research.iteration7_rte_source_physics import SourceRatedRTEGrid
from research.iteration8_reactive_screen import q_limit_summary, json_safe
from research.iteration9_source_generators import read_sources, index_converted_bus_ids


def original_slack_preflight(net, sources, buses):
    """Fail closed rather than pretending to reconstruct source case."""
    slack=[int(k) for k,v in buses.items() if int(v["bus_type"])==3]
    if slack!=[1320]:
        raise ValueError("Original 2019 source slack not BUS1320")
    row298=next((x for x in sources if int(x["source_row_1based"])==298),None)
    if row298 is None or int(row298["gen_bus"])!=1320 or int(row298["gen_status"])!=1:
        raise ValueError("Missing added original 2019 slack generator")
    ref={"pg_mw":0.,"pmin_mw":0.,"pmax_mw":1000.,
         "qmin_mvar":-1.,"qmax_mvar":1.,"vg_pu":1.0588}
    for k,v in ref.items():
        if abs(row298[k]-v)>1e-5:
            raise ValueError("Source slack generator changed in original data: "+k)
    first=[r for r in sources if int(r["gen_bus"])==1268 and int(r["gen_status"])==1]
    if len(first)!=2:
        raise ValueError("Expected two source active PV generators at BUS1268")
    ref_pv={"pg_mw":44.5,"pmin_mw":44.,"pmax_mw":45.,
            "qmin_mvar":-9.,"qmax_mvar":27.,"vg_pu":1.027}
    for item in first:
        for k,v in ref_pv.items():
            if abs(item[k]-v)>1e-5:
                raise ValueError("Source PV generator data changed: "+k)
    ids=index_converted_bus_ids(net)
    if len(net.ext_grid)!=1:
        raise ValueError("Only one ext grid supported in this diagnostic")
    ext_id=int(net.ext_grid.index[0])
    if int(net.ext_grid.at[ext_id,"bus"])!=ids[1268]:
        raise ValueError("Converted slack no longer BUS1268")
    gens=net.gen[(net.gen["bus"]==ids[1268]) & net.gen.in_service]
    if not gens.empty:
        raise ValueError("Unexpected pre-existing converted PV gen at BUS1268")
    f=net.sgen
    active=f[(f["bus"]==ids[1268]) & f.in_service]
    if len(active)!=1 or abs(float(active.iloc[0]["p_mw"])-44.5)>1e-5:
        raise ValueError("Converted sgen source compatibility not established")
    return ids,ext_id,row298,first[0],int(active.index[0])


def ext_output(net, ext_id, limits):
    fields=("p_mw","q_mvar")
    if any(f not in net.res_ext_grid.columns for f in fields):
        raise ValueError("Missing ext_grid PF result P or Q")
    p=float(net.res_ext_grid.at[ext_id,"p_mw"])
    q=float(net.res_ext_grid.at[ext_id,"q_mvar"])
    if not math.isfinite(p) or not math.isfinite(q):
        raise ValueError("Nonfinite ext_grid result")
    diff={
        "slack_p_above_max_mw":max(p-limits["pmax_mw"],0.),
        "slack_p_below_min_mw":max(limits["pmin_mw"]-p,0.),
        "slack_q_above_max_mvar":max(q-limits["qmax_mvar"],0.),
        "slack_q_below_min_mvar":max(limits["qmin_mvar"]-q,0.),
    }
    return {"slack_p_mw":p,"slack_q_mvar":q,**diff}


def diagnostic():
    original_gens,bus=read_sources()
    grid=SourceRatedRTEGrid(1.0)
    ids,ext_id,ref,former,sgen_id=original_slack_preflight(
        grid.net,original_gens,bus)
    orig_bus=int(grid.net.bus.at[grid.net.ext_grid.at[ext_id,"bus"],"name"])+1
    reference=np.asarray(grid.reference,float).copy()

    def evaluation(label,limits,source_bus):
        answer=grid.evaluate(reference)
        qstats=(q_limit_summary(grid.net) if not answer["solver_failed"]
                else dict.fromkeys(("generators_online",
                    "generators_with_valid_q_bounds_and_results",
                    "q_at_lower_count","q_at_upper_count","q_below_min_count",
                    "q_above_max_count","q_max_excess_mvar",
                    "q_total_excess_mvar")))
        ext=(ext_output(grid.net,ext_id,limits) if not answer["solver_failed"]
             else dict.fromkeys(("slack_p_mw","slack_q_mvar",
                     "slack_p_above_max_mw","slack_p_below_min_mw",
                     "slack_q_above_max_mvar","slack_q_below_min_mvar")))
        return {
          "scenario":label,"actual_ac_call":grid.calls,
          "ext_grid_original_bus_id":source_bus,
          "solver_failed":answer["solver_failed"],
          "solver_error":answer["solver_error"],
          "source_rated_feasible_but_not_full_opf":answer["feasible"],
          "voltage_under_pu":answer["voltage_under"],
          "voltage_over_pu":answer["voltage_over"],
          "source_line_excess":answer["source_line_excess"],
          "source_trafo_excess":answer["source_trafo_excess"],
          "combined_violation":answer["violation"],
          "loss_mw_not_optimum":answer["loss"],
          **ext,**qstats}

    limits_old={key:float(grid.net.ext_grid.at[ext_id,key]) for key in
                ("min_p_mw","max_p_mw","min_q_mvar","max_q_mvar")}
    # These are PP limits for the *old* converter ext_grid, not original 2019 slack.
    limits_old_source=dict(pmin_mw=limits_old["min_p_mw"],
                           pmax_mw=limits_old["max_p_mw"],
                           qmin_mvar=limits_old["min_q_mvar"],
                           qmax_mvar=limits_old["max_q_mvar"])
    results=[evaluation("original_converted_pandapower",limits_old_source,orig_bus)]
    print("I10_AC",json.dumps(json_safe(results[-1]),allow_nan=False),flush=True)

    # A counterfactual *study scenario*, not an exact reconstruction.
    net=grid.net
    net.ext_grid.at[ext_id,"bus"]=ids[1320]
    net.ext_grid.at[ext_id,"vm_pu"]=ref["vg_pu"]
    for old,new in (("pmin_mw","min_p_mw"),("pmax_mw","max_p_mw"),
                    ("qmin_mvar","min_q_mvar"),("qmax_mvar","max_q_mvar")):
        net.ext_grid.at[ext_id,new]=ref[old]
    inserted_id=pp.create_gen(net,bus=ids[1268],p_mw=former["pg_mw"],
                 vm_pu=former["vg_pu"],min_p_mw=former["pmin_mw"],
                 max_p_mw=former["pmax_mw"],
                 min_q_mvar=former["qmin_mvar"],
                 max_q_mvar=former["qmax_mvar"],controllable=True,
                 in_service=True)
    results.append(evaluation("experimental_source_slack_relocated",
                              ref,1320))
    print("I10_AC",json.dumps(json_safe(results[-1]),allow_nan=False),flush=True)
    if grid.calls!=2:
        raise ValueError("Exactly two real NR AC attempts required")
    metadata={
      "status":"completed_two_scenario_ac_diagnostic",
      "protocol":"research/ITERATION10_PROTOCOL.md",
      "actual_ac_powerflow_calls":grid.calls,
      "converted_old_slack_original_bus_id":orig_bus,
      "counterfactual_slack_original_bus_id":1320,
      "source_slack_generator_row":298,
      "counterfactual_created_gen_id":int(inserted_id),
      "counterfactual_created_gen_original_bus_id":1268,
      "counterfactual_retained_sgen_id":sgen_id,
      "counterfactual_retained_sgen_original_bus_id":1268,
      "old_ext_limit_source":"converted pandapower ext_grid metadata",
      "new_ext_limit_source":"original MATPOWER generator row 298",
      "software":{"python":platform.python_version(),
                  "pandapower_reported":pp.__version__,
                  "pandas":pd.__version__,"scipy":scipy.__version__},
      "interpretation":("Controlled sensitivity to a changed slack and PV source. "
          "Not an exact source-MATPOWER AC equivalent, not full OPF and "
          "not an optimization algorithm comparison."),
    }
    return results,metadata


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--csv",default="iteration10_slack_ac.csv")
    arg.add_argument("--json",default="iteration10_slack_ac.json")
    args=arg.parse_args()
    rows,info=diagnostic()
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(json_safe({"metadata":info,"rows":rows}),f,
                 indent=2,sort_keys=True,allow_nan=False)
    print("I10_SUMMARY",json.dumps(json_safe(info),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
