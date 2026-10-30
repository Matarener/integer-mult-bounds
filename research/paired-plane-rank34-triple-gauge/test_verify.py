#!/usr/bin/env python3
"""Focused controls for the exact three-channel gauge census."""
import unittest

import verify


class TripleGaugeTests(unittest.TestCase):
    def test_signed_ternary_matrix_and_support_map_census(self):
        maps, count = verify.enumerate_gauge_maps()
        self.assertEqual(count, 11808)
        self.assertEqual(len(maps), 396)
        self.assertEqual(len({(tuple(x["source_column_masks"]),
                               tuple(x["reader_inverse_row_masks"])) for x in maps}), 396)
        self.assertEqual(verify.determinant((1, 1, 1, 1, 1, 1, 1, 1, 1)), 0)

    def test_exact_dense_rational_identity_and_wrong_inverse_rejection(self):
        verify.check_sources()
        labels, pairs, supports = verify.load_inputs()
        receipt = verify.verify_gauge_identity(labels, pairs, supports)
        self.assertEqual(receipt["determinant"], 2)
        self.assertEqual(receipt["dense_entries_checked"], 112 * 112)
        self.assertTrue(receipt["wrong_inverse_rejected"])


if __name__ == "__main__":
    unittest.main()
