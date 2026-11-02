#!/usr/bin/env python3
"""One non-held-out I58 case30/j1: four independent I56 constraint aggregates.

No optimizer. One historical ORPD.evaluate PF, one PYPOWER witness PF, and
one setup OPF. Constraint computations are separate NumPy-only arithmetic;
no claim of independent numerical AC power-flow or novel algorithm.
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
    raise SystemExit('BLOCKED: original research symlinks not restored')
sys.path.insert(0, str(RESEARCH))
sys.path.insert(0, str(HERE))

from pypower import api
from pypower.idx_gen import VG
from pypower.idx_brch import TAP
from pypower.idx_bus import BS

import iteration58_validation as i58
from orpd_operational_witness import COMPONENTS, validate_constraint_components
from orpd_solver_entry_audit import SolverEntryAudit


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def clone_case(case):
    return {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in case.items()}


def tamper_limits_only(solved, baseline):
    """Falsify each constraint category in-memory, no additional PF solve."""
    variants = {}
    # Lower the max voltage below an already-solved bus magnitude.
    c = clone_case(solved)
    row = 0
    vm = float(c['bus'][row, 7])
    # Use the *whole baseline penalty*, not only the chosen bus's current
    # excess: this guarantees an increase even if other buses already fail.
    c['bus'][row, 11] = vm - float(baseline['voltage']) - .05
    c['bus'][row, 12] = min(float(c['bus'][row, 12]), float(c['bus'][row, 11]) - .1)
    variants['voltage'] = c

    # Break the first active generator's upper reactive limit by at least 1 MVAr.
    c = clone_case(solved)
    gen = c['gen']
    g = int(np.flatnonzero(gen[:, 7] > 0)[0])
    q = float(gen[g, 2])
    # A candidate can ALREADY violate several QMIN bounds. Lowering QMIN
    # while adding a small QMAX violation can reduce the total sum (observed
    # in the first real case30 smoke). Force this single generator's new
    # upper violation to EXCEED the entire old reactive sum by 1 MVAr.
    gen[g, 3] = q - float(baseline['reactive']) * float(solved['baseMVA']) - 1.
    gen[g, 4] = min(float(gen[g, 4]), float(gen[g, 3]) - 1.)
    variants['reactive'] = c

    # Break the ref bus generator's PG upper bound by at least 1 MW.
    c = clone_case(solved)
    gen = c['gen']
    buses = set(c['bus'][c['bus'][:, 1] == 3, 0].astype(int))
    ref = [k for k, row in enumerate(gen) if row[7] > 0 and int(row[0]) in buses]
    if not ref:
        raise RuntimeError('no reference generator available for controlled tamper')
    g = ref[0]
    pg = float(gen[g, 1])
    gen[g, 8] = pg - float(baseline['slack']) * float(solved['baseMVA']) - 1.
    gen[g, 9] = min(float(gen[g, 9]), float(gen[g, 8]) - 1.)
    variants['slack'] = c

    # A positive branch limit smaller than its actual |S| at one end.
    c = clone_case(solved)
    br = c['branch']
    flow = np.maximum(np.hypot(br[:, 13], br[:, 14]), np.hypot(br[:, 15], br[:, 16]))
    k = int(np.argmax(flow))
    if flow[k] <= 1:
        raise RuntimeError('development case has no suitable positive-flow branch')
    old = float(br[k, 5])
    if old > 0 and flow[k] > old:
        proposed = min(old / 2, flow[k] - 1)
    else:
        proposed = flow[k] - 1
    br[k, 5] = max(.0001, proposed)
    variants['thermal'] = c
    return variants


def main() -> int:
    audit = SolverEntryAudit()
    with audit.trace():
        with audit.phase('setup'):
            problem = i58.make_problem('case30', 1)
        x = problem.snap((problem.lo + problem.hi) / 2)
        d = problem.delegate
        nb = len(problem.bus_groups)
        controls = d.snap(np.concatenate([x[:nb][problem.expand], x[nb:]]))
        case = clone_case(d.base)
        ng, nt = len(d.gen_rows), len(d.tap_rows)
        case['gen'][d.gen_rows, VG] = controls[:ng]
        case['branch'][d.tap_rows, TAP] = controls[ng:ng + nt]
        case['bus'][d.shunt_rows, BS] = controls[ng + nt:]
        with audit.phase('search'):
            legacy = d.evaluate(controls)
        with audit.phase('witness'):
            solved, converged = api.runpf(case, d.options)

    faults = []
    expected = {'setup': {'runopf': 1, 'runpf': 0},
                'search': {'runopf': 0, 'runpf': 1},
                'witness': {'runopf': 0, 'runpf': 1}}
    trace = audit.evidence()
    if trace['phases'] != expected:
        faults.append('unexpected solver API entrypoint count')
    if not converged or not legacy.get('converged', False):
        faults.append('original or independent diagnostic PF did not converge')
    new = validate_constraint_components(solved) if converged else None
    if new and new['status'] != 'AC_CONSISTENT_CONSTRAINT_CHECK':
        faults.append('AC residual mismatch before constraint comparison')
    observed_delta = None
    checks = {}
    if new and new['components'] is not None and legacy.get('violations') is not None:
        observed_delta = {key: abs(new['components'][key] - float(legacy['violations'][key]))
                          for key in COMPONENTS}
        # Precommitted absolute tolerance on dimensionless I56 components.
        if any(v > 1e-8 for v in observed_delta.values()):
            faults.append('original I56 and NumPy constraint aggregation mismatch')
        if new['i56_compatible_feasible'] != bool(legacy['feasible']):
            faults.append('I56 feasibility label differs from residual-conditioned verifier')
        for key, altered in tamper_limits_only(solved, new['components']).items():
            checked = validate_constraint_components(altered)
            original_v = new['components'][key]
            changed_v = checked['components'][key] if checked['components'] else None
            increases = (checked['status'] == 'AC_CONSISTENT_CONSTRAINT_CHECK' and
                         changed_v is not None and changed_v > original_v + 1e-5)
            checks[key] = {'detected': bool(increases), 'original': original_v,
                           'tampered': changed_v}
            if not increases:
                faults.append('limit-only tamper not detected: ' + key)
    else:
        faults.append('missing comparable PF and I56 violation components')

    result = {
        'status': 'PASS' if not faults else 'FAIL',
        'scenario': {'network': 'case30', 'j': 1, 'resolution': 17},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'legacy': {'converged': bool(legacy.get('converged')), 'feasible': bool(legacy.get('feasible')),
                   'violations': legacy.get('violations'), 'losses': legacy.get('losses')},
        'independent_constraint_verifier': new,
        'absolute_metric_differences': observed_delta,
        'fixed_metric_difference_tolerance': 1e-8,
        'controlled_metadata_tamper': checks,
        'solver_api_entries': trace,
        'source_git_blobs': {
            'orpd': git_blob(RESEARCH / 'legacy/flat/iteration56_orpd.py'),
            'i58': git_blob(RESEARCH / 'legacy/flat/iteration58_validation.py'),
            'ac_equations': git_blob(HERE / 'ac_residual_witness.py'),
            'constraint_verifier': git_blob(HERE / 'orpd_operational_witness.py'),
        },
        'faults': faults,
        'scope': 'one previously used development case, not independent PF solver or optimizer benchmark',
    }
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not faults else 1


if __name__ == '__main__':
    sys.exit(main())
