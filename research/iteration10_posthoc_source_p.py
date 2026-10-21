"""Post-hoc transparent bus-1268 source generator P balance audit.

No AC calls. Avoid interpreting converted ext_grid limits alone as a
single original generator's bounds. Uses immutable raw Iteration 10 runs.
Not preregistered; explicitly an interpretive correction.
"""
import argparse
import json
import math

from research.iteration9_source_generators import read_sources

INPUT = "research/results/rte1888_iteration10_source_slack_ac_20261021.json"


def source_bounds(sources, bus_id):
    online=[x for x in sources if int(x["gen_bus"])==bus_id
            and int(x["gen_status"])==1]
    if not online:
        raise ValueError("No source generator at requested bus")
    return {
        "source_bus_id":bus_id,
        "active_original_generators":len(online),
        "source_pmin_sum_mw":sum(x["pmin_mw"] for x in online),
        "source_pmax_sum_mw":sum(x["pmax_mw"] for x in online),
        "source_initial_pg_sum_mw":sum(x["pg_mw"] for x in online),
    }


def aggregate_pg_check(ext_p_mw, other_pg_mw, lower, upper):
    if any(not math.isfinite(float(x)) for x in
           (ext_p_mw,other_pg_mw,lower,upper)):
        raise ValueError("Nonfinite generator results")
    total=float(ext_p_mw)+float(other_pg_mw)
    return {"observed_source_bus_pg_total_mw":total,
            "p_below_original_aggregate_pmin_mw":max(float(lower)-total,0.),
            "p_above_original_aggregate_pmax_mw":max(total-float(upper),0.),
            "p_within_original_aggregate_bounds":float(lower)-1e-6 <= total <= float(upper)+1e-6}


def audit_rows(raw, sources):
    if raw["metadata"]["actual_ac_powerflow_calls"]!=2:
        raise ValueError("Not an exact two-call physical record")
    rows=raw["rows"]
    if len(rows)!=2 or [r["scenario"] for r in rows]!=[
        "original_converted_pandapower","experimental_source_slack_relocated"]:
        raise ValueError("Unexpected electrical case order")
    base=source_bounds(sources,1268)
    if base["active_original_generators"]!=2:
        raise ValueError("Unexpected source generator count")
    if abs(base["source_pmin_sum_mw"]-88)>1e-6 or abs(base["source_pmax_sum_mw"]-90)>1e-6:
        raise ValueError("Original source generator bounds changed")
    # The preflight for the actual AC run required and retained ONE
    # converted sgen on BUS1268 with P=44.5 MW. Scenario 2 additionally
    # inserted one converted gen with P=44.5 MW and relocated ext_grid.
    # This source-bus total is deliberately NOT ext-grid-only output.
    fixed_sgen_p=44.5
    result=[]
    for index,row in enumerate(rows):
        if row["solver_failed"] or row["slack_p_mw"] is None:
            result.append({"scenario":row["scenario"],"source_pg_comparison":None})
            continue
        other=(fixed_sgen_p if index==0 else fixed_sgen_p+44.5)
        ext=(float(row["slack_p_mw"]) if index==0 else 0.0)
        status=aggregate_pg_check(ext,other,
                  base["source_pmin_sum_mw"],base["source_pmax_sum_mw"])
        result.append({
          "scenario":row["scenario"],
          "retained_source_bus_sgen_p_mw":fixed_sgen_p,
          "added_source_bus_gen_p_mw":0. if index==0 else 44.5,
          "source_bus_ext_grid_p_mw":ext,
          **status})
    return {"status":"POST_HOC_no_AC_original_aggregate_P_check",
       "new_ac_powerflow_calls":0,"original_physical_ac_calls_used":2,
       "source_bus":base,"rows":result,
       "note":("An ext_grid-only minimum P bound is NOT equivalent to a "
           "two-source-generator aggregate bound. This arithmetic preserves "
           "one measured ext and one preflight-verified sgen at source BUS1268. "
           "No independent source Q reconstruction or full OPF claim.")}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default=INPUT)
    p.add_argument("--output",default="iteration10_posthoc_aggregate_p.json")
    a=p.parse_args()
    with open(a.input,encoding="utf-8") as f:
        raw=json.load(f)
    sources,_=read_sources()
    result=audit_rows(raw,sources)
    with open(a.output,"w",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
    print("I10_AGGREGATE_POST_HOC",json.dumps(result,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
