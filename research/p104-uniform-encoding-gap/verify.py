#!/usr/bin/env python3
"""Uniform completion commutes with E0 and not with the physical encodings.

Separate from PR #3954's checker. No predecessor module is imported.
"""
from __future__ import annotations

ZERO = (0, 0)
ONE = (1, 0)
I = (0, 1)

# Two ports, J then N. Address space is the four-point square {0, e1, e2, e1+e2}.
PORTS = 2
ADDR = 4
DIM = 2 * PORTS * ADDR


def gadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def gsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def gmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def mm(left, right):
    size = len(left)
    out = [[ZERO] * size for _ in range(size)]
    for i in range(size):
        for k in range(size):
            if left[i][k] == ZERO:
                continue
            for j in range(size):
                if right[k][j] == ZERO:
                    continue
                out[i][j] = gadd(out[i][j], gmul(left[i][k], right[k][j]))
    return out


def msub(left, right):
    return [[gsub(left[i][j], right[i][j]) for j in range(len(left))] for i in range(len(left))]


def eye(size):
    return [[ONE if i == j else ZERO for j in range(size)] for i in range(size)]


def nnz(matrix):
    return sum(entry != ZERO for row in matrix for entry in row)


def slot(bank, port, addr):
    return (bank * PORTS + port) * ADDR + addr


def translation(shift):
    matrix = [[ZERO] * ADDR for _ in range(ADDR)]
    for addr in range(ADDR):
        # (X_u f)(x) = f(x+u).
        matrix[addr][addr ^ shift] = ONE
    return matrix


def character_e1():
    """Multiplication by (-1)^{x·e1}."""
    matrix = [[ZERO] * ADDR for _ in range(ADDR)]
    for addr in range(ADDR):
        matrix[addr][addr] = ONE if (addr & 1) == 0 else (-1, 0)
    return matrix


def chart(shift):
    """S_u = (1+i)I + (1-i) X_u = 2 C_u, with C_u the PR #3954 boundary chart."""
    return [
        [
            gadd(gmul(gadd(ONE, I), eye(ADDR)[i][j]), gmul(gsub(ONE, I), translation(shift)[i][j]))
            for j in range(ADDR)
        ]
        for i in range(ADDR)
    ]


def lift_uniform(operator):
    matrix = [[ZERO] * DIM for _ in range(DIM)]
    for bank in range(2):
        for port in range(PORTS):
            for i in range(ADDR):
                for j in range(ADDR):
                    matrix[slot(bank, port, i)][slot(bank, port, j)] = operator[i][j]
    return matrix


def encoding(port_charts, scalar_d):
    """L(r, w) = (D r + H T w, w), H = diag(0, 1).

    port_charts[p] is the address operator T_p. The J chart is stored and then
    killed by H, matching the block H T.
    """
    matrix = [[ZERO] * DIM for _ in range(DIM)]
    for port in range(PORTS):
        for addr in range(ADDR):
            matrix[slot(1, port, addr)][slot(1, port, addr)] = ONE
    for row in range(PORTS):
        for col in range(PORTS):
            coef = (scalar_d[row][col], 0)
            if coef == ZERO:
                continue
            for addr in range(ADDR):
                target = slot(0, row, addr)
                source = slot(0, col, addr)
                matrix[target][source] = gadd(matrix[target][source], coef)
    chart_n = port_charts[1]
    for i in range(ADDR):
        for j in range(ADDR):
            matrix[slot(0, 1, i)][slot(1, 1, j)] = gadd(
                matrix[slot(0, 1, i)][slot(1, 1, j)], chart_n[i][j]
            )
    return matrix


def literal_pi():
    """Pi swaps the N slot between the two banks and fixes J."""
    matrix = [[ZERO] * DIM for _ in range(DIM)]
    for addr in range(ADDR):
        matrix[slot(0, 0, addr)][slot(0, 0, addr)] = ONE
        matrix[slot(0, 1, addr)][slot(1, 1, addr)] = ONE
        matrix[slot(1, 0, addr)][slot(1, 0, addr)] = ONE
        matrix[slot(1, 1, addr)][slot(0, 1, addr)] = ONE
    return matrix


def commutator(left, right):
    return msub(mm(left, right), mm(right, left))


# A non-scalar integer D. Any scalar-entry D is covered by the written proof;
# this one keeps the check off the identity matrix.
SCALAR_D = [[1, 1], [1, 2]]


def report():
    zeta = character_e1()
    chart_e1 = chart(1)
    chart_e2 = chart(2)
    identity = eye(ADDR)
    uniform_z = lift_uniform(zeta)
    uniform_e1 = lift_uniform(chart_e1)
    scalar = encoding([identity, identity], SCALAR_D)
    physical = encoding([identity, chart_e1], SCALAR_D)
    even_physical = encoding([identity, chart_e2], SCALAR_D)
    pi = literal_pi()
    literal = mm(pi, physical)
    defect = commutator(uniform_z, physical)
    literal_defect = commutator(uniform_z, literal)
    address_defect = commutator(zeta, chart_e1)
    if nnz(commutator(uniform_z, scalar)) != 0:
        raise ValueError("scalar-bank E0 failed to commute with Z_e1")
    if nnz(defect) == 0:
        raise ValueError("physical L_T commuted with Z_e1")
    if nnz(literal_defect) == 0:
        raise ValueError("literal Pi L_T commuted with Z_e1")
    if literal_defect != mm(pi, defect):
        raise ValueError("Pi did not intertwine the physical commutator")
    if nnz(commutator(uniform_z, pi)) != 0:
        raise ValueError("uniform Z_e1 failed to commute with Pi")
    if nnz(commutator(uniform_e1, physical)) != 0 or nnz(commutator(uniform_e1, literal)) != 0:
        raise ValueError("translation chart failed to commute with its own physical encoding")
    if nnz(commutator(uniform_z, even_physical)) != 0:
        raise ValueError("even character direction was not a commuting control")
    if nnz(commutator(translation(1), translation(2))) != 0:
        raise ValueError("the two translations failed to commute")
    if address_defect != [
        [ZERO, (2, -2), ZERO, ZERO],
        [(-2, 2), ZERO, ZERO, ZERO],
        [ZERO, ZERO, ZERO, (2, -2)],
        [ZERO, ZERO, (-2, 2), ZERO],
    ]:
        raise ValueError("address commutator [Z_e1, S_e1] changed")
    if nnz(defect) != 4 or nnz(literal_defect) != 4 or nnz(address_defect) != 4:
        raise ValueError("unexpected commutator support")
    return {
        "scalar_commutes": True,
        "physical_defect_nnz": nnz(defect),
        "literal_defect_nnz": nnz(literal_defect),
        "address_commutator_01": address_defect[0][1],
        "translation_subalgebra_commutes": True,
        "even_direction_commutes": True,
        "pi_intertwines": True,
    }


def main():
    facts = report()
    entry = facts["address_commutator_01"]
    print(
        "PASS_P104_UNIFORM_ENCODING_GAP"
        f" scalar_commutes=1 physical_defect_nnz={facts['physical_defect_nnz']}"
        f" literal_defect_nnz={facts['literal_defect_nnz']}"
        f" address_entry_01={entry[0]}{entry[1]:+d}i"
        " translation_subalgebra_commutes=1 even_direction_commutes=1 pi_intertwines=1"
        " no_new_kappa"
    )


if __name__ == "__main__":
    main()
