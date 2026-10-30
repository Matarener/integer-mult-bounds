from copy import deepcopy
from fractions import Fraction
import importlib.util
from pathlib import Path
import random
import unittest

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('rational_triple_verify', PACKAGE / 'verify.py')
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class RationalTripleGaugeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maps, cls.source_patterns, cls.feasible_pairs = \
            VERIFY.enumerate_rational_support_maps()

    def test_complete_rational_support_classification_and_witnesses(self):
        self.assertEqual((self.source_patterns, self.feasible_pairs, len(self.maps)),
                         (247, 487, 487))
        for support_map, witness in self.maps.items():
            VERIFY.verify_symbolic_witness(witness, support_map)

    def test_every_signed_ternary_support_map_is_included(self):
        maps, invertible = VERIFY.signed_ternary_maps()
        self.assertEqual(invertible, 11808)
        self.assertEqual(len(maps), 396)
        self.assertLessEqual(maps, set(self.maps))

    def test_random_integer_matrices_have_classified_supports(self):
        rng = random.Random(20261019)
        checked = 0
        attempts = 0
        while checked < 256 and attempts < 2000:
            attempts += 1
            matrix = [[Fraction(rng.randint(-3, 3)) for _ in range(3)] for _ in range(3)]
            inverse = VERIFY.inverse_matrix(matrix)
            if inverse is None:
                continue
            pattern = sum(1 << (3 * r + c) for r in range(3) for c in range(3)
                         if matrix[r][c])
            inverse_pattern = sum(1 << (3 * r + c) for r in range(3) for c in range(3)
                                  if inverse[r][c])
            support_map = VERIFY.matrix_support_map(pattern, inverse_pattern)
            self.assertIn(support_map, self.maps)
            checked += 1
        self.assertEqual(checked, 256)

    def test_inverse_support_mutation_is_rejected(self):
        support_map, witness = next(iter(self.maps.items()))
        mutant = deepcopy(witness)
        mutant['inverse_support'] ^= 1
        with self.assertRaises(VERIFY.CheckFailure):
            VERIFY.verify_symbolic_witness(mutant, support_map)

    def test_determinant_two_dense_scalar_identity_fixture(self):
        _, _, supports = VERIFY.load_inputs()
        receipt = VERIFY.dense_matrix_control(supports)
        self.assertEqual(receipt['determinant'], 2)
        self.assertEqual(receipt['scalar_entries_checked'], 112 * 112)
        self.assertTrue(receipt['wrong_inverse_rejected'])


if __name__ == '__main__':
    unittest.main()
