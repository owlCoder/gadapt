#!/usr/bin/env python3
"""Post hoc I64-R FUNCTION-FAMILY resampling, never a registered inference.

Uses original full-precision `analysis.json.gz` with Git blob check, or a
read-only 9-decimal derived ledger for environments without a local clone.
The nine benchmark functions were purposively selected; percentile envelopes
are descriptive sensitivity, NOT a frequentist confidence interval about a
population of all objective functions. Runs zero optimizer/objective calls.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np

R_BLOB = '59025d6cc052baef76b14e5496962704bdb7604a'
FAMILIES = ('sphere','rosenbrock','rastrigin','ackley','griewank','styblinski_tang','beale','himmelblau','booth')
CONTRASTS = ('c1','c2','c3','c4')
FIELDS = ('shift|gadapt','rot|gadapt','rotm|gadapt','shift|ipop','rotm|ipop')


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def get_rows(*, analysis: Path | None = None, ledger: Path | None = None) -> tuple[list[dict], dict]:
    if (analysis is None) == (ledger is None):
        raise ValueError('Supply exactly one of --analysis, --ledger')
    if analysis is not None:
        raw=analysis.read_bytes()
        if git_blob(raw) != R_BLOB:
            raise ValueError('I64-R original analysis Git-blob mismatch')
        src=json.loads(gzip.decompress(raw))
        raw_pairs=src['per_pair']
        rows=[]
        for name,rec in raw_pairs.items():
            if not all(k in rec for k in FIELDS):
                raise ValueError(f'Missing ECDF field in {name}')
            vals=[rec[k] for k in FIELDS]
            if not all(isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x) and 0<=x<=1 for x in vals):
                raise ValueError('Invalid ECDF area')
            family,dimension=name.split('|')
            c1=rec['rotm|gadapt']-rec['rot|gadapt']
            c2=rec['shift|gadapt']-rec['rotm|gadapt']
            c3=rec['shift|ipop']-rec['rotm|ipop']
            rows.append(dict(cell=name,family=family,dimension=int(dimension),c1=c1,c2=c2,c3=c3,c4=c2-c3))
        original=src['estimates']
        provenance=dict(type='original compressed analysis, full precision',git_blob_sha1=R_BLOB,approximate=False)
    else:
        led=json.loads(ledger.read_text())
        if led['R']['source_blob_sha1'] != R_BLOB:
            raise ValueError('Ledger source does not match original R archive blob')
        rows=led['R']['pairs']
        original=[led['R']['original_exact_point'][k] for k in CONTRASTS]
        provenance=dict(type='derived 9-decimal snapshot; raw event archive NOT accessed',git_blob_sha1=R_BLOB,approximate=True)
    roster={f:set() for f in FAMILIES}
    for r in rows:
        if r['family'] not in roster:
            raise ValueError('Unexpected function family')
        d=int(r['dimension'])
        if r['cell'] != f"{r['family']}|{d}" or d in roster[r['family']]:
            raise ValueError('Duplicate or malformed cell')
        roster[r['family']].add(d)
    if len(rows)!=21 or any(roster[f] != ({2} if f in {'beale','himmelblau','booth'} else {2,7,20}) for f in FAMILIES):
        raise ValueError('Incorrect frozen I64-R 21-pair roster')
    mat=np.array([[np.mean([r[c] for r in rows if r['family']==f]) for c in CONTRASTS] for f in FAMILIES],dtype=np.float64)
    point=mat.mean(axis=0)
    if not np.allclose(point,np.array(original),rtol=0,atol=1e-9 if provenance['approximate'] else 1e-12):
        raise ValueError(f'Original point mismatch {point} / {original}')
    return rows,dict(provenance=provenance,family_matrix=mat,point=point)


def stress(matrix: np.ndarray, *, replications: int=100_000, seed: int=7001, chunk: int=10000) -> dict:
    """An illustrative, non-confirmatory resampling of nine purposive families."""
    assert matrix.shape == (9,4)
    if not 1000<=replications<=500_000:
        raise ValueError('replications outside expected read-only bound')
    rng=np.random.default_rng(seed)
    result=np.empty((replications,4))
    for start in range(0,replications,chunk):
        n=min(chunk,replications-start)
        ix=rng.integers(0,9,size=(n,9))
        result[start:start+n]=matrix[ix].mean(axis=1)
    q=np.quantile(result,(0.025,0.05,0.5,0.95,0.975),axis=0)
    return dict(iterations=replications,seed=seed,kind='illustrative resampling of purposively selected function families, NOT a registered CI',
                percentile_envelopes={key:{p:float(q[i,j]) for i,p in enumerate(('p2.5','p5','median','p95','p97.5'))} for j,key in enumerate(CONTRASTS)},
                proportion_resampled_c4_above_0_05=float(np.mean(result[:,3]>0.05)),
                proportion_resampled_c4_above_zero=float(np.mean(result[:,3]>0)),
                proportion_resampled_c2_above_0_05=float(np.mean(result[:,1]>0.05)))


def run(analysis: Path | None=None,ledger: Path | None=None,replications: int=100_000,seed: int=7001) -> dict:
    rows,s=get_rows(analysis=analysis,ledger=ledger)
    a=s['family_matrix']; full=s['point']
    loo={f:float(a[[j for j,g in enumerate(FAMILIES) if f!=g],3].mean()) for f in FAMILIES}
    two=[]
    for i in range(9):
        for j in range(i+1,9):
            keep=np.delete(a,[i,j],axis=0)
            two.append(dict(removed=[FAMILIES[i],FAMILIES[j]],c4=float(keep[:,3].mean())))
    b=stress(a,replications=replications,seed=seed)
    return dict(status='POST_HOC_ONLY',provenance=s['provenance'],frozen_point={k:float(full[i]) for i,k in enumerate(CONTRASTS)},
                family_means={f:{k:float(a[i,j]) for j,k in enumerate(CONTRASTS)} for i,f in enumerate(FAMILIES)},
                leave_one_family_out_c4=loo,leave_two_family_out_below_0_05=sum(r['c4']<.05 for r in two),
                leave_two_family_out_total=len(two),extreme_two_family_removals=sorted(two,key=lambda z:z['c4'])[:4],resampling=b,
                interpretation='Original R seed-only registered H64r1/r2/r3 unchanged. Deliberately selected family set and R per-seed raw data absent from Git. Resampling nine purposively chosen means gives only exploratory heterogeneity diagnostic.')


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    src=p.add_mutually_exclusive_group(required=True)
    src.add_argument('--analysis',type=Path)
    src.add_argument('--ledger',type=Path)
    p.add_argument('--replications',type=int,default=100_000)
    p.add_argument('--seed',type=int,default=7001)
    p.add_argument('--output',type=Path)
    a=p.parse_args(); out=run(analysis=a.analysis,ledger=a.ledger,replications=a.replications,seed=a.seed)
    t=json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    if a.output:a.output.write_text(t)
    else:print(t,end='')

if __name__=='__main__':main()
