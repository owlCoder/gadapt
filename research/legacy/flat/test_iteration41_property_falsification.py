"""I41 property-based falsification (Hypothesis), synthetic data only.

Tries to REFUTE the I41 theorem on many random tiny instances by brute force
over every binary route vector z in {0,1}^D. No SNDlib/DFN data, no solver.
"""
import itertools
import unittest
from fractions import Fraction
from types import SimpleNamespace

import numpy as np
from hypothesis import given, settings, strategies as st, HealthCheck

from research.iteration41_certified_temporal_rows import (
    certified_route_aware_rows, _physical_masks,
)


def _problem(q, incidence):
    q = np.asarray(q, dtype=float)
    return SimpleNamespace(q=q, n=q.shape[1], links=[None]*incidence.shape[2],
                           incidence=incidence)


def _loads(q, incidence, z):
    # L[t,e] = sum_d q[t,d] * a[z_d, d, e]
    a = incidence[np.asarray(z), np.arange(len(z)), :]
    return q @ a


@st.composite
def instances(draw):
    d = draw(st.integers(1, 5))
    e = draw(st.integers(1, 3))
    t = draw(st.integers(1, 7))
    # Small integer-valued traffic gives many exact ties and dominations.
    value = st.one_of(st.integers(0, 6).map(float),
                      st.floats(0, 10, allow_nan=False, allow_infinity=False))
    q = np.array([[draw(value) for _ in range(d)] for _ in range(t)])
    inc = np.array(draw(st.lists(st.integers(0, 1), min_size=2*d*e,
                                 max_size=2*d*e))).reshape(2, d, e)
    return q, inc


class I41PropertyFalsification(unittest.TestCase):
    @settings(max_examples=1500, deadline=None,
              suppress_health_check=[HealthCheck.too_slow])
    @given(instances())
    def test_kept_rows_preserve_every_edge_peak_for_every_route_vector(self, inst):
        q, inc = inst
        cert = certified_route_aware_rows(_problem(q, inc))
        for z in itertools.product((0, 1), repeat=q.shape[1]):
            loads = _loads(q, inc, z)
            for e, row in enumerate(cert["edge_time_rows"]):
                self.assertEqual(loads[:, e].max(),
                                 loads[row["kept_times"], e].max())

    @settings(max_examples=800, deadline=None)
    @given(instances())
    def test_separable_formula_equals_bruteforce_min_in_exact_arithmetic(self, inst):
        q, inc = inst
        qf = [[Fraction(v) for v in r] for r in q]
        p = _problem(q, inc)
        n_d, n_t = q.shape[1], q.shape[0]
        for e in range(inc.shape[2]):
            both, xor = _physical_masks(p, e)
            for s in range(n_t):
                for t in range(n_t):
                    diff = [qf[s][d]-qf[t][d] for d in range(n_d)]
                    formula = (sum((diff[d] for d in range(n_d) if both[d]), Fraction(0))
                               + sum((min(Fraction(0), diff[d])
                                      for d in range(n_d) if xor[d]), Fraction(0)))
                    brute = min(sum(diff[d]*int(inc[z[d], d, e]) for d in range(n_d))
                                for z in itertools.product((0, 1), repeat=n_d))
                    self.assertEqual(formula, brute)

    def test_pairwise_certificate_is_sufficient_but_not_complete(self):
        """Row t=(5,5) is implied by the MAX of rows s1=(10,0), s2=(0,10)
        for every z, yet neither single row implies it (M=-5). I41 keeps it:
        safe, but not the minimal exact row set. Exact joint redundancy is a
        different (in general NP-hard) test."""
        q = np.array([[10., 0.], [0., 10.], [5., 5.]])
        inc = np.zeros((2, 2, 1), dtype=int)
        inc[0, :, 0] = 1  # route 0 uses the edge, route 1 avoids it
        cert = certified_route_aware_rows(_problem(q, inc))
        self.assertEqual(cert["edge_time_rows"][0]["kept_times"], [0, 1, 2])
        for z in itertools.product((0, 1), repeat=2):
            loads = _loads(q, inc, z)[:, 0]
            self.assertLessEqual(loads[2], max(loads[0], loads[1]))


if __name__ == "__main__":
    unittest.main()
