"""I33 GÉANT real-domain scenario routing: true counted Dijkstra and module cost.

The feasibility constraint of 145000 SNDlib price units is a *NEW*
hypothetical engineering cap, not original SNDlib physical feasibility.
The same 36 routing weights are used in all three traffic scenarios;
modular investment is RECORSE/per-scenario, NOT fixed common deployment.
"""
import argparse
import copy
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
from gadapt.operations.cost_finding.sequential_scenario_budget_cost import SequentialScenarioBudgetCost
from research.iteration32_ieee14_topology_transfer import FullPaidFirstFailureScore
from research.geant_capacity import GeantCapacity, EXPECTED_SHA256
from scipy.optimize import differential_evolution

SCENARIOS=("nominal","odd_source_heavy","even_source_heavy")
METHODS=("ga_full_true","ga_full_censored","ga_stop_fixed","ga_stop_adaptive",
         "de_full_true","de_stop_fixed")
SEEDS=tuple(range(2200,2212))
BUDGET=120
POPULATION=24
HYPOTHETICAL_CAP=145000.
UPPER_BOUND_ROUTING_CALLS=6*12*120


def make_scenario_without_routing(base, profile):
    """Pure source-demand transformation; no Dijkstra, purchasing or solver."""
    if profile not in SCENARIOS:
        raise ValueError("I33 only accepts preregistered traffic scenario")
    nodes=tuple(sorted(base.graph.nodes))
    if len(nodes)!=22 or len(base.edges)!=36 or len(base.demands)!=462:
        raise RuntimeError("Original source GÉANT dimensions changed")
    odd={node:bool((i+1)%2) for i,node in enumerate(nodes)}
    demands=[]
    for source,dest,amount in base.demands:
        if source not in odd or dest not in odd or amount<0 or not math.isfinite(amount):
            raise ValueError("Invalid original GÉANT public demand")
        factor=(1. if profile=="nominal" else
                (1.08 if odd[source] else 0.92) if profile=="odd_source_heavy" else
                (0.92 if odd[source] else 1.08))
        demands.append((source,dest,float(amount)*factor))
    new=copy.copy(base)
    new.demands=demands
    return new


class GeantThreeRoutingScenarios:
    def __init__(self):
        base=GeantCapacity.download()
        if base.data_sha256!=EXPECTED_SHA256 or len(base.edges)!=36 or base.n!=36:
            raise RuntimeError("GÉANT source SHA/decision count mismatch")
        self.original=base
        self.scenario_cases={name:make_scenario_without_routing(base,name)
                             for name in SCENARIOS}
        self.bounds=list(base.bounds)
        self.real_routing_calls=0
        self.failures=[]
        self.n=base.n
        if len(self.bounds)!=36 or any(tuple(b)!=(1.,25.) for b in self.bounds):
            raise RuntimeError("Source integer OSPF bounds changed")

    def evaluate_scenario(self,vector,profile):
        if profile not in SCENARIOS:
            raise ValueError("Unregistered I33 GÉANT profile")
        x=np.asarray(vector,dtype=float)
        if (x.shape!=(self.n,) or not np.all(np.isfinite(x))
                or any(v<1.-1e-8 or v>25.+1e-8 or abs(v-round(v))>1e-6 for v in x)):
            raise ValueError("GÉANT candidate requires 36 real integer weights 1..25")
        converted=tuple(int(round(float(v))) for v in x)
        self.real_routing_calls+=1  # One REAL evaluation, even on exceptions.
        try:
            out=self.scenario_cases[profile].evaluate(converted)
            cost=float(out["cost"])
            if not math.isfinite(cost) or cost<0 or len(out["modules"])!=36:
                raise ValueError("Invalid original module investment cost/length")
            excess=max(0.,cost-HYPOTHETICAL_CAP)
            normalized=excess/HYPOTHETICAL_CAP
            return {"converged":True,"feasible":bool(excess==0.),
                    "original_economic_cost":cost,
                    "normalized_violation":normalized,
                    "hypothetical_module_budget_excess_price_units":excess,
                    "number_source_modules":int(sum(out["modules"])),
                    "max_modules_per_link":int(out["max_modules"]),
                    "max_nodal_mismatch_mva":None}
        except Exception as error:
            self.failures.append((self.real_routing_calls,profile,
                                  (type(error).__name__+": "+str(error))[:200]))
            return {"converged":False,"feasible":False,
                    "error":(type(error).__name__+": "+str(error))[:240]}


