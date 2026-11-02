"""Deterministic, no-PYPOWER tests of the independent Newton AC solver."""
import copy
import unittest

import numpy as np

from independent_ac_newton import UnsupportedACCase, solve_ac_pf


def two_bus():
    bus = np.zeros((2, 13))
    bus[:, 0] = [1, 2]
    bus[:, 1] = [3, 1]
    bus[:, 7] = [1, 1]
    bus[:, 11] = 1.1
    bus[:, 12] = .9
    bus[1, 2] = 19.6  # known two-bus solution: Vm2=.98, r=.1, PF losses=.4 MW
    gen = np.zeros((1, 10))
    gen[0, 0] = 1
    gen[0, 5] = 1
    gen[0, 7] = 1
    branch = np.zeros((1, 13))
    branch[0, 0:4] = [1, 2, .1, 0]
    branch[0, 10] = 1
    return {'baseMVA': 100., 'bus': bus, 'gen': gen, 'branch': branch}


def three_bus(*, complex_tap=False):
    c = two_bus()
    bus = np.zeros((3, 13))
    bus[:, 0] = [11, 12, 13]
    bus[:, 1] = [3, 2, 1]
    bus[:, 7] = 1.0
    bus[:, 11] = 1.1
    bus[:, 12] = .9
    gen = np.zeros((2, 10))
    gen[:, 0] = [11, 12]
    gen[:, 5] = [1.04, 1.02]
    gen[:, 7] = 1
    br = np.zeros((3, 13))
    br[:, :4] = [[11, 12, .02, .06], [12, 13, .08, .24], [11, 13, .06, .18]]
    br[:, 10] = 1
    if complex_tap:
        br[0, 8] = 1.03
        br[0, 9] = 3.0
        br[0, 4] = .05
        bus[1, 4] = 3.
        bus[2, 5] = -5.
    v = np.array([1.04, 1.02, .99]) * np.exp(1j * np.deg2rad([0, -1, -3]))
    # A separate compact reference calculation of prescribed P2/P3 and Q3.
    y = np.diag((bus[:, 4] + 1j * bus[:, 5]) / 100.).astype(complex)
    for b in br:
        u, w = [int(t - 11) for t in b[:2]]
        z = 1 / complex(b[2], b[3])
        a = (b[8] if b[8] else 1) * np.exp(1j * np.deg2rad(b[9]))
        bc = .5j * b[4]
        y[u, u] += (z + bc) / abs(a)**2
        y[u, w] -= z / a.conjugate()
        y[w, u] -= z / a
        y[w, w] += z + bc
    s = 100 * v * np.conj(y @ v)
    gen[1, 1] = s[1].real
    bus[2, 2] = -s[2].real
    bus[2, 3] = -s[2].imag
    return {'baseMVA': 100., 'bus': bus, 'gen': gen, 'branch': br}, v


