"""Static RTE1888 topology/control audit; ZERO AC evaluations.

Consumes versioned pre-optimization observations; selects eligible controls
by frozen distance/headroom rule, NOT by measured future performance.
"""
import argparse
from collections import defaultdict, deque
import json
import math

import pandas as pd
import pandapower.networks as pn


def active(df):
    return df if "in_service" not in df else df[df["in_service"].fillna(False).astype(bool)]


def connect(net):
    adj=defaultdict(set)
    for u,v in zip(active(net.line)["from_bus"], active(net.line)["to_bus"]):
        adj[int(u)].add(int(v));adj[int(v)].add(int(u))
    for u,v in zip(active(net.trafo)["hv_bus"], active(net.trafo)["lv_bus"]):
        adj[int(u)].add(int(v));adj[int(v)].add(int(u))
    return adj


def distances(adj, starts):
    ds={int(s):0 for s in starts}
    todo=deque(ds)
    while todo:
        at=todo.popleft()
        for nxt in adj[at]:
            if nxt not in ds:
                ds[nxt]=ds[at]+1
                todo.append(nxt)
    return ds


def bus_summary(net, bus, adj):
    gr=active(net.gen)
    sg=active(net.sgen)
    load=active(net.load)
    sh=active(net.shunt)
    gids=gr[gr.bus==bus]
    sgs=sg[sg.bus==bus]
    loads=load[load.bus==bus]
    shunts=sh[sh.bus==bus]
    gdata=[]
    for idx,row in gids.iterrows():
        gdata.append({"gen_id":int(idx),"scheduled_p_mw":float(row.p_mw),
                      "min_p_mw":float(row.min_p_mw) if pd.notna(row.get("min_p_mw")) else None,
                      "max_p_mw":float(row.max_p_mw) if pd.notna(row.get("max_p_mw")) else None})
    return {"bus":int(bus),"series_degree":len(adj[bus]),
            "gen":gdata, "n_sgen":len(sgs),"n_load":len(loads),"n_shunt":len(shunts),
            "scheduled_gen_p_mw":float(gids.p_mw.sum()),
            "scheduled_sgen_p_mw":float(sgs.p_mw.sum()),
            "scheduled_load_p_mw":float(loads.p_mw.sum()),
            "scheduled_shunt_p_mw":float(shunts.p_mw.sum()),
            "ext_grid_at_bus":bool((active(net.ext_grid).bus==bus).any())}


def analyze(input_file):
    audit=json.loads(open(input_file,encoding="utf8").read())
    offenders=audit["loads"]["1.0"]["reference_top_thermal_offenders"]
    net=pn.case1888rte()
    adj=connect(net)
    buses=set()
    items=[]
    for row in offenders:
        a,b=int(row["from_bus"]),int(row["to_bus"])
        buses.update((a,b))
        items.append({"element_id":row["element_id"],
                      "loading_percent":row["loading_percent"],
                      "sn_mva":row.get("sn_mva"),
                      "high":bus_summary(net,a,adj),
                      "low":bus_summary(net,b,adj)})
    ds=distances(adj,buses)
    selected=[]
    eligible=[]
    for i,row in active(net.gen).iterrows():
        p=float(row.p_mw)
        minimum=row.get("min_p_mw")
        maximum=row.get("max_p_mw")
        if not all(pd.notna(z) and math.isfinite(float(z)) for z in (p,minimum,maximum)):
            continue
        minimum,maximum=float(minimum),float(maximum)
        if not minimum<=p<=maximum or not maximum>minimum or p-minimum<5.:
            continue
        bus=int(row.bus)
        eligible.append({"gen_id":int(i),"bus":bus,"nominal_p_mw":p,
                         "min_p_mw":minimum,"max_p_mw":maximum,
                         "downward_headroom_mw":p-minimum,
                         "upward_headroom_mw":maximum-p,
                         "hop_distance_to_overloaded_trafo_endpoint":ds.get(bus,9999)})
    eligible.sort(key=lambda row:(row["hop_distance_to_overloaded_trafo_endpoint"],
                                  -row["downward_headroom_mw"],row["gen_id"]))
    selected=eligible[:8]
    return {"audit_provenance":input_file,"physical_evaluations":0,
            "source":"pandapower.networks.case1888rte()",
            "first_eight_pv_gen_ids":[int(x) for x in net.gen.index[:8]],
            "top_baseline_thermal_offenders":items,
            "selected_p_controls":selected,
            "eligible_p_control_count":len(eligible),
            "switch_element_count":len(net.switch),
            "notes":["Topological hop metric ignores electrical reactance and thermal sensitivities.",
                     "This screening is not a mathematical infeasibility certificate.",
                     "Published min/max P are treated as allowed dispatch bounds only in a separate new formulation.",
                     "MATPOWER/pandapower conversion and slack assumptions still require independent validation."]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="research/results/rte1888_iteration7_audit_20261021.json")
    p.add_argument("--output",default="rte1888_topology.json")
    args=p.parse_args()
    result=analyze(args.input)
    with open(args.output,"w",encoding="utf8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
    print("TOPOLOGY",json.dumps({"selected":result["selected_p_controls"],
                                 "eligible":result["eligible_p_control_count"],
                                 "examples":result["top_baseline_thermal_offenders"][:4],
                                 "switches":result["switch_element_count"]}),
          flush=True)


if __name__=="__main__":main()
