"""Independent controls for the bounded geometry/budget screen."""
from fractions import Fraction as Q
import json
from pathlib import Path
import unittest
import screen as S


def tensor(a, b):
    return [[x*y for x in ra for y in rb] for ra in a for rb in b]


def diag_support(n, support):
    return [[Q(i == j and i in support) for j in range(n)] for i in range(n)]


class Controls(unittest.TestCase):
    def test_integer_power_enclosures(self):
        for x in (Q(1, 121), Q(25, 121), Q(36, 121), Q(110, 5)):
            for p, q in ((23, 25), (37, 40)):
                lo, hi = S.power_interval(x, p, q)
                self.assertLessEqual(lo**q, x**p)
                self.assertLessEqual(x**p, hi**q)
                self.assertLessEqual(hi-lo, Q(1, 10**24))

    def test_collision_of_equal_widths_is_counted(self):
        b = S.block_budget(2, 1, Q(2, 25), Q(1))
        self.assertEqual(b['rows'], {1: 7, 2: 4})
        self.assertEqual(sum(t*n for t, n in b['rows'].items()), 15)
        self.assertEqual(b['W_per_pair']*b['m'], 16)

    def test_optimistic_pass_is_rejected_after_required_ports(self):
        for s in (Q(2, 25), Q(3, 40)):
            bare = S.block_budget(11, 5, s, Q(0))
            paid = S.block_budget(11, 5, s, Q(1))
            self.assertLess(bare['moment_interval'][1], 1)
            self.assertGreater(paid['moment_interval'][0], 1)
            for rho in (Q(2), Q(100)):
                self.assertTrue(S.block_budget(11, 5, s, rho)['excluded'])

    def test_packet_common_form_and_corrupt_normalization(self):
        control = S.sunflower_control()
        p = control['projector_left']
        G = [[Q(i == j)-Q(1, 9) for j in range(11)] for i in range(11)]
        pt = list(map(list, zip(*p)))
        self.assertEqual(S.mm(pt, G), S.mm(G, p))
        bad = [[2*x for x in row] for row in p]
        self.assertNotEqual(S.mm(bad, bad), bad)

    def test_dense_small_tensor_products(self):
        # Independent expanded matrices check all three ways the product's
        # off-diagonal central entry can be one. The control also exhibits
        # a nonzero product when neither factor imposes annihilation.
        h, n, r = 5, 5, 2
        sets = [set((i+2*j) % n for j in range(r)) for i in range(n)]
        def P(t, i):
            return tensor(S.line_projector(h, t), diag_support(n, sets[i]))
        a, b, c = (0, 1, 2), (0, 3, 4), (0, 1, 3)
        p = P(a, 0)
        self.assertEqual(S.mm(p, p), p)
        self.assertEqual(S.rank(p), r)
        for t, i in ((a, 1), (b, 0), (b, 1)):
            q = P(t, i)
            for product in (S.mm(p, q), S.mm(q, p)):
                self.assertFalse(any(any(row) for row in product))
        self.assertTrue(any(any(row) for row in S.mm(p, P(c, 0))))

    def test_saved_receipt_and_source_pins(self):
        self.assertEqual(S.encode(S.audit()), json.loads(
            (Path(__file__).parent/'certificate.json').read_text()))


if __name__ == '__main__':
    unittest.main()