def make_cost(method,route):
    if method not in METHODS:
        raise ValueError("Unregistered I33 method")
    kw=dict(scenarios=SCENARIOS,scenario_evaluator=route.evaluate_scenario,
            physical_counter=lambda:route.real_routing_calls,
            budget=BUDGET,penalty=1e5)
    if method=="ga_full_censored":
        return FullPaidFirstFailureScore(**kw)
    mode=("stop_adaptive" if method=="ga_stop_adaptive" else
          "stop_fixed" if method.endswith("stop_fixed") else "full")
    return SequentialScenarioBudgetCost(**kw,mode=mode)


def run_one(method,seed):
    if method not in METHODS or seed not in SEEDS:
        raise ValueError("I33 method/seed preregistration drift")
    random.seed(seed)
    np.random.seed(seed)
    route=GeantThreeRoutingScenarios()
    ev=make_cost(method,route)
    started=time.monotonic()
    success=False
    exception=""
    try:
        if method.startswith("ga_"):
            ga=GA(cost_function=ev,population_size=POPULATION,
                  cost_diversity_metric="log_relative",
                  exit_check="generations",number_of_generations=128,
                  exit_function=lambda:ev.remaining<3,
                  population_mutation="cost_diversity,parent_diversity",
                  timeout=240)
            for lo,hi in route.bounds:
                ga.add(lo,hi,1.)
            result=ga.execute()
            success=bool(result.success)
            if not success:
                exception=str(result.messages)[:250]
        else:
            result=differential_evolution(
                ev,route.bounds,popsize=5,maxiter=12,tol=0.,atol=0.,
                polish=False,seed=seed,updating="immediate",
                integrality=[True]*route.n)
            success=bool(result.success)
            if not success:
                exception=str(result.message)[:250]
    except Exception as error:
        exception=(type(error).__name__+": "+str(error))[:250]
    q=ev.summary()
    n=route.real_routing_calls
    if (n!=q["actual_native_AC_calls"] or n>BUDGET
            or sum(q["actual_AC_per_scenario"])!=n
            or q["verified_all_scenario_feasible_candidates"]>
               q["completely_evaluated_candidates"]):
        raise RuntimeError("I33 true routing boundary or robust certificate mismatch")
    if method in ("ga_full_true","ga_full_censored","de_full_true"):
        if (n%3 or q["actual_AC_per_scenario"]!=[n//3]*3
                or q["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"]):
            raise RuntimeError("I33 full paid control skipped real demand routing")
    return {"seed":int(seed),"method":method,
            "domain":"GÉANT_22node_36edge_SNDlib_hypothetical_cap_recourse",
            "source_cap_is_NOT_SNDlib_physical":True,
            "real_simulator_kind":"networkx_dijkstra_462_demands_plus_source_module_pricing",
            "optimizer_reported_success_not_domain_budget_feasible":success,
            "optimizer_stop_message":exception,
            "wall_seconds":round(time.monotonic()-started,4),
            "real_routing_exceptions":route.failures[:10],
            **q}


def paired(rows,a,b):
    x={r["seed"]:r["verified_all_scenario_feasible_candidates"]>0
       for r in rows if r["method"]==a}
    y={r["seed"]:r["verified_all_scenario_feasible_candidates"]>0
       for r in rows if r["method"]==b}
    if set(x)!=set(SEEDS) or set(y)!=set(SEEDS):
        raise RuntimeError("Missing I33 paired observation")
    aa=sum(x[i] and y[i] for i in SEEDS)
    ab=sum(x[i] and not y[i] for i in SEEDS)
    ba=sum(not x[i] and y[i] for i in SEEDS)
    bb=sum(not x[i] and not y[i] for i in SEEDS)
    n=ab+ba
    p=(min(1.,2*sum(math.comb(n,k) for k in range(min(ab,ba)+1))/2**n)
       if n else 1.)
    return {"first":a,"second":b,"both":aa,
            "first_only":ab,"second_only":ba,"neither":bb,
            "exact_two_sided_discordant_binomial_p_unadjusted":p}


def holm_adjust(p_values):
    """Step-down familywise correction of preregistered five comparisons."""
    m=len(p_values)
    ordered=sorted(range(m),key=lambda i:(p_values[i],i))
    adjusted=[None]*m
    previous=0.
    for rank,index in enumerate(ordered):
        previous=max(previous,min(1.,(m-rank)*p_values[index]))
        adjusted[index]=previous
    return adjusted


def experiment():
    if (SCENARIOS!=("nominal","odd_source_heavy","even_source_heavy")
            or METHODS!=("ga_full_true","ga_full_censored","ga_stop_fixed",
                "ga_stop_adaptive","de_full_true","de_stop_fixed")
            or SEEDS!=tuple(range(2200,2212)) or BUDGET!=120
            or POPULATION!=24 or HYPOTHETICAL_CAP!=145000.
            or UPPER_BOUND_ROUTING_CALLS!=8640):
        raise RuntimeError("I33 preregistration changed")
    rows=[]
    for seed in SEEDS:
        for method in METHODS:
            row=run_one(method,seed)
            rows.append(row)
            print("I33_TRUE_ROUTE",json.dumps(row,sort_keys=True,allow_nan=False),flush=True)
    if len(rows)!=72:
        raise RuntimeError("Missing I33 physical routing experiment")
    summary={}
    for method in METHODS:
        subset=[r for r in rows if r["method"]==method]
        prices=[r["best_verified_robust_mean_economic_cost_or_null"]
                for r in subset
                if r["best_verified_robust_mean_economic_cost_or_null"] is not None]
        summary[method]={
            "runs":len(subset),
            "seeds_with_all_three_hypothetical_budget_feasible":len(prices),
            "actual_Dijkstra_module_routing_evaluations":sum(r["actual_native_AC_calls"] for r in subset),
            "fully_paid_three_scenario_candidates":sum(r["completely_evaluated_candidates"] for r in subset),
            "all_three_verified_hypothetically_feasible_candidates":sum(
                 r["verified_all_scenario_feasible_candidates"] for r in subset),
            "proven_hypothetical_budget_rejects":sum(
                 r["early_screened_physically_infeasible_candidates"] for r in subset),
            "numerically_unknown_candidates":sum(
                 r["numerically_unknown_candidates"] for r in subset),
            "unobserved_never_routed_scenarios":sum(
                 r["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"] for r in subset),
            "optimizer_objective_requests_not_physical_measurements":sum(
                 r["objective_requests"] for r in subset),
            "best_true_recoursed_module_mean_cost_verified_only_or_null":min(prices) if prices else None,
            "median_true_recoursed_module_mean_cost_conditional_on_success_or_null":
                 statistics.median(prices) if prices else None,
        }
    tests=[paired(rows,*pair) for pair in (
        ("ga_full_true","ga_full_censored"),
        ("ga_full_censored","ga_stop_fixed"),
        ("ga_stop_fixed","ga_stop_adaptive"),
        ("ga_stop_fixed","de_stop_fixed"),
        ("ga_full_true","de_full_true"),
    )]
    holm=holm_adjust([x["exact_two_sided_discordant_binomial_p_unadjusted"] for x in tests])
    for item,adj in zip(tests,holm):
        item["holm_five_contrasts_p_adjusted"]=adj
    return {"metadata":{
        "preregistration":"research/ITERATION33_PROTOCOL.md",
        "model_audit":"research/ITERATION33_GEANT_MODEL_AUDIT_SR.md",
        "source_SNDlib_GEANT_sha256":EXPECTED_SHA256,
        "original_network":"22 nodes, 36 links, 462 directed demands",
        "scenarios":list(SCENARIOS),"methods":list(METHODS),"seeds":list(SEEDS),
        "hypothetical_price_cap_per_scenario":HYPOTHETICAL_CAP,
        "source_original_capacity_constraint_is_NOT_145000":True,
        "recourse_three_scenario_mean_cost_not_common_robust_installation":True,
        "max_real_routing_evaluations":UPPER_BOUND_ROUTING_CALLS,
        "actual_real_routing_evaluations":sum(x["actual_native_AC_calls"] for x in rows),
        "real_AC_physics_calls":0,
        "prior_art_scenario_racing_not_novel":True,
        "same_previously_used_GÉANT_topology_not_blind_new_industry":True,
        "python":platform.python_version(),"numpy":np.__version__,
        "scipy":scipy.__version__,"pandas":pd.__version__
    },"runs":rows,"summary":summary,"paired_seed_contrasts":tests}


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--json",default="iteration33_geant_three_scenarios.json")
    a.add_argument("--csv",default="iteration33_geant_three_scenarios.csv")
    args=a.parse_args()
    out=experiment()
    with open(args.json,"w",encoding="utf-8") as dest:
        json.dump(out,dest,sort_keys=True,indent=2,allow_nan=False)
    flattened=[{k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v
                for k,v in r.items()} for r in out["runs"]]
    columns=list(dict.fromkeys(key for r in flattened for key in r))
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader()
        writer.writerows(flattened)
    print("I33_SUMMARY",json.dumps(out["summary"],sort_keys=True,allow_nan=False),flush=True)
    print("I33_PAIRED",json.dumps(out["paired_seed_contrasts"],sort_keys=True,allow_nan=False),flush=True)
    print("I33_METADATA",json.dumps(out["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
