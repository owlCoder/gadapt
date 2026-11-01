"""Iteration 19: ten preregistered genuine IEEE118 AC PF forensic replays.

Replay one exact source baseline and the nine archived best-PENALIZED I18
candidates (all nine were infeasible). Report original bus voltage,
individual generator P/Q and branch both-terminal RATE_A offenders.
NOT optimization. NOT a new GAdapt mechanism. NOT a full AC-OPF solution.
"""
import argparse
import csv
import json
import math
import platform

import numpy as np
import pandas as pd
import scipy

from pypower.idx_bus import VM, VMIN, VMAX
from pypower.idx_gen import GEN_BUS, GEN_STATUS, PG, QG, PMIN, PMAX, QMIN, QMAX, VG
from pypower.idx_brch import BR_STATUS, RATE_A, PF, QF, PT, QT
from pypower.runpf import runpf

from research.iteration18_ieee118_gadapt_transfer import (
    IEEE118NineControlSubset, physics_118, EXPECTED_SELECTED, EXPECTED_SLACK,
)
from research.iteration17_ieee14_gadapt_economic_pf import METHODS, SEEDS

ARCHIVE="research/results/ieee118_iteration18_real_gadapt_de_random_20261021.json"
SCORE_REPLAY_TOL=0.001


def source_vectors_and_preflight(path=ARCHIVE):
    with open(path, encoding="utf-8") as f:
        saved=json.load(f)
    metadata=saved["metadata"]
    if (metadata["true_ac_pf_calls"]!=864 or
        metadata["budget_true_ac_pf_per_seed_method"]!=96 or
        metadata["controlled_original_pg_gen_indices_zero_based"]!=list(EXPECTED_SELECTED) or
        metadata["controlled_original_vg_gen_indices_zero_based"]!=[EXPECTED_SLACK,*EXPECTED_SELECTED]):
        raise ValueError("I18 archived physics, controls or budget changed")
    rows=saved["runs"]
    if len(rows)!=9:
        raise ValueError("Exactly nine I18 best-penalized candidates required")
    mapping={}
    model=IEEE118NineControlSubset()
    for item in rows:
        pair=(item["seed"],item["method"])
        if (pair in mapping or pair[0] not in SEEDS or pair[1] not in METHODS or
            item["real_ac_pf_calls"]!=96 or item["feasible_real_ac_candidates"]!=0 or
            item["best_feasible_economic_cost"] is not None):
            raise ValueError("Unexpected/incomplete I18 candidate")
        x=np.asarray(item["best_penalized_vector"],float)
        if x.shape!=(9,) or not np.all(np.isfinite(x)):
            raise ValueError("Invalid archived 9D vector")
        if any(xv<lo-1e-8 or xv>hi+1e-8 for xv,(lo,hi) in zip(x,model.bounds)):
            raise ValueError("I18 archived vector outside source boundaries")
        original_score=float(item["best_penalized_ac_score"])
        if not math.isfinite(original_score):
            raise ValueError("Nonfinite archived penalized score")
        mapping[pair]=(x,original_score)
    expected={(seed,method) for seed in SEEDS for method in METHODS}
    if set(mapping)!=expected:
        raise ValueError("Missing/extra I18 paired seed-method combination")
    original_gen=model.source["gen"]
    baseline=np.array([original_gen[i,PG] for i in EXPECTED_SELECTED]+
        [original_gen[i,VG] for i in [EXPECTED_SLACK,*EXPECTED_SELECTED]],dtype=float)
    if baseline.shape!=(9,) or not np.all(np.isfinite(baseline)):
        raise ValueError("Original generator PG/VG baseline invalid")
    return baseline, mapping


def top_generator_violations(solved_gen, source_gen, kind, top_n=12, tol=1e-3):
    if kind not in ("P","Q"):
        raise ValueError("P or Q expected")
    idx=(PG,PMIN,PMAX) if kind=="P" else (QG,QMIN,QMAX)
    val,lo,hi=idx
    observed=np.asarray(solved_gen,float)
    origin=np.asarray(source_gen,float)
    if observed.shape[0]!=54 or origin.shape[0]!=54:
        raise ValueError("IEEE118 generator matrix size mismatch")
    items=[]
    for j in range(54):
        if origin[j,GEN_STATUS]<=0:
            continue
        q=float(observed[j,val])
        low=float(origin[j,lo]);high=float(origin[j,hi])
        below=max(0.,low-q)
        above=max(0.,q-high)
        if max(below,above)>tol:
            items.append({
                "generator_row_1based":j+1,
                "bus_id":int(origin[j,GEN_BUS]),
                "value_mw_or_mvar":q,
                "source_min":low,"source_max":high,
                "below":below,"above":above,
                "total_excess":below+above,
            })
    items.sort(key=lambda x:(-x["total_excess"],x["generator_row_1based"]))
    return {"count":len(items),
            "below_count":sum(x["below"]>tol for x in items),
            "above_count":sum(x["above"]>tol for x in items),
            "total_excess":sum(x["total_excess"] for x in items),
            "max_excess":items[0]["total_excess"] if items else 0.,
            "top_12":items[:top_n]}


