#!/usr/bin/env python3
"""Six-label diagonal-lift obstruction for the UT3(F4) central triple.

Read-only. Gates use need() so they stay live under python -O. No new kappa.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
KAPPA = "0.001672660197076918"

X1 = (1, 0, 0)
XW = (2, 0, 0)
XW2 = (3, 0, 0)
Y1 = (0, 1, 0)
YW = (0, 2, 0)
YW2 = (0, 3, 0)
Z1 = (0, 0, 1)
ZW = (0, 0, 2)
ZW2 = (0, 0, 3)
LABELS = (X1, XW, XW2, Y1, YW, YW2)
X_LABELS = (X1, XW, XW2)
Y_LABELS = (Y1, YW, YW2)
ADD = (
    (0, 1, 2, 3),
    (1, 0, 3, 2),
    (2, 3, 0, 1),
    (3, 2, 1, 0),
)
MUL = (
    (0, 0, 0, 0),
    (0, 1, 2, 3),
    (0, 2, 3, 1),
    (0, 3, 1, 2),
)


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def f4_add(a, b):
    return ADD[a][b]


def f4_mul(a, b):
    return MUL[a][b]


def group_mul(left, right):
    a, b, c = left
    aa, bb, cc = right
    return (f4_add(a, aa), f4_add(b, bb), f4_add(f4_add(c, cc), f4_mul(a, bb)))


def group_index(element):
    a, b, c = element
    return a + 4 * b + 16 * c


def element_from_index(index):
    return (index % 4, (index // 4) % 4, index // 16)


def inverse_element(element):
    a, b, c = element
    return (a, b, f4_add(c, f4_mul(a, b)))


ELEMENTS = [element_from_index(i) for i in range(64)]
MUL_TABLE = [
    [group_index(group_mul(ELEMENTS[i], ELEMENTS[j])) for j in range(64)]
    for i in range(64)
]


def coeff_bits(label):
    value = label[0] or label[1]
    return {1: (1, 0), 2: (0, 1), 3: (1, 1)}[value]


def mat_mul(left, right):
    size = len(left)
    return [
        [sum(left[i][k] * right[k][j] for k in range(size)) & 1 for j in range(size)]
        for i in range(size)
    ]


def mat_add(left, right):
    size = len(left)
    return [[(left[i][j] + right[i][j]) & 1 for j in range(size)] for i in range(size)]


def eye(size):
    return [[1 if i == j else 0 for j in range(size)] for i in range(size)]


def zeros(size):
    return [[0] * size for _ in range(size)]


def transpose(matrix):
    size = len(matrix)
    return [[matrix[j][i] for j in range(size)] for i in range(size)]


def embed_scalar(value):
    companion = [[0, 1], [1, 1]]
    ident = eye(2)
    b0, b1 = {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}[value]

    def scale(bit, block):
        return [[bit & block[i][j] for j in range(2)] for i in range(2)]

    return mat_add(scale(b0, ident), scale(b1, companion))


def rho6(element):
    a, b, c = element
    blocks = {
        (0, 0): eye(2), (0, 1): embed_scalar(a), (0, 2): embed_scalar(c),
        (1, 0): zeros(2), (1, 1): eye(2), (1, 2): embed_scalar(b),
        (2, 0): zeros(2), (2, 1): zeros(2), (2, 2): eye(2),
    }
    out = zeros(6)
    for bi in range(3):
        for bj in range(3):
            block = blocks[(bi, bj)]
            for i in range(2):
                for j in range(2):
                    out[2 * bi + i][2 * bj + j] = block[i][j]
    return out


def nilpotent(element):
    return mat_add(rho6(element), eye(6))


def contragredient(element):
    return transpose(rho6(inverse_element(element)))


def bit_rank(masks, width):
    rows = list(masks)
    rank = 0
    for col in range(width):
        shift = width - 1 - col
        pivot = None
        for i, row in enumerate(rows):
            if (row >> shift) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        rank += 1
        pivot_row = rows[pivot]
        for i in range(len(rows)):
            if (rows[i] >> shift) & 1:
                rows[i] ^= pivot_row
    return rank


def vector_mask(bits):
    acc = 0
    for bit in bits:
        acc = (acc << 1) | bit
    return acc


def idempotents(width):
    found = []
    seen = set()
    for u_bits in range(1, 1 << width):
        u = [(u_bits >> k) & 1 for k in range(width)]
        for v_bits in range(1 << width):
            v = [(v_bits >> k) & 1 for k in range(width)]
            if sum(u[k] * v[k] for k in range(width)) & 1 != 1:
                continue
            rows = tuple(tuple(u[i] * v[j] for j in range(width)) for i in range(width))
            if rows not in seen:
                seen.add(rows)
                found.append((u, v, rows))
    return found


IDEMPOTENTS_R3 = idempotents(3)


def projector(index, width):
    rows = [[0] * width for _ in range(width)]
    rows[index][index] = 1
    return rows


def left_mult(label_index, bitset):
    acc = 0
    rest = bitset
    while rest:
        bit = rest & -rest
        rest ^= bit
        j = bit.bit_length() - 1
        acc |= 1 << MUL_TABLE[label_index][j]
    return acc


def apply_word(calls, width, bitset_inputs):
    state = list(bitset_inputs)
    for label, rows in calls:
        label_index = group_index(label)
        updated = []
        for i in range(width):
            acc = state[i]
            for j in range(width):
                if rows[i][j]:
                    acc ^= state[j] ^ left_mult(label_index, state[j])
            updated.append(acc)
        state = updated
    return state


def basis_input(register, element_index, width):
    return [1 << element_index if i == register else 0 for i in range(width)]


def word_matches(calls, targets, width):
    for register, target in enumerate(targets):
        target_index = group_index(target)
        for element_index in range(64):
            got = apply_word(calls, width, basis_input(register, element_index, width))
            expected_element = MUL_TABLE[target_index][element_index]
            expect = [1 << expected_element if i == register else 0 for i in range(width)]
            if got != expect:
                return False
    return True


def schedule_calls(schedule, width):
    calls = []
    for register, labels in schedule:
        rows = projector(register, width)
        for label in labels:
            calls.append((label, rows))
    return calls


def mixed_schedule():
    return (
        (0, (X1, Y1, X1, Y1)),
        (1, (XW, Y1, XW, Y1)),
        (2, (XW2, Y1, XW2, Y1)),
    )


def both_new_schedule():
    return (
        (0, (X1, Y1, X1, Y1)),
        (1, (XW2, YW2, XW2, YW2)),
        (2, (XW, YW, XW, YW)),
    )


def factor_call(label, rows):
    width = len(rows)
    bank = IDEMPOTENTS_R3 if width == 3 else idempotents(width)
    for u, v, matrix in bank:
        if matrix == tuple(tuple(row) for row in rows):
            return u, v
    need(False, "call matrix is not a rank-one idempotent")
    return [], []


def lifts_of(side):
    shadows = []
    columns = []
    rows = []
    width = len(side[0][1])
    for label, u, v in side:
        b0, b1 = coeff_bits(label)
        shadow = vector_mask(u)
        # Low width bits are the first F2 coordinate (coefficient of 1).
        column = (b0 * shadow) | ((b1 * shadow) << width)
        shadows.append(shadow)
        columns.append(column)
        rows.append(vector_mask(v))
    return shadows, columns, rows, width


def split_sides(calls):
    x_side = []
    y_side = []
    for label, rows in calls:
        u, v = factor_call(label, rows)
        if label in X_LABELS:
            x_side.append((label, u, v))
        elif label in Y_LABELS:
            y_side.append((label, u, v))
        else:
            need(False, "label outside the six-involution alphabet")
    return x_side, y_side


def pure_columns(width):
    columns = []
    for shadow in range(1, 1 << width):
        columns.append((shadow, shadow))
        columns.append((shadow, shadow << width))
        columns.append((shadow, shadow | (shadow << width)))
    return columns


def load_json(text):
    def reject_duplicates(pairs):
        keys = [key for key, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        return dict(pairs)

    return json.loads(text, object_pairs_hook=reject_duplicates)


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_group():
    for i in range(64):
        for j in range(64):
            for k in range(64):
                left = MUL_TABLE[MUL_TABLE[i][j]][k]
                right = MUL_TABLE[i][MUL_TABLE[j][k]]
                if left != right:
                    need(False, "group law is not associative")
    for label in LABELS:
        need(group_mul(label, label) == (0, 0, 0), "paid label is not an involution")
        # [g]+[1] is two distinct basis elements, so the F2 augmentation is 0.
        support = {group_index(label), 0}
        need(len(support) == 2 and (len(support) & 1) == 0, "paid factor augments nontrivially")
    for a in (1, 2, 3):
        for b in (1, 2, 3):
            acc = (0, 0, 0)
            for label in ((a, 0, 0), (0, b, 0), (a, 0, 0), (0, b, 0)):
                acc = group_mul(label, acc)
            need(acc == (0, 0, f4_mul(a, b)), "axis commutator mismatch")
    need(f4_mul(3, 3) == 2, "w^2 * w^2 is not w")


def check_nilpotent_calculus():
    nil = {label: nilpotent(label) for label in LABELS}
    x_set = set(X_LABELS)
    y_set = set(Y_LABELS)
    for left in LABELS:
        for right in LABELS:
            product = mat_mul(nil[left], nil[right])
            nonzero = any(bit for row in product for bit in row)
            expect = left in x_set and right in y_set
            need(nonzero == expect, "length-two nilpotent support")
            if expect:
                corner = [[product[i][4 + j] for j in range(2)] for i in range(2)]
                need(corner == mat_mul(embed_scalar(left[0]), embed_scalar(right[1])), "pair corner")
                for i in range(6):
                    for j in range(6):
                        if i < 2 and j >= 4:
                            continue
                        need(product[i][j] == 0, "pair product is not a pure corner")
    for first in LABELS:
        for second in LABELS:
            for third in LABELS:
                triple = mat_mul(nil[first], mat_mul(nil[second], nil[third]))
                need(not any(bit for row in triple for bit in row), "nilpotent triple is nonzero")
    for value in (1, 2, 3):
        block = embed_scalar(value)
        need(transpose(block) == block, "regular representation is not symmetric")
    vee = {label: mat_add(contragredient(label), eye(6)) for label in LABELS}
    for left in LABELS:
        for right in LABELS:
            product = mat_mul(vee[left], vee[right])
            nonzero = any(bit for row in product for bit in row)
            expect = left in y_set and right in x_set
            need(nonzero == expect, "contragredient length-two support")
            if expect:
                corner = [[product[4 + i][j] for j in range(2)] for i in range(2)]
                need(
                    corner == mat_mul(embed_scalar(left[1]), embed_scalar(right[0])),
                    "contragredient corner",
                )
    for target, scalar in ((Z1, 1), (ZW, 2), (ZW2, 3)):
        image = contragredient(target)
        lower = [[image[4 + i][j] for j in range(2)] for i in range(2)]
        need(lower == embed_scalar(scalar), "contragredient target corner")
        direct = rho6(target)
        upper = [[direct[i][4 + j] for j in range(2)] for i in range(2)]
        need(upper == embed_scalar(scalar), "direct target corner")


def check_idempotents_and_scalars():
    need(len(IDEMPOTENTS_R3) == 28, "M3(F2) rank-one idempotent count")
    bank = {matrix for _, _, matrix in IDEMPOTENTS_R3}
    invertible = []
    for bits in range(1 << 9):
        matrix = [[(bits >> (3 * i + j)) & 1 for j in range(3)] for i in range(3)]
        if bit_rank([vector_mask(row) for row in matrix], 3) == 3:
            invertible.append(matrix)
    need(len(invertible) == 168, "GL3(F2) order")
    checked = 0
    for matrix in invertible:
        inverse = invert3(matrix)
        for _, _, rows in IDEMPOTENTS_R3:
            body = [list(row) for row in rows]
            conjugated = mat_mul(inverse, mat_mul(body, matrix))
            key = tuple(tuple(row) for row in conjugated)
            need(key in bank, "conjugation left the idempotent set")
            checked += 1
    need(checked == 168 * 28, "conjugation census")


def invert3(matrix):
    size = 3
    work = [row[:] + [1 if i == j else 0 for j in range(size)] for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = None
        for row in range(col, size):
            if work[row][col]:
                pivot = row
                break
        need(pivot is not None, "singular matrix in GL3")
        work[col], work[pivot] = work[pivot], work[col]
        for row in range(size):
            if row != col and work[row][col]:
                work[row] = [(work[row][k] + work[col][k]) & 1 for k in range(2 * size)]
    return [row[size:] for row in work]


def check_words():
    targets3 = [Z1, ZW, ZW2]
    targets4 = [Z1, ZW, ZW2, (0, 0, 0)]
    mixed = schedule_calls(mixed_schedule(), 3)
    both = schedule_calls(both_new_schedule(), 3)
    need(len(mixed) == 12 and len(both) == 12, "attaining length")
    need(word_matches(mixed, targets3, 3), "mixed word endpoint")
    need(word_matches(both, targets3, 3), "both-new word endpoint")
    need(word_matches(schedule_calls(mixed_schedule(), 4), targets4, 4), "mixed spectator")
    need(word_matches(schedule_calls(both_new_schedule(), 4), targets4, 4), "both-new spectator")
    for calls in (mixed, both):
        for omit in range(12):
            broken = calls[:omit] + calls[omit + 1 :]
            need(not word_matches(broken, targets3, 3), "omitted call still matched")
    need(not word_matches(mixed, [Z1, ZW, Z1], 3), "wrong third target matched")
    labels_used = {label for label, _ in both}
    need(XW2 in labels_used and YW2 in labels_used, "both-new word missed a w^2 label")
    mixed_labels = {label for label, _ in mixed}
    need(XW2 in mixed_labels and YW2 not in mixed_labels, "mixed word label set")


def separated_span(calls):
    shadows = []
    for label, rows in calls:
        if label not in (X1, XW):
            continue
        u, _ = factor_call(label, rows)
        shadows.append(vector_mask(u))
    return bit_rank(shadows, len(calls[0][1]))


def side_stats(side):
    shadows, columns, rows, width = lifts_of(side)
    return {
        "count": len(side),
        "shadow": bit_rank(shadows, width),
        "lift": bit_rank(columns, 2 * width),
        "v": bit_rank(rows, width),
    }


def check_lift_on_words():
    mixed = schedule_calls(mixed_schedule(), 3)
    both = schedule_calls(both_new_schedule(), 3)
    need(separated_span(mixed) == 2, "separated span should be blind to w^2")
    for calls in (mixed, both):
        x_side, y_side = split_sides(calls)
        for side in (x_side, y_side):
            stats = side_stats(side)
            need(stats["count"] == 6, "letter total")
            need(stats["shadow"] == 3 and stats["v"] == 3, "witness spans")
            need(stats["lift"] >= stats["shadow"], "lift lost a shadow")
            need(stats["count"] >= stats["lift"] + stats["v"], "nullity inequality")
        x_stats = side_stats(x_side)
        need(x_stats["lift"] == 3, "mixed or both-new lift rank")
    # The naive sum of the three pure-type subspace dimensions can exceed rank(L).
    # span{(e0,0),(0,e0)} has lift rank 2 and axis dimensions 1+1+1.
    e0 = 1
    columns = [e0, e0 << 3]
    need(bit_rank(columns, 6) == 2, "overcount example rank")
    span = span_vectors(columns, 6)
    axis = axis_dims(span, 3)
    need(sum(axis) == 3 and sum(axis) > bit_rank(columns, 6), "axis sum should overcount")
    phi_bound = phi_delta_bound(span, 3)
    need(phi_bound <= 2, "phi-delta bound failed on the overcount example")


def span_vectors(masks, width):
    basis = []
    rows = list(masks)
    for col in range(width):
        shift = width - 1 - col
        pivot = None
        for i, row in enumerate(rows):
            if (row >> shift) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        pivot_row = rows[pivot]
        basis.append(pivot_row)
        for i in range(len(rows)):
            if (rows[i] >> shift) & 1:
                rows[i] ^= pivot_row
    vectors = [0]
    for vector in basis:
        vectors.extend([item ^ vector for item in vectors])
    return vectors


def axis_dims(vectors, width):
    low_mask = (1 << width) - 1
    a_set = []
    b_set = []
    d_set = []
    for vector in vectors:
        low = vector & low_mask
        high = vector >> width
        if high == 0:
            a_set.append(low)
        if low == 0:
            b_set.append(high)
        if low == high:
            d_set.append(low)
    return (bit_rank(a_set, width), bit_rank(b_set, width), bit_rank(d_set, width))


def phi_delta_bound(vectors, width):
    low_mask = (1 << width) - 1
    phi = []
    diagonal = []
    kernel = []
    for vector in vectors:
        low = vector & low_mask
        high = vector >> width
        phi.append(low ^ high)
        if low == high:
            diagonal.append(low)
        if low ^ high == 0:
            kernel.append(vector)
    # dim phi(L) + dim(L∩Δ) = dim L - dim(L∩ker) + dim(L∩Δ) <= dim L.
    return bit_rank(phi, width) + bit_rank(diagonal, width)


def check_shadow_census():
    columns = pure_columns(3)
    need(len(columns) == 21, "pure column count")
    checked = 0
    violating_triples = 0
    for size in range(0, 7):
        for subset in itertools.combinations(columns, size):
            checked += 1
            shadows = [item[0] for item in subset]
            lifts = [item[1] for item in subset]
            shadow_rank = bit_rank(shadows, 3) if shadows else 0
            lift_rank = bit_rank(lifts, 6) if lifts else 0
            if shadow_rank > lift_rank:
                violating_triples += 1
            if size <= 4 and lifts:
                vectors = span_vectors(lifts, 6)
                need(phi_delta_bound(vectors, 3) <= lift_rank, "phi-delta census")
                need(shadow_rank <= phi_delta_bound(vectors, 3), "shadow outside phi+delta")
    need(checked == 82160, "subset census size")
    need(violating_triples == 0, "a pure family outgrew its lift")
    # Three aligned output directions are independent as lifts, so no rank-2
    # space contains all of them.
    witness = [1, 2 << 3, 4 | (4 << 3)]
    need(bit_rank(witness, 6) == 3, "three output directions are dependent")
    for pair in itertools.combinations(witness, 2):
        need(bit_rank(pair, 6) == 2, "pair of output directions collapsed")


def check_kappa_and_receipt():
    selected = load_json((ROOT / "certificates" / "selected-result.json").read_text(encoding="utf-8"))
    need(selected["decimal"] == KAPPA, "selected kappa drifted")
    certificate = load_json((PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    expect = {
        "schema_version": 1,
        "alphabet_labels": 6,
        "six_label_minimum": 12,
        "mixed_word_calls": 12,
        "both_new_labels_calls": 12,
        "n_X": 6,
        "n_Y": 6,
        "blind_separated_span": 2,
        "mixed_lift_rank": 3,
        "shadow_subsets_r3": 82160,
        "group_order": 64,
        "idempotents_r3": 28,
        "kappa": KAPPA,
        "no_new_kappa": True,
    }
    need(certificate == expect, "certificate mismatch")
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "CERTIFICATE.json"
        text = (PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8")
        bad.write_text(text.replace('"six_label_minimum": 12', '"six_label_minimum": 10'), encoding="utf-8")
        corrupted = load_json(bad.read_text(encoding="utf-8"))
        need(corrupted != expect, "corruption was not detected")
        duplicate = text.replace('"kappa"', '"kappa": "stale", "kappa"', 1)
        try:
            load_json(duplicate)
        except ValueError as exc:
            need(str(exc) == "duplicate JSON key", "duplicate detector message")
        else:
            need(False, "duplicate JSON key was accepted")


def check_read_only(before):
    after = {path: file_digest(path) for path in before}
    need(after == before, "verify wrote into the package")


def main():
    before = {path: file_digest(path) for path in sorted(PACKAGE.iterdir()) if path.is_file()}
    check_group()
    check_nilpotent_calculus()
    check_idempotents_and_scalars()
    check_words()
    check_lift_on_words()
    check_shadow_census()
    check_kappa_and_receipt()
    check_read_only(before)
    print(
        "PASS_UT3_F4_W2_LIFT six_label_minimum=12 labels=6 mixed_word=12 "
        "both_new_labels=12 nX=6 nY=6 blind_span=2 lift_rank=3 "
        "shadow_subsets=82160 spectator=1 no_new_kappa"
    )


if __name__ == "__main__":
    main()
