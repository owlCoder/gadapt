"""Audit actual IEEE118 reproducibility independently of optimizer conclusions.

Reports TWO hashes: one of identical proposed AC voltage vectors and one
of numerical solver outcomes. A divergent INPUT hash suggests random or
order instability; a divergent OUTPUT hash given identical INPUT hash
indicates numerical or solver/environment nondeterminism. No optimizer
is evaluated for research superiority by this diagnostic.
"""
import argparse
import hashlib
import json
import math
import random
import sys
import numpy as np
from gadapt.ga import GA
from research.ieee_grid_benchmark import GridProblem,GEN_VOLTAGE_BOUNDS

def digest(items):
    return hashlib.sha256(json.dumps(items,sort_keys=True,allow_nan=False,
                                     separators=(",",":")).encode()).hexdigest()

def run(mode,seed=200):
    random.seed(seed)
    np.random.seed(seed)
    grid=GridProblem("ieee118",1.)
    inputs=[]
    outputs=[]
    if mode=="ac":
        rng=np.random.default_rng(seed)
        x=np.clip(grid.reference,*GEN_VOLTAGE_BOUNDS)
        vecs=[x]+[np.clip(x+rng.normal(0,.008,grid.dimension),
                           *GEN_VOLTAGE_BOUNDS) for _ in range(15)]
        for vec in vecs:
            inputs.append(list(map(float,vec)))
            info=grid.evaluate(vec)
            outputs.append([float(info["objective"]),float(info["loss"]),
                            float(info["violation"]),bool(info["feasible"]),
                            bool(info["solver_failed"])])
    elif mode=="ga":
        calls=[0]
        def objective(vec):
            calls[0]+=1
            if calls[0]>48:
                return 1e12
            values=list(map(float,vec))
            inputs.append(values)
            info=grid.evaluate(values)
            outputs.append([float(info["objective"]),
                            float(info["loss"]) if math.isfinite(info["loss"]) else "NA",
                            float(info["violation"]) if math.isfinite(info["violation"]) else "NA",
                            bool(info["feasible"]),
                            bool(info["solver_failed"])])
            return float(info["objective"])
        ga=GA(cost_function=objective,population_size=24,
              exit_check="generations",
              exit_function=lambda:calls[0]>=48,
              number_of_generations=12,
              population_mutation="cost_diversity,parent_diversity",
              timeout=90)
        for _ in range(grid.dimension):ga.add(*GEN_VOLTAGE_BOUNDS)
        result=ga.execute()
        if not result.success:raise RuntimeError(str(result.message))
    else:raise ValueError(mode)
    if len(inputs)<16:raise RuntimeError("Expected at least 16 genuine AC solves")
    print(json.dumps(dict(mode=mode,seed=seed,
                          input_sha256=digest(inputs),
                          output_sha256=digest(outputs),
                          n_physical=grid.calls,
                          initial_vectors=inputs[:2],
                          initial_outputs=outputs[:2],
                          versions=dict(python=sys.version.split()[0],
                          numpy=np.__version__)),sort_keys=True),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=["ac","ga"],required=True)
    p.add_argument("--seed",type=int,default=200)
    a=p.parse_args()
    run(a.mode,a.seed)
