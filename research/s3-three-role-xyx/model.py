#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Shared S3 three-role longest Coxeter target model; need()-based admission."""
from __future__ import annotations

import itertools

ROLES = 3
GROUP_ORDER = 6
EXPECTED_IDEM = 28
EXPECTED_CALLS = 56
BITS = 6
NCELL = ROLES * ROLES
KAPPA = "0.001672660197076918"
DIRECT_LEN = 6
SHORT_DEPTH = 5


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_S3_THREE_ROLE_XYX: {message}")


def compose(p, q):
    """Permutation product p*q, applying q first."""
    return tuple(p[q[i]] for i in range(3))


def build_group():
    elements = tuple(itertools.permutations(range(3)))
    need(len(elements) == GROUP_ORDER, "S3 must have 6 elements")
    index = {g: i for i, g in enumerate(elements)}
    table = tuple(
        tuple(index[compose(a, b)] for b in elements) for a in elements
    )
    need(
        all(
            table[table[a][b]][c] == table[a][table[b][c]]
            for a in range(GROUP_ORDER)
            for b in range(GROUP_ORDER)
            for c in range(GROUP_ORDER)
        ),
        "group multiplication table is not associative",
    )
    return elements, index, table


ELEMENTS, GROUP_INDEX, GROUP_MUL = build_group()
E = GROUP_INDEX[(0, 1, 2)]
X = GROUP_INDEX[(1, 0, 2)]  # (1 2)
Y = GROUP_INDEX[(0, 2, 1)]  # (2 3)
XY = GROUP_MUL[X][Y]
YX = GROUP_MUL[Y][X]
XYX = GROUP_MUL[XY][X]
YXY = GROUP_MUL[YX][Y]
GENERATOR_IDS = (X, Y)
GENERATOR_NAMES = ("x", "y")


def rank_one_idempotents():
    """Rank-one idempotents N=u v^T in M3(F2): y^T x = 1 over F2."""
    return tuple(
        (u, v)
        for u in range(1, 1 << ROLES)
        for v in range(1, 1 << ROLES)
        if ((u & v).bit_count() & 1)
    )


IDEMPOTENTS = rank_one_idempotents()
need(len(IDEMPOTENTS) == EXPECTED_IDEM, "expected 28 rank-one idempotents")
CALLS = tuple((g, u, v) for g in GENERATOR_IDS for u, v in IDEMPOTENTS)
need(len(CALLS) == EXPECTED_CALLS, "expected 56 paid factors")
CALL_INDEX = {call: i for i, call in enumerate(CALLS)}


def right_permute_mask(mask: int, g: int) -> int:
    out = 0
    for a in range(GROUP_ORDER):
        if (mask >> a) & 1:
            out ^= 1 << GROUP_MUL[a][g]
    return out


PERMUTED_RIGHT = {
    lab: tuple(right_permute_mask(mask, lab) for mask in range(1 << GROUP_ORDER))
    for lab in GENERATOR_IDS
}


def pack(cells) -> int:
    state = 0
    for i, cell in enumerate(cells):
        state |= int(cell) << (BITS * i)
    return state


def unpack(state: int):
    return tuple((state >> (BITS * i)) & ((1 << BITS) - 1) for i in range(NCELL))


def identity_state() -> int:
    cells = [0] * NCELL
    one = 1 << E
    for i in range(ROLES):
        cells[i * ROLES + i] = one
    return pack(cells)


def target_state() -> int:
    """diag([xyx], [xyx], [e])."""
    cells = [0] * NCELL
    cells[0] = 1 << XYX
    cells[ROLES + 1] = 1 << XYX
    cells[2 * ROLES + 2] = 1 << E
    return pack(cells)


