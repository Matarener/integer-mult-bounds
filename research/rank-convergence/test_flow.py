#!/usr/bin/env python3
"""Finite correctness controls for the changed height and exact invoice."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from flow import Flow, SOURCE, adaptive_flow, load_source, verify_receipt


class HeightFlowTests(unittest.TestCase):
    def test_integer_adaptive_height_boundaries(self):
        targets, paid = {2: 1, 5: 1}, {1: 2, 4: 1}
        witness = {'height_base': 4, 'a': 1, 'b': 1}
        for n, expected in ((19, 0), (20, 2), (79, 2), (80, 4)):
            changed = adaptive_flow(targets, paid, n, witness)
            self.assertEqual(changed.G, expected)
            self.assertEqual(changed.adaptive_geometry['ell'], expected//2)
            self.assertTrue(changed.merged()['sources'])

    def test_eighty_literal_fixtures(self):
        fixtures = [({2: 1, 3: 1}, {1: 1, 2: 1}),
                    ({2: 2, 4: 1}, {1: 2, 3: 1}),
                    ({2: 1, 3: 2}, {1: 2, 2: 1}),
                    ({3: 1, 5: 1}, {1: 1, 4: 1})]
        count = above_old = empty_roots = 0
        for targets, paid in fixtures:
            for factor in (1, 2, 5, 11):
                n = factor*max(targets)
                old_height, least = 0, 1
                while least*min(targets) <= n//max(targets):
                    old_height += 1
                    least *= min(targets)
                for height in range(5):
                    with self.subTest(targets=targets, paid=paid, n=n, G=height):
                        f = Flow(targets, paid, n, height)
                        receipt = f.merged()
                        paid_word = [r for r, w in paid.items() for _ in range(w)]
                        literal = f.literal(paid_word, class_limit=100000)
                        self.assertEqual(receipt['sources'], literal['sources'])
                        self.assertEqual(receipt['exits'], literal['exits'])
                        self.assertTrue(verify_receipt(targets, paid, n, receipt))
                        above_old += height > old_height
                        empty_roots += not receipt['root_sources']
                        count += 1
        self.assertEqual(count, 80)
        self.assertEqual(above_old, 43)
        self.assertGreater(empty_roots, 0)

    def test_small_roots_are_not_subject_to_inner_bound(self):
        f = Flow({2: 1, 3: 1}, {1: 1, 2: 1}, 6, 0)
        receipt = f.merged()
        self.assertIn(2, receipt['root_sources'])
        self.assertFalse(f.n < f.m*2)
        self.assertFalse(receipt['nonroot_sources'])

    def test_empty_root_forest_with_paid_rank_one(self):
        f = Flow({2: 1, 3: 1}, {1: 1, 2: 1}, 3, 4)
        receipt = f.merged()
        self.assertFalse(receipt['root_sources'])
        self.assertTrue(receipt['nonroot_sources'])
        self.assertEqual(receipt['sources'], f.literal([1, 2])['sources'])
        self.assertTrue(all(e < 3 for e in receipt['exits']))

    def test_generic_empty_flow_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Empty arbitrary-height flow'):
            Flow({2: 1, 4: 1}, {2: 1}, 4, 3).merged()

    def test_formal_invoice_rejects_false_rank(self):
        f = Flow({2: 1, 3: 1}, {1: 1, 2: 1}, 15, 2)
        bad = deepcopy(f.merged())
        rank = next(iter(bad['unit_columns']))
        bad['unit_columns'][rank] += 1
        with self.assertRaisesRegex(ValueError, 'Formal rank-invoice cancellation'):
            verify_receipt(f.T, f.P, f.n, bad)

    def test_classification_rejects_false_root_credit(self):
        f = Flow({2: 1, 3: 1}, {1: 1, 2: 1}, 6, 0)
        bad = deepcopy(f.merged())
        bad['root_sources'][2] -= 1
        del bad['root_sources'][2]
        bad['nonroot_sources'][2] += 1
        with self.assertRaisesRegex(ValueError, 'Nonroot source lower bound'):
            verify_receipt(f.T, f.P, f.n, bad)

    def test_source_authentication_precedes_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'untrusted.py'
            path.write_bytes(SOURCE.read_bytes()+b'\nraise RuntimeError("executed")\n')
            with self.assertRaisesRegex(ValueError, 'Changed predecessor flow bytes'):
                load_source(path)


if __name__ == '__main__':
    unittest.main()
