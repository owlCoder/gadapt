"""Iteration23 original IEEE118 Q-bracket preflight with ZERO native AC calls."""
import unittest
from research.iteration23_ieee118_qbracket import (
    history_source_preflight,ALPHAS,ID_BY_BUS,Q_HALF,Q_FULL,
)


class QPhysicalBracketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.solver,cls.proposal=history_source_preflight()

    def test_four_exact_alpha_values_fixed_prior(self):
        self.assertEqual(ALPHAS,(.6,.7,.8,.9))
        self.assertEqual(len(ALPHAS),4)
        self.assertAlmostEqual(Q_HALF,2.4644560480222957)
        self.assertAlmostEqual(Q_FULL,3.642855096077252)
        self.assertEqual(self.solver.real_ac_calls,0)

    def test_historical_slopes_three_source_generators(self):
        self.assertEqual(ID_BY_BUS,{34:15,92:42,19:8})
        self.assertEqual(set(self.proposal),{34,92,19})
        self.assertAlmostEqual(self.proposal[34],.004016033221868577,places=11)
        self.assertAlmostEqual(self.proposal[92],.003533199035653122,places=11)
        self.assertAlmostEqual(self.proposal[19],.004619105395208329,places=11)
        self.assertTrue(all(0<x<.008 for x in self.proposal.values()))

    def test_original_reactive_controls_source_not_mutated(self):
        gen=self.solver.source["gen"]
        self.assertEqual(len(gen),54)
        self.assertEqual(int(gen[45,0]),103)
        self.assertEqual(int(gen[14,0]),32)
        self.assertEqual([int(gen[i,0]) for i in ID_BY_BUS.values()],[34,92,19])
        self.assertEqual(self.solver.real_ac_calls,0)

if __name__=="__main__":
    unittest.main()
