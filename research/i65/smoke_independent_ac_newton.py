#!/usr/bin/env python3
"""One non-held-out I58 case30/j1 comparison of two numerical AC PF solvers.

Opt-in diagnostic ONLY. Fixed midpoint, no GA/DE/CMA/COCO/optimizer search.
PYPOWER is used solely as a distinct existing numerical PF reference;
independent_ac_newton imports NumPy only and starts from flat angles/PQ VM.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
if not (RESEARCH / 'iteration58_validation.py').is_symlink():
    raise SystemExit('BLOCKED: restore original historical research-root aliases')
sys.path.insert(0, str(RESEARCH))
sys.path.insert(0, str(HERE))

from pypower import api
from pypower.idx_gen import VG
from pypower.idx_brch import TAP
from pypower.idx_bus import BS
import iteration58_validation as i58
from independent_ac_newton import solve_ac_pf
from orpd_solver_entry_audit import SolverEntryAudit


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def clone_case(case):
    return {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in case.items()}


def main():
    with SolverEntryAudit().trace() as audit:
        with audit.phase('setup'):
            problem = i58.make_problem('case30', 1)
        x = problem.snap((problem.lo + problem.hi) / 2)
        delegate = problem.delegate
        bus_groups = len(problem.bus_groups)
        controls = delegate.snap(np.concatenate([x[:bus_groups][problem.expand], x[bus_groups:]]))
        original_case = clone_case(delegate.base)
        ng, nt = len(delegate.gen_rows), len(delegate.tap_rows)
        original_case['gen'][delegate.gen_rows, VG] = controls[:ng]
        original_case['branch'][delegate.tap_rows, TAP] = controls[ng:ng + nt]
        original_case['bus'][delegate.shunt_rows, BS] = controls[ng + nt:]
        # IMPORTANT: numerical Newton independently solves the unmodified
        # INPUT CASE before runpf, never from PYPOWER's solved bus arrays.
        fresh = solve_ac_pf(original_case, tolerance_pu=1e-9,
                            max_iterations=20, jacobian_step=1e-6)
        with audit.phase('witness'):
            solved, converged = api.runpf(clone_case(original_case), delegate.options)

    observed = audit.evidence()
    expected = {'setup': {'runopf': 1, 'runpf': 0},
                'search': {'runopf': 0, 'runpf': 0},
                'witness': {'runopf': 0, 'runpf': 1}}
    faults = []
    if observed['phases'] != expected:
        faults.append('wrong PYPOWER entrypoint counts')
    if not bool(converged):
        faults.append('PYPOWER failed to converge')
    if fresh['status'] != 'CONVERGED':
        faults.append('independent Newton failed to converge')
    comparisons = None
    if bool(converged) and fresh['status'] == 'CONVERGED':
        # Predeclared absolute tolerances (do not change after seeing result).
        vm_difference = float(np.max(np.abs(np.asarray(fresh['voltage_magnitudes']) - solved['bus'][:, 7])))
        angles = np.asarray(fresh['voltage_angles_deg']) - solved['bus'][:, 8]
        angle_difference = float(np.max(np.abs((angles + 180) % 360 - 180)))
        py_loss = float(np.sum(solved['branch'][:, 13] + solved['branch'][:, 15]))
        loss_difference = float(abs(fresh['branch_loss_mw'] - py_loss))
        comparisons = {'max_vm_error_pu': vm_difference,
                       'max_angle_error_degrees': angle_difference,
                       'loss_mw_error': loss_difference,
                       'independent_branch_loss_mw': fresh['branch_loss_mw'],
                       'pypower_branch_loss_mw': py_loss,
                       'tolerances': {'vm_pu': 5e-4, 'angle_degrees': 5e-3,
                                      'loss_mw': 5e-3}}
        for field, threshold in [('max_vm_error_pu', 5e-4),
                                 ('max_angle_error_degrees', 5e-3),
                                 ('loss_mw_error', 5e-3)]:
            if comparisons[field] > threshold:
                faults.append('cross-solver numerical disagreement: ' + field)
    report = {'status': 'PASS' if not faults else 'FAIL',
              'case': {'network': 'case30', 'scenario': 1, 'resolution': 17,
                       'candidate': 'grid-snapped midpoint, no search'},
              'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
              'independent_numerical_solver': fresh,
              'pypower_converged': bool(converged),
              'comparison': comparisons,
              'api_entrypoint_trace': observed,
              'source_git_blobs': {
                  'historical_i56': git_blob(RESEARCH / 'legacy/flat/iteration56_orpd.py'),
                  'historical_i58': git_blob(RESEARCH / 'legacy/flat/iteration58_validation.py'),
                  'independent_newton': git_blob(HERE / 'independent_ac_newton.py')},
              'faults': faults,
              'scope': 'independent NumPy numerical Newton PF comparison, not independent physical model or ORPD feasibility'}
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 0 if not faults else 1


if __name__ == '__main__':
    sys.exit(main())
