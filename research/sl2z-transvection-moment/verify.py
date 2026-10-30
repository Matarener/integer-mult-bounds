#!/usr/bin/env python3
"""Exact elementary length and supplier moment for integer transvections.

The alphabet is {X^t, Y^t : t in Z, t != 0}, each letter one rank-1 child.
No new kappa is computed or claimed.
"""

from fractions import Fraction


def X(t):
    return ((1, t), (0, 1))


def Y(t):
    return ((1, 0), (t, 1))


def mul(a, b):
    return (
        (a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]),
        (a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]),
    )


def power(word, k):
    out = ((1, 0), (0, 1))
    step = ((1, 0), (0, 1))
    for factor in word:
        step = mul(step, factor)
    for _ in range(k):
        out = mul(out, step)
    return out


def sequence(limit):
    """Return u[0..limit], v[0..limit] for B^k = [[u_k, v_k], [v_k, u_{k-1}]]."""
    u = [1, 5]
    v = [0, 2]
    for k in range(2, limit + 1):
        u.append(6 * u[k - 1] - u[k - 2])
        v.append(2 * u[k - 1] + v[k - 1])
    return u, v


def b_matrix(u, v, k):
    return ((u[k], v[k]), (v[k], u[k - 1]))


def moment_strict(length, roles, exponent):
    """True when (length/roles) * 2^(exponent-1) < 1, for a rational exponent."""
    if not isinstance(exponent, Fraction):
        exponent = Fraction(exponent)
    if exponent < 0 or exponent > 1:
        raise ValueError("exponent outside [0, 1]")
    # length * 2^p < roles * 2^q, where exponent = p/q.
    p, q = exponent.numerator, exponent.denominator
    return length ** q * 2 ** p < roles ** q * 2 ** q


def xyx_formula(a, b, c):
    # X^a Y^b X^c = [[1+ab, a+c(1+ab)], [b, 1+bc]]
    return (
        (1 + a * b, a + c * (1 + a * b)),
        (b, 1 + b * c),
    )


def yxy_formula(a, b, c):
    # Y^a X^b Y^c = [[1+bc, b], [a+c(1+ab), 1+ab]]
    return (
        (1 + b * c, b),
        (a + c * (1 + a * b), 1 + a * b),
    )


def unit_bfs():
    """Shortest positive-or-inverse unit word for B. Returns the length, or None."""
    target = mul(X(1), mul(X(1), mul(Y(1), Y(1))))
    seen = {((1, 0), (0, 1)): 0}
    frontier = [((1, 0), (0, 1))]
    letters = (X(1), X(-1), Y(1), Y(-1))
    while frontier:
        current = frontier.pop(0)
        depth = seen[current]
        if current == target:
            return depth
        if depth == 4:
            continue
        for letter in letters:
            nxt = mul(current, letter)
            if nxt not in seen:
                seen[nxt] = depth + 1
                frontier.append(nxt)
    return None


def check_identities(limit):
    u, v = sequence(limit)
    base = mul(X(2), Y(2))
    if base != ((5, 2), (2, 1)):
        raise SystemExit("X^2 Y^2 is not B")
    # Cayley-Hamilton / the published square relation.
    square = mul(base, base)
    six = tuple(tuple(6 * entry for entry in row) for row in base)
    if square != (
        (six[0][0] - 1, six[0][1]),
        (six[1][0], six[1][1] - 1),
    ):
        raise SystemExit("B^2 != 6B - I")
    running = ((1, 0), (0, 1))
    for k in range(1, limit + 1):
        running = mul(running, base)
        if running != b_matrix(u, v, k):
            raise SystemExit(f"word (X^2 Y^2)^{k} missed the recurrence matrix")
        det = u[k] * u[k - 1] - v[k] * v[k]
        if det != 1:
            raise SystemExit(f"determinant drifted at k={k}")
        if u[k] != 2 * v[k] + u[k - 1]:
            raise SystemExit(f"quotient identity failed at k={k}")
        if v[k] != 2 * u[k - 1] + v[k - 1]:
            raise SystemExit(f"companion identity failed at k={k}")
        if k >= 1 and u[k] < 5 * u[k - 1]:
            raise SystemExit(f"growth u_k >= 5 u_{{k-1}} failed at k={k}")
    return u, v


