#!/usr/bin/env python3
"""Read-only I64-I2 rare-feasibility-failure and bootstrap Monte Carlo audit.

Loads 16 pinned original I/I2 run parts using the existing archive verifier,
or a *derived, explicitly identified* I64-I2 8x3x30 loss+feasibility fixture.
Never calls optimizer, AC power-flow or an experimental objective.

  python i64_i2_rare_failure_audit.py --repo-root /path/to/gadapt --output audit.json
  python i64_i2_rare_failure_audit.py --derived /tmp/pinned-derived.npz --output audit.json

Do NOT use for confirmatory tests, new population-level inference, or novelty.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

REG_C3 = -0.12530676111239542
REG_TSTAR = 3.4133099733799344
REG_UPPER = -0.00038961539195656036
SEEDS_20K = tuple(range(68, 80))
SEEDS_100K = (68, 69, 70)
N_CELLS, N_CONFIGS, N_SEEDS = 8, 3, 30
CONFIGS = ("gadapt", "gadapt_hyb", "ipop")
DOMINANT_CELL = 3  # case39/j=3


def validate(loss: np.ndarray, feasible: np.ndarray) -> None:
    if loss.shape != (N_CELLS, N_CONFIGS, N_SEEDS):
        raise ValueError(f"loss shape must be (8,3,30), got {loss.shape}")
    if feasible.shape != loss.shape:
        raise ValueError("feasible shape mismatch")
    if not np.all(np.isfinite(loss)) or not np.all((loss >= 0) & (loss <= 1)):
        raise ValueError("nonfinite or out-of-range losses")
    if not np.all(np.isin(feasible, [0.0, 1.0])):
        raise ValueError("feasibility must be binary")
    if not np.all(loss[feasible == 0] == 1.0):
        raise ValueError("nonfeasible run must map to L=1")
    c = cvar_by_config(loss, 3)
    if not np.isclose(c[2] - c[1], REG_C3, atol=1e-12, rtol=0):
        raise ValueError("derived arrays do NOT reproduce original I64-I2 frozen contrast")


def load_archived(repo_root: Path) -> tuple[np.ndarray, np.ndarray]:
    from i64_i2_bootstrap_replay import arrays_from_repo

    arr, frozen = arrays_from_repo(repo_root)  # checks all sixteen original Git blobs
    if not math.isclose(frozen['contrasts']['CVaR(IPOP)-CVaR(H)']['estimate'], REG_C3,
                        rel_tol=0, abs_tol=1e-14):
        raise ValueError("original analysis is no longer the frozen pinned study")
    loss = np.stack([np.stack([arr[(ci, cfg)][:, 0] for cfg in CONFIGS])
                     for ci in range(N_CELLS)])
    feasible = np.stack([np.stack([arr[(ci, cfg)][:, 1] for cfg in CONFIGS])
                         for ci in range(N_CELLS)])
    validate(loss, feasible)
    return loss, feasible


def load_derived(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with np.load(path, allow_pickle=False) as fixture:
        if set(fixture.files) != {'loss', 'feasible'}:
            raise ValueError("derived file must have only loss and feasible arrays")
        loss = fixture['loss'].copy()
        feasible = fixture['feasible'].copy()
    validate(loss, feasible)
    return loss, feasible


def binomial_tail(n: int, p: float, k: int, *, upper: bool) -> float:
    """P(X>=k) if upper; P(X<=k) otherwise, X~Binom(n,p)."""
    if upper:
        return sum(math.comb(n, j) * p**j * (1-p)**(n-j) for j in range(k, n+1))
    return sum(math.comb(n, j) * p**j * (1-p)**(n-j) for j in range(k+1))


def clopper_pearson(k: int, n: int, alpha: float = .05) -> tuple[float, float]:
    """Exact central two-sided binomial interval; stdlib only."""
    if not 0 <= k <= n or n <= 0 or not 0 < alpha < 1:
        raise ValueError("invalid exact-binomial parameters")
    if k == 0:
        low = 0.0
    else:
        a, b = 0., 1.
        for _ in range(80):
            m = (a+b)/2
            if binomial_tail(n, m, k, upper=True) < alpha/2: a = m
            else: b = m
        low = (a+b)/2
    if k == n:
        high = 1.0
    else:
        a, b = 0., 1.
        for _ in range(80):
            m = (a+b)/2
            if binomial_tail(n, m, k, upper=False) > alpha/2: a = m
            else: b = m
        high = (a+b)/2
    return low, high


def exact_paired_feasibility_test(hybrid_feasible: np.ndarray,
                                  ipop_feasible: np.ndarray) -> dict:
    if hybrid_feasible.shape != (30,) or ipop_feasible.shape != (30,):
        raise ValueError("exact paired feasibility requires exactly 30 paired seeds")
    hybrid_only = int(np.sum((hybrid_feasible == 1) & (ipop_feasible == 0)))
    ipop_only = int(np.sum((hybrid_feasible == 0) & (ipop_feasible == 1)))
    discordant = hybrid_only + ipop_only
    p_two = (min(1., 2*sum(math.comb(discordant,j) for j in range(min(hybrid_only,ipop_only)+1))
                      / (2**discordant)) if discordant else 1.)
    p_one = (sum(math.comb(discordant,j) for j in range(hybrid_only+1))
             / 2**discordant if discordant else 1.)
    return {'hybrid_only_feasible':hybrid_only, 'ipop_only_feasible':ipop_only,
            'discordant_pairs':discordant, 'mcnemar_two_sided_exact_p':p_two,
            'one_sided_more_ipop_feasible_p':p_one,
            'scope':'post-hoc selected cell, feasibility only; NOT CVaR hypothesis test'}


def cvar_by_config(loss: np.ndarray, tail_k: int) -> np.ndarray:
    if not 1 <= tail_k <= loss.shape[-1]:
        raise ValueError('bad tail count')
    return np.sort(loss, axis=-1)[..., -tail_k:].mean(axis=-1).mean(axis=0)


def boot_endpoints(loss: np.ndarray, feasible: np.ndarray,
                   *, seed: int, repetitions: int, batch: int = 2500) -> dict:
    """Original I64-I2 4-contrast simultaneous max-t, batched for memory."""
    rng = np.random.default_rng(seed)
    cv = np.sort(loss, axis=-1)[..., -3:].mean(axis=-1).mean(axis=0)
    pf = feasible.mean(axis=-1).mean(axis=0)
    point = np.array([cv[0]-cv[1], pf[1]-pf[0], cv[2]-cv[1], pf[1]-pf[2]])
    records = []
    for start in range(0, repetitions, batch):
        count = min(batch, repetitions-start)
        indices = rng.integers(0, 30, size=(count,8,30))
        idx = indices[:,:,None,:]
        ls = np.take_along_axis(loss[None,:,:,:], idx, axis=-1)
        fs = np.take_along_axis(feasible[None,:,:,:], idx, axis=-1)
        c = np.sort(ls, axis=-1)[..., -3:].mean(axis=-1).mean(axis=1)
        p = fs.mean(axis=-1).mean(axis=1)
        records.append(np.column_stack((c[:,0]-c[:,1],p[:,1]-p[:,0],
                                        c[:,2]-c[:,1],p[:,1]-p[:,2])))
    boot = np.concatenate(records,axis=0)
    se = boot.std(axis=0, ddof=1)
    active = (se > 0) & (np.ptp(boot,axis=0) > 0)
    tstar = float(np.quantile(np.max(np.abs(boot[:,active]-point[active]) / se[active],axis=1), .975))
    upper_c3 = float(point[2] + tstar*se[2])
    return {'seed': seed, 'repetitions': repetitions, 'tstar':tstar,
            'c3_point': float(point[2]), 'c3_upper_simultaneous':upper_c3,
            'c3_percentile_97_5':float(np.quantile(boot[:,2],.975)),
            'bootstrap_fraction_c3_nonnega':float(np.mean(boot[:,2]>=0)),
            'registered_negative_verdict_preserved':upper_c3 < 0}


def audit(loss: np.ndarray, feasible: np.ndarray, *, seeds_20k=SEEDS_20K,
          seeds_100k=SEEDS_100K, include_100k=True) -> dict:
    validate(loss, feasible)
    rare = feasible[DOMINANT_CELL]
    hm = int(np.sum(rare[1] == 0)); im = int(np.sum(rare[2] == 0))
    original = cvar_by_config(loss,3)
    cell_contrasts = np.sort(loss,axis=-1)[...,-3:].mean(axis=-1)
    dominant = float((cell_contrasts[DOMINANT_CELL,2]-cell_contrasts[DOMINANT_CELL,1])/8)
    c3 = float(original[2]-original[1])
    tail = []
    for k in (1,2,3,4,5,6,9,15,30):
        vals = cvar_by_config(loss,k)
        diff = float(vals[2]-vals[1])
        cell = np.sort(loss[DOMINANT_CELL],axis=-1)[:,-k:].mean(axis=-1)
        contribution = float((cell[2]-cell[1])/8)
        tail.append({'worst_k_of_30':k,'c3_ipop_minus_hybrid':diff,
                     'dominant_cell_share_of_signed_contrast':contribution/diff if diff else None})
    seed_delete = []
    for s in range(30):
        mask=np.arange(30)!=s
        sorted_losses=np.sort(loss[:,:,mask],axis=-1)[:,:,-3:].mean(axis=-1).mean(axis=0)
        seed_delete.append({'seed_index':s+1,'c3':float(sorted_losses[2]-sorted_losses[1]),
                            'deleted_hybrid_infeasible_in_dominant':bool(feasible[DOMINANT_CELL,1,s]==0)})
    stability = [boot_endpoints(loss,feasible,seed=seed,repetitions=20000)
                 for seed in seeds_20k]
    if include_100k:
        stability.extend(boot_endpoints(loss,feasible,seed=seed,repetitions=100000)
                         for seed in seeds_100k)
    original_seed = next((x for x in stability if x['seed']==68 and x['repetitions']==20000),None)
    if original_seed is not None and not (abs(original_seed['tstar']-REG_TSTAR) < 1e-10 and
                                           abs(original_seed['c3_upper_simultaneous']-REG_UPPER)<1e-10):
        raise ValueError("original seed=68 20k max-t could not be reconstructed")
    prob_fewer_3 = binomial_tail(30, .1, 2, upper=False)
    return {
        'study':'archived I64-I2, 8 fixed cells, 30 paired seeds each',
        'status':'post-hoc diagnostic, no new PF/optimizer execution, not preregistered',
        'source_analysis_blob':'2b38375126a43128dba37aaf7966b92eb6df8691',
        'original_c3':c3, 'dominant_cell_contribution':dominant,
        'dominant_cell_share':dominant/c3,
        'dominant_cell':{
            'label':'case39/j=3','hybrid_infeasible':hm,'ipop_infeasible':im,
            'hybrid_miss_95pct_CP':clopper_pearson(hm,30),
            'ipop_miss_95pct_CP':clopper_pearson(im,30),
            'paired_feasibility':exact_paired_feasibility_test(rare[1],rare[2]),
            'empirical_seed_bootstrap_Pr_less_than_3_hybrid_misses':prob_fewer_3,
            'note':'When bootstrapping 30 seeds with 3 observed hybrid misses, a resample has fewer than three misses in 41.1% of draws. This is not a p-value for the CVaR contrast.'},
        'monte_carlo_sensitivity':{
            'reproductions':stability,
            'all_simultaneous_upper_negative':all(x['registered_negative_verdict_preserved'] for x in stability),
            'range_simultaneous_upper':[min(x['c3_upper_simultaneous'] for x in stability),
                                        max(x['c3_upper_simultaneous'] for x in stability)]},
        'posthoc_tail_count_sensitivity':tail,
        'leave_one_paired_seed_out':{
            'range_c3':[min(x['c3'] for x in seed_delete),max(x['c3'] for x in seed_delete)],
            'dominant_failure_seed_deletions':[x for x in seed_delete if x['deleted_hybrid_infeasible_in_dominant']]},
        'limits':['Exact McNemar test addresses feasibility occurrence in a post-hoc selected single cell, not original 4-contrast CVaR test.',
                  'Clopper-Pearson intervals are marginal binomial intervals conditional on independent seeds; they are not simultaneous or cell-selection adjusted.',
                  'Reusing bootstrap on fixed eight cells does not account for selection of problem families, physical network uncertainty, or historical model bias.',
                  'Any changes in original threshold or sample composition are post-hoc and not revised H64h2 decisions.']
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    src=p.add_mutually_exclusive_group(required=True)
    src.add_argument('--repo-root',type=Path)
    src.add_argument('--derived',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--no-100k',action='store_true')
    opts=p.parse_args()
    loss,feasible = load_archived(opts.repo_root) if opts.repo_root else load_derived(opts.derived)
    result=audit(loss,feasible,include_100k=not opts.no_100k)
    result['source_mode']='original_git_blob_pinned_archives' if opts.repo_root else 'derived_loss_feasibility_npz_not_original_archives'
    data=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if opts.output: opts.output.write_text(data,encoding='utf-8')
    else: print(data,end='')

if __name__=='__main__': main()
