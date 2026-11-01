"""Iteration 17: actual GAdapt versus DE and random on source IEEE14 AC PF.

Preregistered 9-variable PV-controlled *subset* of economic AC OPF, NOT full
AC-OPF. Every candidate triggers one REAL original PYPOWER Newton-Raphson
runpf, and individually checks source Pg/Qg, V, both-end RATE_A and AC KCL.
No solver failure or budget sentinel can become a feasible incumbent.
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
from gadapt.ga import GA
from pypower.case14 import case14
from pypower.idx_bus import VM, VMIN, VMAX
from pypower.idx_gen import GEN_BUS, GEN_STATUS, PG, PMAX, PMIN, QG, QMAX, QMIN, VG
from pypower.idx_brch import BR_STATUS, RATE_A, PF, QF, PT, QT
from pypower.ppoption import ppoption
from pypower.runpf import runpf
from scipy.optimize import differential_evolution

from research.iteration11_original_matpower_native_pf import summed_limit_violation
from research.iteration14_original_acopf import original_source_ac_residual

METHODS = ("gadapt_legacy", "scipy_de", "random_search")
SEEDS = (2026, 2027, 2028)
BUDGET = 96
POPULATION = 16
PENALTY_SCALE = 1e5
FAILED_SCORE = 1e12
TOLS = {
    "voltage_pu": 1e-5, "generator_p_mw": 1e-3,
    "generator_q_mvar": 1e-3, "thermal_mva": 1e-3,
    "ac_nodal_balance_mva": 1e-3,
}


def original_economic_cost(pg, online, gencost):
    p = np.asarray(pg, dtype=float)
    on = np.asarray(online, dtype=bool)
    c = np.asarray(gencost, dtype=float)
    if p.ndim != 1 or c.shape != (len(p), 7) or on.shape != p.shape:
        raise ValueError("Invalid source cost arrays")
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(c)):
        raise ValueError("Nonfinite source generator cost")
    if not np.all(c[:, 0] == 2) or not np.all(c[:, 3] == 3):
        raise ValueError("Unsupported nonquadratic MATPOWER cost")
    out = np.sum((c[:,4] * p*p + c[:,5]*p + c[:,6])[on])
    if not math.isfinite(float(out)):
        raise ValueError("Nonfinite polynomial economic cost")
    return float(out)


def measured_feasibility(solved, source):
    """Independent physical limit residual from real AC PF arrays, not GA score."""
    sb = source["bus"]; sg = source["gen"]; br = source["branch"]
    b = np.asarray(solved["bus"], float)
    g = np.asarray(solved["gen"], float)
    e = np.asarray(solved["branch"], float)
    if b.shape[0] != 14 or g.shape[0] != 5 or e.shape[0] != 20 or e.shape[1] < 17:
        raise ValueError("AC output shape differs from original IEEE14")
    if not all(np.all(np.isfinite(x)) for x in (b,g,e)):
        raise ValueError("Nonfinite AC output")
    if (not np.array_equal(b[:,0].astype(int),sb[:,0].astype(int)) or
        not np.array_equal(g[:,0].astype(int),sg[:,0].astype(int)) or
        not np.array_equal(e[:,:2].astype(int),br[:,:2].astype(int))):
        raise ValueError("Original bus/gen/branch identity mismatch")
    online = sg[:,GEN_STATUS] > 0
    if not np.array_equal(online, g[:,GEN_STATUS]>0):
        raise ValueError("Generator online status changed")
    voltage = summed_limit_violation(
        b[:,VM], sb[:,VMIN], sb[:,VMAX], sb[:,1]!=4)
    p = summed_limit_violation(g[:,PG], sg[:,PMIN], sg[:,PMAX], online)
    q = summed_limit_violation(g[:,QG], sg[:,QMIN], sg[:,QMAX], online)
    rated = (br[:,RATE_A]>0) & (br[:,BR_STATUS]>0)
    s_from=np.hypot(e[:,PF],e[:,QF])
    s_to=np.hypot(e[:,PT],e[:,QT])
    therm_excess=np.zeros(len(e),dtype=float)
    therm_excess[rated]=np.maximum(np.maximum(s_from[rated],s_to[rated])
                                 - br[rated,RATE_A],0.)
    max_t=float(np.max(therm_excess,initial=0.))
    kcl=original_source_ac_residual(solved)
    actual_cost=original_economic_cost(g[:,PG], online,source["gencost"])
    max_v=max(voltage["max_above_limit"],voltage["max_below_limit"])
    max_p=max(p["max_above_limit"],p["max_below_limit"])
    max_q=max(q["max_above_limit"],q["max_below_limit"])
    max_kcl=kcl["max_bus_nodal_mismatch_mva"]
    all_ok=(max_v<=TOLS["voltage_pu"] and
            max_p<=TOLS["generator_p_mw"] and
            max_q<=TOLS["generator_q_mvar"] and
            max_t<=TOLS["thermal_mva"] and
            max_kcl<=TOLS["ac_nodal_balance_mva"])
    raw_excess=(voltage["below_limit_total"]+voltage["above_limit_total"]+
             (p["below_limit_total"]+p["above_limit_total"])/100.+
             (q["below_limit_total"]+q["above_limit_total"])/100.+
             float(np.sum(therm_excess))/100.+
             kcl["total_bus_nodal_mismatch_mva"]/100.)
    if not math.isfinite(raw_excess) or raw_excess<0:
        raise ValueError("Invalid physics violation")
    return {"converged":True,"feasible":bool(all_ok),
            "actual_economic_cost":actual_cost,
            "voltage_sum_excess_pu":float(voltage["below_limit_total"]+voltage["above_limit_total"]),
            "p_sum_excess_mw":float(p["below_limit_total"]+p["above_limit_total"]),
            "q_sum_excess_mvar":float(q["below_limit_total"]+q["above_limit_total"]),
            "thermal_sum_excess_mva":float(np.sum(therm_excess)),
            "max_voltage_excess_pu":float(max_v),
            "max_generator_p_excess_mw":float(max_p),
            "max_generator_q_excess_mvar":float(max_q),
            "max_branch_terminal_mva_excess":max_t,
            "max_nodal_mismatch_mva":float(max_kcl),
            "source_normalized_violation":float(raw_excess),
            "penalized_objective":actual_cost + PENALTY_SCALE*raw_excess,
            "original_generators_online":int(np.sum(online))}


class IEEE14EconomicPFFeasibleSubset:
    def __init__(self):
        self.source=case14()
        self.s= self.source
        gen=self.s["gen"]
        bus=self.s["bus"]
        online=np.flatnonzero(gen[:,GEN_STATUS]>0)
        slack_buses=set(int(z) for z in bus[bus[:,1]==3,0])
        if len(online)!=5 or len(slack_buses)!=1:
            raise ValueError("Unexpected source IEEE14 generators or slack")
        self.slack_gen_ids=[int(i) for i in online if int(gen[i,GEN_BUS]) in slack_buses]
        if len(self.slack_gen_ids)!=1:
            raise ValueError("Require exactly one original slack generator")
        self.non_slack_gen_ids=[int(i) for i in online if int(i) not in self.slack_gen_ids]
        self.all_gen_ids=[int(i) for i in online]
        bus_lookup={int(row[0]):row for row in bus}
        self.bounds=[
            (float(gen[i,PMIN]),float(gen[i,PMAX]))
            for i in self.non_slack_gen_ids]+[
            (float(bus_lookup[int(gen[i,GEN_BUS])][VMIN]),
             float(bus_lookup[int(gen[i,GEN_BUS])][VMAX]))
            for i in self.all_gen_ids]
        if len(self.bounds)!=9 or any(hi<=lo for lo,hi in self.bounds):
            raise ValueError("IEEE14 source optimizer bounds changed")
        self.n=len(self.bounds)
        self.real_ac_calls=0
        self.settings=ppoption(PF_ALG=1,PF_DC=0,PF_TOL=1e-8,
             PF_MAX_IT=40,ENFORCE_Q_LIMS=0,VERBOSE=0,OUT_ALL=0)

    def evaluate(self, candidate):
        x=np.asarray(candidate,dtype=float)
        if x.shape!=(self.n,) or not np.all(np.isfinite(x)):
            raise ValueError("Candidate outside real finite 9-variable domain")
        for v,(lower,upper) in zip(x,self.bounds):
            if v<lower-1e-8 or v>upper+1e-8:
                raise ValueError("Optimizer proposed an out-of-bounds candidate")
        case={k:(v.copy() if isinstance(v,np.ndarray) else v)
              for k,v in self.source.items()}
        for i,value in zip(self.non_slack_gen_ids,x[:len(self.non_slack_gen_ids)]):
            case["gen"][i,PG]=float(value)
        for i,value in zip(self.all_gen_ids,x[len(self.non_slack_gen_ids):]):
            case["gen"][i,VG]=float(value)
        # This is the one and only physical AC solve per evaluated candidate.
        # Instrument the physical solver boundary, even on an exception.
        try:
            self.real_ac_calls+=1
            solved,success=runpf(case,self.settings)
            if not success:
                return {"converged":False,"feasible":False,"solver_error":
                        "PYPOWER runpf reported success=False",
                        "penalized_objective":FAILED_SCORE,"actual_economic_cost":None}
            result=measured_feasibility(solved,self.source)
            result["solver_error"]=""
            return result
        except Exception as exc:
            return {"converged":False,"feasible":False,
                    "solver_error":(type(exc).__name__+": "+str(exc))[:220],
                    "penalized_objective":FAILED_SCORE,
                    "actual_economic_cost":None}


class PhysicalBudgetRecorder:
    def __init__(self, system,budget):
        self.system=system
        self.budget=int(budget)
        if self.budget<1:
            raise ValueError("Positive actual AC budget required")
        self.requests=0
        self.calls=0
        self.post_budget_requests=0
        self.ac_errors=0
        self.feasible_candidates=0
        self.first_feasible_call=None
        self.best_feasible_cost=math.inf
        self.best_feasible_vector=None
        self.best_feasible_info=None
        self.best_score=math.inf
        self.best_score_vector=None
        self.last_error=""

    def __call__(self,x):
        self.requests+=1
        if self.calls>=self.budget:
            self.post_budget_requests+=1
            return FAILED_SCORE
        values=tuple(float(z) for z in x)
        before=int(self.system.real_ac_calls)
        measured=self.system.evaluate(values)
        physical_delta=int(self.system.real_ac_calls)-before
        if physical_delta != 1:
            raise RuntimeError('Expected exactly one actual runpf attempt for this objective request')
        self.calls+=physical_delta
        score=float(measured["penalized_objective"])
        if not math.isfinite(score):
            raise ValueError("Nonfinite objective from real AC solve")
        if not measured["converged"]:
            self.ac_errors+=1
            self.last_error=measured.get("solver_error","")
        if score<self.best_score:
            self.best_score=score
            self.best_score_vector=values
        if measured["feasible"]:
            self.feasible_candidates+=1
            if self.first_feasible_call is None:
                self.first_feasible_call=self.calls
            cost=float(measured["actual_economic_cost"])
            if not math.isfinite(cost):
                raise ValueError("Feasible candidate without real economic cost")
            if cost<self.best_feasible_cost:
                self.best_feasible_cost=cost
                self.best_feasible_vector=values
                self.best_feasible_info=measured
        return score

    def summary(self):
        return {
          "real_ac_pf_calls":self.calls,
          "objective_requests":self.requests,
          "requests_after_real_ac_budget":self.post_budget_requests,
          "solver_failed_calls":self.ac_errors,
          "feasible_real_ac_candidates":self.feasible_candidates,
          "first_feasible_actual_ac_call":self.first_feasible_call,
          "best_feasible_economic_cost":(
              self.best_feasible_cost if math.isfinite(self.best_feasible_cost) else None),
          "best_feasible_vector":list(self.best_feasible_vector) if self.best_feasible_vector else None,
          "best_feasible_physical_metrics":self.best_feasible_info,
          "best_penalized_ac_score":self.best_score if math.isfinite(self.best_score) else None,
          "best_penalized_vector":list(self.best_score_vector) if self.best_score_vector else None,
          "last_solver_error":self.last_error,
        }


def run_method(system,method,seed,budget=BUDGET,population=POPULATION):
    if method not in METHODS:
        raise ValueError(method)
    random.seed(seed)
    np.random.seed(seed)
    tracker=PhysicalBudgetRecorder(system,budget)
    started=time.monotonic()
    success=True
    reason=""
    operator_credit=[]
    if method=="random_search":
        rng=np.random.default_rng(seed)
        for _ in range(budget):
            x=np.array([rng.uniform(lo,hi) for lo,hi in system.bounds])
            tracker(x)
    elif method=="scipy_de":
        popfactor=max(5,math.ceil(population/system.n))
        try:
            differential_evolution(tracker,system.bounds,
               popsize=popfactor,maxiter=math.ceil(budget/(popfactor*system.n))+2,
               tol=0.,atol=0.,polish=False,seed=seed,updating="immediate")
        except Exception as exc:
            success=False
            reason=(type(exc).__name__+": "+str(exc))[:250]
    else:
        try:
            ga=GA(cost_function=tracker,population_size=population,
              cost_diversity_metric="log_relative",
              exit_check="generations",
              exit_function=lambda:tracker.calls>=budget,
              number_of_generations=math.ceil(4*budget/population)+12,
              population_mutation="cost_diversity,parent_diversity",
              timeout=240)
            for lo,hi in system.bounds:
                ga.add(lo,hi)
            result=ga.execute()
            success=bool(result.success)
            if not success:
                reason=str(getattr(result,"messages",str(result)))[:250]
            operator_credit=getattr(result,"operator_credit_summary",[])
        except Exception as exc:
            success=False
            reason=(type(exc).__name__+": "+str(exc))[:250]
    elapsed=time.monotonic()-started
    return {"case":"IEEE14_original_PF_constrained_economic_subset",
            "method":method,"seed":int(seed),
            "dimension":system.n,"budget_actual_ac_pf":int(budget),
            "optimizer_reported_success":success,
            "optimizer_error":reason,
            "runtime_seconds":round(elapsed,5),
            "operator_selections":sum(x.get("selections",0) for x in operator_credit),
            **tracker.summary()}


def diagnostic(seeds=SEEDS,budget=BUDGET,population=POPULATION):
    if not seeds or budget<population or population<8:
        raise ValueError("Need seeds, budget >= population, population>=8")
    system=IEEE14EconomicPFFeasibleSubset()
    records=[]
    for seed in seeds:
        for method in METHODS:
            # Isolated fresh system and RNG before EACH optimizer
            row=run_method(IEEE14EconomicPFFeasibleSubset(),method,seed,budget,population)
            records.append(row)
            print("I17_REAL_GADAPT",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    summary={}
    for method in METHODS:
        arr=[r for r in records if r["method"]==method]
        good=[r["best_feasible_economic_cost"] for r in arr
              if r["best_feasible_economic_cost"] is not None]
        summary[method]={
            "runs":len(arr),
            "runs_with_at_least_one_physical_feasible_candidate":len(good),
            "median_feasible_cost_only_where_feasible":(
                statistics.median(good) if good else None),
            "true_ac_pf_calls":sum(r["real_ac_pf_calls"] for r in arr),
            "failed_ac_pf_calls":sum(r["solver_failed_calls"] for r in arr),
            "optimizer_status_success_runs":sum(r["optimizer_reported_success"] for r in arr),
        }
    return {"metadata":{
        "protocol":"research/ITERATION17_PROTOCOL.md",
        "algorithm":"real owlCoder/gadapt GA unchanged legacy; DE and random controls",
        "case":"original PYPOWER case14; PV-controlled 9-variable feasible SUBSET, not full AC-OPF",
        "source_IEEE14_20261021_verified_full_acopf_local_reference_cost":8081.526392989456,
        "benchmark_reference_not_free_GA_initialization":True,
        "budget_per_method_seed_real_ac_pf":budget,
        "seeds":list(seeds),"population_gadapt":population,
        "actual_ac_pf_calls":sum(r["real_ac_pf_calls"] for r in records),
        "actual_ac_opf_calls":0,
        "no_new_ga_mechanism_tested":True,
        "python":platform.python_version(),
        "scipy":scipy.__version__,
        "pandas":pd.__version__,
        "source_only_public_test_grid_not_live_industry":True},
        "runs":records,"summary":summary}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default="iteration17_ieee14_gadapt.json")
    parser.add_argument("--csv",default="iteration17_ieee14_gadapt.csv")
    parser.add_argument("--seeds",type=int,nargs="+",default=list(SEEDS))
    parser.add_argument("--budget",type=int,default=BUDGET)
    parser.add_argument("--population",type=int,default=POPULATION)
    args=parser.parse_args()
    result=diagnostic(tuple(args.seeds),args.budget,args.population)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        rows=[]
        for record in result["runs"]:
            flat={k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v)
                  for k,v in record.items()}
            rows.append(flat)
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("I17_SUMMARY",json.dumps(result["metadata"],sort_keys=True),flush=True)
    print("I17_COMPARISON",json.dumps(result["summary"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
