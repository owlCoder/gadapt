#!/usr/bin/env python3
"""Read-only attestation and structural gate for the OFF-GIT I64-R run.json.gz.

History records an ~8 MB `research/results/iteration64_r/run.json.gz`
outside Git with only abbreviated SHA256 f23046f6...3618. Its unavailability
in Git is not evidence of corruption or loss on the experimenter's computer.
Do not rerun the optimizer to create a replacement: recover the ORIGINAL.

Example:
 python i64_r_off_git_raw_recovery_gate.py --repo-root . \
   --raw-run /original/path/iteration64_r/run.json.gz \
   --expected-full-sha256 '<trusted 64 hex digit checksum>' \
   --output /safe/directory/r_recovery_gate.json

No mutation, optimizer, PF/OPF, or new objective evaluation.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import math
import re
from pathlib import Path

from i64_r_e_source_manifest_validation import validate_required_e_inputs

R_ANALYSIS_BLOB='59025d6cc052baef76b14e5496962704bdb7604a'
R_CHECK_REPRO_BLOB='11ca5fdfabfe6ce20cb54752a2a41fe8e2deee3d'
HISTORICAL_SHA256_PREFIX='f23046f6'
HISTORICAL_SHA256_SUFFIX='3618'
PAIRS=tuple((family,d) for family in ('sphere','rosenbrock','rastrigin','ackley','griewank','styblinski_tang','beale','himmelblau','booth') for d in ((2,) if family in ('beale','himmelblau','booth') else (2,7,20)))
BUILDS=('python','pip_freeze','gadapt_tree','files','protocol','mentor_head','settings','r_files','r_settings','freeze_commit')


def blob_sha1(raw:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()


def read_pinned(path:Path,blob:str)->dict:
    raw=path.read_bytes()
    if blob_sha1(raw)!=blob:
        raise ValueError(f'Git blob mismatch: {path}')
    return json.loads(gzip.decompress(raw))


def validate_r_records(records:list)->dict:
    if not isinstance(records,list) or len(records)!=4200:
        raise ValueError('R raw record count must equal 21 x 100 x 2 = 4200')
    seen=set()
    for index,r in enumerate(records):
        if not isinstance(r,dict) or not isinstance(r.get('task'),dict):
            raise ValueError(f'Invalid task at index {index}')
        t=r['task'];k=t.get('k');config=t.get('config');seed=t.get('seed')
        if type(k)!=int or not (0<=k<len(PAIRS)) or config not in ('gadapt','ipop') or type(seed)!=int:
            raise ValueError(f'Invalid R cell/config/seed {index}')
        s=seed-(67_000_000+1000*(63+k))
        if not (1<=s<=100):
            raise ValueError(f'Wrong original R seed {index}: {seed}')
        key=(k,config,s)
        if key in seen:
            raise ValueError(f'Duplicate R task {key}')
        seen.add(key)
        if r.get('ok') is not True or r.get('calls')!=12000:
            raise ValueError(f'Unsuccessful/incomplete historical run {key}')
        events=r.get('events')
        if not isinstance(events,list) or not events:
            raise ValueError(f'Missing best-so-far trajectory {key}')
        previous_call=0
        previous_f=math.inf
        for event in events:
            if not isinstance(event,(tuple,list)) or len(event)!=2:
                raise ValueError(f'Malformed event {key}')
            call,f=event
            if type(call)!=int or not previous_call<call<=12000:
                raise ValueError(f'Invalid event call count/order {key}')
            if isinstance(f,bool) or not isinstance(f,(float,int)) or not math.isfinite(f):
                raise ValueError(f'Non-finite best value {key}')
            # Original frozen e_common.Budget.__call__ records a new event
            # ONLY on strict finite v < best. A tie or even a tiny increase
            # cannot be an authentic archived best-improvement event.
            if not float(f)<previous_f:
                raise ValueError(f'Best value is not strictly improved {key}')
            previous_call=call
            previous_f=float(f)
        # The frozen R driver stores budget.best and budget.best_y from the
        # same final strict-improvement event in this original task.
        best_f=r.get('best_f')
        if type(best_f) not in (float,int) or not math.isfinite(best_f) or float(best_f)!=previous_f:
            raise ValueError(f'Last event does not equal original best_f {key}')
        best_y=r.get('best_y')
        dimension=PAIRS[k][1]
        if not isinstance(best_y,list) or len(best_y)!=dimension or any(
            type(v) not in (float,int) or not math.isfinite(v) for v in best_y
        ):
            raise ValueError(f'Invalid original best_y dimension/coordinates {key}')
    if len(seen)!=4200:
        raise ValueError('Incomplete R seed/config/paired-cell roster')
    return dict(records_checked=4200,pairs=21,algorithms=2,seeds_per_pair=100,objective_calls_per_run=12000,
                event_integrity='PASS',seed_roster='PASS',all_runs_ok='PASS')


def verify_lineage(raw_run:dict,analysis:dict,check:dict)->dict:
    if raw_run.get('e_inputs') != analysis.get('e_inputs') or raw_run.get('e_inputs')!=check.get('e_inputs'):
        raise ValueError('R/E input manifest digest set mismatch')
    manifests=[raw_run.get('manifest'),check.get('manifest')]
    if any(not isinstance(m,dict) for m in manifests):
        raise ValueError('Missing R/check_repro build manifest')
    if any(k not in m for m in manifests for k in BUILDS):
        raise ValueError('Incomplete build manifest')
    if any(manifests[0][k]!=manifests[1][k] for k in BUILDS):
        raise ValueError('R run and check_repro build mismatch')
    checks=check.get('results')
    if not isinstance(checks,list) or len(checks)!=5 or not all(r.get('identical') is True for r in checks):
        raise ValueError('Original five E-R reproducibility witnesses not all identical')
    return dict(e_input_sha256_items=len(raw_run['e_inputs']),build_manifest='MATCH',check_repro_witnesses=5)


def audit(*,repo_root:Path,raw_run_path:Path,expected_full_sha256:str|None=None)->dict:
    repo_root=repo_root.resolve()
    analysis=read_pinned(repo_root/'research/results/iteration64_r/analysis.json.gz',R_ANALYSIS_BLOB)
    check=read_pinned(repo_root/'research/results/iteration64_r/check_repro.json.gz',R_CHECK_REPRO_BLOB)
    if not raw_run_path.is_file():
        return dict(status='NOT_AVAILABLE_ON_THIS_FILESYSTEM',raw_run=str(raw_run_path),
                    archived_Git_run_parts=0,original_R_history='8MB run.json.gz declared outside Git, SHA-256 f23046f6...3618',
                    bootstrap_replay='BLOCKED_ON_ORIGINAL_RAW_R',recommended_action='Find original experimental-machine file; DO NOT regenerate it using an optimizer')
    sha=hashlib.sha256(raw_run_path.read_bytes()).hexdigest()
    partial=sha.startswith(HISTORICAL_SHA256_PREFIX) and sha.endswith(HISTORICAL_SHA256_SUFFIX)
    if not partial:raise ValueError('Recovered R file fails the historical partial SHA256 marker')
    if expected_full_sha256 is not None:
        if not re.fullmatch(r'[0-9a-f]{64}',expected_full_sha256):
            raise ValueError('Expected full SHA256 must be 64 lowercase hexadecimal characters')
        if sha!=expected_full_sha256:
            raise ValueError('Recovered R file does not match supplied FULL trusted SHA256')
    raw=json.loads(gzip.decompress(raw_run_path.read_bytes()))
    struct=validate_r_records(raw.get('records'))
    lineage=verify_lineage(raw,analysis,check)
    # SHA-256 authenticate every E input that is present against the ORIGINAL
    # three-way-agreed R/E input manifest; refuse corrupted files, and
    # separately record optional E-aggregate absences (the original E run
    # combined archive was not committed). Required are the 42 shift/rot
    # source parts, original normalizers and original frozen method params.
    e_integrity=validate_required_e_inputs(repo_root,raw['e_inputs'],raw['records'])
    return dict(status='STRUCTURE_MATCHES_ARCHIVED_R_SPEC',raw_run=str(raw_run_path),actual_sha256=sha,
                historical_abbreviated_marker_match=True,
                trusted_full_digest_confirmed=expected_full_sha256 is not None,
                digest_authentication='FULL_TRUSTED_MATCH' if expected_full_sha256 else 'ONLY_48_BIT_HISTORICAL_ABBREVIATION; FULL_DIGEST_NOT_ATTESTED',
                provenance=lineage,run_structure=struct,
                missing_E_inputs=e_integrity['E_missing_required_paths'],
                E_input_full_SHA256_and_task_param_verification=e_integrity,
                ready_for_independent_raw_seed_bootstrap=e_integrity['ready_for_independent_raw_seed_bootstrap'],
                caution='Ready requires original R source AND SHA256-verified E inputs; no independent R bootstrap has yet been executed, and missing optional E aggregates prevent FULL E manifest attestation.')


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--raw-run',type=Path,required=True)
    p.add_argument('--expected-full-sha256')
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    res=audit(repo_root=a.repo_root,raw_run_path=a.raw_run,expected_full_sha256=a.expected_full_sha256)
    t=json.dumps(res,indent=2,allow_nan=False)+'\n'
    if a.output:a.output.write_text(t)
    else:print(t,end='')
    if res['status']=='NOT_AVAILABLE_ON_THIS_FILESYSTEM':raise SystemExit(2)

if __name__=='__main__':main()
