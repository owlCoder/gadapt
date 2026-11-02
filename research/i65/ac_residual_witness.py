"""Research-only, PYPOWER-independent AC residual/flow verifier.

Takes plain MATPOWER/PYPOWER-format case + already-solved bus/gen/branch
arrays, but NEVER imports PYPOWER or calls a power-flow solver.

This is an independent implementation of AC network equations (including
line charging, taps, phase shift and bus shunts), NOT an independently
implemented numerical PF solver: it validates a supplied operating point.
No optimization or held-out model access is performed here.
"""
from __future__ import annotations

import hashlib
import json
import numpy as np


class InvalidACCase(ValueError):
    """Invalid / unsupported case layout, no validation claim allowed."""


def _arrays(case):
    try:
        base = float(case['baseMVA'])
        bus = np.asarray(case['bus'], dtype=float)
        gen = np.asarray(case['gen'], dtype=float)
        branch = np.asarray(case['branch'], dtype=float)
    except (KeyError, TypeError, ValueError) as ex:
        raise InvalidACCase('invalid case arrays') from ex
    if (not np.isfinite(base) or base <= 0 or
        bus.ndim != 2 or bus.shape[1] < 13 or
        gen.ndim != 2 or gen.shape[1] < 10 or
        branch.ndim != 2 or branch.shape[1] < 13 or
        not all(np.isfinite(a).all() for a in (bus, gen, branch))):
        raise InvalidACCase('invalid shape, baseMVA or nonfinite values')
    ids = bus[:, 0]
    if np.any(ids != np.rint(ids)) or len(set(ids)) != len(ids):
        raise InvalidACCase('bus ids must be unique integers')
    row = {int(v): i for i, v in enumerate(ids)}
    for i in np.r_[gen[gen[:, 7] > 0, 0], branch[branch[:, 10] > 0, :2].ravel()]:
        if i not in row:
            raise InvalidACCase('active generator or branch references missing bus')
    if np.any(branch[:, 10] < 0) or np.any(gen[:, 7] < 0):
        raise InvalidACCase('invalid negative status')
    return base, bus, gen, branch, row


def evaluate_ac_point(case, *, balance_tolerance_mva=1e-4,
                      flow_tolerance_mva=1e-4):
    """Check P/Q nodal balance and recompute branch flows independently.

    All arrays should be an already converged operating point, not a search
    vector or an unsolved case. Returns diagnostics, not a VALIDATED_WITNESS
    status: an AC residual is not a full independent-solver certificate.
    """
    if not all(np.isfinite(t) and t >= 0 for t in
               (balance_tolerance_mva, flow_tolerance_mva)):
        raise InvalidACCase('tolerances must be finite and nonnegative')
    base, bus, gen, branch, row = _arrays(case)
    n = len(bus)
    volts = bus[:, 7] * np.exp(1j * np.deg2rad(bus[:, 8]))
    if np.any(bus[:, 7] <= 0):
        raise InvalidACCase('nonpositive bus voltage')
    admittance = np.zeros((n, n), dtype=complex)
    branch_powers = np.zeros((len(branch), 2), dtype=complex)
    for k, br in enumerate(branch):
        if br[10] <= 0:
            continue
        frm, to = row[int(br[0])], row[int(br[1])]
        r, x, b = br[2], br[3], br[4]
        if r == 0 and x == 0:
            raise InvalidACCase('in-service branch zero impedance')
        tap = br[8] if br[8] != 0 else 1.0
        if tap <= 0:
            raise InvalidACCase('invalid tap magnitude')
        tap_complex = tap * np.exp(1j * np.deg2rad(br[9]))
        y = 1 / complex(r, x)
        charge = 0.5j * b
        yff = (y + charge) / abs(tap_complex)**2
        yft = -y / np.conj(tap_complex)
        ytf = -y / tap_complex
        ytt = y + charge
        admittance[frm, frm] += yff
        admittance[frm, to] += yft
        admittance[to, frm] += ytf
        admittance[to, to] += ytt
        vf, vt = volts[frm], volts[to]
        branch_powers[k, 0] = base * vf * np.conj(yff * vf + yft * vt)
        branch_powers[k, 1] = base * vt * np.conj(ytf * vf + ytt * vt)
    admittance[np.diag_indices(n)] += (bus[:, 4] + 1j * bus[:, 5]) / base
    injected = base * volts * np.conj(admittance @ volts)
    specified = -(bus[:, 2] + 1j * bus[:, 3]).astype(complex)
    active_generators = gen[gen[:, 7] > 0]
    for g in active_generators:
        specified[row[int(g[0])]] += g[1] + 1j * g[2]
    imbalance = injected - specified
    # PF solution branch entries: PF, QF, PT, QT = columns 13..16.
    reported = np.asarray(case['branch'], float)
    if reported.shape[1] < 17:
        raise InvalidACCase('solved branch matrix requires PF/QF/PT/QT columns')
    reported_flow = np.column_stack([reported[:, 13] + 1j * reported[:, 14],
                                     reported[:, 15] + 1j * reported[:, 16]])
    if not np.isfinite(reported_flow).all():
        raise InvalidACCase('nonfinite solved branch flows')
    flow_delta = branch_powers - reported_flow
    balance_max = float(np.max(np.abs(imbalance), initial=0))
    branch_max = float(np.max(np.abs(flow_delta), initial=0))
    loss_mw = float(np.real(np.sum(branch_powers)))
    reported_loss_mw = float(np.sum(reported[:, 13] + reported[:, 15]))
    # The residual comparisons are strictly diagnostic; a pass is necessary
    # but not sufficient for independently validated physical feasibility.
    return {
        'status': 'AC_RESIDUAL_PASS' if balance_max <= balance_tolerance_mva and
                  branch_max <= flow_tolerance_mva else 'AC_RESIDUAL_FAIL',
        'bus_count': n,
        'branch_count': len(branch),
        'active_generator_count': len(active_generators),
        'max_nodal_mismatch_mva': balance_max,
        'max_branch_flow_difference_mva': branch_max,
        'loss_mw_independent_equations': loss_mw,
        'loss_mw_reported': reported_loss_mw,
        'loss_mw_difference': loss_mw - reported_loss_mw,
        'balance_tolerance_mva': balance_tolerance_mva,
        'flow_tolerance_mva': flow_tolerance_mva,
        'meaning': 'residual of supplied PF solution, not independent numerical PF solver',
    }
