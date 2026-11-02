#!/usr/bin/env python3
"""One fixed, non-held-out I58 case30/j1 independent dispatch comparison.

Zero optimizer search; one historical scenario OPF and one reference PF.
Independent NumPy Newton + dispatch operate on the *unsolved* case only.
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
    raise SystemExit('BLOCKED: historical research-root aliases not restored')
sys.path.insert(0, str(RESEARCH))
sys.path.insert(0, str(HERE))

from pypower import api
from pypower.idx_gen import VG
from pypower.idx_brch import TAP
from pypower.idx_bus import BS
import iteration58_validation as i58
from independent_ac_newton import solve_ac_pf
from independent_ac_dispatch import reconstruct_dispatch
from orpd_operational_witness import validate_constraint_components, COMPONENTS
from orpd_solver_entry_audit import SolverEntryAudit


def blob(p):
    d = p.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(d)).encode() + b'\0' + d).hexdigest()


def copy_case(obj):
    return {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in obj.items()}


def main():
    audit = SolverEntryAudit()
    with audit.trace():
        with audit.phase('setup'):
            problem = i58.make_problem('case30', 1)
        x = problem.snap((problem.lo + problem.hi) / 2)
        d = problem.delegate
        nb = len(problem.bus_groups)
        controls = d.snap(np.concatenate([x[:nb][problem.expand], x[nb:]]))
        case = copy_case(d.base)
        ng, nt = len(d.gen_rows), len(d.tap_rows)
        case['gen'][d.gen_rows, VG] = controls[:ng]
        case['branch'][d.tap_rows, TAP] = controls[ng:ng + nt]
        case['bus'][d.shunt_rows, BS] = controls[ng + nt:]
        # This calculation is completed BEFORE the reference PF call.
        newton = solve_ac_pf(case, tolerance_pu=1e-9,
                             max_iterations=20, jacobian_step=1e-6)
        independent = reconstruct_dispatch(case, newton)
        with audit.phase('witness'):
            pypower_case, converged = api.runpf(copy_case(case), d.options)

    events = audit.evidence()
    faults = []
    expect = {'setup': {'runopf': 1, 'runpf': 0},
              'search': {'runopf': 0, 'runpf': 0},
              'witness': {'runopf': 0, 'runpf': 1}}
    if events['phases'] != expect:
        faults.append('unexpected PYPOWER OPF/PF entrypoint count')
    if not converged:
        faults.append('PYPOWER failed to converge')
    if newton['status'] != 'CONVERGED':
        faults.append('independent numerical Newton failed')
    if independent['status'] != 'RECONSTRUCTED_AND_CHECKED':
        faults.append('independent dispatch residual or scope invalid')

    cmp = None
    if converged and independent['status'] == 'RECONSTRUCTED_AND_CHECKED':
        own = independent['solved_case']
        online = np.flatnonzero(case['gen'][:, 7] > 0)
        reference_ids = set(case['bus'][case['bus'][:, 1] == 3, 0].astype(int))
        ref_g = [g for g in online if int(case['gen'][g, 0]) in reference_ids]
        metrics = {
            'max_online_qg_mvar': float(np.max(np.abs(own['gen'][online, 2] - pypower_case['gen'][online, 2]))),
            'max_reference_pg_mw': float(np.max(np.abs(own['gen'][ref_g, 1] - pypower_case['gen'][ref_g, 1]))),
            'max_complex_branch_flow_mva': float(np.max(np.abs(
                (own['branch'][:, 13] - pypower_case['branch'][:, 13]) + 1j *
                (own['branch'][:, 14] - pypower_case['branch'][:, 14])))),
            'max_to_complex_branch_flow_mva': float(np.max(np.abs(
                (own['branch'][:, 15] - pypower_case['branch'][:, 15]) + 1j *
                (own['branch'][:, 16] - pypower_case['branch'][:, 16])))),
        }
        reference = validate_constraint_components(pypower_case)
        if reference['status'] != 'AC_CONSISTENT_CONSTRAINT_CHECK':
            faults.append('reference PF AC residual invalid')
        if reference['components'] is not None:
            for key in COMPONENTS:
                metrics['constraint_difference_' + key] = abs(
                    independent['checker']['components'][key] - reference['components'][key])
        thresholds = {'max_online_qg_mvar': 1e-3,
                      'max_reference_pg_mw': 1e-3,
                      'max_complex_branch_flow_mva': 1e-3,
                      'max_to_complex_branch_flow_mva': 1e-3}
        thresholds.update({'constraint_difference_' + k: 1e-6 for k in COMPONENTS})
        for key, tol in thresholds.items():
            if key not in metrics or not np.isfinite(metrics[key]) or metrics[key] > tol:
                faults.append('predeclared cross-solver threshold exceeded: ' + key)
        independently_feasible = independent['checker']['i56_compatible_feasible']
        reference_feasible = reference['i56_compatible_feasible']
        if independently_feasible is not False or reference_feasible is not False:
            faults.append('original reactive-infeasible midpoint must remain infeasible')
        cmp = {'values': metrics, 'thresholds': thresholds,
               'independent_violations': independent['checker']['components'],
               'pypower_violations': reference['components'],
               'independent_i56_compatible_feasible': independently_feasible,
               'pypower_i56_compatible_feasible': reference_feasible,
               'independent_ac_residual': independent['checker']['residual']}
    result = {
        'status': 'PASS' if not faults else 'FAIL', 'faults': faults,
        'scenario': {'case': 'case30', 'j': 1, 'resolution': 17,
                     'candidate': 'fixed snapped midpoint, no search'},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'independent_newton': {'status': newton['status'],
                               'iterations': newton['iterations'],
                               'residual_evaluations': newton['residual_evaluations']},
        'pypower_converged': bool(converged), 'comparison': cmp,
        'solver_api_events': events,
        'source_git_blobs': {
            'frozen_i56': blob(RESEARCH / 'legacy/flat/iteration56_orpd.py'),
            'frozen_i58': blob(RESEARCH / 'legacy/flat/iteration58_validation.py'),
            'newton': blob(HERE / 'independent_ac_newton.py'),
            'dispatch': blob(HERE / 'independent_ac_dispatch.py'),
            'ac_residual': blob(HERE / 'ac_residual_witness.py'),
            'constraints': blob(HERE / 'orpd_operational_witness.py')},
        'interpretation': 'two software implementations of same AC case, not external grid truth or optimizer result'}
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not faults else 1


if __name__ == '__main__':
    sys.exit(main())
