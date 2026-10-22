"""I39 source-cost algebra, MILP and joint-plan synthetic tests; NO real source solver."""
import unittest
import numpy as np
from research.iteration38_joint_capacity_model import SourceLink
from research.iteration39_source_modular_capacity import (
    ModularCommonPlan, exact_modular_milp,
    verify_exact_source_module_equivalence)


def modules(c20,c40):
    return tuple((float(20*k),float((k//2)*c40+(k%2)*c20))
                 for k in range(1,41))


def tiny(q):
    nodes=("A","B","C")
    links=(
        SourceLink("AB","A","B",0.,0.,0.,0.,modules(10.,16.)),
        SourceLink("BC","B","C",0.,0.,0.,0.,modules(10.,16.)),
        SourceLink("AC","A","C",0.,0.,0.,0.,modules(12.,18.)),
    )
    return ModularCommonPlan(nodes,links,(("A","C"),),np.asarray(q,dtype=float))


class I39SourceModularSyntheticTests(unittest.TestCase):
    def test_source_menu_is_exactly_two_unlimited_primitives(self):
        p=tiny([[21.],[55.]])
        self.assertEqual(len(p.module_prices),3)
        direct=p.evaluate([0])
        self.assertTrue(direct["feasible"])
        self.assertEqual(direct["cost"],30.) # 40 @18 plus 20 @12
        self.assertEqual(direct["modules_20"],[0,0,1])
        self.assertEqual(direct["modules_40"],[0,0,1])
        self.assertEqual(direct["installed_capacity"],[0.,0.,60.])
        self.assertEqual(p.evaluate([1])["cost"],52.) # AB and BC each 40+20
        self.assertTrue(p.validate_plan([0],direct["installed_capacity"],
                                        np.asarray([[59.]]))["all_snapshots_feasible"])
        self.assertFalse(p.validate_plan([0],direct["installed_capacity"],
                                         np.asarray([[61.]]))["all_snapshots_feasible"])

    def test_modular_model_removes_previous_800_per_link_dead_end(self):
        p=tiny([[1000.]])
        v=p.evaluate([0])
        self.assertTrue(v["feasible"])
        self.assertEqual(v["modules_40"],[0,0,25])
        self.assertEqual(v["cost"],450.)
        self.assertEqual(v["worst_excess"],0.)

    def test_milp_same_exact_modular_model_as_ga(self):
        p=tiny([[21.],[55.]])
        ans=exact_modular_milp(p,seconds=15)
        self.assertEqual(ans["status"],0,ans["message"])
        self.assertEqual(ans["incumbent"]["choices"],[0])
        self.assertAlmostEqual(ans["incumbent"]["cost"],30.)
        self.assertAlmostEqual(ans["solver_objective"],30.)
        self.assertAlmostEqual(ans["dual_bound"],30.)

    def test_menu_decomposition_fails_closed_on_source_drift(self):
        p=tiny([[30.]])
        old=p.links[-1]
        wrong=tuple((cap, price+1 if cap==80 else price)
                    for cap,price in old.options)
        changed=SourceLink(old.name,old.u,old.v,0.,0.,0.,0.,wrong)
        with self.assertRaises(ValueError):
            verify_exact_source_module_equivalence(list(p.links[:-1])+[changed])
        changed_setup=SourceLink(old.name,old.u,old.v,0.,0.,0.,17.,old.options)
        with self.assertRaises(ValueError):
            verify_exact_source_module_equivalence(list(p.links[:-1])+[changed_setup])


if __name__=="__main__":
    unittest.main()
