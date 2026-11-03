#!/usr/bin/env python3
"""Assemble the explicitly disclosed, read-only observations captured through the GitHub connector.

The I64-R pair contrasts below were rounded to nine decimal places before
transfer to the working container. They support descriptive replication to
< 1e-8 but are NOT a replacement for the exact frozen per-pair gzip source.
The I64-I2 per-cell summaries were transmitted with full floating-point text
precision; exact per-seed records are only in the source .json.gz files.
"""
import json
import math
from pathlib import Path

from i64_i2_cell_influence import ANALYSIS_BLOB, I_BLOBS, I2_BLOBS, CONTRASTS, CONFIGS
from i64_i2_cell_influence import summarize

DIR = Path(__file__).resolve().parent
R_DATA = """\
rastrigin|7 .005440278 .525940278 .011919722
rastrigin|2 .029684444 .385690000 -.017635833
styblinski_tang|7 -.101935833 .505696944 .213366389
styblinski_tang|20 .022542778 .270905278 .000000000
beale|2 -.027968333 .069277778 -.005641667
ackley|20 .007979722 .129831944 .000195000
griewank|20 -.008708611 .094986389 -.027190278
ackley|7 .035339167 .026986944 -.006558889
rosenbrock|20 -.025835833 .047212778 .015616111
himmelblau|2 .019528889 .003725556 -.003275278
rastrigin|20 .000000000 .013245556 .000000000
styblinski_tang|2 -.012517222 .014613333 .004540833
sphere|7 -.002336389 .003396111 .001303056
ackley|2 .005093889 .000872500 -.000416389
sphere|2 .000741944 -.000171389 -.000128333
sphere|20 .010025000 -.000791944 .001478056
rosenbrock|7 -.012884722 -.002945833 .003909167
booth|2 -.000334722 -.004738333 -.000008056
griewank|7 .008788889 .018834167 .033394722
griewank|2 .057470833 .032020833 .066389444
rosenbrock|2 .090977500 -.087186944 -.000853889"""
ORIGINAL_R = [0.00309419753086404, 0.08088636831275742, 0.010094588477366107, 0.07079177983539131]
ORIGINAL_I2_AGG = {
    "gadapt": {"P": 0.7458333333333333, "cvar90": 0.29725831682237963},
    "gadapt_hyb": {"P": 0.7416666666666667, "cvar90": 0.3771500251324287},
    "ipop": {"P": 0.7708333333333333, "cvar90": 0.25184326402003326},
}
ORIGINAL_I2_CON = [-0.07989170831004905, -0.004166666666666652, -0.12530676111239542, -0.029166666666666563]
# (name, j, reference r, M (CVaR, feasible count), H, IPOP)
I2_CELLS = [
    ("case30", 2, 1.9640266068960095, (0.006526847789736136,30), (0.006526847789736136,30), (0.006526847789736136,30)),
    ("case30", 3, 3.1403782960578326, (1.,0), (1.,0), (1.,0)),
    ("case39", 2, 40.48981176212506, (0.003877319609696707,30), (0.0009480394807600616,30), (0.0015415979655968998,30)),
    ("case39", 3, 44.43558670902649, (1/3,29), (1.,27), (0.,30)),
    ("case39", 4, 50.49477874442633, (1.,0), (1.,1), (1.,5)),
    ("case24_ieee_rts", 2, 56.26158595756312, (0.006448672506910339,30), (0.0000127521118158811,30), (0.00009102052887454092,30)),
    ("case24_ieee_rts", 3, 46.12396022547803, (0.009375150499856476,30), (0.0017983763604921697,30), (0.0006294779660381253,30)),
    ("case24_ieee_rts", 4, 48.70898170022514, (0.01850521083950399,30), (0.007914185316625393,30), (0.005957167910020243,30)),
]


