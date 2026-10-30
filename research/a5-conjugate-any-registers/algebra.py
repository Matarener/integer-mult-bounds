#!/usr/bin/env python3
"""A5 conjugate 5-cycle alphabet and any-register obstruction helpers."""

from __future__ import annotations

from typing import Iterable

# 0-indexed permutations matching research/a5-conjugate-5cycle-seedd316f8.
IDENTITY = (0, 1, 2, 3, 4)
X = (1, 0, 3, 2, 4)  # (1 2)(3 4)
Y = (2, 1, 4, 3, 0)  # (1 3 5)
SELECTED_KAPPA = "0.001672660197076918"


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    """Return a after b (standard right-to-left permutation composition)."""
    return tuple(a[b[i]] for i in range(5))


def build_group() -> tuple[list[tuple[int, ...]], dict[tuple[int, ...], int], list[list[int]]]:
    seen = {IDENTITY}
    frontier = [IDENTITY]
    while frontier:
        current = frontier.pop()
        for generator in (X, Y):
            successor = compose(current, generator)
            if successor not in seen:
                seen.add(successor)
                frontier.append(successor)
    elements = sorted(seen)
    index = {element: i for i, element in enumerate(elements)}
    table = [[index[compose(left, right)] for right in elements] for left in elements]
    return elements, index, table


def ga_mul(a: int, b: int, table: list[list[int]]) -> int:
    out = 0
    aa = a
    while aa:
        abit = aa & -aa
        ai = abit.bit_length() - 1
        bb = b
        while bb:
            bbit = bb & -bb
            bi = bbit.bit_length() - 1
            out ^= 1 << table[ai][bi]
            bb ^= bbit
        aa ^= abit
    return out


def elem_mask(index: dict[tuple[int, ...], int], perm: tuple[int, ...]) -> int:
    return 1 << index[perm]


def subsequence_support(labels: Iterable[tuple[int, ...]]) -> set[tuple[int, ...]]:
    """Group elements that can appear in a length-|labels| expansion."""
    support = {IDENTITY}
    for label in labels:
        nxt: set[tuple[int, ...]] = set()
        for existing in support:
            nxt.add(existing)
            nxt.add(compose(label, existing))
        support = nxt
    return support


def mat_mul(a: tuple[int, ...], b: tuple[int, ...], roles: int) -> tuple[int, ...]:
    return tuple(
        sum(a[row * roles + k] * b[k * roles + col] for k in range(roles)) & 1
        for row in range(roles)
        for col in range(roles)
    )


def mat_add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x ^ y for x, y in zip(a, b))


def projector(roles: int, slot: int) -> tuple[int, ...]:
    out = [0] * (roles * roles)
    out[slot * roles + slot] = 1
    return tuple(out)


def is_rank_one_idempotent(matrix: tuple[int, ...], roles: int) -> bool:
    if mat_mul(matrix, matrix, roles) != matrix:
        return False
    nonzero_rows = []
    for row in range(roles):
        encoded = sum(matrix[row * roles + col] << col for col in range(roles))
        if encoded:
            nonzero_rows.append(encoded)
    return bool(nonzero_rows) and len(set(nonzero_rows)) == 1


def rank_f2(matrix: tuple[int, ...], roles: int) -> int:
    rows = [
        sum(matrix[row * roles + col] << col for col in range(roles))
        for row in range(roles)
    ]
    rank = 0
    basis: dict[int, int] = {}
    for value in rows:
        x = value
        while x:
            pivot = x.bit_length() - 1
            if pivot in basis:
                x ^= basis[pivot]
            else:
                basis[pivot] = x
                rank += 1
                break
    return rank


def apply_factor(
    state: tuple[int, ...],
    label_index: int,
    projector_bits: tuple[int, ...],
    roles: int,
    table: list[list[int]],
) -> tuple[int, ...]:
    """Apply D_N(g) on the right, matching the predecessor search engine."""
    q_products = [
        state[i] ^ _translate_right(state[i], label_index, table)
        for i in range(roles * roles)
    ]
    result = list(state)
    for row in range(roles):
        for col in range(roles):
            entry = state[row * roles + col]
            for inner in range(roles):
                if projector_bits[inner * roles + col]:
                    entry ^= q_products[row * roles + inner]
            result[row * roles + col] = entry
    return tuple(result)


def _translate_right(poly: int, group_element: int, table: list[list[int]]) -> int:
    result = 0
    remaining = poly
    while remaining:
        bit = remaining & -remaining
        left_element = bit.bit_length() - 1
        result ^= 1 << table[left_element][group_element]
        remaining ^= bit
    return result


def identity_state(roles: int, identity_index: int) -> tuple[int, ...]:
    state = [0] * (roles * roles)
    bit = 1 << identity_index
    for i in range(roles):
        state[i * roles + i] = bit
    return tuple(state)


def target_state(
    roles: int,
    xy_index: int,
    yx_index: int,
    identity_index: int,
) -> tuple[int, ...]:
    state = identity_state(roles, identity_index)
    items = list(state)
    items[0] = 1 << xy_index
    items[roles + 1] = 1 << yx_index
    return tuple(items)


def direct_word(
    roles: int,
    x_index: int,
    y_index: int,
    identity_index: int,
    table: list[list[int]],
) -> tuple[int, ...]:
    e00 = projector(roles, 0)
    e11 = projector(roles, 1)
    state = identity_state(roles, identity_index)
    for label, proj in ((x_index, e00), (y_index, e00), (y_index, e11), (x_index, e11)):
        state = apply_factor(state, label, proj, roles, table)
    return state
