#!/usr/bin/env python3
"""Read-only S0 per-cell ranking from the original pinned compressed analysis.
Does NOT re-run optimizer trials or original statistics.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from i64_archival_recheck import open_pinned


def compare_s0(doc: dict) -> dict:
    descriptive = doc['descriptive']
    cells = sorted({"|".join(k.split('|')[:2]) for k in descriptive})
    if len(cells) != 21:
        raise ValueError(f'Expected 21 function×dimension cells, found {len(cells)}')
    rows = []
    for cell in cells:
        de, ga = (descriptive[f'{cell}|{m}'] for m in ('de', 'gadapt'))
        for value in (de['gap_median'], ga['gap_median'], de['A_mean'], ga['A_mean']):
            if not isinstance(value,(int,float)):
                raise ValueError('Non-numeric cell outcome')
        rows.append({'cell':cell,
                     'DE_final_gap_median':de['gap_median'],
                     'GAdapt_final_gap_median':ga['gap_median'],
                     'DE_A':de['A_mean'], 'GAdapt_A':ga['A_mean'],
                     'DE_better_final_median':de['gap_median'] < ga['gap_median'],
                     'GAdapt_better_final_median':ga['gap_median'] < de['gap_median'],
                     'final_median_tie':ga['gap_median'] == de['gap_median'],
                     'DE_better_A':de['A_mean'] > ga['A_mean'],
                     'GAdapt_better_A':ga['A_mean'] > de['A_mean'],
                     'A_tie':ga['A_mean'] == de['A_mean']})
    summary = {key:sum(x[key] for x in rows) for key in (
        'DE_better_final_median','GAdapt_better_final_median','final_median_tie',
        'DE_better_A','GAdapt_better_A','A_tie')}
    summary['expected_count_pattern'] = summary == {
        'DE_better_final_median':14, 'GAdapt_better_final_median':6,
        'final_median_tie':1, 'DE_better_A':4, 'GAdapt_better_A':17,'A_tie':0}
    return {'schema':'GADAPT_I65_S0_CELL_RANKING_RECHECK_V1',
            'source_study':'I64_S0',
            'metric_scope':'Original method stopping points; NOT equal 12,000-call end accuracy',
            'summary':summary, 'cells':rows,
            'no_new_optimization':True,
            'limitation':'These are source analysis fields, not independently reconstructed original seed-level outcomes'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,required=True)
    args=p.parse_args()
    doc=open_pinned(args.repo_root,'S0')
    result=compare_s0(doc)
    print(json.dumps(result,indent=2,allow_nan=False))
    if not result['summary']['expected_count_pattern']:
        raise SystemExit(1)

if __name__=='__main__':main()
