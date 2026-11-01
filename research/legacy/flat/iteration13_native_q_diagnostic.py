"""Iteration 13: one genuine original MATPOWER AC Q-enforcement run, versioned patch.

Previously verified no-Q control is archived in iteration12 and not rerun.
See preregistered ITERATION13_PROTOCOL.md. Not an optimizer.
"""
import argparse
import csv
import json
import platform
import traceback

import numpy as np
import pandas as pd
import scipy
from pypower.ppoption import ppoption

from research.iteration11_original_matpower_native_pf import (
    load_original,inspect_successful_pf)
from research.iteration13_local_pypower_qlim_patch import runpf


def diagnostic():
    baseline=load_original()
    row={"scenario":"iteration13_native_original_matpower_q_enforced",
         "actual_native_ac_call":1,
         "enforce_q_lims":True,
         "solver_converged":False,
         "solver_error":"",
         "limited_traceback":"",
         "metrics":None}
    try:
        opts=ppoption(PF_ALG=1,PF_TOL=1e-8,PF_MAX_IT=40,ENFORCE_Q_LIMS=1,
                      PF_DC=0,VERBOSE=0,OUT_ALL=0)
        case={k:(v.copy() if isinstance(v,np.ndarray) else v)
              for k,v in baseline.items()}
        solved,success=runpf(case,opts)
        row["solver_converged"]=bool(success)
        if success:
            row["metrics"]=inspect_successful_pf(solved,baseline)
        else:
            row["solver_error"]="Locally Q-fixed native PYPOWER reported success=False"
    except Exception as e:
        row["solver_error"]=(type(e).__name__+": "+str(e))[:450]
        # Avoid machine-local traces; keep bounded source filenames,
        # function and line numbers ONLY, not filesystem paths.
        frames=traceback.extract_tb(e.__traceback__)
        row["limited_traceback"]=" > ".join(
            (f.filename.rsplit("/",1)[-1]+":"+str(f.lineno)+":"+f.name)
            for f in frames[-8:])[:650]
    print("I13_NATIVE_AC",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    return {"metadata":{
        "source":"MATPOWER 2019 original case1888rte",
        "source_commit":"80b6e16f760f58721ad31221c7287c28259cd4ad",
        "pypower_vendor_commit":"c7f1cf50bedd34012b92fae4f092ec55617546a8",
        "preregistered":"research/ITERATION13_PROTOCOL.md",
        "actual_native_ac_calls":1,
        "upstream_no_q_control_ran_in_iteration11_and12":True,
        "original_slack_bus_id":1320,
        "python":platform.python_version(),
        "scipy":scipy.__version__,
        "pandas":pd.__version__,
        "original_matpower_source_not_for_real_operation":True,
        "full_ac_opf":False,
        "gadapt_algorithm_tested":False,
    },"attempts":[row]}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--csv",default="iteration13_native_q.csv")
    parser.add_argument("--json",default="iteration13_native_q.json")
    args=parser.parse_args()
    result=diagnostic()
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["scenario","actual_native_ac_call","solver_converged",
             "solver_error","limited_traceback","physically_feasible",
             "original_slack_q_mvar","voltage_under_pu",
             "generator_p_below_mw","generator_q_violation_mvar",
             "source_rate_a_violation"])
        w.writeheader()
        x=result["attempts"][0]
        m=x["metrics"]
        w.writerow({
          "scenario":x["scenario"],"actual_native_ac_call":1,
          "solver_converged":x["solver_converged"],
          "solver_error":x["solver_error"],"limited_traceback":x["limited_traceback"],
          "physically_feasible":m["all_explicit_checked_constraints_feasible"] if m else "",
          "original_slack_q_mvar":m["original_source_slack_qg_mvar"] if m else "",
          "voltage_under_pu":m["voltage"]["below_limit_total"] if m else "",
          "generator_p_below_mw":m["p_generator_bounds_mw"]["below_limit_total"] if m else "",
          "generator_q_violation_mvar":(
              m["q_generator_bounds_mvar"]["above_limit_total"]+
              m["q_generator_bounds_mvar"]["below_limit_total"]) if m else "",
          "source_rate_a_violation":
              m["branch_original_rate_a_mva"]["sum_relative_rating_excess"] if m else ""})
    print("I13_SUMMARY",json.dumps(result["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
