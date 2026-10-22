"""Zero-source-network regression tests for I38 restricted temporal robust model.

These tiny diagrams are synthetic fixtures, NOT Nobel-Germany solver data.
"""
import unittest
import numpy as np

from research.iteration38_joint_capacity_model import (
    JointCapacityProblem, SourceLink, parse_network, parse_nodes, parse_demands,
    temporal_array, solve_milp,
)


NATIVE = """# Synthetic 3-node fixture, NOT SNDlib Nobel-Germany
NODES (
 A ( 0 0 )
 B ( 1 0 )
 C ( 1 1 )
)
LINKS (
 AB ( A B ) 0 0 0 0 ( 20 10 40 19 )
 BC ( B C ) 0 0 0 0 ( 20 10 40 19 )
 AC ( A C ) 0 0 0 0 ( 20 15 40 35 )
)
DEMANDS (
 DAC ( A C ) 1 12 UNLIMITED
)
"""
TMP1 = """NODES (
 A ( 0 0 )
 B ( 1 0 )
 C ( 1 1 )
)
DEMANDS (
 D_AC ( A C ) 1 8 UNLIMITED
 D_CA ( C A ) 1 4 UNLIMITED
)
"""
TMP2 = """NODES (
 A ( 0 0 )
 B ( 1 0 )
 C ( 1 1 )
)
DEMANDS (
 D_AC ( A C ) 1 12 UNLIMITED
)
"""


class I38JointPlanningSyntheticTests(unittest.TestCase):
    def _problem(self):
        nodes, links = parse_network(NATIVE)
        return JointCapacityProblem(nodes, links, (("A","C"),),
                                    np.array([[8.], [12.]]))

    def test_exact_one_common_module_and_two_routes(self):
        p = self._problem()
        self.assertEqual(p.n, 1)
        self.assertEqual(p.paths[0][0], ("A", "C"))
        self.assertEqual(p.paths[0][1], ("A", "B", "C"))
        direct = p.evaluate([0])
        detour = p.evaluate([1])
        self.assertTrue(direct["feasible"])
        self.assertEqual(direct["cost"], 15.)
        self.assertEqual(detour["cost"], 20.)
        self.assertEqual(direct["installed_capacity"], [0., 0., 20.])
        self.assertEqual(direct["selected_options"], [None, None, 0])
        self.assertFalse(p.validate_plan([0], direct["installed_capacity"],
                                         np.array([[23.] ]))["all_snapshots_feasible"])
        self.assertEqual(p.validate_plan([0], direct["installed_capacity"],
                                         np.array([[23.]]))["max_source_unit_excess"],3.)

    def test_exact_milp_matches_bruteforce_two_paths(self):
        p = self._problem()
        m = solve_milp(p, time_limit=15)
        self.assertEqual(m["status"],0, m["message"])
        self.assertEqual(m["incumbent"]["cost"],15.)
        self.assertAlmostEqual(m["solver_objective"],15.,places=5)
        self.assertAlmostEqual(m["dual_bound"],15.,places=4)
        self.assertTrue(m["incumbent"]["feasible"])
        self.assertEqual(m["incumbent"]["choices"],[0])

    def test_native_parser_no_unit_invention(self):
        nodes, links = parse_network(NATIVE)
        self.assertEqual(len(nodes),3)
        self.assertEqual(len(links),3)
        self.assertEqual(len(links[0].options),2)
        self.assertEqual(parse_demands(NATIVE,nodes)[("A","C")],12.)
        pairs,q=temporal_array([(str(i),v) for i,v in enumerate([TMP1,TMP2])]+
                               [(str(i),TMP1) for i in range(2,288)], nodes)
        self.assertEqual(len(pairs),2)
        self.assertEqual(q.shape,(288,2))
        j=pairs.index(("C","A"))
        self.assertEqual(q[1,j],0)
        self.assertEqual(q[0,j],4)

    def test_demand_and_installed_capacity_are_not_recourse(self):
        p=self._problem()
        cap=p.evaluate([0])["installed_capacity"]
        held=p.validate_plan([0],cap,np.array([[21.],[19.]]))
        self.assertEqual(held["violating_slices"],1)
        self.assertAlmostEqual(held["max_source_unit_excess"],1.)
        self.assertEqual(cap,[0.,0.,20.])

    def test_overloaded_model_detected_without_fabricated_hardware(self):
        nodes, links=parse_network(NATIVE)
        p=JointCapacityProblem(nodes,links,(("A","C"),),[[500.]])
        self.assertFalse(p.evaluate([0])["feasible"])
        self.assertFalse(p.evaluate([1])["feasible"])
        self.assertGreater(p.evaluate([0])["worst_excess"],0)

    def test_zero_or_bad_source_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            parse_network(NATIVE.replace("20 10 40 19","20 nan 40 19",1))
        with self.assertRaises(ValueError):
            parse_demands(NATIVE.replace("1 12 UNLIMITED","1 -12 UNLIMITED"),("A","B","C"))
        p=self._problem()
        with self.assertRaises(ValueError):
            p.evaluate([.2])
        with self.assertRaises(ValueError):
            p.validate_plan([0],[0,0,1],[[1,2]])


if __name__=="__main__":
    unittest.main()
