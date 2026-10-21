"""Iteration21: eight pre-registered real IEEE118 AC QMIN sensitivity probes.

This is a physical diagnostic, not genetic optimization. Previous I20
BUS103 -0.02 source state is read from raw JSON, NOT a new free PF call.
Exactly four source generator VG controls (BUS34,92,19,32), each +/-0.01,
all original 54 Pg and every other Vg fixed (except prior BUS103 0.99).
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import scipy
from pypower.idx_gen import GEN_BUS,PG,VG
from pypower.idx_bus import VMIN,VMAX
from pypower.runpf import runpf

from research.iteration18_ieee118_gadapt_transfer import IEEE118NineControlSubset,physics_118
from research.iteration19_ieee118_forensic_diagnostic import (
    top_generator_violations,top_voltage_violations,branch_terminal_source_limits,
)
from research.iteration20_ieee118_reactive_sensitivity import original_specific_q

PREVIOUS="research/results/ieee118_iteration20_q_sensitivity_8_real_ac_20261021.json"
VG_BASELINE_103=.99
CONTROL_LIST=((15,34,.984),(42,92,.99),(8,19,.962),(14,32,.963))
VG_DELTA=.01


def preregistered_states():
    return [(f"bus{bus}_{tag}",index,bus,step) for index,bus,original in CONTROL_LIST
            for tag,step in (("minus",-VG_DELTA),("plus",VG_DELTA))]


def previous_measured_source_preflight(path=PREVIOUS):
    with open(path,encoding="utf-8") as f:
        data=json.load(f)
    if (data["metadata"]["actual_native_ac_pf_calls"]!=8 or
        len(data["runs"])!=8 or
        data["runs"][0]["scenario"]!="gen103_minus"):
        raise ValueError("I20 archived source physical reference unavailable")
    row=data["runs"][0]
    if (not row["converged"] or row["physics"] is None or
        row["physics"]["feasible"] or
        abs(row["generator_q"]["total_excess"]-32.34580769680004)>1e-5):
        raise ValueError("I20 reference source Q state changed")
    offenders=row["generator_q"]["top_12"]
    expected={34,92,19,32}
    if {x["bus_id"] for x in offenders} != expected or len(offenders)!=4:
        raise ValueError("Unexpected I20 remaining original source Q offenders")
    if abs(row["gen103_source_vg_pu"]-VG_BASELINE_103)>1e-8:
        raise ValueError("I20 selected source BUS103 voltage changed")
    source=IEEE118NineControlSubset()
    gen=source.source["gen"];bus=source.source["bus"]
    if len(gen)!=54 or len(bus)!=118 or int(gen[45,GEN_BUS])!=103:
        raise ValueError("Source IEEE118 generator identity drift")
    for idx,bus_id,vg in CONTROL_LIST:
        if int(gen[idx,GEN_BUS])!=bus_id or abs(float(gen[idx,VG])-vg)>1e-8:
            raise ValueError("Source original offender generator or VG changed")
        b=bus[bus[:,0]==bus_id]
        if len(b)!=1 or int(b[0,1])!=2:
            raise ValueError("Expected one PV source BUS")
        if not (b[0,VMIN]<=vg-VG_DELTA<=b[0,VMAX]
                and b[0,VMIN]<=vg+VG_DELTA<=b[0,VMAX]):
            raise ValueError("Source VG step exceeds original bus bounds")
    scenarios=preregistered_states()
    if len(scenarios)!=8 or len({(idx,step) for _,idx,_,step in scenarios})!=8:
        raise ValueError("Eight source-valid unique physical probes required")
    return row,source


def run_eight(path=PREVIOUS):
    previous,original=previous_measured_source_preflight(path)
    source=original.source
    old_q=float(previous["generator_q"]["total_excess"])
    rows=[]
    calls=0
    for label,gen_idx,bus_id,step in preregistered_states():
        case={key:(value.copy() if isinstance(value,np.ndarray) else value)
              for key,value in source.items()}
        case["gen"][45,VG]=VG_BASELINE_103
        case["gen"][gen_idx,VG]=source["gen"][gen_idx,VG]+step
        if not np.array_equal(case["gen"][:,PG],source["gen"][:,PG]):
            raise ValueError("Source PG mutated during reactive screen")
        other=np.ones(54,dtype=bool)
        other[[45,gen_idx]]=False
        if not np.array_equal(case["gen"][other,VG],source["gen"][other,VG]):
            raise ValueError("Other generators VG unexpectedly mutated")
        row={"scenario":label,
             "target_original_gen_row_1based":gen_idx+1,
             "target_bus_id":bus_id,
             "delta_vg_pu":step,
             "new_target_vg_pu":float(case["gen"][gen_idx,VG]),
             "fixed_bus103_vg_pu":VG_BASELINE_103,
             "actual_native_ac_pf_call":calls+1,
             "converged":False,"error":"",
             "physics":None,
             "target_q":None,"generator_q":None,
             "generator_p":None,"bus_v":None,"rated_thermal":None,
             "delta_source_Q_excess_mvar_from_i20":None}
        calls+=1
        try:
            solved,success=runpf(case,original.settings)
            row["converged"]=bool(success)
            if not success:
                row["error"]="Original PYPOWER runpf returned success=False"
            else:
                phys=physics_118(solved,source)
                q=top_generator_violations(solved["gen"],source["gen"],"Q")
                p=top_generator_violations(solved["gen"],source["gen"],"P")
                v=top_voltage_violations(solved["bus"],source["bus"])
                thermal=branch_terminal_source_limits(solved["branch"],source["branch"])
                target=original_specific_q(solved["gen"],source["gen"],gen_idx)
                if (abs(phys["q_sum_excess_mvar"]-q["total_excess"])>1e-6 or
                    abs(phys["p_sum_excess_mw"]-p["total_excess"])>1e-6 or
                    abs(phys["voltage_sum_excess_pu"]-v["total_excess_pu"])>1e-6):
                    raise ValueError("Original source physical violation bookkeeping mismatch")
                row.update(physics=phys,target_q=target,generator_q=q,
                    generator_p=p,bus_v=v,rated_thermal=thermal,
                    delta_source_Q_excess_mvar_from_i20=float(q["total_excess"]-old_q))
        except Exception as err:
            row["error"]=(type(err).__name__+": "+str(err))[:250]
            if row["physics"] is None:
                row["converged"]=False
        rows.append(row)
        print("I21_REAL_AC",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    return {"metadata":{
        "protocol":"research/ITERATION21_PROTOCOL.md",
        "actual_native_ac_pf_calls":calls,
        "preregistered_max_real_ac_calls":8,
        "i20_old_original_source_baseline_not_recomputed":True,
        "source_I20_total_q_excess_mvar":old_q,
        "all_source_54_generators_pg_fixed":True,
        "original_gen_46_bus103_vg_fixed_pu":VG_BASELINE_103,
        "original_controlled_generator_ids_zero_based":[x[0] for x in CONTROL_LIST],
        "additional_ac_opf_calls":0,"optimization_runs":0,
        "environment":{"python":platform.python_version(),
                       "pandas":pd.__version__,"scipy":scipy.__version__},
        "public_test_model_not_operational_data":True,
    },"states":rows}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--previous",default=PREVIOUS)
    ap.add_argument("--json",default="iteration21_ieee118_qmin_screen.json")
    ap.add_argument("--csv",default="iteration21_ieee118_qmin_screen.csv")
    args=ap.parse_args()
    data=run_eight(args.previous)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,sort_keys=True,allow_nan=False)
    keys=("scenario","actual_native_ac_pf_call","converged","error",
        "target_bus_id","delta_vg_pu","new_target_vg_pu",
        "target_q_actual_mvar","target_q_excess_mvar",
        "total_source_q_excess_mvar","delta_source_q_excess_vs_i20",
        "total_q_offender_count","bus_v_offender_count","generator_p_offender_count",
        "rated_thermal_overloads","physically_feasible",
        "max_complex_ac_mismatch_mva","source_economic_cost_diagnostic_only")
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        for x in data["states"]:
            q=x["generator_q"] or {}
            target=x["target_q"] or {}
            physical=x["physics"] or {}
            w.writerow({
              "scenario":x["scenario"],"actual_native_ac_pf_call":x["actual_native_ac_pf_call"],
              "converged":x["converged"],"error":x["error"],
              "target_bus_id":x["target_bus_id"],"delta_vg_pu":x["delta_vg_pu"],
              "new_target_vg_pu":x["new_target_vg_pu"],
              "target_q_actual_mvar":target.get("qg_mvar"),
              "target_q_excess_mvar":target.get("q_total_excess_mvar"),
              "total_source_q_excess_mvar":q.get("total_excess"),
              "delta_source_q_excess_vs_i20":x["delta_source_Q_excess_mvar_from_i20"],
              "total_q_offender_count":q.get("count"),
              "bus_v_offender_count":x["bus_v"]["count"] if x["bus_v"] else None,
              "generator_p_offender_count":x["generator_p"]["count"] if x["generator_p"] else None,
              "rated_thermal_overloads":x["rated_thermal"]["violated_branches"] if x["rated_thermal"] else None,
              "physically_feasible":physical.get("feasible"),
              "max_complex_ac_mismatch_mva":physical.get("max_nodal_mismatch_mva"),
              "source_economic_cost_diagnostic_only":physical.get("actual_economic_cost"),
            })
    print("I21_SUMMARY",json.dumps(data["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
