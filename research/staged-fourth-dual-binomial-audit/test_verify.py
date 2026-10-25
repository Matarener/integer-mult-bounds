"""Positive arithmetic fixtures and adversarial controls for the scoped audit.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""

import copy
from fractions import Fraction as F
import hashlib
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("dual_audit", Path(__file__).with_name("verify.py"))
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class AuditControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = v.patterns()
        cls.bins, cls.profiles, cls.widths, cls.delta = v.source_model()
        cls.published = v.read_source("RESULT.json")
        cls.support = v.support_from_certificate(cls.published)
        cls.dual, _ = v.reconstruct_dual(cls.support, "middle", cls.delta)
        central, _ = v.primal_system(cls.support, cls.bins, cls.widths, True)
        cls.values = [row[0] for row in central[:-1]]

    def test_known_rational_powers(self):
        # Exact roots, not a second floating-point evaluation of the same formula.
        for base, degree in ((2, 2), (3, 2), (5, 2), (7, 2), (2, 3), (3, 3), (2, 6)):
            rank = base**degree
            a = 1 - F(1, degree)
            exact = (base - rank) / a
            lower, upper = v.normalized_power(rank, a)
            with self.subTest(rank=rank, a=a):
                self.assertLessEqual(lower, exact)
                self.assertGreaterEqual(upper, exact)

    def test_integer_rounding_against_exact_partial_sum(self):
        # A slow Fraction oracle checks rounding and the first-omitted-term index.
        for rank, a, terms in ((2, v.LOW, 1), (3, v.HIGH, 8), (48, F(1, 2), 17)):
            z = F(rank - 1, rank)
            term, total = z, F(0)
            for k in range(1, terms + 1):
                total += term
                term *= (k - a) * z / (k + 1)
            exact_lower, exact_upper = -rank * (total + rank * term), -rank * total
            lower, upper = v.normalized_power(rank, a, terms, 1000)
            self.assertLessEqual(lower, exact_lower)
            self.assertGreaterEqual(upper, exact_upper)

    def test_every_used_rank_against_square_identity(self):
        # At a=1/2, positivity and squaring give an exact oracle for every
        # consumed rank, including the stock rank73, without a root routine.
        for rank in range(1, 74):
            lower, upper = v.normalized_power(rank, F(1, 2))
            lower, upper = rank + lower / 2, rank + upper / 2
            with self.subTest(rank=rank):
                self.assertGreater(lower, 0)
                self.assertLessEqual(lower * lower, rank)
                self.assertGreaterEqual(upper * upper, rank)

    def test_tail_is_necessary_and_included(self):
        # At r=4,a=1/2 the normalized power is exactly -4. A one-term
        # tail-free sum says -3 and excludes the true value.
        lower, upper = v.normalized_power(4, F(1, 2), 1)
        self.assertLessEqual(lower, -4)
        self.assertGreaterEqual(upper, -4)
        self.assertGreater(-4 * F(3, 4), -4)

    def test_outside_series_domain_rejected(self):
        for rank, a in ((0, v.LOW), (1, F(0)), (8, F(1))):
            with self.subTest(rank=rank, a=a), self.assertRaisesRegex(ValueError, "binomial domain"):
                v.normalized_power(rank, a)

    def test_missing_empty_pattern_rejected(self):
        rows = [row for row in self.rows if row != (48, 0, 0, 0, 0, 0, 48)]
        with self.assertRaisesRegex(ValueError, "residual spectrum"):
            v.validate_patterns(rows)

    def test_missing_nonempty_pattern_rejected(self):
        rows = [row for row in self.rows if row != (32, 0, 1, 0, 1, 2, 0)]
        with self.assertRaisesRegex(ValueError, "residual spectrum"):
            v.validate_patterns(rows)

    def test_duplicate_preserving_pattern_count_rejected(self):
        rows = list(self.rows)
        rows[-1] = rows[-2]
        self.assertEqual(len(rows), 841)
        with self.assertRaisesRegex(ValueError, "duplicate pattern"):
            v.validate_patterns(rows)

    def test_wrong_residual_rejected(self):
        rows = list(self.rows)
        rows[0] = (*rows[0][:-1], rows[0][-1] + 1)
        with self.assertRaisesRegex(ValueError, "pattern capacity"):
            v.validate_patterns(rows)

    def test_zero_mass_dual_perturbation_rejected_by_sign(self):
        dual = copy.deepcopy(self.dual)
        # H1-H2/2 is positive for 0<a<1 but has zero rank mass. Increasing
        # u8 by it makes the formerly tight width8/cap8 constraint negative.
        dual[0] = v.combine((1, dual[0]), (1, {1: F(1), 2: -F(1, 2)}))
        with self.assertRaisesRegex(ValueError, "nonpositive dual slack"):
            v.check_dual(self.rows, dual)

    def test_nonzero_mass_cannot_be_divided_out(self):
        with self.assertRaisesRegex(ValueError, "zero rank mass"):
            v.interval_expression({1: F(1)})

    def test_insufficient_enclosure_precision_fails_closed(self):
        original = v.normalized_power
        with patch.object(v, "normalized_power", side_effect=lambda r, a, *args: original(r, a, 1)):
            with self.assertRaisesRegex(ValueError, "nonpositive dual slack"):
                v.check_dual(self.rows, self.dual)

    def test_wrong_mixture_with_central_primal_rejected(self):
        with self.assertRaisesRegex(ValueError, "primal bin/helper balance"):
            v.check_primal(self.support, self.values, 1090, self.bins, self.widths)

    def test_extra_empty_bin_rejected(self):
        values = list(self.values)
        empty = self.support.index((48, 0, 0, 0, 0, 0, 48))
        values[empty] += 1
        with self.assertRaisesRegex(ValueError, "primal bin/helper balance"):
            v.check_primal(self.support, values, 1080, self.bins, self.widths)

    def test_wrong_width_inventory_rejected(self):
        widths = copy.deepcopy(self.widths)
        widths["THREE"][7] += 1
        with self.assertRaisesRegex(ValueError, "primal bin/helper balance"):
            v.check_primal(self.support, self.values, 1080, self.bins, widths)

    def test_historical_replica_factor_rejected(self):
        bins = {c: F(n * 37, 360) for c, n in self.bins.items()}
        with self.assertRaisesRegex(ValueError, "primal bin/helper balance"):
            v.check_primal(self.support, self.values, 1080, bins, self.widths)

    def test_negative_primal_rejected(self):
        values = list(self.values)
        values[0] = -1
        with self.assertRaisesRegex(ValueError, "nonnegative primal"):
            v.check_primal(self.support, values, 1080, self.bins, self.widths)

    def test_missing_paid_local_charge_rejected(self):
        profiles = copy.deepcopy(self.profiles)
        profiles["THREE"][1] -= 1
        profiles["FOUR"][1] -= 1
        # Same delta and source dimensions, but the completed invoice is wrong.
        with patch.object(v, "source_model", return_value=(self.bins, profiles, self.widths, self.delta)):
            with self.assertRaisesRegex(ValueError, "complete paid profile"):
                v.compute()

    def test_tampered_source_rejected(self):
        original = b"pinned scientific input"
        expected = hashlib.sha256(original).hexdigest()
        v.check_digest(original, expected)
        with self.assertRaisesRegex(ValueError, "source digest mismatch"):
            v.check_digest(original + b" ", expected)

    def test_singular_equality_system_rejected(self):
        with self.assertRaisesRegex(ValueError, "singular exact system"):
            v.solve([[1, 1], [1, 1]], [[0], [0]])

    def test_source_frame_span_positive_and_bad_vector(self):
        self.assertEqual(v.binary_span([1, 2, 3, 2]), {0, 1, 2, 3})
        with self.assertRaisesRegex(ValueError, "binary frame vector"):
            v.binary_span([512])


if __name__ == "__main__":
    unittest.main(verbosity=2)
