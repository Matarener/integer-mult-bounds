"""Adverse controls for deferred cleanup and carried direct readout."""
from fractions import Fraction as Q
from pathlib import Path
import json
import unittest
import audit as A


class BoundaryReadout(unittest.TestCase):
    def test_deferred_cleanup_preserves_every_dirty_input(self):
        a = A.scalar_core()
        b = A.scalar_core(deferred=True)
        self.assertEqual(a['final_rows'], b['final_rows'])
        self.assertEqual((a['gates'], b['gates']), (450, 360))
        self.assertEqual((b['binary_central_rank'], b['rational_rank_of_binary_matrix']), (5, 10))

    def test_old_dirty_correction_cannot_be_omitted(self):
        self.assertFalse(A.scalar_core(deferred=True, omit_old=True)['exact_all_input_map'])

    def test_frame_histogram_does_not_follow_scalar_gate_count(self):
        a, b = [A.framed_cleanup_control(x) for x in (False, True)]
        self.assertEqual(a['histogram'], b['histogram'])
        self.assertEqual(a['categories']['copied readout'], 3*5*4)
        self.assertTrue(a['physical_endpoints_exact'] and b['physical_endpoints_exact'])

    def test_routing_defect_has_only_one_left_null_direction(self):
        # Independently derive the left kernel by unioning rows joined by
        # each X/Y residual column, instead of binary elimination.
        from itertools import permutations
        B = A.B
        g = B.geometry_control(1)
        G = list(permutations(range(6)))
        index = {x: i for i, x in enumerate(G)}
        R = (g['r12'], tuple(range(6)), g['r23'])
        maps = [[index[B.compose(B.compose(x, h), r)] for x in G]
                for h, r in zip(g['bank_maps'], R)]
        inverse_maps = []
        for p in maps:
            inv = [0]*len(G)
            for i, j in enumerate(p):
                inv[j] = i
            inverse_maps.append(inv)
        parent = list(range(len(G)))
        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for j in range(len(G)):
            for a, b in ((0, 1), (1, 2)):
                parent[find(inverse_maps[a][j])] = find(inverse_maps[b][j])
        components = len({find(i) for i in range(len(G))})
        self.assertEqual(components, 1)
        self.assertEqual(A.routing_control()['residual_binary_rank'], len(G)-components)

    def test_direct_readout_charges_target_return(self):
        x = A.direct_fragment()
        self.assertEqual((x['baseline_rank'], x['direct_rank']), (33, 41))
        self.assertEqual(x['direct_children'], {1: 1, 2: 6, 4: 7})

    def test_visiting_the_source_image_is_an_essential_hypothesis(self):
        I = A.eye(3)
        P = [[Q(i == j and i == 0) for j in range(3)] for i in range(3)]
        K = A.sub(I, P)
        # A visit to K does not fix the excluded source direction. It costs
        # only the normal endpoint distance, so the detour lemma must not apply.
        self.assertNotEqual(A.mm(K, P), P)
        self.assertEqual(A.rank(K)+A.rank(A.sub(K, K)), 2)
        self.assertLess(2, 3+1)
        self.assertTrue(all(c['pair_floor'] == 2*c['m'] for c in A.excursion_controls()))

    def test_literal_address_replay_of_direct_readout(self):
        # Two address coordinates per head/tail, modulo three. P=R selects
        # the first pair, K its complement. Exhaust every input address.
        from itertools import product
        def D(a, active):
            a = list(a)
            for i in active:
                a[i], a[2+i] = a[2+i], a[i]
            return tuple(a)
        for address in product(range(3), repeat=4):
            # Coefficients of arbitrary original y and stored z respectively.
            baseline_y = D(address, (1,))
            direct_y = D(D(D(address, (0,)), (0,)), (1,))
            baseline_z = D(D(address, (0,)), (1,))
            direct_z = D(D(address, (0,)), (1,))
            self.assertEqual((baseline_y, baseline_z), (direct_y, direct_z))
        self.assertNotEqual(D((1, 0, 0, 0), (0,)), D((1, 0, 0, 0), (1,)))

    def test_certificate(self):
        self.assertEqual(A.encode(A.audit()), json.loads(
            (Path(__file__).parent/'certificate.json').read_text()))


if __name__ == '__main__':
    unittest.main()
