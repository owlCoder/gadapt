"""Iteration 16: original IEEE14/IEEE118 native quadratic economic AC-OPF.

Two actual native PYPOWER OPF calls. Per-run source PG/QG, V, original
positive RATE_A on both branch ends, posthoc AC nodal balance and cost.
No genetic algorithm or industrial deployment claims.
"""
import argparse
import csv
import json
import math
import platform
import time

import numpy as np
import pandas as pd
import scipy
from pypower.case14 import case14
from pypower.case118 import case118
from pypower.ppoption import ppoption

from research.iteration11_original_matpower_native_pf import (
    summed_limit_violation,original_rate_a_violation
)
from research.iteration14_original_acopf import (
    original_source_ac_residual,original_cost,timed_runopf,CONSTRAINT_TOL
)


def check_case_structure(source):
    bus=np.asarray(source["bus"],float)
    gen=np.asarray(source["gen"],float)
    branch=np.asarray(source["branch"],float)
    gencost=np.asarray(source["gencost"],float)
    if bus.ndim!=2 or gen.ndim!=2 or branch.ndim!=2 or gencost.ndim!=2:
        raise ValueError("Malformed source arrays")
    if bus.shape[1]<13 or gen.shape[1]<10 or branch.shape[1]<13:
        raise ValueError("Source case lacks MATPOWER original columns")
    if gencost.shape!=(len(gen),7):
        raise ValueError("Cost rows do not correspond to source generators")
    if not all(np.all(np.isfinite(arr)) for arr in (bus,gen,branch,gencost)):
        raise ValueError("Nonfinite source input")
    if not (np.all(gencost[:,0]==2) and np.all(gencost[:,3]==3)):
        raise ValueError("Only original quadratic polynomial costs supported")
    if not np.all(gen[:,7]==np.round(gen[:,7])):
        raise ValueError("Invalid source generator statuses")
    if np.any(branch[:,5]<0):
        raise ValueError("Negative source thermal rating")
    if int(np.sum(bus[:,1]==3))!=1:
        raise ValueError("Exactly one source slack bus is required")
    return {"original_bus_count":len(bus),"original_gen_count":len(gen),
            "original_active_gen_count":int(np.count_nonzero(gen[:,7]>0)),
            "original_branch_count":len(branch),
            "original_positive_rated_branches":int(np.count_nonzero((branch[:,5]>0)&(branch[:,10]>0))),
            "original_unrated_branches":int(np.count_nonzero((branch[:,5]==0)&(branch[:,10]>0)))}


def inspect_opf_result(results, source):
    info=check_case_structure(source)
    bus=np.asarray(results["bus"],float)
    gen=np.asarray(results["gen"],float)
    branch=np.asarray(results["branch"],float)
    if (len(bus)!=info["original_bus_count"] or
        len(gen)!=info["original_gen_count"] or
        len(branch)!=info["original_branch_count"]):
        raise ValueError("OPF output violates original element cardinality")
    if (not np.all(np.isfinite(bus)) or not np.all(np.isfinite(gen))
            or not np.all(np.isfinite(branch))):
        raise ValueError("Nonfinite OPF physical arrays")
    if not np.array_equal(bus[:,0].astype(int),source["bus"][:,0].astype(int)):
        raise ValueError("Source bus identity or order drift")
    if not np.array_equal(gen[:,0].astype(int),source["gen"][:,0].astype(int)):
        raise ValueError("Source generator row identity or order drift")
    if not np.array_equal(branch[:,:2].astype(int),source["branch"][:,:2].astype(int)):
        raise ValueError("Source branch order drift")
    active=np.asarray(source["gen"][:,7]>0)
    if not np.array_equal(active,gen[:,7]>0):
        raise ValueError("Original generator status drift")
    v=summed_limit_violation(bus[:,7],source["bus"][:,12],
        source["bus"][:,11],source["bus"][:,1]!=4)
    p=summed_limit_violation(gen[:,1],source["gen"][:,9],
        source["gen"][:,8],active)
    q=summed_limit_violation(gen[:,2],source["gen"][:,4],
        source["gen"][:,3],active)
    thermal=original_rate_a_violation(branch)
    pos=(branch[:,5]>0)&(branch[:,10]>0)
    from_mva=np.hypot(branch[:,13],branch[:,14])
    to_mva=np.hypot(branch[:,15],branch[:,16])
    abs_thermal=float(np.max(
        np.maximum(np.maximum(from_mva,to_mva)-branch[:,5],0.)[pos],initial=0.))
    kcl=original_source_ac_residual(results)
    obj=original_cost(results,source)
    checks={
       "original_bus_gen_branch_ids":True,
       "bus_voltage_bounds":max(v["max_below_limit"],v["max_above_limit"])<=CONSTRAINT_TOL["bus_voltage_pu"],
       "generator_P":max(p["max_below_limit"],p["max_above_limit"])<=CONSTRAINT_TOL["generator_p_mw"],
       "generator_Q":max(q["max_below_limit"],q["max_above_limit"])<=CONSTRAINT_TOL["generator_q_mvar"],
       "both_branch_ends_positive_RATE_A":abs_thermal<=CONSTRAINT_TOL["rated_branch_terminal_mva"],
       "AC_nodal_complex_balance":kcl["max_bus_nodal_mismatch_mva"]<=CONSTRAINT_TOL["nodal_mismatch_mva"],
       "original_polynomial_cost":obj["original_economic_objective_matches"],
    }
    return {"source":info,"posthoc_constraint_checks":checks,
            "independently_verified_ac_opf":bool(all(checks.values())),
            "individual_generator_p_bounds_mw":p,
            "individual_generator_q_bounds_mvar":q,
            "bus_voltage_bounds_pu":v,
            "source_rating_both_ends":thermal,
            "max_original_rate_a_terminal_mva_excess":abs_thermal,
            "AC_nodal_balance":kcl,
            "original_source_economic_cost":obj,
            "sum_branch_real_losses_MW_not_optimization_objective":
                float(np.sum((branch[:,13]+branch[:,15])[branch[:,10]>0]))}


