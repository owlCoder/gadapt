#!/usr/bin/env python3
"""Exploratory, archived-data-only, matched I64-I2 cell-dropout bootstrap.

NOT preregistered or multiplicity adjusted for selecting a dominant cell after
seeing outcomes. This is not a replacement for frozen H64h2. No optimizers/PF.

From a full git clone:
  python i64_i2_posthoc_dropout_bootstrap.py --repo-root /path/to/gadapt
From already independently source-checked, derivative loss array:
  python i64_i2_posthoc_dropout_bootstrap.py --derived-npz ARCHIVED_LOSSES.npz
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from i64_i2_bootstrap_replay import arrays_from_repo
from i64_i2_cell_influence import CONFIGS, CONTRASTS, N_CELLS, N_SEEDS

EXPECTED_FROZEN_POINTS = np.array([
    -0.07989170831004905,
    -0.004166666666666652,
    -0.12530676111239542,
    -0.029166666666666563,
])
DOMINANT_ORPD_CELL = 3 # case39/j=3, found in post hoc data inspection


def source_arrays(repo_root: Path | None, derived_npz: Path | None) -> tuple[dict, str]:
    if (repo_root is None) == (derived_npz is None):
        raise ValueError('Choose exactly one of --repo-root or --derived-npz')
    if repo_root is not None:
        arr, _frozen = arrays_from_repo(repo_root)
        label='16 pinned original compressed I/I2 archived parts'
    else:
        with np.load(derived_npz,allow_pickle=False) as z:
            loss=np.asarray(z['loss'])
            feas=np.asarray(z['feasible'])
        if loss.shape != (N_CELLS,len(CONFIGS),N_SEEDS) or feas.shape != loss.shape:
            raise ValueError('Expected 8x3x30 archived paired outcomes')
        arr={(ci,c):np.column_stack((loss[ci,j],feas[ci,j]))
             for ci in range(N_CELLS) for j,c in enumerate(CONFIGS)}
        label='preverified derivative of 16 original Git source run parts'
    full=point_contrasts(arr, tuple(range(N_CELLS)),
                         {ci:np.arange(N_SEEDS) for ci in range(N_CELLS)})
    if not np.allclose(full,EXPECTED_FROZEN_POINTS,atol=1e-12,rtol=0):
        raise ValueError('Archived outcome transfer fails original I2 point test')
    return arr,label


def cvar90(v: np.ndarray) -> float:
    return float(np.mean(sorted(v)[-max(1,math.ceil(len(v)*.10)):]))


def point_contrasts(arr: dict, cell_ids: tuple[int,...], indexes: dict) -> np.ndarray:
    if not cell_ids or len(set(cell_ids)) != len(cell_ids):
        raise ValueError('Cell selection must be nonempty and unique')
    if any(ci<0 or ci>=N_CELLS for ci in cell_ids):
        raise ValueError('Unknown source cell')
    out=[]
    for ci in cell_ids:
        ix=indexes[ci]
        if len(ix)!=N_SEEDS:
            raise ValueError('Bad paired sample shape')
        vals={}
        for cfg in CONFIGS:
            cell=arr[(ci,cfg)]
            if cell.shape!=(N_SEEDS,2) or not np.isfinite(cell).all():
                raise ValueError('Bad archived cell array')
            vals[cfg]=(cvar90(cell[ix,0]),float(cell[ix,1].mean()))
        m,h,i=vals['gadapt'],vals['gadapt_hyb'],vals['ipop']
        out.append([m[0]-h[0],h[1]-m[1],i[0]-h[0],h[1]-i[1]])
    return np.mean(out,axis=0)


def bootstrap(arr: dict,cell_ids: tuple[int,...], *, seed: int=68,reps:int=20000)->dict:
    full={ci:np.arange(N_SEEDS) for ci in cell_ids}
    point=point_contrasts(arr,cell_ids,full)
    rng=np.random.default_rng(seed)
    boots=np.array([point_contrasts(arr,cell_ids,
                    {ci:rng.integers(0,N_SEEDS,N_SEEDS) for ci in cell_ids})
                    for _ in range(reps)])
    se=boots.std(axis=0,ddof=1)
    active=(se>0)&(np.ptp(boots,axis=0)>0)
    t=(float(np.quantile(np.max(np.abs(boots[:,active]-point[active])/se[active],axis=1),.975))
       if active.any() else 0.0)
    lower=np.full(4,-1.0);upper=np.ones(4)
    lower[active]=point[active]-t*se[active]
    upper[active]=point[active]+t*se[active]
    # Matched-reference-feasibility exact-zero fallback, like the original I2 method;
    # only applies if every paired feasibility sample difference is exactly 0.
    u=1-(.025/4)**(1/(len(cell_ids)*N_SEEDS))
    for idx,(a,b) in [(1,('gadapt_hyb','gadapt')),(3,('gadapt_hyb','ipop'))]:
        if all(np.all(arr[(ci,a)][:,1]-arr[(ci,b)][:,1]==0) for ci in cell_ids):
            lower[idx],upper[idx]=-u,u
    return {'cells':list(cell_ids),'replicates':reps,'seed':seed,'tstar':t,'se':se.tolist(),
            'contrasts':{name:{'estimate':float(point[j]),'lower':float(lower[j]),
                               'upper':float(upper[j])} for j,name in enumerate(CONTRASTS)},
            'kind':'EXPLORATORY_POST_HOC_SEED_BOOTSTRAP_NOT_REGISTERED_OR_MULTIPLICITY_ADJUSTED'}


def run(repo_root=None,derived_npz=None,reps=20000,seed=68):
    arr,src=source_arrays(repo_root,derived_npz)
    whole=bootstrap(arr,tuple(range(N_CELLS)),seed=seed,reps=reps)
    dropped=bootstrap(arr,tuple(x for x in range(N_CELLS) if x!=DOMINANT_ORPD_CELL),seed=seed,reps=reps)
    return {'input_source':src,'method':'paired bootstrap within fixed ORPD cells; 97.5% max-t quantile',
            'registered_full_set_recheck':whole,
            'exploratory_leave_out_case39_j3':dropped,
            'limitations':['Dropping source cell 3 was selected POST HOC after seeing the original outcome.',
                           'It changes the empirical target population; the seven-cell intervals are NOT prespecified inference.',
                           'No family-selection multiplicity adjustment is made.',
                           'All numbers from original archived run records; no new optimizer or PF.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--repo-root',type=Path)
    group.add_argument('--derived-npz',type=Path)
    ap.add_argument('--reps',type=int,default=20000)
    ap.add_argument('--seed',type=int,default=68)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    result=run(args.repo_root,args.derived_npz,args.reps,args.seed)
    txt=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.output:args.output.write_text(txt)
    else: print(txt,end='')
if __name__=='__main__': main()
