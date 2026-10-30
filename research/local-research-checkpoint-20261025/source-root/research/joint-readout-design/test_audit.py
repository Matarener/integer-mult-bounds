"""Exact and adverse controls for joint target/center readout."""
from fractions import Fraction as Q
from itertools import combinations
import unittest
import audit as A


class JointReadout(unittest.TestCase):
    def test_dirty_target_and_center_decoders_are_paid(self):
        for binary in (False, True):
            pivot = A.target_pivot(binary=binary)
            pair = A.center_pair(binary=binary)
            self.assertEqual((pivot['baseline_rank'], pivot['candidate_rank']), (28, 30))
            self.assertEqual((pair['baseline_rank'], pair['all_common_frame_rank_floor']), (48, 50))
            # The replay also checks that omitting either decoder corrupts
            # the symbolic map on arbitrary independent inputs.

    def test_center_replay_does_not_assume_commuting_projections(self):
        _, _, R = A.geometry(6)
        self.assertNotEqual(A.mm(R[0], R[1]), A.mm(R[1], R[0]))
        self.assertTrue(A.center_pair(6, True)['exact_arbitrary_inputs'])

    def test_single_center_span_hypothesis_is_necessary(self):
        labels, P, R = A.geometry(5)
        p = P[next(i for i, t in enumerate(labels) if 0 in t)]
        D, quotient = A.discrepancy([p], [R[0]], [[1]])
        self.assertEqual(A.rank(quotient), 1)
        self.assertEqual(A.rank(D), 5)
        self.assertLess(A.rank(quotient), A.rank(R[0]))

    def test_pair_incidence_rank_by_independent_modular_elimination(self):
        # A nonsingular modular minor certifies the rational lower bound.
        # The feature identities in audit.py give the rational upper bound.
        def modular_rank(matrix, prime=101):
            a = [list(row) for row in matrix]
            r = 0
            for c in range(len(a[0])):
                pivot = next((i for i in range(r, len(a)) if a[i][c] % prime), None)
                if pivot is None:
                    continue
                a[r], a[pivot] = a[pivot], a[r]
                inv = pow(a[r][c] % prime, -1, prime)
                a[r] = [x*inv % prime for x in a[r]]
                for i in range(r+1, len(a)):
                    k = a[i][c] % prime
                    a[i] = [(x-k*y) % prime for x, y in zip(a[i], a[r])]
                r += 1
            return r
        for h in range(5, 9):
            pairs = list(combinations(range(h), 2))
            triples = list(combinations(range(h), 3))
            incidence = [[int(i in t and j in t) for i, j in pairs] for t in triples]
            self.assertEqual(modular_rank(incidence), len(pairs))
        result = A.joint_quotient(5, dense=True)
        self.assertEqual(result['full_discrepancy_rank'], 50)
        self.assertEqual(result['scalar_broadcast_rank'], 5)

    def test_residual_kernel_is_not_scalar_channel_dependence(self):
        labels, P, _ = A.geometry(5)
        a, b = [Q(1), Q(2), Q(0), Q(0), Q(0)], [Q(2), Q(1), Q(0), Q(0), Q(0)]
        lines = [A.projection([v], 5) for v in (a, b)]
        U = [[int(j in t) for j in range(2)] for t in labels]
        _, q = A.discrepancy(P, lines, U)
        good = [[x] for x in a+[-x for x in b]]
        bad = [[x] for x in a+b]
        self.assertEqual(A.mm(q, good), [[Q(0)] for _ in q])
        self.assertNotEqual(A.mm(q, bad), [[Q(0)] for _ in q])
        self.assertEqual(A.rank(U), 2)
        self.assertEqual(A.rank(q), 1)

    def test_generic_residual_lines_lose_the_one_rank_gap(self):
        labels, P, R = A.geometry(5)
        # Two generic incident triple lines remain nested in their centers,
        # but do not share the specially chosen residual quotient.
        lines = [P[labels.index((0, 2, 3))], P[labels.index((1, 2, 4))]]
        for j in range(2):
            self.assertEqual(A.mm(R[j], lines[j]), lines[j])
        U = [[int(j in t) for j in range(2)] for t in labels]
        _, q = A.discrepancy(P, lines, U)
        self.assertEqual(A.rank(q), 2)

    def test_target_splitting_consumes_the_optimistic_gain(self):
        budget = A.residual_budget(23)
        gain = budget['ideal_moment_gain']
        penalty = budget['per_target_split_penalty']
        self.assertEqual(budget['maximum_such_splits'], 1)
        self.assertLess(penalty[1], gain[0])
        self.assertGreater(2*penalty[0], gain[1])
        self.assertEqual(budget['exclusive_targets'], 420)


if __name__ == '__main__':
    unittest.main()
