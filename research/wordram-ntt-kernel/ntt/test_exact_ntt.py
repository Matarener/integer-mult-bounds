"""Independent finite checks, not universal proof or a runtime benchmark."""
import itertools
import random
import unittest
from exact_ntt import (Counts, carry_normalize, direct_dft, evaluate,
                       exact_convolution, multiply_digits, multiply_integers, ntt, schoolbook,
                       validate_root)


class ExactNTTTests(unittest.TestCase):
    def test_transform_against_direct_dft(self):
        rng = random.Random(20261024)
        for n in [1, 2, 4, 8, 16, 32]:
            omega = pow(3, 65536 // n, 65537)
            for _ in range(12):
                a = [rng.randrange(65537) for _ in range(n)]
                self.assertEqual(ntt(a, 65537, omega), direct_dft(a, 65537, omega))
                self.assertEqual(ntt(a, 65537, omega, True),
                                 direct_dft(a, 65537, omega, True))
                self.assertEqual(ntt(ntt(a, 65537, omega), 65537, omega, True), a)

    def test_all_binary_vectors_up_to_four_digits(self):
        vectors = [list(v) for length in range(1, 5)
                   for v in itertools.product(range(2), repeat=length)]
        for a in vectors:
            for b in vectors:
                c = exact_convolution(a, b, 2)
                self.assertEqual(c, schoolbook(a, b))
                self.assertEqual(evaluate(carry_normalize(c, 2), 2),
                                 evaluate(a, 2) * evaluate(b, 2))

    def test_random_asymmetric_and_maximal_digits(self):
        rng = random.Random(5413)
        for s, t in [(1, 1), (1, 4096), (3, 137), (16, 17),
                     (127, 129), (256, 256), (291, 310)]:
            for maximal in [False, True]:
                a = [15 if maximal else rng.randrange(16) for _ in range(s)]
                b = [15 if maximal else rng.randrange(16) for _ in range(t)]
                c = exact_convolution(a, b)
                self.assertEqual(c, schoolbook(a, b))
                self.assertEqual(evaluate(multiply_digits(a, b), 16),
                                 evaluate(a, 16) * evaluate(b, 16))

    def test_upper_binary_transform_length(self):
        # Boundary N=65536, asymmetric operands; coefficient bound is 2.
        a = [1, 1]
        b = [1] * 65535
        c = exact_convolution(a, b, 2)
        self.assertEqual(c, [1] + [2] * 65534 + [1])
        self.assertEqual(evaluate(carry_normalize(c, 2), 2),
                         evaluate(a, 2) * evaluate(b, 2))

    def test_dense_maximum_binary_operands(self):
        length = 32768
        c = exact_convolution([1] * length, [1] * length, 2)
        self.assertEqual(c, list(range(1, length + 1)) +
                         list(range(length - 1, 0, -1)))
        self.assertEqual(evaluate(carry_normalize(c, 2), 2), ((1 << length) - 1) ** 2)

    def test_signed_endpoint(self):
        values = [-2**1024 + 1, -2**127, -256, -1, 0, 1, 255, 2**127, 2**1024 - 1]
        for x in values:
            for y in values:
                self.assertEqual(multiply_integers(x, y), x * y)

    def test_cost_instrumentation(self):
        counts = Counts()
        exact_convolution([15] * 256, [15] * 256, counts=counts)
        self.assertEqual(counts.butterflies, 3 * (512 // 2) * 9)
        self.assertEqual(counts.butterfly_products, counts.butterflies)
        self.assertEqual(counts.twiddle_products, counts.butterflies)
        self.assertEqual(counts.pointwise_products, 512)
        self.assertEqual(counts.inverse_scales, 512)

    def test_invalid_contracts(self):
        for a, b, base in [([], [1], 16), ([16], [1], 16),
                            ([-1], [1], 16), ([1.0], [1], 16),
                            ([15] * 292, [15] * 292, 16)]:
            with self.assertRaises(ValueError):
                exact_convolution(a, b, base)
        for p, n, omega in [(15, 2, 14), (65537, 3, 3),
                             (65537, 8, 1), (65537, 65536, 1)]:
            with self.assertRaises(ValueError):
                validate_root(p, n, omega)
        with self.assertRaises(ValueError):
            exact_convolution([1] * 65536, [1, 1], 2)
        # Strictness: bound == p must fail even though this input is all zero.
        with self.assertRaises(ValueError):
            exact_convolution([0] * 17, [0] * 17, base=2, p=17)


if __name__ == "__main__":
    unittest.main()
