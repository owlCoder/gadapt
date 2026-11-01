"""Zero-domain theorem check on intentionally impossible source cut."""
import unittest
import numpy as np
from research.iteration38_joint_capacity_model import SourceLink
from research.iteration38_cut_feasibility_certificate import cut_witness


class CutCertificateTinyTests(unittest.TestCase):
    def test_overloaded_singleton_is_proof_in_any_routing(self):
        nodes=("A","B")
        links=(SourceLink("AB","A","B",0,0,0,0,((3,1),)),)
        pairs=(("A","B"),)
        witnesses=cut_witness(nodes,links,pairs,np.asarray([[2.],[5.]]),1)
        self.assertEqual(len(witnesses),2)
        self.assertAlmostEqual(witnesses[0]["mathematically_necessary_shortfall"],2.)
        self.assertEqual(witnesses[0]["first_witness_time"],1)
        self.assertEqual(witnesses[0]["violated_time_count"],1)

    def test_no_violation_is_not_a_feasibility_certificate(self):
        nodes=("A","B")
        links=(SourceLink("AB","A","B",0,0,0,0,((10,1),)),)
        self.assertEqual(cut_witness(nodes,links,(("A","B"),),np.asarray([[5.]]),1),[])


if __name__=="__main__":
    unittest.main()
