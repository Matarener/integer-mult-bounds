"""Exact quadratic saturation and full-coefficient failure certificate. Apache-2.0."""

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as m
import oracle

ROOT = Path(__file__).resolve().parent


def source_check():
    records = json.loads((ROOT / "inputs/RETENTION.json").read_text())
    for row in records:
        raw = (ROOT / row["path"]).read_bytes()
        m.require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained source hash")
    return len(records)


def algebra_check():
    table = oracle.group_table()
    images = m.images()
    for g, h in product(range(8), repeat=2):
        m.require(m.group_product(g, h) == table[g][h], "Hamilton product")
        m.require(m.quotient_product(images[g], images[h]) == images[table[g][h]],
                  "quotient homomorphism")
    for a, b, c in product((1, 2, 4, 8, 16), repeat=3):
        m.require(m.quotient_product(m.quotient_product(a, b), c)
                  == m.quotient_product(a, m.quotient_product(b, c)), "associativity")
    m.require(images[5] == 11 and images[6] == 13, "negative endpoint image")
    return {"group_products": 64, "basis_associativity": 125}


def packet_column(matrix, column):
    c, h = divmod(column, 8)
    return tuple(sum(1 << m.group_product(g, h) for g in range(8) if row[c] >> g & 1)
                 for row in matrix)


def expected(targets, roles):
    return tuple(tuple((1 << targets[a] if a < len(targets) else 1) if a == b else 0
                       for b in range(roles)) for a in range(roles))


def faithful_check(word, roles, matrix):
    for column in range(roles * 8):
        m.require(packet_column(matrix, column) == oracle.action(word, roles, column),
                  "independent faithful action")
    return roles * 8


def witness_check():
    witness = json.loads((ROOT / "WITNESS.json").read_text())
    m.require(witness["roles"] == 4 and witness["targets"] == [5] * 4, "witness target")
    word = tuple(tuple(gate) for gate in witness["word"])
    m.require(len(word) == 8, "eight-call witness")
    actual = m.full_endpoint(word, 4)
    wanted = expected((5,) * 4, 4)
    coefficients = m.polynomial(word, 4)
    m.require(coefficients == tuple(tuple(row) for row in witness["polynomial_coefficients"]),
              "polynomial receipt")
    identity = (1, 2, 4, 8)
    defect = tuple(a ^ b for a, b in zip(coefficients[3], identity, strict=True))
    m.require(defect == tuple(witness["cubic_defect"]), "cubic defect receipt")
    m.require(m.rank(defect) == oracle.span_rank(defect) == 4, "invertible cubic defect")
    inverse = (2, 6, 8, 15)
    m.require(m.multiply(defect, inverse) == m.multiply(inverse, defect) == identity,
              "explicit defect inverse")
    m.require(m.project(actual) == m.project(wanted) and actual != wanted, "quotient false positive")
    delta = tuple(tuple(a ^ b for a, b in zip(row, target, strict=True))
                  for row, target in zip(actual, wanted, strict=True))
    m.require(delta == tuple(tuple(51 if row >> c & 1 else 0 for c in range(4))
                            for row in defect), "exact full-coefficient defect")
    gram = m.gram(word)
    h = m.chronological(gram, tuple(g for _, _, g in word))
    unit = tuple(row ^ (1 << k) for k, row in enumerate(h))
    m.require(m.rank(gram) == 4 and not any(m.multiply(m.multiply(gram, unit), gram)),
              "saturated half-call Gram invariant")
    return word, {"calls": len(word), "roles": 4, "gram_rank": 4,
                  "cubic_defect_rank": 4, "faithful_columns": faithful_check(word, 4, actual)}


def block_check(word):
    fixtures = columns = omissions = 0
    for blocks in range(1, 4):
        for g in (1, 2):
            target = g + 4
            roles = 4 * blocks + 2
            expanded = tuple((u << (4 * k), v << (4 * k), g)
                             for k in range(blocks) for u, v, _ in word)
            actual = m.full_endpoint(expanded, roles)
            wanted = expected((target,) * (4 * blocks), roles)
            m.require(m.project(actual) == m.project(wanted), "direct-sum quotient endpoint")
            m.require(actual != wanted, "full direct-sum rejection")
            errors = []
            for column in range(roles * 8):
                a = packet_column(actual, column)
                b = packet_column(wanted, column)
                errors.append(sum((x ^ y) << (8 * k)
                                  for k, (x, y) in enumerate(zip(a, b, strict=True))))
            m.require(m.rank(errors) == 8 * blocks, "regular defect rank")
            m.require(sum(bool(x) for x in errors) == 32 * blocks, "every active column fails")
            columns += faithful_check(expanded, roles, actual)
            for drop in range(len(expanded)):
                mutant = expanded[:drop] + expanded[drop + 1:]
                m.require(m.project(m.full_endpoint(mutant, roles)) != m.project(wanted),
                          "omitted factor rejected by quotient")
                omissions += 1
            fixtures += 1
    return {"fixtures": fixtures, "faithful_columns": columns, "omissions": omissions}


def generic_check():
    rng = random.Random(35363517)
    words = columns = 0
    for roles in range(2, 7):
        for length in range(1, 11):
            gates = []
            for _ in range(length):
                u = rng.randrange(1, 1 << roles)
                candidates = tuple(v for v in range(1, 1 << roles) if (u & v).bit_count() % 2)
                gates.append((u, rng.choice(candidates), rng.choice((1, 2))))
            word = tuple(gates)
            columns += faithful_check(word, roles, m.full_endpoint(word, roles))
            words += 1
    return {"words": words, "faithful_columns": columns}


def full_positive_controls():
    columns = omissions = 0
    for g in (1, 2):
        word = tuple((1 << k, 1 << k, g) for k in range(4) for _ in range(3))
        wanted = expected((g + 4,) * 4, 6)
        actual = m.full_endpoint(word, 6)
        m.require(actual == wanted, "twelve-call full positive control")
        columns += faithful_check(word, 6, actual)
        for drop in range(12):
            m.require(m.full_endpoint(word[:drop] + word[drop + 1:], 6) != wanted,
                      "full positive control omission")
            omissions += 1
    return {"fixtures": 2, "faithful_columns": columns, "omissions": omissions}


def result():
    source_count = source_check()
    algebra = algebra_check()
    word, witness = witness_check()
    return {"status": "PASS_Q8_QUADRATIC_SATURATION", "algebra": algebra,
            "retained_sources": source_count, "witness": witness,
            "direct_sums": block_check(word), "generic": generic_check(),
            "full_positive_controls": full_positive_controls(),
            "scope": "Exact quotient minimum 2t for homogeneous negative targets, t divisible by 4. "
                     "The displayed words fail full Q8 by an invertible cubic coefficient. "
                     "Full four-negative minimum and supplier/kappa are unclaimed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    actual = result()
    text = json.dumps(actual, indent=2) + "\n"
    if args.write is not None:
        with args.write.open("x", encoding="utf-8") as stream:
            m.require(stream.write(text) == len(text), "receipt write")
    else:
        m.require(actual == json.loads((ROOT / "RESULT.json").read_text()), "result receipt")
    print(text, end="")


if __name__ == "__main__":
    main()
