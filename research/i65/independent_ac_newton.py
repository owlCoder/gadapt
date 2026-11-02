"""Research-only independent NumPy AC power-flow *numerical solver*.

Finite-difference, damped polar Newton method with explicit REF/PV/PQ buses;
no PYPOWER imports, no optimizer, and no calls to prior solved AC states.
Models constant-power demands, line charging, phase-shifting taps and shunts.

This is a separate implementation of the standard Newton AC model, not a
new optimization method, an independent *physical* model or proof of ORPD
feasibility. Does NOT enforce Q limits, distribute Q among parallel gens,
solve OPF, islanded nets or adjust PV/PQ switching. Fail closed on those.
"""
from __future__ import annotations

import numpy as np


class UnsupportedACCase(ValueError):
    """Input outside the explicitly supported Newton model or invalid."""


def _prepare(case):
    try:
        base = float(case['baseMVA'])
        bus = np.array(case['bus'], dtype=float, copy=True)
        gen = np.array(case['gen'], dtype=float, copy=True)
        branch = np.array(case['branch'], dtype=float, copy=True)
    except (KeyError, ValueError, TypeError) as exc:
        raise UnsupportedACCase('invalid MATPOWER-format arrays') from exc
    if (not np.isfinite(base) or base <= 0 or bus.ndim != 2 or bus.shape[1] < 13
        or gen.ndim != 2 or gen.shape[1] < 10 or branch.ndim != 2 or branch.shape[1] < 11
        or not all(np.isfinite(x).all() for x in (bus, gen, branch))):
        raise UnsupportedACCase('incomplete or nonfinite case')
    ids = bus[:, 0]
    if np.any(ids != np.rint(ids)) or len(set(ids)) != len(ids):
        raise UnsupportedACCase('bus IDs must be distinct integers')
    if np.any(bus[:, 1] != np.rint(bus[:, 1])) or np.any(~np.isin(bus[:, 1], (1, 2, 3))):
        raise UnsupportedACCase('supports only PQ, PV and reference buses')
    ref = np.flatnonzero(bus[:, 1] == 3)
    if len(ref) != 1:
        raise UnsupportedACCase('requires exactly one reference bus')
    if np.any(gen[:, 7] < 0) or np.any(branch[:, 10] < 0):
        raise UnsupportedACCase('invalid generator or branch status')
    row = {int(b): i for i, b in enumerate(ids)}
    active = gen[gen[:, 7] > 0]
    for bg in active[:, 0]:
        if bg not in row:
            raise UnsupportedACCase('online generator references absent bus')
    if np.any(~np.isin(branch[branch[:, 10] > 0, :2].ravel(), ids)):
        raise UnsupportedACCase('online branch references absent bus')
    controlled = np.flatnonzero(np.isin(bus[:, 1], (2, 3)))
    for k in controlled:
        gs = active[active[:, 0] == bus[k, 0]]
        if len(gs) == 0:
            raise UnsupportedACCase('reference/PV bus without online generator')
        if np.any(gs[:, 5] <= 0) or np.ptp(gs[:, 5]) > 1e-9:
            raise UnsupportedACCase('conflicting/nonpositive generator voltage setpoints')
        bus[k, 7] = gs[0, 5]
    if np.any(bus[:, 7] <= 0):
        raise UnsupportedACCase('all initial magnitudes must be positive')
    Y = np.diag((bus[:, 4] + 1j * bus[:, 5]) / base).astype(complex)
    for br in branch[branch[:, 10] > 0]:
        frm, to = row[int(br[0])], row[int(br[1])]
        z = complex(br[2], br[3])
        if abs(z) == 0:
            raise UnsupportedACCase('zero impedance active branch')
        if br[8] < 0:
            raise UnsupportedACCase('negative tap')
        tap = (br[8] if br[8] else 1.) * np.exp(1j * np.deg2rad(br[9]))
        y, charge = 1. / z, 0.5j * br[4]
        Y[frm, frm] += (y + charge) / (abs(tap) ** 2)
        Y[frm, to] -= y / np.conj(tap)
        Y[to, frm] -= y / tap
        Y[to, to] += y + charge
    spec = - (bus[:, 2] + 1j * bus[:, 3]).astype(complex) / base
    for g in active:
        spec[row[int(g[0])]] += complex(g[1], g[2]) / base
    pq = np.flatnonzero(bus[:, 1] == 1)
    pv = np.flatnonzero(bus[:, 1] == 2)
    nonref = np.r_[pv, pq]
    return Y, spec, bus, nonref, pq, int(ref[0])


