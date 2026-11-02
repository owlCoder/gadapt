"""Analytic, adversarial, never imports or calls PYPOWER."""
import copy
import unittest
import numpy as np
from independent_ac_newton import solve_ac_pf, UnsupportedACCase
from independent_ac_dispatch import reconstruct_dispatch


def case2():
    bus = np.zeros((2, 13))
    bus[:, 0] = [1, 2]
    bus[:, 1] = [3, 1]
    bus[:, 7] = 1
    bus[:, 11], bus[:, 12] = 1.1, .9
    bus[1, 2] = 19.6
    gen = np.zeros((1, 10))
    gen[0, 0], gen[0, 5], gen[0, 7] = 1, 1, 1
    gen[0, 3], gen[0, 4] = 100, -100
    gen[0, 8], gen[0, 9] = 100, -100
    branch = np.zeros((1, 13))
    branch[0, :4] = [1, 2, .1, 0]
    branch[0, 10] = 1
    branch[0, 5] = 100
    return {'baseMVA':100., 'bus':bus, 'gen':gen, 'branch':branch}


class DispatchTests(unittest.TestCase):
    def test_analytic_ref_pg_and_branch(self):
        c=case2(); x=solve_ac_pf(c)
        out=reconstruct_dispatch(c,x)
        self.assertEqual(out['status'],'RECONSTRUCTED_AND_CHECKED')
        s=out['solved_case']
        self.assertAlmostEqual(s['gen'][0,1],20.,places=7)
        self.assertAlmostEqual(s['branch'][0,13],20.,places=7)
        self.assertAlmostEqual(s['branch'][0,15],-19.6,places=7)
        self.assertAlmostEqual(s['bus'][1,7],.98,places=7)
        self.assertTrue(out['checker']['i56_compatible_feasible'])
        self.assertAlmostEqual(out['checker']['residual']['loss_mw_independent_equations'],.4,places=7)

    def test_slack_pg_can_be_infeasible_even_after_convergence(self):
        c=case2();c['gen'][0,8]=19.
        r=reconstruct_dispatch(c,solve_ac_pf(c))
        self.assertEqual(r['status'],'RECONSTRUCTED_AND_CHECKED')
        self.assertFalse(r['checker']['i56_compatible_feasible'])
        self.assertAlmostEqual(r['checker']['components']['slack'],.01,places=7)

    def test_reference_q_injection_reconstructed(self):
        c=case2()
        c['bus'][1,3] = 5.0
        c['branch'][0,3]=.1
        # Not an analytic V target; Newton independently solves load.
        x=solve_ac_pf(c)
        self.assertEqual(x['status'],'CONVERGED')
        r=reconstruct_dispatch(c,x)
        self.assertEqual(r['status'],'RECONSTRUCTED_AND_CHECKED')
        self.assertNotAlmostEqual(r['solved_case']['gen'][0,2],0.,places=5)

    def test_voltage_and_generator_input_unchanged(self):
        c=case2();cp=copy.deepcopy(c)
        reconstruct_dispatch(c,solve_ac_pf(c))
        for name in ('bus','gen','branch'):
            np.testing.assert_array_equal(c[name],cp[name])

    def test_wrong_marked_converged_voltages_rejected(self):
        c=case2();x=solve_ac_pf(c)
        x['voltage_magnitudes'][1]=1.0
        out=reconstruct_dispatch(c,x)
        self.assertEqual(out['status'],'AC_RESIDUAL_FAIL')
        self.assertIsNone(out['solved_case'])

    def test_nonconverged_refused(self):
        c=case2();x=solve_ac_pf(c,max_iterations=0)
        self.assertEqual(x['status'],'NOT_CONVERGED')
        with self.assertRaises(UnsupportedACCase):
            reconstruct_dispatch(c,x)

    def test_multiple_online_reference_gen_unsupported(self):
        c=case2();c['gen']=np.vstack((c['gen'],c['gen'].copy()))
        with self.assertRaisesRegex(UnsupportedACCase,'one online generator'):
            reconstruct_dispatch(c,solve_ac_pf(c))

    def test_online_pq_generator_unsupported(self):
        c=case2();g=c['gen'][0].copy();g[0]=2;g[1]=0
        c['gen']=np.vstack((c['gen'],g))
        with self.assertRaisesRegex(UnsupportedACCase,'PQ-bus generator'):
            reconstruct_dispatch(c,solve_ac_pf(c))

    def test_offline_duplicate_generator_has_no_contribution(self):
        c=case2();g=c['gen'][0].copy();g[7]=0;g[1]=1e6
        c['gen']=np.vstack((c['gen'],g))
        out=reconstruct_dispatch(c,solve_ac_pf(c))
        self.assertEqual(out['status'],'RECONSTRUCTED_AND_CHECKED')
        self.assertEqual(out['solved_case']['gen'][1,1],1e6)

    def test_disconnected_branch_has_zero_flow(self):
        c=case2(); br=np.zeros((1,13));br[0,:2]=[1,2]
        c['branch']=np.vstack((c['branch'],br))
        out=reconstruct_dispatch(c,solve_ac_pf(c))
        self.assertEqual(out['status'],'RECONSTRUCTED_AND_CHECKED')
        np.testing.assert_array_equal(out['solved_case']['branch'][1,13:17],0)

    def test_invalid_vectors_refused(self):
        c=case2(); x=solve_ac_pf(c)
        for bad in ([1], [1,float('nan')], [-1,.98]):
            y=copy.deepcopy(x); y['voltage_magnitudes']=bad
            with self.assertRaises(UnsupportedACCase):
                reconstruct_dispatch(c,y)

    def test_missing_solved_gen_or_branch_fails_closed(self):
        c=case2();x=solve_ac_pf(c)
        x['voltage_angles_deg']=[]
        with self.assertRaises(UnsupportedACCase):
            reconstruct_dispatch(c,x)

    def test_tight_residual_threshold_prevents_false_pass(self):
        c=case2();x=solve_ac_pf(c)
        x['voltage_magnitudes'][1]+=1e-7
        out=reconstruct_dispatch(c,x,balance_tolerance_mva=1e-10)
        self.assertEqual(out['status'],'AC_RESIDUAL_FAIL')

    def test_voltage_constraint_detected_from_solved_vm(self):
        c=case2();c['bus'][1,12]=.99
        out=reconstruct_dispatch(c,solve_ac_pf(c))
        self.assertEqual(out['status'],'RECONSTRUCTED_AND_CHECKED')
        self.assertFalse(out['checker']['i56_compatible_feasible'])
        self.assertAlmostEqual(out['checker']['components']['voltage'],.01,places=7)

if __name__=='__main__':
    unittest.main()
