"""Independent controls for the in-place producer rejection."""
from fractions import Fraction as Q
from pathlib import Path
import json
import unittest
import audit as A


class Controls(unittest.TestCase):
    def test_budget_thresholds_are_strict(self):
        for d, r, good, bad in ((11, 5, Q(1, 100), Q(11, 1000)),
                                (2, 1, Q(39, 100), Q(2, 5))):
            self.assertLess(A.H.block_budget(d, r, Q(2, 25), good)['moment_interval'][1], 1)
            self.assertGreater(A.H.block_budget(d, r, Q(2, 25), bad)['moment_interval'][0], 1)

    def test_discrepancy_inverse_for_oblique_projectors(self):
        for t in (Q(-7, 3), Q(0), Q(4, 5)):
            U = [[Q(1), t], [Q(0), Q(0)]]
            I, Z = A.identity(2), A.zero(2)
            R, V = A.sub(I, A.scale(2, U)), A.sub(I, U)
            D = [a+b for a, b in zip(Z, A.scale(-1, I))]
            D += [a+b for a, b in zip(R, V)]
            inv = [a+b for a, b in zip(V, R)]
            inv += [a+b for a, b in zip(A.scale(-1, I), Z)]
            self.assertEqual(A.mm(D, inv), A.identity(4))
            self.assertEqual(A.mm(inv, D), A.identity(4))

    def test_idempotence_is_essential_to_the_rank_argument(self):
        model = A.labels(False)
        for i in range(model['n']):
            model['matrices'][f'U{i}'] = A.scale(Q(1, 2), A.identity(2))
            model['matrices'][f'V{i}'] = A.scale(Q(1, 2), A.identity(2))
        D = A.discrepancy(model, A.expected_scalar(3))
        self.assertEqual(A.rank(D), 6)

    def test_all_original_inputs_and_required_restoration(self):
        for fused in (False, True):
            ops = A.word(fused=fused)
            self.assertEqual(A.finite_address_check(ops)['wrong_output_forms'], 0)
        ops = A.word()
        self.assertGreater(A.finite_address_check(ops, correction=False)['wrong_output_forms'], 0)
        self.assertGreater(A.finite_address_check(ops, skip_transition=0)['wrong_output_forms'], 0)
        del ops[-2]
        self.assertGreater(A.finite_address_check(ops)['wrong_output_forms'], 0)

    def test_relative_address_rank_for_noncommuting_frames(self):
        F = A.labels(True)['matrices']
        for p, q in (('U0', 'U1'), ('U1', 'V2'), ('E0', 'A1')):
            P, Qm = F[p], F[q]
            D = A.mm(A.address_matrix(Qm), A.address_matrix(P))
            m = len(P)
            B = [row[m:] for row in D[:m]]
            self.assertEqual(B, A.mm(A.sub(Qm, P), A.sub(A.identity(m), A.scale(2, P))))
            self.assertEqual(A.rank(B), A.rank(A.sub(Qm, P)))

    def test_complete_nonpermutation_telescoping(self):
        for fused in (True, False):
            receipt = A.telescope_control(A.labels(False), A.word(fused=fused))
            self.assertTrue(receipt['exact_matrix_identity'])
            self.assertEqual(receipt['discrepancy_rank'], receipt['dimension'])

    def test_receipt_replay(self):
        receipt = json.loads((Path(__file__).parent/'certificate.json').read_text())
        self.assertEqual(A.encode(A.audit()), receipt)


if __name__ == '__main__':
    unittest.main()
