"""I64-E4: compensatory mutation on the E cells, paired with the archived E records (spec: research/ITERATION64_E4_SPEC.md).
Frozen E files are not modified: this module registers the extra runner and has its own execute/analysis.

  python research/i64/e2_study.py run [workers] | analyse
"""
import gzip
import hashlib
import json
import math
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MBENCH = os.environ["MBENCH"]
for p in (HERE, MBENCH, os.path.dirname(os.path.dirname(HERE))):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np  # noqa: E402

import e_algos  # noqa: E402
import e_common as ec  # noqa: E402
import e_study as es  # noqa: E402

OUT = os.environ.get("E4_OUT", os.path.join(os.path.dirname(HERE), "results", "iteration64_e4"))
E_OUT = es.OUT  # archived E results
N_SEEDS = es.N_SEEDS
B = es.B


def _comp_runner(mode):
    def run(g, d, seed, lo=0.0, hi=1.0):
        """E4: the E GAdapt-M configuration with compensatory_mutation=mode (native domain, no stagnation exit, restart if the library returns)."""
        from gadapt.ga import GA
        gx = e_algos._native(g, lo, hi)

        def single(rng, k):
            random.seed(int(rng.integers(1, 2 ** 31)))
            np.random.seed(int(rng.integers(1, 2 ** 31)))
            ga = GA(cost_function=gx, population_size=64,
                    population_mutation="cost_diversity, variable_columnar_diversity, parent_diversity, random",
                    candidate_solution_mutation="variable_columnar_diversity, random",
                    decision_variable_mutation="variable_columnar_diversity,cost_diversity, random",
                    percentage_of_mutation_candidate_solutions=60, percentage_of_mutation_decision_variables=60,
                    exit_check="generations", number_of_generations=10 ** 6, keep_elitism_percentage=50,
                    parent_selection="roulette_wheel", crossover_probability=0.5, immigration_number=0, crossover="blending",
                    ensure_unique_individuals=False, logging=False, timeout=10 ** 7, compensatory_mutation=mode)
            for _ in range(d):
                ga.add(min_value=float(lo), max_value=float(hi), step=None)
            result = ga.execute()
            if not result.success:
                raise RuntimeError("GA.execute() returned success=False (technical failure, not a restart)")
        e_algos._restart_loop(single, seed, g)
    return run


MODES = {"gadapt_cg": "gated", "gadapt_cu": "ungated", "gadapt_cp": "permuted", "gadapt_cr": "resample"}
for _name, _mode in MODES.items():
    e_algos.RUNNERS[_name] = _comp_runner(_mode)
es.NATIVE = tuple(es.NATIVE) + tuple(MODES)


def run_task2(task):
    for _n, _m in MODES.items():  # also in spawned workers
        e_algos.RUNNERS[_n] = _comp_runner(_m)
    es.NATIVE = tuple(n for n in es.NATIVE if n not in MODES) + tuple(MODES)
    return es.run_task(task)


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name + ".json.gz")


def save(name, data):
    with gzip.open(path(name), "wt") as fh:
        json.dump(data, fh)


def load(name):
    with gzip.open(path(name), "rt") as fh:
        return json.load(fh)


