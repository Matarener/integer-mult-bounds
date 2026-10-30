#!/usr/bin/env python3
"""Exact finite corroboration of the written cyclic cubic obstruction.

Nick Petalas. Apache-2.0. Universal quantifiers are proved in PROOF.md.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAX_ROLES = 8
MAX_CALLS = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(size):
    return tuple(1 << k for k in range(size))


def add(left, right):
    require(len(left) == len(right), "matrix shape")
    return tuple(a ^ b for a, b in zip(left, right, strict=True))


def multiply(left, right):
    require(len(right) <= 64, "matrix capacity")
    result = []
    for row in left:
        require(0 <= row < 1 << len(right), "matrix row width")
        value = 0
        for k, entry in enumerate(right):
            if row >> k & 1:
                value ^= entry
        result.append(value)
    return tuple(result)


def rank(rows):
    require(len(rows) <= 64, "rank capacity")
    pivots = [0] * 64
    count = 0
    for row in rows:
        require(0 <= row < 1 << 64, "rank row width")
        value = row
        for bit in range(63, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    count += 1
                    break
    return count


def projector(roles, u, v):
    require(type(roles) is int and 1 <= roles <= MAX_ROLES, "role capacity")
    require(type(u) is int and type(v) is int, "binary vectors")
    require(0 < u < 1 << roles and 0 < v < 1 << roles, "vector domain")
    require((u & v).bit_count() % 2 == 1, "projector idempotency")
    return tuple(v if u >> k & 1 else 0 for k in range(roles))


def coefficients(roles, word):
    require(len(word) <= MAX_CALLS, "call capacity")
    state = [identity(roles)] + [(0,) * roles for _ in range(3)]
    for u, v in word:
        factor = projector(roles, u, v)
        state = [state[0]] + [
            add(state[d], multiply(factor, state[d - 1]))
            for d in range(1, 4)
        ]
    return tuple(state)


def gram(word):
    require(1 <= len(word) <= MAX_CALLS, "Gram capacity")
    return tuple(
        sum(((v & u).bit_count() % 2) << k for k, (u, _) in enumerate(word))
        for _, v in word
    )


def ordered_data(roles, word):
    a = gram(word)
    lower = tuple(row & ((1 << k) - 1) for k, row in enumerate(a))
    x = tuple(sum(((u >> k) & 1) << j for j, (u, _) in enumerate(word))
              for k in range(roles))
    y = tuple(v for _, v in word)
    return a, lower, x, y


def q8_product(left, right):
    require(0 <= left < 8 and 0 <= right < 8, "Q8 domain")
    a, b = left % 4, left // 4
    c, d = right % 4, right // 4
    return (a + (1 if b == 0 else -1) * c + 2 * b * d) % 4 + 4 * ((b + d) % 2)


def gate_action(state, u, v, label):
    require(label in (1, 4), "single positive generator")
    projector(len(state), u, v)
    source = 0
    for k, value in enumerate(state):
        if v >> k & 1:
            source ^= value
    moved = 0
    for group in range(8):
        if source >> group & 1:
            moved ^= 1 << q8_product(label, group)
    delta = moved ^ source
    return tuple(value ^ (delta if u >> k & 1 else 0)
                 for k, value in enumerate(state))


def word_action(roles, word, label, column):
    require(0 <= column < 8 * roles, "input column")
    state = tuple(1 << (column % 8) if k == column // 8 else 0
                  for k in range(roles))
    for u, v in word:
        state = gate_action(state, u, v, label)
    return state


def polynomial_action(poly, label, column):
    roles = len(poly[0])
    source_role, group = divmod(column, 8)
    power = 1 << group
    result = [0] * roles
    for degree in range(4):
        for k, row in enumerate(poly[degree]):
            if row >> source_role & 1:
                result[k] ^= power
        moved = 0
        for basis in range(8):
            if power >> basis & 1:
                moved ^= 1 << q8_product(label, basis)
        power ^= moved
    return tuple(result)


def matrix_cases(t):
    """All K with A K A=0 for the displayed canonical projection A."""
    require(t in (1, 2), "finite lemma domain")
    size = 2 * t
    mask = (1 << t) - 1
    projection = tuple(1 << k if k < t else 0 for k in range(size))
    tested = 0
    invertible = 0
    for raw in range(1 << (3 * t * t)):
        blocks = tuple((raw >> (j * t)) & mask for j in range(3 * t))
        k = tuple(blocks[j] << t for j in range(t)) + tuple(
            blocks[t + j] | blocks[2 * t + j] << t for j in range(t)
        )
        tested += 1
        if rank(k) != size:
            continue
        invertible += 1
        require(multiply(multiply(projection, k), projection) == (0,) * size,
                "off-diagonal premise")
        compressed = multiply(multiply(projection, multiply(k, k)), projection)
        require(rank(compressed) == t, "invertible block cubic lemma")
    return {"t": t, "all_off_diagonal_k": tested, "invertible_k": invertible}


def witness_check(root):
    witness = json.loads((root / "inputs/pr3551-WITNESS.json").read_text())
    require(witness["roles"] == 4 and witness["targets"] == [5] * 4, "witness target")
    require(all(g == 1 for _, _, g in witness["word"]), "cyclic witness labels")
    word = tuple((u, v) for u, v, _ in witness["word"])
    poly = coefficients(4, word)
    require([list(row) for row in poly] == witness["polynomial_coefficients"],
            "retained witness coefficients")
    a, lower, x, y = ordered_data(4, word)
    k = add(identity(8), lower)
    require(rank(a) == 4 and multiply(a, a) == a and rank(k) == 8, "saturation")
    require(multiply(multiply(a, k), a) == (0,) * 8, "quadratic equality")
    defect = add(poly[3], identity(4))
    compressed = multiply(multiply(y, defect), x)
    require(list(defect) == witness["cubic_defect"], "retained cubic defect")
    require(compressed == multiply(multiply(a, multiply(k, k)), a),
            "compressed cubic identity")
    require(rank(defect) == rank(compressed) == 4, "full-rank cubic defect")
    errors = []
    for column in range(32):
        state = word_action(4, word, 1, column)
        expected = tuple(1 << q8_product(3, column % 8)
                         if j == column // 8 else 0 for j in range(4))
        error = tuple(a ^ b for a, b in zip(state, expected, strict=True))
        errors.append(sum(value << (8 * j) for j, value in enumerate(error)))
    require(all(errors) and rank(errors) == 8, "full formal witness failure")
    return {"calls": 8, "targets": 4, "compressed_defect_rank": 4,
            "role_defect_rank": 4, "regular_error_rank": 8, "failed_columns": 32}


def generic_check():
    words = 0
    columns = 0
    for roles in (1, 2):
        alphabet = tuple((u, v) for u in range(1, 1 << roles)
                         for v in range(1, 1 << roles) if (u & v).bit_count() % 2)
        for length in range(5):
            for word in itertools.product(alphabet, repeat=length):
                poly = coefficients(roles, word)
                for label in (1, 4):
                    words += 1
                    for column in range(8 * roles):
                        require(word_action(roles, word, label, column)
                                == polynomial_action(poly, label, column),
                                "independent formal action")
                        columns += 1
    return {"labeled_words": words, "formal_columns": columns}


def attaining_check():
    endpoints = 0
    columns = 0
    omissions = 0
    for targets in range(1, 5):
        for dirt in (0, 1, 3):
            roles = targets + dirt
            word = tuple((1 << k, 1 << k) for k in range(targets) for _ in range(3))
            poly = coefficients(roles, word)
            p = tuple(1 << k if k < targets else 0 for k in range(roles))
            require(poly == (identity(roles), p, p, p), "attaining coefficients")
            for label in (1, 4):
                inverse = q8_product(q8_product(label, label), label)
                endpoints += 1
                for column in range(8 * roles):
                    role, group = divmod(column, 8)
                    expected_group = q8_product(inverse, group) if role < targets else group
                    expected = tuple(1 << expected_group if j == role else 0
                                     for j in range(roles))
                    require(word_action(roles, word, label, column) == expected,
                            "attaining dirty endpoint")
                    columns += 1
                for cut in range(len(word)):
                    broken = coefficients(roles, word[:cut] + word[cut + 1:])
                    require(broken != poly, "omitted paid factor")
                    omissions += 1
    return {"endpoints": endpoints, "formal_columns": columns, "omissions": omissions}


def source_check(root):
    pins = json.loads((root / "SOURCE_HASHES.json").read_text())
    require(isinstance(pins, dict) and 1 <= len(pins) <= 32, "source inventory")
    for name, digest in pins.items():
        path = root / name
        require(not path.is_symlink() and path.is_file(), "regular source")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                "source hash: " + name)
    retention = json.loads((root / "inputs/RETENTION.json").read_text())
    for row in retention["sources"]:
        raw = (root / row["retained_path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained SHA256")
        header = b"blob " + str(len(raw)).encode() + b"\0"
        require(hashlib.sha1(header + raw).hexdigest() == row["origin_blob"],
                "retained Git blob")
    return len(pins)


def lower_bound(targets):
    require(type(targets) is int and 1 <= targets <= 64, "target capacity")
    return 2 * targets + 1 + ((targets - 1) % 4)


def produce(root=ROOT):
    require(source_check(root) > 0, "authenticated runtime")
    return {"status": "PASS_CYCLIC_CUBIC_OBSTRUCTION",
            "finite_block_lemma": [matrix_cases(1), matrix_cases(2)],
            "saturated_witness": witness_check(root),
            "independent_action": generic_check(),
            "attaining_words": attaining_check(),
            "sharp_minima_t1_through_t4": [lower_bound(t) for t in range(1, 5)],
            "scope": "Written uniform cyclic proof; mixed labels and physical supplier unclaimed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a new exact receipt exclusively")
    args = parser.parse_args()
    result = produce()
    if args.write is not None:
        with args.write.open("x") as output:
            output.write(json.dumps(result, indent=2) + "\n")
    else:
        require(result == json.loads((ROOT / "RESULT.json").read_text()),
                "deterministic receipt changed")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
