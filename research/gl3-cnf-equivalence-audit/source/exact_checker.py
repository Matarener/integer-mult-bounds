"""Independent set/row-tuple replay; no solver or search-model imports.

Brian Ross, with substantial OpenAI Codex assistance. Apache-2.0.
Model lineage: Hanson Sun seed18; Josie Elliston length10/engine3.cpp.
"""
import argparse
import itertools
import json

IDENTITY = (1, 2, 4)
TARGET = ((1, 4, 3), (2, 4, 3), IDENTITY)


def product(a, b):
    # Deliberately entrywise, unlike the model's packed row-combination product.
    return tuple(sum((sum(((a[r] >> k) & 1) * ((b[k] >> c) & 1)
                         for k in range(3)) % 2) << c for c in range(3))
                 for r in range(3))


def group():
    answer = []
    for rows in itertools.product(range(1, 8), repeat=3):
        span = {0}
        for row in rows:
            span |= {x ^ row for x in list(span)}
        if len(span) == 8:
            answer.append(rows)
    assert len(answer) == 168
    return answer


def validate_word(word):
    for gate in word:
        if not isinstance(gate, (list, tuple)) or len(gate) != 4:
            raise ValueError("each gate must be [u,v,address_row,address_column]")
        u, v, i, j = gate
        if any(type(x) is not int for x in gate):
            raise ValueError("gate entries must be integers")
        if not (1 <= u <= 7 and 1 <= v <= 7 and (u & v).bit_count() % 2):
            raise ValueError("not a rank-one idempotent")
        if i not in range(3) or j not in range(3) or i == j:
            raise ValueError("not a coordinate CNOT")


def column(word, input_role, input_group=IDENTITY):
    validate_word(word)
    registers = [set(), set(), set()]
    registers[input_role].add(input_group)
    for u, v, i, j in word:
        source = set()
        for k in range(3):
            if v & (1 << k):
                source ^= registers[k]
        shifted = set()
        for matrix in source:
            rows = list(matrix)
            rows[i] ^= rows[j]
            shifted.add(tuple(rows))
        delta = source ^ shifted
        for k in range(3):
            if u & (1 << k):
                registers[k] ^= delta
    return registers


def check(word, target=TARGET, all_columns=True):
    """Full regular action checks all 3*168 basis inputs, including dirty role."""
    validate_word(word)
    failures = []
    basis = group() if all_columns else [IDENTITY]
    for role in range(3):
        for address in basis:
            expected = [set(), set(), set()]
            expected[role].add(product(target[role], address))
            actual = column(word, role, address)
            if actual != expected:
                failures.append({"role": role, "address": list(address)})
    return {"accepted": not failures, "paid_calls": len(word),
            "basis_columns_checked": 3 * len(basis),
            "failing_columns": len(failures), "first_failure": failures[:1]}


def natural_rows(word):
    validate_word(word)
    rows = [1 << k for k in range(9)]
    for u, v, i, j in word:
        source = 0
        for k in range(3):
            if v & (1 << k):
                source ^= rows[3 * k + j]
        for k in range(3):
            if u & (1 << k):
                rows[3 * k + i] ^= source
    return rows


def natural_target(target):
    return [target[r][i] << (3 * r) for r in range(3) for i in range(3)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("witness", help="JSON object with word_uvij")
    args = parser.parse_args()
    with open(args.witness, encoding="utf-8") as stream:
        witness = json.load(stream)
    report = check(witness["word_uvij"])
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["accepted"] else 1)
