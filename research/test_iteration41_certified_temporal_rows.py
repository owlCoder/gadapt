"""I41 no-domain, no-official-source exhaustive exactness and adversarial tests.

All traffic here is synthetic explicitly, never NVIDIA/DFN/I39 source data.
"""
import copy
import itertools
import unittest
from fractions import Fraction
import numpy as np

from research.test_iteration39_source_modular_capacity import tiny
from research.iteration39_source_modular_capacity import (
    ModularCommonPlan, exact_modular_milp,
)
from research.iteration41_certified_temporal_rows import (
    certified_route_aware_rows, verify_certified_rows, _dominance_margin,
    _physical_masks, _binary64_exact_integer_matrix,
)


class I41SafeRoutingConstraintPruning(unittest.TestCase):
    def test_strictly_rising_128_time_frames_remove_99_percent_safely(self):
        q=np.arange(1,129,dtype=float).reshape(-1,1)
        p=tiny(q)
        certificate=certified_route_aware_rows(p)
        self.assertEqual(certificate["original_rows"],3*128)
        self.assertEqual(certificate["kept_rows"],3)
        self.assertEqual(certificate["removed_rows"],3*127)
        self.assertTrue(verify_certified_rows(p,certificate))
        for x in certificate["edge_time_rows"]:
            self.assertEqual(x["kept_times"],[127])
        for z in (0,1):
            loads=p.base+p.q@(p.delta*np.array([z])[:,None])
            peaks=loads.max(axis=0)
            retained=np.array([
                loads[row["kept_times"],e].max()
                for e,row in enumerate(certificate["edge_time_rows"])])
            np.testing.assert_allclose(peaks,retained,atol=0,rtol=0)

    def test_same_total_traffic_opposite_demand_must_NOT_drop_each_others_rows(self):
        p0=tiny([[1.]])
        q=np.array([[10.,0.],[0.,10.]],dtype=float)
        p=ModularCommonPlan(p0.nodes,p0.links,
             (("A","C"),("C","A")),q)
        cert=certified_route_aware_rows(p)
        for e,item in enumerate(cert["edge_time_rows"]):
            self.assertEqual(item["kept_times"],[0,1])
            self.assertFalse(item["removed"])
        self.assertEqual(cert["removed_rows"],0)

    def test_near_tied_source_values_keep_uncertain_rows(self):
        q=np.array([[5.],[5.+1e-14]],dtype=float)
        p=tiny(q)
        cert=certified_route_aware_rows(p)
        # Here larger traffic safely weakly dominates smaller directly
        # because the source amounts satisfy componentwise inequality;
        # conservatism applies to cancellation cases.
        self.assertEqual(cert["kept_rows"],3)
        self.assertTrue(verify_certified_rows(p,cert))
        close=np.array([[5.,5.],[5.+1e-14,5.-1e-14]],dtype=float)
        p2=ModularCommonPlan(p.nodes,p.links,(("A","C"),("C","A")),close)
        c2=certified_route_aware_rows(p2)
        self.assertEqual(c2["kept_rows"],6)

    def test_every_original_constraint_equal_for_all_binary_routes(self):
        p0=tiny([[1.]])
        traffic=np.array([[10.,5.],[8.,6.],[10.,5.],
                          [12.,9.],[4.,8.],[9.,7.]],dtype=float)
        p=ModularCommonPlan(p0.nodes,p0.links,
                            (("A","C"),("C","A")),traffic)
        cert=certified_route_aware_rows(p)
        self.assertGreater(cert["removed_rows"],0)
        for choice in itertools.product((0,1),repeat=p.n):
            z=np.array(choice)
            loads=p.base+p.q @ (p.delta*z[:,None])
            full=np.max(loads,axis=0)
            kept=np.asarray([np.max(loads[entry["kept_times"],e])
                for e,entry in enumerate(cert["edge_time_rows"])])
            np.testing.assert_allclose(kept,full,atol=1e-12,rtol=0)
            # No change to the exact module cost or installed physical plan.
            original=p.evaluate(z)
            self.assertEqual(original["cost"],
              sum(np.asarray(original["modules_20"])*[10,10,12])+
              sum(np.asarray(original["modules_40"])*[16,16,18]))

    def test_M_formula_equals_bruteforce_min_route_difference(self):
        p0=tiny([[1.]])
        p=ModularCommonPlan(p0.nodes,p0.links,
            (("A","C"),("C","A")),
            np.array([[7.,9.],[10.,5.],[13.,8.]],dtype=float))
        for e in range(len(p.links)):
            both,xor=_physical_masks(p,e)
            for s,t in itertools.product(range(len(p.q)),repeat=2):
                val,_,_= _dominance_margin(p.q,both,xor,s,t)
                actual=min(
                    float(np.sum((p.q[s]-p.q[t]) *
                                 (p.incidence[z,pairs, e])))
                    for pairs in [np.arange(p.n)]
                    for z in itertools.product((0,1),repeat=p.n)
                ) if False else None
                # Explicit independent load enumeration with one route per demand.
                actual=min(float(np.sum((p.q[s]-p.q[t]) *
                      np.array([p.incidence[z[d],d,e] for d in range(p.n)])))
                      for z in itertools.product((0,1),repeat=p.n))
                self.assertAlmostEqual(val,actual,places=10)

    def test_certificate_tampering_is_fail_closed_and_rejected_by_MILP(self):
        p=tiny(np.arange(1,21,dtype=float).reshape(-1,1))
        cert=certified_route_aware_rows(p)
        forged=copy.deepcopy(cert)
        forged["edge_time_rows"][0]["removed"][0]["dominated_by"]=0
        if forged["edge_time_rows"][0]["removed"][0]["time"]==0:
            forged["edge_time_rows"][0]["removed"][0]["dominated_by"]=0
        with self.assertRaises(ValueError):
            verify_certified_rows(p,forged)
        with self.assertRaises(ValueError):
            exact_modular_milp(p,seconds=10,certified_rows=forged)
        partial=copy.deepcopy(cert)
        partial["edge_time_rows"][0]["removed"].pop()
        with self.assertRaises(ValueError):
            verify_certified_rows(p,partial)

    def test_exact_binary64_arithmetic_catches_decimal_rounding(self):
        vals=np.array([[0.1,0.2,0.3],[1e-12,1e12,0.]],dtype=float)
        q=_binary64_exact_integer_matrix(vals)
        ratios=[float(v).as_integer_ratio() for v in vals.flat]
        exponent=max(x[1].bit_length()-1 for x in ratios)
        denom=1<<exponent
        for i in range(vals.shape[0]):
            for j in range(vals.shape[1]):
                self.assertEqual(Fraction(int(q[i,j]),denom),
                                 Fraction.from_float(float(vals[i,j])))
        self.assertGreater(q[0,0]+q[0,1]-q[0,2],0)
        with self.assertRaises(ValueError):
            _binary64_exact_integer_matrix([[float("nan")]])

    def test_same_global_MILP_lower_bound_and_exact_source_cost(self):
        p=tiny(np.arange(1,41,dtype=float).reshape(-1,1))
        cert=certified_route_aware_rows(p)
        full=exact_modular_milp(p,seconds=15)
        reduced=exact_modular_milp(p,seconds=15,certified_rows=cert)
        self.assertEqual(full["status"],0,full["message"])
        self.assertEqual(reduced["status"],0,reduced["message"])
        self.assertEqual(full["source_capacity_constraints"],120)
        self.assertEqual(reduced["source_capacity_constraints"],3)
        self.assertEqual(reduced["certified_rows_removed"],117)
        self.assertAlmostEqual(full["incumbent"]["cost"],
                               reduced["incumbent"]["cost"],places=7)
        self.assertAlmostEqual(full["dual_bound"],reduced["dual_bound"],places=7)
        self.assertEqual(p.evaluate(reduced["incumbent"]["choices"])["cost"],
                         reduced["incumbent"]["cost"])
        # Default existing I39 results metadata remains unchanged.
        self.assertNotIn("certified_rows_removed",full)


if __name__=="__main__":
    unittest.main()
