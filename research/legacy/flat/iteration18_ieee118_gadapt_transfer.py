"""Iteration 18: controlled transfer of real IEEE14 GAdapt AC-PF methodology to IEEE118.

Same original-P/Q/V/RATE_A/KCL feasibility and original source-economic cost;
same 9-dimensional controls and 3 paired seeds x 3 methods x 96 real AC
budget. This freezes 49 other IEEE118 generator PG/VG values, hence is NOT
an unrestricted 54-generator nonlinear AC-OPF.
"""
import argparse
import csv
import json
import math
import platform
import statistics

import numpy as np
import pandas as pd
import scipy
from pypower.case118 import case118
from pypower.idx_bus import VM, VMIN, VMAX
from pypower.idx_gen import GEN_BUS, GEN_STATUS, PG, PMAX, PMIN, QG, QMAX, QMIN, VG
from pypower.idx_brch import BR_STATUS, RATE_A, PF, QF, PT, QT
from pypower.ppoption import ppoption
from pypower.runpf import runpf

from research.iteration11_original_matpower_native_pf import summed_limit_violation
from research.iteration14_original_acopf import original_source_ac_residual
from research.iteration17_ieee14_gadapt_economic_pf import (
    run_method,original_economic_cost,METHODS,SEEDS,BUDGET,POPULATION,
    PENALTY_SCALE,FAILED_SCORE,TOLS,
)

EXPECTED_SELECTED=(39,36,4,28)
EXPECTED_SLACK=29


def physics_118(solved,source):
    sb=source["bus"];sg=source["gen"];br=source["branch"]
    bus=np.asarray(solved["bus"],float)
    gen=np.asarray(solved["gen"],float)
    branch=np.asarray(solved["branch"],float)
    if bus.shape[0]!=118 or gen.shape[0]!=54 or branch.shape[0]!=186 or branch.shape[1]<17:
        raise ValueError("Wrong output IEEE118 source matrix cardinality")
    if not all(np.all(np.isfinite(x)) for x in (bus,gen,branch)):
        raise ValueError("Nonfinite IEEE118 AC result")
    if (not np.array_equal(bus[:,0].astype(int),sb[:,0].astype(int)) or
        not np.array_equal(gen[:,0].astype(int),sg[:,0].astype(int)) or
        not np.array_equal(branch[:,:2].astype(int),br[:,:2].astype(int)) or
        not np.array_equal(gen[:,GEN_STATUS]>0,sg[:,GEN_STATUS]>0)):
        raise ValueError("Original IEEE118 source row identities/statuses changed")
    online=sg[:,GEN_STATUS]>0
    v=summed_limit_violation(bus[:,VM],sb[:,VMIN],sb[:,VMAX],sb[:,1]!=4)
    p=summed_limit_violation(gen[:,PG],sg[:,PMIN],sg[:,PMAX],online)
    q=summed_limit_violation(gen[:,QG],sg[:,QMIN],sg[:,QMAX],online)
    rated=(br[:,RATE_A]>0)&(br[:,BR_STATUS]>0)
    flow_from=np.hypot(branch[:,PF],branch[:,QF])
    flow_to=np.hypot(branch[:,PT],branch[:,QT])
    thermal=np.zeros(len(branch))
    thermal[rated]=np.maximum(np.maximum(flow_from[rated],flow_to[rated])
                             -br[rated,RATE_A],0.)
    kcl=original_source_ac_residual(solved)
    cost=original_economic_cost(gen[:,PG],online,source["gencost"])
    v_max=max(v["max_below_limit"],v["max_above_limit"])
    p_max=max(p["max_below_limit"],p["max_above_limit"])
    q_max=max(q["max_below_limit"],q["max_above_limit"])
    t_max=float(np.max(thermal,initial=0.))
    k_max=float(kcl["max_bus_nodal_mismatch_mva"])
    feasible=(v_max<=TOLS["voltage_pu"] and
             p_max<=TOLS["generator_p_mw"] and
             q_max<=TOLS["generator_q_mvar"] and
             t_max<=TOLS["thermal_mva"] and
             k_max<=TOLS["ac_nodal_balance_mva"])
    violation=(v["below_limit_total"]+v["above_limit_total"]+
              (p["below_limit_total"]+p["above_limit_total"])/100.+
              (q["below_limit_total"]+q["above_limit_total"])/100.+
              float(thermal.sum())/100.+
              kcl["total_bus_nodal_mismatch_mva"]/100.)
    if not math.isfinite(violation) or violation<0:
        raise ValueError("Invalid violation metric")
    return {
        "converged":True,"feasible":bool(feasible),
        "actual_economic_cost":cost,
        "voltage_sum_excess_pu":float(v["below_limit_total"]+v["above_limit_total"]),
        "p_sum_excess_mw":float(p["below_limit_total"]+p["above_limit_total"]),
        "q_sum_excess_mvar":float(q["below_limit_total"]+q["above_limit_total"]),
        "thermal_sum_excess_mva":float(thermal.sum()),
        "max_voltage_excess_pu":float(v_max),
        "max_generator_p_excess_mw":float(p_max),
        "max_generator_q_excess_mvar":float(q_max),
        "max_branch_terminal_mva_excess":t_max,
        "max_nodal_mismatch_mva":k_max,
        "source_normalized_violation":float(violation),
        "penalized_objective":float(cost+PENALTY_SCALE*violation),
        "original_generators_online":int(online.sum()),
    }


