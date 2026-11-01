"""Inspect pandapower converter identifiers for MATPOWER rate provenance.

Static metadata only; no PF evaluations or topology modifications.
"""
import argparse
import json
import math

import numpy as np
import pandas as pd
import pandapower.networks as pn

def safe(value):
    if isinstance(value,(np.integer,)):return int(value)
    if isinstance(value,(int,str,bool)) or value is None:return value
    if isinstance(value,(float,np.floating)):
        return float(value) if math.isfinite(value) else None
    if pd.isna(value):return None
    return str(value)

def row(frame, idx):
    if idx not in frame.index:return None
    return {"index":int(idx),**{k:safe(v) for k,v in frame.loc[idx].items()}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="rte1888_conversion_probe.json")
    a=p.parse_args()
    net=pn.case1888rte()
    info={
        "net_name":str(net.name),"line_columns":list(net.line.columns),
        "trafo_columns":list(net.trafo.columns),
        "bus_columns":list(net.bus.columns),
        "trafo_rated_99_999_count":int(np.sum(np.isclose(net.trafo.sn_mva,99.999,rtol=0,atol=.00001))),
        "transformers_sample":[row(net.trafo,i) for i in (404,466,402,403,493,380,491,492,494,479,522,322,323,324)],
        "bus_samples":[row(net.bus,i) for i in (1705,1767,1703,1704,1794,1681,444,104)],
        "gen_samples":[row(net.gen,i) for i in (122,183,120,121,210,99,208)],
        "line_samples":[row(net.line,i) for i in (0,1,2)],
    }
    with open(a.output,"w",encoding="utf8") as f:json.dump(info,f,indent=2,sort_keys=True,allow_nan=False)
    print("CONVERSION_META",json.dumps({
        "trafo_rated_99_999_count":info["trafo_rated_99_999_count"],
        "selected":info["transformers_sample"][:3],
        "bus_samples":info["bus_samples"][:2],
        "line_columns":info["line_columns"], "trafo_columns":info["trafo_columns"],
        "bus_columns":info["bus_columns"]
    }),flush=True)

if __name__=="__main__":main()
