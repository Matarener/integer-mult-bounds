"""Screen all 216 diagonal targets in the paid two-generator S3 alphabet."""

from collections import deque
from itertools import permutations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
LEMMA = (
    "Eight diagonal S3 targets, those whose three labels all lie in the two "
    "length-two elements, have representation rank 6 and a six-call coordinate "
    "word. One hundred twenty-five of the 216 diagonal targets match in the same way."
)


def require(ok, why):
    if not ok:
        raise SystemExit(why)


def rank(matrix):
    rows = [list(row) for row in matrix]
    pivot_row = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][col] & 1), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        for i in range(len(rows)):
            if i != pivot_row and rows[i][col] & 1:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def mul2(left, right):
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(2)) & 1
                       for j in range(2)) for i in range(2))


def compose(later, earlier):
    return tuple(later[earlier[i]] for i in range(3))


def zero_matrix():
    return [[0, 0, 0] for _ in range(3)]


def identity_matrix(identity_index):
    out = zero_matrix()
    for i in range(3):
        out[i][i] = 1 << identity_index
    return out


def algebra_mul(left, right, table):
    out = 0
    for a in range(6):
        if (left >> a) & 1:
            for b in range(6):
                if (right >> b) & 1:
                    out ^= 1 << table[a][b]
    return out


def matrix_mul(left, right, table):
    out = zero_matrix()
    for i in range(3):
        for j in range(3):
            value = 0
            for k in range(3):
                value ^= algebra_mul(left[i][k], right[k][j], table)
            out[i][j] = value
    return out


def paid(label, projector, identity_index):
    out = identity_matrix(identity_index)
    delta = (1 << label) ^ (1 << identity_index)
    for i in range(3):
        for j in range(3):
            if projector[i][j]:
                out[i][j] ^= delta
    return out


def diagonal(labels):
    out = zero_matrix()
    for i, label in enumerate(labels):
        out[i][i] = 1 << label
    return out


def main():
    require(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    group = sorted(permutations(range(3)))
    index = {item: i for i, item in enumerate(group)}
    identity = (0, 1, 2)
    s = (1, 0, 2)
    t = (0, 2, 1)
    generators = (s, t)
    eye = ((1, 0), (0, 1))
    rho = {identity: eye}
    pending = [identity]
    while pending:
        current = pending.pop()
        for generator, matrix in ((s, ((1, 1), (0, 1))), (t, ((1, 0), (1, 1)))):
            nxt = compose(current, generator)
            image = mul2(rho[current], matrix)
            if nxt in rho:
                require(rho[nxt] == image, "representation drift")
            else:
                rho[nxt] = image
                pending.append(nxt)
    require(len(set(map(tuple, rho.values()))) == 6, "representation is not faithful")
    table = [[index[compose(left, right)] for right in group] for left in group]
    identity_index = index[identity]

    def plus(element):
        return tuple(tuple(rho[element][i][j] ^ eye[i][j] for j in range(2)) for i in range(2))

    length = {identity: 0}
    steps = {identity: ()}
    queue = deque([identity])
    while queue:
        current = queue.popleft()
        for generator in generators:
            nxt = compose(current, generator)
            if nxt not in length:
                length[nxt] = length[current] + 1
                steps[nxt] = steps[current] + (generator,)
                queue.append(nxt)

    def represented_rank(element):
        return rank(plus(element))

    gap = (2, 1, 0)
    require(length[gap] == 3 and represented_rank(gap) == 1, "transposition gap changed")
    length_two = tuple(element for element in group if length[element] == 2)
    require(len(length_two) == 2, "expected two length-two elements")
    for element in length_two:
        require(represented_rank(element) == 2, "length-two rank changed")

    projectors = tuple(tuple(tuple(int(i == row and j == row) for j in range(3))
                             for i in range(3)) for row in range(3))
    matched = 0
    floor_six = 0
    for labels in product(group, repeat=3):
        direct = sum(length[label] for label in labels)
        bound = sum(represented_rank(label) for label in labels)
        if direct != bound:
            require(gap in labels, "gap without the long transposition")
            continue
        matched += 1
        word = []
        for register, label in enumerate(labels):
            for generator in steps[label]:
                word.append((index[generator], projectors[register]))
        state = identity_matrix(identity_index)
        for label_index, projector in word:
            state = matrix_mul(state, paid(label_index, projector, identity_index), table)
        require(state == diagonal(tuple(index[label] for label in labels)), "coordinate word missed")
        if bound == 6:
            floor_six += 1
            require(set(labels) <= set(length_two), "floor 6 left the length-two set")
    require(matched == 125 and floor_six == 8, "classification counts changed")

    # Published four-call control: diag(s, t, st) with st = s then t.
    st = compose(s, t)
    published = [(index[s], projectors[0]), (index[t], projectors[1]),
                 (index[s], projectors[2]), (index[t], projectors[2])]
    state = identity_matrix(identity_index)
    for label_index, projector in published:
        state = matrix_mul(state, paid(label_index, projector, identity_index), table)
    require(state == diagonal((index[s], index[t], index[st])), "published witness drifted")
    require(length[s] + length[t] + length[st] == 4, "published bill is not 4")
    print("PASS_S3_DIAGONAL_RANK_SCREEN matched=125 floor6=8 gap=91")


if __name__ == "__main__":
    main()