def diagnostic():
    cases=[("case14",case14(),120),("case118",case118(),300)]
    opts=ppoption(OPF_ALG=560,PF_DC=0,OPF_FLOW_LIM=0,
        OPF_IGNORE_ANG_LIM=False,OPF_VIOLATION=5e-6,
        PDIPM_MAX_IT=100,VERBOSE=0,OUT_ALL=0)
    records=[]
    for i,(name,source,seconds) in enumerate(cases,1):
        structure=check_case_structure(source)
        record={"scenario":name,"actual_ac_opf_call":i,
            "source":structure,"solver_success":False,
            "solver_error":"","elapsed_seconds":None,
            "physical_validation":None,"posthoc_validator_error":""}
        start=time.monotonic()
        try:
            copied={k:(v.copy() if isinstance(v,np.ndarray) else v)
                    for k,v in source.items()}
            result=timed_runopf(copied,opts,seconds)
            record["solver_success"]=bool(result.get("success",False))
            if record["solver_success"]:
                try:
                    record["physical_validation"]=inspect_opf_result(result,source)
                except Exception as e:
                    record["posthoc_validator_error"]=(type(e).__name__+": "+str(e))[:450]
            else:
                record["solver_error"]="PYPOWER returned success=False"
        except Exception as exc:
            record["solver_error"]=(type(exc).__name__+": "+str(exc))[:450]
        record["elapsed_seconds"]=round(time.monotonic()-start,5)
        records.append(record)
        print("I16_AC_OPF",json.dumps(record,sort_keys=True,allow_nan=False),flush=True)
    return {"metadata":{"protocol":"research/ITERATION16_PROTOCOL.md",
         "real_native_ac_opf_calls":len(records),
         "target":"two original public IEEE test cases, NOT original RTE1888",
         "algorithm":"PYPOWER native PIPS AC OPF 560",
         "source":"PYPOWER 5.1.19 case14 and case118",
         "source_data_changed":False,
         "gadapt_algorithm_evaluated":False,
         "python":platform.python_version(),
         "scipy":scipy.__version__,"pandas":pd.__version__,
         "limits":"per-generator PG QG, bus VM, both terminal MVA RATE_A and complex KCL",
        },"runs":records}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",default="iteration16_ieee_opf.json")
    p.add_argument("--csv",default="iteration16_ieee_opf.csv")
    a=p.parse_args()
    result=diagnostic()
    with open(a.json,"w",encoding="utf-8") as f:
        json.dump(result,f,sort_keys=True,indent=2,allow_nan=False)
    with open(a.csv,"w",encoding="utf-8",newline="") as f:
        keys=("scenario","actual_ac_opf_call","solver_success","solver_error",
          "elapsed_seconds","independently_verified_ac_opf",
          "posthoc_validator_error","generator_P_above_mw","generator_P_below_mw",
          "generator_Q_above_mvar","generator_Q_below_mvar",
          "voltage_above_pu","voltage_below_pu",
          "maximum_branch_rate_a_mva_excess","maximum_nodal_mismatch_mva",
          "original_polynomial_cost","losses_mw_not_objective")
        w=csv.DictWriter(f,fieldnames=keys)
        w.writeheader()
        for row in result["runs"]:
            m=row["physical_validation"]
            w.writerow({
             "scenario":row["scenario"],
             "actual_ac_opf_call":row["actual_ac_opf_call"],
             "solver_success":row["solver_success"],
             "solver_error":row["solver_error"],
             "elapsed_seconds":row["elapsed_seconds"],
             "independently_verified_ac_opf":m["independently_verified_ac_opf"] if m else "",
             "posthoc_validator_error":row["posthoc_validator_error"],
             "generator_P_above_mw":m["individual_generator_p_bounds_mw"]["above_limit_total"] if m else "",
             "generator_P_below_mw":m["individual_generator_p_bounds_mw"]["below_limit_total"] if m else "",
             "generator_Q_above_mvar":m["individual_generator_q_bounds_mvar"]["above_limit_total"] if m else "",
             "generator_Q_below_mvar":m["individual_generator_q_bounds_mvar"]["below_limit_total"] if m else "",
             "voltage_above_pu":m["bus_voltage_bounds_pu"]["above_limit_total"] if m else "",
             "voltage_below_pu":m["bus_voltage_bounds_pu"]["below_limit_total"] if m else "",
             "maximum_branch_rate_a_mva_excess":m["max_original_rate_a_terminal_mva_excess"] if m else "",
             "maximum_nodal_mismatch_mva":m["AC_nodal_balance"]["max_bus_nodal_mismatch_mva"] if m else "",
             "original_polynomial_cost":m["original_source_economic_cost"]["objective_native_reported"] if m else "",
             "losses_mw_not_objective":m["sum_branch_real_losses_MW_not_optimization_objective"] if m else "",
            })
    print("I16_SUMMARY",json.dumps(result["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
