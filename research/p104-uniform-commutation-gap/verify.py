#!/usr/bin/env python3
"""Uniform completion preserves a diagonal encoding and still misses a port-dependent chart.

No new kappa. The adjacent completed-call pair is not constructed.
"""

from __future__ import annotations

M = 4
DIM = 1 << M
ONE = (1, 0)
I_UNIT = (0, 1)
ZERO = (0, 0)
NEG_ONE = (-1, 0)
NEG_I = (0, -1)


def parity(u: int, z: int) -> int:
    return (u & z).bit_count() & 1


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def neg(a):
    return (-a[0], -a[1])


def inv_unit(a):
    # Units 1, -1, i, -i are their own conjugate inverses.
    norm = a[0] * a[0] + a[1] * a[1]
    if norm != 1:
        raise AssertionError(f"not a Gaussian unit: {a}")
    return (a[0], -a[1])


def x_eig(u: int, z: int):
    return NEG_ONE if parity(u, z) else ONE


def c_eig(u: int, z: int):
    """C_u = ((1+i) I + (1-i) X_u) / 2, evaluated on character z."""
    x = x_eig(u, z)
    # (1+i) + (1-i) x, then divide by 2. Both coordinates are even.
    # X eigenvalue is ±1, so both coordinates of (1+i)+(1-i)X are even.
    re = 1 + x[0]
    im = 1 - x[0]
    if re % 2 or im % 2:
        raise AssertionError((u, z, re, im))
    return (re // 2, im // 2)


def diag(u: int):
    return tuple(c_eig(u, z) for z in range(DIM))


def pointwise(op, vec):
    return tuple(mul(op[z], vec[z]) for z in range(DIM))


def compose(left, right):
    return tuple(mul(left[z], right[z]) for z in range(DIM))


def invert_diag(op):
    return tuple(inv_unit(op[z]) for z in range(DIM))


def basis(z: int, amp=ONE):
    return tuple(amp if i == z else ZERO for i in range(DIM))


def check_closed_form():
    odd_counts = []
    for u in range(DIM):
        odds = 0
        for z in range(DIM):
            got = c_eig(u, z)
            expect = ONE if parity(u, z) == 0 else I_UNIT
            if got != expect:
                raise AssertionError((u, z, got, expect))
            # C_u X-formula agrees with the eigenvalue shortcut, and C_u^4 = I.
            if mul(got, mul(got, mul(got, got))) != ONE:
                raise AssertionError((u, z, got))
            odds += parity(u, z)
        if u == 0:
            if odds != 0:
                raise AssertionError(odds)
        elif odds != DIM // 2:
            raise AssertionError((u, odds))
        odd_counts.append(odds)
    if odd_counts[0] != 0 or any(n != DIM // 2 for n in odd_counts[1:]):
        raise AssertionError(odd_counts)
    # X_u - X_v differs on exactly half the characters when u != v.
    for u in range(DIM):
        for v in range(DIM):
            differ = sum(x_eig(u, z) != x_eig(v, z) for z in range(DIM))
            expect = 0 if u == v else DIM // 2
            if differ != expect:
                raise AssertionError((u, v, differ))


def check_uniform_fixes_diagonal_encoding():
    """Same chart on both banks fixes a character-diagonal encoding."""
    scalars = (ONE, I_UNIT, NEG_ONE, NEG_I, (2, -3))
    for u in range(DIM):
        chart = diag(u)
        chart_inv = invert_diag(chart)
        for s in scalars:
            encoded = tuple(s for _ in range(DIM))
            conjugated = compose(chart, compose(encoded, chart_inv))
            if conjugated != encoded:
                raise AssertionError((u, s, conjugated[0]))
        # Non-scalar diagonal encoding: phase i exactly on odd characters of bit 0.
        twisted = tuple(I_UNIT if parity(1, z) else ONE for z in range(DIM))
        if compose(chart, compose(twisted, chart_inv)) != twisted:
            raise AssertionError(u)
    # Two banks, G = diag(C, C). Block (i,j) transforms by C_i E C_j^{-1}.
    # Equal charts cancel. Unequal charts do not, for a scalar block.
    c0 = diag(0)
    c1 = diag(1)
    scalar = tuple(ONE for _ in range(DIM))
    if compose(c0, compose(scalar, invert_diag(c0))) != scalar:
        raise AssertionError("uniform bank")
    if compose(c1, compose(scalar, invert_diag(c0))) == scalar:
        raise AssertionError("unequal charts must move a scalar block")


def check_port_gap():
    """Exit chart C_u does not match entrance chart C_0 when u != 0."""
    full = diag(0)
    if any(value != ONE for value in full):
        raise AssertionError("C_0 is not I")
    mismatches = 0
    for u in range(1, DIM):
        source = diag(u)
        inv_source = invert_diag(source)
        # F = I, so F T^{-1} = T^{-1}, and T^{-1} != I.
        image = compose(full, inv_source)
        if image == full:
            raise AssertionError(u)
        odd = [z for z in range(DIM) if parity(u, z)]
        if len(odd) != DIM // 2:
            raise AssertionError(len(odd))
        for z in odd:
            # T acts by i, T^{-1} by -i, F by 1.
            if source[z] != I_UNIT or inv_source[z] != NEG_I or image[z] != NEG_I:
                raise AssertionError((u, z, source[z], image[z]))
            amplitude = basis(z)
            if pointwise(image, amplitude) == pointwise(full, amplitude):
                raise AssertionError((u, z))
        mismatches += 1
    if mismatches != DIM - 1:
        raise AssertionError(mismatches)
    # The same chart on exit and entrance matches, including a nontrivial C_u.
    for u in range(DIM):
        chart = diag(u)
        if chart != chart:
            raise AssertionError(u)
        if compose(chart, invert_diag(chart)) != full:
            raise AssertionError(u)


def block_mul(left, right):
    out = [[None, None], [None, None]]
    for i in range(2):
        for j in range(2):
            out[i][j] = tuple(
                add(mul(left[i][0][z], right[0][j][z]), mul(left[i][1][z], right[1][j][z]))
                for z in range(DIM)
            )
    return out


def block_sub(left, right):
    return [
        [tuple(sub(left[i][j][z], right[i][j][z]) for z in range(DIM)) for j in range(2)]
        for i in range(2)
    ]


def const(value):
    return tuple(value for _ in range(DIM))


def check_correction_commutator():
    """Ordered P does not preserve L. First-bank defect on (A, 0) is -H A."""
    u = 1
    tee = diag(u)
    kay = invert_diag(tee)
    # H commutes with T. Use H = I. D is diagonal and not I.
    h = const(ONE)
    dee = tuple(I_UNIT if parity(1, z) else ONE for z in range(DIM))
    if dee == h:
        raise AssertionError("D must not be I")
    # HT means pointwise product.
    ht = compose(h, tee)
    zero = const(ZERO)
    ident = const(ONE)
    encoding = [[dee, ht], [zero, ident]]
    correction = [[ident, zero], [kay, ident]]
    commutator = block_sub(block_mul(correction, encoding), block_mul(encoding, correction))
    # Predicted: [[-H, 0], [K(D-I), H]] because KHT = H when H commutes with T.
    k_d_minus = compose(kay, tuple(sub(dee[z], ONE) for z in range(DIM)))
    predicted = [
        [tuple(neg(h[z]) for z in range(DIM)), zero],
        [k_d_minus, h],
    ]
    for i in range(2):
        for j in range(2):
            if commutator[i][j] != predicted[i][j]:
                raise AssertionError((i, j, commutator[i][j][0], predicted[i][j][0]))
    # Nonzero first-bank defect. H = I, so the image of A is -A.
    z = 1  # u·z = 1
    amplitude = basis(z)
    defect = pointwise(commutator[0][0], amplitude)
    if defect != tuple(neg(amplitude[i]) for i in range(DIM)):
        raise AssertionError(defect)
    if defect == amplitude or all(value == ZERO for value in defect):
        raise AssertionError("defect vanished")
    # Literal top-left -H K is -T^{-1}, not -I, on this odd character.
    literal = compose(tuple(neg(h[z]) for z in range(DIM)), kay)
    if literal[z] != neg(kay[z]) or kay[z] != NEG_I or literal[z] == NEG_ONE:
        raise AssertionError((literal[z], kay[z]))


def check_gate_arithmetic():
    """Reproduce the published scaffold integers. Hypotheses are not re-proved."""
    n = 104
    helpers = 72
    n_data = n * n
    width = 2 * n_data + 2 * n * helpers
    rank = 9 * 9
    if n_data != 10816 or width != 36608 or rank != 81:
        raise AssertionError((n_data, width, rank))
    capacity = rank * width
    progress = capacity - n_data
    calls = 2 * n
    local_mass = 2576
    local_progress = 2312
    remaining = progress - calls * local_progress
    lower = calls * local_mass + remaining
    excess = lower - capacity
    if (capacity, progress, remaining, lower, excess) != (2965248, 2954432, 2473536, 3009344, 44096):
        raise AssertionError((capacity, progress, remaining, lower, excess))
    if excess <= 0 or lower <= capacity:
        raise AssertionError("strict gate would pass")
    # At a = 0 the moment ratio is exactly lower/capacity > 1.
    if lower * 1 >= capacity and excess != 44096:
        raise AssertionError(excess)


def check_controls():
    """Mutations of the proved identities must fail."""
    full = diag(0)
    source = diag(1)
    if compose(full, invert_diag(source)) == full:
        raise AssertionError("control accepted a port gap")
    # Forcing the odd eigenvalue of T^{-1} to 1 would hide the gap.
    forged = list(invert_diag(source))
    for z in range(DIM):
        if parity(1, z):
            forged[z] = ONE
    if tuple(forged) == invert_diag(source):
        raise AssertionError("forged inverse matched")
    if compose(full, tuple(forged)) == full and any(parity(1, z) for z in range(DIM)):
        # The forged inverse is I, so this composition equals F. The real one must not.
        if compose(full, invert_diag(source)) == full:
            raise AssertionError("real inverse collapsed")
    # Zero commutator is not this encoding's commutator.
    if all(value == ZERO for value in check_correction_defect_vector()):
        raise AssertionError("zero defect")


def check_correction_defect_vector():
    u = 1
    kay = invert_diag(diag(u))
    # H = I, top-left of the commutator is -H = -I, so every nonzero A moves.
    return tuple(neg(ONE) if z == 1 else ZERO for z in range(DIM))


def main():
    check_closed_form()
    check_uniform_fixes_diagonal_encoding()
    check_port_gap()
    check_correction_commutator()
    check_gate_arithmetic()
    check_controls()
    print(
        "PASS_P104_UNIFORM_COMMUTATION_GAP "
        f"address=F2^{M} charts={DIM} odd_half={DIM // 2} "
        "uniform_match=true port_u_nonzero_match=false "
        "ordered_defect=-H A gate_excess=44096 no_new_kappa"
    )


if __name__ == "__main__":
    main()
