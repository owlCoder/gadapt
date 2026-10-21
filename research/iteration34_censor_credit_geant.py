"""I34 in-core GAdapt censored-safe AOS benchmark on I33 original GÉANT routing.

New statistical series, NOT a new independent topology or empirical traffic set.
Uses existing I33 synthetic per-scenario PRICE CAP: not source physical safety.
"""
import argparse
import csv
import json
import math
import platform
import random
import time

import numpy as np
import scipy
import pandas as pd
from gadapt.ga import GA
from gadapt.operations.cost_finding.sequential_scenario_budget_cost import SequentialScenarioBudgetCost
from research.iteration33_geant_routing_budget import (
    GeantThreeRoutingScenarios, SCENARIOS, HYPOTHETICAL_CAP,
    paired as _old_paired, holm_adjust,
)

SEEDS=tuple(range(2300,2312))
METHODS=("legacy_fixed","ucb_objective_fixed","uniform_censor_safe_fixed",
         "ucb_censor_safe_fixed","ucb_scenario_full")
BUDGET=120
POPULATION=24
MAX_REAL_ROUTINGS=len(SEEDS)*len(METHODS)*BUDGET


class ObservedSequentialCost(SequentialScenarioBudgetCost):
    """Read-only, true counted LAST candidate event; no stale score cache.

    No physical measurement is performed in either operator-credit callback.
    """
    def __init__(self, route, mode):
        self.route=route
        self._current=[]
        self.last=None
        super().__init__(SCENARIOS,route.evaluate_scenario,
                         lambda:route.real_routing_calls,
                         budget=BUDGET,mode=mode,penalty=1e5)

    def _one_verified_physical_call(self,candidate,index):
        observed=super()._one_verified_physical_call(candidate,index)
        self._current.append((self.scenarios[index],
                              float(observed["normalized_violation"]) if observed["converged"]
                              else None))
        return observed

    def __call__(self,x):
        self._current=[]
        self.last=None
        before=self.calls
        score=super().__call__(x)
        measured=self.calls-before
        if len(self._current)!=measured:
            raise RuntimeError("I34 observation trace length != true simulator delta")
        if not measured:
            return score
        if any(v is None for _,v in self._current):
            status="numerically_unknown"
        elif measured==len(SCENARIOS) and all(v==0 for _,v in self._current):
            status="verified_feasible"
        elif any(v>0 for _,v in self._current):
            status="measured_infeasible"
        else:
            raise RuntimeError("I34 incomplete source scenarios cannot be called feasible")
        self.last={"vector":tuple(float(v) for v in x),
                   "counter_after":self.route.real_routing_calls,
                   "status":status,
                   "actual_calls":measured,
                   "observed_scenarios":[name for name,_ in self._current],
                   "observed_violations":[v for _,v in self._current]}
        return score

    def _last_only(self,values):
        if self.last is None:
            return None
        if (tuple(float(v) for v in values)!=self.last["vector"]
                or self.route.real_routing_calls!=self.last["counter_after"]):
            return None
        return self.last

    def censor_safe_cached_feedback(self,values,score):
        event=self._last_only(values)
        if event is None or event["status"]=="numerically_unknown":
            return None
        return {k:event[k] for k in (
            "status","actual_calls","observed_scenarios","observed_violations")}

    def full_scenario_cached_feedback(self,values,score):
        event=self._last_only(values)
        if event is None or event["actual_calls"]!=len(SCENARIOS) or event["status"]=="numerically_unknown":
            return None
        if set(event["observed_scenarios"])!=set(SCENARIOS):
            raise RuntimeError("I34 full scenario callback missing predeclared profile")
        pairs=dict(zip(event["observed_scenarios"],event["observed_violations"]))
        return [pairs[name] for name in SCENARIOS]