class IEEE118NineControlSubset:
    def __init__(self):
        self.source=case118()
        b=self.source["bus"];g=self.source["gen"]
        if b.shape[0]!=118 or g.shape[0]!=54 or self.source["branch"].shape[0]!=186:
            raise ValueError("Expected exactly original IEEE118 shape")
        ref=[int(k) for k,z in enumerate(g) if b[b[:,0]==z[GEN_BUS],1][0]==3]
        if ref!=[EXPECTED_SLACK] or int(g[EXPECTED_SLACK,GEN_BUS])!=69:
            raise ValueError("Original IEEE118 slack generator changed")
        selectable=[int(k) for k in range(len(g)) if
                    g[k,GEN_STATUS]>0 and k!=EXPECTED_SLACK]
        order=sorted(selectable,key=lambda k:(-g[k,PG],k))
        if tuple(order[:4])!=EXPECTED_SELECTED:
            raise ValueError("Preregistered source high-P IEEE118 gen order changed")
        self.slack_gen_ids=[EXPECTED_SLACK]
        self.non_slack_gen_ids=list(EXPECTED_SELECTED)
        self.all_gen_ids=[EXPECTED_SLACK]+list(EXPECTED_SELECTED)
        buses={int(z[0]):z for z in b}
        self.bounds=[
            (float(g[i,PMIN]),float(g[i,PMAX]))
            for i in self.non_slack_gen_ids]+[
            (float(buses[int(g[i,GEN_BUS])][VMIN]),
             float(buses[int(g[i,GEN_BUS])][VMAX]))
            for i in self.all_gen_ids]
        if len(self.bounds)!=9 or any(hi<=lo for lo,hi in self.bounds):
            raise ValueError("Original IEEE118 source P/V bounds invalid")
        self.n=len(self.bounds)
        self.real_ac_calls=0
        self.settings=ppoption(PF_ALG=1,PF_DC=0,PF_TOL=1e-8,PF_MAX_IT=40,
             ENFORCE_Q_LIMS=0,VERBOSE=0,OUT_ALL=0)

    def evaluate(self,candidate):
        x=np.asarray(candidate,dtype=float)
        if x.shape!=(self.n,) or not np.all(np.isfinite(x)):
            raise ValueError("Need finite original IEEE118 9-dimensional decision vector")
        for value,(lo,hi) in zip(x,self.bounds):
            if value<lo-1e-8 or value>hi+1e-8:
                raise ValueError("Source constrained P/V decision out of bounds")
        case={k:(v.copy() if isinstance(v,np.ndarray) else v)
              for k,v in self.source.items()}
        for idx,val in zip(self.non_slack_gen_ids,x[:4]):
            case["gen"][idx,PG]=float(val)
        for idx,val in zip(self.all_gen_ids,x[4:]):
            case["gen"][idx,VG]=float(val)
        try:
            self.real_ac_calls+=1
            solved,success=runpf(case,self.settings)
            if not success:
                return {"converged":False,"feasible":False,
                        "solver_error":"PYPOWER runpf success=False",
                        "penalized_objective":FAILED_SCORE,
                        "actual_economic_cost":None}
            out=physics_118(solved,self.source)
            out["solver_error"]=""
            return out
        except Exception as err:
            return {"converged":False,"feasible":False,
                    "solver_error":(type(err).__name__+": "+str(err))[:200],
                    "penalized_objective":FAILED_SCORE,
                    "actual_economic_cost":None}