def _branch_loss_mw(case, voltages):
    """Calculate actual branch (not GS shunt) active loss from solved V."""
    bus = np.asarray(case['bus'], dtype=float)
    rows = {int(b): k for k, b in enumerate(bus[:, 0])}
    loss = 0.0
    base = float(case['baseMVA'])
    for line in np.asarray(case['branch'], dtype=float):
        if line[10] <= 0:
            continue
        from_i, to_i = rows[int(line[0])], rows[int(line[1])]
        series = 1 / complex(line[2], line[3])
        a = (line[8] if line[8] else 1.) * np.exp(1j * np.deg2rad(line[9]))
        charge = 0.5j * line[4]
        vf, vt = voltages[from_i], voltages[to_i]
        ifrom = (series + charge) / abs(a)**2 * vf - series / np.conj(a) * vt
        ito = (series + charge) * vt - series / a * vf
        loss += float(np.real(base * (vf * np.conj(ifrom) + vt * np.conj(ito))))
    return loss


def solve_ac_pf(case, *, tolerance_pu=1e-9, max_iterations=20,
                jacobian_step=1e-6, max_backtracks=14):
    """Solve P balance at PV/PQ and Q balance at PQ, independently.

    Deterministic finite-difference Jacobian; flat angles except fixed REF,
    flat 1.0 pu PQ magnitudes, PV/REF magnitudes from generator VG. Does not
    use a PYPOWER solution or its initial voltages/angles as Newton warm start.

    Returns a fail-closed diagnostic, rather than fabricating bus/gen outputs.
    Counts every residual-function evaluation (including FD and line search).
    """
    if (not np.isfinite(tolerance_pu) or tolerance_pu <= 0 or
        not np.isfinite(jacobian_step) or jacobian_step <= 0 or
        not isinstance(max_iterations, int) or not 0 <= max_iterations <= 30 or
        not isinstance(max_backtracks, int) or not 0 <= max_backtracks <= 20):
        raise ValueError('invalid bounded Newton parameters')
    Y, spec, bus, nonref, pq, ref = _prepare(case)
    n = len(bus)
    angles = np.zeros(n, dtype=float)
    angles[ref] = np.deg2rad(bus[ref, 8])
    magnitudes = np.ones(n, dtype=float)
    magnitudes[bus[:, 1] != 1] = bus[bus[:, 1] != 1, 7]
    n_angle, n_pq = len(nonref), len(pq)
    state = np.r_[angles[nonref], magnitudes[pq]]
    counters = {'residual_calls': 0}

    def evaluate(vector):
        counters['residual_calls'] += 1
        va = angles.copy()
        vm = magnitudes.copy()
        va[nonref] = vector[:n_angle]
        vm[pq] = vector[n_angle:]
        V = vm * np.exp(1j * va)
        injections = V * np.conj(Y @ V)
        mismatch = injections - spec
        return np.r_[mismatch[nonref].real, mismatch[pq].imag], V, injections

    reasons = []
    completed = 0
    for iteration in range(max_iterations + 1):
        f, v, injections = evaluate(state)
        error = float(np.max(abs(f), initial=0))
        if not np.isfinite(error):
            reasons.append('nonfinite_residual')
            break
        if error <= tolerance_pu:
            result = dict(status='CONVERGED', iterations=completed,
                          residual_evaluations=counters['residual_calls'],
                          mismatch_inf_pu=error,
                          voltage_magnitudes=np.abs(v).tolist(),
                          voltage_angles_deg=np.rad2deg(np.angle(v)).tolist(),
                          branch_loss_mw=_branch_loss_mw(case, v),
                          net_injection_mw=float(np.real(np.sum(injections)) * float(case['baseMVA'])),
                          buses=n, pq_buses=n_pq, pv_buses=n - 1 - n_pq)
            return result
        if iteration == max_iterations:
            reasons.append('max_iterations')
            break
        dim = len(state)
        J = np.empty((len(f), dim), dtype=float)
        for j in range(dim):
            perturbed = state.copy()
            perturbed[j] += jacobian_step
            fplus, _, _ = evaluate(perturbed)
            perturbed[j] -= 2 * jacobian_step
            fminus, _, _ = evaluate(perturbed)
            J[:, j] = (fplus - fminus) / (2 * jacobian_step)
        try:
            delta = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError:
            reasons.append('singular_jacobian')
            break
        accepted = False
        for k in range(max_backtracks + 1):
            trial = state + (0.5 ** k) * delta
            if np.any(trial[n_angle:] <= 0):
                continue
            tf, _, _ = evaluate(trial)
            trial_error = float(np.max(abs(tf), initial=0))
            if np.isfinite(trial_error) and trial_error < error:
                state = trial
                completed += 1
                accepted = True
                break
        if not accepted:
            reasons.append('no_descent_step')
            break
    return dict(status='NOT_CONVERGED', reason=reasons[0],
                iterations=completed, residual_evaluations=counters['residual_calls'],
                mismatch_inf_pu=error, buses=n, pq_buses=n_pq,
                pv_buses=n - 1 - n_pq)