class NewtonStandaloneTests(unittest.TestCase):
    def test_two_bus_exact_known_loss(self):
        r = solve_ac_pf(two_bus())
        self.assertEqual(r['status'], 'CONVERGED')
        self.assertAlmostEqual(r['voltage_magnitudes'][1], .98, places=7)
        self.assertAlmostEqual(r['branch_loss_mw'], .4, places=7)
        self.assertLess(r['mismatch_inf_pu'], 1e-9)

    def test_shunt_conductance_not_counted_as_branch_loss(self):
        c = two_bus()
        c['bus'][0, 4] = 5.0  # 5 MW of shunt GS at |Vref|=1 pu
        r = solve_ac_pf(c)
        self.assertEqual(r['status'], 'CONVERGED')
        self.assertAlmostEqual(r['branch_loss_mw'], .4, places=6)
        self.assertAlmostEqual(r['net_injection_mw'], 5.4, places=6)

    def test_three_bus_pv_pq_slack_from_flat_start(self):
        case, volts = three_bus()
        r = solve_ac_pf(case)
        self.assertEqual(r['status'], 'CONVERGED')
        np.testing.assert_allclose(r['voltage_magnitudes'], abs(volts), atol=1e-6)
        np.testing.assert_allclose(r['voltage_angles_deg'], np.rad2deg(np.angle(volts)), atol=1e-5)
        self.assertEqual(r['pv_buses'], 1)
        self.assertEqual(r['pq_buses'], 1)

    def test_phase_shifter_charging_shunt_nonconsecutive_ids(self):
        case, volts = three_bus(complex_tap=True)
        r = solve_ac_pf(case)
        self.assertEqual(r['status'], 'CONVERGED', r)
        np.testing.assert_allclose(r['voltage_magnitudes'], abs(volts), atol=1e-6)
        np.testing.assert_allclose(r['voltage_angles_deg'], np.rad2deg(np.angle(volts)), atol=1e-5)

    def test_original_case_is_not_mutated(self):
        case = two_bus()
        cp = copy.deepcopy(case)
        solve_ac_pf(case)
        for key in ('bus', 'gen', 'branch'):
            np.testing.assert_array_equal(case[key], cp[key])

    def test_zero_iterations_fails_closed_with_no_voltage_output(self):
        r = solve_ac_pf(two_bus(), max_iterations=0)
        self.assertEqual(r['status'], 'NOT_CONVERGED')
        self.assertEqual(r['reason'], 'max_iterations')
        self.assertNotIn('voltage_magnitudes', r)

    def test_singular_disconnected_network_fails_closed(self):
        c = two_bus()
        c['branch'][0, 10] = 0
        r = solve_ac_pf(c)
        self.assertEqual(r['status'], 'NOT_CONVERGED')
        self.assertEqual(r['reason'], 'singular_jacobian')

    def test_out_of_scope_bus_type_rejected(self):
        c = two_bus()
        c['bus'][1, 1] = 4
        with self.assertRaises(UnsupportedACCase):
            solve_ac_pf(c)

    def test_two_reference_buses_rejected(self):
        c = two_bus()
        c['bus'][1, 1] = 3
        with self.assertRaises(UnsupportedACCase):
            solve_ac_pf(c)

    def test_missing_online_ref_generator_rejected(self):
        c = two_bus()
        c['gen'][0, 7] = 0
        with self.assertRaises(UnsupportedACCase):
            solve_ac_pf(c)

    def test_conflicting_pv_generator_vg_rejected(self):
        c, _ = three_bus()
        extra = c['gen'][1].copy()
        extra[5] = 1.03
        c['gen'] = np.vstack((c['gen'], extra))
        with self.assertRaises(UnsupportedACCase):
            solve_ac_pf(c)

    def test_zero_active_impedance_rejected(self):
        c = two_bus()
        c['branch'][0, 2:4] = 0
        with self.assertRaises(UnsupportedACCase):
            solve_ac_pf(c)

    def test_bad_tolerances_and_caps_rejected(self):
        for kwargs in ({'tolerance_pu': float('nan')}, {'tolerance_pu': -1},
                       {'max_iterations': 10000}, {'jacobian_step': 0},
                       {'max_backtracks': 50}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                solve_ac_pf(two_bus(), **kwargs)

    def test_nonfinite_case_rejected(self):
        c = two_bus()
        c['bus'][1, 2] = float('nan')
        with self.assertRaises(UnsupportedACCase):
            solve_ac_pf(c)

    def test_missing_branch_bus_rejected(self):
        c = two_bus()
        c['branch'][0, 1] = 999
        with self.assertRaises(UnsupportedACCase):
            solve_ac_pf(c)

    def test_bounded_residual_evaluation_count(self):
        # 2-bus PQ: two unknowns and <= 30 Newton iterations; guard counters.
        r = solve_ac_pf(two_bus())
        self.assertLessEqual(r['residual_evaluations'], 1 + 20 * (1 + 2 * 2 + 15))
        self.assertGreater(r['residual_evaluations'], r['iterations'])


if __name__ == '__main__':
    unittest.main()
