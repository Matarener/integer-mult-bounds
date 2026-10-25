#!/usr/bin/env python3
"""Independent exact controls for the valuation and decoder bridge.

Copyright 2026 thakrarsagar. Written with OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0

No predecessor executable is imported. The box oracle enumerates literal
sub-anchor label pairs in every order; the rational arithmetic is independent
of the finite Boolean classifiers.
"""

from fractions import Fraction
from itertools import combinations, combinations_with_replacement, permutations
import unittest

import verify


CORE_P = [(-1, -3, 0), (1, -1, -2), (3, 3, 3)]
CORE_Q = [(1, -3, 2), (3, -1, -2), (3, -1, 2)]


def valuation(value):
    """The exact 2-adic valuation of a nonzero rational, including negatives."""
    value = Fraction(value)
    if not value:
        raise ValueError("zero has no finite valuation")
    numerator, denominator = abs(value.numerator), value.denominator
    return ((numerator & -numerator).bit_length()
            - (denominator & -denominator).bit_length())


def product_matrix(left, right):
    return [[sum(Fraction(a) * Fraction(b) for a, b in zip(row, column))
             for column in right] for row in left]


def rational_rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows))
                      if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][column]
        rows[rank] = [value / divisor for value in rows[rank]]
        for i in range(rank + 1, len(rows)):
            factor = rows[i][column]
            rows[i] = [a - factor * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def anchors(left, right):
    """Discard zero-product columns, then normalize over the 2-adic integers."""
    minimum = {}
    for j in range(3):
        p_values = [valuation(row[j]) for row in left if row[j]]
        q_values = [valuation(row[j]) for row in right if row[j]]
        if p_values and q_values:
            minimum[j] = (min(p_values), min(q_values))
    if not minimum:
        raise ValueError("no nonzero product column")
    gamma = min(m + n for m, n in minimum.values())
    a = [sum(1 << j for j, (m, _) in minimum.items()
             if row[j] and valuation(row[j]) == m) for row in left]
    b = [sum(1 << j for j, (m, _) in minimum.items()
             if row[j] and valuation(row[j]) == gamma - m) for row in right]
    tau = [sum(bool(p[j] and q[j])
               and valuation(Fraction(p[j]) * q[j]) == gamma
               for j in range(3)) for p, q in zip(left, right)]
    return gamma, a, b, tau


def parity(left, right):
    return (left & right).bit_count() % 2


def bridge_holds(matrix, gamma, a, b):
    for t, row in enumerate(matrix):
        for s, value in enumerate(row):
            expected = int(bool(value) and valuation(value) == gamma)
            if parity(a[t], b[s]) != expected:
                return False
    return True


def zero_arcs(matrix):
    return {(i, j) for i, row in enumerate(matrix)
            for j, value in enumerate(row) if i != j and not value}


def witness_errors(a0, b0, arcs, witness):
    """Literal box inequalities, retaining each failed directed constraint."""
    kept, order = witness["kept"], witness["order"]
    a, b = witness["a"], witness["b"]
    if len(set(kept)) != len(kept) or sorted(kept) != sorted(order):
        return ["order"]
    errors = []
    for t in kept:
        if a[t] & ~a0[t] or b[t] & ~b0[t]:
            errors.append(("support", t))
        if parity(a[t], b[t]) != 1:
            errors.append(("diagonal", t))
    for earlier, later in combinations(order, 2):
        if (earlier, later) in arcs and parity(a[earlier], b[later]):
            errors.append((earlier, later))
    return errors


def submasks(mask):
    return [value for value in range(8) if value & ~mask == 0]


def box_witness(a0, b0, arcs, count):
    """Exhaust literal label pairs, pruning only already violated equations."""
    size = len(a0)
    choices = [[(a, b) for a in submasks(a0[t]) for b in submasks(b0[t])
                if parity(a, b)] for t in range(size)]

    def fill(order, labels):
        if len(labels) == count:
            a, b = [0] * size, [0] * size
            for t, (left, right) in zip(order, labels):
                a[t], b[t] = left, right
            return {"kept": list(order), "order": list(order), "a": a, "b": b}
        t = order[len(labels)]
        for a, b in choices[t]:
            if any((s, t) in arcs and parity(old_a, b)
                   for s, (old_a, _) in zip(order, labels)):
                continue
            result = fill(order, labels + [(a, b)])
            if result is not None:
                return result
        return None

    for order in permutations(range(size), count):
        result = fill(order, [])
        if result is not None:
            return result
    return None


def coherent_families():
    """Both orientations of each two-bit cap, with the all-equal overlap once."""
    families = set()
    for common in (3, 5, 6):
        for alphabet in (((common, common), (common, 7)),
                         ((common, common), (7, common))):
            families.update(combinations_with_replacement(alphabet, 5))
    return sorted(families)


class BridgeTests(unittest.TestCase):
    def test_exact_rational_valuation_and_zero_boundary(self):
        cases = {Fraction(-3, 8): -3, Fraction(12, 5): 2,
                 Fraction(-40, 9): 3, Fraction(7, 3): 0}
        for value, expected in cases.items():
            self.assertEqual(valuation(value), expected)
        with self.assertRaisesRegex(ValueError, "zero"):
            valuation(0)

    def test_rational_bridge_and_corrupted_anchor(self):
        scales = (Fraction(-3, 8), Fraction(5, 2), Fraction(-7, 4))
        p = [[Fraction(x) * scales[j] for j, x in enumerate(row)]
             for row in CORE_P]
        q = [[Fraction(x) / scales[j] for j, x in enumerate(row)]
             for row in CORE_Q]
        matrix = product_matrix(p, q)
        gamma, a, b, tau = anchors(p, q)
        self.assertEqual((gamma, a, b, tau), (0, [3, 3, 7], [3, 3, 3], [2] * 3))
        self.assertEqual(matrix, [[8, 0, 0], [0, 8, 0], [0, 0, 12]])
        self.assertTrue(bridge_holds(matrix, gamma, a, b))
        self.assertEqual(tau, [(x & y).bit_count() for x, y in zip(a, b)])
        damaged = a[:]
        damaged[0] ^= 1
        self.assertFalse(bridge_holds(matrix, gamma, damaged, b))

    def test_inactive_columns_and_negative_global_valuation(self):
        p = [[Fraction(1, 2), 7, 0], [Fraction(-3, 2), 9, 0]]
        q = [[Fraction(1, 4), 0, 5], [Fraction(-5, 4), 0, 6]]
        gamma, a, b, tau = anchors(p, q)
        self.assertEqual((gamma, a, b, tau), (-3, [1, 1], [1, 1], [1, 1]))
        self.assertTrue(bridge_holds(product_matrix(p, q), gamma, a, b))
        with self.assertRaisesRegex(ValueError, "product column"):
            anchors([[1, 0, 0]], [[0, 1, 0]])

    def test_all_missing_arc_witnesses(self):
        families = coherent_families()
        self.assertEqual(len(families), 33)
        checked = 0
        for family in families:
            a0, b0 = map(list, zip(*family))
            for x, y in permutations(range(5), 2):
                arcs = set(permutations(range(5), 2)) - {(x, y)}
                for z in set(range(5)) - {x, y}:
                    witness = verify.missing_arc_witness(a0, b0, x, y, z)
                    self.assertEqual(witness_errors(a0, b0, arcs, witness), [])
                    self.assertEqual(set(witness["kept"]), {x, y, z})
                    checked += 1
        self.assertEqual(checked, 1980)

    def test_direction_and_omitted_zero_constraint_controls(self):
        a0 = b0 = [3] * 5
        arcs = set(permutations(range(5), 2)) - {(0, 1)}
        witness = verify.missing_arc_witness(a0, b0, 0, 1, 2)
        self.assertEqual(witness_errors(a0, b0, arcs, witness), [])
        reversed_order = dict(witness, order=[1, 0, 2])
        self.assertEqual(witness_errors(a0, b0, arcs, reversed_order), [(1, 0)])
        self.assertEqual(witness_errors(a0, b0, arcs | {(0, 1)}, witness), [(0, 1)])
        # Omitting this single failed equation would accept the invalid witness.
        self.assertEqual(witness_errors(a0, b0, arcs - {(1, 0)}, reversed_order), [])

    def test_sharp_four_line_decoder(self):
        p, q = [CORE_P[0]] + CORE_P, [CORE_Q[0]] + CORE_Q
        matrix = product_matrix(p, q)
        self.assertEqual(matrix, [[8, 8, 0, 0], [8, 8, 0, 0],
                                  [0, 0, 8, 0], [0, 0, 0, 12]])
        self.assertEqual(rational_rank(matrix), 3)
        gamma, a, b, tau = anchors(p, q)
        self.assertEqual((gamma, a, b, tau), (0, [3, 3, 3, 7], [3] * 4, [2] * 4))
        self.assertTrue(bridge_holds(matrix, gamma, a, b))
        arcs = zero_arcs(matrix)
        witness = box_witness(a, b, arcs, 3)
        self.assertIsNotNone(witness)
        self.assertEqual(witness_errors(a, b, arcs, witness), [])
        self.assertIsNone(box_witness(a, b, arcs, 4))

    def test_three_line_boundary(self):
        matrix = product_matrix(CORE_P, CORE_Q)
        gamma, a, b, tau = anchors(CORE_P, CORE_Q)
        self.assertEqual(rational_rank(matrix), 3)
        self.assertEqual(tau, [2] * 3)
        self.assertTrue(bridge_holds(matrix, gamma, a, b))
        self.assertIsNotNone(box_witness(a, b, zero_arcs(matrix), 2))
        self.assertIsNone(box_witness(a, b, zero_arcs(matrix), 3))

    def test_tau_and_rank_hypotheses_are_necessary(self):
        p = [(2 ** i, 0, 0) for i in range(4)]
        q = [(1, 0, 0)] * 4
        matrix = product_matrix(p, q)
        gamma, a, b, tau = anchors(p, q)
        self.assertEqual(rational_rank(matrix), 1)
        self.assertEqual(tau, [1, 0, 0, 0])
        self.assertTrue(bridge_holds(matrix, gamma, a, b))
        self.assertIsNotNone(box_witness(a, b, zero_arcs(matrix), 1))
        self.assertIsNone(box_witness(a, b, zero_arcs(matrix), 2))
        # This abstract anchor/zero-arc object is outside the rank-three premise.
        diagonal = [[2 * int(i == j) for j in range(4)] for i in range(4)]
        self.assertEqual(rational_rank(diagonal), 4)
        self.assertTrue(bridge_holds(diagonal, 0, [3] * 4, [3] * 4))
        self.assertIsNotNone(box_witness([3] * 4, [3] * 4, zero_arcs(diagonal), 2))
        self.assertIsNone(box_witness([3] * 4, [3] * 4, zero_arcs(diagonal), 3))


if __name__ == "__main__":
    unittest.main()
