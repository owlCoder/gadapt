#!/usr/bin/env python3
"""Read-only exact-original-method 20k paired bootstrap replay for I64-I2.

Requires a COMPLETE pinned owlCoder/gadapt clone and numpy. No optimizer or PF.
This file was unit-tested synthetically but NOT run on the full archived inputs
in the 2026-11-03 connector review (source file transfer limitation).

  python i64_i2_bootstrap_replay.py --repo-root /path/to/gadapt \
    --output bootstrap_replay.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from i64_i2_cell_influence import (
    I_BLOBS, I2_BLOBS, ANALYSIS_BLOB, CONTRASTS, CONFIGS,
    N_CELLS, N_SEEDS, read_pinned, by_cell, loss_and_feasible,
)

BOOTSTRAPS = 20_000
BOOT_SEED = 68


def arrays_from_repo(root: Path) -> tuple[dict, dict]:
    base=root / 'research' / 'results'
    arr={}
    for ci in range(N_CELLS):
        original=read_pinned(base/f'iteration64_i/run_part_{ci}.json.gz',I_BLOBS[ci])['records']
        hybrid=read_pinned(base/f'iteration64_i2/run2_part_{ci}.json.gz',I2_BLOBS[ci])['records']
        rs={'gadapt':[r for r in original if r['task']['config']=='gadapt'],
            'ipop':[r for r in original if r['task']['config']=='ipop'],
            'gadapt_hyb':hybrid}
        by_cell(rs,ci)  # validates all paired seed IDs, budgets, archived witness flags
        for config in CONFIGS:
            rows=sorted(rs[config],key=lambda r:r['task']['s'])
            arr[(ci,config)] = np.array([loss_and_feasible(r) for r in rows],dtype=np.float64)
    return arr,read_pinned(base/'iteration64_i2/analysis.json.gz',ANALYSIS_BLOB)


def cvar90(values: np.ndarray) -> float:
    """Original I.cvar logic, with numpy mean of top ceil(0.1*N)."""
    return float(np.mean(sorted(values)[-max(1,int(np.ceil(.1*len(values)))):]))


def contrasts_at(arr: dict, indexes: dict) -> np.ndarray:
    # I64-I2 used equal cell weights and paired resampling indices per cell
    def cv(c,ci):
        return cvar90(arr[(ci,c)][indexes[ci],0])
    def pf(c,ci):
        return arr[(ci,c)][indexes[ci],1].mean()
    mean=lambda vals: sum(vals)/N_CELLS
    return np.array([
        mean([cv('gadapt',ci) for ci in range(N_CELLS)])-
        mean([cv('gadapt_hyb',ci) for ci in range(N_CELLS)]),
        mean([pf('gadapt_hyb',ci) for ci in range(N_CELLS)])-
        mean([pf('gadapt',ci) for ci in range(N_CELLS)]),
        mean([cv('ipop',ci) for ci in range(N_CELLS)])-
        mean([cv('gadapt_hyb',ci) for ci in range(N_CELLS)]),
        mean([pf('gadapt_hyb',ci) for ci in range(N_CELLS)])-
        mean([pf('ipop',ci) for ci in range(N_CELLS)])
    ],dtype=np.float64)


def reproduce(arr: dict, frozen: dict, *, replicates: int=BOOTSTRAPS, seed: int=BOOT_SEED) -> dict:
    if any(not np.all(np.isfinite(v)) for v in arr.values()):
        raise ValueError("Nonfinite input per-seed loss or feasibility")
    full={ci:np.arange(N_SEEDS) for ci in range(N_CELLS)}
    point=contrasts_at(arr,full)
    rng=np.random.default_rng(seed)
    boots=np.array([contrasts_at(arr,{ci:rng.integers(0,N_SEEDS,N_SEEDS) for ci in range(N_CELLS)})
                    for _ in range(replicates)])
    finite=bool(np.all(np.isfinite(point)) and np.all(np.isfinite(boots)))
    if not finite:
        raise ValueError('Nonfinite statistic or bootstrap sample')
    se=boots.std(axis=0,ddof=1)
    active=(se>0)&(np.ptp(boots,axis=0)>0)
    t=float(np.quantile(np.max(np.abs(boots[:,active]-point[active])/se[active],axis=1),.975)) if active.any() else 0.
    lower=np.full(4,-1.)
    upper=np.ones(4)
    lower[active]=point[active]-t*se[active]
    upper[active]=point[active]+t*se[active]
    u=1-(.025/4)**(1/(N_CELLS*N_SEEDS))
    for index,(a,b) in [(1,('gadapt_hyb','gadapt')),(3,('gadapt_hyb','ipop'))]:
        if all(np.all(arr[(ci,a)][:,1]-arr[(ci,b)][:,1]==0) for ci in range(N_CELLS)):
            lower[index]=-u
            upper[index]=u
    rows={name:{'estimate':float(point[i]),'lower':float(lower[i]),'upper':float(upper[i])}
          for i,name in enumerate(CONTRASTS)}
    checks=[]
    if replicates==BOOTSTRAPS and seed==BOOT_SEED:
        for k,name in enumerate(CONTRASTS):
            for metric in ('estimate','lower','upper'):
                want=frozen['contrasts'][name][metric]
                actual=rows[name][metric]
                checks.append({'contrast':name,'metric':metric,'difference':actual-want,
                               'match_tol_1e-10':abs(actual-want)<=1e-10})
        checks.append({'metric':'tstar','difference':t-frozen['tstar'],
                       'match_tol_1e-10':abs(t-frozen['tstar'])<=1e-10})
    return {'source':'16 original pinned I/I2 run parts plus original I2 analysis',
            'repetitions':replicates,'seed':seed,'tstar':t,'point_and_simultaneous_intervals':rows,
            'source_checks':checks,'all_original_values_match':bool(checks) and all(x['match_tol_1e-10'] for x in checks),
            'limitations':['Bootstrap replays original archived measurements only; no optimizer/PF execution.',
                           'Original inference is conditional on eight fixed cells.']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    arr,frozen=arrays_from_repo(args.repo_root)
    result=reproduce(arr,frozen)
    text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.output:args.output.write_text(text,encoding='utf-8')
    else: print(text,end='')
    if not result['all_original_values_match']:
        raise SystemExit('STOP: historical bootstrap values DID NOT reproduce; preserve report for diagnosis')

if __name__=='__main__':main()