def diagnostic(seeds=SEEDS,budget=BUDGET,population=POPULATION):
    if not seeds or budget<population or population<8:
        raise ValueError("Invalid pre-registered IEEE118 AC search budget")
    rows=[]
    for seed in seeds:
        for method in METHODS:
            row=run_method(IEEE118NineControlSubset(),method,seed,budget,population)
            row["case"]="IEEE118_original_PF_9_controls_49_gen_fixed"
            rows.append(row)
            print("I18_REAL_IEEE118",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    by={}
    for method in METHODS:
        cur=[r for r in rows if r["method"]==method]
        feasible=[r["best_feasible_economic_cost"] for r in cur
                  if r["best_feasible_economic_cost"] is not None]
        by[method]={
           "runs":len(cur),
           "runs_with_physically_feasible":len(feasible),
           "total_real_ac_pf_calls":sum(r["real_ac_pf_calls"] for r in cur),
           "failed_physical_ac_calls":sum(r["solver_failed_calls"] for r in cur),
           "median_only_feasible_economic_cost":statistics.median(feasible) if feasible else None,
        }
    return {"metadata":{
        "protocol":"research/ITERATION18_PROTOCOL.md",
        "original_ieee118_full_source_ac_opf_reference_cost":
            129660.68639034468,
        "not_same_full_original_opf_space":True,
        "controlled_original_pg_gen_indices_zero_based":list(EXPECTED_SELECTED),
        "controlled_original_vg_gen_indices_zero_based":[EXPECTED_SLACK,*EXPECTED_SELECTED],
        "fixed_original_other_gen_p_v_count":49,
        "true_ac_pf_calls":sum(r["real_ac_pf_calls"] for r in rows),
        "ac_opf_calls":0,
        "seeds":list(seeds),
        "budget_true_ac_pf_per_seed_method":budget,
        "gadapt_algorithm_is_original_legacy":True,
        "source_model":"unchanged PYPOWER IEEE118 public reference",
        "python":platform.python_version(),
        "scipy":scipy.__version__,"pandas":pd.__version__,
        "source_is_not_real_utility_field_data":True},
        "runs":rows,"summary":by}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",default="iteration18_ieee118_gadapt.json")
    p.add_argument("--csv",default="iteration18_ieee118_gadapt.csv")
    p.add_argument("--seeds",type=int,nargs="+",default=list(SEEDS))
    p.add_argument("--budget",type=int,default=BUDGET)
    p.add_argument("--population",type=int,default=POPULATION)
    a=p.parse_args()
    record=diagnostic(tuple(a.seeds),a.budget,a.population)
    with open(a.json,"w",encoding="utf-8") as f:
        json.dump(record,f,indent=2,sort_keys=True,allow_nan=False)
    with open(a.csv,"w",encoding="utf-8",newline="") as f:
        entries=[{k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v)
            for k,v in row.items()} for row in record["runs"]]
        out=csv.DictWriter(f,fieldnames=list(entries[0]))
        out.writeheader();out.writerows(entries)
    print("I18_SUMMARY",json.dumps(record["metadata"],sort_keys=True),flush=True)
    print("I18_COMPARISON",json.dumps(record["summary"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
