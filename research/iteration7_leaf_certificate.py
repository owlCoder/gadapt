"""Conditional analytic RTE1888 infeasibility screen for radial transformer terminals.

NO AC powerflows. Uses nameplate current rating and bus voltage upper bound.
Certificate is conditional on interpreting pandapower nameplate 100% as a
physical constraint; source MATPOWER RATE_A provenance remains open.
"""
import argparse
import json
import math
import pandas as pd
import pandapower.networks as pn


def in_service(frame):
    return frame if "in_service" not in frame else frame[frame.in_service.fillna(False).astype(bool)]


def count_series(net,bus):
    lines=in_service(net.line)
    trafos=in_service(net.trafo)
    return (int(((lines.from_bus==bus)|(lines.to_bus==bus)).sum()) +
            int(((trafos.hv_bus==bus)|(trafos.lv_bus==bus)).sum()))


def terminal_capacity(sn_mva, max_vm_pu, bus_nom_kv, trafo_nom_kv, limit_percent):
    vals=[sn_mva,max_vm_pu,bus_nom_kv,trafo_nom_kv,limit_percent]
    if not all(math.isfinite(float(v)) and float(v)>0 for v in vals):
        raise ValueError("No positive finite thermal/voltage rating")
    return float(sn_mva)*float(max_vm_pu)*float(bus_nom_kv)/float(trafo_nom_kv)*float(limit_percent)/100.


def candidate(net,trafo_id,terminal_bus):
    t=net.trafo.loc[trafo_id]
    if not bool(t.in_service) or count_series(net,terminal_bus)!=1:
        return {"eligible":False,"reason":"not exactly one energized series branch"}
    if terminal_bus==int(t.lv_bus):
        nom_kv=float(t.vn_lv_kv)
        side="lv"
    elif terminal_bus==int(t.hv_bus):
        nom_kv=float(t.vn_hv_kv)
        side="hv"
    else:
        return {"eligible":False,"reason":"bus is not a transformer terminal"}
    if len(net.switch) or any(len(in_service(getattr(net,name))[in_service(getattr(net,name)).bus==terminal_bus]) for name in
                              ("shunt","sgen","ext_grid","storage","ward","xward")
                              if hasattr(net,name) and "bus" in getattr(net,name)):
        return {"eligible":False,"reason":"other active devices or switch may inject or redirect power"}
    loads=in_service(net.load)
    loads=loads[loads.bus==terminal_bus]
    for col in ("const_i_percent","const_z_percent"):
        if col in loads and any(pd.isna(x) or abs(float(x))>1e-9 for x in loads[col]):
            return {"eligible":False,"reason":"load P is not confirmed constant-power"}
    gens=in_service(net.gen)
    gens=gens[gens.bus==terminal_bus]
    if not len(gens):
        return {"eligible":False,"reason":"no local conventional generator"}
    if not ("min_p_mw" in gens and
            all(pd.notna(x) and math.isfinite(float(x)) for x in gens.min_p_mw)):
        return {"eligible":False,"reason":"missing finite minimum generator active power"}
    load_p=float((loads.p_mw*loads.scaling).sum()) if "scaling" in loads else float(loads.p_mw.sum())
    min_gen_p=float(gens.min_p_mw.sum())
    p_bound=min_gen_p-load_p
    v_upper=float(net.bus.at[terminal_bus,"max_vm_pu"])
    rated_bus=float(net.bus.at[terminal_bus,"vn_kv"])
    lim=float(t.max_loading_percent) if pd.notna(t.get("max_loading_percent")) else 100.
    cap=terminal_capacity(float(t.sn_mva),v_upper,rated_bus,nom_kv,lim)
    return {"eligible":True,"trafo_id":int(trafo_id),"side":side,"bus":int(terminal_bus),
            "terminal_series_count":count_series(net,terminal_bus),
            "gen_ids":[int(x) for x in gens.index],"generator_min_p_mw":min_gen_p,
            "constant_load_p_mw":load_p,"minimum_export_p_mw":p_bound,
            "trafo_rating_mva":float(t.sn_mva),"trafo_limit_percent":lim,
            "bus_v_max_pu":v_upper,"bus_nominal_kv":rated_bus,
            "trafo_terminal_nominal_kv":nom_kv,
            "necessary_max_export_mw_from_current_limit":cap,
            "excess_lower_bound_mw":p_bound-cap,
            "certified_infeasible_under_assumptions":bool(p_bound>cap+1e-7)}


def check(audit_path):
    data=json.loads(open(audit_path,encoding="utf8").read())
    offenders=data["loads"]["1.0"]["reference_top_thermal_offenders"]
    net=pn.case1888rte()
    checks=[]
    for row in offenders:
        if row["type"]!="trafo":
            continue
        for terminal in (int(row["from_bus"]),int(row["to_bus"])):
            check=candidate(net,int(row["element_id"]),terminal)
            check["baseline_loading_percent"]=float(row["loading_percent"])
            check["element_id"]=int(row["element_id"])
            check["terminal_bus"]=terminal
            checks.append(check)
    certified=[row for row in checks if row.get("certified_infeasible_under_assumptions")]
    return {"input":audit_path,"actual_pf_calls":0,
            "model":"case1888rte with original 100% trafo current limits and published P minima",
            "certificate_status":"conditional_on_input_ratings",
            "screened_trafo_count":len(offenders),"screened_terminals":len(checks),
            "certified_leaf_terminals":certified,
            "all_screen_results":checks,
            "network_infeasible_under_stated_constraints":len(certified)>0,
            "caveats":["No N-1, global optimum, field-operation or data-provenance certification.",
                       "Certificate requires current-based loading at the bus terminal, fixed constant-power loads and published active-power minima.",
                       "MATPOWER source and pandapower conversion ratings must be independently justified before declaring any real-network physical limit."]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="research/results/rte1888_iteration7_audit_20261021.json")
    p.add_argument("--output",default="rte1888_leaf_certificate.json")
    a=p.parse_args()
    out=check(a.input)
    with open(a.output,"w",encoding="utf8") as f:json.dump(out,f,indent=2,sort_keys=True,allow_nan=False)
    print("CERTIFICATE",json.dumps({"certified":len(out["certified_leaf_terminals"]),
          "examples":out["certified_leaf_terminals"][:8],
          "checked":out["screened_terminals"]}),flush=True)


if __name__=="__main__":
    main()
