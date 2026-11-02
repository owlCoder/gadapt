"""Reconstruct REF/PV generator injections and flows from independently solved V.

Research-only; no PYPOWER imports, OPF or optimizer. The original input case
is required and is never mutated. Exactly one online generator per REF/PV
bus, none at PQ buses: otherwise individual Q allocations are not identifiable
from bus-level AC power flow and this checker fails closed.

Returns a solved MATPOWER-like array for cross-check with an independent
AC residual and I56 four-component operational constraint checker. This
is an independent NUMERICAL implementation of the SAME classical AC model;
not independent physical network evidence, and not a Q-limit-enforcing PF.
"""
from __future__ import annotations

import numpy as np
from independent_ac_newton import UnsupportedACCase, _prepare
from orpd_operational_witness import validate_constraint_components


def reconstruct_dispatch(case, numerical_pf, *, balance_tolerance_mva=1e-3,
                         flow_tolerance_mva=1e-5):
    if not isinstance(numerical_pf, dict) or numerical_pf.get('status') != 'CONVERGED':
        raise UnsupportedACCase('numerical AC PF must converge before dispatch reconstruction')
    Y, _, prepared_bus, _, _, ref = _prepare(case)
    base = float(case['baseMVA'])
    bus = np.asarray(case['bus'], dtype=float).copy()
    gen = np.asarray(case['gen'], dtype=float).copy()
    branch_src = np.asarray(case['branch'], dtype=float)
    branch = np.zeros((len(branch_src), max(17, branch_src.shape[1])))
    branch[:, :branch_src.shape[1]] = branch_src
    n = len(bus)
    try:
        vm = np.asarray(numerical_pf['voltage_magnitudes'], dtype=float)
        va = np.asarray(numerical_pf['voltage_angles_deg'], dtype=float)
    except (KeyError, TypeError, ValueError) as exc:
        raise UnsupportedACCase('missing numerical voltage vectors') from exc
    if (vm.shape != (n,) or va.shape != (n,) or not np.isfinite(vm).all()
            or not np.isfinite(va).all() or np.any(vm <= 0)):
        raise UnsupportedACCase('invalid numerical voltage vectors')
    # Prevent accidentally accepting a fake CONVERGED status paired with an
    # arbitrary voltage vector: the AC residual checks below are mandatory.
    bus[:, 7], bus[:, 8] = vm, va
    voltage = vm * np.exp(1j * np.deg2rad(va))
    injection = base * voltage * np.conj(Y @ voltage)
    id_map = {int(v): i for i, v in enumerate(bus[:, 0])}
    online = np.flatnonzero(gen[:, 7] > 0)
    counts = {int(v): 0 for v in bus[:, 0]}
    for g in online:
        b = int(gen[g, 0])
        counts[b] += 1
        if bus[id_map[b], 1] == 1:
            raise UnsupportedACCase('PQ-bus generator distribution is out of scope')
    for k in range(n):
        is_voltage_controlled = bus[k, 1] in (2, 3)
        n_gens = counts[int(bus[k, 0])]
        if is_voltage_controlled and n_gens != 1:
            raise UnsupportedACCase('one online generator per PV/REF bus required')
        if not is_voltage_controlled and n_gens:
            raise UnsupportedACCase('PQ generator unsupported')
    for g in online:
        k = id_map[int(gen[g, 0])]
        # Reactive QG is unknown at PV and REF; always recompute from network.
        gen[g, 2] = injection[k].imag + bus[k, 3]
        # Slack PG is likewise unknown. PV PG stays fixed by input.
        if k == ref:
            gen[g, 1] = injection[k].real + bus[k, 2]
    for k, line in enumerate(branch):
        if line[10] <= 0:
            branch[k, 13:17] = 0.0
            continue
        f, t = id_map[int(line[0])], id_map[int(line[1])]
        y = 1 / complex(line[2], line[3])
        tap = (line[8] if line[8] else 1.) * np.exp(1j * np.deg2rad(line[9]))
        b = 0.5j * line[4]
        vf, vt = voltage[f], voltage[t]
        ifrom = (y + b) / abs(tap)**2 * vf - y / np.conj(tap) * vt
        ito = (y + b) * vt - y / tap * vf
        sf, st = base * vf * np.conj(ifrom), base * vt * np.conj(ito)
        branch[k, 13:17] = (sf.real, sf.imag, st.real, st.imag)
    solved = {k: (np.asarray(v).copy() if isinstance(v, np.ndarray) else v)
              for k, v in case.items()}
    solved.update(bus=bus, gen=gen, branch=branch)
    checked = validate_constraint_components(
        solved, residual_balance_tolerance_mva=balance_tolerance_mva,
        residual_flow_tolerance_mva=flow_tolerance_mva)
    if checked['status'] != 'AC_CONSISTENT_CONSTRAINT_CHECK':
        return {'status': 'AC_RESIDUAL_FAIL', 'checker': checked,
                'solved_case': None}
    return {'status': 'RECONSTRUCTED_AND_CHECKED', 'checker': checked,
            'solved_case': solved,
            'scope': 'single-generator PV/REF fixed-PV-PG PF, no Q limits enforced'}
