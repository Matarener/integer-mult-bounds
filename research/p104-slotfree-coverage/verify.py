#!/usr/bin/env python3
"""Slot-free P104 consumer screen. Apache-2.0. See README.md and PROOF.md.

The geometry rule is the one in research/p104-role-exchange-residue/verify.py.
This file does not import that module. It re-derives the ports, the tail
frames and the linear forms from the pinned geometry.json puncture.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GEOMETRY = REPO / "research/p104-role-exchange-residue/geometry.json"
GEOMETRY_SHA256 = "8212331ef435650469b6fca71448bcc2915a0cab46562acc41c5fc2a3dfa56c7"
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)
CHANNEL_MASS = 2368
TAIL_RANK = 208
IDLE = 72 * 832 - 9 * 2312
CAPACITY = 73 * 832
CALLS = 9


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load_geometry():
    raw = GEOMETRY.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == GEOMETRY_SHA256, "geometry.json hash")
    data = json.loads(raw)
    need(data["extraction"].startswith("section4_explicit_P104"), "geometry extraction")
    return data["F0"], data["C"]


def ports_from(f0, puncture_c):
    roots = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for tail in itertools.product((-1, 1), repeat=7):
        if sum(t < 0 for t in tail) % 2 == 0:
            roots.add((1,) + tail)
    removed = {tuple(r) for r in f0 + puncture_c}
    need(len(roots) == 120 and len(removed) == 16 and removed <= roots, "root universe")
    ports = sorted(roots - removed)
    need(len(ports) == 104, "port count")
    return ports


def matrices(ports):
    gram = [[sum(a * b for a, b in zip(r, s)) for s in ports] for r in ports]
    A = [[F(gram[i][j], 8) for j in range(104)] for i in range(104)]
    pivots = []
    for a, b in ((0, 2), (1, 3), (4, 6), (5, 7)):
        for sign in (-1, 1):
            root = [0] * 8
            root[a], root[b] = 2, 2 * sign
            pivots.append(ports.index(tuple(root)))
    pivots.sort()
    need(tuple(pivots) == PIVOTS, "pivot indices")
    nonpivots = [i for i in range(104) if i not in pivots]
    B = [[A[j][i] for i in nonpivots] for j in pivots]
    need(all(v in (F(-1, 2), 0, F(1, 2)) for row in B for v in row), "B alphabet")
    nnz = sum(v != 0 for row in B for v in row)
    need(nnz == 384, "B support")
    # B B^t on the eight pivots. The residue block form requires 12 I.
    for a in range(8):
        for b in range(8):
            dot = sum(B[a][k] * B[b][k] for k in range(96))
            need(dot == (12 if a == b else 0), "B B^t")
    need(all(any(v != 0 for v in row) for row in B), "B row support")
    need(all(any(B[j][a] != 0 for j in range(8)) for a in range(96)), "B column support")
    for a, i in enumerate(nonpivots):
        for b, k in enumerate(nonpivots):
            need(A[i][k] == sum(B[j][a] * B[j][b] for j in range(8)), "A_NN")
    for j in pivots:
        for k in pivots:
            need(A[j][k] == (1 if j == k else 0), "A_JJ")
    return A, pivots, nonpivots, B, nnz


def zero():
    return [F(0)] * 208


def add_into(target, source, sign):
    for i, value in enumerate(source):
        target[i] += sign * value


def tail(A, pivots, nonpivots, B):
    state = [zero() for _ in range(208)]
    for i in range(104):
        state[i][i] = 1
        state[104 + i][104 + i] = 1
        for k in range(104):
            state[104 + i][k] += A[i][k]
    frames = [9] * 104 + [8] * 104
    lifts = drops = 0
    for index in range(104):
        need(frames[104 + index] == 8, "lift entrance")
        frames[104 + index] = 9
        lifts += 1
    for a, i in enumerate(nonpivots):
        state[i] = [value * F(1, 2) for value in state[i]]
        for b, j in enumerate(pivots):
            if B[b][a]:
                sign = int(2 * B[b][a])
                add_into(state[j], state[i], sign)
                add_into(state[104 + j], state[i], -sign)
        state[i] = [value * 2 for value in state[i]]
    for b, j in enumerate(pivots):
        state[j] = [value * F(1, 2) for value in state[j]]
        for a, i in enumerate(nonpivots):
            if B[b][a]:
                add_into(state[i], state[j], -int(2 * B[b][a]))
        state[j] = [value * 2 for value in state[j]]
    for i in nonpivots:
        add_into(state[i], state[104 + i], 1)
        need(frames[i] == 9, "drop X_N")
        frames[i] = 8
        drops += 1
    for j in pivots:
        need(frames[104 + j] == 9, "drop Y_J")
        frames[104 + j] = 8
        drops += 1
    need(lifts == 104 and drops == 104, "conversion count")
    return state, frames, lifts + drops


def form_of(kind, index):
    row = zero()
    if kind == "x":
        row[index] = 1
    elif kind == "y":
        row[104 + index] = -1
    elif kind == "w":
        row[index] = 1
        row[104 + index] = 1
    else:
        raise SystemExit("unknown form")
    return row


def key(row):
    return tuple(row)


def q_form(pivots, nonpivots, B, b):
    row = zero()
    row[pivots[b]] = 1
    for a, i in enumerate(nonpivots):
        row[i] += B[b][a]
    return row


def v_form(pivots, nonpivots, B, a):
    # v = y_N + B^t q, and q = x_J + B x_N.
    row = zero()
    row[104 + nonpivots[a]] = 1
    for b, j in enumerate(pivots):
        coef = B[b][a]
        if coef:
            q = q_form(pivots, nonpivots, B, b)
            for t, value in enumerate(q):
                row[t] += coef * value
    return row


def screen(credit):
    numerator = CALLS * (CHANNEL_MASS + TAIL_RANK) + IDLE - CALLS * credit
    return F(numerator, CAPACITY)


def check_payload(state, frames, pivots, nonpivots, B):
    full = []
    hyper = []
    for i in range(104):
        (full if frames[i] == 9 else hyper).append(state[i])
        (full if frames[104 + i] == 9 else hyper).append(state[104 + i])
    need(len(full) == 104 and len(hyper) == 104, "frame split")
    need(sorted(frames[:208]) == [8] * 104 + [9] * 104, "dimension multiset")
    w_forms = [form_of("w", i) for i in range(104)]
    need(sorted(map(key, hyper)) == sorted(map(key, w_forms)), "hyperplane banks are w")
    for b, j in enumerate(pivots):
        need(state[j] == q_form(pivots, nonpivots, B, b), "q")
        need(frames[j] == 9 and frames[104 + j] == 8, "pivot frames")
        need(state[104 + j] == form_of("w", j), "pivot sum")
    for a, i in enumerate(nonpivots):
        need(state[104 + i] == v_form(pivots, nonpivots, B, a), "v_N")
        need(frames[i] == 8 and frames[104 + i] == 9, "nonpivot frames")
        need(state[i] == form_of("w", i), "nonpivot sum")
    x_forms = {key(form_of("x", i)) for i in range(104)}
    y_forms = {key(form_of("y", i)) for i in range(104)}
    full_keys = {key(row) for row in full}
    need(full_keys.isdisjoint(x_forms), "FULL payload is not x")
    need(full_keys.isdisjoint(y_forms), "FULL payload is not -y")
    need(full_keys != {key(row) for row in w_forms}, "FULL payload is not w")
    # One coordinate witness: y = e_0, x = 0. Port 0 is a pivot.
    # (q, v_N) = 0 while -y and w are not.
    witness = zero()
    witness[104] = 1
    q0 = sum(state[pivots[0]][t] * witness[t] for t in range(208))
    need(q0 == 0 and state[104] != form_of("y", 0), "pivot witness separates -y")


def check_screen():
    need(IDLE == 39096 and CAPACITY == 60736, "coverage constants")
    threshold = F(TAIL_RANK, 1) - F(328, 9)
    need(threshold == F(1544, 9), "credit threshold")
    need(screen(0) == F(7785, 7592) > 1, "uncredited screen")
    need(screen(threshold) == 1, "exact threshold")
    need(screen(threshold + F(1, 9)) < 1, "strict credit passes the comparison")
    need(screen(171) > 1 and screen(172) < 1, "integer credit")
    # The tail's own 208 conversions are already in k. A later adapter is not
    # required for this count, so omitting slot restoration does not lower it.
    need(TAIL_RANK == 104 + 104, "lifts plus drops")


def controls(pivots, nonpivots, B):
    # A zero B row would make that residual a pure source coordinate.
    fake = q_form(pivots, nonpivots, [[0] * 96 for _ in range(8)], 0)
    need(fake == form_of("x", pivots[0]), "control sees a pure coordinate")
    real = q_form(pivots, nonpivots, B, 0)
    need(real != form_of("x", pivots[0]), "real q is not that coordinate")
    need(sum(real[i] != 0 for i in range(104)) > 1, "real q support")
    # Forgetting the channel's A x term would make Y_N start as y_N and fail v.
    bare = zero()
    bare[104 + nonpivots[0]] = 1
    need(bare != v_form(pivots, nonpivots, B, 0), "control sees a bare y_N")


def main():
    f0, puncture = load_geometry()
    ports = ports_from(f0, puncture)
    A, pivots, nonpivots, B, nnz = matrices(ports)
    state, frames, conversions = tail(A, pivots, nonpivots, B)
    need(conversions == TAIL_RANK and nnz == 384, "tail invoice")
    check_payload(state, frames, pivots, nonpivots, B)
    check_screen()
    controls(pivots, nonpivots, B)
    print(
        "PASS_P104_SLOTFREE_COVERAGE "
        f"full=104 hyperplane=104 conversions={conversions} "
        f"M0={screen(0)} credit>{F(1544, 9)} "
        "integer_credit>=172 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