def check_length(u, v, limit):
    for k in range(1, limit + 1):
        matrix = b_matrix(u, v, k)
        # Length 1: a transvection has a zero off-diagonal entry.
        if matrix[1][0] == 0 or matrix[0][1] == 0:
            raise SystemExit(f"B^{k} collapsed to one transvection")
        # Length 2: XY has bottom-right 1; YX has top-left 1.
        if k == 1:
            if matrix != mul(X(2), Y(2)):
                raise SystemExit("k=1 is not the length-2 word X^2 Y^2")
        else:
            if matrix[1][1] == 1 or matrix[0][0] == 1:
                raise SystemExit(f"B^{k} has an elementary length-2 shape")
            gap = v[k] - (u[k - 1] - 1)
            # v_k - (u_{k-1}-1) = u_{k-1} + v_{k-1} + 1 > 0,
            # and u_{k-1}-1 > 0, so the remainder is not zero.
            if gap != u[k - 1] + v[k - 1] + 1:
                raise SystemExit(f"remainder gap formula failed at k={k}")
            if not (0 < u[k - 1] - 1 < v[k]):
                raise SystemExit(f"divisibility obstruction failed at k={k}")
            if (u[k] - 1) % v[k] == 0 or (u[k - 1] - 1) % v[k] == 0:
                raise SystemExit(f"unexpected length-3 divisor at k={k}")


def check_formula_control():
    samples = (-7, -1, 1, 2, 5)
    for a in samples:
        for b in samples:
            for c in samples:
                got = mul(X(a), mul(Y(b), X(c)))
                if got != xyx_formula(a, b, c):
                    raise SystemExit("XYX expansion does not match multiplication")
                got = mul(Y(a), mul(X(b), Y(c)))
                if got != yxy_formula(a, b, c):
                    raise SystemExit("YXY expansion does not match multiplication")
    # The third XYX coordinate identity is the determinant, not an extra constraint.
    u, v = sequence(6)
    for k in range(2, 7):
        # Would-be exponents are not integers; the cleared numerator is v^2.
        numerator = (u[k] - 1) + u[k] * (u[k - 1] - 1)
        if numerator != v[k] * v[k]:
            raise SystemExit("automatic third-coordinate identity failed")


def check_moments(limit):
    grid = [Fraction(p, q) for q in range(1, 9) for p in range(q + 1)]
    for exponent in grid:
        if not moment_strict(2, 2, exponent) and exponent < 1:
            raise SystemExit(f"W=2 length-2 moment should pass at {exponent}")
        if moment_strict(2, 2, Fraction(1, 1)):
            raise SystemExit("W=2 length-2 moment is not strict at a=1")
        if moment_strict(2, 1, exponent):
            raise SystemExit(f"W=1 length-2 moment should fail at {exponent}")
        for length in (4, 6, 8):
            if moment_strict(length, 2, exponent):
                raise SystemExit(f"length {length} should fail the W=2 test at {exponent}")
    # k=1 passes on [0, 1); every later checked power has length >= 4.
    if limit < 2:
        raise SystemExit("need at least B^2")


def check_negative_controls():
    if unit_bfs() != 4:
        raise SystemExit("unit-shear control did not recover length 4")
    # A false divisor claim at k=2 is rejected by the remainder test.
    u, v = sequence(2)
    if (u[2] - 1) % v[2] == 0:
        raise SystemExit("control matrix accidentally had length 3")
    # Swapping the strict comparison would accept the boundary M=1.
    if moment_strict(4, 2, Fraction(0, 1)):
        raise SystemExit("boundary M=1 was treated as a pass")
    # Damaging the square coefficient breaks the word/recurrence agreement.
    damaged = mul(X(3), Y(2))
    if damaged == mul(X(2), Y(2)):
        raise SystemExit("damage control did not move the matrix")


def main():
    limit = 24
    u, v = check_identities(limit)
    check_length(u, v, limit)
    check_formula_control()
    check_moments(limit)
    check_negative_controls()
    print(
        "PASS_SL2Z_TRANSVECTION_MOMENT"
        f" powers={limit}"
        " lambda(B)=2"
        " lambda(B^k)>=4_for_k>=2"
        " W2_passes_on_[0,1)"
        " W1_fails"
        " powers_fail"
        " no_new_kappa"
    )


if __name__ == "__main__":
    main()