def top_voltage_violations(solved_bus, source_bus, tol=1e-5,top_n=12):
    bus=np.asarray(solved_bus,float);source=np.asarray(source_bus,float)
    if len(bus)!=118 or len(source)!=118 or not np.array_equal(
            bus[:,0].astype(int),source[:,0].astype(int)):
        raise ValueError("Original IEEE118 bus source IDs changed")
    entries=[]
    for i in range(len(bus)):
        observed=float(bus[i,VM])
        lo=float(source[i,VMIN]);hi=float(source[i,VMAX])
        below=max(lo-observed,0.)
        above=max(observed-hi,0.)
        if max(below,above)>tol:
            entries.append({"bus_id":int(source[i,0]),
                "vm_pu":observed,"source_vmin_pu":lo,"source_vmax_pu":hi,
                "below_pu":below,"above_pu":above,"total_excess_pu":below+above})
    entries.sort(key=lambda z:(-z["total_excess_pu"],z["bus_id"]))
    return {"count":len(entries),
            "below_count":sum(x["below_pu"]>tol for x in entries),
            "above_count":sum(x["above_pu"]>tol for x in entries),
            "total_excess_pu":sum(x["total_excess_pu"] for x in entries),
            "max_excess_pu":entries[0]["total_excess_pu"] if entries else 0.,
            "top_12":entries[:top_n]}


def branch_terminal_source_limits(solved_br, source_br, tol=1e-3):
    flow=np.asarray(solved_br,float);br=np.asarray(source_br,float)
    if len(flow)!=186 or len(br)!=186 or flow.shape[1]<17:
        raise ValueError("Incomplete original source branch flow result")
    if not np.array_equal(flow[:,:2].astype(int),br[:,:2].astype(int)):
        raise ValueError("IEEE118 branch source row identity mismatch")
    active=(br[:,BR_STATUS]>0)
    rated=active & (br[:,RATE_A]>0)
    s_from=np.hypot(flow[:,PF],flow[:,QF])
    s_to=np.hypot(flow[:,PT],flow[:,QT])
    excess=np.zeros(len(br),float)
    excess[rated]=np.maximum(np.maximum(s_from[rated],s_to[rated])-
                             br[rated,RATE_A],0.)
    offender=[]
    for i in np.flatnonzero(rated & (excess>tol)):
        offender.append({"branch_row_1based":int(i)+1,
            "from_bus":int(br[i,0]),"to_bus":int(br[i,1]),
            "rating_mva":float(br[i,RATE_A]),
            "from_mva":float(s_from[i]),"to_mva":float(s_to[i]),
            "excess_mva":float(excess[i])})
    offender.sort(key=lambda z:(-z["excess_mva"],z["branch_row_1based"]))
    return {
        "rated_active_branches":int(np.count_nonzero(rated)),
        "unrated_active_branches":int(np.count_nonzero(active & (br[:,RATE_A]==0))),
        "violated_branches":len(offender),
        "total_excess_mva":float(np.sum(excess)),
        "maximum_excess_mva":float(np.max(excess,initial=0.)),
        "top_12":offender[:12],
    }


def source_detail(solved,source):
    physical=physics_118(solved,source)
    gen=solved["gen"]
    slack=int(EXPECTED_SLACK)
    p=top_generator_violations(gen,source["gen"],"P")
    q=top_generator_violations(gen,source["gen"],"Q")
    v=top_voltage_violations(solved["bus"],source["bus"])
    t=branch_terminal_source_limits(solved["branch"],source["branch"])
    return {"physical":physical,
            "generator_p_mw":p,"generator_q_mvar":q,
            "bus_voltage_pu":v,"branch_rated_mva":t,
            "original_slack_generator_row_1based":slack+1,
            "original_slack_bus_id":int(source["gen"][slack,GEN_BUS]),
            "slack_pg_mw":float(gen[slack,PG]),
            "slack_qg_mvar":float(gen[slack,QG])}


