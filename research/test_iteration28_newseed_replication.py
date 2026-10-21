"""I28 new-seed holdout protocol tests; NO AC solver is invoked."""
import unittest

from research.iteration28_newseed_scenario_credit_replication import (
    SEEDS,METHODS,BUDGET,POPULATION,EXPECTED_REAL_AC_UPPER_BOUND,
    HISTORICAL_I27_SEEDS,wilson_95,summarize,
)
from research.iteration27_real_scenario_credit_benchmark import (
    LOADS,PHYSICAL_SCENARIOS,CONTROL_BUS_GEN,
)


def artificial(seed,method,feasible):
    """Already paid fake summary only to validate paired arithmetic."""
    return {
        "method":method,"seed":seed,
        "all_three_original_source_feasible_batches":1 if feasible else 0,
        "true_real_ac_pf_calls":180,
        "complete_three_source_scenario_batches":60,
        "failed_real_ac_nr_calls":0,
        "best_all_three_feasible_mean_original_economic_cost":1. if feasible else None,
        "per_load_source_feasible_batch_counts":[int(feasible)]*3,
    }


class NewSeedReplicationProtocolTests(unittest.TestCase):
    def test_frozen_new_seed_set_unique_no_history_overlap(self):
        self.assertEqual(SEEDS,tuple(range(2040,2052)))
        self.assertEqual(len(SEEDS),12)
        self.assertEqual(len(set(SEEDS)),12)
        self.assertFalse(set(SEEDS)&set(HISTORICAL_I27_SEEDS))
        self.assertEqual(METHODS,
            ("gadapt_legacy","gadapt_ucb_objective",
             "gadapt_ucb_scalar_feasibility",
             "gadapt_ucb_scenario_feasibility"))
        self.assertEqual(len(METHODS)*len(SEEDS),48)
        self.assertEqual(BUDGET,180)
        self.assertEqual(EXPECTED_REAL_AC_UPPER_BOUND,8640)
        self.assertEqual(POPULATION,12)
        self.assertEqual(LOADS,(.98,1.0,1.02))
        self.assertEqual(PHYSICAL_SCENARIOS,3)
        self.assertEqual([bus for bus,_ in CONTROL_BUS_GEN],
            [103,32,34,92,19,74])

    def test_wilson_marginal_is_descriptive_not_paired_pvalue(self):
        self.assertEqual(wilson_95(0,12)[0],0.)
        self.assertAlmostEqual(wilson_95(12,12)[1],1.)
        self.assertLess(wilson_95(0,12)[1],.3)
        self.assertGreater(wilson_95(12,12)[0],.7)
        with self.assertRaises(ValueError):
            wilson_95(-1,12)
        with self.assertRaises(ValueError):
            wilson_95(13,12)

    def test_summary_accounts_all_four_methods_and_12_paired_seed_outcomes(self):
        rows=[]
        for s in SEEDS:
            for m in METHODS:
                success=((m=="gadapt_ucb_scenario_feasibility" and s%3==0)
                         or (m=="gadapt_legacy" and s%4==0))
                rows.append(artificial(s,m,success))
        result,paired=summarize(rows)
        self.assertEqual(result["gadapt_ucb_scenario_feasibility"][
            "runs_with_at_least_one_all_three_feasible"],4)
        self.assertEqual(result["gadapt_legacy"][
            "runs_with_at_least_one_all_three_feasible"],3)
        self.assertEqual(result["gadapt_ucb_objective"]["runs_with_at_least_one_all_three_feasible"],0)
        self.assertEqual(paired["gadapt_legacy"]["both_yes"],1)
        self.assertEqual(paired["gadapt_legacy"]["new_yes_control_no"],3)
        self.assertEqual(paired["gadapt_legacy"]["new_no_control_yes"],2)
        self.assertEqual(paired["gadapt_legacy"]["both_no"],6)

    def test_fail_closed_missing_pair_or_duplicate_record(self):
        rows=[artificial(s,m,False) for s in SEEDS for m in METHODS]
        with self.assertRaises(ValueError):
            summarize(rows[:-1])
        with self.assertRaises(ValueError):
            summarize(rows+[rows[0]])
        # duplicate identical tuple leads count mismatch despite dictionary replacing it
        with self.assertRaises(ValueError):
            summarize(rows+[artificial(2060,METHODS[0],False)])

if __name__=="__main__":
    unittest.main()
