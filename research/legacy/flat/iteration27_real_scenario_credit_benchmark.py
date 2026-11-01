"""I27: true IEEE118 three-load-scenario GA operator credit comparison.

ALWAYS charge three native PYPOWER NR AC power flows per fitness candidate,
regardless of source feasibility and success. New scenario-credit callback
reads cached feedback, NEVER invokes another simulator. The original 5-VG
calibration box is inherited from I24; 6th PV BUS74 added on I25 Q evidence.
This is a pilot on synthetic ±2% source loads, NOT independent industrial
validation or claimed theoretical novelty.
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
from pypower.idx_bus import PD, QD, VMIN, VMAX
from pypower.idx_gen import GEN_BUS, PG, VG
from pypower.runpf import runpf
from scipy.optimize import differential_evolution, minimize

from research.iteration18_ieee118_gadapt_transfer import IEEE118NineControlSubset, physics_118
from research.iteration24_ieee118_fivepv_real_gadapt import calibrated_source_center

LOADS=(.98,1.0,1.02)
METHODS=("gadapt_legacy","gadapt_ucb_objective",
         "gadapt_ucb_scalar_feasibility","gadapt_ucb_scenario_feasibility",
         "scipy_de","bounded_powell")
SEEDS=(2026,2027,2028)
BUDGET=180
POPULATION=12
PHYSICAL_SCENARIOS=3
FAILED_SCORE=1e12
PENALTY=1e5
CONTROL_BUS_GEN=((103,45),(32,14),(34,15),(92,42),(19,8),(74,33))


class IEEE118SixSourcePVThreeScenarios:
    def __init__(self):
        self.reference=IEEE118NineControlSubset()
        self.source=self.reference.source
        five_center,five_bounds=calibrated_source_center()
        g=self.source["gen"]
        b=self.source["bus"][self.source["bus"][:,0]==74]
        if len(b)!=1 or int(b[0,1])!=2 or int(g[33,GEN_BUS])!=74 or len(g)!=54:
            raise ValueError("Source IEEE118 BUS74 PV generator row changed")
        original_vg=float(g[33,VG])
        if abs(original_vg-.958)>1e-8:
            raise ValueError("Source BUS74 VG changed from prerecorded original case")
        low=max(float(b[0,VMIN]),original_vg-.01)
        high=min(float(b[0,VMAX]),original_vg+.01)
        if not low<original_vg<high:
            raise ValueError("Original BUS74 6th control outside source V bounds")
        self.center=np.array([*five_center,original_vg])
        self.bounds=[*five_bounds,(low,high)]
        self.n=6
        self.real_ac_calls=0

    def evaluate_scenario(self, candidate, factor):
        """Perform ONE true original load-modified PYPOWER AC NR simulation."""
        x=np.asarray(candidate,dtype=float)
        if x.shape!=(self.n,) or not np.all(np.isfinite(x)):
            raise ValueError("Invalid source IEEE118 6D VG control vector")
        if any(v<low-1e-8 or v>high+1e-8 for v,(low,high) in zip(x,self.bounds)):
            raise ValueError("IEEE118 6D candidate violates source local search box")
        if factor not in LOADS:
            raise ValueError("Non-preregistered original IEEE118 source load scenario")
        case={key:(value.copy() if isinstance(value,np.ndarray) else value)
              for key,value in self.source.items()}
        case["bus"][:,PD]*=factor
        case["bus"][:,QD]*=factor
        for (_,idx),value in zip(CONTROL_BUS_GEN,x):
            case["gen"][idx,VG]=float(value)
        if not np.array_equal(case["gen"][:,PG],self.source["gen"][:,PG]):
            raise ValueError("Unregistered PG redispatch")
        other=np.ones(54,dtype=bool)
        other[[idx for _,idx in CONTROL_BUS_GEN]]=False
        if not np.array_equal(case["gen"][other,VG],self.source["gen"][other,VG]):
            raise ValueError("Unexpected original VG change")
        self.real_ac_calls+=1  # exact boundary, even if runpf returns failure or throws.
        try:
            result,success=runpf(case,self.reference.settings)
            if not success:
                return {"converged":False,"feasible":False,
                        "error":"PYPOWER original IEEE118 NR runpf success=False"}
            p=physics_118(result,case)
            return {"converged":True,"feasible":bool(p["feasible"]),
                "error":"","original_economic_cost":p["actual_economic_cost"],
                "normalized_violation":(
                    0.0 if p["feasible"] else float(p["source_normalized_violation"])),
                "q_source_excess_mvar":p["q_sum_excess_mvar"],
                "p_source_excess_mw":p["p_sum_excess_mw"],
                "bus_v_excess_pu":p["voltage_sum_excess_pu"],
                "positive_rate_a_mva_excess":p["thermal_sum_excess_mva"],
                "max_source_q_excess_mvar":p["max_generator_q_excess_mvar"],
                "max_nodal_mismatch_mva":p["max_nodal_mismatch_mva"]}
        except Exception as e:
            return {"converged":False,"feasible":False,
                    "error":(type(e).__name__+": "+str(e))[:240]}


class ThreeScenarioPhysicalBudget:
    def __init__(self,grid,budget):
        self.grid=grid
        if budget<PHYSICAL_SCENARIOS or budget%PHYSICAL_SCENARIOS:
            raise ValueError("A full integer number of three-scenario AC batches required")
        self.budget=int(budget)
        self.requests=0
        self.post_budget_requests=0
        self.complete_batches=0
        self.numerically_failed_ac=0
        self.robust_feasible_batches=0
        self.first_robust_real_AC_call=None
        self.best_robust_economic_cost=math.inf
        self.best_robust_vector=None
        self.best_robust_source_metrics=None
        self.best_penalized=math.inf
        self.best_penalized_vector=None
        self.per_scenario_source_feasible=[0,0,0]
        self._latest=None

    @property
    def calls(self):
        return self.grid.real_ac_calls

    def __call__(self, candidate):
        self.requests+=1
        self._latest=None  # stale cache cannot reward sentinel/old chromosome
        if self.calls+PHYSICAL_SCENARIOS>self.budget:
            self.post_budget_requests+=1
            return FAILED_SCORE
        before=self.calls
        signals=[]
        for factor in LOADS:
            # These are three genuine distinct load-source simulations.
            signals.append(self.grid.evaluate_scenario(candidate,factor))
        if self.calls-before!=PHYSICAL_SCENARIOS:
            raise RuntimeError("Physics evaluation did not charge exactly three real AC PF calls")
        self.complete_batches+=1
        for i,signal in enumerate(signals):
            if not signal["converged"]:
                self.numerically_failed_ac+=1
            if signal["feasible"]:
                self.per_scenario_source_feasible[i]+=1
        if not all(z["converged"] for z in signals):
            return FAILED_SCORE
        source_costs=[float(z["original_economic_cost"]) for z in signals]
        normalized=[float(z["normalized_violation"]) for z in signals]
        if any(not math.isfinite(v) or v<0 for v in normalized):
            raise ValueError("Invalid original physical scenario violation")
        mean_cost=float(np.mean(source_costs))
        score=mean_cost+PENALTY*sum(normalized)
        if not math.isfinite(score):
            raise ValueError("Nonfinite true multi-scenario AC score")
        key=tuple(float(z) for z in candidate)
        # Stored only after all THREE actual simulator calls. A callback only reads it.
        self._latest=(key,score,tuple(normalized))
        if score<self.best_penalized:
            self.best_penalized=score
            self.best_penalized_vector=key
        if all(z["feasible"] for z in signals):
            self.robust_feasible_batches+=1
            if self.first_robust_real_AC_call is None:
                self.first_robust_real_AC_call=self.calls
            if mean_cost<self.best_robust_economic_cost:
                self.best_robust_economic_cost=mean_cost
                self.best_robust_vector=key
                self.best_robust_source_metrics={
                   "per_load_original_economic_cost":source_costs,
                   "per_load_normalized_violation":normalized,
                   "per_load_max_original_q_excess_mvar":[z["max_source_q_excess_mvar"] for z in signals],
                   "per_load_max_kcl_mva":[z["max_nodal_mismatch_mva"] for z in signals]}
        return float(score)

    def cached_scenario_violation(self,vector,score):
        if self._latest is None:
            return None
        key,known_score,violations=self._latest
        if (tuple(float(v) for v in vector)!=key or
            not math.isclose(float(score),known_score,rel_tol=0.,abs_tol=1e-9)):
            return None
        return violations

    def cached_scalar_worst_violation(self,vector,score):
        signal=self.cached_scenario_violation(vector,score)
        return max(signal) if signal is not None else None

    def summary(self):
        return {
            "true_real_ac_pf_calls":self.calls,
            "complete_three_source_scenario_batches":self.complete_batches,
            "objective_requests":self.requests,
            "requests_after_real_ac_budget":self.post_budget_requests,
            "failed_real_ac_nr_calls":self.numerically_failed_ac,
            "per_load_source_feasible_batch_counts":list(self.per_scenario_source_feasible),
            "all_three_original_source_feasible_batches":self.robust_feasible_batches,
            "first_all_three_feasible_true_ac_call":self.first_robust_real_AC_call,
            "best_all_three_feasible_mean_original_economic_cost":(
                self.best_robust_economic_cost if math.isfinite(self.best_robust_economic_cost) else None),
            "best_all_three_feasible_vector":(
                list(self.best_robust_vector) if self.best_robust_vector is not None else None),
            "best_all_three_feasible_physical_metrics":self.best_robust_source_metrics,
            "best_penalized_three_scenario_score":(
                self.best_penalized if math.isfinite(self.best_penalized) else None),
            "best_penalized_three_scenario_vector":(
                list(self.best_penalized_vector) if self.best_penalized_vector is not None else None),
        }


def run_method(method,seed,budget=BUDGET,population=POPULATION,model=None):
    if method not in METHODS:
        raise ValueError("Method not preregistered")
    random.seed(seed)
    np.random.seed(seed)
    grid=model if model is not None else IEEE118SixSourcePVThreeScenarios()
    physical=ThreeScenarioPhysicalBudget(grid,budget)
    time_begin=time.monotonic()
    ok=True
    reason=""
    stats=[]
    result=None
    try:
        if method.startswith("gadapt_"):
            kw={}
            if method!="gadapt_legacy":
                kw["mutation_operator_policy"]="ucb"
                kw["mutation_evaluation_counter"]=lambda:physical.calls
                if method=="gadapt_ucb_objective":
                    kw["mutation_operator_credit"]="objective"
                elif method=="gadapt_ucb_scalar_feasibility":
                    kw["mutation_operator_credit"]="feasibility"
                    kw["mutation_violation_function"]=physical.cached_scalar_worst_violation
                else:
                    kw["mutation_operator_credit"]="scenario_feasibility"
                    kw["mutation_scenario_count"]=PHYSICAL_SCENARIOS
                    kw["mutation_violation_function"]=physical.cached_scenario_violation
            ga=GA(cost_function=physical,population_size=population,
                  cost_diversity_metric="log_relative",
                  exit_check="generations",number_of_generations=48,
                  exit_function=lambda:physical.calls>=budget,
                  population_mutation="cost_diversity,parent_diversity",
                  timeout=240,**kw)
            for lo,hi in grid.bounds:
                ga.add(lo,hi)
            result=ga.execute()
            ok=bool(result.success)
            reason="" if ok else str(result.messages)[:240]
            stats=getattr(result,"operator_credit_summary",[])
        elif method=="scipy_de":
            pop=max(5,math.ceil(population/grid.n))
            result=differential_evolution(
               physical,grid.bounds,popsize=pop,
               maxiter=math.ceil(budget/(PHYSICAL_SCENARIOS*pop*grid.n))+3,
               tol=0.,atol=0.,polish=False,seed=seed,updating="immediate")
            ok=bool(result.success)
            reason="" if ok else str(result.message)[:240]
        else:
            result=minimize(physical,grid.center.copy(),method="Powell",
              bounds=grid.bounds,options={"maxfev":budget//PHYSICAL_SCENARIOS,
                   "xtol":1e-5,"ftol":1e-7,"disp":False})
            ok=bool(result.success)
            reason="" if ok else str(result.message)[:240]
    except Exception as err:
        ok=False
        reason=(type(err).__name__+": "+str(err))[:240]
    if physical.calls>budget or physical.calls%PHYSICAL_SCENARIOS:
        raise RuntimeError("Hard physical cap violated or partial source load batch")
    if physical.complete_batches*PHYSICAL_SCENARIOS!=physical.calls:
        raise RuntimeError("AC solver attempts not equal to counted full source scenario batches")
    return {
       "method":method,"seed":int(seed),
       "actual_ac_max_budget":int(budget),
       "optimizer_success_flag":ok,
       "optimizer_error_or_stop_reason":reason,
       "real_elapsed_seconds":round(time.monotonic()-time_begin,5),
       "operator_credit_summary":stats,
       **physical.summary()
    }


def execute(seeds=SEEDS,budget=BUDGET,population=POPULATION):
    if not seeds or budget<3*population or budget%3 or population<10:
        raise ValueError("Run must supply valid preregistered 3-AC batch budget")
    rows=[]
    for seed in seeds:
        for method in METHODS:
            outcome=run_method(method,seed,budget,population)
            rows.append(outcome)
            print("I27_REAL_3SCENARIO",json.dumps(outcome,sort_keys=True,allow_nan=False),flush=True)
    summary={}
    for method in METHODS:
        selected=[r for r in rows if r["method"]==method]
        feasible=[r["best_all_three_feasible_mean_original_economic_cost"] for r in selected
                  if r["best_all_three_feasible_mean_original_economic_cost"] is not None]
        summary[method]={
          "runs":len(selected),
          "runs_with_all_three_physical_scenarios_feasible":len(feasible),
          "true_ac_pf_calls":sum(r["true_real_ac_pf_calls"] for r in selected),
          "physically_all_three_feasible_batches":sum(
                r["all_three_original_source_feasible_batches"] for r in selected),
          "min_robust_original_economic_mean_cost_or_null":min(feasible) if feasible else None,
          "median_robust_cost_conditional_on_success_only":statistics.median(feasible) if feasible else None,
          "mean_per_load_feasible_counts":[sum(r["per_load_source_feasible_batch_counts"][k] for r in selected)
                                           for k in range(3)],
          "deterministic_powell_triplicate_not_independent":method=="bounded_powell",
        }
    probe=IEEE118SixSourcePVThreeScenarios()
    return {"metadata":{
       "protocol":"research/ITERATION27_PROTOCOL.md",
       "source_network":"original public PYPOWER IEEE118, synthetic 98/100/102 percent PD and QD",
       "all_scenario_source_load_factors":list(LOADS),
       "three_distinct_real_ac_per_scored_candidate":True,
       "preregistered_methods":list(METHODS),
       "seeds":list(seeds),"population_gadapt":population,
       "original_six_pv_bus_ids":[bus for bus,_ in CONTROL_BUS_GEN],
       "new_bus74_sixth_control_chosen_based_on_prior_i25_stress":True,
       "common_center_pu":list(map(float,probe.center)),
       "common_six_VG_bounds_pu":probe.bounds,
       "calibrated_in_sample_not_generalization":True,
       "max_real_ac_per_method_seed":int(budget),
       "total_preregistered_upper_bound_true_ac":budget*len(METHODS)*len(seeds),
       "actual_native_ac_pf_calls":sum(r["true_real_ac_pf_calls"] for r in rows),
       "new_actual_ac_opf_calls":0,
       "source_only_public_IEEE_not_field_data":True,
       "algorithm_novelty_not_verified":True,
       "python":platform.python_version(),"scipy":scipy.__version__,
       "pandas":pd.__version__,
    },"runs":rows,"summary":summary}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default="iteration27_scenario_credit.json")
    parser.add_argument("--csv",default="iteration27_scenario_credit.csv")
    parser.add_argument("--seeds",type=int,nargs="+",default=list(SEEDS))
    parser.add_argument("--budget",type=int,default=BUDGET)
    parser.add_argument("--population",type=int,default=POPULATION)
    args=parser.parse_args()
    data=execute(tuple(args.seeds),args.budget,args.population)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,sort_keys=True,allow_nan=False)
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        rows=[{k:(json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v)
              for k,v in record.items()} for record in data["runs"]]
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    print("I27_COMPARISON",json.dumps(data["summary"],sort_keys=True),flush=True)
    print("I27_METADATA",json.dumps(data["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
