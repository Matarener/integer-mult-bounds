"""Source-pinned and adverse controls for the decoder admission screen."""
from fractions import Fraction as Q
import unittest
import audit as A


class TerminalAdmission(unittest.TestCase):
    def test_actual_complex_summary_budget(self):
        result = A.source_control()
        self.assertEqual(result['leverage'], Q(1, 60))
        self.assertEqual(result['projection_trace_per_group'], Q(11, 30))
        self.assertEqual(result['both_input_summary_rank_lower_per_group'], Q(1309, 15))
        self.assertEqual(result['expansion_over_aligned_lower'], Q(119, 60))
        self.assertEqual(result['route_maps_checked'], 2640)

    def test_dense_regular_cover_and_routing_collision(self):
        distinct = A.regular_cover_control(False)
        collided = A.regular_cover_control(True)
        self.assertEqual(distinct['trace'], distinct['intersection'])
        self.assertEqual(distinct['stacked_rank'], 8)
        self.assertEqual(collided['stacked_rank'], 6)
        self.assertNotEqual(collided['trace'], collided['diagonal_formula'])

    def test_exchange_family_fixes_padding_and_source(self):
        for block in (1, 3):
            x, y = A.exchange(21, 6, block), A.exchange(22, 6, block)
            self.assertNotEqual(x, y)
            self.assertEqual(A.apply(x, 21), 21)
            self.assertEqual(x[-2:], (1 << 16, 1 << 17))

    def test_common_frame_bound_requires_distinct_caps(self):
        self.assertEqual(A.common_frame_control()['minimum_one_way_sum'], 8)
        cap = A.basis(x for x in range(16) if x & 1 == 0)
        # A single cap can be its own common frame at zero cost.
        self.assertEqual(2*len(A.basis(cap+cap))-2*len(cap), 0)

    def test_auxiliary_stock_cannot_dilute_capacity_failure(self):
        m, n = 66, 1320
        for stock in (0, 1, 22, 88, 10686):
            self.assertEqual(2*n*(m-1)+2*n+stock*m, (2*n+stock)*m)


if __name__ == '__main__':
    unittest.main()
