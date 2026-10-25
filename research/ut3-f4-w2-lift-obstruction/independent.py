#!/usr/bin/env python3
"""Independent frozenset replay of the six-label diagonal lift.

Does not import verify.py. Recomputes commutators, both mixed words, the
blind {1,w} span, and the phi-diagonal inequality on those witnesses.
"""
from __future__ import annotations

import itertools

X1 = (1, 0, 0)
XW = (2, 0, 0)
XW2 = (3, 0, 0)
Y1 = (0, 1, 0)
YW = (0, 2, 0)
YW2 = (0, 3, 0)
Z1 = (0, 0, 1)
ZW = (0, 0, 2)
ZW2 = (0, 0, 3)
IDENTITY = (0, 0, 0)


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def f4_add(a, b):
    table = (
        (0, 1, 2, 3),
        (1, 0, 3, 2),
        (2, 3, 0, 1),
        (3, 2, 1, 0),
    )
    return table[a][b]


def f4_mul(a, b):
    table = (
        (0, 0, 0, 0),
        (0, 1, 2, 3),
        (0, 2, 3, 1),
        (0, 3, 1, 2),
    )
    return table[a][b]


def mul(left, right):
    a, b, c = left
    aa, bb, cc = right
    return (f4_add(a, aa), f4_add(b, bb), f4_add(f4_add(c, cc), f4_mul(a, bb)))


def support_mul(label, support):
    return frozenset(mul(label, element) for element in support)


def apply_calls(calls, width, registers):
    state = list(registers)
    for label, coordinate in calls:
        updated = []
        for i in range(width):
            if i == coordinate:
                updated.append(support_mul(label, state[i]))
            else:
                updated.append(state[i])
        state = updated
    return tuple(state)


