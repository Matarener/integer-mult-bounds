#!/usr/bin/env python3
"""Vector-form replay of the uniform-encoding gap. Does not import verify.py."""
from __future__ import annotations

ZERO = (0, 0)
ONE = (1, 0)
I = (0, 1)


def gadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def gsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def gmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def zvec():
    return tuple(ONE if (addr & 1) == 0 else (-1, 0) for addr in range(4))


def apply(matrix_cols, vector):
    """matrix_cols[j] is the image of basis vector j."""
    out = [ZERO] * 4
    for j, coef in enumerate(vector):
        if coef == ZERO:
            continue
        for i in range(4):
            out[i] = gadd(out[i], gmul(coef, matrix_cols[j][i]))
    return tuple(out)


def translation_cols(shift):
    cols = []
    for addr in range(4):
        image = [ZERO] * 4
        image[addr ^ shift] = ONE
        cols.append(tuple(image))
    return cols


def chart_cols(shift):
    """Columns of S_u = (1+i)I + (1-i) X_u."""
    translated = translation_cols(shift)
    cols = []
    for addr in range(4):
        image = [ZERO] * 4
        image[addr] = gadd(ONE, I)
        for i in range(4):
            image[i] = gadd(image[i], gmul(gsub(ONE, I), translated[addr][i]))
        cols.append(tuple(image))
    return cols


def character_cols():
    signs = zvec()
    return tuple(tuple(signs[i] if i == j else ZERO for i in range(4)) for j in range(4))


def matvec(cols, vector):
    return apply(cols, vector)


def commutator_on(cols_left, cols_right, vector):
    return tuple(
        gsub(a, b)
        for a, b in zip(
            matvec(cols_left, matvec(cols_right, vector)),
            matvec(cols_right, matvec(cols_left, vector)),
        )
    )


# State is (r_J, r_N, w_J, w_N), each an address 4-tuple.
BASIS = tuple(tuple(ONE if i == addr else ZERO for i in range(4)) for addr in range(4))
D = ((1, 1), (1, 2))


def scale_addr(coef, vector):
    return tuple(gmul((coef, 0), entry) for entry in vector)


def add_addr(left, right):
    return tuple(gadd(a, b) for a, b in zip(left, right))


def sub_addr(left, right):
    return tuple(gsub(a, b) for a, b in zip(left, right))


def zero_addr():
    return (ZERO, ZERO, ZERO, ZERO)


def uniform(cols, state):
    return tuple(matvec(cols, slot) for slot in state)


def physical(chart, state):
    r_j, r_n, w_j, w_n = state
    # r' = D r + (0, T w_N), w' = w.
    out_j = add_addr(scale_addr(D[0][0], r_j), scale_addr(D[0][1], r_n))
    out_n = add_addr(scale_addr(D[1][0], r_j), scale_addr(D[1][1], r_n))
    out_n = add_addr(out_n, matvec(chart, w_n))
    return (out_j, out_n, w_j, w_n)


def scalar(state):
    r_j, r_n, w_j, w_n = state
    out_j = add_addr(scale_addr(D[0][0], r_j), scale_addr(D[0][1], r_n))
    out_n = add_addr(
        add_addr(scale_addr(D[1][0], r_j), scale_addr(D[1][1], r_n)),
        w_n,
    )
    return (out_j, out_n, w_j, w_n)


def permute(state):
    r_j, r_n, w_j, w_n = state
    return (r_j, w_n, w_j, r_n)


def states_equal(left, right):
    return all(a == b for pair in zip(left, right) for a, b in zip(pair[0], pair[1]))


def basis_states():
    for slot in range(4):
        for addr in range(4):
            state = [zero_addr(), zero_addr(), zero_addr(), zero_addr()]
            state[slot] = BASIS[addr]
            yield tuple(state)


def difference(apply_encoding, cols):
    misses = 0
    for state in basis_states():
        left = uniform(cols, apply_encoding(state))
        right = apply_encoding(uniform(cols, state))
        if not states_equal(left, right):
            misses += 1
    return misses


def main():
    zeta = character_cols()
    chart_e1 = chart_cols(1)
    chart_e2 = chart_cols(2)
    if difference(scalar, zeta) != 0:
        raise ValueError("independent scalar encoding failed")
    physical_misses = difference(lambda state: physical(chart_e1, state), zeta)
    even_misses = difference(lambda state: physical(chart_e2, state), zeta)
    literal_misses = difference(lambda state: permute(physical(chart_e1, state)), zeta)
    self_misses = difference(lambda state: physical(chart_e1, state), chart_e1)
    if physical_misses == 0 or literal_misses == 0:
        raise ValueError("independent physical obstruction vanished")
    if even_misses != 0 or self_misses != 0:
        raise ValueError("independent commuting controls failed")
    column = commutator_on(zeta, chart_e1, BASIS[0])
    if column != (ZERO, (-2, 2), ZERO, ZERO):
        raise ValueError("independent address column changed: " + repr(column))
    print(
        "PASS_P104_UNIFORM_ENCODING_GAP_INDEPENDENT"
        f" scalar_misses=0 physical_basis_misses={physical_misses}"
        f" literal_basis_misses={literal_misses} even_misses=0 self_misses=0"
        " address_column0=0,-2+2i no_new_kappa"
    )


if __name__ == "__main__":
    main()
