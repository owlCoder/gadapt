"""Read-only diagnostic of existing public IEEE118 and French RTE1888 AC test settings.

No algorithm is selected or tuned by this probe. Each evaluate call is an
actual pandapower NR solve; returned feasibility is independent of penalty.
"""
import argparse, json, time
import numpy as np
from research.ieee_grid_benchmark import GridProblem,GEN_VOLTAGE_BOUNDS

def run(case,load,seed,probes):
    start=time.perf_counter()
    grid=GridProblem(case,load)
    rng=np.random.default_rng(seed)
    observations=[]
    candidates=[("published_reference",grid.reference)]
    for j in range(probes):
        candidates.append((f"bounded_perturb_{j}",np.clip(grid.reference+
                    rng.normal(0.,.008,grid.dimension),*GEN_VOLTAGE_BOUNDS)))
    for name,vec in candidates:
        t=time.perf_counter()
        obj=grid.evaluate(vec)
        observations.append(dict(candidate=name,elapsed_sec=round(time.perf_counter()-t,3),
                                 converged=not obj["solver_failed"],
                                 feasible=obj["feasible"],
                                 objective=obj["objective"],loss=obj["loss"],
                                 violation=obj["violation"],
                                 maximum_loading=obj["maximum_loading"],
                                 voltage_min=obj["minimum_voltage"],
                                 voltage_max=obj["maximum_voltage"],
                                 error=obj["solver_error"]))
    print("DIAGNOSTIC",json.dumps(dict(case=case,load=load,seed=seed,dimension=grid.dimension,
                                     physical_pf_calls=grid.calls,
                                     elapsed_total=round(time.perf_counter()-start,3),
                                     results=observations)),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--rte",action="store_true")
    a=p.parse_args()
    run("ieee118",1.0,1741,3)
    run("ieee118",1.1,1741,3)
    if a.rte:run("rte1888",1.0,1741,2)
if __name__=="__main__":main()
