#!/usr/bin/env python3
"""Exact corroboration of the asymmetric UT3 tariff gap. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(r):
    require(1 <= r <= 6, "matrix dimension outside 1..6")
    return tuple(1 << i for i in range(r))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a, b):
    r = len(a)
    require(len(b) == r and 1 <= r <= 6, "matrix shape")
    rows = []
    for row in a:
        out = 0
        for j in range(r):
            if row >> j & 1:
                out ^= b[j]
        rows.append(out)
    return tuple(rows)


def rank(a):
    rows = list(a)
    r = len(rows)
    pivots = 0
    for j in range(r):
        candidates = [i for i in range(pivots, r) if rows[i] >> j & 1]
        if candidates:
            i = candidates[0]
            rows[pivots], rows[i] = rows[i], rows[pivots]
            for h in range(pivots + 1, r):
                if rows[h] >> j & 1:
                    rows[h] ^= rows[pivots]
            pivots += 1
    return pivots


def group_product(g, h):
    x, y, z = g & 1, g >> 1 & 1, g >> 2 & 1
    u, v, w = h & 1, h >> 1 & 1, h >> 2 & 1
    return (x ^ u) | ((y ^ v) << 1) | ((z ^ w ^ (x & v)) << 2)


def literal_product(g, h):
    a = ((1, g & 1, g >> 2 & 1), (0, 1, g >> 1 & 1), (0, 0, 1))
    b = ((1, h & 1, h >> 2 & 1), (0, 1, h >> 1 & 1), (0, 0, 1))
    c = [[sum(a[i][k] * b[k][j] for k in range(3)) % 2
          for j in range(3)] for i in range(3)]
    return c[0][1] | (c[1][2] << 1) | (c[0][2] << 2)


def algebra_product(a, b):
    out = 0
    for g in range(8):
        if a >> g & 1:
            for h in range(8):
                if b >> h & 1:
                    out ^= 1 << group_product(g, h)
    return out


def formal_identity(r):
    return tuple(tuple(int(i == j) for j in range(r)) for i in range(r))


def formal_word(word, r):
    require(0 <= len(word) <= 16, "word bound")
    op = formal_identity(r)
    for g, n in word:
        require(g in (1, 2) and len(n) == r, "illegal call")
        require(all(0 <= row < 1 << r for row in n), "nonbinary matrix")
        factor = tuple(tuple(int(i == j) ^ (((1 << g) ^ 1) if n[i] >> j & 1 else 0)
                             for j in range(r)) for i in range(r))
        nxt = []
        for i in range(r):
            row = []
            for j in range(r):
                entry = 0
                for k in range(r):
                    entry ^= algebra_product(op[i][k], factor[k][j])
                row.append(entry)
            nxt.append(tuple(row))
        op = tuple(nxt)
    return op


def shadow(op, coefficient):
    require(coefficient in range(4), "unknown coefficient")
    rows = []
    for row in op:
        out = 0
        for j, cell in enumerate(row):
            parity = 0
            for g in range(8):
                x, y, z = g & 1, g >> 1 & 1, g >> 2 & 1
                value = (x, y, z, z ^ (x & y))[coefficient]
                parity ^= (cell >> g & 1) & value
            out |= parity << j
        rows.append(out)
    return tuple(rows)


def expected(r, w=3):
    return tuple(tuple((1 << 4 if i < w else 1) if i == j else 0
                       for j in range(r)) for i in range(r))


def literal_check(word, op, r):
    columns = 0
    for source in range(r):
        for address in range(8):
            payload = [0] * r
            payload[source] = 1 << address
            for g, n in reversed(word):
                delta = [0] * r
                for i in range(r):
                    for j in range(r):
                        if n[i] >> j & 1:
                            for h in range(8):
                                if payload[j] >> h & 1:
                                    delta[i] ^= (1 << h) ^ (1 << literal_product(g, h))
                payload = [x ^ y for x, y in zip(payload, delta, strict=True)]
            want = []
            for i in range(r):
                cell = 0
                for g in range(8):
                    if op[i][source] >> g & 1:
                        cell ^= 1 << literal_product(g, address)
                want.append(cell)
            require(payload == want, "literal regular action disagrees")
            columns += 1
    return columns


def price_checks():
    a, b = (0, 6, 9, 14), (0, 11, 12, 13)
    require(all(2 * a[d] >= 9 * d for d in range(1, 4)), "a dual")
    require(all(3 * b[d] >= 13 * d for d in range(1, 4)), "b dual")
    require([d for d in range(1, 4) if 2 * a[d] == 9 * d] == [2], "a equality")
    require([d for d in range(1, 4) if 3 * b[d] == 13 * d] == [3], "b equality")
    lists = []
    for counts in itertools.product(range(7), repeat=3):
        if sum(d * counts[d - 1] for d in range(1, 4)) == 6:
            lists.append(counts)
    costs = [[sum(table[d] * c[d - 1] for d in range(1, 4)) for c in lists]
             for table in (a, b)]
    require(min(costs[0]) == 27 and min(costs[1]) == 26, "separate optima")
    orders = list(itertools.combinations(range(5), 2))
    for left, right in orders:
        inside = right - left - 1
        require(2 * inside < 3 or 2 * (3 - inside) < 3, "cut exclusion")
    return {"a_prices": a, "b_prices": b, "separate_minimum": 53,
            "full_minimum": 54, "partitions": len(lists), "letter_orders": len(orders)}


def cut_checks():
    matrices = list(itertools.product(range(4), repeat=2))
    zero = (0, 0)
    cases = 0
    full_targets = 0
    for n in matrices[1:]:
        for left in matrices:
            for middle in matrices:
                right = add(left, middle)
                word = [(1, left), (2, n), (1, middle), (2, n), (1, right)]
                op = formal_word(word, 2)
                require(shadow(op, 0) == zero and shadow(op, 1) == zero, "linear closure")
                require(shadow(op, 2) == multiply(middle, n), "XY interval")
                require(shadow(op, 3) == multiply(n, middle), "YX interval")
                if op == expected(2, 2):
                    require(rank(middle) >= 2 and rank(add(left, right)) >= 2,
                            "full target violates cut")
                    full_targets += 1
                cases += 1
    require(cases == 3840 and full_targets > 0, "cut coverage")
    return {"cut_cases": cases, "full_two_target_cases": full_targets}


def witness_checks():
    fixtures = 0
    columns = 0
    controls = 0
    for r in range(3, 7):
        q = tuple(1 << i if i < 3 else 0 for i in range(r))
        for letters in ((1, 2, 1, 2), (2, 1, 2, 1)):
            word = [(g, q) for g in letters]
            op = formal_word(word, r)
            require(op == expected(r), "optimal full endpoint")
            require(sum((5 + rank(n) ** 2 if g == 1 else 10 + rank(n))
                        for g, n in word) == 54, "attaining bill")
            columns += literal_check(word, op, r)
            fixtures += 1
            for deleted in range(4):
                require(formal_word(word[:deleted] + word[deleted + 1:], r) != expected(r),
                        "deleted paid call accepted")
                controls += 1
        frames = [identity(r)]
        for i, j in itertools.permutations(range(3), 2):
            s = list(identity(r))
            s[i] ^= 1 << j
            frames.append(tuple(s))
        for s in frames:
            word = []
            for omitted in range(3):
                p = tuple(1 << i if i < 3 and i != omitted else 0 for i in range(r))
                n = multiply(multiply(s, p), s)
                require(rank(n) == 2, "comparison rank")
                word.extend(((1, n), (2, n)))
            op = formal_word(word, r)
            require(op == expected(r), "conjugated comparison endpoint")
            columns += literal_check(word, op, r)
            fixtures += 1
    return {"endpoint_fixtures": fixtures, "regular_basis_columns": columns,
            "deleted_call_controls": controls}


def semantic_controls():
    q = (1, 2, 4, 0)
    word = [(g, q) for g in (1, 2, 1, 2)]
    bad = word + [(1, (0, 0, 0, 8))]
    require(formal_word(bad, 4) != expected(4), "dirty spectator accepted")
    base = formal_word(word, 4)
    kernel = []
    for cell in range(1, 256):
        op = ((cell,),)
        if all(shadow(op, i) == (0,) for i in range(4)) and cell.bit_count() % 2 == 0:
            kernel.append(cell)
    require(kernel, "missing shadow kernel control")
    mutant = [list(row) for row in base]
    mutant[3][3] ^= kernel[0]
    mutant = tuple(tuple(row) for row in mutant)
    require(mutant != base and all(shadow(mutant, i) == shadow(base, i) for i in range(4)),
            "quotient-only endpoint control")
    a, b = (2, 0), (0, 1)
    require(multiply(a, b) != multiply(b, a), "noncommuting matrix fixture")
    op = formal_word([(1, a), (2, b), (1, a)], 2)
    require(shadow(op, 1) != (0, 0), "unrestored first-order control")
    return {"semantic_controls": 3, "shadow_kernel_masks": len(kernel)}


def source_hashes():
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        with (package / name).open("rb") as stream:
            data = stream.read(131073)
        require(len(data) <= 131072, "source file size bound")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    require(all(group_product(g, h) == literal_product(g, h)
                for g in range(8) for h in range(8)), "literal group law")
    report = {"schema_version": 1, "claim_type": "scoped algebraic proof",
              "no_new_kappa": True, "prices": price_checks(), **cut_checks(),
              **witness_checks(), **semantic_controls(), "source_sha256": source_hashes()}
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        path = Path(__file__).resolve().parent / "RESULT.json"
        with path.open("rb") as stream:
            raw = stream.read(131073)
        require(len(raw) <= 131072, "receipt size bound")
        require(json.loads(raw) == json.loads(json.dumps(report)), "receipt differs from replay")
        print("PASS_UT3_ASYMMETRIC_MONOTONE_GAP separate=53 exact=54 no_new_kappa")
        print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
