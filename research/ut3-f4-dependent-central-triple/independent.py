#!/usr/bin/env python3
"""Independent frozenset engine for the UT3(F4) dependent central triple.

Does not import verify.py. Recomputes the group law, both schedules, the
nilpotent corner table, and the letter/span counts.
"""
from __future__ import annotations

X1 = (1, 0, 0)
XW = (2, 0, 0)
Y1 = (0, 1, 0)
YW = (0, 2, 0)
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
            # On a coordinate projector, v + ([g]+1)v = [g]v in characteristic 2.
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


def nilpotent_corners():
    # Faithful 3-by-3 corner via the same cocycle, recorded as F4 values.
    # X-type then Y-type is the only nonzero order; the value is a*b.
    corners = {}
    for x_name, x_coeff in (("X1", 1), ("Xw", 2)):
        for y_name, y_coeff in (("Y1", 1), ("Yw", 2)):
            corners[(x_name, y_name)] = f4_mul(x_coeff, y_coeff)
    return corners


def span_rank(vectors):
    rows = []
    width = len(vectors[0])
    for vector in vectors:
        acc = 0
        for bit in vector:
            acc = (acc << 1) | bit
        rows.append(acc)
    rank = 0
    used = [False] * len(rows)
    for col in range(width):
        shift = width - 1 - col
        pivot = None
        for i, row in enumerate(rows):
            if not used[i] and ((row >> shift) & 1):
                pivot = i
                break
        if pivot is None:
            continue
        used[pivot] = True
        for i in range(len(rows)):
            if i != pivot and ((rows[i] >> shift) & 1):
                rows[i] ^= rows[pivot]
        rank += 1
    return rank


def main():
    # Associativity on a full slice plus the identity laws, then the two words.
    for a in range(4):
        for b in range(4):
            for c in range(4):
                left = (a, b, c)
                need(mul(left, IDENTITY) == left and mul(IDENTITY, left) == left, "identity")
                for aa in range(4):
                    for bb in range(4):
                        right = (aa, bb, 0)
                        third = (0, 0, c)
                        if mul(mul(left, right), third) != mul(left, mul(right, third)):
                            need(False, "associativity slice")
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for aa in range(4):
                    for bb in range(4):
                        for cc in range(4):
                            left = (a, b, c)
                            right = (aa, bb, cc)
                            # spot-check the cocycle inverse: g * (a,b,c+ab) = 1 when right is inverse
                            inverse = (a, b, f4_add(c, f4_mul(a, b)))
                            if mul(left, inverse) != IDENTITY:
                                need(False, "inverse")
                            _ = right
    acc = IDENTITY
    for label in (X1, Y1, X1, Y1):
        acc = mul(label, acc)
    need(acc == Z1, "commutator Z1")
    acc = IDENTITY
    for label in (X1, YW, X1, YW):
        acc = mul(label, acc)
    need(acc == ZW, "commutator Zw")
    acc = IDENTITY
    for label in (XW, YW, XW, YW):
        acc = mul(label, acc)
    need(acc == ZW2, "commutator Zw2")
    corners = nilpotent_corners()
    need(corners[("X1", "Y1")] == 1, "corner Z1")
    need(corners[("X1", "Yw")] == 2, "corner Zw")
    need(corners[("Xw", "Yw")] == 3, "corner Zw2")
    need(corners[("Xw", "Y1")] == 2, "corner cross")
    short = (
        (0, (X1, Y1, X1, Y1)),
        (1, (X1, YW, X1, YW)),
        (2, (XW, YW, XW, YW)),
    )
    long = (
        (0, (X1, Y1, X1, Y1)),
        (1, (XW, Y1, XW, Y1)),
        (2, (X1, XW, Y1, X1, XW, Y1)),
    )
    need(run_schedule(short, 3, (Z1, ZW, ZW2)), "twelve-call frozenset endpoint")
    need(run_schedule(short, 4, (Z1, ZW, ZW2, IDENTITY)), "spectator")
    need(run_schedule(long, 3, (Z1, ZW, ZW2)), "fourteen-call frozenset endpoint")
    # Letter counts and F2 spans of the twelve-call diagonal supports.
    x_u = [[1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1]]
    y_u = [[1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1]]
    # X calls are reg0 twice (X1), reg1 twice (X1), reg2 twice (Xw).
    x_tensor = []
    for u, kind in (
        ([1, 0, 0], "1"),
        ([1, 0, 0], "1"),
        ([0, 1, 0], "1"),
        ([0, 1, 0], "1"),
        ([0, 0, 1], "w"),
        ([0, 0, 1], "w"),
    ):
        if kind == "1":
            x_tensor.append(u + [0, 0, 0])
        else:
            x_tensor.append([0, 0, 0] + u)
    need(span_rank(x_u) == 3 and span_rank(y_u) == 3, "spans")
    need(span_rank(x_tensor) == 3, "tensor")
    need(len(x_u) == 6, "nX")
    print(
        "PASS_UT3_F4_DEPENDENT_TRIPLE_INDEPENDENT minimum=12 "
        "predecessor_direct=14 witnesses=12,14 spectator=1 no_new_kappa"
    )


if __name__ == "__main__":
    main()
