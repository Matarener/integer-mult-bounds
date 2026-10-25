"""Full formal F2[Q8] matrices, with chronological left action.

Nick Petalas, Apache-2.0. No finite-address quotient is used.
"""

from dataclasses import dataclass

from linear import MAX_DIM, matrix, parity, require


@dataclass(frozen=True)
class Gate:
    label: int
    u: int
    v: int


def validate(gates, roles):
    require(0 <= roles <= MAX_DIM and len(gates) <= MAX_DIM, "word dimension")
    for gate in gates:
        require(gate.label in (2, 4), "positive labels only")
        require(0 < gate.u < (1 << roles) and 0 < gate.v < (1 << roles), "gate vector")
        require(parity(gate.u & gate.v) == 1, "rank-one idempotent")


def group_product(left, right):
    # Each entry is (sign, axis); encoding is 2*axis+sign.
    axes = (
        ((0, 0), (0, 1), (0, 2), (0, 3)),
        ((0, 1), (1, 0), (0, 3), (1, 2)),
        ((0, 2), (1, 3), (1, 0), (0, 1)),
        ((0, 3), (0, 2), (1, 1), (1, 0)),
    )
    sign, axis = axes[left // 2][right // 2]
    return 2 * axis + ((left ^ right ^ sign) & 1)


def ring_product(left, right):
    value = 0
    for a in range(8):
        for b in range(8):
            if ((left >> a) & 1) and ((right >> b) & 1):
                value ^= 1 << group_product(a, b)
    return value


def endpoint(gates, roles):
    validate(gates, roles)
    result = [[int(a == b) for b in range(roles)] for a in range(roles)]
    for gate in gates:
        row = [0] * roles
        for a in range(roles):
            if (gate.v >> a) & 1:
                for b in range(roles):
                    row[b] ^= result[a][b]
        delta = [ring_product(1 ^ (1 << gate.label), value) for value in row]
        for a in range(roles):
            if (gate.u >> a) & 1:
                for b in range(roles):
                    result[a][b] ^= delta[b]
    return tuple(tuple(row) for row in result)


def gram(gates, roles):
    validate(gates, roles)
    return tuple(sum(parity(left.v & right.u) << k for k, right in enumerate(gates)) for left in gates)


def binary_right(formal, binary, columns):
    require(0 <= columns <= MAX_DIM, "output dimension")
    return tuple(tuple(xor_column(row, binary, j) for j in range(columns)) for row in formal)


def xor_column(row, binary, index):
    value = 0
    for j, coefficient in enumerate(row):
        if (binary[j] >> index) & 1:
            value ^= coefficient
    return value


def label_sum(gates, roles, label):
    rows = [0] * roles
    for gate in gates:
        if gate.label == label:
            for j in range(roles):
                if (gate.u >> j) & 1:
                    rows[j] ^= gate.v
    return matrix(rows, roles)