def assemble():
    r_rows=[]
    for item in R_DATA.splitlines():
        cell,c1,c2,c3=item.split()
        f,d=cell.split('|')
        c1,c2,c3=map(float,(c1,c2,c3))
        w=1/9 if f in ('beale','himmelblau','booth') else 1/27
        r_rows.append(dict(cell=cell,family=f,dimension=int(d),weight=w,c1=c1,c2=c2,c3=c3,c4=c2-c3,weighted_c4=w*(c2-c3)))
    assert len(r_rows)==21
    r_points={name:math.fsum(row['weight']*row[name] for row in r_rows) for name in ('c1','c2','c3','c4')}
    assert max(abs(r_points[x]-ORIGINAL_R[i]) for i,x in enumerate(('c1','c2','c3','c4')))<1e-8
    family_loo=[]
    for f in ['sphere','rosenbrock','rastrigin','ackley','griewank','styblinski_tang','beale','himmelblau','booth']:
        remain=[row for row in r_rows if row['family']!=f]
        denom=math.fsum(r['weight'] for r in remain)
        family_loo.append(dict(removed=f,removed_n=21-len(remain),c4=math.fsum(r['weighted_c4'] for r in remain)/denom,
                               c2=math.fsum(r['weight']*r['c2'] for r in remain)/denom))
    r_result={"source_blob_sha1":"59025d6cc052baef76b14e5496962704bdb7604a",
              "data_precision":"PER_PAIR_C1_C2_C3_ROUNDED_TO_9_DECIMAL_PLACES_FROM_DIRECT_DECOMPRESSED_ARCHIVE",
              "point_reconstructed_from_rounded_pairs":r_points,
              "max_abs_deviation_from_original":max(abs(r_points[x]-ORIGINAL_R[i]) for i,x in enumerate(('c1','c2','c3','c4'))),
              "original_exact_point":dict(zip(('c1','c2','c3','c4'),ORIGINAL_R)),
              "family_leave_one_out":family_loo,
              "dimension_leave_one_out":[dict(drop_d=d,remaining_weight=sum(r['weight'] for r in r_rows if r['dimension']!=d),
                                               c4=sum(r['weighted_c4'] for r in r_rows if r['dimension']!=d)/sum(r['weight'] for r in r_rows if r['dimension']!=d)) for d in (2,7,20)],
              "pairs":r_rows}
    i2=[]
    for ci, (net,j,ref,m,h,i) in enumerate(I2_CELLS):
        configs={name:{'feasible_count':v[1], 'p_feasible':v[1]/30,'cvar90':v[0]}
                 for name,v in zip(CONFIGS,(m,h,i))}
        M,H,IPOP=[configs[name] for name in CONFIGS]
        i2.append({'cell_index':ci,'network':net,'j':j,'reference_r':ref,'configs':configs,
                   'contrasts':dict(zip(CONTRASTS,(M['cvar90']-H['cvar90'], H['p_feasible']-M['p_feasible'],
                                                   IPOP['cvar90']-H['cvar90'],H['p_feasible']-IPOP['p_feasible']))),
                   'source_blob_sha1':{'i':I_BLOBS[ci],'i2':I2_BLOBS[ci]}})
    frozen={"aggregate":ORIGINAL_I2_AGG,"contrasts":{name:{'estimate':point} for name,point in zip(CONTRASTS,ORIGINAL_I2_CON)},
            'H64h1':'undecided','H64h2':'opposite'}
    i2_result=summarize(i2,frozen)
    i2_result['observed_infeasible_seed_forensics'] = {
        'cell_index': 3, 'case': 'case39', 'j': 3,
        'gadapt': [68003023], 'gadapt_hyb': [68003015, 68003018, 68003028], 'ipop': [],
        'source': 'Directly decompressed pinned run_part_3 and run2_part_3 GitHub archives',
        'limitations': 'Flags rechecked; independent physical solver and optimizer NOT rerun',
    }
    return {'date':'2026-11-03','repo':'owlCoder/gadapt','reference_main_commit':'6b56fbc53ffc4d275ecef5e911ea4663474c9a08',
            'kind':'READ_ONLY_CROSS_ARCHIVE_POST_HOC_POINT_SENSITIVITIES',
            'R':r_result,'I2':i2_result,
            'audit_limits':['I64-R table uses 9-decimal pair contrasts; full-clone tool verifies exact original compressed archive.',
                            'I64-I2 table comes from direct inspection of all 16 original compressed per-cell run parts through GitHub connector.',
                            'Original I64-I2 bootstrap (20k paired resamples) not rerun in this session.',
                            'Neither original study verdict is overwritten or re-registered.',
                            'No PF or optimizer was run and no held-out COCO was viewed.']}


if __name__=='__main__':
    out=assemble()
    path=DIR/'I65_I64_R_I2_INFLUENCE_LEDGER_2026-11-03.json'
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('wrote',path)
    print('R LOO rastrigin',next(x for x in out['R']['family_leave_one_out'] if x['removed']=='rastrigin'))
    print('I2 dominant cell',out['I2']['dominant_cell'])
    print('I2 point cross-archive checks:',out['I2']['contrasts_from_original_run_records'])
