"""Iteration 14 preregistered native AC-OPF reference on ORIGINAL MATPOWER RTE1888.

No source rating fabrication, no pandapower conversion, no GAdapt optimization.
Economic-dispatch objective uses exactly original 2019 MATPOWER gencost.
Small PYPOWER case9 smoke, then at most one original 1888 native AC-OPF.
"""
import argparse
import csv
import json
import math
import platform
import signal
import time

import numpy as np
import pandas as pd
import scipy
from pypower.case9 import case9
from pypower.ext2int import ext2int
from pypower.makeSbus import makeSbus
from pypower.makeYbus import makeYbus
from pypower.ppoption import ppoption
from pypower.runopf import runopf

from research.iteration11_original_matpower_native_pf import (
    load_original, numeric_csv, inspect_successful_pf
)

GENCOST_SOURCE = "research/results/rte1888_iteration14_original_matpower_gencost_full7_2019.csv"
COST_COLUMNS=("model","startup","shutdown","ncost","c2","c1","c0")
CONSTRAINT_TOL={
    "nodal_mismatch_mva":1e-3,"bus_voltage_pu":1e-5,
    "generator_p_mw":1e-3,"generator_q_mvar":1e-3,
    "rated_branch_terminal_mva":1e-3,
}
EQUALITY_COST_TOL_ABS=1e-3


def source_opf_data():
    result=load_original()
    gencost=numeric_csv(GENCOST_SOURCE,COST_COLUMNS,298)
    if gencost.shape!=(298,7):
        raise ValueError("Source generator costs shape mismatch")
    if not (np.all(gencost[:,0]==2) and np.all(gencost[:,3]==3)
            and np.all(gencost[:,4]==0) and np.all(gencost[:,6]==0)):
        raise ValueError("MATPOWER cost is not exactly linear polynomial")
    if set(gencost[:,5].tolist())!={1.,2.,10.}:
        raise ValueError("Source original linear cost coefficient provenance changed")
    if not np.all(result["gen"][:,7]==np.round(result["gen"][:,7])):
        raise ValueError("Source online generator flags not discrete")
    if len(result["gen"])!=len(gencost):
        raise ValueError("Generator costs not aligned to source gen")
    if not np.all(result["branch"][:,11:13]==0):
        raise ValueError("Original branch angle limits must be all zero")
    result["gencost"]=gencost
    return result


def native_ac_mismatch(Ybus,V,Sbus,baseMVA):
    """Compute |V conj(Ybus V) - Sbus| in MVA; finite inputs required."""
    observed=np.asarray(V)*np.conj(Ybus@np.asarray(V))
    expected=np.asarray(Sbus)
    if observed.shape!=expected.shape or observed.ndim!=1:
        raise ValueError("Bad AC power-balance dimensions")
    errors=np.abs(observed-expected)*float(baseMVA)
    if not np.all(np.isfinite(errors)):
        raise ValueError("Nonfinite nodal AC KCL results")
    return {"max_bus_nodal_mismatch_mva":float(np.max(errors,initial=0.)),
            "total_bus_nodal_mismatch_mva":float(np.sum(errors)),
            "buses_nodal_mismatch_over_1e_3_mva":
                int(np.count_nonzero(errors>CONSTRAINT_TOL["nodal_mismatch_mva"]))}


def original_source_ac_residual(result):
    """Independent *residual calculation*, using PYPOWER's network admittance.
    This is NOT a second independently developed solver.
    """
    internal=ext2int({
        "version":result.get("version","2"),
        "baseMVA":float(result["baseMVA"]),
        "bus":np.asarray(result["bus"],float).copy(),
        "gen":np.asarray(result["gen"],float).copy(),
        "branch":np.asarray(result["branch"],float).copy(),
        "gencost":np.asarray(result["gencost"],float).copy(),
    })
    ybus,_,_=makeYbus(internal["baseMVA"],internal["bus"],internal["branch"])
    b=internal["bus"]
    v=b[:,7]*np.exp(1j*np.deg2rad(b[:,8]))
    sbus=makeSbus(internal["baseMVA"],b,internal["gen"])
    return native_ac_mismatch(ybus,v,sbus,internal["baseMVA"])


