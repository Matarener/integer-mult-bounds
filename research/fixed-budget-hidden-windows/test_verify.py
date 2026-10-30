"""Mathematical regression and rejection tests; Python 3.10+ stdlib."""
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import copy
import json
import unittest
from unittest.mock import patch

import verify as v


class BudgetWidthTests(unittest.TestCase):
    def setUp(self):
        self.pa, self.pb = v.build(1, 6, -17, 12)  # n=3, roots 4/3 and 3/2

    def test_source_example(self):
        pa, pb = v.build(1, 8, -22, 15)
        self.assertEqual(pa, [0, 89, 0, 46, 0])
        self.assertEqual(pb, [30, 0, 97, 0, 8])
        cert = v.certify(1, pa, pb, 135)
        self.assertEqual(cert['discriminant'], 4)
        self.assertEqual(cert['rank_mass_per_profile'], 546)

    def test_common_paid_padding_is_counted(self):
        pa = [x + 7 for x in self.pa]
        pb = [x + 7 for x in self.pb]
        cert = v.certify(1, pa, pb, 140)
        self.assertEqual(cert['common_calls'], 35)
        self.assertEqual(cert['uncancelled_calls_per_profile'], 105)
        self.assertEqual(cert['actual_calls_per_profile'], 140)
        with self.assertRaises(v.Rejected):
            v.certify(1, pa, pb, 139)

    def test_budget_is_per_profile(self):
        cert = v.certify(1, self.pa, self.pb, 105)
        self.assertEqual(cert['actual_calls_per_profile'], 105)
        self.assertEqual(sum(self.pa) + sum(self.pb), 210)
        with self.assertRaises(v.Rejected):
            v.certify(1, self.pa, self.pb, 104)

    def test_reversed_losing_orientation_rejected(self):
        with self.assertRaises(v.Rejected):
            v.certify(1, self.pb, self.pa, 105)

    def test_noninteger_and_negative_counts_rejected(self):
        for bad in (True, False, 0.0, F(0), -1):
            with self.subTest(bad=bad):
                pa = self.pa[:]
                pa[0] = bad
                with self.assertRaises(v.Rejected):
                    v.certify(1, pa, self.pb, 1000)

    def test_noninteger_h_and_budget_rejected(self):
        for bad in (True, 1.0, F(1)):
            with self.assertRaises(v.Rejected):
                v.certify(bad, self.pa, self.pb, 105)
            with self.assertRaises(v.Rejected):
                v.certify(1, self.pa, self.pb, bad)

    def test_missing_count_conservation_rejected(self):
        pa = self.pa[:]
        pa[0] += 1
        with self.assertRaisesRegex(v.Rejected, 'count'):
            v.certify(1, pa, self.pb, 1000)

    def test_missing_rank_mass_conservation_rejected(self):
        pa = self.pa[:]
        pa[1] -= 1
        pa[0] += 1
        with self.assertRaisesRegex(v.Rejected, 'mass'):
            v.certify(1, pa, self.pb, 1000)

    def test_extra_rank_even_common_padding_rejected(self):
        with self.assertRaisesRegex(v.Rejected, 'alphabet'):
            v.certify(1, self.pa + [1], self.pb + [1], 106)

    def test_repeated_root_rejected(self):
        pa, pb = v.build(1, 4, -12, 9)
        with self.assertRaisesRegex(v.Rejected, 'distinct'):
            v.certify(1, pa, pb, 1000)

    def test_complex_roots_rejected(self):
        pa, pb = v.build(1, 1, -3, 3)
        with self.assertRaisesRegex(v.Rejected, 'distinct'):
            v.certify(1, pa, pb, 1000)

    def test_endpoint_and_exterior_roots_rejected(self):
        # (1,3/2), (3/2,2), (1/2,3/2), and (2,3).
        for a, b, c in ((2, -5, 3), (2, -7, 6), (4, -8, 3), (1, -5, 6)):
            pa, pb = v.build(1, a, b, c)
            with self.subTest(quadratic=(a, b, c)):
                with self.assertRaises(v.Rejected):
                    v.certify(1, pa, pb, 1000)

    def test_false_endpoint_multiplicity_rejected(self):
        # Add a pair of roots elsewhere, retaining degree but not h=2 endpoints.
        q = [b - a for a, b in zip(self.pa, self.pb)]
        q = v.multiply(q, [12, -7, 1])
        pa, pb = [max(-x, 0) for x in q], [max(x, 0) for x in q]
        with self.assertRaisesRegex(v.Rejected, 'multiplicity'):
            v.certify(2, pa, pb, 100000)

    def test_zero_difference_rejected(self):
        with self.assertRaisesRegex(v.Rejected, 'saturated'):
            v.certify(1, self.pa, self.pa, 105)

    def test_irrational_pair_accepted_and_enclosed(self):
        pa, pb = v.build(1, 5, -15, 11)
        cert = v.certify(1, pa, pb, 93)
        self.assertFalse(cert['rational_roots'])
        self.assertEqual(cert['discriminant'], 5)
        out = v.interval_check(cert)
        lo, hi = F(out['normalized_ratio_lower']), F(out['normalized_ratio_upper'])
        self.assertGreater(lo * lo, 5)
        self.assertGreater(hi, lo)

    def test_integer_scaling_and_common_padding(self):
        pa, pb = [7*x + 3 for x in self.pa], [7*x + 3 for x in self.pb]
        cert = v.certify(1, pa, pb, 750)
        self.assertEqual(cert['discriminant'], 49)
        self.assertEqual(cert['uncancelled_calls_per_profile'], 735)
        self.assertEqual(cert['common_calls'], 15)
        v.interval_check(cert)

    def test_finite_budget_sharpness_is_not_claimed(self):
        pa, pb = v.build(1, 6, -19, 15)
        better = v.certify(1, pa, pb, 120)
        family = v.certify(1, self.pa, self.pb, 120)
        better_ratio = v.ratio_bounds(better)
        family_ratio = v.ratio_bounds(family)
        self.assertEqual(better_ratio, (F(10, 9), F(10, 9)))
        self.assertEqual(family_ratio, (F(9, 8), F(9, 8)))
        self.assertLess(better_ratio[1], family_ratio[0])

    def test_discrete_budget_bound_exact_attainment(self):
        for h in (1, 2, 8, 32):
            for n in (3, 10, 10000):
                pa, pb = v.build(h, n*(n-1), 1-2*n*n, n*(n+1))
                budget = 6**h*(4*n*n-1)//2
                cert = v.certify(h, pa, pb, budget)
                self.assertTrue(cert['discrete_bound_attained'])
                self.assertEqual(cert['endpoint_residual_value'], 1)
                self.assertEqual(F(cert['discrete_width_ratio_lower']), F(n*n, n*n-1))

    def test_discrete_bound_not_always_attained(self):
        pa, pb = v.build(1, 72, -161, 90)
        cert = v.certify(1, pa, pb, 1000)
        self.assertFalse(cert['discrete_bound_attained'])
        self.assertEqual(cert['budget_trace_cap'], 166)
        self.assertEqual(v.ratio_bounds(cert), (F(81, 80), F(81, 80)))
        self.assertLess(F(cert['discrete_width_ratio_lower']), F(81, 80))

    def test_census_against_independent_coefficient_simplex(self):
        # Enumerate the whole positive (a,-b,c) simplex allowed by W=3*(a-b+c),
        # not the optimized root-derived a and c ranges in enumerate_quadratics.
        for budget in (90, 135, 180):
            total = budget // 3
            brute = set()
            for a in range(1, total):
                for z in range(1, total - a):
                    for c in range(1, total - a - z + 1):
                        delta = z*z - 4*a*c
                        # Compare the radical with distance from vertex to each
                        # boundary; equivalent inequalities, independently arranged.
                        left, right = z - 2*a, 4*a - z
                        if delta > 0 and left > 0 and right > 0 and left*left > delta and right*right > delta:
                            brute.add((a, -z, c))
            self.assertEqual(brute, set(v.enumerate_quadratics(budget)))

    def test_sqrt_bounds_exact_square_and_nonsquare(self):
        for n in range(200):
            lo, hi = v.sqrt_bounds(n, bits=12)
            self.assertLessEqual(lo*lo, n)
            self.assertGreaterEqual(hi*hi, n)
            self.assertLessEqual(hi-lo, F(1, 4096))
            self.assertEqual(lo == hi, isqrt(n)**2 == n)

    def test_log_positive_series_nested_bounds(self):
        for x in (F(1), F(11, 10), F(3, 2), F(2)):
            prev = v.log_bounds(x, 1)
            for terms in (2, 4, 8, 16):
                now = v.log_bounds(x, terms)
                self.assertGreaterEqual(now[0], prev[0])
                self.assertLessEqual(now[1], prev[1])
                prev = now
        self.assertEqual(v.log_bounds(F(1)), (0, 0))

    def test_log_outside_domain_rejected(self):
        for x in (0, F(1, 2), 3, 1.0, True):
            with self.assertRaises(v.Rejected):
                v.log_bounds(x)

    def test_endpoint_window_outside_class_rejected(self):
        # Reviewer's counterexample to dropping the two-interior-crossing premise.
        q = [-22, 31, 12, -31, 10]
        pa, pb = [max(-x, 0) for x in q], [max(x, 0) for x in q]
        with self.assertRaises(v.Rejected):
            v.certify(1, pa, pb, 53)

    def test_source_manifest_metadata_mutations_rejected(self):
        root = Path(v.__file__).resolve().parent
        original = json.loads((root / 'SOURCES.json').read_text())
        read = Path.read_bytes
        for where, key, bad in ((None, 'source_pr', 1), (None, 'source_commit', '0'*40),
                                (0, 'commit', '0'*40), (0, 'upstream_path', 'wrong/path'),
                                (0, 'url', 'https://example.invalid/')):
            changed = copy.deepcopy(original)
            (changed if where is None else changed['files'][where])[key] = bad
            replacement = (json.dumps(changed, indent=2)+'\n').encode()
            def read_mutation(path):
                return replacement if path.name == 'SOURCES.json' else read(path)
            with patch.object(Path, 'read_bytes', new=read_mutation):
                with self.assertRaisesRegex(v.Rejected, 'provenance manifest'):
                    v.source_check()

    def test_source_export_mutation_rejected(self):
        read = Path.read_bytes
        for filename in ('pr6049-README.md.txt', 'pr6049-verify.py.txt'):
            def read_mutation(path):
                data = read(path)
                return data + b'changed\n' if path.name == filename else data
            with patch.object(Path, 'read_bytes', new=read_mutation):
                with self.assertRaisesRegex(v.Rejected, 'source SHA256'):
                    v.source_check()


if __name__ == '__main__':
    unittest.main()
