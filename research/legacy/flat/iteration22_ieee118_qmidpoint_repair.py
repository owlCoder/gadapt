"""Iteration22: five genuine IEEE118 source AC PF Q/VG feasibility-repair probes.

Classical finite-difference Q/VG sensitivities computed ONLY from prior
fully archived I21 (8 paid AC), with source I21 BUS32+0.01 as measured
baseline. All 54 PG fixed; only source VG BUS103, BUS32 and three
bounded predicted PV controls vary. This is NOT a novel GAdapt algorithm.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import scipy

from pypower.idx_bus import VMIN, VMAX
from pypower.idx_gen import GEN_BUS, PG, VG, QMIN, QMAX
from pypower.runpf import runpf

from research.iteration18_ieee118_gadapt_transfer import IEEE118NineControlSubset,physics_118
from research.iteration19_ieee118_forensic_diagnostic import (
    top_generator_violations,top_voltage_violations,branch_terminal_source_limits,
)
from research.iteration20_ieee118_reactive_sensitivity import original_specific_q

PREVIOUS="research/results/ieee118_iteration21_four_qmin_8_real_ac_20261021.json"
SOURCE_ID_BY_BUS={34:15,92:42,19:8}
STEP_HALF_WIDTH=.01
MAX_PREDICTED_STEP=.008
Q_BASELINE=30.525900533161856


def fixed_control_preflight(path=PREVIOUS):
    with open(path,encoding="utf-8") as f:
        archive=json.load(f)
    runs=archive["states"]
    if archive["metadata"]["actual_native_ac_pf_calls"]!=8 or len(runs)!=8:
        raise ValueError("Previous original source 8 real AC results are missing")
    by={r["scenario"]:r for r in runs}
    if len(by)!=8 or not all(x["converged"] and x["physics"] is not None for x in runs):
        raise ValueError("Previous I21 Q sensitivity source AC did not finish validly")
    base=by["bus32_plus"]
    if (base["physics"]["feasible"] or
        abs(base["generator_q"]["total_excess"]-Q_BASELINE)>1e-5 or
        {x["bus_id"] for x in base["generator_q"]["top_12"]}!={34,92,19}):
        raise ValueError("Wrong real source I21 BUS32 repaired Q reference")
    grid=IEEE118NineControlSubset()
    source=grid.source
    gen=source["gen"]
    if (len(gen)!=54 or int(gen[45,GEN_BUS])!=103 or
        int(gen[14,GEN_BUS])!=32 or
        abs(gen[45,VG]-1.01)>1e-8 or
        abs(gen[14,VG]-.963)>1e-8):
        raise ValueError("Original IEEE118 source Q repair identities changed")
    prediction={}
    for bus,idx in SOURCE_ID_BY_BUS.items():
        plus=by["bus"+str(bus)+"_plus"]
        minus=by["bus"+str(bus)+"_minus"]
        if plus["target_bus_id"]!=bus or minus["target_bus_id"]!=bus:
            raise ValueError("Archive source Q gradient target not matched")
        value_plus=plus["target_q"]["qg_mvar"]
        value_minus=minus["target_q"]["qg_mvar"]
        slope=(value_plus-value_minus)/(2.*STEP_HALF_WIDTH)
        if not math.isfinite(slope) or slope<=0:
            raise ValueError("Source Q/VG slope must be finite and positive")
        offending=next(x for x in base["generator_q"]["top_12"] if x["bus_id"]==bus)
        qbaseline=offending["value_mw_or_mvar"]
        qmid=(float(gen[idx,QMIN])+float(gen[idx,QMAX]))/2.
        unconstrained=(qmid-qbaseline)/slope
        delta=float(np.clip(unconstrained,0.,MAX_PREDICTED_STEP))
        if not 0<delta<=MAX_PREDICTED_STEP:
            raise ValueError("Source Q step zero/inconsistent with original QMIN")
        bound=source["bus"][source["bus"][:,0]==bus]
        if len(bound)!=1 or int(bound[0,1])!=2:
            raise ValueError("Source required PV generator missing")
        if not bound[0,VMIN]<=gen[idx,VG]+delta<=bound[0,VMAX]:
            raise ValueError("Predicted sensitivity step outside original bus source V bounds")
        prediction[bus]={"generator_row_1based":idx+1,
            "original_generator_vg_pu":float(gen[idx,VG]),
            "already_measured_q_base_mvar":float(qbaseline),
            "source_qmin":float(gen[idx,QMIN]),
            "source_qmax":float(gen[idx,QMAX]),
            "target_midpoint_mvar":float(qmid),
            "finite_difference_q_slope_mvar_per_pu":float(slope),
            "unclipped_delta_vg_pu":float(unconstrained),
            "preregistered_clipped_delta_vg_pu":delta}
    if len(prediction)!=3:
        raise ValueError("Expected three source Q control corrections")
    return grid,prediction


def five_fixed_scenarios():
    return [
       ("bus34_predicted",{34:1.}),
       ("bus92_predicted",{92:1.}),
       ("bus19_predicted",{19:1.}),
       ("all_three_half",{34:.5,92:.5,19:.5}),
       ("all_three_full",{34:1.,92:1.,19:1.}),
    ]


def run_five(path=PREVIOUS):
    grid,formula=fixed_control_preflight(path)
    source=grid.source
    rows=[]
    physical_calls=0
    for label,scales in five_fixed_scenarios():
        case={k:(v.copy() if isinstance(v,np.ndarray) else v)
              for k,v in source.items()}
        case["gen"][45,VG]=.99
        case["gen"][14,VG]=float(source["gen"][14,VG])+.01
        for bus,fraction in scales.items():
            idx=SOURCE_ID_BY_BUS[bus]
            case["gen"][idx,VG]+=formula[bus]["preregistered_clipped_delta_vg_pu"]*fraction
        if not np.array_equal(case["gen"][:,PG],source["gen"][:,PG]):
            raise ValueError("Unpreregistered original PG change")
        allowed=set(SOURCE_ID_BY_BUS.values())|{45,14}
        masked=np.ones(54,dtype=bool)
        masked[list(allowed)]=False
        if not np.array_equal(case["gen"][masked,VG],source["gen"][masked,VG]):
            raise ValueError("Other original source generator VG modified")
        record={
           "scenario":label,
           "actual_native_ac_pf_call":physical_calls+1,
           "gen_vg_source_changes_pu":{
              "bus103":-.02,"bus32":+.01,
              **{"bus"+str(bus):formula[bus]["preregistered_clipped_delta_vg_pu"]*scales.get(bus,0.)
                 for bus in SOURCE_ID_BY_BUS}},
           "converged":False,
           "solver_error":"","physics":None,
           "generator_q":None,"generator_p":None,
           "bus_voltage":None,"branch_original_thermal":None,
           "target_q_individuals":None,
           "delta_total_q_excess_from_prior_source_baseline_mvar":None,
        }
        physical_calls+=1
        try:
            solved,ok=runpf(case,grid.settings)
            record["converged"]=bool(ok)
            if not ok:
                record["solver_error"]="Original IEEE118 NR PYPOWER runpf returned success=False"
            else:
                physics=physics_118(solved,source)
                q=top_generator_violations(solved["gen"],source["gen"],"Q")
                p=top_generator_violations(solved["gen"],source["gen"],"P")
                v=top_voltage_violations(solved["bus"],source["bus"])
                t=branch_terminal_source_limits(solved["branch"],source["branch"])
                if (abs(q["total_excess"]-physics["q_sum_excess_mvar"])>1e-6 or
                    abs(p["total_excess"]-physics["p_sum_excess_mw"])>1e-6 or
                    abs(v["total_excess_pu"]-physics["voltage_sum_excess_pu"])>1e-6):
                    raise ValueError("Source Q/P/V independent diagnostic metrics disagree")
                record.update(physics=physics,
                  generator_q=q,generator_p=p,bus_voltage=v,branch_original_thermal=t,
                  target_q_individuals={
                     "bus"+str(bus):original_specific_q(solved["gen"],source["gen"],idx)
                     for bus,idx in SOURCE_ID_BY_BUS.items()},
                  delta_total_q_excess_from_prior_source_baseline_mvar=float(
                       q["total_excess"]-Q_BASELINE))
        except Exception as err:
            record["solver_error"]=(type(err).__name__+": "+str(err))[:270]
            if record["physics"] is None:
                record["converged"]=False
        rows.append(record)
        print("I22_REAL_AC",json.dumps(record,sort_keys=True,allow_nan=False),flush=True)
    return {"metadata":{
       "protocol":"research/ITERATION22_PROTOCOL.md",
       "raw_original_ieee118_source":"PYPOWER case118",
       "real_native_ac_pf_calls":physical_calls,
       "max_preregistered_native_ac_calls":5,
       "baseline_source_i21_measurement_reused_not_evaluated":True,
       "historical_i21_ac_calls_not_recounted":8,
       "prior_source_q_violation_mvar":Q_BASELINE,
       "source_q_repair_proposals":formula,
       "algorithm":"previously measured central finite differences + clipped midpoint target; NOT novel GAdapt",
       "actual_gadapt_algorithm_calls":0,"actual_ac_opf_calls":0,
       "python":platform.python_version(),"pandas":pd.__version__,
       "scipy":scipy.__version__,
       "source_not_utility_operational_data":True,
    },"states":rows}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--previous",default=PREVIOUS)
    parser.add_argument("--json",default="iteration22_ieee118_qrepair.json")
    parser.add_argument("--csv",default="iteration22_ieee118_qrepair.csv")
    args=parser.parse_args()
    output=run_five(args.previous)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(output,f,indent=2,sort_keys=True,allow_nan=False)
    fields=("scenario","actual_native_ac_pf_call","converged","solver_error",
        "original_generator_q_offenders","total_Q_excess_mvar",
        "delta_Q_excess_from_prev_baseline_mvar",
        "original_generator_p_offenders","voltage_bus_offenders",
        "source_rated_thermal_overloads",
        "all_checked_physical_source_constraints_satisfied",
        "complex_ac_balance_max_mva",
        "economic_cost_only_if_source_feasible")
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in output["states"]:
            phys=r["physics"] or {}
            q=r["generator_q"] or {}
            w.writerow({
                "scenario":r["scenario"],"actual_native_ac_pf_call":r["actual_native_ac_pf_call"],
                "converged":r["converged"],"solver_error":r["solver_error"],
                "original_generator_q_offenders":q.get("count"),
                "total_Q_excess_mvar":q.get("total_excess"),
                "delta_Q_excess_from_prev_baseline_mvar":r["delta_total_q_excess_from_prior_source_baseline_mvar"],
                "original_generator_p_offenders":r["generator_p"]["count"] if r["generator_p"] else None,
                "voltage_bus_offenders":r["bus_voltage"]["count"] if r["bus_voltage"] else None,
                "source_rated_thermal_overloads":r["branch_original_thermal"]["violated_branches"] if r["branch_original_thermal"] else None,
                "all_checked_physical_source_constraints_satisfied":phys.get("feasible"),
                "complex_ac_balance_max_mva":phys.get("max_nodal_mismatch_mva"),
                "economic_cost_only_if_source_feasible":(
                    phys.get("actual_economic_cost") if phys.get("feasible") else None),
            })
    print("I22_SUMMARY",json.dumps(output["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
