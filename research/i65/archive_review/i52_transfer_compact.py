"""Read-only chance-adjusted I52 transfer and class-identity audit.

Post hoc descriptive: agreement is not ground-truth detector specificity.
Usage: python i52_transfer_compact.py /path/to/gadapt
"""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

BLOBS = {'integrity_dispatch.json': 'c85b680cd536defc0d849d932855228c8223eb3c',
         'sensitivity.json': '4c31e359c45af97afa5be68bc7e5c4c631c69a90'}
K = {'C3','C4','C5','R1','R2','R3','D2','D3','D3x'}

def source(root):
    result = []
    for filename, sha in BLOBS.items():
        raw = (Path(root)/'research'/'results'/'iteration52'/filename).read_bytes()
        got = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if got != sha:
            raise ValueError('I52 Git blob mismatch '+filename+': '+got)
        result.append(json.loads(raw))
    return result

def fraction(x):
    return {'exact': str(x), 'value': float(x)}

def chance_agreement(a, b, c, d):
    n=a+b+c+d
    if not n: raise ValueError('empty table')
    observed=Fraction(a+d,n)
    expected=Fraction((a+b)*(a+c)+(c+d)*(b+d),n*n)
    kappa=(observed-expected)/(1-expected) if expected < 1 else None
    return {'n':n, 'matrix':{'S1_D1':a,'S1_D0':b,'S0_D1':c,'S0_D0':d},
            'observed':fraction(observed), 'chance_expected':fraction(expected),
            'kappa':fraction(kappa) if kappa is not None else None,
            'positive_agreement':fraction(Fraction(2*a,2*a+b+c)) if 2*a+b+c else None,
            'negative_agreement':fraction(Fraction(2*d,2*d+b+c)) if 2*d+b+c else None}

def compute(primary, sensitivity):
    rows=primary['per_library']
    if len(rows)!=22 or 'gadapt' not in rows:
        raise ValueError('I52 21-library roster mismatch')
    s,d=set(),set(); flags={}
    for lib,r in rows.items():
        if lib=='gadapt': continue
        a,b=r['synthetic_classes'],r['real_classes']
        if not isinstance(a,list) or not isinstance(b,list) or not (set(a)|set(b))<=K:
            raise ValueError('I52 detector-class mismatch: '+lib)
        if r['status_agrees'] != (bool(a)==bool(b)):
            raise ValueError('I52 stored-status mismatch: '+lib)
        flags[lib]=(bool(a),bool(b))
        s.update((lib,x) for x in a);d.update((lib,x) for x in b)
    def matrix(keys):
        f=[flags[k] for k in keys]
        return tuple(sum((a,b)==z for a,b in f) for z in ((True,True),(True,False),(False,True),(False,False)))
    main=chance_agreement(*matrix(flags))
    if (main['n'],main['matrix']) != (21,{'S1_D1':7,'S1_D0':1,'S0_D1':1,'S0_D0':12}):
        raise ValueError('I52 source-label control mismatch')
    if (primary['primary']['agree'],primary['primary']['of']) != (19,21):
        raise ValueError('I52 primary archive control mismatch')
    per=sensitivity['archive_A_original']['per_library']
    if set(per)!=set(flags) or any((per[k]['S'],per[k]['D'])!=flags[k] for k in flags):
        raise ValueError('I52 post-hoc archive status mismatch')
    complete=chance_agreement(*matrix(k for k in flags if per[k]['m']==15))
    if complete['matrix']!=sensitivity['archive_A_original']['complete_only']['confusion']:
        raise ValueError('I52 complete-case control mismatch')
    missing=sensitivity['archive_A_original']['missing_bounds']
    if (missing['lower'],missing['upper'])!=(17,20):
        raise ValueError('I52 missingness control mismatch')
    overlap=s&d;union=s|d
    if (len(s),len(d),len(overlap),len(union))!=(10,8,7,11):
        raise ValueError('I52 class-identity control mismatch')
    return {'source_git_blobs':BLOBS,'study':'I52','type':'post_hoc_descriptive_NOT_accuracy',
            'original_H52':'SUPPORTED_UNCHANGED','full':main,'complete_only':complete,
            'missingness_bound':[17,20],
            'class_pairs':{'synthetic':10,'dispatch':8,'overlap':7,'union':11,
                           'jaccard':fraction(Fraction(7,11)),
                           'only_synthetic':sorted(map(list,s-d)),
                           'only_dispatch':sorted(map(list,d-s))},
            'limitations':'No independent defect ground truth; nonrandom library sample; no physical-oracle rerun.'}

if __name__=='__main__':
    p,s=source(sys.argv[1] if len(sys.argv)>1 else '.')
    print(json.dumps(compute(p,s),indent=2,sort_keys=True))
