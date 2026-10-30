#!/usr/bin/env python3
"""Pi P_enc Pi does not match the #3954 adjacent helper contract, and no
nonnegative price of that slot exchange makes the published gate favorable.

The arithmetic is PROOF.md. Charts are Gaussian-integer eigenvalues. The
helper coordinate is an explicit direct sum with the literal-slot encoding.
"""

from __future__ import annotations

M = 4
DIM = 1 << M
ONE = (1, 0)
I_UNIT = (0, 1)
ZERO = (0, 0)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_P104_LITERAL_HELPER_GATE " + message)


def parity(u: int, z: int) -> int:
    return (u & z).bit_count() & 1


def mul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def inv_unit(value):
    norm = value[0] * value[0] + value[1] * value[1]
    require(norm == 1, "chart value is a Gaussian unit")
    return (value[0], -value[1])


def c_eig(u: int, z: int):
    """C_u on character z. Equals 1 when u·z is even and i when u·z is odd."""
    return ONE if parity(u, z) == 0 else I_UNIT


def gate():
    """Pinned #3954 scaffold integers. s is an added nonnegative rank-mass."""
    n = 104
    helpers_per_fiber = 72
    m = 81
    ports_n = n - 8
    data_lines = n * n
    helper_roles = 2 * n * helpers_per_fiber
    roles = 2 * data_lines + helper_roles
    calls = 2 * n
    local_mass = 2576
    local_progress = 2312
    progress = m * roles - data_lines
    remaining = progress - calls * local_progress
    lower = calls * local_mass + remaining
    capacity = m * roles
    return {
        "n": n,
        "ports_n": ports_n,
        "data_lines": data_lines,
        "helper_roles": helper_roles,
        "roles": roles,
        "calls": calls,
        "progress": progress,
        "remaining": remaining,
        "lower": lower,
        "capacity": capacity,
        "excess": lower - capacity,
        "helper_progress": m * helper_roles,
        "local_mass": local_mass,
        "local_progress": local_progress,
    }


def favorable(added_rank_mass: int) -> bool:
    """True only for a nonnegative price that lands strictly under capacity."""
    if added_rank_mass < 0:
        return False
    numbers = gate()
    return numbers["lower"] + added_rank_mass < numbers["capacity"]


# --- rational block arithmetic for the literal slot plus one helper ---

from fractions import Fraction


def fr(value):
    return value if isinstance(value, Fraction) else Fraction(value)


def zeros(rows, cols):
    return [[fr(0) for _ in range(cols)] for _ in range(rows)]


def eye(n):
    return [[fr(int(i == j)) for j in range(n)] for i in range(n)]


def diag(values):
    matrix = zeros(len(values), len(values))
    for index, value in enumerate(values):
        matrix[index][index] = fr(value)
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


def matmul(left, right):
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


