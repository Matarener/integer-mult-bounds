#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral and independent arithmetic controls for the uniform theorem."""

import copy
import runpy
import unittest
from fractions import Fraction as Q
from pathlib import Path

V = runpy.run_path(str(Path(__file__).with_name("verify.py")))


class UniformTests(unittest.TestCase):
    def test_complete_pattern_domain(self):
        cert = V["load_json"](V["HERE"] / "CERTIFICATE.json")
        actual = {(c, ns) for c, ns, _r, _a, _b in V["patterns"](cert)}
        expected = set()
        for capacity in (8, 16, 32, 48):
            frontier = [((), 0)]
            for width in (4, 5, 7, 8, 9):
                frontier = [
                    (ns + (n,), mass + n * width)
                    for ns, mass in frontier
                    for n in range((capacity - mass) // width + 1)
                ]
            expected.update((capacity, ns) for ns, _mass in frontier)
        self.assertEqual(actual, expected)

    def test_inventory_semantics(self):
        cert = V["load_json"](V["HERE"] / "CERTIFICATE.json")
        self.assertEqual(V["witness"](cert, V["RHS"]), {1: 2431, 17: 1, 48: 4887})
        for value in (0, -1, Q(1, 2)):
            bad = copy.deepcopy(cert)
            bad["integer_patterns"][0]["multiplicity"] = value
            with self.assertRaisesRegex(ValueError, "multiplicity"):
                V["witness"](bad, V["RHS"])
        bad = copy.deepcopy(cert)
        bad["integer_patterns"][0]["counts"] = [3, 0, 0, 0, 0]
        with self.assertRaisesRegex(ValueError, "capacity"):
            V["witness"](bad, V["RHS"])

    def test_path_and_dual_forgeries(self):
        cert = V["load_json"](V["HERE"] / "CERTIFICATE.json")
        rows = V["patterns"](cert)
        bad = copy.deepcopy(cert)
        bad["residue_paths"][13] = []
        with self.assertRaisesRegex(ValueError, "destination"):
            V["potential"](bad, rows)
        bad = copy.deepcopy(cert)
        bad["fractional_dual_constant"][0] += 1
        with self.assertRaisesRegex(ValueError, "rank identity"):
            V["patterns"](bad)

    def test_discrete_concavity_identity(self):
        # Independent exact reconstruction on every integer rank, f(r)=r^2.
        values = [Q(r * r) for r in range(49)]
        slope = values[48] - values[47]
        curvature = [
            2 * values[t] - values[t - 1] - values[t + 1] for t in range(1, 48)
        ]
        for r in range(49):
            rebuilt = r * slope + sum(
                curvature[t - 1] * min(r, t) for t in range(1, 48)
            )
            self.assertEqual(rebuilt, values[r])
        self.assertLess(min(V["hinges"](((1, -2), (2, 1)))), 0)

    def test_log_bounds_and_analytic_rejection(self):
        self.assertEqual(V["log_bounds"](Q(1)), (0, 0))
        lo, hi = V["log_bounds"](Q(2))
        self.assertTrue(Q(2, 3) < lo <= hi < Q(7, 10))
        self.assertLess(hi - lo, Q(1, 2**150))
        logs = {r: V["log_bounds"](Q(48, r)) for r in range(1, 49)}
        self.assertGreater(V["bernstein_lower"](((1, -74), (5, 74), (8, -37)), logs), 0)
        with self.assertRaisesRegex(ValueError, "positivity"):
            V["bernstein_lower"](((1, -2), (2, 1)), logs)
        with self.assertRaisesRegex(ValueError, "saving domain"):
            V["bernstein_lower"](((1, -74), (5, 74), (8, -37)), logs, Q(3, 20))

    def test_power_brackets_by_integer_oracle(self):
        for r in range(1, 49):
            for p in (Q(1), Q(1, 2), Q(2, 3), Q(17, 20)):
                lo, hi = V["rational_power"](r, p)
                self.assertLessEqual(lo**p.denominator, r**p.numerator)
                self.assertGreater(hi**p.denominator, r**p.numerator)
        for args in ((0, Q(1, 2)), (49, Q(1, 2)), (2, Q(1, 21))):
            with self.assertRaises(ValueError):
                V["rational_power"](*args)

    def test_positive_source_and_wrong_inventory(self):
        rhs = V["source_inventory"](V["sources"]())
        self.assertEqual(rhs, V["RHS"])
        cert = V["load_json"](V["HERE"] / "CERTIFICATE.json")
        bad_rhs = list(rhs)
        bad_rhs[-1] += 1
        with self.assertRaisesRegex(ValueError, "inventories"):
            V["witness"](cert, bad_rhs)


if __name__ == "__main__":
    unittest.main()
