#!/usr/bin/env python3
"""Independent finite audits of adaptive flow and local-exponent induction.

The oracle convolves ordered target/paid words, rather than enumerating target
multiindices or using Pascal demands. Exact mirror windows reconstruct the
whole invoice. Floating checks below are regression controls, not certificates.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from math import exp, fsum, log
import unittest

from flow import Flow


def words(histogram, length):
    result = Counter({1: 1})
    for _ in range(length):
        following = Counter()
        for x, count in result.items():
            for r, multiplicity in histogram.items():
                following[x*r] += count*multiplicity
        result = following
    return result


def mirror_oracle(targets, paid, n, height):
    """Reconstruct all invoice components from ordered-word window formulas."""
    cap = n//max(targets)
    root, inner, boundary, leaves, units = (Counter() for _ in range(5))
    for col, count in words(targets, height).items():
        if col <= cap:
            for k, multiplicity in targets.items():
                root[k*col] += count*multiplicity
    for depth in range(height+1):
        for rho, paths in words(paid, depth).items():
            for col, count in words(targets, height-depth).items():
                if rho*col <= cap:
                    units[rho*col] += paths*count
            if depth == height:
                if rho <= cap:
                    for r, multiplicity in paid.items():
                        leaves[r*rho] += paths*multiplicity
                continue
            for col, count in words(targets, height-depth-1).items():
                z = rho*col
                for r, pr in paid.items():
                    for k, wk in targets.items():
                        rank, mass = r*k*z, paths*count*pr*wk
                        if k*z <= cap < r*z:
                            boundary[rank] += mass
                        if r*z <= cap < k*z:
                            inner[rank] += mass
    return dict(root_sources=root, nonroot_sources=inner,
                boundary_exits=boundary, leaf_exits=leaves,
                sources=root+inner, exits=boundary+leaves, unit_columns=units)


class IndependentFlowAudit(unittest.TestCase):
    def test_ordered_word_mirror_reconstruction(self):
        targets, paid = {2: 2, 5: 1}, {1: 1, 3: 1}
        saw_empty_root = saw_small_root = False
        for n in (5, 10, 27, 61):
            for height in range(6):
                with self.subTest(n=n, height=height):
                    expected = mirror_oracle(targets, paid, n, height)
                    actual = Flow(targets, paid, n, height).merged()
                    for key, value in expected.items():
                        self.assertEqual(dict(actual[key]), dict(value), key)
                    # Exact formal cancellation at every individual rank.
                    balance = Counter(expected['sources'])
                    balance.subtract(expected['exits'])
                    for col, count in expected['unit_columns'].items():
                        for k, wk in targets.items():
                            balance[k*col] -= count*wk
                        for r, pr in paid.items():
                            balance[r*col] += count*pr
                    self.assertTrue(all(value == 0 for value in balance.values()))
                    self.assertTrue(all(max(targets)*s > n
                                        for s in expected['nonroot_sources']))
                    saw_empty_root |= not expected['root_sources']
                    saw_small_root |= any(max(targets)*s <= n
                                          for s in expected['root_sources'])
        self.assertTrue(saw_empty_root, 'exercise a forest with no root units')
        self.assertTrue(saw_small_root, 'old root source lower bound must fail')

    def test_small_roots_cannot_use_inner_capacity(self):
        invoice = mirror_oracle({2: 2, 5: 1}, {1: 1, 3: 1}, 61, 0)
        self.assertEqual(invoice['root_sources'], Counter({2: 2, 5: 1}))
        self.assertFalse(invoice['nonroot_sources'])
        self.assertTrue(all(s <= Q(61, 5) for s in invoice['root_sources']))


class IndependentInductionAudit(unittest.TestCase):
    def test_sharp_source_boundary_threshold_and_failure_below_it(self):
        for beta in (Q(0), Q(1, 3), Q(3, 4)):
            eta = beta+(1-beta)/2
            threshold = (1-eta)/(eta-beta)
            for factor in (Q(1, 2), Q(1), Q(2)):
                excess, leaves = threshold*factor, Q(1)
                # Saturate the permitted boundary share, independently of flow.
                inner = (leaves+excess)/(1-beta)
                boundary = beta*inner
                self.assertEqual(inner, boundary+leaves+excess)
                self.assertEqual((boundary+leaves <= eta*inner), factor >= 1)

    def test_local_exponent_domain_regression(self):
        t0, power, shift = .99731352, .1, 38.
        log_n0 = log(121)+100*log(256)
        tau_max = t0+power/(shift+log_n0)
        # The initially proposed upper endpoint was a genuine failed guard.
        self.assertGreater(tau_max, .9974808)
        self.assertLess(tau_max, .997481)
        self.assertGreaterEqual(shift*(1-t0), power)
        for log_n in (0., 1., log(121), log_n0, 1.e6):
            tau = t0+power/(shift+log_n)
            self.assertLessEqual(tau, 1.)
            curvature = tau*(tau-1)-power/(shift+log_n)**2
            self.assertLess(curvature, 0.)
            for fraction in (0., .01, .5, .99, 1.):
                log_e = fraction*log_n
                actual = t0*(log_e-log_n)+power*log((shift+log_e)/(shift+log_n))
                tangent = tau*(log_e-log_n)
                self.assertLessEqual(actual, tangent+1.e-9)

    def test_raw_superpotential_rejects_below_root_mutant(self):
        targets = {5:420, 6:270, 7:840, 8:1395, 9:3195,
                   25:448, 41:448, 57:448, 121:224}
        paid = {1:37305, 2:10695, 3:3360, 4:1530, 5:300,
                8:1464, 16:448, 32:448, 48:448}
        def ratio(t):
            return (fsum(count*exp(t*log(k)) for k,count in targets.items()) /
                    fsum(count*exp(t*log(k)) for k,count in paid.items()))
        self.assertGreater(ratio(.99731352), 1.)
        self.assertLess(ratio(.99731252), 1.)


if __name__ == '__main__':
    unittest.main(verbosity=2)
