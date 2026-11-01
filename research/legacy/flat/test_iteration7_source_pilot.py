"""Budget/protocol structural tests for the source-correct RTE pilot."""
import unittest

from research.iteration7_source_rated_pilot import METHODS

class SourceRatedPilotProtocolTest(unittest.TestCase):
    def test_fixed_methods_and_population(self):
        self.assertEqual(METHODS,("gadapt_penalty","gadapt_feasibility_first",
                                 "slsqp_penalty","hybrid_fixed","scipy_de"))
        self.assertEqual(len(set(METHODS)),5)

    def test_regression_against_unpinned_experiment_substitution(self):
        from research.iteration7_rte_source_physics import DEFAULT_MAP
        self.assertEqual(DEFAULT_MAP,
          "research/results/rte1888_iteration7_matpower_to_pandapower_thermal_map_20261021.csv")

if __name__=="__main__":
    unittest.main()
