#!/usr/bin/env python3
"""Separate dense rational check of the general rank lemma; no producer imports.

Prepared for commdata2338 with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
import itertools


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def zero(n):
    return [[F(0) for _ in range(n)] for _ in range(n)]


def subtract(a, b):
    return [[x-y for x, y in zip(r, s)] for r, s in zip(a, b)]


def multiply(a, b):
    cols = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in cols] for row in a]


def block(a, b, c, d):
    return [x+y for x, y in zip(a, b)] + [x+y for x, y in zip(c, d)]


def reduce_rows(matrix):
    a = [list(map(F, row)) for row in matrix]
    if not a:
        return a, 0
    count = 0
    for column in range(len(a[0])):
        pivot = next((r for r in range(count, len(a)) if a[r][column]), None)
        if pivot is None:
            continue
        a[count], a[pivot] = a[pivot], a[count]
        v = a[count][column]
        a[count] = [x/v for x in a[count]]
        for row in range(len(a)):
            if row != count and a[row][column]:
                v = a[row][column]
                a[row] = [x-v*y for x, y in zip(a[row], a[count])]
        count += 1
        if count == len(a):
            break
    return a, count


def rank(a):
    return reduce_rows(a)[1]


def inverse(a):
    n = len(a)
    red, _ = reduce_rows([row+unit for row, unit in zip(a, identity(n))])
    need([r[:n] for r in red] == identity(n), "invertible matrix required")
    return [r[n:] for r in red]


def maps(d, h, t):
    n = len(d)
    i, z = identity(n), zero(n)
    k = inverse(t)
    j = subtract(i, h)
    p = block(i, z, k, i)
    l = block(d, multiply(h, t), z, i)
    pi = block(j, h, h, j)
    return p, l, pi, multiply(pi, l)


def expected(d, h, t):
    n = len(d)
    i, z = identity(n), zero(n)
    k = inverse(t)
    j = subtract(i, h)
    return block(subtract(z, multiply(h, k)), z,
                 subtract(multiply(multiply(k, j), subtract(d, i)), h), multiply(k, h))


def exhaustive_small():
    total = 0
    histogram = {}
    # Every 3x3 binary D; invertibility of D is not needed for the defect lemma.
    for jdim in range(4):
        h = [[F(i == j and i >= jdim) for j in range(3)] for i in range(3)]
        t = identity(3)
        for i in range(2):
            if (i < jdim) == (i+1 < jdim):
                t[i][i+1] = F(1)
        i3 = identity(3)
        for entries in itertools.product((0, 1), repeat=9):
            d = [list(map(F, entries[3*i:3*i+3])) for i in range(3)]
            p, _l, _pi, a = maps(d, h, t)
            actual = subtract(multiply(p, a), multiply(a, p))
            need(actual == expected(d, h, t), "literal dense block identity")
            jj = [row[:jdim] for row in subtract(d, i3)[:jdim]]
            observed = rank(actual)
            need(observed == 2*(3-jdim)+rank(jj), "general exact rank")
            histogram[observed] = histogram.get(observed, 0) + 1
            total += 1
    need(total == 2048, "complete small domain")
    return histogram


def noncommuting_address_blocks():
    # Three ports, two-dimensional address payloads. T's port blocks do not
    # commute with one another; the proof must not diagonalize them together.
    small = [[1, 1, 2], [1, 0, 2], [2, 2, 3]]
    d = [[F(small[i//2][j//2] * (i % 2 == j % 2)) for j in range(6)] for i in range(6)]
    t = zero(6)
    blocks = ([[1, 1], [0, 1]], [[1, 0], [1, 1]], [[2, 0], [0, 1]])
    need(multiply(blocks[0], blocks[1]) != multiply(blocks[1], blocks[0]),
         "address blocks really do not commute")
    for port, matrix in enumerate(blocks):
        for i in range(2):
            for j in range(2):
                t[2*port+i][2*port+j] = F(matrix[i][j])
    h = [[F(i == j and i >= 2) for j in range(6)] for i in range(6)]
    need(multiply(t, h) == multiply(h, t), "H/T premise")
    need(multiply(t, d) != multiply(d, t), "D/T must not be commuted")
    p, l, _pi, a = maps(d, h, t)
    defect = subtract(multiply(p, a), multiply(a, p))
    need(defect == expected(d, h, t) and rank(defect) == 8, "operator-block rank")
    ordered = subtract(multiply(p, l), multiply(l, p))
    need(rank(ordered) == 8 and ordered != defect, "same rank does not bind slots")
    q = multiply(multiply(a, p), inverse(a))
    repair = multiply(q, inverse(p))
    need(multiply(repair, multiply(p, a)) == multiply(a, p), "dense full repair")
    need(rank(subtract(repair, identity(12))) == 8, "repair rank preserved")
    # Alter the pivot block: the old 2h specialization is now false.
    changed = [row[:] for row in d]
    changed[0][0] += 1
    p2, _l, _pi, a2 = maps(changed, h, t)
    altered = subtract(multiply(p2, a2), multiply(a2, p2))
    need(rank(altered) == 9, "pivot-block control must add one rank")
    return {"address_dimension": 2, "rank": 8, "changed_pivot_rank": 9}


def dropped_hypotheses():
    d = identity(2)
    h = [[F(0), F(0)], [F(0), F(1)]]
    t = [[F(1), F(1)], [F(0), F(1)]]
    p, _l, _pi, a = maps(d, h, t)
    defect = subtract(multiply(p, a), multiply(a, p))
    need(multiply(h, t) != multiply(t, h), "noncommuting premise control")
    need(defect != expected(d, h, t), "omitted H/T premise must fail")
    bad_h = [[F(0), F(0)], [F(0), F(2)]]
    _p, _l, pi, _a = maps(d, bad_h, identity(2))
    need(multiply(pi, pi) != identity(4), "nonprojector must fail literal swap")
    return 2


def main():
    histogram = exhaustive_small()
    operator_case = noncommuting_address_blocks()
    controls = dropped_hypotheses()
    print("PASS_P104_REPAIR_RANK_ALGEBRA cases=2048 operator_rank=8 "
          "changed_pivot_rank=9 hypothesis_controls=2")
    print("rank_histogram=" + repr(sorted(histogram.items())))
    need(operator_case["rank"] == 8 and controls == 2, "all corroboration groups")


if __name__ == "__main__":
    main()
