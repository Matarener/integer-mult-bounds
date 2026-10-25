from fractions import Fraction
from itertools import combinations
import importlib.util
from pathlib import Path
import unittest

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('rational_pair_verify', PACKAGE / 'verify.py')
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class RationalPairGaugeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        labels, pairs, supports = VERIFY.load_inputs()
        cls.basis, cls.channel_planes, _, _ = VERIFY.geometry(labels, pairs, supports)
        cls.supports = supports
        cls.base_costs = [VERIFY.pairing_rank(VERIFY.plane_vectors(mask, cls.basis),
                                               VERIFY.plane_vectors(mask, cls.basis))
                          for mask in cls.channel_planes]

    def test_every_base_pair_has_exact_rational_minimum_zero(self):
        state = VERIFY.GaugeState()
        minima = []
        for i, j in combinations(range(VERIFY.CHANNELS), 2):
            local = VERIFY.local_pair_minimum(state, i, j,
                                               self.channel_planes, self.basis)
            minima.append((i, j, local['invoice'], local['candidate_slopes']))
        self.assertEqual(len(minima), 561)
        self.assertTrue(all(invoice == self.base_costs[i] + self.base_costs[j]
                            for i, j, invoice, _ in minima))
        self.assertTrue(all(count == 4 for _, _, _, count in minima))

    def test_two_generic_directions_are_kept_distinct(self):
        state = VERIFY.GaugeState()
        candidates = VERIFY.projective_candidates(state, 0, 1)
        self.assertEqual(candidates, [Fraction(0), Fraction(1), Fraction(2), None])

    def test_arbitrary_rational_directions_are_dominated_by_exact_cell_census(self):
        state = VERIFY.GaugeState()
        i, j = 0, 7
        local = VERIFY.local_pair_minimum(state, i, j, self.channel_planes, self.basis)
        minimum = local['invoice']
        samples = [Fraction(-7, 3), Fraction(-1, 2), Fraction(1, 3),
                   Fraction(5, 2), Fraction(17), None]
        for x in samples:
            for y in samples:
                if x == y:
                    continue
                changed_columns, changed_rows = state.apply(i, j, x, y)
                direct = (VERIFY.pairing_rank(
                              VERIFY.plane_vectors(
                                  VERIFY.union_planes(VERIFY.support_mask(changed_columns[0]),
                                                      self.channel_planes), self.basis),
                              VERIFY.plane_vectors(
                                  VERIFY.union_planes(VERIFY.support_mask(changed_rows[0]),
                                                      self.channel_planes), self.basis))
                          + VERIFY.pairing_rank(
                              VERIFY.plane_vectors(
                                  VERIFY.union_planes(VERIFY.support_mask(changed_columns[1]),
                                                      self.channel_planes), self.basis),
                              VERIFY.plane_vectors(
                                  VERIFY.union_planes(VERIFY.support_mask(changed_rows[1]),
                                                      self.channel_planes), self.basis)))
                self.assertGreaterEqual(direct, minimum)

    def test_exact_breakpoints_after_an_even_denominator_gauge(self):
        state = VERIFY.GaugeState()
        columns, rows = state.apply(0, 1, Fraction(0), Fraction(2))
        state.columns[0], state.columns[1] = columns
        state.rows[0], state.rows[1] = rows
        state.check_inverse()
        candidates = VERIFY.projective_candidates(state, 0, 1)
        self.assertIn(Fraction(-1), candidates)
        self.assertEqual(len(candidates), 5)
        minimum = VERIFY.local_pair_minimum(
            state, 0, 1, self.channel_planes, self.basis)['invoice']
        for x, y in ((Fraction(-1), Fraction(1, 2)),
                     (Fraction(1, 3), Fraction(4)),
                     (Fraction(0), None)):
            columns, rows = state.apply(0, 1, x, y)
            direct = 0
            for col, row in zip(columns, rows):
                source_mask = VERIFY.union_planes(
                    VERIFY.support_mask(col), self.channel_planes)
                reader_mask = VERIFY.union_planes(
                    VERIFY.support_mask(row), self.channel_planes)
                direct += VERIFY.pairing_rank(
                    VERIFY.plane_vectors(source_mask, self.basis),
                    VERIFY.plane_vectors(reader_mask, self.basis))
            self.assertGreaterEqual(direct, minimum)

    def test_singular_basis_is_rejected(self):
        state = VERIFY.GaugeState()
        with self.assertRaises(VERIFY.CheckFailure):
            state.apply(0, 1, Fraction(3, 2), Fraction(3, 2))

    def test_det_two_exact_fixture_and_wrong_inverse_control(self):
        labels, pairs, supports = VERIFY.load_inputs()
        _, _, owner, orthogonal = VERIFY.geometry(labels, pairs, supports)
        K = VERIFY.scalar_matrix(supports)
        VERIFY.check_scalar_mask(K, owner, orthogonal, supports)
        fixture = VERIFY.rational_fixture(K, supports)
        self.assertEqual(fixture['determinant'], 2)
        self.assertEqual(fixture['scalar_entries_checked'], 112 * 112)
        self.assertTrue(fixture['wrong_inverse_rejected'])


if __name__ == '__main__':
    unittest.main()
