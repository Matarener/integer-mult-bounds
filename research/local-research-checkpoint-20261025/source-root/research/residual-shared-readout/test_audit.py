"""Adverse controls for the scoped residual shared-readout exclusions."""
from fractions import Fraction as Q
import unittest
import audit as R

A = R.A


class ResidualReadout(unittest.TestCase):
    def test_exact_direct_words_and_charged_peeling(self):
        for binary in (False, True):
            for copies, expected in (((), 52), ((0,), 47), ((1,), 47), ((0, 1), 42)):
                row = R.direct_word(5, copies, binary)
                self.assertEqual(row['residual_rank'], expected)
                self.assertEqual(sum(int(w)*c for w, c in row['complete_histogram'].items()),
                                 expected+6)
                self.assertGreater(row['moment_increase'][0], 0)

    def test_shared_transform_really_works_when_both_inputs_have_same_frame_and_demands(self):
        # A positive control: the rejection must not be interpreted as
        # forbidding one transform of a sum in every broadcast problem.
        labels, K, L, _ = R.setup(5)
        n = len(labels)
        U = [[1, 1]]*n
        centers = [A.unit(n+j, 10) for j in range(2)]
        for binary in (False, True):
            mixed = A.plus(centers[0], centers[1], binary=binary)
            copied = A.move(mixed, A.partial(L[0]))
            actual = [A.move(A.plus(A.unit(t, 10), copied, binary=binary), A.partial(K[t]))
                      for t in range(n)]
            self.assertEqual(actual, A.expected(U, K, [L[0], L[0]], binary))
            self.assertNotEqual(actual, A.expected(U, K, L, binary))

    def test_exclusive_demands_block_using_a_single_transformed_sum(self):
        labels, K, L, U = R.setup(5)
        n = len(labels)
        centers = [A.unit(n+j, 10) for j in range(2)]
        t = U.index([1, 0])
        copied = A.move(A.plus(*centers, binary=True), A.partial(L[0]))
        actual = A.move(A.plus(A.unit(t, 10), copied, binary=True), A.partial(K[t]))
        self.assertNotEqual(actual, A.expected(U, K, L, True)[t])
        self.assertNotEqual(actual, A.expected(U, K, [L[0], L[0]], True)[t])
        self.assertTrue(any(role == n+1 for role, _ in actual))

    def test_address_matrix_quotient_and_operator_quotient_are_different(self):
        labels, K, L, U = R.setup(5)
        P = [A.sub(A.eye(5), k) for k in K]
        _, q = A.discrepancy(P, L, U)
        self.assertEqual(A.rank(q), 1)
        result = R.operator_obstruction(5)
        self.assertEqual(result['early_extra_transform_lower_bound'], 2)
        self.assertEqual(result['late_extra_transform_lower_bound'], 9)
        self.assertEqual(result['distinct_operators'], result['distinct_images'])

    def test_general_ledger_predicts_larger_exact_control(self):
        for copies in ((), (0,), (0, 1)):
            row = R.direct_word(6, copies, True)
            self.assertEqual(row['residual_histogram'], R.formula_ledger(6, len(copies)))
        base = 1771*22
        for copies in range(3):
            hist = R.formula_ledger(23, copies)
            self.assertEqual(sum(w*c for w, c in hist.items()), base+copies+42*(2-copies))

    def test_noncommuting_residual_lines_prevent_a_free_common_frame(self):
        _, _, L, _ = R.setup(6)
        self.assertNotEqual(A.mm(L[0], L[1]), A.mm(L[1], L[0]))
        self.assertEqual(A.rank(A.sub(L[0], L[1])), 2)


if __name__ == '__main__':
    unittest.main()
