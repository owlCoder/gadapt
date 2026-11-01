"""I32 preregistered original IEEE14 *different topology* transfer test.

Public 14-bus source; not an unseen historical network or a full AC-OPF.
Real PYPOWER runpf is counted at its actual physical invocation boundary.
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
import scipy
import pandas as pd
from gadapt.ga import GA
from gadapt.operations.cost_finding.sequential_scenario_budget_cost import (
    CENSORED_BASE_SCORE, SequentialScenarioBudgetCost,
)
from pypower.idx_bus import BUS_I, PD, QD
from pypower.idx_gen import PG, VG
from pypower.runpf import runpf
from scipy.optimize import differential_evolution
from research.iteration17_ieee14_gadapt_economic_pf import (
    IEEE14EconomicPFFeasibleSubset, measured_feasibility,
)

SCENARIOS = ("nominal", "odd_bus_plus1pct", "even_bus_plus1pct")
METHODS = ("gadapt_full_true", "gadapt_full_censored", "gadapt_stop_fixed",
           "gadapt_stop_adaptive", "de_full_true", "de_stop_fixed")
SEEDS = tuple(range(2104, 2116))
BUDGET = 180
POPULATION = 12
UPPER_BOUND_AC = len(METHODS)*len(SEEDS)*BUDGET


class IEEE14OriginalSpatialLoad:
    """9D original I17 PG/VG subset; only PD/QD vary between I32 profiles."""
    def __init__(self):
        self.reference = IEEE14EconomicPFFeasibleSubset()
        self.original = self.reference.source
        self.bounds = self.reference.bounds
        self.n = self.reference.n
        self.real_ac_calls = 0
        self.source_bus_ids = tuple(int(v) for v in self.original["bus"][:, BUS_I])
        if (self.n != 9 or len(self.source_bus_ids)!=14
                or self.source_bus_ids != tuple(range(1,15))
                or len(self.reference.non_slack_gen_ids)!=4
                or len(self.reference.all_gen_ids)!=5
                or len(self.original["branch"])!=20):
            raise RuntimeError("IEEE14 original case or decision space drift")

    def source_case_without_ac(self, vector, profile):
        if profile not in SCENARIOS:
            raise ValueError("Non-registered I32 scenario")
        x = np.asarray(vector, float)
        if (x.shape != (self.n,) or not np.all(np.isfinite(x))
                or any(v<lo-1e-8 or v>hi+1e-8
                       for v,(lo,hi) in zip(x,self.bounds))):
            raise ValueError("IEEE14 9D candidate must satisfy original source bounds")
        case = {k:(v.copy() if isinstance(v,np.ndarray) else v)
                for k,v in self.original.items()}
        odd = np.asarray(self.source_bus_ids) % 2 == 1
        if profile == "nominal":
            factor = np.ones(14)
        elif profile == "odd_bus_plus1pct":
            factor = np.where(odd,1.01,0.99)
        else:
            factor = np.where(odd,0.99,1.01)
        case["bus"][:,PD] = self.original["bus"][:,PD]*factor
        case["bus"][:,QD] = self.original["bus"][:,QD]*factor
        n_p = len(self.reference.non_slack_gen_ids)
        for gen_index, value in zip(self.reference.non_slack_gen_ids, x[:n_p]):
            case["gen"][gen_index,PG] = float(value)
        for gen_index, value in zip(self.reference.all_gen_ids, x[n_p:]):
            case["gen"][gen_index,VG] = float(value)
        if (not np.array_equal(case["branch"],self.original["branch"])
                or not np.array_equal(case["gencost"],self.original["gencost"])):
            raise RuntimeError("IEEE14 source branch or economic cost modified")
        return case

    def evaluate_scenario(self, vector, profile):
        case = self.source_case_without_ac(vector,profile)
        self.real_ac_calls += 1  # Genuine runpf, even if NR fails/throws.
        try:
            solved, converged = runpf(case, self.reference.settings)
            if not converged:
                return {"converged":False,"feasible":False,
                        "error":"Original IEEE14 runpf did not converge"}
            info = measured_feasibility(solved,case)
            violation = 0. if info["feasible"] else float(info["source_normalized_violation"])
            if not math.isfinite(violation) or (not info["feasible"] and violation<=0):
                raise ValueError("Original physical source violation must be positive")
            return {
                "converged":True, "feasible":bool(info["feasible"]),
                "original_economic_cost":float(info["actual_economic_cost"]),
                "normalized_violation":float(violation),
                "q_source_excess_mvar":info["q_sum_excess_mvar"],
                "p_source_excess_mw":info["p_sum_excess_mw"],
                "bus_v_excess_pu":info["voltage_sum_excess_pu"],
                "positive_rate_a_mva_excess":info["thermal_sum_excess_mva"],
                "max_nodal_mismatch_mva":info["max_nodal_mismatch_mva"],
            }
        except Exception as exc:
            return {"converged":False,"feasible":False,
                    "error":(type(exc).__name__+": "+str(exc))[:240]}


class FullPaidFirstFailureScore(SequentialScenarioBudgetCost):
    """No AC skipped. Only the GA/DE ranking score gets I29 first-fail censoring.

    This class is a *control*, independent of the separate I31 PR branch.
    A numerical-unknown in any of the three truly paid AC returns the
    original unknown score. The true fully verified source cost/feasibility
    remains stored in the inherited audit summary, never fabricated.
    """
    def __init__(self, **kwargs):
        super().__init__(mode="full",**kwargs)
        self._inner_evaluator = self._evaluate
        self._first_failure = None
        self._censored_full_candidates = 0
        self._evaluate = self._audit_first_failure

    def _audit_first_failure(self,x,scenario):
        raw = self._inner_evaluator(x,scenario)
        if (isinstance(raw,dict) and raw.get("converged") is True
                and raw.get("feasible") is False
                and self._first_failure is None):
            self._first_failure = raw.get("normalized_violation")
        return raw

    def __call__(self,x):
        self._first_failure = None
        true_score = super().__call__(x)
        if self._last_status != "completely_evaluated" or self._first_failure is None:
            return true_score
        failure = float(self._first_failure)
        if not math.isfinite(failure) or failure<=0:
            raise RuntimeError("Physical first-failure censoring inconsistent")
        censored = CENSORED_BASE_SCORE+self.penalty*failure
        if censored>=self.unknown_score or not math.isfinite(censored):
            raise RuntimeError("Physical failure score exceeds numerical-unknown sentinel")
        self._censored_full_candidates += 1
        self.best_censored_ranking_score = min(self.best_censored_ranking_score,censored)
        return float(censored)

    def summary(self):
        result = super().summary()
        result["mode"] = "full_censored"
        result["fully_paid_candidates_with_censored_selection_score"] = self._censored_full_candidates
        result["complete_true_physical_score_retained_separately"] = True
        return result


def make_cost(method,grid):
    if method not in METHODS:
        raise ValueError("Unregistered I32 method")
    args = dict(scenarios=SCENARIOS,scenario_evaluator=grid.evaluate_scenario,
                physical_counter=lambda:grid.real_ac_calls,budget=BUDGET,
                penalty=1e5)
    if method=="gadapt_full_censored":
        return FullPaidFirstFailureScore(**args)
    mode = ("stop_adaptive" if method=="gadapt_stop_adaptive" else
            "stop_fixed" if method.endswith("stop_fixed") else "full")
    return SequentialScenarioBudgetCost(**args,mode=mode)


def run_one(method,seed):
    if method not in METHODS or seed not in SEEDS:
        raise ValueError("I32 run must be preregistered")
    random.seed(seed)
    np.random.seed(seed)
    grid = IEEE14OriginalSpatialLoad()
    evaluator = make_cost(method,grid)
    started = time.monotonic()
    optimizer_success = False
    error = ""
    try:
        if method.startswith("gadapt_"):
            ga=GA(cost_function=evaluator,population_size=POPULATION,
                  cost_diversity_metric="log_relative",
                  exit_check="generations",number_of_generations=128,
                  exit_function=lambda:evaluator.remaining<3,
                  population_mutation="cost_diversity,parent_diversity",
                  timeout=240)
            for lo,hi in grid.bounds:
                ga.add(float(lo),float(hi))
            result=ga.execute()
            optimizer_success=bool(result.success)
            if not optimizer_success:
                error=str(result.messages)[:250]
        else:
            result=differential_evolution(
                evaluator,grid.bounds,popsize=5,maxiter=12,tol=0.,atol=0.,
                polish=False,seed=seed,updating="immediate")
            optimizer_success=bool(result.success)
            if not optimizer_success:
                error=str(result.message)[:250]
    except Exception as exc:
        error=(type(exc).__name__+": "+str(exc))[:250]
    q=evaluator.summary()
    n=grid.real_ac_calls
    if (q["actual_native_AC_calls"]!=n or n>BUDGET
            or sum(q["actual_AC_per_scenario"])!=n
            or q["verified_all_scenario_feasible_candidates"]>
                 q["completely_evaluated_candidates"]
            or sum(q["actually_observed_numerical_unknown_per_scenario"])
               >n):
        raise RuntimeError("I32 true AC budget or feasible-observation invariant failed")
    if method in ("gadapt_full_true","gadapt_full_censored","de_full_true"):
        if (n%3 or q["actual_AC_per_scenario"]!=[n//3]*3
                or q["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"]):
            raise RuntimeError("I32 fully paid control skipped scenario")
    return {"seed":int(seed),"method":method,"optimizer_success_not_physical_feasible":optimizer_success,
            "optimizer_stop_message":error,"wall_seconds":round(time.monotonic()-started,5),
            **q}


def paired(rows,a,b):
    x={r["seed"]:r["verified_all_scenario_feasible_candidates"]>0
       for r in rows if r["method"]==a}
    y={r["seed"]:r["verified_all_scenario_feasible_candidates"]>0
       for r in rows if r["method"]==b}
    if set(x)!=set(SEEDS) or set(y)!=set(SEEDS):
        raise ValueError("Missing preregistered seed")
    aa=sum(x[s] and y[s] for s in SEEDS)
    ab=sum(x[s] and not y[s] for s in SEEDS)
    ba=sum(not x[s] and y[s] for s in SEEDS)
    bb=sum(not x[s] and not y[s] for s in SEEDS)
    n=ab+ba
    two_sided_p=min(1.,2*sum(math.comb(n,k) for k in range(min(ab,ba)+1))/2**n) if n else 1.
    return {"first":a,"second":b,"both":aa,"first_only":ab,
            "second_only":ba,"neither":bb,
            "exact_two_sided_discordant_binomial_p_UNADJUSTED":two_sided_p}


def experiment():
    if (SCENARIOS!=("nominal","odd_bus_plus1pct","even_bus_plus1pct")
            or METHODS!=("gadapt_full_true","gadapt_full_censored",
               "gadapt_stop_fixed","gadapt_stop_adaptive","de_full_true","de_stop_fixed")
            or SEEDS!=tuple(range(2104,2116)) or BUDGET!=180
            or POPULATION!=12 or UPPER_BOUND_AC!=12960):
        raise RuntimeError("I32 preregistration parameter drift")
    rows=[]
    for seed in SEEDS:
        for method in METHODS:
            r=run_one(method,seed)
            rows.append(r)
            print("I32_REAL_SOURCE_AC",json.dumps(r,sort_keys=True,allow_nan=False),flush=True)
    summary={}
    for method in METHODS:
        selected=[r for r in rows if r["method"]==method]
        costs=[r["best_verified_robust_mean_economic_cost_or_null"]
               for r in selected if r["best_verified_robust_mean_economic_cost_or_null"] is not None]
        summary[method]={
            "runs":len(selected),"successful_seeds":len(costs),
            "actual_true_native_AC":sum(r["actual_native_AC_calls"] for r in selected),
            "complete_all_three_candidates":sum(r["completely_evaluated_candidates"] for r in selected),
            "verified_robust_source_feasible_candidates":sum(
                r["verified_all_scenario_feasible_candidates"] for r in selected),
            "proven_physical_early_screens":sum(
                r["early_screened_physically_infeasible_candidates"] for r in selected),
            "numerically_unknown_candidates":sum(
                r["numerically_unknown_candidates"] for r in selected),
            "objective_requests":sum(r["objective_requests"] for r in selected),
            "skipped_unobserved_scenarios":sum(
                r["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"]
                for r in selected),
            "best_truly_robust_source_mean_economic_cost_or_null":min(costs) if costs else None,
            "median_truly_verified_cost_conditional_on_seed_success_or_null":
                statistics.median(costs) if costs else None,
        }
    contrasts=[
        paired(rows,"gadapt_full_true","gadapt_full_censored"),
        paired(rows,"gadapt_full_censored","gadapt_stop_fixed"),
        paired(rows,"gadapt_stop_fixed","gadapt_stop_adaptive"),
        paired(rows,"gadapt_stop_fixed","de_stop_fixed"),
        paired(rows,"gadapt_full_true","de_full_true"),
    ]
    return {"metadata":{
        "protocol":"research/ITERATION32_PROTOCOL.md",
        "original_ieee14_distinct_topology_not_blind_or_real_industry":True,
        "nine_decision_variables_not_full_acopf":True,
        "original_source_9D":True,
        "source_scenario_PD_QD_multipliers":"odd bus x1.01 even x0.99 or reverse",
        "scenarios":list(SCENARIOS),"seeds":list(SEEDS),"methods":list(METHODS),
        "max_native_AC_per_method_seed":BUDGET,"max_true_native_AC":UPPER_BOUND_AC,
        "actual_native_AC":sum(r["actual_native_AC_calls"] for r in rows),
        "num_native_AC_OPF_calls":0,
        "core_GAdapt_and_I29_evaluator_unchanged":True,
        "software":{"python":platform.python_version(),"numpy":np.__version__,
                    "scipy":scipy.__version__,"pandas":pd.__version__}
    },"runs":rows,"summary":summary,"paired_seed_contrasts":contrasts}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",default="iteration32_ieee14_robust.json")
    p.add_argument("--csv",default="iteration32_ieee14_robust.csv")
    a=p.parse_args()
    result=experiment()
    with open(a.json,"w",encoding="utf-8") as handle:
        json.dump(result,handle,sort_keys=True,indent=2,allow_nan=False)
    flat=[{k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v
           for k,v in row.items()} for row in result["runs"]]
    columns=list(dict.fromkeys(k for row in flat for k in row))
    with open(a.csv,"w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=columns)
        writer.writeheader()
        writer.writerows(flat)
    print("I32_SUMMARY",json.dumps(result["summary"],sort_keys=True,allow_nan=False),flush=True)
    print("I32_PAIRED",json.dumps(contrasts if False else result["paired_seed_contrasts"],sort_keys=True,allow_nan=False),flush=True)
    print("I32_METADATA",json.dumps(result["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
