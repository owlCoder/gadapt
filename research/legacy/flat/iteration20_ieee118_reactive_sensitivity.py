"""Iteration 20: 8 real IEEE118 original source AC NR Q-control probes.

All 54 original generator Pg remain fixed; only original VG of #46 BUS103
and #48 BUS105 vary by +/- 0.02. The baseline is the ALREADY measured
original source PF in I19, not an unaccounted ninth new simulator call.
Not an optimizer or evidence of feasible AC-OPF.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import scipy

from pypower.idx_gen import GEN_BUS, PG, VG, QG, QMIN, QMAX
from pypower.idx_bus import VMIN, VMAX
from pypower.runpf import runpf

from research.iteration18_ieee118_gadapt_transfer import IEEE118NineControlSubset,physics_118
from research.iteration19_ieee118_forensic_diagnostic import (
    top_generator_violations,top_voltage_violations,branch_terminal_source_limits,
)

PREVIOUS="research/results/ieee118_iteration19_forensic_10_real_ac_20261021.json"
ID103=45
ID105=47
DELTA=.02


def preregistered_states():
    return [
      ("gen103_minus",-.02,0.),
      ("gen103_plus",+.02,0.),
      ("gen105_minus",0.,-.02),
      ("gen105_plus",0.,+.02),
      ("both_minus_minus",-.02,-.02),
      ("both_minus_plus",-.02,+.02),
      ("both_plus_minus",+.02,-.02),
      ("both_plus_plus",+.02,+.02),
    ]


def source_sensitivity_preflight(previous_path=PREVIOUS):
    with open(previous_path,encoding="utf-8") as f:
        raw=json.load(f)
    if raw["metadata"]["actual_ac_pf_calls"]!=10 or len(raw["states"])!=10:
        raise ValueError("Missing prerecorded source IEEE118 baseline")
    baseline=raw["states"][0]
    detail=baseline["details"]
    if (not baseline["converged"] or
        baseline["kind"]!="original_source_initial_pg_vg" or
        detail is None or detail["physical"]["feasible"] or
        detail["original_slack_bus_id"]!=69):
        raise ValueError("Wrong already measured IEEE118 source reference")
    reference=IEEE118NineControlSubset()
    source=reference.source
    gen=source["gen"]
    bus=source["bus"]
    if not (len(gen)==54 and int(gen[ID103,GEN_BUS])==103 and
            int(gen[ID105,GEN_BUS])==105 and
            abs(gen[ID103,VG]-1.01)<1e-9 and
            abs(gen[ID105,VG]-.965)<1e-9):
        raise ValueError("Original 2019(?) IEEE118 source generator setpoints drifted")
    if (abs(detail["generator_q_mvar"]["total_excess"]-78.09919501728558)>1e-5 or
        not any(z["bus_id"]==103 and abs(z["above"]-35.42236358206827)<1e-5
                for z in detail["generator_q_mvar"]["top_12"]) or
        not any(z["bus_id"]==105 and abs(z["below"]-10.334525252389284)<1e-5
                for z in detail["generator_q_mvar"]["top_12"])):
        raise ValueError("I19 source Q violation identity changed")
    bound={int(row[0]):(float(row[VMIN]),float(row[VMAX])) for row in bus}
    controls=[(ID103,103),(ID105,105)]
    for k,bus_id in controls:
        if int(bus[bus[:,0]==bus_id,1][0])!=2:
            raise ValueError("Original IEEE118 Q-probe gen BUS must be PV")
        low,high=bound[bus_id]
        if not (low<=gen[k,VG]-DELTA<=high and low<=gen[k,VG]+DELTA<=high):
            raise ValueError("Voltage perturbation exceeds original IEEE118 bus bounds")
    scenarios=preregistered_states()
    if len(scenarios)!=8 or len(set((a,b) for _,a,b in scenarios))!=8:
        raise ValueError("Exactly 8 distinct pre-registered probes")
    return detail,reference


def original_specific_q(solved_gen,source_gen,index):
    q=float(solved_gen[index,QG])
    lo=float(source_gen[index,QMIN])
    hi=float(source_gen[index,QMAX])
    return {"source_generator_row_1based":index+1,
            "original_bus_id":int(source_gen[index,GEN_BUS]),
            "qg_mvar":q,"source_qmin_mvar":lo,"source_qmax_mvar":hi,
            "q_excess_below_min_mvar":max(lo-q,0.),
            "q_excess_above_max_mvar":max(q-hi,0.),
            "q_total_excess_mvar":max(lo-q,0.)+max(q-hi,0.)}


def run_eight(previous_path=PREVIOUS):
    reference,engine=source_sensitivity_preflight(previous_path)
    basegen=engine.source["gen"]
    base103=float(basegen[ID103,VG])
    base105=float(basegen[ID105,VG])
    baseq=reference["generator_q_mvar"]["total_excess"]
    old103=next(x for x in reference["generator_q_mvar"]["top_12"] if x["bus_id"]==103)
    old105=next(x for x in reference["generator_q_mvar"]["top_12"] if x["bus_id"]==105)
    records=[]
    actual_calls=0
    for label,d103,d105 in preregistered_states():
        case={k:(v.copy() if isinstance(v,np.ndarray) else v)
              for k,v in engine.source.items()}
        case["gen"][ID103,VG]=base103+d103
        case["gen"][ID105,VG]=base105+d105
        if not np.array_equal(case["gen"][:,PG],basegen[:,PG]):
            raise ValueError("Unintended PG redispatch")
        untouched=np.ones(len(basegen),dtype=bool)
        untouched[[ID103,ID105]]=False
        if not np.array_equal(case["gen"][untouched,VG],basegen[untouched,VG]):
            raise ValueError("Unintended change to non-probed generator VG")
        row={"scenario":label,
             "gen103_delta_vg_pu":d103,"gen105_delta_vg_pu":d105,
             "gen103_source_vg_pu":base103+d103,
             "gen105_source_vg_pu":base105+d105,
             "actual_native_ac_pf_call":actual_calls+1,
             "converged":False,"solver_error":"","physics":None,
             "q_source_generators":None,
             "generator_p":None,"generator_q":None,
             "voltage_bus":None,"thermal_original_rate_a":None,
             "delta_total_q_excess_mvar_vs_i19_baseline":None,
             "delta_q103_excess_mvar_vs_i19_baseline":None,
             "delta_q105_excess_mvar_vs_i19_baseline":None,
             "both_target_q_generators_within_limits":None}
        actual_calls+=1
        try:
            solved,success=runpf(case,engine.settings)
            row["converged"]=bool(success)
            if not success:
                row["solver_error"]="PYPOWER runpf returned success=False"
            else:
                checked=physics_118(solved,engine.source)
                q103=original_specific_q(solved["gen"],basegen,ID103)
                q105=original_specific_q(solved["gen"],basegen,ID105)
                q=top_generator_violations(solved["gen"],basegen,"Q")
                p=top_generator_violations(solved["gen"],basegen,"P")
                v=top_voltage_violations(solved["bus"],engine.source["bus"])
                thermal=branch_terminal_source_limits(solved["branch"],engine.source["branch"])
                if (abs(q["total_excess"]-checked["q_sum_excess_mvar"])>1e-6 or
                    abs(p["total_excess"]-checked["p_sum_excess_mw"])>1e-6 or
                    abs(v["total_excess_pu"]-checked["voltage_sum_excess_pu"])>1e-6):
                    raise ValueError("Independent source physical Q/P/V accounting disagree")
                row.update(physics=checked,
                    q_source_generators={"bus103":q103,"bus105":q105},
                    generator_p=p,generator_q=q,voltage_bus=v,
                    thermal_original_rate_a=thermal,
                    delta_total_q_excess_mvar_vs_i19_baseline=float(q["total_excess"]-baseq),
                    delta_q103_excess_mvar_vs_i19_baseline=float(q103["q_total_excess_mvar"]-old103["total_excess"]),
                    delta_q105_excess_mvar_vs_i19_baseline=float(q105["q_total_excess_mvar"]-old105["total_excess"]),
                    both_target_q_generators_within_limits=bool(
                        q103["q_total_excess_mvar"]<=1e-3 and q105["q_total_excess_mvar"]<=1e-3))
        except Exception as err:
            row["solver_error"]=(type(err).__name__+": "+str(err))[:350]
            # Prevent invalid partial physical data from becoming credible.
            if row["physics"] is None:
                row["converged"]=False
        records.append(row)
        print("I20_REAL_AC",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    return {"metadata":{
       "protocol":"research/ITERATION20_PROTOCOL.md",
       "original_ieee118_source_model":"unaltered PYPOWER case118",
       "i19_source_baseline_not_a_new_ac_call":True,
       "source_q_baseline_mvar":baseq,
       "i19_actual_ac_calls_historical":10,
       "actual_native_ac_pf_calls":actual_calls,
       "optimizer_runs":0,
       "source_generator_indices_zero_based":[ID103,ID105],
       "fixed_source_PG_all_54":True,
       "python":platform.python_version(),
       "scipy":scipy.__version__,"pandas":pd.__version__,
       "public_reference_network_not_operational_data":True,
       },"runs":records}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--previous",default=PREVIOUS)
    parser.add_argument("--json",default="iteration20_q_screen.json")
    parser.add_argument("--csv",default="iteration20_q_screen.csv")
    args=parser.parse_args()
    data=run_eight(args.previous)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,sort_keys=True,allow_nan=False)
    cols=("scenario","actual_native_ac_pf_call","converged","solver_error",
          "gen103_delta_vg_pu","gen105_delta_vg_pu",
          "q103_actual_mvar","q103_excess_mvar","q105_actual_mvar","q105_excess_mvar",
          "delta_q103_excess_mvar_vs_baseline","delta_q105_excess_mvar_vs_baseline",
          "q_offender_count","q_total_excess_mvar","q_delta_total_vs_baseline_mvar",
          "both_target_q_within_bounds","entire_source_physically_feasible",
          "voltage_violation_count","p_violation_count","rated_thermal_violation_count",
          "max_ac_nodal_mismatch_mva",
          "source_economic_cost_diagnostic_not_feasible_opf")
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader()
        for r in data["runs"]:
            q=r["q_source_generators"] or {}
            q103=q.get("bus103") or {}
            q105=q.get("bus105") or {}
            checked=r["physics"] or {}
            w.writerow({
              "scenario":r["scenario"],"actual_native_ac_pf_call":r["actual_native_ac_pf_call"],
              "converged":r["converged"],"solver_error":r["solver_error"],
              "gen103_delta_vg_pu":r["gen103_delta_vg_pu"],
              "gen105_delta_vg_pu":r["gen105_delta_vg_pu"],
              "q103_actual_mvar":q103.get("qg_mvar"),
              "q103_excess_mvar":q103.get("q_total_excess_mvar"),
              "q105_actual_mvar":q105.get("qg_mvar"),
              "q105_excess_mvar":q105.get("q_total_excess_mvar"),
              "delta_q103_excess_mvar_vs_baseline":r["delta_q103_excess_mvar_vs_i19_baseline"],
              "delta_q105_excess_mvar_vs_baseline":r["delta_q105_excess_mvar_vs_i19_baseline"],
              "q_offender_count":r["generator_q"]["count"] if r["generator_q"] else None,
              "q_total_excess_mvar":r["generator_q"]["total_excess"] if r["generator_q"] else None,
              "q_delta_total_vs_baseline_mvar":r["delta_total_q_excess_mvar_vs_i19_baseline"],
              "both_target_q_within_bounds":r["both_target_q_generators_within_limits"],
              "entire_source_physically_feasible":checked.get("feasible"),
              "voltage_violation_count":r["voltage_bus"]["count"] if r["voltage_bus"] else None,
              "p_violation_count":r["generator_p"]["count"] if r["generator_p"] else None,
              "rated_thermal_violation_count":r["thermal_original_rate_a"]["violated_branches"] if r["thermal_original_rate_a"] else None,
              "max_ac_nodal_mismatch_mva":checked.get("max_nodal_mismatch_mva"),
              "source_economic_cost_diagnostic_not_feasible_opf":checked.get("actual_economic_cost")
            })
    print("I20_SUMMARY",json.dumps(data["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
