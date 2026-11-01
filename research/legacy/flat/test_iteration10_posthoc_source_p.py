"""Post hoc arithmetic only; 0 AC calls."""
import unittest
from research.iteration10_posthoc_source_p import (
    aggregate_pg_check, audit_rows, source_bounds)
from research.iteration9_source_generators import read_sources

class PosthocSourcePTests(unittest.TestCase):
    def test_source_2019_has_two_distinct_active_bus1268_generators(self):
        rows,_=read_sources()
        total=source_bounds(rows,1268)
        self.assertEqual(total["active_original_generators"],2)
        self.assertEqual(total["source_pmin_sum_mw"],88)
        self.assertEqual(total["source_pmax_sum_mw"],90)
        self.assertEqual(total["source_initial_pg_sum_mw"],89)

    def test_grouped_bounds_not_ext_only(self):
        base=aggregate_pg_check(55.00583800688405,44.5,88,90)
        self.assertAlmostEqual(base["observed_source_bus_pg_total_mw"],99.50583800688405)
        self.assertAlmostEqual(base["p_above_original_aggregate_pmax_mw"],9.50583800688405)
        self.assertFalse(base["p_within_original_aggregate_bounds"])
        alt=aggregate_pg_check(0.,89.,88.,90.)
        self.assertTrue(alt["p_within_original_aggregate_bounds"])

    def test_rejects_invented_or_incomplete_run_budget(self):
        rows,_=read_sources()
        with self.assertRaises(ValueError):
            audit_rows({"metadata":{"actual_ac_powerflow_calls":1},"rows":[]},rows)

if __name__=="__main__":
    unittest.main()
