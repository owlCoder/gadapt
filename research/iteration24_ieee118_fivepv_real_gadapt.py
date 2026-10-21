"""Iteration 24: actual unchanged legacy GAdapt vs DE/random/bounded Powell.

Fixed identical five ORIGINAL IEEE118 generator VG decision variables.
All 54 source PG fixed except physical slack output; all Q/P/V/RATE_A and
complex nodal power balance are checked by actual PYPOWER AC PF.
The calibration box is informed by old I19-I23 source AC measurements,
therefore these are explicitly *in-sample calibration* experiments.
No new GAdapt operator, and no free physical feasibility lookups.
"""
import argparse
import csv
import json
import math
import platform
import random
import statistics
import time

import numpy as np
import pandas as pd
import scipy
from pypower.idx_bus import VMIN, VMAX
from pypower.idx_gen import GEN_BUS, PG, VG
from pypower.runpf import runpf
from scipy.optimize import minimize

from research.iteration18_ieee118_gadapt_transfer import IEEE118NineControlSubset, physics_118
from research.iteration17_ieee14_gadapt_economic_pf import (
    PhysicalBudgetRecorder, FAILED_SCORE, run_method
)

HISTORY="research/results/ieee118_iteration23_qbracket_4_real_ac_20261021.json"
METHODS=("gadapt_legacy","scipy_de","random_search","bounded_powell")
SEEDS=(2026,2027,2028)
BUDGET=96
POPULATION=16
CONTROL_BUS_TO_SOURCE_GEN=((103,45),(32,14),(34,15),(92,42),(19,8))
CONTROL_HALF_WIDTH_PU=.005


def calibrated_source_center(history=HISTORY):
    with open(history,encoding="utf-8") as f:
        old=json.load(f)
    if (old["metadata"]["actual_native_ac_pf_calls"]!=4 or
        len(old["states"])!=4 or
        [float(x["alpha"]) for x in old["states"]] != [.6,.7,.8,.9] or
        not all(x["solver_converged"] for x in old["states"]) or
        [x["all_checked_original_constraints_feasible"] for x in old["states"]] !=
          [False,True,True,False]):
        raise ValueError("Post-discovery source feasibility history is not authentic")
    vals=old["metadata"]["previous_source_vg_repair_deltas"]
    if set(vals)!={"34","92","19"}:
        raise ValueError("I23 source Q repair control IDs changed")
    d={int(k):float(v) for k,v in vals.items()}
    for bus,step in d.items():
        if not math.isfinite(step) or not 0<step<=.008:
            raise ValueError("Invalid source sensitivity VG step")
    grid=IEEE118NineControlSubset()
    g=grid.source["gen"]
    center=np.array([
        .99,.973,
        float(g[15,VG])+.75*d[34],
        float(g[42,VG])+.75*d[92],
        float(g[8,VG])+.75*d[19],
    ])
    if not np.all(np.isfinite(center)):
        raise ValueError("Invalid informed local source PV center")
    buses=grid.source["bus"]
    bounds=[]
    for (bus,genid),value in zip(CONTROL_BUS_TO_SOURCE_GEN,center):
        if int(g[genid,GEN_BUS])!=bus:
            raise ValueError("IEEE118 generator identity changed")
        rows=buses[buses[:,0]==bus]
        if len(rows)!=1 or int(rows[0,1])!=2:
            raise ValueError("Source controls require actual PV buses")
        lo=max(float(rows[0,VMIN]),float(value-CONTROL_HALF_WIDTH_PU))
        hi=min(float(rows[0,VMAX]),float(value+CONTROL_HALF_WIDTH_PU))
        if not math.isfinite(lo) or not math.isfinite(hi) or not lo<value<hi:
            raise ValueError("Missing original V bounds for calibrated common search box")
        bounds.append((lo,hi))
    return center,bounds


