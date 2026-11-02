"""Two-bus analytic validation and adversarial failures, no PYPOWER import."""
import copy
import unittest

import numpy as np

from ac_residual_witness import InvalidACCase, evaluate_ac_point


def two_bus():
    bus = np.zeros((2, 13))
    bus[:, 0] = (1, 2)
    bus[:, 1] = (3, 1)
    bus[:, 7] = (1., 1.)
    bus[:, 11] = 1.1
    bus[:, 12] = .9
    gen = np.zeros((1, 10))
    gen[0, 0] = 1
    gen[0, 7] = 1
    branch = np.zeros((1, 17))
    branch[0, :5] = [1, 2, 0, .1, 0]
    branch[0, 10] = 1
    return {'baseMVA': 100., 'bus': bus, 'gen': gen, 'branch': branch}


class ACWitnessTests(unittest.TestCase):
    def test_analytic_zero_flow(self):
        a = evaluate_ac_point(two_bus())
        self.assertEqual(a['status'], 'AC_RESIDUAL_PASS')
        self.assertEqual(a['max_nodal_mismatch_mva'], 0)
        self.assertEqual(a['loss_mw_independent_equations'], 0)

    def test_exact_resistive_two_bus_flow_and_losses(self):
        c = two_bus()
        # Analytic: r=0.1 pu, V1=1, V2=0.98, y=10 pu;
        # S_12=20 MW, S_21=-19.6 MW, resistive loss=0.4 MW.
        c['branch'][0, 2:4] = (.1, 0.)
        c['bus'][1, 7] = .98
        c['bus'][1, 2] = 19.6
        c['gen'][0, 1] = 20.
        c['branch'][0, 13] = 20.
        c['branch'][0, 15] = -19.6
        out = evaluate_ac_point(c)
        self.assertEqual(out['status'], 'AC_RESIDUAL_PASS')
        self.assertAlmostEqual(out['loss_mw_independent_equations'], .4, places=9)
        self.assertLess(out['max_nodal_mismatch_mva'], 1e-9)

    def test_analytic_resistive_loss_inconsistent_case_is_rejected(self):
        c = two_bus()
        c['branch'][0, 2:4] = (.1, 0.)
        c['bus'][1, 7] = .98
        c['bus'][1, 2] = 19.6
        c['gen'][0, 1] = 19.6  # neglecting physical 0.4 MW losses
        c['branch'][0, 13] = 20.
        c['branch'][0, 15] = -19.6
        self.assertEqual(evaluate_ac_point(c)['status'], 'AC_RESIDUAL_FAIL')

    def test_perturbed_generation_fails_balance(self):
        c = two_bus()
        c['gen'][0, 1] = 1
        self.assertEqual(evaluate_ac_point(c)['status'], 'AC_RESIDUAL_FAIL')

    def test_wrong_reported_branch_flow_fails(self):
        c = two_bus()
        c['branch'][0, 13] = 2
        self.assertEqual(evaluate_ac_point(c)['status'], 'AC_RESIDUAL_FAIL')

    def test_bus_shunt_is_included(self):
        c = two_bus()
        c['bus'][0, 5] = 10.  # Bs=+10 MVAr at 1 pu
        c['gen'][0, 2] = -10.
        self.assertEqual(evaluate_ac_point(c)['status'], 'AC_RESIDUAL_PASS')

    def test_open_branch_does_not_transfer_power(self):
        c = two_bus()
        c['branch'][0, 10] = 0
        self.assertEqual(evaluate_ac_point(c)['status'], 'AC_RESIDUAL_PASS')

    def test_nontrivial_tap_and_phase_shift_recompute(self):
        c = two_bus()
        br = c['branch'][0]
        br[8] = 1.05
        br[9] = 5.0
        mismatch = evaluate_ac_point(c)
        self.assertEqual(mismatch['status'], 'AC_RESIDUAL_FAIL')
        self.assertGreater(mismatch['max_nodal_mismatch_mva'], 0)

    def test_reject_nonfinite(self):
        c = two_bus()
        c['bus'][0, 8] = float('nan')
        with self.assertRaises(InvalidACCase):
            evaluate_ac_point(c)

    def test_reject_duplicate_bus(self):
        c = two_bus()
        c['bus'][1, 0] = 1
        with self.assertRaises(InvalidACCase):
            evaluate_ac_point(c)

    def test_reject_unmapped_active_line(self):
        c = two_bus()
        c['branch'][0, 1] = 999
        with self.assertRaises(InvalidACCase):
            evaluate_ac_point(c)

    def test_reject_zero_impedance(self):
        c = two_bus()
        c['branch'][0, 3] = 0
        with self.assertRaises(InvalidACCase):
            evaluate_ac_point(c)

    def test_reject_nonfinite_negative_tolerance(self):
        for bad in (-1, float('inf'), float('nan')):
            with self.assertRaises(InvalidACCase):
                evaluate_ac_point(two_bus(), balance_tolerance_mva=bad)

    def test_missing_solved_branch_fields(self):
        c = two_bus()
        c['branch'] = c['branch'][:, :13]
        with self.assertRaises(InvalidACCase):
            evaluate_ac_point(c)

    def test_balance_tolerance_controls_decision(self):
        c = two_bus()
        c['gen'][0, 1] = 1e-3
        self.assertEqual(evaluate_ac_point(c)['status'], 'AC_RESIDUAL_FAIL')
        self.assertEqual(evaluate_ac_point(c, balance_tolerance_mva=1e-2)['status'], 'AC_RESIDUAL_PASS')


if __name__ == '__main__':
    unittest.main()