def inverse(matrix):
    n = len(matrix)
    augmented = [row[:] + eye(n)[i] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next(row for row in range(col, n) if augmented[row][col] != 0)
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


def direct_sum(data, helper):
    """Place a scalar helper block on the diagonal after the data operator."""
    n = len(data)
    out = zeros(n + 1, n + 1)
    for i in range(n):
        for j in range(n):
            out[i][j] = data[i][j]
    out[n][n] = fr(helper)
    return out


def check_charts():
    """Exit charts (C_0, C_u^{-1}) equal entrance charts (C_u, C_0) only for u = 0."""
    degenerate = 0
    mismatched = 0
    for u in range(DIM):
        for z in range(DIM):
            exit_first = c_eig(0, z)
            exit_second = inv_unit(c_eig(u, z))
            entrance_first = c_eig(u, z)
            entrance_second = c_eig(0, z)
            same = exit_first == entrance_first and exit_second == entrance_second
            if u == 0:
                require(same, "degenerate line must match both banks")
            elif not same:
                mismatched += 1
                # The first bank is i against 1 on every odd character.
                if parity(u, z) == 1:
                    require(exit_first == ONE and entrance_first == I_UNIT,
                            "odd character separates F from T")
        if u == 0:
            degenerate += 1
            for v in range(1, DIM):
                for z in range(DIM):
                    if parity(v, z) == 1:
                        require(c_eig(v, z) != c_eig(0, z),
                                "a nonzero next address misses the degenerate exit")
    require(degenerate == 1, "one zero address")
    # Every nonzero u fails on its 8 odd characters, two banks not required.
    require(mismatched == (DIM - 1) * (DIM // 2), "every nonzero address mismatches")


def check_helper_extension():
    """One J port, one N port, one helper. Pi swaps only the N slots."""
    mask = [0, 1]
    t_values = diag([4, 2])
    data = eye(2)
    h = diag(mask)
    n = 2
    j0 = sub(eye(n), h)
    k = inverse(t_values)
    p = blocks(eye(n), zeros(n, n), k, eye(n))
    l = blocks(data, matmul(h, t_values), zeros(n, n), eye(n))
    pi = blocks(j0, h, h, j0)
    encoded = matmul(pi, l)
    require(matmul(pi, pi) == eye(2 * n), "Pi is an involution on the data slots")
    # Pi moves the single N coordinate and fixes the J coordinate.
    require(pi[0][0] == 1 and pi[0][1] == 0, "J slot stays in the first bank")
    require(pi[1][3] == 1 and pi[3][1] == 1, "N slot is the swapped coordinate")
    p_enc = matmul(matmul(l, p), inverse(l))
    p_literal = matmul(matmul(pi, p_enc), pi)
    require(matmul(p_literal, encoded) == matmul(encoded, p), "literal conjugation on data")
    require(matmul(p, encoded) != matmul(encoded, p), "old P still fails on the literal slots")

    full_correction = direct_sum(p_literal, 1)
    full_encoding = direct_sum(encoded, 1)
    full_old = direct_sum(p, 1)
    # P_literal A_T = A_T P, so the helper extension satisfies the same on data
    # and acts as the identity on the helper. It does not commute with A_T.
    require(
        matmul(full_correction, full_encoding) == matmul(full_encoding, full_old),
        "identity helper preserves the literal intertwining",
    )
    require(
        matmul(full_old, full_encoding) != matmul(full_encoding, full_old),
        "old P still fails after the helper is adjoined",
    )
    helper = [fr(0), fr(0), fr(0), fr(0), fr(1)]
    image = [
        sum(full_correction[i][j] * helper[j] for j in range(5))
        for i in range(5)
    ]
    require(image == helper, "helper basis vector is fixed")
    data_only = [fr(3), fr(5), fr(7), fr(11), fr(0)]
    data_image = [
        sum(full_correction[i][j] * data_only[j] for j in range(5))
        for i in range(5)
    ]
    require(data_image[4] == 0, "a data vector gains no helper component")
    # The extension's helper progress on this coordinate is zero.
    require(full_correction[4][4] == 1 and all(full_correction[4][j] == 0 for j in range(4)),
            "helper row is the identity row")


def check_gate():
    numbers = gate()
    require(numbers["ports_n"] == 96, "N-port count")
    require(numbers["data_lines"] == 10816, "data lines")
    require(numbers["helper_roles"] == 14976, "helper roles")
    require(numbers["roles"] == 36608, "role count")
    require(numbers["progress"] == 2954432, "persistent progress")
    require(numbers["remaining"] == 2473536, "progress after local calls")
    require(numbers["lower"] == 3009344, "favorable lower mass")
    require(numbers["capacity"] == 2965248, "capacity")
    require(numbers["excess"] == 44096, "zero-price excess")
    require(numbers["helper_progress"] == 1213056, "helper progress demanded by 81 per role")
    require(not favorable(0), "zero price is already over capacity")
    require(not favorable(96), "charging the N-port support does not help")
    require(not favorable(-44096), "a negative price is outside the contract")
    # The raw excess formula still sees the cancelled integer, and rejects it.
    require(numbers["excess"] + (-44096) == 0, "arithmetic control for the boundary price")
    require(numbers["lower"] - numbers["capacity"] == numbers["excess"], "excess identity")


def main():
    check_charts()
    check_helper_extension()
    check_gate()
    numbers = gate()
    print(
        "PASS_P104_LITERAL_HELPER_GATE "
        f"charts=F2^{M} nonzero_mismatch=true "
        f"helper_extension=identity helper_progress={numbers['helper_progress']} "
        f"excess0={numbers['excess']} ports_n={numbers['ports_n']} "
        "nonnegative_price=unfavorable no_new_kappa"
    )


if __name__ == "__main__":
    main()
