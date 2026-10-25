#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite oracles and semantic rejection controls for the phase theorem."""

import copy
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))
CERT = json.loads((HERE / "CERTIFICATE.json").read_text())


class PhaseTests(unittest.TestCase):
    def test_separate_pattern_frontier(self):
        actual = set()
        for cap in (8, 16, 32, 48):
            frontier = {(0, (0,) * 5)}
            for j, width in enumerate((4, 5, 7, 8, 9)):
                nxt = set()
                for used, counts in frontier:
                    for n in range((cap - used) // width + 1):
                        new = list(counts)
                        new[j] = n
                        nxt.add((used + n * width, tuple(new)))
                frontier = nxt
            actual.update((cap, counts, cap - used) for used, counts in frontier)
        expected = {(c, ns, r) for c, ns, r, _a, _b in V["patterns"](CERT)}
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 1163)

    def test_both_attainments_and_inventory_rejection(self):
        profiles = CERT["integer_profiles"]
        for p in profiles:
            idle = V["inventory"](p, V["RHS"])
            self.assertEqual(sum(r * n for r, n in idle.items()), 237024)
        for i in range(2):
            bad = copy.deepcopy(profiles[i])
            bad[0]["multiplicity"] += 1
            with self.assertRaisesRegex(ValueError, "integer inventories"):
                V["inventory"](bad, V["RHS"])
        bad = copy.deepcopy(profiles[0])
        bad[0]["counts"][0] = 3
        with self.assertRaisesRegex(ValueError, "witness capacity"):
            V["inventory"](bad, V["RHS"])

    def test_paths_and_dual_rejections(self):
        rows = V["patterns"](CERT)
        V["potentials"](CERT, rows)
        for replacement in ([1163], [True], [0] * 4):
            bad = copy.deepcopy(CERT)
            bad["potential_options"][1][0] = replacement
            with self.assertRaises(ValueError):
                V["potentials"](bad, rows)
        bad = copy.deepcopy(CERT)
        bad["fractional_dual_power48"][0] += 1
        with self.assertRaisesRegex(ValueError, "dual rank identity"):
            V["patterns"](bad)

    def test_discrete_identity_independently(self):
        # Every integer-rank function with f(0)=0 has the stated hinge expansion.
        f = [0] + [(r * r + 3 * r) % 53 for r in range(1, 49)]
        for r in range(49):
            right = r * (f[48] - f[47])
            right += sum(
                min(r, t) * (2 * f[t] - f[t - 1] - f[t + 1]) for t in range(1, 48)
            )
            self.assertEqual(f[r], right)

    def test_root_brackets_and_phase_controls(self):
        for p in (Q(1, 2), Q(3, 5), Q(7, 12), Q(17, 20)):
            for r in (1, 5, 14, 17, 48):
                lo, hi = V["rational_power"](r, p)
                self.assertLessEqual(lo**p.denominator, r**p.numerator)
                self.assertGreater(hi**p.denominator, r**p.numerator)
        for r, p in ((0, Q(1, 2)), (49, Q(1, 2)), (2, Q(1, 21))):
            with self.assertRaises(ValueError):
                V["rational_power"](r, p)
        self.assertEqual(V["phase_checks"]()["old_profile_optimal_at"], "3/20")
        # A separate rational enclosure shows the strict square-root win.
        self.assertLess(
            Q(223607, 100000) + Q(374166, 100000) - Q(412310, 100000) - 2, -Q(7, 50)
        )
        for r, low, high in (
            (5, 223606, 223607),
            (14, 374165, 374166),
            (17, 412310, 412311),
        ):
            self.assertLess(Q(low, 100000) ** 2, r)
            self.assertGreater(Q(high, 100000) ** 2, r)

    def test_analytic_acceptance_and_rejection(self):
        logs = {r: V["log_bounds"](Q(48, r)) for r in range(1, 49)}
        self.assertEqual(V["certify"]((), logs)[0], "symbolic")
        self.assertEqual(V["certify"](((1, 2), (2, -1)), logs)[0], "concavity")
        # This has the required zero linear endpoint, but the wrong sign.
        self.assertIsNone(V["certify"](((1, -2), (2, 1)), logs)[0])
        with self.assertRaisesRegex(ValueError, "zero linear endpoint"):
            V["certify"](((1, 1),), logs)
        for q in (Q(0), Q(49)):
            with self.assertRaises(ValueError):
                V["log_bounds"](q)

    def test_actual_source_corruption_rejects(self):
        root = HERE.parents[1]
        pins = json.loads((HERE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory(prefix="t16-phase-control-") as name:
            target = Path(name)
            package = target / "research/t16-integer-phase"
            shutil.copytree(HERE, package)
            for row in pins["files"]:
                if row["usage"] == "input":
                    dest = target / row["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(root / row["path"], dest)
            bad = target / "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
            bad.write_bytes(bad.read_bytes() + b" ")
            run = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-O",
                    "-Werror",
                    "-B",
                    str(package / "verify.py"),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source drift", run.stderr)


if __name__ == "__main__":
    unittest.main()