def run_one(method,seed):
    if method not in METHODS or seed not in SEEDS:
        raise ValueError("I34 pre-registered method/seed only")
    random.seed(seed)
    np.random.seed(seed)
    route=GeantThreeRoutingScenarios()  # strict original source SHA audit before routing
    evaluator=ObservedSequentialCost(route,"full" if method=="ucb_scenario_full" else "stop_fixed")
    settings={}
    if method=="ucb_objective_fixed":
        settings=dict(mutation_operator_policy="ucb",
                      mutation_operator_credit="objective")
    elif method in ("uniform_censor_safe_fixed","ucb_censor_safe_fixed"):
        settings=dict(
            mutation_operator_policy="uniform" if method.startswith("uniform") else "ucb",
            mutation_operator_credit="censored_verified_per_cost",
            mutation_scenario_count=len(SCENARIOS),
            mutation_violation_function=evaluator.censor_safe_cached_feedback,
            mutation_evaluation_counter=lambda:route.real_routing_calls)
    elif method=="ucb_scenario_full":
        settings=dict(mutation_operator_policy="ucb",
                      mutation_operator_credit="scenario_feasibility",
                      mutation_scenario_count=len(SCENARIOS),
                      mutation_violation_function=evaluator.full_scenario_cached_feedback,
                      mutation_evaluation_counter=lambda:route.real_routing_calls)
    ga=GA(cost_function=evaluator,population_size=POPULATION,
          cost_diversity_metric="log_relative",
          exit_check="generations",number_of_generations=128,
          exit_function=lambda:evaluator.remaining<len(SCENARIOS),
          population_mutation="cost_diversity,parent_diversity",
          timeout=240,**settings)
    for lo,hi in route.bounds:
        ga.add(float(lo),float(hi),1.)
    started=time.monotonic()
    succeeded=False
    fail_reason=""
    try:
        result=ga.execute()
        succeeded=bool(result.success)
        if not succeeded:
            fail_reason=str(result.messages)[:240]
    except Exception as exc:
        fail_reason=(type(exc).__name__+": "+str(exc))[:250]
    operator_stats=getattr(result,"operator_credit_summary",[]) if "result" in locals() else []
    q=evaluator.summary()
    actual=route.real_routing_calls
    if actual!=q["actual_native_AC_calls"] or actual>BUDGET or sum(q["actual_AC_per_scenario"])!=actual:
        raise RuntimeError("I34 genuine routing cost accounting inconsistent")
    if (method=="ucb_scenario_full" and
            (q["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"] or
             any(i!=actual//3 for i in q["actual_AC_per_scenario"]))):
        raise RuntimeError("Old I26 scenario credit must have full actual batches")
    if method in ("uniform_censor_safe_fixed","ucb_censor_safe_fixed"):
        if any(z["censor_safe_verified_feedback"]>q["verified_all_scenario_feasible_candidates"]*len(operator_stats)
               for z in operator_stats):
            raise RuntimeError("No operator may have more robust feedback than true verified cost trials")
        if any(z["censor_safe_verified_feedback"]<0 for z in operator_stats):
            raise RuntimeError("Negative verified reward count")
    return {"method":method,"seed":seed,
            "domain":"GÉANT source traffic with synthetic 145000 PRICE cap NOT physical safety",
            "real_evaluator":"Dijkstra+unsplittable module pricing; not AC",
            "optimization_success_is_not_hypothetical_domain_feasibility":succeeded,
            "optimizer_error_or_budget_termination":fail_reason,
            "wall_seconds":round(time.monotonic()-started,5),
            "total_rewarded_operator_selections":sum(a["rewarded"] for a in operator_stats),
            "total_operator_observations":sum(a["observations"] for a in operator_stats),
            "total_operator_selections":sum(a["selections"] for a in operator_stats),
            "total_withheld_operator_traces":sum(a["withheld_unpaid_credits"] for a in operator_stats)//max(1,len(operator_stats)),
            "operator_credit_summary":operator_stats,
            **q}


def paired(rows,a,b):
    aa={r["seed"]:r["verified_all_scenario_feasible_candidates"]>0 for r in rows if r["method"]==a}
    bb={r["seed"]:r["verified_all_scenario_feasible_candidates"]>0 for r in rows if r["method"]==b}
    if set(aa)!=set(SEEDS) or set(bb)!=set(SEEDS):raise RuntimeError("I34 missing paired seeds")
    both=sum(aa[s] and bb[s] for s in SEEDS)
    first=sum(aa[s] and not bb[s] for s in SEEDS)
    second=sum(not aa[s] and bb[s] for s in SEEDS)
    neither=sum(not aa[s] and not bb[s] for s in SEEDS)
    n=first+second
    p=(min(1.,2*sum(math.comb(n,k) for k in range(min(first,second)+1))/2**n)
       if n else 1.)
    return dict(first=a,second=b,both=both,first_only=first,second_only=second,
                neither=neither,exact_two_sided_p_unadjusted=p)


def experiment():
    if (SEEDS!=tuple(range(2300,2312)) or
            METHODS!=("legacy_fixed","ucb_objective_fixed","uniform_censor_safe_fixed",
                      "ucb_censor_safe_fixed","ucb_scenario_full") or
            BUDGET!=120 or POPULATION!=24 or
            MAX_REAL_ROUTINGS!=7200 or HYPOTHETICAL_CAP!=145000.):
        raise RuntimeError("I34 pre-registration drift")
    rows=[]
    for seed in SEEDS:
        for method in METHODS:
            r=run_one(method,seed)
            rows.append(r)
            print("I34_TRUE_ROUTE",json.dumps(r,sort_keys=True,allow_nan=False),flush=True)
    if len(rows)!=60:raise RuntimeError("I34 missing registered experiment")
    stats={}
    for method in METHODS:
        rr=[r for r in rows if r["method"]==method]
        costs=[r["best_verified_robust_mean_economic_cost_or_null"] for r in rr
               if r["best_verified_robust_mean_economic_cost_or_null"] is not None]
        stats[method]=dict(
            runs=len(rr),seed_success=len(costs),
            genuine_routing_calls=sum(r["actual_native_AC_calls"] for r in rr),
            verified_cap_feasible_candidates=sum(r["verified_all_scenario_feasible_candidates"] for r in rr),
            real_early_screened_candidates=sum(r["early_screened_physically_infeasible_candidates"] for r in rr),
            withheld_operator_feedback=sum(r["total_withheld_operator_traces"] for r in rr),
            real_complete_candidates=sum(r["completely_evaluated_candidates"] for r in rr),
            minimum_true_verified_mean_module_cost_or_null=min(costs) if costs else None,
            median_verified_mean_module_cost_only_successful_seed_or_null:
                float(np.median(costs)) if costs else None)
    comparisons=[
        ("ucb_censor_safe_fixed","legacy_fixed"),
        ("ucb_censor_safe_fixed","ucb_objective_fixed"),
        ("ucb_censor_safe_fixed","uniform_censor_safe_fixed"),
        ("ucb_censor_safe_fixed","ucb_scenario_full"),
        ("ucb_objective_fixed","legacy_fixed"),
    ]
    tests=[paired(rows,*c) for c in comparisons]
    adjusted=holm_adjust([q["exact_two_sided_p_unadjusted"] for q in tests])
    for q,p in zip(tests,adjusted):q["holm_five_p_adjusted"]=p
    return dict(metadata=dict(
        preregistered_protocol="research/ITERATION34_PROTOCOL.md",
        source_GÉANT_SHA256="ff316c23220ff4485deafcb8701d49c353db0c80072152df3ed9023ed4b4f4ff",
        non_source_hypothetical_cap=HYPOTHETICAL_CAP,
        not_independent_topology_or_real_telecom_validation=True,
        method_names=list(METHODS),seeds=list(SEEDS),registered_scenarios=list(SCENARIOS),
        max_true_dijkstra_module_evaluations=MAX_REAL_ROUTINGS,
        actual_true_dijkstra_module_evaluations=sum(r["actual_native_AC_calls"] for r in rows),
        actual_true_AC_electric_power_solve_calls=0,
        python=platform.python_version(),numpy=np.__version__,
        scipy=scipy.__version__,pandas=pd.__version__),
        runs=rows,summary=stats,paired_seed_contrasts=tests)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default="i34_geant_60_true_route_runs.json")
    parser.add_argument("--csv",default="i34_geant_60_true_route_runs.csv")
    args=parser.parse_args()
    out=experiment()
    with open(args.json,"w",encoding="utf8") as fd:
        json.dump(out,fd,sort_keys=True,indent=2,allow_nan=False)
    flat=[{k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v
           for k,v in r.items()} for r in out["runs"]]
    cols=list(dict.fromkeys(k for row in flat for k in row))
    with open(args.csv,"w",encoding="utf8",newline="") as fd:
        writer=csv.DictWriter(fd,fieldnames=cols)
        writer.writeheader()
        writer.writerows(flat)
    print("I34_SUMMARY",json.dumps(out["summary"],sort_keys=True,allow_nan=False),flush=True)
    print("I34_PAIRED",json.dumps(out["paired_seed_contrasts"],sort_keys=True,allow_nan=False),flush=True)
    print("I34_METADATA",json.dumps(out["metadata"],sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":main()
