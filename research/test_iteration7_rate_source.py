"""Tests for independent RTE rating provenance (no AC calls)."""
import unittest
from collections import Counter

from research.iteration7_source_rating_map import source_branches, unordered


class RatingProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=source_branches("research/results/rte1888_matpower_original_branch_ratings_2019.csv")

    def test_original_source_counts_and_nonnegativity(self):
        self.assertEqual(len(self.rows),2531)
        self.assertEqual(sum(r["rate_a_mva"]==0 for r in self.rows),455)
        self.assertEqual(sum(r["rate_a_mva"]>0 for r in self.rows),2076)

    def test_original_transformers_404_and_466_have_no_matpower_rate_a(self):
        for pair in ((453,1699),(107,1732),(452,1697),(451,1698)):
            branch=[r for r in self.rows
                    if unordered(r["from_bus"],r["to_bus"])==unordered(*pair)]
            self.assertEqual(len(branch),1)
            self.assertEqual(branch[0]["rate_a_mva"],0.)
            self.assertEqual(branch[0]["rate_b_mva"],0.)

    def test_parallel_mixed_rating_must_not_be_mapped_by_pair_alone(self):
        group=[r for r in self.rows if unordered(r["from_bus"],r["to_bus"])==(28,289)]
        self.assertEqual(len(group),2)
        self.assertEqual({r["rate_a_mva"] for r in group},{356.,452.})

if __name__=="__main__":
    unittest.main()
