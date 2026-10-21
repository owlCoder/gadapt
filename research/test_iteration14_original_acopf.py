"""Iteration 14 preregistered SOURCE AC-OPF audit unit tests. No solver calls."""
import unittest

import numpy as np
from scipy.sparse import csr_matrix

from research.iteration14_original_acopf import (
    source_opf_data,native_ac_mismatch,original_cost,CONSTRAINT_TOL,
    audit_success,
)


class NativeACOPFSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=source_opf_data()

    def test_unmodified_source_case_and_original_linear_economic_costs(self):
        c=self.original
        self.assertEqual(c["gencost"].shape,(298,7))
        self.assertEqual(c["gen"].shape,(298,21))
        self.assertEqual(c["bus"].shape,(1888,13))
        self.assertEqual(c["branch"].shape,(2531,13))
        self.assertEqual(len(c["bus"][c["bus"][:,1]==3]),1)
        self.assertEqual(int(c["bus"][c["bus"][:,1]==3,0][0]),1320)
        self.assertTrue(np.all(c["gencost"][:,0]==2))
        self.assertTrue(np.all(c["gencost"][:,3]==3))
        self.assertEqual(set(c["gencost"][:,5]),{1.,2.,10.})
        self.assertEqual(int(np.sum(c["branch"][:,5]==0)),455)
        self.assertEqual(int(np.sum(c["gen"][:,7]>0)),291)

    def test_nodal_mismatch_on_exact_one_bus_balance(self):
        y=csr_matrix(np.array([[0+0j]]))
        summary=native_ac_mismatch(y,np.array([1.+0j]),np.array([0.+0j]),100.)
        self.assertEqual(summary["max_bus_nodal_mismatch_mva"],0.)
        self.assertEqual(summary["buses_nodal_mismatch_over_1e_3_mva"],0)

    def test_nodal_mismatch_reports_reactive_not_just_active_residual(self):
        y=csr_matrix(np.array([[-1j]]))
        report=native_ac_mismatch(y,np.array([1.+0j]),np.array([0.+0j]),100.)
        self.assertAlmostEqual(report["max_bus_nodal_mismatch_mva"],100.)
        self.assertEqual(report["buses_nodal_mismatch_over_1e_3_mva"],1)

    def test_original_cost_recomputation_rejects_fake_claimed_improvement(self):
        c=self.original
        expected=float(np.sum(c["gencost"][c["gen"][:,7]>0,5]*
                              c["gen"][c["gen"][:,7]>0,1]))
        fake={"gen":c["gen"].copy(),"f":expected}
        out=original_cost(fake,c)
        self.assertTrue(out["original_economic_objective_matches"])
        self.assertAlmostEqual(out["objective_original_gencost_recomputed"],expected)
        fake["f"]+=300.
        invalid=original_cost(fake,c)
        self.assertFalse(invalid["original_economic_objective_matches"])

    def test_degenerate_or_incomplete_solver_output_cannot_be_certified(self):
        with self.assertRaises((ValueError,KeyError,IndexError)):
            audit_success({"bus":np.zeros((100,13))},self.original)

    def test_kcl_tolerances_have_declared_units(self):
        self.assertEqual(CONSTRAINT_TOL["nodal_mismatch_mva"],1e-3)
        self.assertEqual(CONSTRAINT_TOL["generator_p_mw"],1e-3)
        self.assertEqual(CONSTRAINT_TOL["generator_q_mvar"],1e-3)
        self.assertEqual(CONSTRAINT_TOL["rated_branch_terminal_mva"],1e-3)


if __name__=="__main__":
    unittest.main()
