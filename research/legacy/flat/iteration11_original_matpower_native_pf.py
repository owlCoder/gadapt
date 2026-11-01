"""Iteration 11: original 2019 MATPOWER RTE1888 directly in native PYPOWER AC NR.

No pandapower conversion; 2 pre-registered genuine AC PF attempts.
The source is MATPOWER CC BY 4.0, commit 80b6e16...; not operational data.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import pypower
from pypower.ppoption import ppoption
from pypower.runpf import runpf
import scipy

from research.iteration9_source_generators import read_sources

BUS_SOURCE="research/results/rte1888_iteration9_original_matpower_bus_rows_2019.csv"
GEN_SOURCE="research/results/rte1888_iteration11_original_matpower_gen_full21_2019.csv"
BRANCH_SOURCE="research/results/rte1888_iteration11_original_matpower_branch_full13_2019.csv"

BUS_COLUMNS=("bus_id","bus_type","pd_mw","qd_mvar","gs_mw","bs_mvar",
             "area","vm_pu","va_deg","base_kv","zone","vmax_pu","vmin_pu")
GEN_COLUMNS=("gen_bus","pg_mw","qg_mvar","qmax_mvar","qmin_mvar","vg_pu",
             "mbase_mva","gen_status","pmax_mw","pmin_mw","pc1","pc2",
             "qc1min","qc1max","qc2min","qc2max","ramp_agc","ramp_10",
             "ramp_30","ramp_q","apf")
BR_COLUMNS=("from_bus","to_bus","br_r_pu","br_x_pu","br_b_pu","rate_a_mva",
            "rate_b_mva","rate_c_mva","tap","shift_deg","br_status",
            "angmin","angmax")


def numeric_csv(filename, fields, n):
    with open(filename,encoding="utf-8",newline="") as f:
        reader=csv.reader(f)
        header=tuple(next(reader))
        if header != tuple(fields):
            raise ValueError("Wrong original source CSV header: "+filename)
        entries=list(reader)
    if len(entries)!=n:
        raise ValueError("Wrong original source row count: "+filename)
    a=np.array([[float(x) for x in r] for r in entries],dtype=float)
    if a.shape!=(n,len(fields)) or not np.all(np.isfinite(a)):
        raise ValueError("Invalid source numeric matrix: "+filename)
    return a


def load_original():
    bus=numeric_csv(BUS_SOURCE,BUS_COLUMNS,1888)
    gen=numeric_csv(GEN_SOURCE,GEN_COLUMNS,298)
    branch=numeric_csv(BRANCH_SOURCE,BR_COLUMNS,2531)
    raw_gen,raw_bus=read_sources()
    if len(raw_gen)!=len(gen) or len(raw_bus)!=len(bus):
        raise ValueError("Source case counts disagree with iteration 9")
    if sorted(int(x) for x in bus[:,0])!=sorted(raw_bus):
        raise ValueError("Source bus IDs differ")
    for i,row in enumerate(gen):
        check=raw_gen[i]
        fields=GEN_COLUMNS[:10]
        for index,field in enumerate(fields):
            # Identical numerical generator values from two independent archives
            key=("source_row_1based" if field=="source_row_1based" else field)
            if abs(row[index]-check[key])>1e-9:
                raise ValueError("Source gen 21 versus 10 columns mismatch")
    if np.count_nonzero(bus[:,1]==3)!=1 or int(bus[bus[:,1]==3,0][0])!=1320:
        raise ValueError("Source slack bus changed")
    if int(gen[-1,0])!=1320 or int(gen[-1,7])!=1 or abs(gen[-1,3]-1.)>1e-9:
        raise ValueError("Missing 2019 source reference generator")
    if np.sum(gen[:,7]==1)!=291 or np.sum(gen[:,7]==0)!=7:
        raise ValueError("Unexpected source generator statuses")
    if np.sum(branch[:,10]==1)!=len(branch):
        raise ValueError("Unexpected offline branches in source")
    if np.sum(branch[:,5]==0)!=455:
        raise ValueError("Source MATPOWER no-rating RATE_A count changed")
    if np.any(gen[:,8]<gen[:,9]) or np.any(gen[:,3]<gen[:,4]):
        raise ValueError("Inverted original generator P/Q ranges")
    return {"version":"2","baseMVA":100.0,"bus":bus,"gen":gen,"branch":branch}


def summed_limit_violation(observed,mins,maxes,active,tol=1e-7):
    v=np.asarray(observed,dtype=float)
    lo=np.asarray(mins,dtype=float)
    hi=np.asarray(maxes,dtype=float)
    act=np.asarray(active,dtype=bool)
    if not all(x.shape==v.shape for x in (lo,hi,act)):
        raise ValueError("Limit vector shape mismatch")
    if np.any(~np.isfinite(v)) or np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)):
        raise ValueError("Nonfinite result or limit")
    if np.any(lo>hi):
        raise ValueError("Invalid limits")
    below=np.where(act,np.maximum(lo-v,0.),0.)
    above=np.where(act,np.maximum(v-hi,0.),0.)
    return {
        "below_limit_count":int(np.count_nonzero(below>tol)),
        "above_limit_count":int(np.count_nonzero(above>tol)),
        "below_limit_total":float(np.sum(below)),
        "above_limit_total":float(np.sum(above)),
        "max_below_limit":float(np.max(below,initial=0.)),
        "max_above_limit":float(np.max(above,initial=0.)),
    }


def original_rate_a_violation(branch, tol=1e-7):
    b=np.asarray(branch,float)
    if b.ndim!=2 or b.shape[1]<17:
        raise ValueError("PF branch result needs flow columns PF/QF/PT/QT")
    if not np.all(np.isfinite(b[:,13:17])):
        raise ValueError("Invalid PF branch flow")
    active=(b[:,10]>0)&(b[:,5]>0)
    observed=np.maximum(np.hypot(b[:,13],b[:,14]),np.hypot(b[:,15],b[:,16]))
    rate=b[:,5]
    ratio=np.zeros(len(rate),float)
    ratio[active]=observed[active]/rate[active]
    violation=np.maximum(ratio-1.,0.)
    return {"rated_active_branches":int(np.count_nonzero(active)),
            "unrated_active_branches":int(np.count_nonzero((b[:,10]>0)&(b[:,5]==0))),
            "overloaded_branches":int(np.count_nonzero(violation>tol)),
            "sum_relative_rating_excess":float(np.sum(violation)),
            "max_source_rate_a_loading_percent":
                float(np.max(ratio,initial=0.)*100.)}


def inspect_successful_pf(result, original):
    bus=np.asarray(result["bus"],dtype=float)
    gen=np.asarray(result["gen"],dtype=float)
    branch=np.asarray(result["branch"],dtype=float)
    if bus.shape[0]!=1888 or gen.shape[0]!=298 or branch.shape[0]!=2531:
        raise ValueError("Solved case changed bus, generator or branch count")
    if not all(np.all(np.isfinite(x)) for x in (bus,gen,branch)):
        raise ValueError("Nonfinite original AC results")
    ids=bus[:,0].astype(int)
    if set(ids)!=set(original["bus"][:,0].astype(int)):
        raise ValueError("Solved original bus identities changed")
    # PYPOWER returns original gen row order after int2ext
    if not np.array_equal(gen[:,0].astype(int),original["gen"][:,0].astype(int)):
        raise ValueError("Solver changed source gen row identities")
    if not np.array_equal(branch[:,:2].astype(int),original["branch"][:,:2].astype(int)):
        raise ValueError("Solver changed branch row identities")
    active=gen[:,7]>0
    voltage=summed_limit_violation(
        bus[:,7],bus[:,12],bus[:,11],bus[:,1]!=4,1e-7)
    p=summed_limit_violation(gen[:,1],original["gen"][:,9],
                             original["gen"][:,8],active)
    q=summed_limit_violation(gen[:,2],original["gen"][:,4],
                             original["gen"][:,3],active)
    thermal=original_rate_a_violation(branch)
    target=np.flatnonzero((gen[:,0]==1320)&active)
    if len(target)!=1:
        raise ValueError("Original slack source generator identity lost")
    index=int(target[0])
    source_slack=original["gen"][index]
    out_slack=gen[index]
    # PP Q enforcing can turn REF into PQ; report final source bus type
    bus1320=int(np.flatnonzero(bus[:,0]==1320)[0])
    active_bus=bus[:,1]!=4
    branch_active=branch[:,10]>0
    p_loss=float(np.sum((branch[:,13]+branch[:,15])[branch_active]))
    residual=float(
        voltage["below_limit_total"]+voltage["above_limit_total"]+
        thermal["sum_relative_rating_excess"]+
        p["below_limit_total"]+p["above_limit_total"]+
        q["below_limit_total"]+q["above_limit_total"])
    return {
        "actual_pq_bus_count":int(np.sum(bus[:,1]==1)),
        "actual_pv_bus_count":int(np.sum(bus[:,1]==2)),
        "actual_ref_bus_count":int(np.sum(bus[:,1]==3)),
        "actual_ref_bus_ids":[int(z) for z in bus[bus[:,1]==3,0]],
        "active_bus_count":int(np.count_nonzero(active_bus)),
        "online_original_generator_count":int(np.count_nonzero(active)),
        "voltage":voltage,
        "p_generator_bounds_mw":p,
        "q_generator_bounds_mvar":q,
        "branch_original_rate_a_mva":thermal,
        "original_source_slack_row_1based":index+1,
        "original_source_slack_bus_id":1320,
        "original_source_slack_final_bus_type":int(bus[bus1320,1]),
        "original_source_slack_pg_mw":float(out_slack[1]),
        "original_source_slack_qg_mvar":float(out_slack[2]),
        "original_source_slack_source_qmax_mvar":float(source_slack[3]),
        "original_source_slack_source_qmin_mvar":float(source_slack[4]),
        "original_source_slack_qmax_excess_mvar":
             float(max(out_slack[2]-source_slack[3],0.)),
        "sum_branch_real_losses_mw_not_feasible_optimum":p_loss,
        "complete_checked_residual_mixed_units_not_opf_objective":residual,
        "all_explicit_checked_constraints_feasible":bool(residual<=1e-7),
    }


def diagnostic():
    original=load_original()
    attempts=[]
    for index,enforce in enumerate((False,True),1):
        details={"scenario":("source_matpower_original_no_q_enforcement"
                       if not enforce else "source_matpower_q_enforcement"),
                 "actual_native_ac_call":index,
                 "enforce_q_lims":enforce,"solver_converged":False,
                 "solver_error":"","metrics":None}
        # Count the attempt even if PYPOWER throws an exception.
        try:
            opts=ppoption(PF_ALG=1, PF_TOL=1e-8, PF_MAX_IT=40,
                ENFORCE_Q_LIMS=int(enforce),PF_DC=0,VERBOSE=0,OUT_ALL=0)
            copied={k:(v.copy() if isinstance(v,np.ndarray) else v)
                    for k,v in original.items()}
            solved,ok=runpf(copied,opts)
            details["solver_converged"]=bool(ok)
            if ok:
                details["metrics"]=inspect_successful_pf(solved,original)
            else:
                details["solver_error"]="PYPOWER reported success=False"
        except Exception as e:
            details["solver_error"]=(type(e).__name__+": "+str(e))[:450]
        attempts.append(details)
        print("I11_NATIVE_AC",json.dumps(details,allow_nan=False,sort_keys=True),
              flush=True)
    return {"metadata":{
        "source":"MATPOWER/matpower/data/case1888rte.m",
        "source_commit":"80b6e16f760f58721ad31221c7287c28259cd4ad",
        "license":"CC BY 4.0; NOT for real French/EU grid operations or planning",
        "actual_native_ac_calls":len(attempts),
        "native_solver":"PYPOWER 5.1.19 runpf (no pandapower conversion)",
        "source_baseMVA":100,
        "source_bus_count":1888,"source_gen_count":298,
        "source_branch_count":2531,
        "source_slack_bus_id":1320,
        "runtime":{"python":platform.python_version(),
                   "scipy":scipy.__version__,"pandas":pd.__version__,
                   "pypower":getattr(pypower,"__version__","not exposed")},
        "scope":"AC power flow diagnostic ONLY; not AC-OPF, no GAdapt comparison",
       }, "attempts":attempts}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",default="iteration11_original_native_ac.json")
    p.add_argument("--csv",default="iteration11_original_native_ac.csv")
    args=p.parse_args()
    data=diagnostic()
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,sort_keys=True,allow_nan=False)
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        fields=("scenario","actual_native_ac_call","enforce_q_lims",
                "solver_converged","solver_error","checked_feasible",
                "voltage_violation","thermal_violation",
                "p_generator_violation_mw","q_generator_violation_mvar",
                "original_slack_q_mvar")
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        for attempt in data["attempts"]:
            m=attempt["metrics"]
            writer.writerow(dict(scenario=attempt["scenario"],
                actual_native_ac_call=attempt["actual_native_ac_call"],
                enforce_q_lims=attempt["enforce_q_lims"],
                solver_converged=attempt["solver_converged"],
                solver_error=attempt["solver_error"],
                checked_feasible=m["all_explicit_checked_constraints_feasible"] if m else "",
                voltage_violation=(m["voltage"]["below_limit_total"]+
                    m["voltage"]["above_limit_total"]) if m else "",
                thermal_violation=m["branch_original_rate_a_mva"]["sum_relative_rating_excess"] if m else "",
                p_generator_violation_mw=(m["p_generator_bounds_mw"]["below_limit_total"]+
                    m["p_generator_bounds_mw"]["above_limit_total"]) if m else "",
                q_generator_violation_mvar=(m["q_generator_bounds_mvar"]["below_limit_total"]+
                    m["q_generator_bounds_mvar"]["above_limit_total"]) if m else "",
                original_slack_q_mvar=m["original_source_slack_qg_mvar"] if m else ""))
    print("I11_SUMMARY",json.dumps(data["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
