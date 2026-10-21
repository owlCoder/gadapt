"""Iteration 6: IEEE118 risk/progress-aware *budget allocation*, not novel AOS.

Run as python -m research.ieee118_allocation --seeds 6 --budget 180.
Protocol was frozen before implementation in ITERATION6_PROTOCOL.md.
Uses actual installed GAdapt and real pandapower AC PF, NOT fake evaluations.
"""
import argparse
import csv
import math
import random
import statistics
import time

import numpy as np
from scipy.optimize import differential_evolution, minimize
from gadapt.ga import GA
from research.ieee_grid_benchmark import GridProblem, GEN_VOLTAGE_BOUNDS

METHODS = ("gadapt_legacy", "slsqp_multistart", "hybrid_fixed_half",
           "hybrid_adaptive", "scipy_de", "cma_es")


class BudgetExhausted(Exception):
    pass


class PhysicalGridRecorder:
    def __init__(self, grid, budget):
        self.grid, self.budget = grid, budget
        self.stage_cap = budget
        self.calls = 0
        self.requests = 0
        self.best_feasible = math.inf
        self.best_feasible_vector = None
        self.best_penalized = math.inf
        self.best_penalized_vector = None
        self.minimum_violation = math.inf
        self.failed_ac_calls = 0
        self.physical_feasible_calls = 0
        self.random_fills = 0
        self.local_starts = 0
        self.local_bad_exits = 0
        self.cma_rounds = 0
        self.checkpoint_best_feasible = None
        self.checkpoint_count = math.ceil(.125 * budget)
        self.probe_count = math.ceil(.25 * budget)
        self.events = []

    def __call__(self, values):
        self.requests += 1
        if self.calls >= min(self.stage_cap, self.budget):
            return 1e12  # rejected wrapper request; not a physical evaluation
        self.calls += 1
        x = tuple(float(v) for v in values)
        observation = self.grid.evaluate(x)
        score = float(observation["objective"])
        if not math.isfinite(score):
            raise ValueError("Non-finite objective from physical model")
        if observation["solver_failed"]:
            self.failed_ac_calls += 1
        else:
            violation = float(observation["violation"])
            self.minimum_violation = min(self.minimum_violation, violation)
            if observation["feasible"]:
                self.physical_feasible_calls += 1
                loss = float(observation["loss"])
                if loss < self.best_feasible:
                    self.best_feasible = loss
                    self.best_feasible_vector = x
        if score < self.best_penalized:
            self.best_penalized = score
            self.best_penalized_vector = x
        if self.calls == self.checkpoint_count:
            self.checkpoint_best_feasible = (
                float(self.best_feasible) if math.isfinite(self.best_feasible)
                else None
            )
        return score

    def strict(self, values):
        if self.calls >= min(self.stage_cap, self.budget):
            self.requests += 1
            raise BudgetExhausted
        return self(values)

    def local_start_point(self):
        if self.best_feasible_vector is not None:
            return np.array(self.best_feasible_vector, float)
        if self.best_penalized_vector is not None:
            return np.array(self.best_penalized_vector, float)
        return np.clip(np.asarray(self.grid.reference, float),
                       *GEN_VOLTAGE_BOUNDS)


class AllocationSwitch:
    """One frozen decision made at the first GA generation after 25% budget."""

    def __init__(self, recorder, policy):
        self.recorder = recorder
        self.policy = policy
        self.target = recorder.budget if policy == "legacy" else (
            math.ceil(.5 * recorder.budget) if policy == "fixed" else recorder.budget)
        self.decided = policy != "adaptive"
        if self.decided:
            recorder.stage_cap = self.target
        self.decision = ("full_ga" if policy == "legacy" else
                         "half_ga" if policy == "fixed" else "")
        self.progress = None
        self.decision_at = None

    def check(self):
        rec = self.recorder
        if not self.decided and rec.calls >= rec.probe_count:
            self.decided = True
            self.decision_at = rec.calls
            before = rec.checkpoint_best_feasible
            if not math.isfinite(rec.best_feasible):
                self.decision, fraction = "infeasible_explore", .75
            else:
                self.progress = (
                    max(0., (before - rec.best_feasible) / (1. + abs(before)))
                    if before is not None else 0.
                )
                if self.progress >= .002:
                    self.decision, fraction = "feasible_improving", .55
                else:
                    self.decision, fraction = "feasible_stalled", .30
            self.target = math.ceil(fraction * rec.budget)
            rec.stage_cap = self.target
        return rec.calls >= self.target


