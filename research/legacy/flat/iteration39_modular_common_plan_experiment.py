"""I39 preregistered original GAdapt versus MILP on SNDlib modular common capacity."""
import argparse
import json
import os
import platform
import time

import numpy as np
import scipy
from research.iteration38_joint_capacity_experiment import source_data_gate, ga_run
from research.iteration39_source_modular_capacity import (
    NETWORK_SHA, ARCHIVE_SHA, ModularCommonPlan, exact_modular_milp)

SEEDS=tuple(range(3900,3912))
TRAIN,HOLDOUT=192,96
BUDGET=360


def experiment(out_file,manifest_file):
    if SEEDS!=tuple(range(3900,3912)) or TRAIN!=192 or HOLDOUT!=96 or BUDGET!=360:
        raise RuntimeError("I39 preregistration drift")
    nodes,links,pairs,q,meta=source_data_gate()
    if (meta["source_network"]["sha256"]!=NETWORK_SHA or
            meta["source_matrices"]["sha256"]!=ARCHIVE_SHA or
            len(pairs)!=272 or q.shape!=(288,272)):
        raise RuntimeError("I39 original source SHA/matrix geometry mismatch")
    os.makedirs(os.path.dirname(os.path.abspath(out_file)),exist_ok=True)
    with open(manifest_file,"w",encoding="utf8") as f:
        json.dump(meta,f,sort_keys=True,indent=2,allow_nan=False)
    model=ModularCommonPlan(nodes,links,pairs,q[:TRAIN]) # strict source-module proof before solver
    print("I39_MODULE_EQUIVALENCE_CERT",json.dumps({
        "edges_verified":len(model.module_prices),
        "original_modules_per_link":40,
        "primitive_capacity_types":[20,40],
        "native_network_SHA256":NETWORK_SHA,
        "source_temporal_SHA256":ARCHIVE_SHA,
        "no_new_traffic_or_price_cap":True}),flush=True)
    baseline=model.evaluate(np.zeros(model.n,dtype=int))
    base_holdout=model.validate_plan(
        np.zeros(model.n,dtype=int),baseline["installed_capacity"],q[TRAIN:])
    t=time.monotonic()
    reference=exact_modular_milp(model,seconds=180.)
    reference["wall_seconds"]=round(time.monotonic()-t,5)
    if reference["incumbent"] is not None:
        reference["holdout"]=model.validate_plan(
            reference["incumbent"]["choices"],
            reference["incumbent"]["installed_capacity"],q[TRAIN:])
    print("I39_MILP",json.dumps({k:v for k,v in reference.items() if k!="incumbent"},
                                sort_keys=True,allow_nan=False),flush=True)
    runs=[]
    for seed in SEEDS:
        r=ga_run(model,seed)
        b=r["best_train_feasible_common_plan"]
        if b is not None:
            direct=model.evaluate(b["choices"])
            if (not direct["feasible"] or abs(direct["cost"]-b["cost"])>1e-6 or
                    direct["worst_excess"]>1e-6):
                raise RuntimeError("I39 independent training plan re-verification failed")
            r["holdout"]=model.validate_plan(b["choices"],
                    b["installed_capacity"],q[TRAIN:])
            lb=reference["dual_bound"]
            r["cost_excess_vs_milp_verified_dual_lower_bound"]=(
                b["cost"]-lb if lb is not None else None)
            r["relative_upper_bound_on_gap_to_optimum"]=(
                (b["cost"]-lb)/max(1.,abs(lb)) if lb is not None else None)
        else:
            r["holdout"]=None
        runs.append(r)
        print("I39_REAL_GADAPT",json.dumps(r,sort_keys=True,allow_nan=False),flush=True)
    if len(runs)!=12 or len(set(r["seed"] for r in runs))!=12 or any(
            r["actual_full_train_panel_evaluations"]>360 for r in runs):
        raise RuntimeError("I39 frozen seeds and real source evaluation accounting failed")
    output=dict(protocol="research/ITERATION39_PROTOCOL.md",
                actual_original_GAdapt_core=True,
                physical_model_scope="historical SNDlib source demand, shared undirected capacity; assumed 1 module unit=1 Mbit/s; NOT present-day DFN hardware validation",
                source_data=meta,
                module_menu_equivalence="all 26 x 40 source options checked exactly against unlimited source 20/40 modular pair",
                numpy=np.__version__,scipy=scipy.__version__,python=platform.python_version(),
                baseline_all_first_paths=baseline,baseline_holdout=base_holdout,
                milp=reference,ga= runs,
                true_full_train_panel_evaluations=sum(
                    r["actual_full_train_panel_evaluations"] for r in runs))
    with open(out_file,"w",encoding="utf8") as f:
        json.dump(output,f,sort_keys=True,indent=2,allow_nan=False)
    print("I39_DONE",json.dumps(dict(
        real_ga_runs=len(runs),
        actual_whole_train_panel_evaluations=output["true_full_train_panel_evaluations"],
        milp_status=reference["status"],
        milp_incumbent_source_cost=(
            reference["incumbent"]["cost"] if reference["incumbent"] else None),
        milp_valid_dual_lower_bound=reference["dual_bound"],
        shortest_path_source_cost=baseline["cost"],
        ga_best_source_cost=min((r["best_train_feasible_common_plan"]["cost"]
                         for r in runs if r["best_train_feasible_common_plan"] is not None),
                        default=None),
        holdout_ga_feasible_seeds=sum(bool(r["holdout"]) and
                                     r["holdout"]["all_snapshots_feasible"] for r in runs)
    ),allow_nan=False),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--json",required=True)
    p.add_argument("--manifest",required=True)
    a=p.parse_args()
    experiment(a.json,a.manifest)
