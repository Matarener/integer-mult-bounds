#!/usr/bin/env python3
"""Failure controls for the omitted-side addition bill."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


class ConsumerBillTests(unittest.TestCase):
    def setUp(self):
        self.b2 = verify.load_b2()
        verify.check_b2(self.b2)
        self.side, self.moment = verify.scaled_operators(self.b2)

    def test_three_banks_match_and_share_one_bill(self):
        counts = []
        for matrix in verify.banks():
            output, adds = verify.consume_bank(self.b2, matrix)
            self.assertEqual(output, verify.reference_bank(self.side, self.moment, matrix))
            counts.append(adds)
        self.assertEqual(counts, [199680, 199680, 199680])

    def test_zero_bank_is_zero_and_still_pays_the_straight_line(self):
        zero = [[0 for _ in range(verify.N)] for _ in range(verify.N)]
        output, adds = verify.consume_bank(self.b2, zero)
        self.assertEqual(output, verify.reference_bank(self.side, self.moment, zero))
        self.assertTrue(all(entry == 0 for row in output for entry in row))
        self.assertEqual(adds, 199680)

    def test_omitting_btb_breaks_the_identity(self):
        matrix = verify.banks()[0]
        output, adds = verify.consume_bank(self.b2, matrix, omit_btb=True)
        reference = verify.reference_bank(self.side, self.moment, matrix)
        self.assertNotEqual(output[8][0], reference[8][0])
        self.assertEqual(adds, 199680 - verify.N * 384)

    def test_flipping_one_b2_entry_breaks_the_gram_identity(self):
        mutated = [row[:] for row in self.b2]
        mutated[0][0] = 0 if mutated[0][0] else 1
        with self.assertRaises(SystemExit):
            verify.check_b2(mutated)

    def test_two_pair_saving_does_not_pay_for_one_side(self):
        self.assertEqual(verify.gram_add_saving(2), 110592)
        self.assertLess(verify.gram_add_saving(2) - 199680, 0)
        self.assertGreater(verify.gram_add_saving(3) - 199680, 0)
        self.assertGreater(verify.CODED_PAIR_ADDS + 2 * 199680, verify.REFERENCE_PAIR_ADDS)


if __name__ == "__main__":
    unittest.main()