def execute_diagnostics(path=ARCHIVE):
    baseline,replays=source_vectors_and_preflight(path)
    models=[("original_source_initial_pg_vg",None,None,baseline,None)]
    for seed in SEEDS:
        for method in METHODS:
            v,score=replays[(seed,method)]
            models.append(("archived_best_penalized_i18",seed,method,v,score))
    if len(models)!=10:
        raise ValueError("Exactly ten preregistered real AC replay states")
    rows=[]
    calls=0
    for label,seed,method,x,score in models:
        grid=IEEE118NineControlSubset()
        case={key:(value.copy() if isinstance(value,np.ndarray) else value)
              for key,value in grid.source.items()}
        for gen_idx,pg in zip(grid.non_slack_gen_ids,x[:4]):
            case["gen"][gen_idx,PG]=float(pg)
        for gen_idx,vg in zip(grid.all_gen_ids,x[4:]):
            case["gen"][gen_idx,VG]=float(vg)
        entry={"kind":label,"seed":seed,"method":method,
            "source_nine_control_vector":list(map(float,x)),
            "archived_i18_best_penalized_score":score,
            "actual_ac_call":calls+1,"converged":False,
            "error":"","details":None,"replay_score_diff":None,
            "replay_matches_archived_score":None}
        calls+=1  # INCREMENT at actual direct PYPOWER runpf boundary, even exception.
        try:
            solved,success=runpf(case,grid.settings)
            entry["converged"]=bool(success)
            if not success:
                entry["error"]="PYPOWER runpf returned success=False"
            else:
                entry["details"]=source_detail(solved,grid.source)
                if score is not None:
                    diff=abs(float(entry["details"]["physical"]["penalized_objective"])-score)
                    entry["replay_score_diff"]=float(diff)
                    entry["replay_matches_archived_score"]=bool(diff<=SCORE_REPLAY_TOL)
        except Exception as error:
            entry["error"]=(type(error).__name__+": "+str(error))[:300]
        rows.append(entry)
        print("I19_REAL_AC",json.dumps(entry,allow_nan=False,sort_keys=True),flush=True)
    return {"metadata":{
        "status":"completed_source_IEEE118_10_AC_forensic_replay",
        "protocol":"research/ITERATION19_PROTOCOL.md",
        "input_archive":path,
        "preregistered_actual_ac_pf_calls":10,
        "actual_ac_pf_calls":calls,
        "new_ac_opf_calls":0,
        "optimizer_method_executions":0,
        "source":"unaltered PYPOWER IEEE118, 9D PG/VG controls from I18",
        "archive_i18_physical_calls_not_recounted":864,
        "source_initial_state_not_an_optimizer_incumbent":True,
        "software":{"python":platform.python_version(),
                    "scipy":scipy.__version__,"pandas":pd.__version__},
        "no_gadapt_algorithm_change":True,
        "source_is_public_not_industrial_utility_data":True},
        "states":rows}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",default=ARCHIVE)
    parser.add_argument("--json",default="iteration19_ieee118_forensic.json")
    parser.add_argument("--csv",default="iteration19_ieee118_forensic.csv")
    args=parser.parse_args()
    result=execute_diagnostics(args.input)
    with open(args.json,"w",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
    fields=("kind","seed","method","actual_ac_call","converged","error",
        "archived_i18_best_penalized_score","replay_matches_archived_score",
        "replay_score_diff","physically_feasible","actual_cost_not_valid_opf",
        "p_violations","p_total_excess_mw","q_violations","q_total_excess_mvar",
        "voltage_violations","voltage_total_excess_pu",
        "thermal_rated_violations","thermal_total_excess_mva",
        "max_ac_balance_error_mva","slack_pg_mw","slack_qg_mvar")
    with open(args.csv,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for x in result["states"]:
            d=x["details"]
            row={"kind":x["kind"],"seed":x["seed"],"method":x["method"],
                "actual_ac_call":x["actual_ac_call"],
                "converged":x["converged"],"error":x["error"],
                "archived_i18_best_penalized_score":x["archived_i18_best_penalized_score"],
                "replay_matches_archived_score":x["replay_matches_archived_score"],
                "replay_score_diff":x["replay_score_diff"]}
            if d is not None:
                row.update(physically_feasible=d["physical"]["feasible"],
                    actual_cost_not_valid_opf=d["physical"]["actual_economic_cost"],
                    p_violations=d["generator_p_mw"]["count"],
                    p_total_excess_mw=d["generator_p_mw"]["total_excess"],
                    q_violations=d["generator_q_mvar"]["count"],
                    q_total_excess_mvar=d["generator_q_mvar"]["total_excess"],
                    voltage_violations=d["bus_voltage_pu"]["count"],
                    voltage_total_excess_pu=d["bus_voltage_pu"]["total_excess_pu"],
                    thermal_rated_violations=d["branch_rated_mva"]["violated_branches"],
                    thermal_total_excess_mva=d["branch_rated_mva"]["total_excess_mva"],
                    max_ac_balance_error_mva=d["physical"]["max_nodal_mismatch_mva"],
                    slack_pg_mw=d["slack_pg_mw"],
                    slack_qg_mvar=d["slack_qg_mvar"])
            w.writerow(row)
    print("I19_SUMMARY",json.dumps(result["metadata"],sort_keys=True),flush=True)


if __name__=="__main__":
    main()
