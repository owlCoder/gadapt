"""Trace MATPOWER case1888rte RATE_A to each pandapower line/transformer.

Static source-specified limit audit, without AC calls. Not an optimizer.
Source: MATPOWER/matpower commit 80b6e16..., file blob SHA
820bd317167381baf819d67eab7d886013e8b05a (CC BY 4.0).
The raw branch input archive was extracted verbatim for numeric columns.
"""
import argparse
from collections import defaultdict
import csv
import json
import math

import numpy as np
from scipy.optimize import linear_sum_assignment
import pandapower.networks as pn

INPUT="research/results/rte1888_matpower_original_branch_ratings_2019.csv"


def source_branches(path):
    with open(path,encoding="utf8",newline="") as handle:
        rows=list(csv.DictReader(handle))
    expected={"source_branch_row_1based","from_bus","to_bus","br_r_pu",
              "br_x_pu","rate_a_mva","rate_b_mva","rate_c_mva",
              "tap","shift_degrees","branch_status"}
    if not rows or set(rows[0])!=expected:
        raise ValueError("Missing required source MATPOWER branch fields")
    parsed=[]
    for r in rows:
        d={k: int(r[k]) if k in ("source_branch_row_1based","from_bus",
                               "to_bus","branch_status") else float(r[k])
           for k in expected}
        if not all(math.isfinite(float(v)) for v in d.values()):
            raise ValueError("Nonfinite source ratings or impedances")
        if d["rate_a_mva"]<0:
            raise ValueError("Invalid negative source RATE_A")
        parsed.append(d)
    if sorted(x["source_branch_row_1based"] for x in parsed)!=list(range(1,len(parsed)+1)):
        raise ValueError("Source row IDs are not contiguous")
    return parsed


def unordered(a,b):
    return (min(int(a),int(b)),max(int(a),int(b)))


def converted_impedance(net,kind,index):
    if kind=="line":
        row=net.line.loc[index]
        from_bus=int(row.from_bus)
        to_bus=int(row.to_bus)
        vn1=float(net.bus.at[from_bus,"vn_kv"])
        vn2=float(net.bus.at[to_bus,"vn_kv"])
        if abs(vn1-vn2)>1e-6:
            raise ValueError("Line spans unlike nominal voltages")
        zbase=vn1*vn1/float(net.sn_mva)
        return (float(row.r_ohm_per_km)*float(row.length_km)/zbase/float(row.parallel),
                float(row.x_ohm_per_km)*float(row.length_km)/zbase/float(row.parallel))
    row=net.trafo.loc[index]
    factor=float(net.sn_mva)/float(row.sn_mva)/float(row.parallel)
    vkr=float(row.vkr_percent)/100.
    vk=float(row.vk_percent)/100.
    return (vkr*factor,math.sqrt(max(0.,vk*vk-vkr*vkr))*factor)


def match(net,rows):
    if len(net.bus["name"].dropna())!=len(net.bus):
        raise ValueError("Source bus identifiers missing")
    names={int(idx):int(net.bus.at[idx,"name"])+1 for idx in net.bus.index}
    if len(set(names.values()))!=len(names):
        raise ValueError("Duplicate original source bus IDs")
    source=defaultdict(list)
    for item in rows:
        source[unordered(item["from_bus"],item["to_bus"])].append(item)
    converted=defaultdict(list)
    for kind,df,ac,bc in (("line",net.line,"from_bus","to_bus"),
                          ("trafo",net.trafo,"hv_bus","lv_bus")):
        for idx,v in df.iterrows():
            key=unordered(names[int(v[ac])],names[int(v[bc])])
            r,x=converted_impedance(net,kind,idx)
            converted[key].append({"kind":kind,"element_index":int(idx),
                                   "r_pu":r,"x_pu":x,"pp_in_service":bool(v.in_service),
                                   "sn_mva":float(v.sn_mva) if kind=="trafo" else None})
    allkeys=set(source)|set(converted)
    unmatched=[]
    assigned=[]
    max_error=0.
    ambiguous=[]
    for key in sorted(allkeys):
        sr=source.get(key,[])
        cr=converted.get(key,[])
        if len(sr)!=len(cr):
            unmatched.append({"key":list(key),"source":len(sr),"pandapower":len(cr)})
            continue
        n=len(sr)
        if not n:continue
        cost=np.zeros((n,n),float)
        for i,c in enumerate(cr):
            for j,b in enumerate(sr):
                # Original MATPOWER branch impedances are rounded to approx 6-9 decimals.
                cost[i,j]=(abs(c["r_pu"]-b["br_r_pu"])/(1e-4+abs(b["br_r_pu"]))+
                           abs(c["x_pu"]-b["br_x_pu"])/(1e-4+abs(b["br_x_pu"])))
        ia,ib=linear_sum_assignment(cost)
        for i,j in zip(ia,ib):
            item=dict(cr[int(i)])
            br=sr[int(j)]
            item.update({"source_branch_row_1based":br["source_branch_row_1based"],
                         "source_from_bus":br["from_bus"],
                         "source_to_bus":br["to_bus"],
                         "rate_a_mva":br["rate_a_mva"],
                         "source_in_service":bool(br["branch_status"]),
                         "match_impedance_relative_error":float(cost[i,j])})
            max_error=max(max_error,float(cost[i,j]))
            assigned.append(item)
        # If rounded r and x match and RATE_A differs, verify uniqueness.
        if n>1 and len({v["rate_a_mva"] for v in sr})>1:
            for i in range(n):
                nearest=np.sort(cost[i,:])
                if len(nearest)>1 and nearest[1]-nearest[0] < 1e-8:
                    ambiguous.append({"key":list(key),"candidate_rates":
                                      [v["rate_a_mva"] for v in sr]})
                    break
    assigned.sort(key=lambda z:(z["kind"],z["element_index"]))
    return {"source_branch_count":len(rows),
            "pandapower_line_count":len(net.line),
            "pandapower_trafo_count":len(net.trafo),
            "mapped_count":len(assigned),
            "unmatched_pairs":unmatched,
            "ambiguous_parallel_pairs":ambiguous,
            "max_match_impedance_relative_error":max_error,
            "source_rate_a_zero":sum(z["rate_a_mva"]==0 for z in rows),
            "source_rate_a_positive":sum(z["rate_a_mva"]>0 for z in rows),
            "mapped_transformers_with_zero_rate_a":
                sum(z["kind"]=="trafo" and z["rate_a_mva"]==0 for z in assigned),
            "mapped_lines_with_zero_rate_a":
                sum(z["kind"]=="line" and z["rate_a_mva"]==0 for z in assigned),
            "map":assigned}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",default=INPUT)
    parser.add_argument("--output",default="rte1888_source_rating_map.json")
    args=parser.parse_args()
    net=pn.case1888rte()
    result=match(net,source_branches(args.source))
    with open(args.output,"w",encoding="utf8") as handle:
        json.dump(result,handle,indent=2,sort_keys=True,allow_nan=False)
    print("RATING_MAP",json.dumps({k:v for k,v in result.items() if k!="map"}),flush=True)
    print("RATING_EXAMPLES",json.dumps([x for x in result["map"] if
        x["kind"]=="trafo" and x["element_index"] in (404,466,402,403)]),flush=True)
    if (result["unmatched_pairs"] or result["ambiguous_parallel_pairs"] or
        result["mapped_count"]!=result["source_branch_count"]):
        raise RuntimeError("Cannot assert a complete source-faithful rating map")
    # Do not assume that conversion preserves resistance/inductance precisely.
    # Diagnostics log worst mismatch and must justify trust before optimization.


if __name__=="__main__":
    main()
