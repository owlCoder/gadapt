"""Fast controller-level checks, real solver budget checks separately in CI."""
import math
import unittest
from research.ieee118_allocation import AllocationSwitch, PhysicalGridRecorder, BudgetExhausted


class FakeRecord:
    def __init__(self, feasible, checkpoint, calls=46):
        self.budget=180
        self.calls=calls
        self.stage_cap=180
        self.best_feasible=feasible
        self.checkpoint_best_feasible=checkpoint
        self.probe_count=45


class FakeGrid:
    def __init__(self):
        self.calls=0
    def evaluate(self, x):
        self.calls+=1
        return dict(objective=sum(t*t for t in x),solver_failed=False,
                    feasible=True,loss=sum(t*t for t in x),violation=0.0)


class AdaptivePolicyTests(unittest.TestCase):
    def test_no_feasible_gives_more_ga_budget(self):
        r=FakeRecord(math.inf,None)
        p=AllocationSwitch(r,"adaptive")
        self.assertFalse(p.check())
        self.assertEqual(p.decision,"infeasible_explore")
        self.assertEqual(r.stage_cap,135)
        r.calls=135
        self.assertTrue(p.check())

    def test_stalled_feasible_reserves_local_budget(self):
        r=FakeRecord(120.,120.)
        p=AllocationSwitch(r,"adaptive")
        self.assertFalse(p.check())
        self.assertEqual(p.decision,"feasible_stalled")
        self.assertEqual(r.stage_cap,54)
        r.calls=54
        self.assertTrue(p.check())

    def test_progressing_feasible_keeps_ga_longer(self):
        r=FakeRecord(110.,120.)
        p=AllocationSwitch(r,"adaptive")
        self.assertFalse(p.check())
        self.assertEqual(p.decision,"feasible_improving")
        self.assertEqual(r.stage_cap,99)
        self.assertGreater(p.progress,.002)

    def test_fixed_and_legacy_fraction(self):
        r=FakeRecord(120.,120.)
        self.assertEqual(AllocationSwitch(r,"fixed").target,90)
        r=FakeRecord(120.,120.)
        self.assertEqual(AllocationSwitch(r,"legacy").target,180)

    def test_true_calls_only_never_credit_rejected(self):
        grid=FakeGrid()
        recorder=PhysicalGridRecorder(grid,3)
        recorder.stage_cap=2
        self.assertEqual(recorder([1.,2.]),5.)
        self.assertEqual(recorder([0.,1.]),1.)
        self.assertEqual(recorder([0.,0.]),1e12)
        self.assertEqual(recorder.calls,2)
        self.assertEqual(grid.calls,2)
        self.assertEqual(recorder.best_feasible,1.)
        with self.assertRaises(BudgetExhausted):
            recorder.strict([0.,0.])
        recorder.stage_cap=3
        self.assertEqual(recorder.strict([.5,.5]),.5)
        self.assertEqual(grid.calls,3)
        self.assertEqual(recorder.best_feasible,.5)
        self.assertEqual(recorder.requests,5)


if __name__=="__main__":
    unittest.main()
