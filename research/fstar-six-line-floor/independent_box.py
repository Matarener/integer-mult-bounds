#!/usr/bin/env python3
"""Definition-level box oracle, independently written by Sagar Thakrar/Codex.

SPDX-License-Identifier: Apache-2.0

Fix the target labels first. For a proposed next source in the order, solve
its restricted three-variable affine system against all later targets.
No predecessor executable or enumeration routine is imported.
"""

from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import json


def dot(left, right):
    return (left & right).bit_count() & 1


def linear_solution(allowed, equations):
    """Solve dot(x, coefficients)=rhs with x a submask of allowed."""
    rows = [(coefficients & allowed) | (rhs << 3)
            for coefficients, rhs in equations]
    pivots = []
    cursor = 0
    for column in range(3):
        pivot = next((i for i in range(cursor, len(rows))
                      if rows[i] & (1 << column)), None)
        if pivot is None:
            continue
        rows[cursor], rows[pivot] = rows[pivot], rows[cursor]
        for i in range(len(rows)):
            if i != cursor and rows[i] & (1 << column):
                rows[i] ^= rows[cursor]
        pivots.append((column, cursor))
        cursor += 1
    if any(row == 8 for row in rows):
        return None
    return sum(1 << column for column, row in pivots if rows[row] & 8)


def _inputs(a0, b0, arcs):
    a0, b0 = tuple(a0), tuple(b0)
    if len(a0) != len(b0):
        raise ValueError("anchor lengths differ")
    if any(type(mask) is not int or not 0 <= mask < 8 for mask in a0 + b0):
        raise ValueError("anchors must be three-bit masks")
    arcs = frozenset(tuple(arc) for arc in arcs)
    if any(len(arc) != 2 or any(type(i) is not int or not 0 <= i < len(a0)
                               for i in arc) or arc[0] == arc[1] for arc in arcs):
        raise ValueError("zero arcs must be distinct valid line pairs")
    return a0, b0, arcs


def _target_completion(a0, targets, arcs, kept):
    """Every fixed-target source system is independent of earlier sources."""
    @lru_cache(None)
    def order_sources(remaining):
        if not remaining:
            return ()
        for source in remaining:
            later = tuple(i for i in remaining if i != source)
            equations = [(targets[source], 1)]
            equations.extend((targets[target], 0) for target in later
                             if (source, target) in arcs)
            label = linear_solution(a0[source], equations)
            if label is None:
                continue
            suffix = order_sources(later)
            if suffix is not None:
                return ((source, label),) + suffix
        return None

    chosen = order_sources(tuple(kept))
    if chosen is None:
        return None
    sources = [0] * len(a0)
    for line, label in chosen:
        sources[line] = label
    return {"a": sources, "b": list(targets), "kept": list(kept),
            "order": [line for line, _label in chosen]}


def kept_witness(a0, b0, arcs, kept=None):
    """Return a witness keeping every specified line, or None exactly."""
    a0, b0, arcs = _inputs(a0, b0, arcs)
    kept = tuple(range(len(a0))) if kept is None else tuple(kept)
    if len(set(kept)) != len(kept) or any(type(i) is not int or
                                        not 0 <= i < len(a0) for i in kept):
        raise ValueError("invalid kept lines")
    choices = [tuple(b for b in range(1, 8) if not b & ~b0[i] and b & a0[i])
               for i in kept]
    for labels in product(*choices):
        targets = [0] * len(a0)
        for line, label in zip(kept, labels):
            targets[line] = label
        witness = _target_completion(a0, targets, arcs, kept)
        if witness is not None:
            if not check_witness(a0, b0, arcs, witness):
                raise ValueError("constructed witness failed its definition")
            return witness
    return None


def find_kept(a0, b0, arcs, count=4):
    """Find any kept set of the requested cardinality, or None exactly."""
    a0, b0, arcs = _inputs(a0, b0, arcs)
    if type(count) is not int or not 0 <= count <= len(a0):
        raise ValueError("invalid kept count")
    for kept in combinations(range(len(a0)), count):
        witness = kept_witness(a0, b0, arcs, kept)
        if witness is not None:
            return witness
    return None


def maximum_box(a0, b0, arcs):
    a0, b0, arcs = _inputs(a0, b0, arcs)
    for count in range(len(a0), -1, -1):
        witness = find_kept(a0, b0, arcs, count)
        if witness is not None:
            return count, witness
    raise ValueError("empty kept set should always exist")


