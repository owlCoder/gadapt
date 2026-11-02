#!/usr/bin/env python3
"""One development-only ORPD AC residual diagnostic; NO optimization runs.

Requires full history clone, restored historical paths and PYPOWER. The
numerical solver produces one operating point; independent NumPy-only AC
network equations verify its nodal balance, branch flows and losses.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[0]
if not (RESEARCH / 'iteration58_validation.py').is_symlink():
    raise SystemExit('BLOCKED: restore historic research-root symlinks')
sys.path.insert(0, str(RESEARCH))
sys.path.insert(0, str(HERE))

from pypower import api
from pypower.idx_gen import VG
from pypower.idx_brch import TAP
from pypower.idx_bus import BS
import iteration58_validation as i58
from ac_residual_witness import evaluate_ac_point
from orpd_solver_entry_audit import SolverEntryAudit


def git_blob(p: Path) -> str:
    content = p.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()


def main() -> int:
    trace = SolverEntryAudit()
    with trace.trace():
        with trace.phase('setup'):
            problem = i58.make_problem('case30', 1)
        x = problem.snap((problem.lo + problem.hi) / 2)
        d = problem.delegate
        n_b = len(problem.bus_groups)
        controls = d.snap(np.concatenate([x[:n_b][problem.expand], x[n_b:]]))
        case = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in d.base.items()}
        n_g, n_t = len(d.gen_rows), len(d.tap_rows)
        case['gen'][d.gen_rows, VG] = controls[:n_g]
        case['branch'][d.tap_rows, TAP] = controls[n_g:n_g + n_t]
        case['bus'][d.shunt_rows, BS] = controls[n_g + n_t:]
        with trace.phase('witness'):
            solved, converged = api.runpf(case, d.options)
    # Verifier imports only NumPy and consumes solved plain arrays.
    witness = evaluate_ac_point(solved, balance_tolerance_mva=1e-3,
                                flow_tolerance_mva=1e-5) if converged else None
    altered = None
    if converged:
        altered_case = {k: (v.copy() if isinstance(v, np.ndarray) else v)
                        for k, v in solved.items()}
        # Deliberately falsify an output power balance WITHOUT another PF call.
        altered_case['gen'][d.gen_rows[0], 1] += 1.0
        altered = evaluate_ac_point(altered_case, balance_tolerance_mva=1e-3,
                                    flow_tolerance_mva=1e-5)

    expected = {'setup': {'runopf': 1, 'runpf': 0},
                'search': {'runopf': 0, 'runpf': 0},
                'witness': {'runopf': 0, 'runpf': 1}}
    faults = []
    if trace.evidence()['phases'] != expected:
        faults.append('unplanned numerical solver entrypoint count')
    if not converged:
        faults.append('development-only case30/j1 PF failed to converge')
    if witness is not None and witness['status'] != 'AC_RESIDUAL_PASS':
        faults.append('independently recomputed AC residual mismatch')
    if altered is not None and altered['status'] != 'AC_RESIDUAL_FAIL':
        faults.append('tampered 1-MW generator injection was not rejected')
    print(json.dumps({
        'status': 'PASS' if not faults else 'FAIL',
        'scenario': {'network': 'case30', 'j': 1, 'resolution': 17},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'numerical_pf_converged': bool(converged),
        'ac_witness': witness,
        'tampered_witness': altered,
        'solver_api_entrypoints': trace.evidence(),
        'source_git_blobs': {
            'historic_orpd': git_blob(RESEARCH / 'legacy/flat/iteration56_orpd.py'),
            'historic_i58': git_blob(RESEARCH / 'legacy/flat/iteration58_validation.py'),
            'ac_verifier': git_blob(HERE / 'ac_residual_witness.py'),
        },
        'faults': faults,
        'scope': 'one non-held-out development operating point; not an independent numerical AC solver',
    }, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not faults else 1


if __name__ == '__main__':
    sys.exit(main())
