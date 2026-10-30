#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Small complete matrix/fibre oracles, not a substitute for real-source replay."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import types
import unittest

HERE = Path(__file__).resolve().parent
engine = types.ModuleType("tested_sheaf")
engine.__file__ = str(HERE / "sheaf.py")
exec(compile((HERE / "sheaf.py").read_bytes(), engine.__file__, "exec"), engine.__dict__)
ROUTES = [(2, 1), (1, 3), (3, 2)]
ROWS = [[1, 1, 0], [1, 0, 1]]


def full_operator(rows, routes, owners, omit_outputs=()):
    """Independent direct assembly: send each (owner,port) to its actual output.

    The later equation is multiplied by four, harmless over Q/Z for kernels.
    """
    width = len(owners) * len(routes)
    old = [[0] * width for _ in range(len(owners) * len(rows))]
    outputs = sorted({engine.compose(owner, route) for owner in owners for route in routes})
    outputs = [x for x in outputs if x not in omit_outputs]
    positions = {owner: i for i, owner in enumerate(outputs)}
    later = [[0] * width for _ in range(len(outputs) * len(rows))]
    for i, owner in enumerate(owners):
        for p, route in enumerate(routes):
            col = i * len(routes) + p
            target = engine.compose(owner, route)
            for k, row in enumerate(rows):
                old[i * len(rows) + k][col] = row[p]
                if target in positions:
                    later[positions[target] * len(rows) + k][col] = row[p]
    return old + later


def matvec(matrix, vector):
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)


class Tests(unittest.TestCase):
    def setUp(self):
        self.owners = engine.closure([engine.compose(ROUTES[0], ROUTES[1]), engine.compose(ROUTES[0], ROUTES[2])])
        self.matrix = full_operator(ROWS, ROUTES, self.owners)
        self.move = (1, -1, -1) * len(self.owners)

    def test_noncommuting_routes(self):
        self.assertEqual(len(self.owners), 3)
        self.assertNotEqual(engine.compose(ROUTES[0], ROUTES[1]), engine.compose(ROUTES[1], ROUTES[0]))
        self.assertEqual(engine.coset_classes(ROUTES, set(self.owners)), [[0, 1, 2]])

    def test_complete_operator_kernel(self):
        self.assertEqual(engine.rank(self.matrix), 8)
        self.assertEqual(matvec(self.matrix, self.move), (0,) * len(self.matrix))
        echelon, pivots = engine.rref(self.matrix)
        self.assertEqual(len(pivots), 8)
        self.assertEqual(len(self.move) - len(pivots), 1)

    def test_every_proper_owner_subset(self):
        for bits in product((0, 1), repeat=3):
            subset = [g for b, g in zip(bits, self.owners) if b]
            if subset and len(subset) < 3:
                self.assertEqual(engine.rank(full_operator(ROWS, ROUTES, subset)), 3 * len(subset))

    def test_exact_nonnegative_fibres(self):
        fibres = {}
        for point in product((0, 1), repeat=9):
            fibres.setdefault(matvec(self.matrix, point), []).append(point)
        multiple = 0
        for points in fibres.values():
            if len(points) > 1:
                multiple += 1
            first = points[0]
            for point in points:
                t = point[0] - first[0]
                self.assertEqual(tuple(a + t * v for a, v in zip(first, self.move)), point)
        self.assertGreater(multiple, 0)

    def test_count_constraint(self):
        self.assertEqual(sum(self.move), -3)
        self.assertEqual(engine.rank(self.matrix + [[1] * 9]), 9)

    def test_wrong_sign_breaks_witness(self):
        wrong = (1, 1, -1) * 3
        self.assertNotEqual(matvec(self.matrix, wrong), (0,) * len(self.matrix))

    def test_omitting_later_constraints_is_unsafe(self):
        old_only = self.matrix[:6]
        self.assertEqual(engine.rank(old_only), 6)
        self.assertLess(engine.rank(old_only), engine.rank(self.matrix))

    def test_wrong_port_permutation(self):
        changed = list(ROUTES)
        changed[0], changed[1] = changed[1], changed[0]
        matrix = full_operator(ROWS, changed, self.owners)
        # Source equality alone cannot detect a route change on a constant
        # global mode. An impulse response does detect it.
        impulse = (1, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertNotEqual(matvec(matrix, impulse), matvec(self.matrix, impulse))


if __name__ == "__main__":
    unittest.main()
