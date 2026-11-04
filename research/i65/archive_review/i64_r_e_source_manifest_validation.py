#!/usr/bin/env python3
"""Independent read-only SHA-256 + frozen task-param integrity gate for I64-R E inputs.

The original R `e_inputs` manifest lists all 63 E run parts and four
aggregate sources. Replaying R's 21 fixed pairs requires shift+rot E parts,
normalizers, and the frozen optimizer-parameter manifest. A missing optional
E aggregate `run.json.gz` is recorded, never silently labeled FULL lineage.
No optimizer, PF/OPF, physics, or COCO implementation is imported.
"""
from __future__ import annotations
import gzip
import hashlib
import json
import re
from pathlib import Path

EXPECTED_KEYS = frozenset({f'run_part_{i}' for i in range(63)} |
                          {'run', 'freeze', 'normalizers', 'manifest_run'})
REQUIRED_KEYS = frozenset({f'run_part_{3*k+j}' for k in range(21) for j in (1, 2)} |
                          {'freeze', 'normalizers'})


def validate_required_e_inputs(repo_root: Path, source_digests: dict,
                               records: list, *, original_r_roster_attested: bool = False) -> dict:
    """Check all present E inputs; verify required original replay inputs.

    When an original file is absent, report it instead of replacing data.
    If a present file differs from its independently pinned R SHA-256,
    abort even if the file is optional for the downstream seed analysis.
    No source is created, recomputed or rewritten.
    """
    if not isinstance(source_digests, dict) or set(source_digests) != EXPECTED_KEYS:
        raise ValueError('Original E input digest manifest must have 63 parts plus four aggregate keys')
    if any(not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None
           for digest in source_digests.values()):
        raise ValueError('Original E input manifest must use 67 full 64-hex SHA256 digests')
    if not isinstance(records, list):
        raise ValueError('R seed-level task records must be a list')
    e_root = Path(repo_root) / 'research/results/iteration64_e'
    missing_required, missing_optional, present_verified = [], [], []
    for key in sorted(EXPECTED_KEYS):
        path = e_root / (key + '.json.gz')
        if not path.is_file():
            (missing_required if key in REQUIRED_KEYS else missing_optional).append(str(path))
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != source_digests[key]:
            raise ValueError('Original E input SHA256 mismatch: ' + str(path))
        present_verified.append(key)
    tasks_checked = 0
    if 'freeze' in present_verified:
        frozen = json.loads(gzip.decompress((e_root / 'freeze.json.gz').read_bytes()))
        # E-only custody (zero R records) authenticates the frozen E bytes,
        # not the schema of unavailable original R task parameter records.
        # A later *actual* R roster must still pass the strict parameter gate.
        if not isinstance(frozen, dict):
            raise ValueError('Verified E freeze source is not a JSON object')
        params = frozen.get('params')
        if records and (not isinstance(params, dict) or
                        not {'gadapt', 'ipop'} <= set(params)):
            raise ValueError('Verified E freeze source missing original algorithm parameters')
        for i, r in enumerate(records):
            if not isinstance(r, dict) or not isinstance(r.get('task'), dict):
                raise ValueError(f'Invalid original R task at index {i}')
            task = r['task']
            cfg = task.get('config')
            if cfg not in ('gadapt', 'ipop') or set(task) != {'k', 'config', 'seed', 'params'}:
                raise ValueError(f'Original R task shape/config mismatch at index {i}')
            if task['params'] != params.get(cfg):
                raise ValueError(f'Original R task optimizer parameters differ from E freeze at index {i}')
            tasks_checked += 1
    # E-only audits have no recovered R records and MUST NOT report R-bootstrap readiness.
    ready = (not missing_required and original_r_roster_attested is True and
             len(records) == 4200 and tasks_checked == 4200)
    return {
        'E_original_manifest_entries': len(EXPECTED_KEYS),
        'required_for_independent_R_seed_bootstrap': len(REQUIRED_KEYS),
        'E_source_sha256_verified_count': len(present_verified),
        'E_required_source_SHA256_verified': sum(k in REQUIRED_KEYS for k in present_verified),
        'E_original_R_tasks_params_matched_to_frozen_E': tasks_checked,
        'E_original_R_task_parameter_comparison':
            ('NOT_PERFORMED_NO_ORIGINAL_R_RECORDS' if not records else
             'MATCHED_PRESENT_R_RECORDS'),
        'E_missing_required_paths': missing_required,
        'E_missing_optional_paths': missing_optional,
        'E_full_original_input_manifest_present_and_sha256_verified':
            not missing_required and not missing_optional,
        'ready_for_independent_raw_seed_bootstrap': bool(ready),
        'caution': 'Optional E source absences still prevent FULL original E manifest attestation.'
    }