def stage_run(workers):
    if os.path.exists(path("run")):
        raise SystemExit("EXISTS: run exists (create-once)")
    from multiprocessing import Pool
    em = es.load("manifest_run")
    cur = es.manifest("e2")
    if json.loads(json.dumps(em["pip_freeze"])) != json.loads(json.dumps(cur["pip_freeze"])) or em["python"] != cur["python"]:
        raise SystemExit("STOP: environment differs from the one that produced the archived E records")
    # E provenance: the archived E raw data must be the ones published by E (hash of every part recorded here)
    parts = {f"run_part_{ci}": sha(os.path.join(E_OUT, f"run_part_{ci}.json.gz")) for ci in range(len(es.CELLS))}
    allrecs = []
    for ci in range(len(es.CELLS)):
        part = f"run4_part_{ci}"
        if os.path.exists(path(part)):
            allrecs.extend(load(part)["records"])
            continue
        tasks = [dict(config=cfg, params=None, cell=ci, seed=es.seed_of("run", ci, s), purpose="run") for s in range(1, N_SEEDS + 1) for cfg in MODES]
        with Pool(workers, maxtasksperchild=1) as pool:
            records = list(pool.imap(run_task2, tasks, chunksize=1))
        for i, r in enumerate(records):
            if not r.get("ok"):
                with Pool(1, maxtasksperchild=1) as pool:
                    again = pool.apply(run_task2, (tasks[i],))
                again["rerun"], again["first_attempt"] = True, r
                records[i] = again
        bad = [r for r in records if not r.get("ok")]
        if bad:
            raise SystemExit(f"STOP: {len(bad)} E2 runs failed technically twice: {bad[0].get('error')}")
        save(part, dict(records=records))
        allrecs.extend(records)
        print("cell", ci, es.CELLS[ci], "done", flush=True)
    freeze = subprocess.run(["git", "-C", os.path.dirname(os.path.dirname(HERE)), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    save("run", dict(records=allrecs, e_parts_sha256=parts, git_head=freeze))


def cvar(values, share=0.1):
    k = max(1, int(math.ceil(share * len(values))))
    return float(np.mean(sorted(values)[-k:]))


def analyse():
    if os.path.exists(path("analysis")):
        raise SystemExit("EXISTS: analysis exists (create-once)")
    d2 = load("run")
    for part, h in d2["e_parts_sha256"].items():
        if sha(os.path.join(E_OUT, part + ".json.gz")) != h:
            raise SystemExit(f"STOP: archived E part {part} changed since E4 ran")
    norm = es.load("normalizers")
    n_cells = len(es.CELLS)
    w_all = {}
    for ci, (name, d, v) in enumerate(es.CELLS):
        dims = next(len(dd) for n_, _, _, _, dd in es.FUNCS if n_ == name)
        w_all[ci] = (1 / 9) / dims / len(es.VARIANTS)
    want = ("gadapt", "ipop", "cma", "bipop", "de")
    raw = {}

    def add(r):
        ci, c, s = r["task"]["cell"], r["task"]["config"], r["task"]["seed"]
        n = norm[f"{es.CELLS[ci][0]}|{es.CELLS[ci][1]}"]

        def gp(f):
            if not math.isfinite(f):
                return math.inf
            if f < n["f_star"] - 1e-12 * n["s"]:
                raise SystemExit(f"STOP: value below f* in cell {ci}")
            return max(0.0, (f - n["f_star"]) / n["s"])
        g = gp(r["best_f"])
        area = 0.0
        for tau in es.TAUS:
            hit = next((cc for cc, f in r["events"] if gp(f) <= tau), None)
            if hit is not None:
                area += (B - hit + 1) / B
        raw.setdefault((ci, c), {})[s] = (area / len(es.TAUS), 1.0 if math.isinf(g) else g / (1 + g), g)
    for ci in range(n_cells):
        for r in es.load(f"run_part_{ci}")["records"]:
            if r["task"]["config"] in want:
                add(r)
    for r in d2["records"]:
        assert r["ok"] and r["calls"] == B
        add(r)
    arr = {}
    for k, v in raw.items():
        assert sorted(v) == [es.seed_of("run", k[0], s) for s in range(1, N_SEEDS + 1)], k
        arr[k] = np.array([v[s] for s in sorted(v)])
    rot = [ci for ci in range(n_cells) if es.CELLS[ci][2] == "rot"]
    nonrot = [ci for ci in range(n_cells) if es.CELLS[ci][2] != "rot"]

    def wsum(cells, fn):
        tot = sum(w_all[ci] for ci in cells)
        return sum(w_all[ci] * fn(ci) for ci in cells) / tot

    def stats(idx):
        A = lambda c, ci: arr[(ci, c)][idx[ci], 0].mean()
        CV = lambda c, ci: cvar(list(arr[(ci, c)][idx[ci], 1]))
        G = "gadapt_cg"
        return np.array([wsum(rot, lambda ci: A(G, ci) - A("gadapt", ci)),
                         0.8 * wsum(rot, lambda ci: CV("gadapt", ci)) - wsum(rot, lambda ci: CV(G, ci)),
                         wsum(nonrot, lambda ci: A(G, ci) - A("gadapt", ci)),
                         1.5 * wsum(nonrot, lambda ci: CV("gadapt", ci)) - wsum(nonrot, lambda ci: CV(G, ci)),
                         wsum(rot, lambda ci: A(G, ci) - A("gadapt_cp", ci)),
                         wsum(rot, lambda ci: A(G, ci) - A("gadapt_cr", ci)),
                         wsum(rot, lambda ci: A(G, ci) - A("ipop", ci))])
    names = ["dA_rot(G-M)", "0.8*CVaR_rot(M)-CVaR_rot(G)", "dA_nonrot(G-M)", "1.5*CVaR_nonrot(M)-CVaR_nonrot(G)", "dA_rot(G-permuted)", "dA_rot(G-resample)", "dA_rot(G-IPOP)"]
    N = N_SEEDS
    point = stats({ci: np.arange(N) for ci in range(n_cells)})
    R = int(os.environ.get("E4_BOOT", "20000"))
    rng = np.random.default_rng(69)
    boots = np.array([stats({ci: rng.integers(0, N, N) for ci in range(n_cells)}) for _ in range(R)])
    finite = bool(np.all(np.isfinite(point)) and np.all(np.isfinite(boots)))
    se = boots.std(axis=0, ddof=1) if finite else np.full(len(point), np.nan)
    blocked = (not finite) or bool(np.any(se <= 0))
    if blocked:
        lo = hi = np.full(len(point), np.nan); t = float("nan")
    else:
        t = float(np.quantile(np.max(np.abs(boots - point) / se, axis=1), 0.95))
        lo, hi = point - t * se, point + t * se
    res = {n: dict(estimate=float(p), lower=float(a), upper=float(b)) for n, p, a, b in zip(names, point, lo, hi)}
    cm_rot = wsum(rot, lambda ci: cvar(list(arr[(ci, "gadapt")][:, 1])))

    def tri(sup, opp):
        return "blocked" if blocked else ("supported" if sup else ("opposite" if opp else "undecided"))
    L = lambda i: res[names[i]]["lower"]
    U = lambda i: res[names[i]]["upper"]
    k1 = tri(L(0) > 0 and L(1) >= 0 and cm_rot > 0, U(0) < 0 or U(1) < 0)
    k2 = tri(L(2) >= -0.05 and L(3) >= 0, U(2) < -0.05 or U(3) < 0)
    k3 = tri(L(4) > 0, U(4) < 0)
    k4 = tri(L(5) > 0, U(5) < 0)
    k5 = tri(L(6) > -0.05, U(6) < -0.05)
    cfgs = ("gadapt", "gadapt_cg", "gadapt_cu", "gadapt_cp", "gadapt_cr", "ipop", "cma", "bipop", "de")
    agg = {}
    for var, cells in (("orig", [c for c in range(n_cells) if es.CELLS[c][2] == "orig"]), ("shift", [c for c in range(n_cells) if es.CELLS[c][2] == "shift"]), ("rot", rot)):
        agg[var] = {c: dict(A=wsum(cells, lambda ci: arr[(ci, c)][:, 0].mean()), cvar90=wsum(cells, lambda ci: cvar(list(arr[(ci, c)][:, 1]))),
                            median_gap=wsum(cells, lambda ci: float(np.median(arr[(ci, c)][:, 2])))) for c in cfgs if (cells[0], c) in arr}
    out = dict(blocked=blocked, tstar=t, alpha=0.05, bootstrap=R, contrasts=res, H64k1=k1, H64k2=k2, H64k3=k3, H64k4=k4, H64k5=k5,
               supported_core=bool(k1 == "supported" and k2 == "supported" and k3 == "supported" and k4 == "supported"), CVaR_rot_M=float(cm_rot),
               aggregate_by_variant=agg, e_parts_sha256_checked=True)
    save("analysis", out)
    save("manifest_analysis", es.manifest("e4"))
    print(json.dumps(out, indent=1)[:5000])


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else ""
    if st == "run":
        stage_run(int(sys.argv[2]) if len(sys.argv) > 2 else 8)
    elif st == "analyse":
        analyse()
    else:
        print(__doc__)
