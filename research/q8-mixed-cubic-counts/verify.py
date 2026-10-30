"""Finite corroboration of a written mixed-Q8 bound. Apache-2.0."""

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as m
import oracle as o

ROOT = Path(__file__).resolve().parent


def hamilton_product(a, b):
    sign_a, a = divmod(a, 4)
    sign_b, b = divmod(b, 4)
    if a == 0 or b == 0:
        return 4 * (sign_a ^ sign_b) + (a or b)
    if a == b:
        return 4 * (sign_a ^ sign_b ^ 1)
    negative = (a, b) not in ((1, 2), (2, 3), (3, 1))
    return 4 * (sign_a ^ sign_b ^ int(negative)) + (6 - a - b)


def algebra_checks():
    conversion = o.coordinates()
    for a, b in product(range(8), repeat=2):
        m.require(o.GROUP[a][b] == hamilton_product(a, b), "Hamilton product table")
    for a, b, c in product(range(8), repeat=3):
        m.require(o.GROUP[o.GROUP[a][b]][c] == o.GROUP[a][o.GROUP[b][c]],
                  "Hamilton associativity")
    m.require(o.BASIS == (1, 3, 5, 17, 15, 51, 85, 255), "basis identity")
    m.require(conversion[o.algebra(5, 3)] == 248, "noncommuting pair")
    for value in range(256):
        m.require(o.algebra(255, value) in (0, 255)
                  and o.algebra(value, 255) in (0, 255), "socle ideal")
    for a, b in product(range(2), repeat=2):
        pair = conversion[o.algebra((3, 5)[a], (3, 5)[b])]
        m.require((pair >> 3) & 1 == int((a, b) != (0, 1)), "quadratic pair table")
        m.require((pair >> 5 ^ pair >> 6) & 1 == 0, "pair cubic cancellation")
    for a, b, c, d in product((3, 5), repeat=4):
        packet = o.algebra(o.algebra(o.algebra(a, b), c), d)
        m.require(packet in (0, 255), "four-increment socle")
    for increment in (3, 5):
        m.require(o.algebra(255, increment) == o.algebra(increment, 255) == 0,
                  "higher-increment vanishing")
    triples = []
    for a, b, c in product(range(2), repeat=3):
        packet = o.algebra(o.algebra((3, 5)[a], (3, 5)[b]), (3, 5)[c])
        coordinates = conversion[packet]
        actual = (coordinates >> 5 ^ coordinates >> 6) & 1
        expected = int((a, b) != (0, 1)) * int((b, c) != (0, 1))
        expected ^= int(a == 0 and c == 1)
        m.require(actual == expected, "mixed cubic table")
        triples.append([a, b, c, coordinates, actual])
    return conversion, triples


def fixture_words():
    rng = random.Random(182034)
    fixtures = []
    for case in range(240):
        roles = 1 + case % 6
        word = []
        for _ in range(case % 13):
            u = rng.randrange(1, 1 << roles)
            choices = tuple(v for v in range(1, 1 << roles) if (u & v).bit_count() % 2)
            word.append((u, rng.choice(choices), rng.randrange(2)))
        fixtures.append((roles, tuple(word)))
    fixtures.append((1, ((1, 1, 1), (1, 1, 0), (1, 1, 0))))
    return tuple(fixtures)


def matrix_action_checks(conversion):
    columns = 0
    digest = hashlib.sha256()
    fixtures = fixture_words()
    for roles, word in fixtures:
        predicted = m.predicted(roles, word)
        actual = o.coefficients(roles, word, conversion)
        m.require(actual == predicted, "independent matrix/action coefficient mismatch")
        _, _, _, _, correction, _ = m.call_matrices(roles, word)
        ni = sum(label == 0 for _, _, label in word)
        m.require(m.rank(correction) <= min(ni, len(word) - ni), "cross rank cap")
        digest.update(json.dumps([roles, word, actual], separators=(",", ":")).encode())
        columns += roles
    x, y, _, h, correction, _ = m.call_matrices(*fixtures[-1])
    m.require(m.multiply(m.multiply(x, correction), y) == (1,), "cross-term control")
    m.require(m.multiply(m.multiply(x, m.multiply(h, h)), y) != (1,),
              "naive homogeneous cubic control")
    return {"fixtures": len(fixtures), "group_identity_columns": columns,
            "stream_sha256": digest.hexdigest()}


def lemma_measure(x, y, k):
    n, t = len(k), len(x)
    m.require(m.rank(k) == n, "lemma needs invertibility")
    m.require(m.multiply(x, y) == m.identity(t), "lemma needs XY identity")
    m.require(m.multiply(m.multiply(x, k), y) == (0,) * t, "lemma needs XKY zero")
    actual = m.rank(m.multiply(m.multiply(m.multiply(x, k), k), y))
    m.require(actual >= 3 * t - n, "subspace rank inequality")
    return actual