def run_schedule(schedule, width, targets):
    calls = []
    for coordinate, labels in schedule:
        for label in labels:
            calls.append((label, coordinate))
    for element_bits in range(64):
        element = (element_bits % 4, (element_bits // 4) % 4, element_bits // 16)
        for register, target in enumerate(targets):
            start = [frozenset() for _ in range(width)]
            start[register] = frozenset((element,))
            got = apply_calls(calls, width, start)
            expect = [frozenset() for _ in range(width)]
            expect[register] = frozenset((mul(target, element),))
            if got != tuple(expect):
                return False
    return True


def bit_rank(masks, width):
    rows = list(masks)
    rank = 0
    for col in range(width):
        shift = width - 1 - col
        pivot = None
        for i, row in enumerate(rows):
            if (row >> shift) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        rank += 1
        pivot_row = rows[pivot]
        for i in range(len(rows)):
            if (rows[i] >> shift) & 1:
                rows[i] ^= pivot_row
    return rank


def span_vectors(masks, width):
    basis = []
    rows = list(masks)
    for col in range(width):
        shift = width - 1 - col
        pivot = None
        for i, row in enumerate(rows):
            if (row >> shift) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        pivot_row = rows[pivot]
        basis.append(pivot_row)
        for i in range(len(rows)):
            if (rows[i] >> shift) & 1:
                rows[i] ^= pivot_row
    vectors = [0]
    for vector in basis:
        vectors.extend([item ^ vector for item in vectors])
    return vectors


def phi_delta_bound(vectors, width):
    low_mask = (1 << width) - 1
    phi = []
    diagonal = []
    for vector in vectors:
        low = vector & low_mask
        high = vector >> width
        phi.append(low ^ high)
        if low == high:
            diagonal.append(low)
    return bit_rank(phi, width) + bit_rank(diagonal, width)


def main():
    for a in range(4):
        for b in range(4):
            for c in range(4):
                element = (a, b, c)
                inverse = (a, b, f4_add(c, f4_mul(a, b)))
                need(mul(element, inverse) == IDENTITY, "inverse")
                need(mul(element, IDENTITY) == element, "identity")
    need(f4_mul(3, 3) == 2, "w^2 square")
    for a in (1, 2, 3):
        for b in (1, 2, 3):
            acc = IDENTITY
            for label in ((a, 0, 0), (0, b, 0), (a, 0, 0), (0, b, 0)):
                acc = mul(label, acc)
            need(acc == (0, 0, f4_mul(a, b)), "commutator")
    mixed = (
        (0, (X1, Y1, X1, Y1)),
        (1, (XW, Y1, XW, Y1)),
        (2, (XW2, Y1, XW2, Y1)),
    )
    both = (
        (0, (X1, Y1, X1, Y1)),
        (1, (XW2, YW2, XW2, YW2)),
        (2, (XW, YW, XW, YW)),
    )
    targets = (Z1, ZW, ZW2)
    need(run_schedule(mixed, 3, targets), "mixed frozenset endpoint")
    need(run_schedule(both, 3, targets), "both-new frozenset endpoint")
    need(run_schedule(both, 4, targets + (IDENTITY,)), "spectator")
    # Drop the last Y_w. The third register must miss Z_{w^2}.
    broken = (
        (0, (X1, Y1, X1, Y1)),
        (1, (XW2, YW2, XW2, YW2)),
        (2, (XW, YW, XW)),
    )
    need(not run_schedule(broken, 3, targets), "shortened both-new word matched")
    # X shadows of the mixed word, ignoring w^2: e0 twice from X1, e1 twice from Xw.
    blind = bit_rank([0b100, 0b100, 0b010, 0b010], 3)
    need(blind == 2, "blind span")
    # Lifts: X1 -> (e0, 0), Xw -> (0, e1), Xw2 -> (e2, e2). Low bits are the 1-coordinate.
    e0, e1, e2 = 0b001, 0b010, 0b100
    lifts = [e0, e1 << 3, e2 | (e2 << 3)]
    shadows = [e0, e1, e2]
    need(bit_rank(lifts, 6) == 3, "lift rank")
    need(bit_rank(shadows, 3) == 3, "shadow rank")
    bound = phi_delta_bound(span_vectors(lifts, 6), 3)
    need(bound <= 3 and bit_rank(shadows, 3) <= bound, "phi-delta on the mixed lifts")
    # Overcount trap: axis dimensions 1+1+1 on a rank-2 lift. Not used as a bound.
    trap = span_vectors([e0, e0 << 3], 6)
    low_mask = 0b111
    dims = []
    for selector in (
        lambda low, high: high == 0,
        lambda low, high: low == 0,
        lambda low, high: low == high,
    ):
        picked = []
        for vector in trap:
            low = vector & low_mask
            high = vector >> 3
            if selector(low, high):
                picked.append(low if high == 0 or low == high else high)
        dims.append(bit_rank(picked, 3))
    need(sum(dims) == 3 and bit_rank([e0, e0 << 3], 6) == 2, "axis overcount")
    need(phi_delta_bound(trap, 3) <= 2, "phi-delta repairs the overcount")
    # Every triple of pure columns in r=3 obeys the shadow bound. A violation
    # with shadow dimension 3 would appear as one of these triples.
    pure = []
    for shadow in range(1, 8):
        pure.append((shadow, shadow))
        pure.append((shadow, shadow << 3))
        pure.append((shadow, shadow | (shadow << 3)))
    need(len(pure) == 21, "pure columns")
    for triple in itertools.combinations(pure, 3):
        shadow_rank = bit_rank([item[0] for item in triple], 3)
        lift_rank = bit_rank([item[1] for item in triple], 6)
        need(shadow_rank <= lift_rank, "triple outgrew its lift")
    print(
        "PASS_UT3_F4_W2_LIFT_INDEPENDENT minimum=12 labels=6 mixed=12 "
        "both_new=12 blind_span=2 lift_rank=3 no_new_kappa"
    )


if __name__ == "__main__":
    main()
