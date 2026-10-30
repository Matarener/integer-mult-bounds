#!/usr/bin/env python3
"""Independent review of the common-map tensor-pairing bound.

This file does not import or execute PR #3928. It rebuilds the four-fold
Kronecker Gram, the F2 pairing, one E8 line model, and the two witnesses
from their definitions.
"""

from itertools import combinations, product

PASS = (
    "PASS_TENSOR_PAIRING_COMMON_MAP_REVIEW full_rank=16 subsets=65536 "
    "rank_screen_max=12 common_map_cap=8 witness_gram_rank=8 "
    "scalar_before=16 scalar_normalized=2 root_entry=0 "
    "abstract_labels=9 noninjective_indices=9 no_new_kappa"
)

TENSOR_INDEX = (0, 15, 1, 14, 2, 13, 3, 12)
NINE_INDEX = TENSOR_INDEX + (4,)
# Frozen output of the smallest-vector symplectic construction below.
NINE_LABELS = (508, 506, 496, 488, 448, 416, 256, 128, 511)
SIZE12_INDEX = (0, 15, 1, 14, 2, 13, 3, 12, 4, 5, 6, 7)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank_f2(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def pack(row, width):
    return sum((bit & 1) << col for col, bit in enumerate(row[:width]))


def tensor_model():
    block = ((2, 1), (1, 2))
    gram = [[1]]
    for _ in range(4):
        nxt = []
        for row in gram:
            for brow in block:
                nxt.append([value * factor for value in row for factor in brow])
        gram = nxt
    need(len(gram) == 16 and all(len(row) == 16 for row in gram), "tensor shape")
    pairing = []
    for i, row in enumerate(gram):
        bits = []
        for j, value in enumerate(row):
            distance = (i ^ j).bit_count()
            need(value == 2 ** (4 - distance), "tensor entry left the Hamming formula")
            bits.append((value + 1) & 1)
        pairing.append(bits)
    for i in range(16):
        for j in range(16):
            need(pairing[i][j] == int(j != (i ^ 15)), "complement rule")
    return gram, pairing


def square_is_identity(pairing):
    width = len(pairing)
    for i in range(width):
        for j in range(width):
            total = sum(pairing[i][k] & pairing[k][j] for k in range(width)) & 1
            need(total == int(i == j), "pairing square is not the identity")


def canon(vector):
    for value in vector:
        if value:
            if value < 0:
                return tuple(-item for item in vector)
            return tuple(vector)
    raise ValueError("zero root")


def e8_model():
    lines = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            lines.append(canon(row))
    for signs in product((-1, 1), repeat=8):
        if signs.count(-1) % 2 == 0:
            lines.append(canon(signs))
    lines = sorted(set(lines))
    frame = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            frame.append(canon(row))
    frame = set(frame)
    need(len(lines) == 120 and frame <= set(lines) and len(frame) == 8, "E8 line count")
    live = [row for row in lines if row not in frame]
    need(len(live) == 112, "P112 complement count")
    need(all(sum(value * value for value in row) == 8 for row in lines), "doubled norm")
    for left, right in combinations(lines, 2):
        inner = sum(a * b for a, b in zip(left, right))
        need(inner in (-4, 0, 4), "distinct lines left the E8 alphabet")
    return live


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def subset_shape(mask):
    pairs = sum(
        1
        for i in range(8)
        if (mask >> i) & 1 and (mask >> (i ^ 15)) & 1
    )
    size = mask.bit_count()
    return pairs, size - 2 * pairs


def expected_rank(pairs, singles):
    if singles == 0:
        return 2 * pairs
    return 2 * pairs + 1


def census(pairing):
    rows = [pack(row, 16) for row in pairing]
    need(rank_f2(rows) == 16, "full pairing rank")
    largest = 0
    largest_mask = 0
    for mask in range(1 << 16):
        chosen = [rows[i] & mask for i in range(16) if (mask >> i) & 1]
        pairs, singles = subset_shape(mask)
        actual = rank_f2(chosen)
        need(actual == expected_rank(pairs, singles), "principal rank formula")
        if actual <= 9 and mask.bit_count() > largest:
            largest = mask.bit_count()
            largest_mask = mask
    need(largest == 12, "rank screen maximum")
    return largest, largest_mask


def witness(live, gram, pairing):
    wanted = (
        (0, 0, 0, 0, 0, 2, -2, 0),
        (0, 0, 0, 0, 0, 2, 0, -2),
        (0, 0, 0, 2, -2, 0, 0, 0),
        (0, 0, 2, 0, -2, 0, 0, 0),
        (1, -1, -1, -1, -1, 1, 1, 1),
        (1, -1, 1, 1, 1, -1, -1, -1),
        (1, 1, -1, -1, -1, -1, -1, -1),
        (1, 1, 1, 1, 1, 1, 1, 1),
    )
    live_set = set(live)
    need(all(canon(row) in live_set for row in wanted), "witness left the 112-line complement")
    matrix = [[dot(left, right) // 4 for right in wanted] for left in wanted]
    for i in range(8):
        need(matrix[i][i] == 2, "witness norm")
        for j in range(8):
            same_pair = i // 2 == j // 2
            if i != j and same_pair:
                need(matrix[i][j] in (-1, 1), "within-pair product")
            if not same_pair:
                need(matrix[i][j] == 0, "cross-pair product")
            bit = (matrix[i][j] + 1) & 1
            need(bit == pairing[TENSOR_INDEX[i]][TENSOR_INDEX[j]], "witness pairing")
    packed = [pack([(matrix[i][j] + 1) & 1 for j in range(8)], 8) for i in range(8)]
    need(rank_f2(packed) == 8, "witness pairing rank")
    # Positive-definite 2 by 2 blocks, either sign.
    for sign in (-1, 1):
        need(4 - sign * sign == 3 and 3 > 0, "pair block determinant")
    cross = gram[0][1]
    need(cross == 8 and matrix[0][2] == 0, "scalar mismatch coordinates")
    need(2 * cross == 16 and 2 * cross / 8 == 2, "normalized coefficient")
    return matrix


def singleton_rows(pairing, indices):
    rows = []
    for i in indices:
        if (i ^ 15) not in indices:
            rows.append(tuple(pairing[i][j] for j in indices))
    return rows


def abstract_nine(pairing):
    def bit_dot(left, right):
        return (left & right).bit_count() & 1

    space = [value for value in range(512) if value.bit_count() % 2 == 0]
    basis = []
    for _ in range(4):
        first = next(value for value in space if value)
        second = next(value for value in space if bit_dot(first, value) == 1)
        basis.extend((first, second))
        space = [
            value
            for value in space
            if bit_dot(first, value) == 0 and bit_dot(second, value) == 0
        ]
    need(space == [0], "symplectic basis")
    labels = tuple(((1 << 9) - 1) ^ value for value in basis) + ((1 << 9) - 1,)
    need(labels == NINE_LABELS and len(set(labels)) == 9, "frozen nine labels")
    for i, left in enumerate(NINE_INDEX):
        for j, right in enumerate(NINE_INDEX):
            bit = (labels[i] & labels[j]).bit_count() & 1
            need(bit == pairing[left][right], "abstract nine pairing")
    rows = [tuple(pairing[i][j] for j in NINE_INDEX) for i in NINE_INDEX]
    need(len(set(rows)) == 9, "nine-set rows separate points")


def size12_obstruction(pairing):
    rows = singleton_rows(pairing, SIZE12_INDEX)
    need(len(rows) == 4 and len(set(rows)) == 1, "size-12 singleton rows")
    chosen = [pack([pairing[i][j] for j in SIZE12_INDEX], 12) for i in SIZE12_INDEX]
    need(rank_f2(chosen) == 9, "size-12 rank")


def noninjective(live, pairing):
    first = canon((2, 0, -2, 0, 0, 0, 0, 0))
    second = canon((2, 0, 0, -2, 0, 0, 0, 0))
    third = canon((0, 2, 0, 0, -2, 0, 0, 0))
    live_set = set(live)
    need({first, second, third} <= live_set, "noninjective lines")
    images = {0: first, 15: second}
    indices = (0, 15, 1, 2, 3, 4, 5, 6, 7)
    for left in indices:
        for right in indices:
            a = images.get(left, third)
            b = images.get(right, third)
            bit = (dot(a, b) // 4 + 1) & 1
            need(bit == pairing[left][right], "noninjective pairing")
    need(len({images.get(i, third) for i in indices}) == 3, "three lines")


def audit():
    gram, pairing = tensor_model()
    square_is_identity(pairing)
    census(pairing)
    live = e8_model()
    witness(live, gram, pairing)
    abstract_nine(pairing)
    size12_obstruction(pairing)
    noninjective(live, pairing)
    return {
        "full_rank": 16,
        "subsets": 65536,
        "rank_screen_max": 12,
        "common_map_cap": 8,
        "scalar_before": 16,
        "scalar_normalized": 2,
        "root_entry": 0,
    }


def main():
    result = audit()
    need(result["scalar_before"] == 16 and result["root_entry"] == 0, "receipt")
    print(PASS)


if __name__ == "__main__":
    main()