def rank_fixtures():
    results = []
    for t in range(1, 5):
        for two_cycles in range(t + 1):
            sizes = (2,) * two_cycles + (3,) * (t - two_cycles)
            n = sum(sizes)
            k, starts = [0] * n, []
            offset = 0
            for size in sizes:
                starts.append(offset)
                for r in range(size):
                    k[offset + (r + 1) % size] = 1 << (offset + r)
                offset += size
            x = tuple(1 << start for start in starts)
            y = tuple(sum(int(r == start) << c for c, start in enumerate(starts))
                      for r in range(n))
            actual = lemma_measure(x, y, tuple(k))
            m.require(actual == two_cycles == 3 * t - n, "sharp rank fixture")
            results.append([t, n, actual])
    return results


def endpoint_checks():
    endpoints = columns = omissions = 0
    for t in range(1, 5):
        for labels, signs in product(product(range(2), repeat=t), repeat=2):
            word = tuple(gate for r in range(t) for gate in
                         ((1 << r, 1 << r, labels[r]),
                          (1 << r, 1 << r, signs[r]), (1 << r, 1 << r, signs[r])))
            ni = sum(label == 0 for _, _, label in word)
            ti = labels.count(0)
            m.require(m.count_constraints(ti, t - ti, ni, len(word) - ni), "direct count")
            for dirty in (0, 2):
                roles = t + dirty
                for source, group in product(range(roles), range(8)):
                    actual = o.act(roles, word, source, group)
                    target = labels[source] + 5 if source < t else 0
                    expected = tuple((1 << o.GROUP[target][group]) if r == source else 0
                                     for r in range(roles))
                    m.require(actual == expected, "full dirty endpoint")
                    columns += 1
                endpoints += 1
            for deleted in range(len(word)):
                reduced = word[:deleted] + word[deleted + 1:]
                m.require(any(o.act(t, reduced, r, 0)[r] != 1 << (labels[r] + 5)
                              for r in range(t)), "deleted call escaped")
                omissions += 1
    return {"endpoints": endpoints, "faithful_dirty_columns": columns,
            "deleted_factor_controls": omissions}


def retained_fixture(conversion):
    witness = json.loads((ROOT / "inputs/pr3551-WITNESS.json").read_text())
    word = tuple((u, v, label - 1) for u, v, label in witness["word"])
    coefficients = o.coefficients(4, word, conversion)
    m.require(coefficients == m.predicted(4, word), "retained cubic identity")
    m.require(coefficients[:2] == (m.identity(4), m.identity(4)), "quadratic fixture")
    defect = m.add(coefficients[2], m.identity(4))
    m.require(list(defect) == witness["cubic_defect"] and m.rank(defect) == 4,
              "retained full-rank cubic defect")
    m.require(not m.count_constraints(4, 0, 8, 0), "cubic excludes retained false positive")
    return {"cubic_defect": defect, "rank": 4, "paid_counts": [8, 0]}


def sources():
    retention = json.loads((ROOT / "inputs/RETENTION.json").read_text())
    m.require(len(retention["files"]) == 3, "retained inventory capacity")
    expected = {"inputs/pr3536-PROOF.md", "inputs/pr3558-PROOF.md", "inputs/pr3551-WITNESS.json"}
    m.require({item["retained_path"] for item in retention["files"]} == expected,
              "retained inventory paths")
    for item in retention["files"]:
        m.require(hashlib.sha256((ROOT / item["retained_path"]).read_bytes()).hexdigest()
                  == item["sha256"], "retained source changed")
    names = ("model.py", "oracle.py", "verify.py", "test_package.py", "PROOF.md",
             "inputs/RETENTION.json", *(item["retained_path"] for item in retention["files"]))
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}


def build():
    conversion, triples = algebra_checks()
    m.require(m.count_floor(3, 1) == m.count_floor(1, 3) == 10, "mixed 3/1 count floor")
    m.require(m.count_floor(4, 0) == m.count_floor(2, 2) == 8, "undecided shape control")
    m.require(not m.count_constraints(3, 1, 3, 5)
              and not m.count_constraints(3, 1, 5, 3), "new parity exclusion")
    return {"claim": "n+min(n_i,n_j)>=3t for all-negative formal Q8 endpoints",
            "scope": "Author-written proof, finite corroboration; 3/1 minimum is ten or twelve",
            "basis": o.BASIS, "triple_table": triples,
            "matrix_action": matrix_action_checks(conversion), "rank_fixtures": rank_fixtures(),
            "direct_endpoints": endpoint_checks(), "retained_false_positive": retained_fixture(conversion),
            "count_floor_3_1": 10, "sources_sha256": sources()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(build()))
    if args.write:
        with args.write.open("x") as output:
            output.write(json.dumps(result, indent=2) + "\n")
    else:
        m.require(result == json.loads((ROOT / "RESULT.json").read_text()), "receipt mismatch")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
