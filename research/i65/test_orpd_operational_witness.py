"""Analytic independent constraint checks; no PYPOWER or optimizer imports."""
import unittest

import numpy as np

from ac_residual_witness import InvalidACCase
from orpd_operational_witness import calculate_constraint_components, validate_constraint_components


def base_case():
    bus = np.zeros((2, 13))
    bus[:, 0] = (1, 2)
    bus[:, 1] = (3, 1)
    bus[:, 7] = 1
    bus[:, 11] = 1.1
    bus[:, 12] = .9
    gen = np.zeros((1, 10))
    gen[0, 0] = 1
    gen[0, 3] = 10
    gen[0, 4] = -10
    gen[0, 7] = 1
    gen[0, 8] = 100
    gen[0, 9] = -100
    br = np.zeros((1, 17))
    br[0, :4] = [1, 2, 0, .1]
    br[0, 5] = 100
    br[0, 10] = 1
    return {"baseMVA": 100., "bus": bus, "gen": gen, "branch": br}


def solved_resistive():
    case = base_case()
    case["branch"][0, 2:4] = (.1, 0)
    case["bus"][1, 7] = .98
    case["bus"][1, 2] = 19.6
    case["gen"][0, 1] = 20.
    case["branch"][0, 13] = 20.
    case["branch"][0, 15] = -19.6
    return case


class ConstraintWitnessTests(unittest.TestCase):
    def test_zero_limits(self):
        out = validate_constraint_components(base_case())
        self.assertEqual(out['status'], 'AC_CONSISTENT_CONSTRAINT_CHECK')
        self.assertTrue(out['i56_compatible_feasible'])
        self.assertEqual(sum(out['components'].values()), 0.)

    def test_voltage_upper_and_lower(self):
        c = base_case()
        c['bus'][:, 11] = .99
        c['bus'][:, 12] = .98
        self.assertAlmostEqual(calculate_constraint_components(c)['voltage'], .02)
        c['bus'][:, 11] = 1.2
        c['bus'][:, 12] = 1.1
        self.assertAlmostEqual(calculate_constraint_components(c)['voltage'], .2)

    def test_reactive_upper_and_lower(self):
        c = base_case()
        c['gen'][0, 3] = -1
        c['gen'][0, 4] = -10
        self.assertAlmostEqual(calculate_constraint_components(c)['reactive'], .01)
        c['gen'][0, 3] = 10
        c['gen'][0, 4] = 1
        self.assertAlmostEqual(calculate_constraint_components(c)['reactive'], .01)

    def test_slack_upper_and_lower(self):
        c = base_case()
        c['gen'][0, 8] = -1
        self.assertAlmostEqual(calculate_constraint_components(c)['slack'], .01)
        c['gen'][0, 8] = 100
        c['gen'][0, 9] = 1
        self.assertAlmostEqual(calculate_constraint_components(c)['slack'], .01)

    def test_thermal_max_of_two_ends(self):
        c = solved_resistive()
        c['branch'][0, 5] = 10
        out = validate_constraint_components(c)
        self.assertEqual(out['status'], 'AC_CONSISTENT_CONSTRAINT_CHECK')
        self.assertAlmostEqual(out['components']['thermal'], .1)
        self.assertFalse(out['i56_compatible_feasible'])

    def test_zero_rate_means_unlimited(self):
        c = solved_resistive()
        c['branch'][0, 5] = 0
        self.assertEqual(validate_constraint_components(c)['components']['thermal'], 0.)

    def test_offline_gen_excluded_from_reactive(self):
        c = base_case()
        offline = c['gen'][0].copy()
        offline[7] = 0
        offline[2] = 1e4
        c['gen'] = np.vstack((c['gen'], offline))
        self.assertEqual(calculate_constraint_components(c)['reactive'], 0.)

    def test_unmapped_reference_generator_fails_closed(self):
        c = base_case()
        c['gen'][0, 7] = 0
        with self.assertRaisesRegex(InvalidACCase, 'no online reference'):
            calculate_constraint_components(c)

    def test_perturbed_generation_rejects_residual_first(self):
        c = base_case()
        c['gen'][0, 1] = 1
        out = validate_constraint_components(c)
        self.assertEqual(out['status'], 'AC_RESIDUAL_FAIL')
        self.assertIsNone(out['components'])
        self.assertIsNone(out['i56_compatible_feasible'])

    def test_bad_branch_flow_rejects_residual_first(self):
        c = base_case()
        c['branch'][0, 13] = 1
        self.assertEqual(validate_constraint_components(c)['status'], 'AC_RESIDUAL_FAIL')

    def test_invalid_limits_rejected(self):
        cases = [base_case() for _ in range(4)]
        cases[0]['bus'][0, 11:13] = (.5, 1.2)
        cases[1]['gen'][0, 3:5] = (-2, 2)
        cases[2]['gen'][0, 8:10] = (-2, 2)
        cases[3]['branch'][0, 5] = -1
        for case in cases:
            with self.subTest(case=case['branch'][0, 5]), self.assertRaises(InvalidACCase):
                calculate_constraint_components(case)

    def test_invalid_tolerance_rejected(self):
        for tol in (float('nan'), float('inf'), -1):
            with self.assertRaises(InvalidACCase):
                validate_constraint_components(base_case(), i56_component_tolerance=tol)

    def test_multiple_slack_generators_and_nonref_ignored(self):
        c = base_case()
        g2 = c['gen'][0].copy()
        g2[8] = 0
        g2[1] = 15
        c['gen'] = np.vstack((c['gen'], g2))
        self.assertAlmostEqual(calculate_constraint_components(c)['slack'], .15)
        c['gen'][-1, 0] = 2
        self.assertEqual(calculate_constraint_components(c)['slack'], 0.)

    def test_all_four_violation_metrics(self):
        c = solved_resistive()
        c['bus'][1, 11] = .97
        c['gen'][0, 3] = -1
        c['gen'][0, 8] = 10
        c['branch'][0, 5] = 10
        out = validate_constraint_components(c)
        self.assertEqual(out['status'], 'AC_CONSISTENT_CONSTRAINT_CHECK')
        self.assertFalse(out['i56_compatible_feasible'])
        for key in ('voltage', 'reactive', 'slack', 'thermal'):
            self.assertGreater(out['components'][key], 0, key)

    def test_inverted_limits_cannot_be_relabelled_feasible(self):
        c = base_case()
        c['bus'][0, 12] = 1.3
        with self.assertRaises(InvalidACCase):
            validate_constraint_components(c)


if __name__ == '__main__':
    unittest.main()
