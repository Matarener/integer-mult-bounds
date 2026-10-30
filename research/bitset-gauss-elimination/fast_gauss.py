"""Exact bounded quadratic Gauss sums. Produced by Nick Petalas. Apache-2.0."""

MAX_DIMENSION = 256


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unpack(n, poly):
    require(type(n) is int and 0 <= n <= MAX_DIMENSION, "Dimension in 0..256")
    require(type(poly) is dict and len(poly) <= 1 + n * (n + 1) // 2,
            "Bounded polynomial dictionary")
    diagonal, adjacency = [0] * n, [0] * n
    constant = 0
    for mask, coefficient in poly.items():
        require(type(mask) is int and 0 <= mask < (1 << n), "Variable mask")
        require(type(coefficient) is int and 0 < coefficient < 4,
                "Canonical nonzero phase coefficient")
        degree = mask.bit_count()
        require(degree <= 2 and (degree != 2 or coefficient == 2),
                "Only even quadratic terms")
        if not mask:
            constant = coefficient
        elif degree == 1:
            diagonal[mask.bit_length() - 1] = coefficient
        else:
            low = mask & -mask
            i, j = low.bit_length() - 1, (mask ^ low).bit_length() - 1
            adjacency[i] |= 1 << j
            adjacency[j] |= 1 << i
    return constant, diagonal, adjacency


def odd_step(diagonal, adjacency, neighbors, coefficient, n):
    """Add -coefficient times the parity of neighbors, modulo four."""
    for k in range(n):
        if neighbors >> k & 1:
            diagonal[k] = (diagonal[k] - coefficient) % 4
            adjacency[k] ^= neighbors ^ (1 << k)


def pair_step(diagonal, adjacency, left, right, coefficient, target, n):
    """Substitute y=target XOR parity(left) after summing the paired x."""
    for k in range(n):
        in_left, in_right = left >> k & 1, right >> k & 1
        diagonal[k] = (diagonal[k] + coefficient * (1 - 2 * target) * in_left
                       + 2 * target * in_right + 2 * (in_left & in_right)) % 4
        delta = (right if in_left else 0) ^ (left if in_right else 0)
        if coefficient & 1 and in_left:
            delta ^= left ^ (1 << k)
        adjacency[k] ^= delta & ~(1 << k)


def gauss(n, poly):
    """Return sum_x i**q(x), without affine-polynomial substitutions."""
    constant, diagonal, adjacency = unpack(n, poly)
    active, real, imaginary = (1 << n) - 1, 1, 0
    for _ in range(n):
        if not active:
            break
        i = active.bit_length() - 1
        active ^= 1 << i
        coefficient = diagonal[i]
        neighbors = adjacency[i] & active
        if coefficient & 1:
            sign = 1 if coefficient == 1 else -1
            real, imaginary = real - sign * imaginary, imaginary + sign * real
            odd_step(diagonal, adjacency, neighbors, coefficient, n)
        elif neighbors:
            j = neighbors.bit_length() - 1
            active ^= 1 << j
            left, right = neighbors & active, adjacency[j] & active
            target, other = coefficient // 2, diagonal[j]
            constant = (constant + other * target) % 4
            pair_step(diagonal, adjacency, left, right, other, target, n)
            real, imaginary = 2 * real, 2 * imaginary
        elif coefficient:
            return 0, 0
        else:
            real, imaginary = 2 * real, 2 * imaginary
    require(active == 0, "Every variable was eliminated")
    return ((real, imaginary), (-imaginary, real),
            (-real, -imaginary), (imaginary, -real))[constant]