def check_witness(a0, b0, arcs, witness):
    """Literal forward-arc definition; nonkept labels do not matter."""
    a0, b0, arcs = _inputs(a0, b0, arcs)
    a, b = witness["a"], witness["b"]
    order, kept = witness["order"], witness["kept"]
    if len(a) != len(a0) or len(b) != len(b0) or len(set(kept)) != len(kept):
        return False
    if sorted(order) != sorted(kept) or any(not 0 <= i < len(a0) for i in kept):
        return False
    if any(type(a[i]) is not int or type(b[i]) is not int or
           not 0 <= a[i] < 8 or not 0 <= b[i] < 8 or
           a[i] & ~a0[i] or b[i] & ~b0[i] or dot(a[i], b[i]) != 1 for i in kept):
        return False
    return all((source, target) not in arcs or dot(a[source], b[target]) == 0
               for k, source in enumerate(order) for target in order[k + 1:])


def valuation(value):
    value = Fraction(value)
    if not value:
        raise ValueError("valuation of zero")
    numerator, denominator = abs(value.numerator), value.denominator
    return ((numerator & -numerator).bit_length() -
            (denominator & -denominator).bit_length())


def rational_rank(matrix):
    rows = [[Fraction(x) for x in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][column]
        rows[rank] = [x / divisor for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                multiplier = rows[i][column]
                rows[i] = [x - multiplier * y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def rational_data(P, Q):
    P, Q = [list(map(Fraction, row)) for row in P], [list(map(Fraction, row)) for row in Q]
    if not P or len(P) != len(Q) or any(len(row) != 3 for row in P + Q):
        raise ValueError("expected two equally sized nonempty three-column arrays")
    matrix = [[sum(x * y for x, y in zip(p, q)) for q in Q] for p in P]
    if any(not matrix[i][i] for i in range(len(P))):
        raise ValueError("zero diagonal")
    minima = []
    for column in range(3):
        left = [valuation(row[column]) for row in P if row[column]]
        right = [valuation(row[column]) for row in Q if row[column]]
        minima.append((min(left), min(right)) if left and right else None)
    gamma = min(left + right for pair in minima if pair for left, right in [pair])
    a0 = [sum(1 << j for j, pair in enumerate(minima) if pair and row[j]
              and valuation(row[j]) == pair[0]) for row in P]
    b0 = [sum(1 << j for j, pair in enumerate(minima) if pair and row[j]
              and valuation(row[j]) == gamma - pair[0]) for row in Q]
    arcs = [(i, j) for i in range(len(P)) for j in range(len(P))
            if i != j and not matrix[i][j]]
    if any(dot(a0[i], b0[j]) != bool(matrix[i][j] and valuation(matrix[i][j]) == gamma)
           for i in range(len(P)) for j in range(len(P))):
        raise ValueError("rational normalization violated the scope identity")
    return {"M": matrix, "rank": rational_rank(matrix), "gamma": gamma,
            "a0": a0, "b0": b0, "tau": [(a & b).bit_count() for a, b in zip(a0, b0)],
            "arcs": arcs}


def core_fixture():
    P = [(-1, -3, 0), (1, -1, -2), (3, 3, 3)]
    Q = [(1, -3, 2), (3, -1, -2), (3, -1, 2)]
    return ([row for row in P for _ in range(2)],
            [row for row in Q for _ in range(2)])


def fixture_certificate():
    data = rational_data(*core_fixture())
    value, witness = maximum_box(data["a0"], data["b0"], data["arcs"])
    expected = [[(8 if i < 4 else 12) if i // 2 == j // 2 else 0
                 for j in range(6)] for i in range(6)]
    if data["M"] != expected or data["rank"] != 3 or data["tau"] != [2] * 6 or value != 4:
        raise ValueError("sharp fixture failed")
    # Every five-set meets all three blocks; representatives have only zero
    # off-diagonal entries. Their forward constraints force triangular rank3.
    # Every target label is in the same two-dimensional space, a contradiction.
    upper_bound = all(len({i // 2 for i in subset}) == 3
                      for subset in combinations(range(6), 5))
    if not upper_bound or any(mask & ~3 for mask in data["b0"]):
        raise ValueError("analytic upper-bound preconditions failed")
    data["M"] = [[int(value) for value in row] for row in data["M"]]
    return {**data, "box": value, "witness": witness,
            "upper_bound": "every five-set contains a rank3 triangular minor; target span has rank2"}


if __name__ == "__main__":
    print(json.dumps(fixture_certificate(), sort_keys=True))
