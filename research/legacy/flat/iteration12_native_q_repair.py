"""Iteration 12 preregistered local BSD-PYPOWER Q-limit repair A/B diagnostic.

Two actual original MATPOWER AC solves: unpatched-equivalent control and
locally repaired Q-limit enforcement. Not new GAdapt and not full AC-OPF.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import scipy
from pypower.ppoption import ppoption

from research.iteration11_original_matpower_native_pf import (
    load_original, inspect_successful_pf,
)
from research.iteration12_local_pypower_qlim_patch import runpf

PREVIOUS="research/results/rte1888_iteration11_original_native_ac_20261021.json"


def compare_native_control(measured,previous,tol=1e-5):
    if not previous["solver_converged"] or previous["metrics"] is None:
        raise ValueError("Original unpatched control must have converged")
    if not measured["solver_converged"] or measured["metrics"] is None:
        raise ValueError("Patched no-Q control did not converge")
    a=measured["metrics"]
    b=previous["metrics"]
    keys=("original_source_slack_pg_mw","original_source_slack_qg_mvar",
          "sum_branch_real_losses_mw_not_feasible_optimum")
    for key in keys:
        if not math.isfinite(float(a[key])) or abs(a[key]-b[key])>tol:
            raise ValueError("Local runpf patch modified no-Q physics: "+key)
    for section in ("voltage","p_generator_bounds_mw","q_generator_bounds_mvar",
                    "branch_original_rate_a_mva"):
        if set(a[section])!=set(b[section]):
            raise ValueError("Physical diagnostic schema drift: "+section)
        for key in a[section]:
            new,old=a[section][key],b[section][key]
            if not math.isfinite(float(new)) or abs(new-old)>tol:
                raise ValueError("Patched no-Q physical drift: "+section+"."+key)
    return True


def paired_native_source_diagnostic(previous_path=PREVIOUS):
    with open(previous_path,encoding="utf-8") as f:
        previous=json.load(f)
    if previous["metadata"]["actual_native_ac_calls"]!=2:
        raise ValueError("Missing original baseline archive")
    source=load_original()
    rows=[]
    equivalent=False
    for i, enforce in enumerate((False,True),1):
        record={"scenario":("patched_control_without_Q_enforce" if not enforce
                           else "patched_native_source_Q_enforcement"),
                "actual_native_ac_call":i,
                "solver_converged":False,
                "enforce_q_lims":enforce,"solver_error":"","metrics":None,
                "control_verified_against_iteration11":None}
        try:
            options=ppoption(PF_ALG=1,PF_TOL=1e-8,PF_MAX_IT=40,
                  ENFORCE_Q_LIMS=int(enforce),PF_DC=0,VERBOSE=0,OUT_ALL=0)
            ppc={k:(v.copy() if isinstance(v,np.ndarray) else v)
                 for k,v in source.items()}
            out,success=runpf(ppc,options)
            record["solver_converged"]=bool(success)
            if success:
                record["metrics"]=inspect_successful_pf(out,source)
            else:
                record["solver_error"]="Local Q-fixed PYPOWER reported success=False"
        except Exception as error:
            record["solver_error"]=(type(error).__name__+": "+str(error))[:450]
        if i==1:
            try:
                equivalent=compare_native_control(record,previous["attempts"][0])
                record["control_verified_against_iteration11"]=True
            except Exception as e:
                record["control_verified_against_iteration11"]=False
                record["control_verification_error"]=str(e)
                rows.append(record)
                print("I12_AC",json.dumps(record,sort_keys=True,allow_nan=False),flush=True)
                break
        rows.append(record)
        print("I12_AC",json.dumps(record,sort_keys=True,allow_nan=False),flush=True)
    result={"metadata":{
       "status":("two_native_AC_attempts_completed" if equivalent and len(rows)==2
                 else "control_failed_no_second_call"),
       "actual_native_ac_calls":len(rows),
       "patched_control_matches_unmodified_baseline":equivalent,
       "native_solver":"PYPOWER 5.1.19 + locally vendored BSD runpf Q-index repair",
       "vendor_source_sha":"c7f1cf50bedd34012b92fae4f092ec55617546a8",
       "original_matpower_source_sha":"80b6e16f760f58721ad31221c7287c28259cd4ad",
       "license":"original MATPOWER CC BY 4.0, PYPOWER BSD",
       "source_slack_bus_id":1320,
       "python":platform.python_version(),
       "scipy":scipy.__version__,
       "pandas":pd.__version__,
       "full_ac_opf":False,
       "gadapt_algorithm_tested":False,
    },"attempts":rows}
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",default="iteration12_native_Q_patch.json")
    p.add_argument("--csv",default="iteration12_native_Q_patch.csv")
    args=p.parse_args()
    result=paired_native_source_diagnostic()
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=[
            "scenario","actual_native_ac_call","enforce_q_lims",
            "solver_converged","solver_error","control_verified_against_iteration11",
            "original_slack_bus_final_type","original_slack_q_mvar",
            "all_explicit_checked_constraints_feasible","v_under_pu",
            "v_over_pu","generator_p_below_mw","generator_q_below_mvar",
            "generator_q_above_mvar","source_rate_a_sum_excess"])
        writer.writeheader()
        for row in result["attempts"]:
            m=row["metrics"]
            writer.writerow({
                "scenario":row["scenario"],
                "actual_native_ac_call":row["actual_native_ac_call"],
                "enforce_q_lims":row["enforce_q_lims"],
                "solver_converged":row["solver_converged"],
                "solver_error":row["solver_error"],
                "control_verified_against_iteration11":
                     row["control_verified_against_iteration11"],
                "original_slack_bus_final_type":
                     m["original_source_slack_final_bus_type"] if m else "",
                "original_slack_q_mvar":
                     m["original_source_slack_qg_mvar"] if m else "",
                "all_explicit_checked_constraints_feasible":
                     m["all_explicit_checked_constraints_feasible"] if m else "",
                "v_under_pu":m["voltage"]["below_limit_total"] if m else "",
                "v_over_pu":m["voltage"]["above_limit_total"] if m else "",
                "generator_p_below_mw":m["p_generator_bounds_mw"]["below_limit_total"] if m else "",
                "generator_q_below_mvar":m["q_generator_bounds_mvar"]["below_limit_total"] if m else "",
                "generator_q_above_mvar":m["q_generator_bounds_mvar"]["above_limit_total"] if m else "",
                "source_rate_a_sum_excess":
                     m["branch_original_rate_a_mva"]["sum_relative_rating_excess"] if m else ""})
    print("I12_SUMMARY",json.dumps(result["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
