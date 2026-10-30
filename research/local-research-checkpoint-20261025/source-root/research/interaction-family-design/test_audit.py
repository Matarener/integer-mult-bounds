"""Independent small controls for the structural design screens."""
import json
import itertools
from fractions import Fraction as Q
from pathlib import Path
import unittest
import audit as A


class Screens(unittest.TestCase):
    def test_triangle_hypothesis_is_essential(self):
        c = A.graph_screen([7, 7, 7])
        self.assertFalse(c['triangle_free'])
        self.assertEqual(c['rank'], 1)
        self.assertGreater(c['v'], c['rank']*(c['rank']+1))

    def test_all_small_directed_supports(self):
        # Exhaust all 4096 diagonal-one 4x4 binary matrices. Both directions
        # must enter the graph, even though the scalar matrix need not be symmetric.
        positions = [(i, j) for i in range(4) for j in range(4) if i != j]
        for mask in range(1 << len(positions)):
            rows = [1 << i for i in range(4)]
            for b, (i, j) in enumerate(positions):
                if (mask >> b)&1:
                    rows[i] |= 1 << j
            A.graph_screen(rows)

    def test_integer_scale_screen_against_brute_force(self):
        for alpha in (Q(1, 2), Q(2, 5), Q(1, 3), Q(2, 7), Q(1, 10)):
            for strict in (False, True):
                expected = None
                for v in range(1, 150):
                    ks = [k for k in range(1, v+1) if v <= k*(k+1)
                          and ((Q(k, v) < alpha) if strict else (Q(k, v) <= alpha))]
                    if ks:
                        expected = (v, min(ks))
                        break
                got = A.minimum_scale(alpha, strict)
                self.assertEqual(expected, (got['minimum_ports'],
                                            got['central_rank_at_first_scale']))

    def test_cycle_dimension_inequality_is_sharp(self):
        for k in (2, 3, 7, 9):
            c = A.odd_cycle_control(k)
            self.assertEqual(k*(c['d']-2*c['r']), c['r'])
        self.assertLess(8*(19-2*9), 9)  # a 17-cycle cannot support rank 9 in 19

    def test_span_floor_against_integer_optimization(self):
        for v in range(1, 61):
            for r in (1, 2, 9):
                brute = min(r*K+b for K in range(1, v+1)
                            for b in range(K+1) if v <= K*(b+1)-b*(b-1)//2)
                self.assertEqual(A.span_loss_floor(v, r)['loss'], brute)

    def test_grouped_channel_inequality(self):
        # Every binary 3x3 matrix with unit diagonal; factor via a row basis.
        # Independent color classes stand for coincident address images.
        positions = [(i, j) for i in range(3) for j in range(3) if i != j]
        for mask in range(1 << len(positions)):
            rows = [1 << i for i in range(3)]
            for bit, (i, j) in enumerate(positions):
                if (mask >> bit)&1:
                    rows[i] |= 1 << j
            c = A.graph_screen(rows)
            if not c['triangle_free']:
                continue
            basis = []
            for row in rows:
                if A.B.H.binary_rank(basis+[row]) > len(basis):
                    basis.append(row)
            K = len(basis)
            for colors in itertools.product(range(3), repeat=3):
                if any(colors[i] == colors[j] and
                       (((rows[i] >> j)&1) or ((rows[j] >> i)&1))
                       for i in range(3) for j in range(i)):
                    continue
                b = sum(len({colors[i] for i in range(3) if (row >> i)&1}) > 1
                        for row in basis)
                self.assertLessEqual(3, K*(b+1)-b*(b-1)//2)

    def test_folded_cube_characteristic_gap(self):
        c = A.folded_cube(5)
        self.assertEqual((c['binary_rank'], c['rational_rank']), (6, 16))
        # Independently eliminate the small integer matrix over Q.
        generators = [1, 2, 4, 8, 15]
        dense = [[int(i == j or (i ^ j) in generators)
                  for j in range(16)] for i in range(16)]
        self.assertEqual(A.B.H.rank(dense), 16)
        # It is important not to claim the integer matrix is invertible for
        # every odd cube: q=7 has zero Walsh eigenvalues.
        self.assertLess(A.folded_cube(7)['rational_rank'], 64)

    def test_copy_floor_invalidates_passing_histogram(self):
        raw = A.B.ideal_budget(19, 9, Q(2, 25), Q(1), Q(1, 250))
        self.assertLess(raw['moment_interval'][1], 1)
        self.assertEqual(A.rank_floor(250), 16)
        corrected = A.B.ideal_budget(19, 9, Q(2, 25), Q(1), Q(144, 4750))
        self.assertGreater(corrected['moment_interval'][0], 1)

    def test_saved_certificate(self):
        self.assertEqual(A.encode(A.audit()), json.loads(
            (Path(__file__).parent/'certificate.json').read_text()))


if __name__ == '__main__':
    unittest.main()