def original_cost(result,source):
    gencost=source["gencost"]
    actual_gens=np.asarray(result["gen"],float)
    if len(actual_gens)!=len(gencost) or not np.array_equal(
            actual_gens[:,0].astype(int),source["gen"][:,0].astype(int)):
        raise ValueError("Source PG/gencost row correspondence invalid")
    enabled=source["gen"][:,7]>0
    if not np.array_equal(enabled,actual_gens[:,7]>0):
        raise ValueError("Original generator status changed")
    pg=actual_gens[:,1]
    price=gencost[:,4]*pg**2+gencost[:,5]*pg+gencost[:,6]
    cost=float(np.sum(price[enabled]))
    reported=float(result["f"])
    if not math.isfinite(reported) or not math.isfinite(cost):
        raise ValueError("Nonfinite OPF cost")
    delta=abs(reported-cost)
    return {"objective_native_reported":reported,
            "objective_original_gencost_recomputed":cost,
            "absolute_objective_recomputation_disagreement":delta,
            "original_economic_objective_matches":bool(delta<=max(
                  EQUALITY_COST_TOL_ABS,abs(cost)*1e-7))}


def audit_success(result,source):
    """Accept 'success' as necessary, not sufficient for physical validity."""
    metrics=inspect_successful_pf(result,source)
    kcl=original_source_ac_residual(result)
    costs=original_cost(result,source)
    br=np.asarray(result["branch"],float)
    rated=(br[:,5]>0)&(br[:,10]>0)
    sf=np.hypot(br[:,13],br[:,14])
    st=np.hypot(br[:,15],br[:,16])
    max_thermal_mva=float(np.max(
        np.maximum(np.maximum(sf,st)-br[:,5],0.)[rated],initial=0.))
    bounds_v=metrics["voltage"]
    gen_p=metrics["p_generator_bounds_mw"]
    gen_q=metrics["q_generator_bounds_mvar"]
    checks={
        "max_nodal_mismatch_mva":
             kcl["max_bus_nodal_mismatch_mva"]<=CONSTRAINT_TOL["nodal_mismatch_mva"],
        "bus_voltage":
             max(bounds_v["max_below_limit"],bounds_v["max_above_limit"])<=CONSTRAINT_TOL["bus_voltage_pu"],
        "generator_p":
             max(gen_p["max_below_limit"],gen_p["max_above_limit"])<=CONSTRAINT_TOL["generator_p_mw"],
        "generator_q":
             max(gen_q["max_below_limit"],gen_q["max_above_limit"])<=CONSTRAINT_TOL["generator_q_mvar"],
        "source_branch_terminal_mva":
             max_thermal_mva<=CONSTRAINT_TOL["rated_branch_terminal_mva"],
        "source_cost":
             costs["original_economic_objective_matches"],
        "original_bus_and_gen_source_identities":
             metrics["online_original_generator_count"]==291 and metrics["active_bus_count"]==1888,
    }
    return {"native_pf_constraints":metrics,
            "posthoc_nodal_balance":kcl,
            "posthoc_economic_objective":costs,
            "max_original_thermal_rate_a_mva_excess":max_thermal_mva,
            "independent_checks":checks,
            "all_posthoc_checks_pass":bool(all(checks.values()))}


def _alarm_timeout(_signum,_frame):
    raise TimeoutError("Preregistered solver wall timeout exceeded")


def timed_runopf(case,opts,seconds):
    # Linux GitHub Actions runner; timer enforces finite CPU budget per call.
    previous=signal.signal(signal.SIGALRM,_alarm_timeout)
    signal.alarm(int(seconds))
    try:
        return runopf(case,opts)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM,previous)


