"""Iteration 16 IEEE14 and IEEE118 physical OPF controls: ZERO optimizer calls."""
import copy
import unittest

import numpy as np
from pypower.case14 import case14
from pypower.case118 import case118

from research.iteration16_ieee_original_acopf import (
    check_case_structure,inspect_opf_result
)
from research.iteration11_original_matpower_native_pf import (
    summed_limit_violation,original_rate_a_violation
)


class IEEEACOPFValidatorTests(unittest.TestCase):
    def test_genuine_ieee_quadratic_costs_and_source_counts(self):
        x=check_case_structure(case14())
        y=check_case_structure(case118())
        self.assertEqual(x["original_bus_count"],14)
        self.assertEqual(y["original_bus_count"],118)
        self.assertEqual(x["original_gen_count"],5)
        self.assertEqual(y["original_gen_count"],54)

    def test_cannot_audit_incomplete_source_as_feasible_opf(self):
        s=case14()
        s["gencost"]=s["gencost"][:-1]
        with self.assertRaises(ValueError):
            check_case_structure(s)

    def test_source_branch_unrated_and_to_end_flow_checked(self):
        branch=np.zeros((2,17))
        branch[:,10]=1
        branch[:,5]=[0,150]
        branch[0,13]=999.
        branch[1,15]=151.
        d=original_rate_a_violation(branch)
        self.assertEqual(d["rated_active_branches"],1)
        self.assertEqual(d["unrated_active_branches"],1)
        self.assertEqual(d["overloaded_branches"],1)

    def test_single_generator_p_q_violation_is_never_ignored(self):
        p=summed_limit_violation([8.,0.],[9.,0.],[15.,0.],[True,False])
        q=summed_limit_violation([0.,-6.],[-1.,-5.],[1.,10.],[True,True])
        self.assertEqual(p["below_limit_count"],1)
        self.assertEqual(q["below_limit_count"],1)

    def test_unsolved_input_must_not_claim_validated_acopf(self):
        s=case14()
        with self.assertRaises((ValueError,KeyError,IndexError)):
            inspect_opf_result(copy.deepcopy(s),s)

if __name__=="__main__":
    unittest.main()
