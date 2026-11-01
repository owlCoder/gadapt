"""Iteration 7 corrected source-MATPOWER RTE1888 AC feasibility evaluator.

Finite RATE_A is checked as MVA at both terminals; zero RATE_A is
unconstrained. Explicitly a DIFFERENT optimization problem from
iteration 6. It preserves original GridProblem voltage controls and NR
powerflow but never uses the pandapower 100%-of-surrogate rating.
See preregistration ITERATION7_PROTOCOL.md (addendum C).
"""
import argparse
import csv
import math

import numpy as np
import pandapower as pp

from research.ieee_grid_benchmark import GridProblem, PENALTY_WEIGHT

DEFAULT_MAP = (
    "research/results/rte1888_iteration7_matpower_to_pandapower_thermal_map_20261021.csv"
)


def read_and_validate_map(net, path=DEFAULT_MAP):
    with open(path,encoding="utf8",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=len(net.line)+len(net.trafo):
        raise ValueError("Rate-map count mismatch")
    by_kind={"line":{},"trafo":{}}
    ids=set()
    for row in rows:
        kind=row["kind"]
        if kind not in by_kind:
            raise ValueError("Unknown element kind")
        index=int(row["element_index"])
        original_branch=int(row["source_branch_row_1based"])
        if original_branch in ids or index in by_kind[kind]:
            raise ValueError("Duplicate source branch or mapped element")
        ids.add(original_branch)
        table=getattr(net,kind)
        if index not in table.index:
            raise ValueError("Missing converted element")
        sfrom=int(row["source_from_bus"])
        sto=int(row["source_to_bus"])
        if kind=="line":
            local=(int(table.at[index,"from_bus"]),int(table.at[index,"to_bus"]))
        else:
            local=(int(table.at[index,"hv_bus"]),int(table.at[index,"lv_bus"]))
        names={int(net.bus.at[bus,"name"])+1 for bus in local}
        if names!={sfrom,sto}:
            raise ValueError("Source and pandapower branch endpoints disagree")
        rate=float(row["rate_a_mva"])
        if not math.isfinite(rate) or rate<0:
            raise ValueError("Invalid RATE_A")
        by_kind[kind][index]=rate
    if sorted(ids)!=list(range(1,len(rows)+1)):
        raise ValueError("Source indices incomplete")
    if sum(v==0 for d in by_kind.values() for v in d.values())!=455:
        raise ValueError("Expected exactly 455 source branches with no rating")
    if len(by_kind["line"])!=1976 or len(by_kind["trafo"])!=555:
        raise ValueError("Source case counts differ")
    return {k:np.array([v[int(i)] for i in getattr(net,k).index],float)
            for k,v in by_kind.items()}


def source_apparent_violations(net, rating_by_kind):
    counts,totals,largest={}, {}, {}
    for kind, flow_fields in (
        ("line",(("p_from_mw","q_from_mvar"),("p_to_mw","q_to_mvar"))),
        ("trafo",(("p_hv_mw","q_hv_mvar"),("p_lv_mw","q_lv_mvar")))
    ):
        r=getattr(net,"res_"+kind)
        rate=rating_by_kind[kind]
        if not all(f in r.columns for p in flow_fields for f in p):
            raise ValueError("Missing required apparent-flow result fields")
        first=np.hypot(r[flow_fields[0][0]].to_numpy(float),
                       r[flow_fields[0][1]].to_numpy(float))
        second=np.hypot(r[flow_fields[1][0]].to_numpy(float),
                        r[flow_fields[1][1]].to_numpy(float))
        if not np.all(np.isfinite(first)) or not np.all(np.isfinite(second)):
            raise FloatingPointError("Nonfinite physical power flows")
        observed=np.maximum(first,second)
        if len(observed)!=len(rate):
            raise ValueError("Mismatched rating vector")
        active=np.asarray(getattr(net,kind).in_service,dtype=bool)
        finite=(rate>0)&active
        excess=np.zeros(len(rate),float)
        excess[finite]=np.maximum(observed[finite]/rate[finite]-1.,0.)
        totals[kind]=float(np.sum(excess))
        counts[kind]=int(np.sum(excess>1e-8))
        largest[kind]=float(np.max(observed[finite]/rate[finite])*100.) if np.any(finite) else 0.
    return totals,counts,largest


class SourceRatedRTEGrid(GridProblem):
    """Source-MATPOWER RATE_A semantics with original eight PV setpoints."""

    def __init__(self, load_factor=1.0, scoring="penalty", rating_file=DEFAULT_MAP):
        if scoring not in ("penalty","feasibility_first"):
            raise ValueError("Invalid scoring rule")
        super().__init__("rte1888",load_factor)
        self.scoring=scoring
        self.source_rates=read_and_validate_map(self.net,rating_file)

    def evaluate(self, x, count=True):
        if count:
            self.calls+=1
        if len(x)!=self.dimension:
            raise ValueError("Expected exactly eight generator voltages")
        for idx,value in zip(self.gen_ids,x):
            self.net.gen.at[idx,"vm_pu"]=float(value)
        try:
            pp.runpp(self.net,init="dc",algorithm="nr",
                     calculate_voltage_angles=True,numba=False,
                     enforce_q_lims=True,max_iteration=40,
                     tolerance_mva=1e-8)
            v=self.net.res_bus.vm_pu.to_numpy(float)
            if not np.all(np.isfinite(v)):
                raise FloatingPointError("Nonfinite bus voltage")
            voltage_low=float(np.maximum(self.v_lower-v,0).sum())
            voltage_high=float(np.maximum(v-self.v_upper,0).sum())
            totals,counts,largest=source_apparent_violations(self.net,self.source_rates)
            violation=voltage_low+voltage_high+totals["line"]+totals["trafo"]
            loss=float(self.net.res_line.pl_mw.sum()+self.net.res_trafo.pl_mw.sum())
            if not math.isfinite(loss) or not math.isfinite(violation):
                raise FloatingPointError("Nonfinite powerflow objective")
            feasible=bool(violation<=1e-8)
            if self.scoring=="feasibility_first":
                score=(-1./(1.+max(0.,loss)) if feasible else violation)
            else:
                score=loss+PENALTY_WEIGHT*violation
            return {
                "loss":loss,"violation":float(violation),"feasible":feasible,
                "objective":float(score),"solver_failed":False,"solver_error":"",
                "voltage_under":voltage_low,"voltage_over":voltage_high,
                "source_line_excess":totals["line"],
                "source_trafo_excess":totals["trafo"],
                "source_line_overloads":counts["line"],
                "source_trafo_overloads":counts["trafo"],
                "min_voltage_pu":float(min(v)),
                "max_voltage_pu":float(max(v)),
                "max_line_source_loading_pct":largest["line"],
                "max_trafo_source_loading_pct":largest["trafo"],
                "max_loading":max(largest.values())}
        except Exception as exc:
            return {
                "loss":math.nan,"violation":math.inf,"feasible":False,
                "objective":1e12,"solver_failed":True,
                "solver_error":(type(exc).__name__+": "+str(exc))[:180],
                "voltage_under":math.nan,"voltage_over":math.nan,
                "source_line_excess":math.nan,
                "source_trafo_excess":math.nan,
                "source_line_overloads":None,"source_trafo_overloads":None,
                "min_voltage_pu":math.nan,"max_voltage_pu":math.nan,
                "max_line_source_loading_pct":math.nan,
                "max_trafo_source_loading_pct":math.nan,
                "max_loading":math.nan,
            }


def diagnostic(load):
    grid=SourceRatedRTEGrid(load)
    reference=np.asarray(grid.reference,float)
    points=[("reference",-1,0.,reference)]
    for i in range(grid.dimension):
        for delta in (-0.02,0.02):
            x=reference.copy()
            x[i]=np.clip(x[i]+delta,.95,1.08)
            points.append(("voltage_perturbation",i,delta,x))
    rows=[]
    for title,index,delta,values in points:
        x=grid.evaluate(values)
        record={"load_factor":load,"trial":title,"generator_index":index,
                "requested_delta":delta,"actual_ac_call":grid.calls,
                "solver_failed":x["solver_failed"],
                "physical_feasible":x["feasible"],
                "loss_mw":x["loss"],
                "normalized_violation":x["violation"],
                "voltage_under_pu":x["voltage_under"],
                "voltage_over_pu":x["voltage_over"],
                "source_line_excess_sum":x["source_line_excess"],
                "source_trafo_excess_sum":x["source_trafo_excess"],
                "source_line_overloads":x["source_line_overloads"],
                "source_trafo_overloads":x["source_trafo_overloads"],
                "max_line_source_loading_pct":x["max_line_source_loading_pct"],
                "max_trafo_source_loading_pct":x["max_trafo_source_loading_pct"],
                "solver_error":x["solver_error"]}
        rows.append(record)
        print("SOURCE_AC",record,flush=True)
    if grid.calls!=17:
        raise ValueError("Expected 17 true source-rated AC calls per load")
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--loads",nargs="+",type=float,default=[1.,1.1])
    parser.add_argument("--output",default="rte1888_source_rated_17x2.csv")
    args=parser.parse_args()
    if not args.loads or any(not math.isfinite(v) or v<=0 for v in args.loads):
        parser.error("Only positive finite loads")
    rows=[]
    for load in args.loads:
        rows.extend(diagnostic(load))
    with open(args.output,"w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if len(rows)!=17*len(args.loads):
        raise RuntimeError("Physical budget inconsistent")
    print("SOURCE_SUMMARY",{
        x: {"physically_feasible":sum(z["physical_feasible"] for z in rows if z["load_factor"]==x),
            "ac_solver_failures":sum(z["solver_failed"] for z in rows if z["load_factor"]==x),
            "min_converged_violation":min([z["normalized_violation"] for z in rows
                  if z["load_factor"]==x and not z["solver_failed"]],default=None)}
        for x in args.loads},flush=True)


if __name__=="__main__":
    main()
