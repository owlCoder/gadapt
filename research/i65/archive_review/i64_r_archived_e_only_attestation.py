#!/usr/bin/env python3
"""Authenticate only ORIGINAL Git-tracked I64-E inputs against frozen R source metadata.

Does not load, create or simulate original off-Git I64-R records.
Does not run optimizer/PF/OPF/COCO or a seed/bootstrap calculation.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from i64_r_e_source_manifest_validation import REQUIRED_KEYS, EXPECTED_KEYS, validate_required_e_inputs
from i64_r_off_git_raw_recovery_gate import (
    read_pinned, blob_sha1, R_ANALYSIS_BLOB, R_CHECK_REPRO_BLOB, BUILDS,
)

E_RUN_CHECKSUM_GIT_BLOB = '5ab84804d195b4a75e80c700285acd3262fcb230'
E_RUN_ORIGINAL_SHA256 = '1f0f4525d55b0ae4d1976824b9ca211d972914f82daae57c9c95243b55de271f'


def verify_archived_R_E_lineage(analysis: dict, check: dict, e_run_sha: str) -> dict:
    original_inputs=analysis.get('e_inputs')
    if not isinstance(original_inputs,dict) or set(original_inputs)!=EXPECTED_KEYS:
        raise ValueError('Wrong original R analysis E input digest roster')
    if original_inputs!=check.get('e_inputs'):
        raise ValueError('Original R analysis and check_repro E input digests differ')
    if e_run_sha!=E_RUN_ORIGINAL_SHA256 or original_inputs['run']!=e_run_sha:
        raise ValueError('Original E aggregate full SHA256 differs from original git-recorded digest')
    manifest=check.get('manifest')
    if not isinstance(manifest,dict) or any(k not in manifest for k in BUILDS):
        raise ValueError('Original E/R check_repro build manifest incomplete')
    if not isinstance(check.get('results'),list) or len(check['results'])!=5 or not all(
        isinstance(r,dict) and r.get('identical') is True for r in check['results']
    ):
        raise ValueError('Original five frozen E reproducibility witnesses incomplete')
    if analysis.get('freeze_commit') != manifest['freeze_commit']:
        raise ValueError('Original R analysis freeze commit differs from check_repro manifest')
    if (analysis.get('boot'),analysis.get('boot_seed'),analysis.get('alpha'))!=(20000,70,0.05):
        raise ValueError('Original R seed-only bootstrap settings differ from frozen specification')
    return {'analysis_check_repro_E_sha256_manifest': 'MATCH',
            'historically_git_pinned_E_aggregate_sha256':e_run_sha,
            'five_original_E_reproducibility_witnesses':'ARCHIVED_MATCH',
            'original_R_bootstrap_settings':'ARCHIVED_20000_SEED70_ALPHA0_05_NOT_REPLAYED'}


def audit_original_E_only(repo_root:Path) -> dict:
    repo=repo_root.resolve()
    base=repo/'research/results/iteration64_r'
    analysis=read_pinned(base/'analysis.json.gz',R_ANALYSIS_BLOB)
    check=read_pinned(base/'check_repro.json.gz',R_CHECK_REPRO_BLOB)
    digest_file=repo/'research/results/iteration64_e/run.json.gz.sha256'
    raw=digest_file.read_bytes()
    if blob_sha1(raw)!=E_RUN_CHECKSUM_GIT_BLOB:
        raise ValueError('Original E combined source checksum file Git blob mismatch')
    line=raw.decode('ascii').strip()
    match=re.fullmatch(r'([a-f0-9]{64})\s+research/results/iteration64_e/run\.json\.gz',line)
    if match is None:
        raise ValueError('Original E combined archive SHA256 file malformed')
    lineage=verify_archived_R_E_lineage(analysis,check,match.group(1))
    # The missing original 4,200-row R source is never supplied or invented.
    # A zero-record E-only audit MUST NEVER set original R-bootstrap READY.
    checked=validate_required_e_inputs(repo,analysis['e_inputs'],[])
    if checked['ready_for_independent_raw_seed_bootstrap']:
        raise ValueError('E-only source check must never assert R-bootstrap readiness')
    required_complete=checked['E_required_source_SHA256_verified']==len(REQUIRED_KEYS)
    return {'schema':'I65_I64_R_ORIGINAL_GIT_TRACKED_E_ONLY_SOURCE_V1',
            'source':'original source-pinned R analysis/check_repro and original E files only',
            'R_original_raw_4200_seed_source':'MISSING_NOT_RECREATED',
            'R_original_bootstrap_20000_draws':'NOT_EXECUTED',
            'original_E_R_manifest':lineage,
            'required_E_original_part_and_freeze_normalizer_count':len(REQUIRED_KEYS),
            'original_E_manifest_entries_total':len(EXPECTED_KEYS),
            'E_inputs':checked,
            'required_E_sources_SHA256_authenticated_without_R_raw':required_complete,
            'full_E_aggregate_original_file_available_and_attested':
                checked['E_full_original_input_manifest_present_and_sha256_verified'],
            'science_status':'DRAFT / NO-FREEZE / NOT_ESTABLISHED',
            'new_optimizer_PF_OPF_COCO_runs':0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',required=True,type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    result=audit_original_E_only(a.repo_root)
    data=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n'
    if a.output:
        a.output.write_text(data,encoding='utf-8')
    else:
        print(data,end='')


if __name__=='__main__':
    main()
