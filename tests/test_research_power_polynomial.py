# SPDX-License-Identifier: Apache-2.0
"""Independent range and factor oracles for uniform power invoice order.

Ali Romman with substantial OpenAI Codex assistance.
"""

from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/compare_power_polynomial.py"
SPEC = importlib.util.spec_from_file_location("power_polynomial", SCRIPT)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def invoice(paid=None, targets=None):
    return {"schema": "integer-mult-recursive-invoice/v1", "contract": {
        "model": "test-common-base", "rank_semantics": "r^t",
        "ambient_rank": 10**9, "boundary": "same declared unit"},
        "paid": {str(r): n for r, n in (paid or {}).items()},
        "targets": {str(r): n for r, n in (targets or {}).items()}}


def times(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


class PowerPolynomialTests(unittest.TestCase):
    def test_inconclusive_hinge_has_strict_uniform_power_order(self):
        old, new = invoice({2: 2}), invoice({1: 1, 4: 1})
        self.assertEqual(M.INVOICES["compare_invoices"](old, new)["classification"], "inconclusive")
        result = M.compare(old, new)
        self.assertEqual(result["classification"], "uniformly_higher")
        self.assertEqual(result["polynomial_ascending"], [1, -2, 1])
        self.assertEqual(result["endpoint_multiplicities"], {"1": 2, "2": 0})
        self.assertEqual(M.compare(new, old)["classification"], "uniformly_lower")

    def test_interior_equality_and_crossing_are_different(self):
        for coefficients, expected, odd in (([9, -12, 4], "nonnegative_with_equality", 0),
                                             ([-9, 12, -4], "nonpositive_with_equality", 0),
                                             ([-3, 2], "crossing", 1)):
            result = M.classify_polynomial(coefficients, 2)
            self.assertEqual(result["classification"], expected)
            self.assertEqual((result["interior_roots"], result["odd_interior_roots"]), (1, odd))

    def test_all_343_small_quadratics_against_extrema_and_monotone_intervals(self):
        for c, b, a in product(range(-3, 4), repeat=3):
            poly = [c, b, a]
            if not any(poly):
                expected, roots = "equal", 0
            else:
                # An independent quadratic range oracle uses the vertex and
                # monotone pieces. It does not use a GCD or Sturm sequence.
                points = [Q(1), Q(2)]
                if a and 1 < Q(-b, 2 * a) < 2:
                    points.insert(1, Q(-b, 2 * a))
                values = [a * x * x + b * x + c for x in points]
                roots = sum(v == 0 for v in values[1:-1])
                roots += sum(x * y < 0 for x, y in zip(values, values[1:]))
                low, high = min(values), max(values)
                expected = ("crossing" if low < 0 < high else
                            "nonnegative_with_equality" if low >= 0 and roots else
                            "nonpositive_with_equality" if high <= 0 and roots else
                            "uniformly_higher" if low >= 0 else "uniformly_lower")
            result = M.classify_polynomial(poly, 2)
            self.assertEqual((result["classification"], result["interior_roots"]),
                             (expected, roots), poly)

    def test_288_factored_polynomials_with_repeated_and_endpoint_roots(self):
        for middle, left, right, nonreal in product(range(6), range(4), range(4), range(3)):
            poly = [1]
            for count, factor in ((middle, [-3, 2]), (left, [-1, 1]),
                                  (right, [-2, 1]), (nonreal, [1, 0, 1])):
                for _ in range(count):
                    poly = times(poly, factor)
            expected = ("crossing" if middle % 2 else
                        "nonpositive_with_equality" if middle and right % 2 else
                        "nonnegative_with_equality" if middle else
                        "uniformly_lower" if right % 2 else "uniformly_higher")
            result = M.classify_polynomial(poly, 2)
            self.assertEqual(result["classification"], expected, (middle, left, right, nonreal))
            self.assertEqual(result["interior_roots"], int(middle > 0))
            self.assertEqual(result["odd_interior_roots"], middle % 2)
            self.assertEqual(result["endpoint_multiplicities"], {"1": left, "2": right})

    def test_irrational_roots_and_maximum_degree(self):
        square = times([-3, 0, 1], [-3, 0, 1])
        result = M.classify_polynomial(square, 2)
        self.assertEqual((result["classification"], result["interior_roots"]),
                         ("nonnegative_with_equality", 1))
        poly = [1]
        for _ in range(29):
            poly = times(poly, [-3, 2])
        old = invoice({2**i: -v for i, v in enumerate(poly) if v < 0})
        new = invoice({2**i: v for i, v in enumerate(poly) if v > 0})
        result = M.compare(old, new)
        self.assertEqual((result["classification"], result["interior_roots"],
                          result["odd_interior_roots"]), ("crossing", 1, 1))

    def test_common_base_targets_cancellation_and_large_coefficients(self):
        self.assertEqual(M.common_base([1, 36, 216]), (6, {1: 0, 36: 2, 216: 3}))
        self.assertEqual(M.common_base([16, 64])[0], 2)
        with self.assertRaisesRegex(ValueError, "not powers"):
            M.compare(invoice({2: 1}), invoice({3: 1}))
        old = invoice({3: 10**60, 2: 2}, {4: 1})
        new = invoice({3: 10**60, 1: 1})
        self.assertEqual(M.compare(old, new)["classification"], "uniformly_higher")
        self.assertEqual(M.compare(invoice({3: 1}), invoice({3: 1}))["classification"], "equal")
        self.assertEqual(M.compare(invoice(), invoice({1: 10**60}))["classification"], "uniformly_higher")

    def test_real_cli_optimized_byte_binding_and_domain_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            old, new = Path(tmp) / "old.json", Path(tmp) / "new.json"
            old.write_text(json.dumps(invoice({2: 2})), encoding="utf-8")
            new.write_text(json.dumps(invoice({1: 1, 4: 1})), encoding="utf-8")
            command = [sys.executable, "-I", "-O", "-B", str(SCRIPT), str(old), str(new)]
            run = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads(run.stdout)
            self.assertEqual(report["classification"], "uniformly_higher")
            self.assertEqual(report["inputs"]["old"]["sha256"], sha256(old.read_bytes()).hexdigest())
            for bad in (invoice({3: 1}), invoice({2: True}), dict(invoice(), schema="unsupported")):
                new.write_text(json.dumps(bad), encoding="utf-8")
                run = subprocess.run(command, text=True, capture_output=True)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, "")

    def test_optional_independent_sympy_root_isolation(self):
        try:
            import sympy
        except ImportError:
            self.skipTest("Optional independent oracle: install sympy==1.14.0")
        x = sympy.Symbol("x")
        fixtures = []
        for seed in range(48):
            degree = 29 if seed < 24 else 1 + seed % 15
            poly = [int.from_bytes(sha256(f"{seed}:{i}".encode()).digest(), "big")
                    % (2 * 10**60) - 10**60 for i in range(degree + 1)]
            fixtures.append(poly)
        for multiplicity in range(1, 17):
            poly = [1]
            for _ in range(multiplicity):
                poly = times(poly, [-3, 2])
            fixtures.append(times(times(poly, [-1, 1]), [-2, 1]))
        for poly in fixtures:
            source = sympy.Poly(sum(c * x**i for i, c in enumerate(poly)), x)
            intervals = source.intervals(inf=1, sup=2)
            interior = [(ab, multiplicity) for ab, multiplicity in intervals
                        if ab not in ((1, 1), (2, 2))]
            odd = sum(m % 2 for _, m in interior)
            result = M.classify_polynomial(poly, 2)
            self.assertEqual((result["interior_roots"], result["odd_interior_roots"]),
                             (len(interior), odd), poly)
            self.assertEqual(result["classification"] == "crossing", odd > 0)


if __name__ == "__main__":
    unittest.main()
