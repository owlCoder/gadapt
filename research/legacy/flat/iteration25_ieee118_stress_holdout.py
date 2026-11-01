"""Iteration25: stress fixed prior IEEE118 physically feasible PV controllers.

Exactly TEN NEW genuine AC NR PF calls: original source public IEEE118 PD/QD
scaled by 0.98 and 1.02, five SOURCE-feasible controller vectors recorded
and selected BEFORE stress evaluations. No optimization, no new GAdapt
operator, no free original-baseline PF, no industrial field claim.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import scipy
from pypower.idx_bus import PD, QD
from pypower.idx_gen import PG, VG
from pypower.runpf import runpf

from research.iteration24_ieee118_fivepv_real_gadapt import (
    IEEE118FiveRelevantPV,CONTROL_BUS_TO_SOURCE_GEN,METHODS
)
from research.iteration18_ieee118_gadapt_transfer import physics_118
from research.iteration19_ieee118_forensic_diagnostic import (
    top_generator_violations,top_voltage_violations,
    branch_terminal_source_limits
)

PREVIOUS_I23="research/results/ieee118_iteration23_qbracket_4_real_ac_20261021.json"
PREVIOUS_I24="research/results/ieee118_iteration24_legacy_gadapt_de_random_powell_20261021.json"
FACTORS=(.98,1.02)
ORDER=("historic_i23_alpha08","gadapt_legacy","scipy_de","random_search","bounded_powell")


def selected_original_source_controllers(i23=PREVIOUS_I23,i24=PREVIOUS_I24):
    with open(i23,encoding="utf-8") as f:
        historic=json.load(f)
    with open(i24,encoding="utf-8") as f:
        trial=json.load(f)
    if (historic["metadata"]["actual_native_ac_pf_calls"]!=4 or
        len(historic["states"])!=4 or
        trial["metadata"]["true_AC_PF_calls"]!=1152 or
        len(trial["runs"])!=12 or
        trial["metadata"]["common_control_buses"]!=
        [bus for bus,_ in CONTROL_BUS_TO_SOURCE_GEN] or
        set(trial["metadata"]["methods"])!=set(METHODS) or
        trial["metadata"]["budget_real_AC_per_method_seed"]!=96):
        raise ValueError("Original source calibrated prior data changed")
    entry=historic["states"][2]
    if (entry["alpha"]!=.8 or
        not entry["all_checked_original_constraints_feasible"] or
        not entry["solver_converged"] or
        abs(entry["reached_feasible_original_economic_cost"]-
            131198.7975746236)>1e-5):
        raise ValueError("Preregistered source alpha0.8 physically valid historic reference unavailable")
    grid=IEEE118FiveRelevantPV()
    source=grid.source
    alpha_case=source["gen"].copy()
    allowed={k for _,k in CONTROL_BUS_TO_SOURCE_GEN}
    for bus,gen_idx in CONTROL_BUS_TO_SOURCE_GEN:
        alpha_case[gen_idx,VG]+=float(entry["source_original_vg_changes_pu"]["bus"+str(bus)])
    # source reference includes the exact 5 original source generator VG,
    # no new simulator call and no wholesale source modifications.
    if any((abs(alpha_case[i,VG]-source["gen"][i,VG])>0) for i in
           range(len(source["gen"])) if i not in allowed):
        raise ValueError("Prior source reference mutates unrelated generator")
    points={"historic_i23_alpha08":{
        "vector":alpha_case[[i for _,i in CONTROL_BUS_TO_SOURCE_GEN],VG].astype(float),
        "historic_original_feasible_cost":entry["reached_feasible_original_economic_cost"],
        "historic_seed":None}}
    for method in METHODS:
        candidates=[r for r in trial["runs"] if
                    r["method"]==method and
                    r["real_ac_pf_calls"]==96 and
                    r["feasible_real_ac_candidates"]>0 and
                    r["best_feasible_economic_cost"] is not None and
                    r["best_feasible_physical_metrics"] is not None and
                    r["best_feasible_physical_metrics"]["feasible"]]
        if len(candidates)!=3:
            raise ValueError("Original benchmark missing 3 valid method source runs")
        winner=min(candidates,key=lambda r:(r["best_feasible_economic_cost"],r["seed"]))
        points[method]={
          "vector":np.asarray(winner["best_feasible_vector"],float),
          "historic_original_feasible_cost":float(winner["best_feasible_economic_cost"]),
          "historic_seed":int(winner["seed"])}
    if tuple(points)!=ORDER:
        raise ValueError("Original source five selected controller identity/order drift")
    for name,item in points.items():
        x=item["vector"]
        if x.shape!=(5,) or not np.all(np.isfinite(x)):
            raise ValueError("Missing authentic 5D source controller from prior AC")
        if any(v<lo-1e-8 or v>hi+1e-8 for v,(lo,hi) in zip(x,grid.bounds)):
            raise ValueError("Selected prior five PV controller not in source common local box")
    return grid,points


def run_ten(i23=PREVIOUS_I23,i24=PREVIOUS_I24):
    grid,selected=selected_original_source_controllers(i23,i24)
    source=grid.source
    rows=[]
    physical_calls=0
    for factor in FACTORS:
        for name in ORDER:
            info=selected[name]
            scenario={k:(v.copy() if isinstance(v,np.ndarray) else v)
                      for k,v in source.items()}
            scenario["bus"][:,PD]*=factor
            scenario["bus"][:,QD]*=factor
            for (_,gen_idx),val in zip(CONTROL_BUS_TO_SOURCE_GEN,info["vector"]):
                scenario["gen"][gen_idx,VG]=val
            if (not np.array_equal(scenario["gen"][:,PG],source["gen"][:,PG]) or
                not np.array_equal(scenario["bus"][:,PD],source["bus"][:,PD]*factor) or
                not np.array_equal(scenario["bus"][:,QD],source["bus"][:,QD]*factor)):
                raise ValueError("Unregistered source PG or load scenario change")
            row={"load_factor":factor,"prior_controller_name":name,
                 "prior_source_best_feasible_economic_cost":info["historic_original_feasible_cost"],
                 "prior_source_seed":info["historic_seed"],
                 "five_original_pv_setpoints_pu":list(map(float,info["vector"])),
                 "actual_original_ac_pf_call":physical_calls+1,
                 "solver_converged":False,"solver_error":"",
                 "source_stress_feasible":False,
                 "physical_metrics":None,
                 "generator_p":None,"generator_q":None,
                 "bus_voltage":None,"branch_positive_rated_mva":None,
                 "stress_feasible_economic_cost":None}
            physical_calls+=1  # only directly at true original solver boundary.
            try:
                solved,success=runpf(scenario,grid.reference.settings)
                row["solver_converged"]=bool(success)
                if not success:
                    row["solver_error"]="Stressed original IEEE118 PYPOWER runpf success=False"
                else:
                    phy=physics_118(solved,scenario)
                    p=top_generator_violations(solved["gen"],scenario["gen"],"P")
                    q=top_generator_violations(solved["gen"],scenario["gen"],"Q")
                    v=top_voltage_violations(solved["bus"],scenario["bus"])
                    t=branch_terminal_source_limits(solved["branch"],scenario["branch"])
                    if (abs(p["total_excess"]-phy["p_sum_excess_mw"])>1e-6 or
                        abs(q["total_excess"]-phy["q_sum_excess_mvar"])>1e-6 or
                        abs(v["total_excess_pu"]-phy["voltage_sum_excess_pu"])>1e-6 or
                        abs(t["total_excess_mva"]-phy["thermal_sum_excess_mva"])>1e-6):
                        raise ValueError("Inconsistent true physical stress source constraint audits")
                    row.update(source_stress_feasible=bool(phy["feasible"]),
                        physical_metrics=phy,generator_p=p,generator_q=q,
                        bus_voltage=v,branch_positive_rated_mva=t,
                        stress_feasible_economic_cost=(
                            phy["actual_economic_cost"] if phy["feasible"] else None))
            except Exception as exc:
                row["solver_error"]=(type(exc).__name__+": "+str(exc))[:280]
                if row["physical_metrics"] is None:
                    row["solver_converged"]=False
            rows.append(row)
            print("I25_STRESS_AC",json.dumps(row,allow_nan=False,sort_keys=True),flush=True)
    return {"metadata":{
       "protocol":"research/ITERATION25_PROTOCOL.md",
       "original_source":"PYPOWER case118 original with ONLY PD,QD scaled 0.98,1.02",
       "source_I23_and_I24_feasible_points_preselected_not_new_ac_calls":True,
       "original_118_bus_54_gen_186_branch_PG_and_limit_values_unchanged":True,
       "tested_stressed_load_factors":list(FACTORS),
       "original_five_pv_controller_order":[bus for bus,_ in CONTROL_BUS_TO_SOURCE_GEN],
       "preregistered_number_of_new_native_ac_pf_calls":10,
       "actual_new_native_ac_pf_calls":physical_calls,
       "new_optimizer_calls":0,"new_ac_opf_calls":0,
       "python":platform.python_version(),"pandas":pd.__version__,
       "scipy":scipy.__version__,
       "artificial_public_grid_stress_not_operational_data":True,
    },"states":rows}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--i23",default=PREVIOUS_I23)
    p.add_argument("--i24",default=PREVIOUS_I24)
    p.add_argument("--json",default="iteration25_ieee118_stress.json")
    p.add_argument("--csv",default="iteration25_ieee118_stress.csv")
    args=p.parse_args()
    result=run_ten(args.i23,args.i24)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
    fields=("load_factor","prior_controller_name","prior_source_seed",
        "actual_original_ac_pf_call","solver_converged","solver_error",
        "source_stress_feasible","original_Q_offender_count",
        "original_Q_total_excess_mvar",
        "original_P_offender_count","original_P_total_excess_mw",
        "original_V_bus_offender_count",
        "original_positive_Rate_A_overloads",
        "maximum_AC_KCL_mva",
        "stress_feasible_economic_cost")
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in result["states"]:
            phy=r["physical_metrics"] or {}
            w.writerow({
                "load_factor":r["load_factor"],
                "prior_controller_name":r["prior_controller_name"],
                "prior_source_seed":r["prior_source_seed"],
                "actual_original_ac_pf_call":r["actual_original_ac_pf_call"],
                "solver_converged":r["solver_converged"],
                "solver_error":r["solver_error"],
                "source_stress_feasible":r["source_stress_feasible"] if r["physical_metrics"] is not None else None,
                "original_Q_offender_count":r["generator_q"]["count"] if r["generator_q"] else None,
                "original_Q_total_excess_mvar":r["generator_q"]["total_excess"] if r["generator_q"] else None,
                "original_P_offender_count":r["generator_p"]["count"] if r["generator_p"] else None,
                "original_P_total_excess_mw":r["generator_p"]["total_excess"] if r["generator_p"] else None,
                "original_V_bus_offender_count":r["bus_voltage"]["count"] if r["bus_voltage"] else None,
                "original_positive_Rate_A_overloads":r["branch_positive_rated_mva"]["violated_branches"] if r["branch_positive_rated_mva"] else None,
                "maximum_AC_KCL_mva":phy.get("max_nodal_mismatch_mva"),
                "stress_feasible_economic_cost":r["stress_feasible_economic_cost"],
            })
    print("I25_SUMMARY",json.dumps(result["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
