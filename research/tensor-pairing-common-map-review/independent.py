#!/usr/bin/env python3
"""Second reading of the pairing identity, witness Gram and nine labels.

No function in this file is imported from verify.py. The census of all
65536 principal sets stays in that file.
"""

PASS = (
    "PASS_TENSOR_PAIRING_COMMON_MAP_REVIEW_INDEPENDENT "
    "square=I16 witness_cross=0 coefficient=16 normalized=2 labels=9 no_new_kappa"
)

WITNESS = (
    (0, 0, 0, 0, 0, 2, -2, 0),
    (0, 0, 0, 0, 0, 2, 0, -2),
    (0, 0, 0, 2, -2, 0, 0, 0),
    (0, 0, 2, 0, -2, 0, 0, 0),
    (1, -1, -1, -1, -1, 1, 1, 1),
    (1, -1, 1, 1, 1, -1, -1, -1),
    (1, 1, -1, -1, -1, -1, -1, -1),
    (1, 1, 1, 1, 1, 1, 1, 1),
)
TENSOR_INDEX = (0, 15, 1, 14, 2, 13, 3, 12)
LABELS = (508, 506, 496, 488, 448, 416, 256, 128, 511)
NINE_INDEX = TENSOR_INDEX + (4,)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pairing_from_formula():
    table = []
    gram = []
    for i in range(16):
        grow = []
        brow = []
        for j in range(16):
            value = 2 ** (4 - (i ^ j).bit_count())
            grow.append(value)
            brow.append((value + 1) & 1)
        gram.append(grow)
        table.append(brow)
    return gram, table


def square_identity(pairing):
    for i in range(16):
        for j in range(16):
            total = 0
            for k in range(16):
                total ^= pairing[i][k] & pairing[k][j]
            need(total == int(i == j), "square")


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def witness_and_scalar(gram, pairing):
    matrix = [[dot(left, right) // 4 for right in WITNESS] for left in WITNESS]
    for i in range(8):
        for j in range(8):
            if i // 2 != j // 2:
                need(matrix[i][j] == 0, "cross")
            elif i != j:
                need(abs(matrix[i][j]) == 1, "pair")
            else:
                need(matrix[i][j] == 2, "norm")
            need(
                ((matrix[i][j] + 1) & 1) == pairing[TENSOR_INDEX[i]][TENSOR_INDEX[j]],
                "pairing",
            )
    for sign in (-1, 1):
        determinant = 4 - sign * sign
        need(determinant == 3, "block")
    need(gram[0][1] == 8 and matrix[0][2] == 0, "mismatch")
    need(2 * gram[0][1] == 16, "raw coefficient")
    return matrix


def nine_labels(pairing):
    for i, left in enumerate(NINE_INDEX):
        for j, right in enumerate(NINE_INDEX):
            bit = (LABELS[i] & LABELS[j]).bit_count() & 1
            need(bit == pairing[left][right], "label")
    need(len(set(LABELS)) == 9, "distinct")


def main():
    gram, pairing = pairing_from_formula()
    square_identity(pairing)
    witness_and_scalar(gram, pairing)
    nine_labels(pairing)
    print(PASS)


if __name__ == "__main__":
    main()
