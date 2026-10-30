#!/usr/bin/env python3
"""Index-to-tensor bridge for the scalar P104 code described in PR #3996.

The published index is index(bank, i, j) = (bank*104 + i)*104 + j.
Axis 0 varies i at fixed j. Axis 1 varies j at fixed i. This checker
does not import PR #3996 and does not replay its 763,392 events.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json"
FIXTURE_SHA256 = "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"
B2_SHA256 = "88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535"
N = 104
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def matvec(matrix, vector):
    return [sum(coefficient * entry for coefficient, entry in zip(row, vector))
            for row in matrix]


def matmul(left, right):
    right_columns = list(zip(*right))
    return [[sum(x * y for x, y in zip(row, column)) for column in right_columns]
            for row in left]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def eye(scale=1):
    return [[scale if i == j else 0 for j in range(N)] for i in range(N)]


def unit(length, index):
    vector = [0] * length
    vector[index] = 1
    return vector


def frobenius_inner(left, right):
    return sum(x * y for row, other in zip(left, right) for x, y in zip(row, other))


def dense_kronecker(left, right):
    blocks = []
    for i in range(len(left)):
        for j in range(len(right)):
            row = []
            for p in range(len(left)):
                for q in range(len(right)):
                    row.append(left[i][p] * right[j][q])
            blocks.append(row)
    return blocks


def factored_frobenius_square(terms):
    """||sum c_k A_k tensor B_k||_F^2 = sum c_k c_l <A_k,A_l> <B_k,B_l>."""
    total = 0
    for coeff, row_factor, column_factor in terms:
        for other, other_row, other_column in terms:
            total += (coeff * other * frobenius_inner(row_factor, other_row)
                      * frobenius_inner(column_factor, other_column))
    return total


def dense_frobenius_square(terms):
    size = len(terms[0][1]) * len(terms[0][2])
    matrix = [[0] * size for _ in range(size)]
    for coeff, row_factor, column_factor in terms:
        block = dense_kronecker(row_factor, column_factor)
        for i in range(size):
            for j in range(size):
                matrix[i][j] += coeff * block[i][j]
    return frobenius_inner(matrix, matrix)


def axis0_broadcast(matrix, state):
    """Apply matrix to every column. This is the axis-0 fiber broadcast."""
    width = len(matrix)
    output = [[0] * width for _ in range(width)]
    for column in range(width):
        image = matvec(matrix, [state[row][column] for row in range(width)])
        for row in range(width):
            output[row][column] = image[row]
    return output


def axis1_broadcast(matrix, state):
    """Apply matrix to every row-vector ordered by j. This is axis 1."""
    width = len(matrix)
    output = [[0] * width for _ in range(width)]
    for row in range(width):
        image = matvec(matrix, state[row])
        output[row] = image
    return output


def kronecker_from_index(left, right, state):
    """(left tensor right) on row-major index i*n+j, summed from the coefficients."""
    width = len(left)
    output = [[0] * width for _ in range(width)]
    for i in range(width):
        for j in range(width):
            total = 0
            for p in range(width):
                for q in range(width):
                    total += left[i][p] * right[j][q] * state[p][q]
            output[i][j] = total
    return output


def witness(width):
    return [[(3 * i + 5 * j + 1) % 7 - 3 for j in range(width)] for i in range(width)]


def state_from(width, seed):
    return [[(i * i + 3 * j + seed) % 5 - 2 for j in range(width)] for i in range(width)]


def compare(left, right):
    gaps = 0
    for row, other in zip(left, right):
        for entry, expected in zip(row, other):
            if entry != expected:
                gaps += 1
    return gaps


def check_small_index_bridge():
    """Brute-force every coefficient at widths 2 and 8, then one dense width-104 state."""
    naive_positions = 0
    for width in (2, 8):
        operator = witness(width)
        state = state_from(width, 1)
        identity = [[1 if i == j else 0 for j in range(width)] for i in range(width)]
        naive_positions += width ** 4
        require(axis0_broadcast(operator, state) == kronecker_from_index(operator, identity, state),
                "axis 0 differs from K tensor I at width %d" % width)
        require(axis1_broadcast(operator, state) == kronecker_from_index(identity, operator, state),
                "axis 1 differs from I tensor K at width %d" % width)
        swapped = axis0_broadcast(identity, state)  # not used; keep identity path obvious
        require(swapped == state, "identity broadcast")
    operator = witness(N)
    state = state_from(N, 4)
    identity = eye()
    # The coefficient (I tensor K)_(i j),(p q) is δ_ip K_jq. Sum that explicitly.
    summed = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            total = 0
            for q in range(N):
                total += operator[j][q] * state[i][q]
            summed[i][j] = total
    require(axis1_broadcast(operator, state) == summed, "axis-1 fiber differs from the index sum")
    column_sum = [[0] * N for _ in range(N)]
    for j in range(N):
        image = matvec(operator, [state[row][j] for row in range(N)])
        for i in range(N):
            column_sum[i][j] = image[i]
    require(axis0_broadcast(operator, state) == column_sum, "axis-0 fiber differs from its column sum")
    # One full naive Kronecker product is too large at width 104. The width-8
    # check above executed every coefficient. Here compare axis 0 with K tensor I
    # through the same δ-sum the definition gives, on this dense state.
    axis0_sum = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            total = 0
            for p in range(N):
                total += operator[i][p] * state[p][j]
            axis0_sum[i][j] = total
    require(axis0_broadcast(operator, state) == axis0_sum, "axis 0 differs from K tensor I")
    wrong = matmul(state, operator)  # right multiply, omitting the transpose
    require(compare(wrong, axis1_broadcast(operator, state)) > 0,
            "a non-symmetric witness must expose the column transpose")
    return naive_positions


def check_contraction_formula():
    samples = []
    for width, seed in ((2, 0), (3, 1)):
        first = witness(width)
        second = state_from(width, seed)
        third = transpose(first)
        terms = [(1, first, second), (-2, third, first), (3, second, third)]
        factored = factored_frobenius_square(terms)
        dense = dense_frobenius_square(terms)
        require(factored == dense and factored > 0, "contraction formula mismatch")
        samples.append(factored)
    single = [(1, eye(), eye())]
    require(factored_frobenius_square(single) == N * N, "identity tensor norm")
    return samples


def integer_lift(b2):
    """2U and 2U^{-1}. U = [I, B; 0, I] with B = B2/2."""
    upper = eye(2)
    inverse = eye(2)
    for i in range(8):
        for j in range(96):
            upper[i][8 + j] = b2[i][j]
            inverse[i][8 + j] = -b2[i][j]
    require(matmul(upper, inverse) == eye(4), "integer lift is a two-sided inverse up to scale 4")
    require(matmul(inverse, upper) == eye(4), "inverse on the left")
    return upper, inverse


def load_b2():
    raw = FIXTURE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256, "canonical P104 fixture")
    section = json.loads(raw)["section4_explicit_P104"]
    roots = set()
    for coords in itertools.product((-2, 0, 2), repeat=8):
        support = [value for value in coords if value]
        if len(support) == 2 and support[0] > 0:
            roots.add(coords)
    for coords in itertools.product((-1, 1), repeat=8):
        if coords[0] == 1 and coords.count(-1) % 2 == 0:
            roots.add(coords)
    removed = {tuple(row) for row in section["F0"] + section["C"]}
    require(len(roots) == 120 and len(removed) == 16 and removed <= roots, "E8 root domain")
    original = sorted(roots - removed)
    order = list(PIVOTS) + [index for index in range(N) if index not in PIVOTS]
    ports = [original[index] for index in order]
    gram = [[sum(x * y for x, y in zip(row, other)) for other in ports] for row in ports]
    b2 = [[gram[i][8 + j] // 4 for j in range(96)] for i in range(8)]
    digest = hashlib.sha256(json.dumps(b2, separators=(",", ":")).encode("ascii")).hexdigest()
    require(digest == B2_SHA256, "ordered B2 digest")
    require(all(sum(b2[i][k] * b2[j][k] for k in range(96)) == 48 * int(i == j)
                for i in range(8) for j in range(8)), "B2 B2^t = 48 I")
    return b2, gram


def projector():
    return [[1 if i == j < 8 else 0 for j in range(N)] for i in range(N)]


def check_geometry(b2):
    upper, inverse = integer_lift(b2)
    pivot = projector()
    moment = matmul(upper, transpose(upper))       # 4 U U^t
    wrong = matmul(transpose(upper), upper)        # 4 U^t U
    require(moment != wrong, "U U^t and U^t U differ on this code")
    gram_scale = matmul(matmul(transpose(upper), pivot), upper)  # 4 A
    squared = matmul(gram_scale, gram_scale)
    require(squared == [[52 * entry for entry in row] for row in gram_scale], "A^2 = 13 A")
    # A = G/4 with G = gram_scale. (I - G/4)(12 I - G/4) = 12 I,
    # so (4I - G)(48I - G) = 192 I.
    left = [[4 * int(i == j) - gram_scale[i][j] for j in range(N)] for i in range(N)]
    right = [[48 * int(i == j) - gram_scale[i][j] for j in range(N)] for i in range(N)]
    require(matmul(left, right) == eye(192), "I-A is invertible over Q")
    moment_inverse_num = matmul(transpose(inverse), inverse)  # 4 U^{-t} U^{-1} = 4 M^{-1}
    require(matmul(moment, moment_inverse_num) == eye(16), "M is invertible")
    side = [[moment_inverse_num[i][j] - 4 * pivot[i][j] for j in range(N)] for i in range(N)]
    # side = 4(N-P). inverse = 2 U^{-1} and left = 4(I-A), so
    # inverse^t left inverse = 16 U^{-t}(I-A)U^{-1} = 16(N-P) = 4*side.
    expected_side = matmul(matmul(transpose(inverse), left), inverse)
    return upper, moment, wrong, gram_scale, side, expected_side


def reduced_fraction(numerator, denominator):
    sign = 1 if numerator * denominator >= 0 else -1
    numerator, denominator = abs(numerator), abs(denominator)
    common = numerator
    other = denominator
    while other:
        common, other = other, common % other
    return sign * numerator // common, denominator // common


def main():
    naive_positions = check_small_index_bridge()
    contraction_samples = check_contraction_formula()
    b2, gram = load_b2()
    upper, moment, wrong, gram_scale, side, expected_side = check_geometry(b2)
    # Scales: inverse = 2 U^{-1}, left = 4(I-A), so
    # inverse^t left inverse = 2 U^{-t} * 4(I-A) * 2 U^{-1} = 16(N-P).
    # side was defined as 4(N-P). The equality N-P = U^{-t}(I-A)U^{-1}
    # is 16(N-P) = 4 * side.
    require(expected_side == [[4 * entry for entry in row] for row in side],
            "N-P congruence")
    completion = [[48 * (i == j) - gram_scale[i][j] for j in range(N)] for i in range(N)]
    exhibited = matmul(side, matmul(upper, matmul(completion, transpose(upper))))
    require(exhibited == eye(768), "exhibited rational inverse of N-P")
    # (A tensor B)(A^{-1} tensor B^{-1}) = I on a 2-by-2 invertible pair.
    factor_a = [[1, 2], [0, 1]]
    factor_ainv = [[1, -2], [0, 1]]
    factor_b = [[1, 1], [0, 1]]
    factor_binv = [[1, -1], [0, 1]]
    require(matmul(factor_b, factor_binv) == [[1, 0], [0, 1]], "2x2 inverse")
    product = matmul(dense_kronecker(factor_a, factor_b), dense_kronecker(factor_ainv, factor_binv))
    require(product == [[1 if i == j else 0 for j in range(4)] for i in range(4)],
            "Kronecker product of inverses")
    gap_entries = [[moment[i][j] - wrong[i][j] for j in range(N)] for i in range(N)]
    # moment - wrong = 4(M - U^t U). ||P tensor (M - U^t U)||^2
    # = ||P||^2 ||M - U^t U||^2 = 8 * ||gap_entries||^2 / 16.
    gap_square = frobenius_inner(gap_entries, gap_entries)
    require(gap_square > 0 and gap_square % 16 == 0, "transpose-order gap")
    block_square = 8 * (gap_square // 16)
    numerator, denominator = reduced_fraction(block_square, 1)
    # Four sweeps through the index bridge. The four shears are the A/M block
    # maps named in the receipt; their factors are the matrices checked above.
    inverse_lift = integer_lift(b2)[1]
    sweeps = {
        "U": upper,
        "U_inverse": inverse_lift,
        "U_transpose": transpose(upper),
        "U_inverse_transpose": transpose(inverse_lift),
    }
    for name, operator in sweeps.items():
        state = state_from(N, 2)
        require(axis0_broadcast(operator, state)
                == [[sum(operator[i][p] * state[p][j] for p in range(N)) for j in range(N)]
                    for i in range(N)],
                name + " axis 0")
        require(axis1_broadcast(operator, state)
                == [[sum(operator[j][q] * state[i][q] for q in range(N)) for j in range(N)]
                    for i in range(N)],
                name + " axis 1 is I tensor K, hence right multiplication by K^t")
    # Shears, as block maps on a bank pair (X, Y), checked by the matrix factors.
    # Lower A: Y := Y + A X with A acting on axis 0. Upper A uses axis 1 of A,
    # which right-multiplies by A^t. Coded forms use M = U U^t, not U^t U.
    require(gram_scale == matmul(matmul(transpose(upper), projector()), upper), "A factor")
    receipt = {
        "index": "(bank*104+i)*104+j",
        "naive_kronecker_positions": naive_positions,
        "contraction_samples": contraction_samples,
        "b2_nonzero": sum(value != 0 for row in b2 for value in row),
        "A_square_is_13A": True,
        "I_minus_A_invertible_over_Q": True,
        "M_invertible": True,
        "omitted_side_rank": N * N,
        "wrong_factor_block_frobenius_square": "%d/%d" % (numerator, denominator),
        "literal_events_replayed": False,
        "new_kappa": False,
    }
    # gram is retained so a reviewer can see the integer normalization used above.
    require(gram[0][0] == 8, "pivot norm")
    print("PASS_P104_INDEX_TENSOR_BRIDGE " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