class IEEE118FiveRelevantPV:
    def __init__(self, history=HISTORY):
        self.reference=IEEE118NineControlSubset()
        self.source=self.reference.source
        self.center,self.bounds=calibrated_source_center(history)
        self.n=5
        self.real_ac_calls=0

    def evaluate(self, candidate):
        x=np.asarray(candidate,dtype=float)
        if x.shape!=(self.n,) or not np.all(np.isfinite(x)):
            raise ValueError("Bad physical five PV controls")
        if any(val<low-1e-8 or val>high+1e-8
               for val,(low,high) in zip(x,self.bounds)):
            raise ValueError("IEEE118 source PV outside common local bounds")
        source=self.source
        case={key:(v.copy() if isinstance(v,np.ndarray) else v)
              for key,v in source.items()}
        for (_,genid),voltage in zip(CONTROL_BUS_TO_SOURCE_GEN,x):
            case["gen"][genid,VG]=float(voltage)
        if not np.array_equal(case["gen"][:,PG],source["gen"][:,PG]):
            raise ValueError("Unregistered original PG redispatch")
        mask=np.ones(len(case["gen"]),dtype=bool)
        mask[[k for _,k in CONTROL_BUS_TO_SOURCE_GEN]]=False
        if not np.array_equal(case["gen"][mask,VG],source["gen"][mask,VG]):
            raise ValueError("Unregistered change of other 49 original PV setpoints")
        try:
            self.real_ac_calls+=1  # Native physical solver boundary, even exception.
            solved,success=runpf(case,self.reference.settings)
            if not success:
                return {"converged":False,"feasible":False,
                        "solver_error":"PYPOWER original IEEE118 runpf returned success=False",
                        "penalized_objective":FAILED_SCORE,
                        "actual_economic_cost":None}
            out=physics_118(solved,source)
            out["solver_error"]=""
            return out
        except Exception as exc:
            return {"converged":False,"feasible":False,
                    "solver_error":(type(exc).__name__+": "+str(exc))[:250],
                    "penalized_objective":FAILED_SCORE,
                    "actual_economic_cost":None}


def powell_once(system,seed,budget=BUDGET):
    """Bounded derivative-free local solver, its deterministic centered start is declared."""
    random.seed(seed)
    np.random.seed(seed)
    tracker=PhysicalBudgetRecorder(system,budget)
    start=time.monotonic()
    success=True
    reason=""
    result=None
    try:
        result=minimize(tracker,system.center.copy(),method="Powell",
            bounds=system.bounds,
            options={"maxfev":int(budget),"xtol":1e-5,
                     "ftol":1e-7,"disp":False})
        success=bool(result.success)
        if not success:
            reason=str(result.message)[:250]
    except Exception as error:
        success=False
        reason=(type(error).__name__+": "+str(error))[:250]
    return {
        "case":"IEEE118_original_fixed_PG_five_relevant_PV_local_calibrated_in_sample",
        "method":"bounded_powell","seed":int(seed),
        "dimension":5,"budget_actual_ac_pf":int(budget),
        "optimizer_reported_success":success,
        "optimizer_error":reason,
        "runtime_seconds":round(time.monotonic()-start,5),
        "optimizer_reported_nfev":int(result.nfev) if result is not None else None,
        "centered_initialization_informed_by_prior_I23":True,
        "operator_selections":0,
        **tracker.summary(),
    }