def step(state: int, call) -> int:
    """Right-multiply a 3x3 F2[S3] matrix by one paid factor D_N(g)."""
    g, u, v = call
    cells = list(unpack(state))
    p = PERMUTED_RIGHT[g]
    for row in range(ROLES):
        value = 0
        for middle in range(ROLES):
            if (u >> middle) & 1:
                value ^= cells[ROLES * row + middle]
        delta = value ^ p[value]
        for col in range(ROLES):
            if (v >> col) & 1:
                cells[ROLES * row + col] ^= delta
    return pack(cells)


def word_state(word) -> int:
    state = identity_state()
    for call in word:
        state = step(state, call)
    return state


def convolve(left: int, right: int) -> int:
    out = 0
    for a in range(GROUP_ORDER):
        if (left >> a) & 1:
            for b in range(GROUP_ORDER):
                if (right >> b) & 1:
                    out ^= 1 << GROUP_MUL[a][b]
    return out


def formal_matrix_product(word_indices):
    """Independent literal 3x3 matrix product with six-bit group coefficients."""
    out = [0] * NCELL
    one = 1 << E
    for i in range(ROLES):
        out[i * ROLES + i] = one
    for index in word_indices:
        g, u, v = CALLS[index]
        factor = [0] * NCELL
        for row in range(ROLES):
            for col in range(ROLES):
                cell = one if row == col else 0
                if ((u >> row) & 1) and ((v >> col) & 1):
                    cell ^= one ^ (1 << g)
                factor[ROLES * row + col] = cell
        nxt = [0] * NCELL
        for row in range(ROLES):
            for col in range(ROLES):
                value = 0
                for middle in range(ROLES):
                    value ^= convolve(
                        out[ROLES * row + middle], factor[ROLES * middle + col]
                    )
                nxt[ROLES * row + col] = value
        out = nxt
    return tuple(out)


def make_direct_word():
    """Separate geodesic xyx on roles 0 and 1; dirty role stays identity."""
    letters = (X, Y, X)
    word = [(lab, 1, 1) for lab in letters] + [(lab, 2, 2) for lab in letters]
    need(len(word) == DIRECT_LEN, "direct word length")
    need(all(call in CALL_INDEX for call in word), "direct calls admitted")
    return tuple(word)


def ball(start: int, depth: int):
    """All states within distance <= depth, with exact layer sizes."""
    found = {start: 0}
    frontier = [start]
    layers = [1]
    for dist in range(depth):
        nxt = []
        for state in frontier:
            for call in CALLS:
                image = step(state, call)
                if image not in found:
                    found[image] = dist + 1
                    nxt.append(image)
        frontier = nxt
        layers.append(len(nxt))
    return found, layers


def mitm_short_hits(identity: int, target: int):
    """
    Return whether any paid word of length <= SHORT_DEPTH reaches target.

    Because every paid factor is an involution, backward search uses the same
    generators. Every path of length L<=5 has its state at step min(2,L) inside
    ball(I,2) ∩ ball(T,3).
    """
    fwd, layers_fwd = ball(identity, 3)
    bwd, layers_bwd = ball(target, 3)
    near_i = {state for state, dist in fwd.items() if dist <= 2}
    near_t = set(bwd.keys())
    hits = near_i & near_t
    # Symmetric split for an independent cross-check of the same depth budget.
    near_i3 = set(fwd.keys())
    near_t2 = {state for state, dist in bwd.items() if dist <= 2}
    hits_sym = near_i3 & near_t2
    return {
        "layers_from_identity": layers_fwd,
        "layers_from_target": layers_bwd,
        "ball_i2": len(near_i),
        "ball_t3": len(near_t),
        "ball_i3": len(near_i3),
        "ball_t2": len(near_t2),
        "hits_i2_t3": len(hits),
        "hits_i3_t2": len(hits_sym),
        "short_witness": None if not hits and not hits_sym else "found",
    }


def state_digest(states) -> str:
    import hashlib

    h = hashlib.sha256()
    for state in sorted(states):
        h.update(int(state).to_bytes(8, "little", signed=False))
    return h.hexdigest()