def ga_stage(grid, recorder, seed, population, allocation):
    random.seed(seed)
    np.random.seed(seed)
    controller = AllocationSwitch(recorder, allocation)
    ga = GA(
        cost_function=recorder,
        population_size=population,
        cost_diversity_metric="log_relative",
        exit_check="generations",
        exit_function=controller.check,
        number_of_generations=math.ceil(6 * recorder.budget / population) + 20,
        population_mutation="cost_diversity,parent_diversity",
        timeout=900,
    )
    for _ in range(grid.dimension):
        ga.add(*GEN_VOLTAGE_BOUNDS)
    output = ga.execute()
    return bool(output.success), (output.message if not output.success else ""), controller


def slsqp_stage(grid, recorder, seed, warm_start):
    rng = np.random.default_rng(seed + 18013)
    lo, hi = GEN_VOLTAGE_BOUNDS
    first = np.clip(np.asarray(warm_start, float), lo, hi)
    while recorder.calls < recorder.stage_cap:
        if recorder.local_starts == 0:
            initial = first
        elif recorder.local_starts % 3 == 0 and recorder.best_feasible_vector:
            initial = np.clip(np.asarray(recorder.best_feasible_vector) +
                              rng.normal(0.,.02,grid.dimension),lo,hi)
        else:
            initial = rng.uniform(lo,hi,grid.dimension)
        before = recorder.calls
        recorder.local_starts += 1
        try:
            result = minimize(recorder.strict, initial,
                              method="SLSQP",
                              bounds=[GEN_VOLTAGE_BOUNDS]*grid.dimension,
                              options={"maxiter":90,"ftol":1e-10,"disp":False})
            if not result.success:
                recorder.local_bad_exits += 1
        except BudgetExhausted:
            break
        except (ValueError,ArithmeticError,FloatingPointError):
            recorder.local_bad_exits += 1
        if recorder.calls == before:
            recorder.strict(rng.uniform(lo,hi,grid.dimension))


def differential_evolution_stage(grid,recorder,seed,population):
    factor=max(5,math.ceil(population/grid.dimension))
    try:
        differential_evolution(
            recorder.strict,
            [GEN_VOLTAGE_BOUNDS]*grid.dimension,
            popsize=factor,
            maxiter=math.ceil(recorder.budget/(factor*grid.dimension))+10,
            tol=0,atol=0,polish=False,seed=seed)
    except BudgetExhausted:
        pass


def cma_stage(grid,recorder,seed):
    import cma
    lo,hi=GEN_VOLTAGE_BOUNDS
    initial=np.clip(np.asarray(grid.reference),lo+1e-7,hi-1e-7)
    restarts=0
    while recorder.calls < recorder.budget and restarts<20:
        if restarts and recorder.best_penalized_vector is not None:
            initial=np.clip(np.asarray(recorder.best_penalized_vector),
                            lo+1e-7,hi-1e-7)
        es=cma.CMAEvolutionStrategy(initial.tolist(),.035,
               dict(bounds=[[lo]*grid.dimension,[hi]*grid.dimension],
                    popsize=8,seed=seed+37*restarts,
                    verbose=-9,verb_log=0,verb_disp=0))
        while not es.stop() and recorder.calls<recorder.budget:
            candidates=es.ask()
            costs=[]
            for x in candidates:
                if recorder.calls>=recorder.budget:break
                costs.append(recorder.strict(x))
            if len(costs)!=len(candidates):break
            es.tell(candidates,costs)
            recorder.cma_rounds+=1
        restarts+=1


def fill_actual_solver_budget(grid,recorder,seed):
    rng=np.random.default_rng(seed+77311)
    recorder.stage_cap=recorder.budget
    while recorder.calls<recorder.budget:
        recorder(rng.uniform(*GEN_VOLTAGE_BOUNDS,grid.dimension))
        recorder.random_fills+=1