def benchmark(seeds=SEEDS,budget=BUDGET,population=POPULATION):
    if not seeds or budget<population or population<8 or budget>500:
        raise ValueError("Invalid physical AC budget or GA population")
    rows=[]
    center,bounds=calibrated_source_center()
    for seed in seeds:
        for method in METHODS:
            system=IEEE118FiveRelevantPV()
            if method=="bounded_powell":
                record=powell_once(system,seed,budget)
            else:
                record=run_method(system,method,seed,budget,population)
                record["case"]="IEEE118_original_fixed_PG_five_relevant_PV_local_calibrated_in_sample"
                record["centered_initialization_informed_by_prior_I23"]=False
                record["optimizer_reported_nfev"]=None
            if record["real_ac_pf_calls"] != system.real_ac_calls:
                raise RuntimeError("Objective tracked physical AC counts disagree with solver boundary")
            if record["real_ac_pf_calls"]>budget:
                raise RuntimeError("Preregistered real AC budget exceeded")
            rows.append(record)
            print("I24_REAL_GADAPT",json.dumps(record,sort_keys=True,allow_nan=False),flush=True)
    summary={}
    for method in METHODS:
        selected=[r for r in rows if r["method"]==method]
        actual=[r["best_feasible_economic_cost"] for r in selected
                if r["best_feasible_economic_cost"] is not None]
        summary[method]={
           "runs":len(selected),
           "runs_with_physical_feasible":len(actual),
           "total_native_ac_pf_calls":sum(r["real_ac_pf_calls"] for r in selected),
           "total_converged_physical_candidates":sum(
              r["real_ac_pf_calls"]-r["solver_failed_calls"] for r in selected),
           "total_source_feasible_candidates":sum(r["feasible_real_ac_candidates"] for r in selected),
           "median_feasible_cost_conditional_on_success_only":(
              statistics.median(actual) if actual else None),
           "best_source_feasible_cost_or_null":min(actual) if actual else None,
           "median_actual_ac_calls_per_run":statistics.median(r["real_ac_pf_calls"] for r in selected),
           "deterministic_powell_triplicate_not_independent_seeds":method=="bounded_powell",
        }
    return {"metadata":{
         "protocol":"research/ITERATION24_PROTOCOL.md",
         "source_network":"unaltered PYPOWER IEEE118 public test grid",
         "search":"five SOURCE PV setpoints localized around calibrated I23 alpha=.75; in-sample, not validation",
         "original_online_generators_PG_fixed_except_slack_from_AC":True,
         "common_control_buses":[bus for bus,_ in CONTROL_BUS_TO_SOURCE_GEN],
         "common_source_gen_rows_1based":[i+1 for _,i in CONTROL_BUS_TO_SOURCE_GEN],
         "common_center_pu":list(map(float,center)),
         "common_bounds_pu":bounds,
         "center_bracketing_reference_from_previous_real_AC":True,
         "previous_feasible_I23_cost_only_historical_not_free_optimizer_call":131198.7975746236,
         "previous_full_source_AC_OPF_I16_cost_different_model_space":129660.68639034468,
         "methods":list(METHODS),"seeds":list(seeds),
         "budget_real_AC_per_method_seed":budget,
         "upper_bound_new_true_AC":budget*len(METHODS)*len(seeds),
         "true_AC_PF_calls":sum(r["real_ac_pf_calls"] for r in rows),
         "new_original_AC_OPF_calls":0,
         "no_new_gadapt_operator_tested":True,
         "environment":{"python":platform.python_version(),
                        "scipy":scipy.__version__,
                        "pandas":pd.__version__},
         "public_case_not_real_operational_infrastructure":True,
    },"runs":rows,"summary":summary}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",default="iteration24_gadapt_fivePV.json")
    p.add_argument("--csv",default="iteration24_gadapt_fivePV.csv")
    p.add_argument("--seeds",type=int,nargs="+",default=list(SEEDS))
    p.add_argument("--budget",type=int,default=BUDGET)
    p.add_argument("--population",type=int,default=POPULATION)
    args=p.parse_args()
    results=benchmark(tuple(args.seeds),args.budget,args.population)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(results,f,sort_keys=True,indent=2,allow_nan=False)
    fields=list(results["runs"][0])
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        for row in results["runs"]:
            writer.writerow({k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v)
                              for k,v in row.items()})
    print("I24_COMPARISON",json.dumps(results["summary"],sort_keys=True),flush=True)
    print("I24_METADATA",json.dumps(results["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
