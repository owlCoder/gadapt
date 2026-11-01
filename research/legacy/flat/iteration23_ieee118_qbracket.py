"""Iteration 23: four strictly pre-registered real IEEE118 source AC PF bracket trials.

Historical source I22 half/full VG sensitivity states are NOT recomputed.
Trial scales are fixed 0.6,0.7,0.8,0.9 (all four run regardless of
outcome). Original 54 PG, all other source VG/P/Q/load/topology immutable.
This is deterministic physical feasibility probing, NOT GAdapt optimization.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import scipy

from pypower.idx_bus import VMIN,VMAX
from pypower.idx_gen import GEN_BUS,PG,VG
from pypower.runpf import runpf

from research.iteration18_ieee118_gadapt_transfer import IEEE118NineControlSubset,physics_118
from research.iteration19_ieee118_forensic_diagnostic import (
    top_generator_violations,top_voltage_violations,branch_terminal_source_limits,
)

PREVIOUS="research/results/ieee118_iteration22_qmidpoint_5_real_ac_20261021.json"
ALPHAS=(.6,.7,.8,.9)
ID_BY_BUS={34:15,92:42,19:8}
Q_HALF=2.4644560480222957
Q_FULL=3.642855096077252


def history_source_preflight(path=PREVIOUS):
    with open(path,encoding="utf-8") as f:
        raw=json.load(f)
    runs=raw["states"]
    if raw["metadata"]["real_native_ac_pf_calls"]!=5 or len(runs)!=5:
        raise ValueError("Five true previous source AC repairs not archived")
    if [r["scenario"] for r in runs]!=[
         "bus34_predicted","bus92_predicted","bus19_predicted",
         "all_three_half","all_three_full"]:
        raise ValueError("History source scenario identity changed")
    half,full=runs[3],runs[4]
    if (not half["converged"] or not full["converged"] or
        half["physics"]["feasible"] or full["physics"]["feasible"] or
        abs(half["generator_q"]["total_excess"]-Q_HALF)>1e-5 or
        abs(full["generator_q"]["total_excess"]-Q_FULL)>1e-5 or
        half["generator_q"]["top_12"][0]["bus_id"]!=92 or
        full["generator_q"]["top_12"][0]["bus_id"]!=36 or
        len(half["generator_q"]["top_12"])!=1 or
        len(full["generator_q"]["top_12"])!=1):
        raise ValueError("Opposite previous source Q offenders no longer verified")
    source=IEEE118NineControlSubset()
    g=source.source["gen"]
    if (len(g)!=54 or int(g[45,GEN_BUS])!=103 or
        int(g[14,GEN_BUS])!=32 or
        abs(g[45,VG]-1.01)>1e-9 or
        abs(g[14,VG]-.963)>1e-9):
        raise ValueError("Source IEEE118 base PV generator setpoints changed")
    raw_deltas=raw["metadata"]["source_q_repair_proposals"]
    if set(raw_deltas)!={"19","34","92"}:
        raise ValueError("Wrong archived original generator control set")
    proposal={}
    for bus,idx in ID_BY_BUS.items():
        item=raw_deltas[str(bus)]
        if item["generator_row_1based"]!=idx+1:
            raise ValueError("Source Q repair mapping changed")
        step=float(item["preregistered_clipped_delta_vg_pu"])
        if not math.isfinite(step) or not 0<step<=.008:
            raise ValueError("Invalid previously frozen source clipped Q/VG step")
        proposal[bus]=step
        if int(g[idx,GEN_BUS])!=bus:
            raise ValueError("Original generator source BUS misidentified")
    for alpha in ALPHAS:
        for bus,idx in ID_BY_BUS.items():
            x=float(g[idx,VG])+alpha*proposal[bus]
            record=source.source["bus"][source.source["bus"][:,0]==bus]
            if len(record)!=1 or not record[0,VMIN]<=x<=record[0,VMAX]:
                raise ValueError("Interpolated alpha VG violates source bus bounds")
    return source,proposal


def run_four(path=PREVIOUS):
    solver,proposal=history_source_preflight(path)
    source=solver.source
    rows=[]
    physical_calls=0
    for alpha in ALPHAS:
        case={key:(v.copy() if isinstance(v,np.ndarray) else v)
              for key,v in source.items()}
        case["gen"][45,VG]=.99
        case["gen"][14,VG]=.973
        for bus,idx in ID_BY_BUS.items():
            case["gen"][idx,VG]+=alpha*proposal[bus]
        if not np.array_equal(case["gen"][:,PG],source["gen"][:,PG]):
            raise ValueError("Source generator PG changed, invalid physical experiment")
        allowed={45,14,*ID_BY_BUS.values()}
        other=np.ones(54,dtype=bool)
        other[list(allowed)]=False
        if not np.array_equal(case["gen"][other,VG],source["gen"][other,VG]):
            raise ValueError("Noncontrolled original source generator VG changed")
        row={"scenario":f"alpha_{alpha:.1f}",
          "alpha":alpha,
          "actual_native_ac_pf_call":physical_calls+1,
          "source_original_vg_changes_pu":{"bus103":-.02,"bus32":+.01,
             **{"bus"+str(bus):alpha*step for bus,step in proposal.items()}},
          "solver_converged":False,"solver_error":"",
          "all_checked_original_constraints_feasible":False,
          "physical_metrics":None,"source_generator_q":None,
          "source_generator_p":None,"source_bus_v":None,
          "original_positive_rate_a":None,
          "reached_feasible_original_economic_cost":None}
        physical_calls+=1
        try:
            out,success=runpf(case,solver.settings)
            row["solver_converged"]=bool(success)
            if not success:
                row["solver_error"]="PYPOWER native AC NR returned success=False"
            else:
                physical=physics_118(out,source)
                q=top_generator_violations(out["gen"],source["gen"],"Q")
                p=top_generator_violations(out["gen"],source["gen"],"P")
                v=top_voltage_violations(out["bus"],source["bus"])
                thermal=branch_terminal_source_limits(out["branch"],source["branch"])
                if (abs(q["total_excess"]-physical["q_sum_excess_mvar"])>1e-6 or
                    abs(p["total_excess"]-physical["p_sum_excess_mw"])>1e-6 or
                    abs(v["total_excess_pu"]-physical["voltage_sum_excess_pu"])>1e-6 or
                    abs(thermal["total_excess_mva"]-physical["thermal_sum_excess_mva"])>1e-6):
                    raise ValueError("Original source P Q V MVA independently recalculated metrics disagree")
                row.update(
                  all_checked_original_constraints_feasible=bool(physical["feasible"]),
                  physical_metrics=physical,source_generator_q=q,source_generator_p=p,
                  source_bus_v=v,original_positive_rate_a=thermal,
                  reached_feasible_original_economic_cost=(
                       physical["actual_economic_cost"] if physical["feasible"] else None))
        except Exception as err:
            row["solver_error"]=(type(err).__name__+": "+str(err))[:300]
            if row["physical_metrics"] is None:
                row["solver_converged"]=False
        rows.append(row)
        print("I23_REAL_AC",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    return {"metadata":{
        "protocol":"research/ITERATION23_PROTOCOL.md",
        "actual_native_ac_pf_calls":physical_calls,
        "preregistered_native_ac_pf_calls":4,
        "original_ieee118_source":"unchanged PYPOWER case118",
        "prior_real_I22_baselines_reused_not_new_pf_calls":True,
        "previous_half_source_Q_excess_mvar":Q_HALF,
        "previous_full_source_Q_excess_mvar":Q_FULL,
        "previous_source_vg_repair_deltas":proposal,
        "alphas_fixed_in_preregistration":list(ALPHAS),
        "num_optimizer_gadapt_calls":0,"num_ac_opf_calls":0,
        "fixed_all_54_original_generators_pg":True,
        "python":platform.python_version(),"pandas":pd.__version__,
        "scipy":scipy.__version__,
        "public_ieee_case_not_operational_data":True,
    },"states":rows}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous",default=PREVIOUS)
    p.add_argument("--json",default="iteration23_bracket.json")
    p.add_argument("--csv",default="iteration23_bracket.csv")
    a=p.parse_args()
    data=run_four(a.previous)
    with open(a.json,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,sort_keys=True,allow_nan=False)
    fields=("scenario","alpha","actual_native_ac_pf_call",
         "solver_converged","solver_error",
         "source_physically_feasible","original_Q_offender_count",
         "original_total_Q_excess_mvar","original_P_offender_count",
         "original_voltage_offender_count","original_positive_Rate_A_overloads",
         "max_complex_AC_nodal_balance_mva",
         "feasible_original_economic_cost_only_when_passed")
    with open(a.csv,"w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in data["states"]:
            phy=r["physical_metrics"] or {}
            writer.writerow({
              "scenario":r["scenario"],"alpha":r["alpha"],
              "actual_native_ac_pf_call":r["actual_native_ac_pf_call"],
              "solver_converged":r["solver_converged"],"solver_error":r["solver_error"],
              "source_physically_feasible":r["all_checked_original_constraints_feasible"] if r["physical_metrics"] is not None else None,
              "original_Q_offender_count":r["source_generator_q"]["count"] if r["source_generator_q"] else None,
              "original_total_Q_excess_mvar":r["source_generator_q"]["total_excess"] if r["source_generator_q"] else None,
              "original_P_offender_count":r["source_generator_p"]["count"] if r["source_generator_p"] else None,
              "original_voltage_offender_count":r["source_bus_v"]["count"] if r["source_bus_v"] else None,
              "original_positive_Rate_A_overloads":r["original_positive_rate_a"]["violated_branches"] if r["original_positive_rate_a"] else None,
              "max_complex_AC_nodal_balance_mva":phy.get("max_nodal_mismatch_mva"),
              "feasible_original_economic_cost_only_when_passed":r["reached_feasible_original_economic_cost"]
            })
    print("I23_SUMMARY",json.dumps(data["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
