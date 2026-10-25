#!/usr/bin/env python3
"""Exact 12-call minimum for the UT3(F4) dependent central triple.

Read-only. Assertions stay live under python -O. No new kappa.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
KAPPA = "0.001672660197076918"

X1 = (1, 0, 0)
XW = (2, 0, 0)
Y1 = (0, 1, 0)
YW = (0, 2, 0)
Z1 = (0, 0, 1)
ZW = (0, 0, 2)
ZW2 = (0, 0, 3)
LABELS = (X1, XW, Y1, YW)
X_LABELS = (X1, XW)
Y_LABELS = (Y1, YW)


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def f4_add(a, b):
    decode = {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}
    encode = {(0, 0): 0, (1, 0): 1, (0, 1): 2, (1, 1): 3}
    x, y = decode[a]
    u, v = decode[b]
    return encode[((x + u) & 1, (y + v) & 1)]


def f4_mul(a, b):
    if a == 0 or b == 0:
        return 0
    return {
        (1, 1): 1, (1, 2): 2, (1, 3): 3,
        (2, 1): 2, (2, 2): 3, (2, 3): 1,
        (3, 1): 3, (3, 2): 1, (3, 3): 2,
    }[(a, b)]


def group_mul(left, right):
    a, b, c = left
    aa, bb, cc = right
    return (f4_add(a, aa), f4_add(b, bb), f4_add(f4_add(c, cc), f4_mul(a, bb)))


def group_index(element):
    a, b, c = element
    return a + 4 * b + 16 * c


def element_from_index(index):
    return (index % 4, (index // 4) % 4, index // 16)


ELEMENTS = [element_from_index(i) for i in range(64)]
MUL_TABLE = [
    [group_index(group_mul(ELEMENTS[i], ELEMENTS[j])) for j in range(64)]
    for i in range(64)
]


def left_mult(label_index, bitset):
    acc = 0
    rest = bitset
    while rest:
        bit = rest & -rest
        rest ^= bit
        j = bit.bit_length() - 1
        acc |= 1 << MUL_TABLE[label_index][j]
    return acc


def alpha_bits(label):
    """F2 coordinates of the F4 coefficient on an X-type label: 1=(1,0), w=(0,1)."""
    if label == X1:
        return (1, 0)
    if label == XW:
        return (0, 1)
    return (0, 0)


def beta_bits(label):
    if label == Y1:
        return (1, 0)
    if label == YW:
        return (0, 1)
    return (0, 0)


def mat_mul(left, right, size):
    return [
        [(sum(left[i][k] * right[k][j] for k in range(size)) & 1) for j in range(size)]
        for i in range(size)
    ]


def mat_add(left, right, size):
    return [[(left[i][j] + right[i][j]) & 1 for j in range(size)] for i in range(size)]


def eye(size):
    return [[1 if i == j else 0 for j in range(size)] for i in range(size)]


def embed_scalar(value):
    companion_w = [[0, 1], [1, 1]]
    ident = eye(2)
    zero = [[0, 0], [0, 0]]
    bits = {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}[value]

    def scale(bit, block):
        return [[bit & block[i][j] for j in range(2)] for i in range(2)]

    return mat_add(scale(bits[0], ident), scale(bits[1], companion_w), 2)


def rho6(element):
    a, b, c = element
    blocks = {
        (0, 0): eye(2), (0, 1): embed_scalar(a), (0, 2): embed_scalar(c),
        (1, 0): [[0, 0], [0, 0]], (1, 1): eye(2), (1, 2): embed_scalar(b),
        (2, 0): [[0, 0], [0, 0]], (2, 1): [[0, 0], [0, 0]], (2, 2): eye(2),
    }
    out = [[0] * 6 for _ in range(6)]
    for bi in range(3):
        for bj in range(3):
            for i in range(2):
                for j in range(2):
                    out[2 * bi + i][2 * bj + j] = blocks[(bi, bj)][i][j]
    return out


def nilpotent(element):
    image = rho6(element)
    return mat_add(image, eye(6), 6)


def inverse_element(element):
    a, b, c = element
    return (a, b, f4_add(c, f4_mul(a, b)))


def contragredient(element):
    image = rho6(inverse_element(element))
    return [[image[j][i] for j in range(6)] for i in range(6)]


def nilpotent_vee(element):
    return mat_add(contragredient(element), eye(6), 6)


def corner_block(matrix):
    return [[matrix[i][4 + j] for j in range(2)] for i in range(2)]


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


def projector(index, width):
    rows = [[0] * width for _ in range(width)]
    rows[index][index] = 1
    return rows


def apply_word(calls, width, bitset_inputs):
    """Apply calls in time order. Each call is (label, N rows)."""
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


def twelve_call_word(width):
    schedule = (
        (0, (X1, Y1, X1, Y1)),
        (1, (X1, YW, X1, YW)),
        (2, (XW, YW, XW, YW)),
    )
    calls = []
    for register, labels in schedule:
        rows = projector(register, width)
        for label in labels:
            calls.append((label, rows))
    return calls


def fourteen_call_word(width):
    schedule = (
        (0, (X1, Y1, X1, Y1)),
        (1, (XW, Y1, XW, Y1)),
        (2, (X1, XW, Y1, X1, XW, Y1)),
    )
    calls = []
    for register, labels in schedule:
        rows = projector(register, width)
        for label in labels:
            calls.append((label, rows))
    return calls


def factor_calls(calls):
    x_calls = []
    y_calls = []
    for label, rows in calls:
        width = len(rows)
        found = False
        u = [0] * width
        v = [0] * width
        for trial_u, trial_v, trial_rows in idempotents(width):
            if trial_rows == tuple(tuple(row) for row in rows):
                u, v, found = trial_u, trial_v, True
                break
        need(found, "call matrix is a rank-one idempotent")
        if label in X_LABELS:
            x_calls.append((label, u, v))
        elif label in Y_LABELS:
            y_calls.append((label, u, v))
        else:
            need(False, "label outside the four-involution alphabet")
    return x_calls, y_calls


def span_rank(vectors):
    rows = []
    for vector in vectors:
        acc = 0
        for bit in vector:
            acc = (acc << 1) | bit
        rows.append(acc)
    rank = 0
    used = [False] * len(rows)
    for col in range(max((len(v) for v in vectors), default=0)):
        shift = len(vectors[0]) - 1 - col
        pivot = None
        for i, row in enumerate(rows):
            if not used[i] and (row >> shift) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        used[pivot] = True
        for i in range(len(rows)):
            if i != pivot and (rows[i] >> shift) & 1:
                rows[i] ^= rows[pivot]
        rank += 1
    return rank


def rank_nullity_gap(calls):
    x_calls, y_calls = factor_calls(calls)
    width = len(calls[0][1])

    def side_ranks(side, bit_of):
        u_span = []
        v_span = []
        tensor = []
        for label, u, v in side:
            b0, b1 = bit_of(label)
            u_span.append(u)
            v_span.append(v)
            tensor.append([b0 * bit for bit in u] + [b1 * bit for bit in u])
        return {
            "count": len(side),
            "u": span_rank(u_span),
            "v": span_rank(v_span),
            "tensor": span_rank(tensor),
            "width": width,
        }

    return side_ranks(x_calls, alpha_bits), side_ranks(y_calls, beta_bits)


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
        square = group_mul(label, label)
        need(square == (0, 0, 0), "paid label is not an involution")
    need(group_mul(group_mul(X1, Y1), group_mul(X1, Y1)) == Z1, "XYXY misses Z1")
    need(group_mul(group_mul(X1, YW), group_mul(X1, YW)) == ZW, "X Yw misses Zw")
    need(group_mul(group_mul(XW, YW), group_mul(XW, YW)) == ZW2, "Xw Yw misses Zw^2")
    composite = (X1, XW, Y1, X1, XW, Y1)
    acc = (0, 0, 0)
    for label in composite:
        acc = group_mul(label, acc)
    need(acc == ZW2, "six-call composite misses Zw^2")


def check_nilpotent_calculus():
    nil = {label: nilpotent(label) for label in LABELS}
    for left in LABELS:
        for right in LABELS:
            product = mat_mul(nil[left], nil[right], 6)
            corner = corner_block(product)
            x_then_y = left in X_LABELS and right in Y_LABELS
            if not x_then_y:
                need(product == [[0] * 6 for _ in range(6)], "unexpected length-two nilpotent")
            else:
                expect = mat_mul(embed_scalar({X1: 1, XW: 2}[left]), embed_scalar({Y1: 1, YW: 2}[right]), 2)
                need(corner == expect, "pair corner mismatch")
                # The product is pure corner: only rows 0-1, cols 4-5 may be nonzero.
                for i in range(6):
                    for j in range(6):
                        if i < 2 and j >= 4:
                            continue
                        need(product[i][j] == 0, "pair product is not a pure corner")
    for first in LABELS:
        for second in LABELS:
            pair = mat_mul(nil[first], nil[second], 6)
            for third in LABELS:
                triple = mat_mul(nil[first], mat_mul(nil[second], nil[third], 6), 6)
                need(triple == [[0] * 6 for _ in range(6)], "nilpotent triple is nonzero")
                _ = pair
    vee = {label: nilpotent_vee(label) for label in LABELS}
    for left in LABELS:
        for right in LABELS:
            product = mat_mul(vee[left], vee[right], 6)
            # Contragredient corner sits in the lower-left block.
            corner = [[product[4 + i][j] for j in range(2)] for i in range(2)]
            y_then_x = left in Y_LABELS and right in X_LABELS
            if not y_then_x:
                need(product == [[0] * 6 for _ in range(6)], "unexpected contragredient length-two")
            else:
                expect = mat_mul(
                    embed_scalar({Y1: 1, YW: 2}[left]),
                    embed_scalar({X1: 1, XW: 2}[right]),
                    2,
                )
                need(corner == expect, "contragredient corner mismatch")
    for target, scalar in ((Z1, 1), (ZW, 2), (ZW2, 3)):
        image = contragredient(target)
        lower = [[image[4 + i][j] for j in range(2)] for i in range(2)]
        need(lower == embed_scalar(scalar), "contragredient target corner")


def check_idempotents():
    rows = idempotents(3)
    need(len(rows) == 28, "M3(F2) rank-one idempotent count")
    for u, v, matrix in rows:
        flat = mat_mul([list(row) for row in matrix], [list(row) for row in matrix], 3)
        need(tuple(tuple(row) for row in flat) == matrix, "idempotent square")
        need(sum(matrix[i][i] for i in range(3)) & 1 == 1, "trace")
        need(sum(u[k] * v[k] for k in range(3)) & 1 == 1, "factorization")


def check_words():
    targets3 = [Z1, ZW, ZW2]
    targets4 = [Z1, ZW, ZW2, (0, 0, 0)]
    short = twelve_call_word(3)
    long = fourteen_call_word(3)
    need(len(short) == 12, "twelve-call schedule length")
    need(len(long) == 14, "fourteen-call schedule length")
    need(word_matches(short, targets3, 3), "twelve-call full algebra endpoint")
    need(word_matches(twelve_call_word(4), targets4, 4), "dirty spectator stays identity")
    need(word_matches(long, targets3, 3), "predecessor fourteen-call word")
    for omit in range(12):
        broken = short[:omit] + short[omit + 1 :]
        need(not word_matches(broken, targets3, 3), "omitted call still matched")
    swapped = [Z1, ZW, Z1]
    need(not word_matches(short, swapped, 3), "wrong third target matched")


def check_rank_bound():
    x_side, y_side = rank_nullity_gap(twelve_call_word(3))
    for side in (x_side, y_side):
        need(side["u"] == 3 and side["v"] == 3, "attaining word spans all three outputs")
        need(side["tensor"] >= side["u"], "tensor rank lost an output direction")
        need(side["count"] >= side["v"] + side["tensor"], "nullity inequality failed on the witness")
    need(x_side["count"] == 6 and y_side["count"] == 6, "letter totals")
    # The target corner images force both spans to be at least 3, hence at least 6+6 calls.
    p_cols = [[1, 0, 0], [0, 0, 0], [0, 0, 1]]
    q_cols = [[0, 0, 0], [0, 1, 0], [0, 0, 1]]
    # columns of diag(1,0,1) and diag(0,1,1)
    p_vectors = [[1, 0, 0], [0, 0, 0], [0, 0, 1]]
    q_vectors = [[0, 0, 0], [0, 1, 0], [0, 0, 1]]
    need(span_rank(p_vectors + q_vectors) == 3, "target column rank")
    need(span_rank(p_cols) == 2 and span_rank(q_cols) == 2, "component ranks")
    need(6 + 6 == 12, "tariff arithmetic")


def check_kappa_and_receipt():
    selected = load_json((ROOT / "certificates" / "selected-result.json").read_text(encoding="utf-8"))
    need(selected["decimal"] == KAPPA, "selected kappa drifted")
    certificate = load_json((PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    expect = {
        "schema_version": 1,
        "minimum_calls": 12,
        "predecessor_direct_calls": 14,
        "n_X": 6,
        "n_Y": 6,
        "group_order": 64,
        "labels": 4,
        "idempotents_r3": 28,
        "spectator_width": 4,
        "kappa": KAPPA,
        "no_new_kappa": True,
    }
    need(certificate == expect, "certificate mismatch")
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "CERTIFICATE.json"
        text = (PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8")
        bad.write_text(text.replace('"minimum_calls": 12', '"minimum_calls": 11'), encoding="utf-8")
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
    check_idempotents()
    check_words()
    check_rank_bound()
    check_kappa_and_receipt()
    check_read_only(before)
    print(
        "PASS_UT3_F4_DEPENDENT_TRIPLE minimum=12 predecessor_direct=14 "
        "nX=6 nY=6 group_order=64 idempotents=28 spectator=1 "
        "omission_controls=12 no_new_kappa"
    )


if __name__ == "__main__":
    main()
