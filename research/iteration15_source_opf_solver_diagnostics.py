"""Iteration 15 preregistered second native AC-OPF algorithm on original RTE1888.

PIPS step-controlled OPF_ALG=565. Includes case9 control. Record raw solver
termination diagnostics even if no numerical/physical solution. Never
promote a failed iteration into feasible results.
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
from pypower.case9 import case9
from pypower.ppoption import ppoption

from research.iteration14_original_acopf import (
    source_opf_data,audit_success,timed_runopf
)


def finite_or_null(value):
    if value is None:
        return None
    try:
        x=float(value)
    except (TypeError,ValueError,OverflowError):
        return None
    return x if math.isfinite(x) else None


def safe_raw_termination(solved):
    raw=solved.get("raw",{})
    if not isinstance(raw,dict):
        return {"raw_info":None,"message":"No structured raw output",
                "iterations":None,"first":None,"last":None}
    output=raw.get("output",{})
    if not isinstance(output,dict):
        output={}
    hist=output.get("hist",[])
    if not isinstance(hist,(list,tuple)):
        hist=[]
    def summarize(z):
        if not isinstance(z,dict):
            return None
        return {k:finite_or_null(z.get(k)) for k in
                ("feascond","gradcond","compcond","costcond")}
    code=finite_or_null(raw.get("info"))
    iterations=finite_or_null(output.get("iterations"))
    return {"raw_info":code,
            "message":str(output.get("message",""))[:200],
            "iterations":int(iterations) if iterations is not None else None,
            "first":summarize(hist[0]) if hist else None,
            "last":summarize(hist[-1]) if hist else None}


def diagnostic():
    source=source_opf_data()
    c9=case9()
    cases=[("control_case9_opf_565",c9,120),
           ("original_rte1888_opf_565",source,780)]
    opts=ppoption(OPF_ALG=565,PF_DC=0,OPF_FLOW_LIM=0,
                  OPF_IGNORE_ANG_LIM=False,OPF_VIOLATION=5e-6,
                  PDIPM_MAX_IT=100,VERBOSE=0,OUT_ALL=0)
    runs=[]
    success_small=False
    physical_calls=0
    for label,raw,limit in cases:
        if label.startswith("original") and not success_small:
            runs.append({"scenario":label,"attempted":False,
              "actual_ac_opf_call":None,"solver_success":False,
              "solver_error":"Skipped because case9 step-controlled smoke failed",
              "elapsed_seconds":None,"solver_diagnostics":None,
              "posthoc_validated":False,"validator_error":"",
              "posthoc":None})
            continue
        physical_calls+=1
        row={"scenario":label,"attempted":True,
             "actual_ac_opf_call":physical_calls,
             "solver_success":False,"solver_error":"",
             "elapsed_seconds":None,"solver_diagnostics":None,
             "posthoc_validated":False,"validator_error":"",
             "posthoc":None}
        begin=time.monotonic()
        try:
            copied={k:(v.copy() if isinstance(v,np.ndarray) else v)
                    for k,v in raw.items()}
            result=timed_runopf(copied,opts,limit)
            row["solver_success"]=bool(result.get("success",False))
            row["solver_diagnostics"]=safe_raw_termination(result)
            if not row["solver_success"]:
                row["solver_error"]="PYPOWER reported success=False"
            elif label.startswith("control"):
                if "f" not in result or finite_or_null(result["f"]) is None:
                    raise ValueError("Successful case9 has no finite reported cost")
                success_small=True
                row["control_cost_only"]=float(result["f"])
            else:
                try:
                    row["posthoc"]=audit_success(result,source)
                    row["posthoc_validated"]=bool(row["posthoc"]["all_posthoc_checks_pass"])
                except Exception as err:
                    row["validator_error"]=(type(err).__name__+": "+str(err))[:400]
        except Exception as exc:
            row["solver_error"]=(type(exc).__name__+": "+str(exc))[:450]
        row["elapsed_seconds"]=round(time.monotonic()-begin,5)
        runs.append(row)
        print("I15_AC_OPF",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    return {"metadata":{
       "protocol":"research/ITERATION15_PROTOCOL.md",
       "source_matpower_commit":"80b6e16f760f58721ad31221c7287c28259cd4ad",
       "source_slack_bus_id":1320,
       "native_solver":"PYPOWER 5.1.19 runopf OPF_ALG=565 step-controlled PIPS",
       "total_actual_ac_opf_calls":physical_calls,
       "maximum_allowed_ac_opf_calls":2,
       "unmodified_MATPOWER_original_source":True,
       "original_line_cost_not_loss_MW":True,
       "gadapt_algorithm_touched":False,
       "environment":{"python":platform.python_version(),
                      "scipy":scipy.__version__,"pandas":pd.__version__},
       "research_only_not_usable_for_real_french_eu_grid":True,
       },"runs":runs}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default="iteration15_opf_diagnostic.json")
    parser.add_argument("--csv",default="iteration15_opf_diagnostic.csv")
    args=parser.parse_args()
    result=diagnostic()
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(result,f,sort_keys=True,indent=2,allow_nan=False)
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        cols=["scenario","attempted","actual_ac_opf_call","solver_success",
              "solver_error","elapsed_seconds","raw_info","solver_message",
              "iteration_count","start_feascond","last_feascond",
              "last_gradcond","last_compcond","posthoc_validated",
              "validator_error","source_economic_cost","max_nodal_mismatch_mva"]
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader()
        for row in result["runs"]:
            diag=row.get("solver_diagnostics") or {}
            last=diag.get("last") or {}
            first=diag.get("first") or {}
            audit=row.get("posthoc") or {}
            w.writerow({"scenario":row["scenario"],"attempted":row["attempted"],
                "actual_ac_opf_call":row["actual_ac_opf_call"],
                "solver_success":row["solver_success"],
                "solver_error":row["solver_error"],
                "elapsed_seconds":row["elapsed_seconds"],
                "raw_info":diag.get("raw_info"),
                "solver_message":diag.get("message"),
                "iteration_count":diag.get("iterations"),
                "start_feascond":first.get("feascond"),
                "last_feascond":last.get("feascond"),
                "last_gradcond":last.get("gradcond"),
                "last_compcond":last.get("compcond"),
                "posthoc_validated":row["posthoc_validated"],
                "validator_error":row["validator_error"],
                "source_economic_cost":(
                    audit.get("posthoc_economic_objective") or {}).get("objective_native_reported"),
                "max_nodal_mismatch_mva":(
                    audit.get("posthoc_nodal_balance") or {}).get("max_bus_nodal_mismatch_mva"),
            })
    print("I15_SUMMARY",json.dumps(result["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
