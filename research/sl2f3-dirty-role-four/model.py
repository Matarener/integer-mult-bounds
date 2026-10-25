#!/usr/bin/env python3
"""Shared SL2(F3) four-role conjugate-triple model; need()-based admission."""
from __future__ import annotations

ROLES = 4
GROUP_ORDER = 24
EXPECTED_IDEM = 120
EXPECTED_CALLS = 480
KAPPA = "0.001672660197076918"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_SL2F3_DIRTY_ROLE_FOUR: {message}")


def mat2_mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(a[2 * r + k] * b[2 * k + c] for k in range(2)) % 3
        for r in range(2)
        for c in range(2)
    )


def build_group():
    elements = sorted(
        (a, b, c, d)
        for a in range(3)
        for b in range(3)
        for c in range(3)
        for d in range(3)
        if (a * d - b * c) % 3 == 1
    )
    need(len(elements) == GROUP_ORDER, "SL2(F3) must have 24 elements")
    index = {g: i for i, g in enumerate(elements)}
    identity = index[(1, 0, 0, 1)]
    table = tuple(
        tuple(index[mat2_mul(a, b)] for b in elements) for a in elements
    )
    inverses = tuple(
        next(
            j
            for j in range(GROUP_ORDER)
            if table[i][j] == identity and table[j][i] == identity
        )
        for i in range(GROUP_ORDER)
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
    return elements, index, identity, table, inverses


ELEMENTS, GROUP_INDEX, E, GROUP_MUL, GROUP_INV = build_group()
I2 = GROUP_INDEX[(0, 1, 2, 0)]
W = GROUP_INDEX[(0, 2, 1, 2)]
IW = GROUP_INV[W]
C = GROUP_MUL[GROUP_MUL[IW][I2]][W]
GENERATOR_IDS = (I2, GROUP_INV[I2], W, IW)
GENERATOR_NAMES = ("i", "i^-1", "w", "w^-1")
CALL_NAMES = {g: name for g, name in zip(GENERATOR_IDS, GENERATOR_NAMES)}


def group_power(g: int, n: int) -> int:
    out = E
    for _ in range(n):
        out = GROUP_MUL[out][g]
    return out


def right_translate(mask: int, g: int) -> int:
    out = 0
    while mask:
        bit = mask & -mask
        a = bit.bit_length() - 1
        out |= 1 << GROUP_MUL[a][g]
        mask ^= bit
    return out


def left_translate(mask: int, g: int) -> int:
    out = 0
    while mask:
        bit = mask & -mask
        a = bit.bit_length() - 1
        out |= 1 << GROUP_MUL[g][a]
        mask ^= bit
    return out


def identity_state() -> tuple[int, ...]:
    one = 1 << E
    return tuple(one if r == c else 0 for r in range(ROLES) for c in range(ROLES))


def right_call(state: tuple[int, ...], call: tuple[int, int, int]) -> tuple[int, ...]:
    g, x, y = call
    out = list(state)
    for r in range(ROLES):
        accumulated = 0
        for k in range(ROLES):
            if (x >> k) & 1:
                accumulated ^= state[ROLES * r + k]
        delta = accumulated ^ right_translate(accumulated, g)
        for c in range(ROLES):
            if (y >> c) & 1:
                out[ROLES * r + c] ^= delta
    return tuple(out)


def direct_gate(call: tuple[int, int, int]) -> tuple[int, ...]:
    g, x, y = call
    one = 1 << E
    out = []
    for r in range(ROLES):
        for c in range(ROLES):
            support = one if r == c else 0
            if ((x >> r) & 1) and ((y >> c) & 1):
                support ^= one ^ (1 << g)
            out.append(support)
    return tuple(out)


def convolution(a: int, b: int) -> int:
    out = 0
    aa = a
    while aa:
        abit = aa & -aa
        ga = abit.bit_length() - 1
        bb = b
        while bb:
            bbit = bb & -bb
            gb = bbit.bit_length() - 1
            out ^= 1 << GROUP_MUL[ga][gb]
            bb ^= bbit
        aa ^= abit
    return out


def formal_matrix_product(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * (ROLES * ROLES)
    for r in range(ROLES):
        for c in range(ROLES):
            value = 0
            for k in range(ROLES):
                value ^= convolution(a[ROLES * r + k], b[ROLES * k + c])
            out[ROLES * r + c] = value
    return tuple(out)


def word_state(calls: tuple[tuple[int, int, int], ...]) -> tuple[int, ...]:
    state = identity_state()
    for call in calls:
        state = right_call(state, call)
    return state


def target_state(diagonal: tuple[int, ...]) -> tuple[int, ...]:
    need(len(diagonal) == ROLES, "diagonal length")
    out = [0] * (ROLES * ROLES)
    for r, g in enumerate(diagonal):
        out[ROLES * r + r] = 1 << g
    return tuple(out)


def left_diagonal(state: tuple[int, ...], diagonal: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        left_translate(state[ROLES * r + c], diagonal[r])
        for r in range(ROLES)
        for c in range(ROLES)
    )


def make_calls() -> tuple[tuple[int, int, int], ...]:
    calls = []
    for g in GENERATOR_IDS:
        for x in range(1, 1 << ROLES):
            for y in range(1, 1 << ROLES):
                if (bin(x & y).count("1") & 1) == 1:
                    calls.append((g, x, y))
    need(len(calls) == EXPECTED_CALLS, f"expected {EXPECTED_CALLS} paid gates")
    need(len(calls) // 4 == EXPECTED_IDEM, f"expected {EXPECTED_IDEM} idempotents")
    return tuple(calls)


CALLS = make_calls()


def idempotent_name(x: int, y: int) -> str:
    def vec(v: int) -> str:
        return "".join(str((v >> k) & 1) for k in range(ROLES))

    return f"{vec(x)}*{vec(y)}^T"


def call_name(call: tuple[int, int, int]) -> str:
    g, x, y = call
    return f"D[{CALL_NAMES[g]};{idempotent_name(x, y)}]"


def make_direct_word(call_index: dict) -> tuple[int, ...]:
    def at(g: int, role: int) -> int:
        e = 1 << role
        return call_index[(g, e, e)]

    # Same five-call conjugate word on roles 0..2; dirty role 3 stays identity.
    return (
        at(I2, 0),
        at(W, 1),
        at(IW, 2),
        at(I2, 2),
        at(W, 2),
    )


def pair_state(a: int, b: int, gates: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    return right_call(gates[a], CALLS[b])


def search_through_four(
    target: tuple[int, ...],
    diagonal: tuple[int, ...],
    gates: tuple[tuple[int, ...], ...],
    pair_words: dict,
    call_inverse: tuple[int, ...],
):
    """Return a witness of length ≤4, or None if every such word misses."""
    one_words = {gates[i]: (i,) for i in range(len(CALLS))}
    if target == identity_state():
        return ()
    if target in one_words:
        return one_words[target]
    if target in pair_words:
        return pair_words[target]

    for _suffix_state, (a, b) in pair_words.items():
        inv_suffix = pair_state(call_inverse[b], call_inverse[a], gates)
        need_prefix = left_diagonal(inv_suffix, diagonal)
        if need_prefix in one_words:
            return one_words[need_prefix] + (a, b)

    for _suffix_state, (a, b) in pair_words.items():
        inv_suffix = pair_state(call_inverse[b], call_inverse[a], gates)
        need_prefix = left_diagonal(inv_suffix, diagonal)
        if need_prefix in pair_words:
            return pair_words[need_prefix] + (a, b)
    return None


def state_digest(states) -> str:
    import hashlib

    digest = hashlib.sha256()
    for state in sorted(states):
        for coefficient_support in state:
            digest.update(coefficient_support.to_bytes(3, "little"))
    return digest.hexdigest()


TARGET_DIAGONAL = (I2, W, C, E)
