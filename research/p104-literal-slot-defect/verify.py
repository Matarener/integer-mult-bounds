#!/usr/bin/env python3
"""Literal-slot defect of the old P104 correction.

The argument is the block multiplication in PROOF.md. These checks recompute
that multiplication over the rationals, including the cases where a hypothesis
is dropped.
"""

from fractions import Fraction


def F(value):
    return value if isinstance(value, Fraction) else Fraction(value)


def zeros(rows, cols):
    return [[F(0) for _ in range(cols)] for _ in range(rows)]


def eye(n):
    return [[F(int(i == j)) for j in range(n)] for i in range(n)]


def diag(values):
    matrix = zeros(len(values), len(values))
    for i, value in enumerate(values):
        matrix[i][i] = F(value)
    return matrix


def add(left, right):
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def sub(left, right):
    return [
        [left[i][j] - right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def scale(matrix, factor):
    factor = F(factor)
    return [[factor * entry for entry in row] for row in matrix]


def mul(left, right):
    rows, mid = len(left), len(left[0])
    cols = len(right[0])
    out = zeros(rows, cols)
    for i in range(rows):
        for k in range(mid):
            if left[i][k] == 0:
                continue
            for j in range(cols):
                out[i][j] += left[i][k] * right[k][j]
    return out


def blocks(top_left, top_right, bottom_left, bottom_right):
    n = len(top_left)
    out = zeros(2 * n, 2 * n)
    for i in range(n):
        for j in range(n):
            out[i][j] = top_left[i][j]
            out[i][n + j] = top_right[i][j]
            out[n + i][j] = bottom_left[i][j]
            out[n + i][n + j] = bottom_right[i][j]
    return out


def apply(matrix, vector):
    return [
        sum((matrix[i][j] * vector[j] for j in range(len(vector))), F(0))
        for i in range(len(matrix))
    ]


def inverse(matrix):
    n = len(matrix)
    augmented = [row[:] + eye(n)[i] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next(r for r in range(col, n) if augmented[r][col] != 0)
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        pivot_value = augmented[col][col]
        augmented[col] = [entry / pivot_value for entry in augmented[col]]
        for row in range(n):
            if row == col or augmented[row][col] == 0:
                continue
            factor = augmented[row][col]
            augmented[row] = [
                augmented[row][j] - factor * augmented[col][j] for j in range(2 * n)
            ]
    return [row[n:] for row in augmented]


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_P104_LITERAL_SLOT_DEFECT " + message)


def projection(mask):
    return diag(mask)


def commutator(left, right):
    return sub(mul(left, right), mul(right, left))


def assemble(h_mask, t_values, data):
    """Build P, L, Pi and A_T. t_values is a matrix."""
    h = projection(h_mask)
    n = len(h_mask)
    j0 = sub(eye(n), h)
    k = inverse(t_values)
    p = blocks(eye(n), zeros(n, n), k, eye(n))
    ht = mul(h, t_values)
    l = blocks(data, ht, zeros(n, n), eye(n))
    pi = blocks(j0, h, h, j0)
    return h, j0, k, p, l, pi, mul(pi, l)


def check_general_ordered(h, k, t_values, data, p, l):
    """P L - L P = [[-H T K, 0], [K(D-I), K H T]] with no commutation hypothesis."""
    n = len(h)
    expected = blocks(
        scale(mul(mul(h, t_values), k), -1),
        zeros(n, n),
        mul(k, sub(data, eye(n))),
        mul(mul(k, h), t_values),
    )
    require(commutator(p, l) == expected, "general ordered commutator")


def check_simplified(h, k, data, p, l, pi, encoded):
    n = len(h)
    j0 = sub(eye(n), h)
    ordered = blocks(scale(h, -1), zeros(n, n), mul(k, sub(data, eye(n))), h)
    require(commutator(p, l) == ordered, "simplified ordered commutator")
    literal = blocks(
        scale(mul(h, k), -1),
        zeros(n, n),
        sub(mul(mul(k, j0), sub(data, eye(n))), h),
        mul(k, h),
    )
    require(commutator(p, encoded) == literal, "literal-slot commutator")
    require(mul(pi, pi) == eye(2 * n), "Pi squared")
    encoded_correction = mul(mul(l, p), inverse(l))
    require(mul(encoded_correction, l) == mul(l, p), "ordered conjugation")
    literal_correction = mul(mul(pi, encoded_correction), pi)
    require(mul(literal_correction, encoded) == mul(encoded, p), "literal conjugation")
    require(commutator(p, encoded) != zeros(2 * n, 2 * n), "old P does not pass through A_T")


def n_port_indices(mask):
    return [i for i, bit in enumerate(mask) if bit]


def first_bank(commutator_matrix, amplitude):
    n = len(amplitude)
    image = apply(commutator_matrix, amplitude + [F(0)] * n)
    return image[:n]


def scalar_multiplier(h, k, p, encoded):
    """Return the common first-bank multiplier, or None when the N-ports disagree."""
    mask = [int(h[i][i]) for i in range(len(h))]
    indices = n_port_indices(mask)
    require(indices, "need an N-port")
    comm = commutator(p, encoded)
    multipliers = []
    for index in indices:
        amplitude = [F(int(i == index)) for i in range(len(h))]
        error = first_bank(comm, amplitude)
        column = [F(0)] * len(h)
        column[index] = F(1)
        require(error == apply(scale(k, -1), column), "first bank is -K on an N-port basis vector")
        # The complement of this basis vector is untouched.
        for other in range(len(h)):
            if other != index:
                require(error[other] == 0, "first-bank error stays on that port")
        multipliers.append(error[index])
    if len(set(multipliers)) != 1:
        return None
    factor = multipliers[0]
    # Every H-supported amplitude, not just basis vectors.
    amplitude = [F(0) for _ in range(len(h))]
    for index in indices:
        amplitude[index] = F(index + 2)
    error = first_bank(comm, amplitude)
    require(error == [factor * entry for entry in amplitude], "scalar extends linearly on the N-ports")
    # A J0 component is not multiplied by that same scalar.
    if any(bit == 0 for bit in mask):
        mixed = amplitude[:]
        mixed[mask.index(0)] = F(7)
        mixed_error = first_bank(comm, mixed)
        require(
            mixed_error != [factor * entry for entry in mixed],
            "scalar does not absorb a J0 component",
        )
        require(
            mixed_error == first_bank(comm, amplitude),
            "J0 component does not change the first-bank defect",
        )
    return factor


def main():
    # Distinct N-port scales. D does not commute with T.
    mask = [0, 0, 1, 1]
    t_values = diag([4, 5, 2, 3])
    data = [
        [F(1), F(1), F(0), F(0)],
        [F(0), F(1), F(0), F(0)],
        [F(0), F(0), F(1), F(1)],
        [F(0), F(0), F(0), F(1)],
    ]
    h, _j0, k, p, l, pi, encoded = assemble(mask, t_values, data)
    require(mul(data, t_values) != mul(t_values, data), "D is not forced to commute with T")
    check_general_ordered(h, k, t_values, data, p, l)
    check_simplified(h, k, data, p, l, pi, encoded)
    require(scalar_multiplier(h, k, p, encoded) is None, "distinct scales have no scalar")

    # Sharpness: one N-port scale. A scalar cancels the first bank on im H.
    constant = diag([4, 5, 2, 2])
    h2, _j2, k2, p2, l2, pi2, encoded2 = assemble(mask, constant, eye(4))
    check_general_ordered(h2, k2, constant, eye(4), p2, l2)
    check_simplified(h2, k2, eye(4), p2, l2, pi2, encoded2)
    factor = scalar_multiplier(h2, k2, p2, encoded2)
    require(factor == Fraction(-1, 2), "constant N-port scale is -1/T")

    # Dropping commutation keeps the unsimplified ordered identity and breaks the simplification.
    mixed = [[F(1), F(1)], [F(0), F(1)]]
    h3 = diag([0, 1])
    require(mul(h3, mixed) != mul(mixed, h3), "control T does not commute with H")
    k3 = inverse(mixed)
    n = 2
    p3 = blocks(eye(n), zeros(n, n), k3, eye(n))
    l3 = blocks(eye(n), mul(h3, mixed), zeros(n, n), eye(n))
    check_general_ordered(h3, k3, mixed, eye(n), p3, l3)
    simplified = blocks(scale(h3, -1), zeros(n, n), mul(k3, zeros(n, n)), h3)
    require(commutator(p3, l3) != simplified, "simplification needs HT = TH")

    # Dropping idempotence breaks Pi^2 = I. This H is not a coordinate projection.
    bad = diag([2, 0])
    j_bad = sub(eye(2), bad)
    pi_bad = blocks(j_bad, bad, bad, j_bad)
    require(mul(pi_bad, pi_bad) != eye(4), "Pi^2 needs a projection")

    # The ordered defect is -A, not -K A. They differ when a port scale is not 1.
    require(scale(h, -1) != scale(mul(h, k), -1), "literal defect is not the ordered defect")

    print(
        "PASS_P104_LITERAL_SLOT_DEFECT "
        "ordered=general literal=projection_and_commutation "
        "distinct_scales=no_scalar constant_scale=-1/2 "
        "pi_required=1 no_new_kappa"
    )


if __name__ == "__main__":
    main()
