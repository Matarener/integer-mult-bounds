#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact arithmetic calibrations and scientific failure controls for this audit."""
import copy
from fractions import Fraction as Q
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pooling_audit', HERE / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class ArithmeticControls(unittest.TestCase):
    def test_independent_algebraic_calibration(self):
        # These checks use polynomial identities, not another power routine.
        for rank in range(1, 73):
            lo, hi = V.price(rank, Q(1, 2))
            self.assertLessEqual(lo * lo * 73, rank * V.SCALE ** 2)
            self.assertGreaterEqual(hi * hi * 73, rank * V.SCALE ** 2)
        for rank in (1, 14, 27, 51, 72):
            for saving, exponent in ((Q(1, 3), 2), (Q(2, 3), 1)):
                lo, hi = V.price(rank, saving)
                target = rank ** exponent * V.SCALE ** 3
                self.assertLessEqual(lo ** 3 * 73 ** exponent, target)
                self.assertGreaterEqual(hi ** 3 * 73 ** exponent, target)
        # A bad enclosure is detectable by the same exact calibration.
        lo, hi = V.price(27, Q(1, 2))
        self.assertGreater((hi + 10 ** 30) ** 2 * 73, 27 * V.SCALE ** 2)

    def test_price_domain_and_rounding(self):
        for rank, saving in ((0, Q(1, 2)), (73, Q(1, 2)), (True, Q(1, 2)),
                             (1, 0), (1, 1), (1, -1)):
            with self.subTest(rank=rank, saving=saving), self.assertRaises(ValueError):
                V.price(rank, saving)
        for numerator in range(-20, 21):
            for denominator in range(1, 9):
                upper = V.ceil_div(numerator, denominator)
                self.assertLess((upper - 1) * denominator, numerator)
                self.assertLessEqual(numerator, upper * denominator)

    def test_small_exhaustive_partition_control(self):
        def partitions(mass, cap):
            if cap == 0:
                if mass == 0:
                    yield {}
                return
            for count in range(mass // cap + 1):
                for rest in partitions(mass - count * cap, cap - 1):
                    yield rest | ({cap: count} if count else {})
        count = 0
        for cap in range(2, 5):
            for mass in range(13):
                expected = V.optimum(mass, cap)
                lo_best, hi_best = V.moment({}, 1, 1, expected, Q(1, 10))
                for candidate in partitions(mass, cap):
                    V.validate(candidate, mass, cap)
                    count += 1
                    if candidate != expected:
                        lo, _ = V.moment({}, 1, 1, candidate, Q(1, 10))
                        self.assertGreater(lo, hi_best)
        self.assertGreater(count, 250)

    def test_histogram_failures(self):
        for hist, mass in (({52: 1}, 52), ({51: Q(1, 2)}, 51),
                           ({51: -1}, -51), ({True: 1}, 1),
                           ({51: True}, 51), ({51: 1}, 50), ({0: 1}, 0)):
            with self.subTest(hist=hist), self.assertRaises(ValueError):
                V.validate(hist, mass)
        # Scaling to an average can introduce fractional counts despite integer
        # total mass. Rejecting those averages would reject the relaxed object.
        with self.assertRaises(ValueError):
            V.validate({51: Q(4647, 144), 27: Q(1, 144)}, 1646)
        V.validate({51: 4647, 27: 1}, 237024)


class SourceAndSemanticControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = V.ROOT / 'research/complex-t16-rare-pattern-exchanges/data'
        cls.roles = json.loads(gzip.decompress((parent / 'OWNERS.json.gz').read_bytes()))
        cls.plan = json.loads((parent / 'PLAN.json').read_text())

    def test_actual_owner_ledger_and_mutants(self):
        V.owner_ledger(self.roles, self.plan)
        mutants = [self.roles[:-1]]
        for field, value in (('family', 14336), ('offset', 1), ('time', 143),
                             ('width', 74)):
            rows = [dict(self.roles[0], **{field: value})] + self.roles[1:]
            mutants.append(rows)
        for rows in mutants:
            with self.subTest(first=rows[0]), self.assertRaises(ValueError):
                V.owner_ledger(rows, self.plan)

    def test_source_corruption(self):
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'research/audit'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for row in manifest['files']:
                if row['usage'] == 'input':
                    target = root / row['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(V.ROOT / row['path'], target)
            with patch.object(V, 'ROOT', root), patch.object(V, 'HERE', package):
                V.authenticate()
                retained = package / 'sources/pr3729/RESULT.json'
                original = retained.read_bytes()
                retained.write_bytes(original + b' ')
                with self.assertRaisesRegex(ValueError, 'retained predecessor changed'):
                    V.authenticate()
                retained.write_bytes(original)
                source = root / 'certificates/selected-result.json'
                source.write_bytes(source.read_bytes() + b' ')
                with self.assertRaisesRegex(ValueError, 'source input changed'):
                    V.authenticate()

    def test_wrong_per_call_identification(self):
        local, n, w, mass = V.selected()
        pooled = V.optimum(mass)
        single = V.optimum(mass // n)
        repeated = {r: count * n for r, count in single.items()}
        saving = Q('0.001689')
        self.assertLess(V.moment(local, n, w, pooled, saving)[1], 1)
        self.assertGreater(V.moment(local, n, w, repeated, saving)[0], 1)
        self.assertNotEqual(pooled, repeated)
        # A missing call factor and a missing W normalization do not reproduce
        # either side of the source-bound decision.
        bad = V.moment(local, 1, w, repeated, saving)
        self.assertLess(bad[1], 1)
        bad = V.moment(local, n, 1, pooled, saving)
        self.assertGreater(bad[0], 1)

    def test_full_receipt(self):
        receipt = V.audit()
        self.assertEqual(json.loads(json.dumps(receipt)), json.loads((HERE / 'RESULT.json').read_text()))
        changed = copy.deepcopy(receipt)
        changed['pooled_histogram'][51] -= 1
        self.assertNotEqual(changed, receipt)


if __name__ == '__main__':
    unittest.main(verbosity=2)