def diagnostic():
    original=source_opf_data()
    case9_data=case9()
    cases=(("small_case9_solver_smoke",case9_data,120),
           ("original_2019_case1888rte",original,780))
    opts=ppoption(OPF_ALG=560,PF_DC=0,OPF_FLOW_LIM=0,
                  OPF_IGNORE_ANG_LIM=False,OPF_VIOLATION=5e-6,
                  PDIPM_MAX_IT=100,VERBOSE=0,OUT_ALL=0)
    records=[]
    n_calls=0
    smoke_success=False
    for label,raw,seconds in cases:
        if label.startswith("original") and not smoke_success:
            records.append({"scenario":label,"attempted":False,"call_number":None,
                 "solver_reported_success":False,"solver_error":"Skipped: case9 smoke did not succeed",
                 "elapsed_wall_seconds":None,"posthoc":None})
            continue
        n_calls+=1
        record={"scenario":label,"attempted":True,"call_number":n_calls,
                "solver_reported_success":False,
                "solver_error":"","elapsed_wall_seconds":None,"posthoc":None}
        started=time.monotonic()
        try:
            working={k:(np.asarray(v).copy() if isinstance(v,np.ndarray) else v)
                     for k,v in raw.items()}
            solved=timed_runopf(working,opts,seconds)
            record["solver_reported_success"]=bool(solved.get("success",False))
            if not record["solver_reported_success"]:
                record["solver_error"]="Native PYPOWER runopf reported success=False"
            elif label.startswith("original"):
                record["posthoc"]=audit_success(solved,original)
                record["locally_verified_source_opf"]=record["posthoc"]["all_posthoc_checks_pass"]
            else:
                if "f" not in solved or not math.isfinite(float(solved["f"])):
                    raise ValueError("case9 smoke returned nonfinite economic objective")
                smoke_success=True
                record["small_case9_solver_reported_cost"]=float(solved["f"])
        except Exception as exc:
            record["solver_reported_success"]=False
            record["solver_error"]=(type(exc).__name__+": "+str(exc))[:480]
            record["posthoc"]=None
        record["elapsed_wall_seconds"]=round(time.monotonic()-started,5)
        records.append(record)
        print("I14_AC_OPF",json.dumps(record,sort_keys=True,allow_nan=False),flush=True)
    metadata={"protocol":"research/ITERATION14_PROTOCOL.md",
       "original_source":"MATPOWER/matpower/data/case1888rte.m",
       "source_commit":"80b6e16f760f58721ad31221c7287c28259cd4ad",
       "original_gencost_rows":298,"source_slack_bus_id":1320,
       "opfalgo":560,"opf_flow_limit":"original positive RATE_A apparent MVA",
       "real_ac_opf_calls":n_calls,"max_allowed_ac_opf_calls":2,
       "solver":"native PYPOWER 5.1.19 runopf",
       "python":platform.python_version(),"scipy":scipy.__version__,
       "pandas":pd.__version__,
       "objective":"original MATPOWER linear generator economic cost, NOT MW line losses",
       "source_license":"CC BY 4.0, strictly not for real French/EU operations or planning",
       "no_gadapt_algorithm_comparison":True}
    return {"metadata":metadata,"runs":records}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default="iteration14_source_ac_opf.json")
    parser.add_argument("--csv",default="iteration14_source_ac_opf.csv")
    args=parser.parse_args()
    result=diagnostic()
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        fields=["scenario","attempted","call_number","solver_reported_success",
           "solver_error","elapsed_wall_seconds","independently_verified_source_opf",
           "original_reported_cost","max_kcl_mismatch_mva","voltage_under_pu",
           "generator_p_below_mw","generator_q_below_mvar",
           "positive_rate_a_mva_excess"]
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        for row in result["runs"]:
            m=row["posthoc"]
            metrics=m["native_pf_constraints"] if m else None
            writer.writerow({"scenario":row["scenario"],
                "attempted":row["attempted"],"call_number":row["call_number"],
                "solver_reported_success":row["solver_reported_success"],
                "solver_error":row["solver_error"],
                "elapsed_wall_seconds":row["elapsed_wall_seconds"],
                "independently_verified_source_opf":
                    m["all_posthoc_checks_pass"] if m else "",
                "original_reported_cost":
                    m["posthoc_economic_objective"]["objective_native_reported"] if m else "",
                "max_kcl_mismatch_mva":
                    m["posthoc_nodal_balance"]["max_bus_nodal_mismatch_mva"] if m else "",
                "voltage_under_pu":
                    metrics["voltage"]["below_limit_total"] if m else "",
                "generator_p_below_mw":
                    metrics["p_generator_bounds_mw"]["below_limit_total"] if m else "",
                "generator_q_below_mvar":
                    metrics["q_generator_bounds_mvar"]["below_limit_total"] if m else "",
                "positive_rate_a_mva_excess":
                    metrics["branch_original_rate_a_mva"]["sum_relative_rating_excess"] if m else ""})
    print("I14_SUMMARY",json.dumps(result["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
