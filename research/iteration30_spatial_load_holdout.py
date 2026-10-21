"""I30 physical scenario holdout: SAME IEEE118, spatial rather than uniform load.

Preregistered three *new* synthetic PD/QD profiles only:
   nominal, odd source BUS_I x1.02 even x0.98, reverse.
No change to inherited 6 generator source VG controls, bounds, original
PG/Q limits, topology, thermal ratings, or genuine solver-count semantics.

Same I29 opt-in metered evaluator, full vs fixed vs empirical scenario
order; four NEW seeds, 5 methods, cap 3600 real native AC PF in total.
THIS IS NOT AN INDEPENDENT NETWORK OR PROOF OF ORIGINAL ALGORITHM.
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
from gadapt.operations.cost_finding.sequential_scenario_budget_cost import (
    SequentialScenarioBudgetCost
)
from pypower.idx_bus import BUS_I,PD,QD
from pypower.idx_gen import PG,VG
from pypower.runpf import runpf
from scipy.optimize import differential_evolution

from research.iteration18_ieee118_gadapt_transfer import physics_118
from research.iteration27_real_scenario_credit_benchmark import (
    IEEE118SixSourcePVThreeScenarios,CONTROL_BUS_GEN
)
from research.iteration29_real_scenario_earlystop_benchmark import (
    METHODS, BUDGET, POPULATION,method_mode
)

SPATIAL_SCENARIOS=("nominal","odd_bus_heavier","even_bus_heavier")
SPATIAL_SEEDS=(2070,2071,2072,2073)
UPPER_BOUND_TRUE_AC=5*4*180


class IEEE118SourceParityLoadScenario(IEEE118SixSourcePVThreeScenarios):
    """Build new original-source PD/QD-only parity stress; AC is not free."""
    def new_source_case_no_ac(self,vector,profile):
        if profile not in SPATIAL_SCENARIOS:
            raise ValueError("Unknown preregistered IEEE118 load spatial profile")
        x=np.asarray(vector,dtype=float)
        if x.shape!=(self.n,) or not np.all(np.isfinite(x)):
            raise ValueError("Original IEEE118 six source PV controls invalid")
        if any(v<low-1e-8 or v>high+1e-8
               for v,(low,high) in zip(x,self.bounds)):
            raise ValueError("Original IEEE118 source PV bounds exceeded")
        original=self.source
        case={k:(v.copy() if isinstance(v,np.ndarray) else v)
              for k,v in original.items()}
        ids=case["bus"][:,BUS_I]
        if len(ids)!=118 or not np.array_equal(ids,np.arange(1.,119.)):
            raise ValueError("Original source IEEE118 BUS_I identity changed")
        odd=np.mod(ids.astype(int),2)==1
        if profile=="nominal":
            factors=np.ones(len(ids))
        elif profile=="odd_bus_heavier":
            factors=np.where(odd,1.02,.98)
        else:
            factors=np.where(odd,.98,1.02)
        case["bus"][:,PD]=original["bus"][:,PD]*factors
        case["bus"][:,QD]=original["bus"][:,QD]*factors
        for (_,idx),val in zip(CONTROL_BUS_GEN,x):
            case["gen"][idx,VG]=float(val)
        if not np.array_equal(case["gen"][:,PG],original["gen"][:,PG]):
            raise ValueError("Original generator active dispatch changed")
        other=np.ones(54,dtype=bool)
        other[[i for _,i in CONTROL_BUS_GEN]]=False
        if not np.array_equal(case["gen"][other,VG],original["gen"][other,VG]):
            raise ValueError("Other source generator VG changed")
        return case

    def evaluate_scenario(self,vector,profile):
        case=self.new_source_case_no_ac(vector,profile)
        self.real_ac_calls+=1  # Genuine runpf boundary, even on numerical failure.
        try:
            out,converged=runpf(case,self.reference.settings)
            if not converged:
                return {"converged":False,"feasible":False,
                        "error":"Original parity-load PYPOWER AC NR did not converge"}
            p=physics_118(out,case)
            return {
                "converged":True,
                "feasible":bool(p["feasible"]),
                "original_economic_cost":float(p["actual_economic_cost"]),
                "normalized_violation":(
                    0. if p["feasible"] else float(p["source_normalized_violation"])),
                "q_source_excess_mvar":p["q_sum_excess_mvar"],
                "p_source_excess_mw":p["p_sum_excess_mw"],
                "bus_v_excess_pu":p["voltage_sum_excess_pu"],
                "positive_rate_a_mva_excess":p["thermal_sum_excess_mva"],
                "max_source_q_excess_mvar":p["max_generator_q_excess_mvar"],
                "max_nodal_mismatch_mva":p["max_nodal_mismatch_mva"]
            }
        except Exception as err:
            return {"converged":False,"feasible":False,
                    "error":(type(err).__name__+": "+str(err))[:240]}


def perform_one(method,seed):
    if method not in METHODS or seed not in SPATIAL_SEEDS:
        raise ValueError("Not a preregistered I30 model/seed")
    random.seed(seed)
    np.random.seed(seed)
    grid=IEEE118SourceParityLoadScenario()
    ev=SequentialScenarioBudgetCost(
        SPATIAL_SCENARIOS,grid.evaluate_scenario,
        lambda:grid.real_ac_calls, BUDGET,mode=method_mode(method),penalty=1e5)
    start=time.monotonic()
    success=False
    error=""
    try:
        if method.startswith("gadapt_"):
            ga=GA(
               cost_function=ev,
               population_size=POPULATION,
               cost_diversity_metric="log_relative",
               exit_check="generations",number_of_generations=128,
               exit_function=lambda:ev.remaining<3,
               population_mutation="cost_diversity,parent_diversity",
               timeout=240,
            )
            for lo,hi in grid.bounds:
                ga.add(float(lo),float(hi))
            result=ga.execute()
            success=bool(result.success)
            error="" if success else str(result.messages)[:280]
        else:
            result=differential_evolution(
                ev,grid.bounds,popsize=5,maxiter=12,tol=0.,atol=0.,
                polish=False,seed=seed,updating="immediate")
            success=bool(result.success)
            error="" if success else str(result.message)[:280]
    except Exception as ex:
        error=(type(ex).__name__+": "+str(ex))[:280]
    q=ev.summary()
    if q["actual_native_AC_calls"]!=grid.real_ac_calls or grid.real_ac_calls>BUDGET:
        raise RuntimeError("Original spatial load real physical count false")
    return {
        "method":method,"seed":seed,
        "solver_original_bus_parity_scenario_holdout":True,
        "optimizer_success_flag":success,
        "optimizer_stop_reason":error,
        "runtime_seconds":round(time.monotonic()-start,5),
        **q}


def run_all():
    if (METHODS!=("gadapt_full","gadapt_stop_fixed","gadapt_stop_adaptive",
                  "scipy_de_full","scipy_de_stop_fixed") or
        SPATIAL_SEEDS!=(2070,2071,2072,2073) or
        SPATIAL_SCENARIOS!=("nominal","odd_bus_heavier","even_bus_heavier")
        or UPPER_BOUND_TRUE_AC!=3600):
        raise RuntimeError("Preregistered I30 new spatial load experiment changed")
    rows=[]
    for seed in SPATIAL_SEEDS:
        for method in METHODS:
            row=perform_one(method,seed)
            rows.append(row)
            print("I30_REAL_SPATIAL_AC",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    summary={}
    for method in METHODS:
        selected=[x for x in rows if x["method"]==method]
        real_feasible=[x["best_verified_robust_mean_economic_cost_or_null"]
             for x in selected if x["best_verified_robust_mean_economic_cost_or_null"] is not None]
        summary[method]={
          "runs":len(selected),
          "runs_with_actual_all_spatial_scenarios_feasible":len(real_feasible),
          "total_truly_attempted_original_AC":sum(x["actual_native_AC_calls"] for x in selected),
          "complete_all_three_scenario_cases":sum(x["completely_evaluated_candidates"] for x in selected),
          "actually_all_three_source_feasible_cases":sum(x["verified_all_scenario_feasible_candidates"] for x in selected),
          "partial_verified_physical_infeasible_screens":sum(x["early_screened_physically_infeasible_candidates"] for x in selected),
          "true_objective_requests":sum(x["objective_requests"] for x in selected),
          "unobserved_original_ac_that_were_NEVER_run":sum(x["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"] for x in selected),
          "true_observed_AC_per_spatial_profile":[sum(x["actual_AC_per_scenario"][i] for x in selected) for i in range(3)],
          "best_verified_original_mean_cost_or_null":min(real_feasible) if real_feasible else None,
          "median_verified_cost_conditional_only":statistics.median(real_feasible) if real_feasible else None,
        }
    probe=IEEE118SourceParityLoadScenario()
    return {"metadata":{
       "protocol":"research/ITERATION30_PROTOCOL.md",
       "spatial_profiles":list(SPATIAL_SCENARIOS),
       "original_source_load_construction":"PD QD original BUS_I odd/even factors 1.02/0.98",
       "same_six_original_PV_buses":[bus for bus,_ in CONTROL_BUS_GEN],
       "fixed_legacy_ga_and_I29_sequential_scenario_cost_UNMODIFIED":True,
       "new_unseen_spatial_scenarios_not_new_grid":True,
       "seeds":list(SPATIAL_SEEDS),"methods":list(METHODS),
       "real_AC_per_run_max":BUDGET,
       "preregistered_max_true_source_AC":UPPER_BOUND_TRUE_AC,
       "actual_true_source_AC":sum(x["actual_native_AC_calls"] for x in rows),
       "new_ac_opf_calls":0,
       "engineering_early_reject_known_prior_art":True,
       "public_ieee118_not_real_industry":True,
       "no_physics_solved_in_preflight":probe.real_ac_calls,
       "environment":{"python":platform.python_version(),
                      "scipy":scipy.__version__,
                      "pandas":pd.__version__},
    },"runs":rows,"summary":summary}


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--json",default="iteration30_spatial_holdout.json")
    a.add_argument("--csv",default="iteration30_spatial_holdout.csv")
    args=a.parse_args()
    out=run_all()
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(out,f,sort_keys=True,indent=2,allow_nan=False)
    flat=[{k:(json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v)
           for k,v in item.items()} for item in out["runs"]]
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]))
        w.writeheader();w.writerows(flat)
    print("I30_SPATIAL_SUMMARY",json.dumps(out["summary"],sort_keys=True,allow_nan=False),flush=True)
    print("I30_SPATIAL_META",json.dumps(out["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
