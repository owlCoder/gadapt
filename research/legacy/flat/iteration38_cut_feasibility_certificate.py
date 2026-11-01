"""I38 post-result forensic: source-data node-cut capacity infeasibility certificate.

NO solver/GAdapt evaluation, NO modification of the preregistered model.
If a cut violates sum_d demand_crossing <= sum_e maximal installed edge
capacity, no routing scheme whatsoever can satisfy the common-plan model,
even a fully splittable route, for that snapshot and that chosen edge model.
This is a necessary condition, not a sufficient feasibility test.
"""
import argparse
import itertools
import json
import math
import os
from research.iteration38_joint_capacity_experiment import source_data_gate, TRAIN


def cut_witness(nodes, links, pairs, traffic, max_side=3):
    """All node cuts with 1..max_side nodes. Deterministic, source link rules."""
    index = list(nodes)
    bound = {e.name: e.base + max(cap for cap, price in e.options)
             for e in links}
    data = []
    for side_size in range(1, min(max_side, len(index)//2)+1):
        for side in itertools.combinations(index, side_size):
            chosen = set(side)
            crossing = [d for d, (a, b) in enumerate(pairs) if (a in chosen)!=(b in chosen)]
            cap = sum(bound[e.name] for e in links
                      if (e.u in chosen)!=(e.v in chosen))
            if not crossing:
                continue
            cut_flow = traffic[:, crossing].sum(axis=1)
            worst_t = int(cut_flow.argmax())
            peak = float(cut_flow[worst_t])
            excess = peak-cap
            if excess > 1e-7:
                data.append(dict(
                    side=list(side), split_node_count=side_size,
                    first_witness_time=worst_t, peak_crossing_demand=peak,
                    maximum_possible_installed_cut_capacity=float(cap),
                    mathematically_necessary_shortfall=float(excess),
                    violated_time_count=int((cut_flow>cap+1e-7).sum())))
    data.sort(key=lambda a:(-a["mathematically_necessary_shortfall"],
                            a["split_node_count"],a["side"]))
    return data


def main(dest):
    nodes, links, pairs, q, meta = source_data_gate()
    train = cut_witness(nodes, links, pairs, q[:TRAIN], 3)
    holdout = cut_witness(nodes, links, pairs, q[TRAIN:], 3)
    out = dict(
        analysis="post-I38 source-data-only necessary cut feasibility theorem",
        uses_no_GAdapt_no_MILP_no_true_network_routing_calls=True,
        source_sha256=meta["source_network"]["sha256"],
        matrix_sha256=meta["source_matrices"]["sha256"],
        model="max ONE capacity option from each original SNDlib edge list",
        link_direction="shared UNDIRECTED installed capacity; both directed demands SUM",
        training_violating_cuts=len(train),
        training_largest_witnesses=train[:25],
        holdout_violating_cuts=len(holdout),
        holdout_largest_witnesses=holdout[:25],
        note=("A nonempty training witness proves the I38 common-plan model "
              "infeasible for ANY routing, not just its two shortest paths. "
              "Empty witness does not prove MILP feasibility."),
    )
    os.makedirs(os.path.dirname(os.path.abspath(dest)),exist_ok=True)
    with open(dest,"w",encoding="utf-8") as f:
        json.dump(out,f,indent=2,sort_keys=True,allow_nan=False)
    print("I38_CUT_CERT",json.dumps({
        "training_violating_cuts":len(train),
        "holdout_violating_cuts":len(holdout),
        "strongest_train":train[0] if train else None,
        "strongest_holdout":holdout[0] if holdout else None
    },sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--json",required=True)
    main(p.parse_args().json)