def run(case,load,method,seed,budget,population):
    random.seed(seed)
    np.random.seed(seed)
    grid=GridProblem(case,load)
    recorder=PhysicalGridRecorder(grid,budget)
    started=time.perf_counter()
    success,error=True,""
    controller=None
    ga_calls=0
    try:
        if method=="gadapt_legacy":
            success,error,controller=ga_stage(grid,recorder,seed,population,"legacy")
            ga_calls=recorder.calls
        elif method=="slsqp_multistart":
            slsqp_stage(grid,recorder,seed,recorder.local_start_point())
        elif method in ("hybrid_fixed_half","hybrid_adaptive"):
            mode="fixed" if method=="hybrid_fixed_half" else "adaptive"
            success,error,controller=ga_stage(grid,recorder,seed,population,mode)
            ga_calls=recorder.calls
            recorder.stage_cap=budget
            slsqp_stage(grid,recorder,seed,recorder.local_start_point())
        elif method=="scipy_de":
            differential_evolution_stage(grid,recorder,seed,population)
        elif method=="cma_es":
            cma_stage(grid,recorder,seed)
        else:
            raise ValueError("unrecognized method")
        fill_actual_solver_budget(grid,recorder,seed)
    except Exception as exc:
        success=False
        error=(type(exc).__name__+": "+str(exc))[:500]
    physically_feasible=math.isfinite(recorder.best_feasible)
    return dict(
        case=case,load_factor=load,method=method,seed=seed,
        dimension=grid.dimension,
        optimizer_success=success,error=error,
        physically_feasible=physically_feasible,
        feasible_loss_mw=(recorder.best_feasible if physically_feasible else ""),
        min_observed_violation=(recorder.minimum_violation if
                                math.isfinite(recorder.minimum_violation) else ""),
        best_penalized=recorder.best_penalized,
        actual_solver_calls=recorder.calls,
        rejected_solver_requests=recorder.requests-recorder.calls,
        converged_solver_failures=recorder.failed_ac_calls,
        physically_feasible_calls=recorder.physical_feasible_calls,
        ga_physical_calls=ga_calls,
        local_physical_calls=(recorder.calls-ga_calls-recorder.random_fills if
                              method in ("slsqp_multistart","hybrid_fixed_half","hybrid_adaptive")
                              else 0),
        local_starts=recorder.local_starts,
        local_failed_terminations=recorder.local_bad_exits,
        cma_generations=recorder.cma_rounds,
        random_filler_evaluations=recorder.random_fills,
        adaptive_decision=(controller.decision if controller else ""),
        adaptive_decision_at_call=(controller.decision_at if controller else ""),
        adaptive_progress=(controller.progress if controller and
                           controller.progress is not None else ""),
        elapsed_sec=round(time.perf_counter()-started,3),
        best_physical_feasible_voltages=(
            ";".join(f"{v:.10f}" for v in recorder.best_feasible_vector)
            if recorder.best_feasible_vector is not None else ""))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seeds",type=int,default=6)
    p.add_argument("--seed-start",type=int,default=200)
    p.add_argument("--budget",type=int,default=180)
    p.add_argument("--population",type=int,default=24)
    p.add_argument("--loads",nargs="+",type=float,default=[1.,1.1])
    p.add_argument("--case",choices=("ieee118",),default="ieee118")
    p.add_argument("--output",default="ieee118_iteration6.csv")
    args=p.parse_args()
    if args.seeds<1 or args.budget<4*args.population:
        p.error("seeds>=1 and budget>=4*population are required")
    rows=[]
    for factor in args.loads:
        for seed in range(args.seed_start,args.seed_start+args.seeds):
            for method in METHODS:
                result=run(args.case,factor,method,seed,args.budget,args.population)
                rows.append(result)
                print("RUN",result,flush=True)
        for method in METHODS:
            subset=[v for v in rows if v["load_factor"]==factor and v["method"]==method]
            good=[v["feasible_loss_mw"] for v in subset if
                  v["physically_feasible"] and v["optimizer_success"]]
            violations=[v["min_observed_violation"] for v in subset
                        if v["min_observed_violation"] != ""]
            print("SUMMARY",factor,method,"feasible",len(good),"/",len(subset),
                  "median_loss_mw",statistics.median(good) if good else "NA",
                  "median_min_violation",statistics.median(violations) if violations else "NA",
                  "actual_solver_calls_range",(min(v["actual_solver_calls"] for v in subset),
                                               max(v["actual_solver_calls"] for v in subset)),
                  "median_runtime_sec",statistics.median(v["elapsed_sec"] for v in subset),
                  flush=True)
    with open(args.output,"w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if any(r["actual_solver_calls"]!=args.budget for r in rows):
        print("ALERT actual physical budgets differ, keep failure rows",flush=True)
    if any(not r["optimizer_success"] for r in rows):
        print("ALERT optimization failures, keep all failures",flush=True)


if __name__=="__main__":main()
