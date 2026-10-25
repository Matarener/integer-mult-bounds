"""Bounded arithmetic/control tests; no original source imports or scientific replay.

Run python -I -B [-O] /path/to/test_capacity.py. The capacity module is loaded
from source bytes, never a cached .pyc; no sys.path extension is needed.
Substantial OpenAI Codex assistance. Apache-2.0; original Opus review credit
and selected-source contributor attribution are retained in capacity.py.
"""
import itertools
import math
from pathlib import Path
import sys
import types
import unittest

path = Path(__file__).with_name("capacity.py")
capacity = types.ModuleType("_bridge_capacity_unit")
capacity.__file__ = str(path)
sys.modules[capacity.__name__] = capacity
exec(compile(path.read_bytes(), str(path), "exec", dont_inherit=True), capacity.__dict__)


class CapacityTests(unittest.TestCase):
    def test_tiny_independent_cardinalities(self):
        self.assertEqual(capacity.gl_order(2, 1), 1)
        self.assertEqual(capacity.gl_order(3, 1), 2)
        self.assertEqual(capacity.gl_order(2, 2), 6)
        self.assertEqual(capacity.gl_order(3, 2), 48)
        self.assertEqual(capacity.gl_order(2, 3), 168)
        # Only 16 + 81 tiny 2x2 matrices. No GL64 enumeration/unranking.
        for q in (2, 3):
            nonsingular = sum((a*d - b*c) % q != 0
                              for a, b, c, d in itertools.product(range(q), repeat=4))
            self.assertEqual(capacity.gl_order(q, 2), nonsingular)

    def test_independent_product_factorization(self):
        for q, dimension in ((2, 1), (2, 3), (3, 2), (3, 64), (5, 4)):
            alternative = q ** (dimension * (dimension - 1) // 2)
            alternative *= math.prod(q**j - 1 for j in range(1, dimension + 1))
            self.assertEqual(capacity.gl_order(q, dimension), alternative)

    def test_q3_exact_arithmetic_bound(self):
        report = capacity.build_report()
        n3 = int(report["N_GL64_F3_exact_decimal"])
        t = int(report["T_exact_decimal"])
        minimum = int(report["min_len_2T_exact_decimal"])
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(n3, math.prod(3**64 - 3**k for k in range(64)))
        self.assertEqual(n3.bit_length(), 6492)
        self.assertEqual(len(str(n3)), 1955)
        self.assertEqual(t, 904896 * n3)
        self.assertEqual(minimum, 1809792 * n3)
        self.assertEqual(minimum, 2 * t)
        self.assertEqual(t.bit_length(), 6511)
        self.assertEqual(minimum.bit_length(), 6512)
        self.assertGreaterEqual(n3, (2 * 3**63)**64)
        self.assertGreaterEqual(minimum, 2**6511)
        self.assertLess(minimum, 2**6512)
        self.assertGreater(minimum, 2**6500)
        self.assertTrue(all(report["min_len_gt_conventional"].values()))

    def test_monotonic_argument_not_only_sampled_primes(self):
        argument = capacity.factor_monotonicity()
        self.assertIn("b >= a >= 3", argument["domain"])
        self.assertIn("64-k >= 1", argument["strictness"])
        self.assertIn("every integer q >= 3", argument["conclusion"])
        self.assertFalse(argument["formal_verification"])
        # Finite checks catch an implementation/sign error; the quantified
        # positive-factor argument in the module proves the general statement.
        for a, b in ((3, 3), (3, 4), (4, 5), (6, 7)):
            for k in range(64):
                left_a, right_a = a**k, a**(64-k) - 1
                left_b, right_b = b**k, b**(64-k) - 1
                self.assertGreater(left_a, 0)
                self.assertGreater(right_a, 0)
                self.assertGreaterEqual(left_b, left_a)
                self.assertGreaterEqual(right_b, right_a)
                self.assertEqual(a**64 - a**k, left_a * right_a)
                self.assertGreaterEqual(b**64 - b**k, a**64 - a**k)
                if b > a:
                    self.assertGreater(right_b, right_a)
                    self.assertGreater(b**64 - b**k, a**64 - a**k)

    def test_arithmetic_is_not_source_semantics_or_first_failure(self):
        report = capacity.build_report()
        self.assertFalse(report["source_semantics"]["checked_by_this_script"])
        self.assertFalse(report["source_semantics"]["first_failure_determined"])
        self.assertIn("Conditional on", report["scope"])
        self.assertIn("not a first-failure", report["range_illustration_scope"])
        self.assertIn("not falsified", report["source_semantics"]["unaffected"])
        for filename in report["source_semantics"]["files"]:
            self.assertTrue(filename.startswith("research/"))
            self.assertNotIn("\\", filename)
            self.assertFalse(Path(filename).is_absolute())

    def test_range_illustration_uses_only_two_ordinals(self):
        report = capacity.build_report()
        self.assertFalse(report["illustration_len_range_N_representable"])
        self.assertTrue(report["illustration_range_N_iterates"])
        self.assertIn("not an operation asserted", report["range_illustration_scope"])

    def test_type_and_execution_bounds_survive_optimization(self):
        for q in (True, False, 1, 0, -3, 3.0, "3", 1 << capacity.MAX_Q_BITS):
            with self.subTest(q=q), self.assertRaises(capacity.Rejected):
                capacity.gl_order(q)
        for dimension in (True, False, 0, -1, 65, 2.0, "2"):
            with self.subTest(dimension=dimension), self.assertRaises(capacity.Rejected):
                capacity.gl_order(3, dimension)
        # No primality assertion: q=4 is allowed for arithmetic, not asserted prime.
        self.assertEqual(capacity.gl_order(4, 2), (4**2 - 1) * (4**2 - 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
