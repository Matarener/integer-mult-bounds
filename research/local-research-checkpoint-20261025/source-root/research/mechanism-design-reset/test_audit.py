"""Admission and adverse checks for the design comparison."""
import unittest
import audit as A


class MechanismDesign(unittest.TestCase):
    def test_coupled_decoder_restores_arbitrary_workspace_in_both_fields(self):
        for h, binary in ((6, True), (5, False)):
            result = A.terminal_decoder(h, binary)
            self.assertTrue(result['exact_dirty_endpoint'])
            self.assertTrue(result['tested_coefficients_dyadic'])
        self.assertFalse(A.terminal_decoder(5, False, True)['exact_dirty_endpoint'])

    def test_unequal_stage_maps_cannot_be_replaced_by_one_common_map(self):
        for h, binary in ((6, True), (5, False)):
            result = A.unequal_stage_control(h, binary)
            self.assertTrue(result['noncommuting_stages'])
            self.assertGreater(result['algebraic_summary_dimension'], 2*result['channels_per_stage'])
            self.assertLessEqual(result['algebraic_summary_dimension'], result['uncompressed_workspace'])

    def test_binary_nilpotent_shortcut_is_not_a_complex_identity(self):
        f, _, a, b, c = A.factor(6, True)
        self.assertEqual(f.mm(a, b), f.zero(6))
        self.assertEqual(f.mm(c, c), f.zero(len(c)))
        g, _, _, _, d = A.factor(5, False)
        self.assertNotEqual(g.mm(d, d), g.zero(len(d)))
        self.assertNotEqual(g.mm(d, d), g.add(d, d))
        budget = A.nilpotent_controls()['complex_relaxed_endpoint_moments']
        self.assertTrue(all(bounds[0] > 1 for bounds in budget))

    def test_rank_boosting_tensor_labels_break_a_required_edge(self):
        rows = A.tensor_lift_control()['exact_coordinate_counterexample']
        self.assertEqual(rows['intersection']['required_edge_product_rank'], 0)
        for label in ('union', 'parity'):
            self.assertGreater(rows[label]['rank'], rows['intersection']['rank'])
            self.assertGreater(rows[label]['required_edge_product_rank'], 0)

    def test_orbit_packing_charges_both_directions(self):
        for n in (4, 5, 6):
            result = A.orbit_difference_control(n)
            self.assertEqual(result['total_aligned_volume'], result['moved_addresses'])
            self.assertEqual(len(result['paid_alignments']), 2)


if __name__ == '__main__':
    unittest.main()
