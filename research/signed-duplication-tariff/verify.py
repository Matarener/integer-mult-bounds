#!/usr/bin/env python3
"""Check the new replicated-target constructor and its transversal cover."""

import argparse
import hashlib
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
C = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
CHARS = (0, 2, 3, 4, 5, 8, 12)
MAX_GROUP = 4
MAX_OPS = 6 * MAX_GROUP
MAX_WORD = 4 * MAX_OPS
MAX_FILE_BYTES = 2 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    require(len(data) <= MAX_FILE_BYTES, "file capacity: " + str(path))
    return data


def load_anchors():
    """Use predecessor constructions as inputs, without auditing their results."""
    sources = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    require(len(sources["files"]) <= 16, "source inventory capacity")
    anchors = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        data = read_bytes(ROOT / row["path"])
        require(digest(data) == row["sha256"], "source hash: " + row["path"])
        source = json.loads(data)
        if "canonical_words" in source:
            anchors[3] = source["canonical_words"]
        elif "witnesses" in source:
            anchors[0] = source["witnesses"]
    require(set(anchors) == {0, 3}, "two predecessor anchor families")
    return anchors


def groups_for(sizes):
    require(len(sizes) == 6, "six group sizes")
    require(all(type(n) is int and 1 <= n <= MAX_GROUP for n in sizes),
            "group size outside evidence capacity")
    groups, offset = [], 0
    for size in sizes:
        groups.append(tuple(range(offset, offset + size)))
        offset += size
    require(offset <= MAX_OPS, "operator capacity")
    return tuple(groups)


def premium(char):
    require(char == 0 or type(char) is int and 2 <= char <= 256,
            "invalid characteristic")
    return 0 if char == 2 else 1 if char == 3 else 2


def envelope(groups, prices, char):
    require(len(prices) == sum(map(len, groups)), "price shape")
    require(all(p > 0 for p in prices), "positive complete prices required")
    sums = tuple(sum(prices[op] for op in group) for group in groups)
    return 2 * sum(prices) + premium(char) * min(sums)


def construct(groups, char, chosen, anchors):
    require(chosen in range(6), "chosen group")
    premium(char)
    if char == 2:
        tokens = "B0+ B1+ B2+ A0+ A1+ B2- A2+ B1- B0- A0- A1- A2-"
        base = [(t[0], int(t[1]), 1 if t[2] == "+" else -1)
                for t in tokens.split()]
    else:
        name = ("B" if chosen < 3 else "A") + str(chosen % 3)
        base = anchors[3 if char == 3 else 0][name]
    word = []
    for kind, index, sign in base:
        group = groups[index + (3 if kind == "A" else 0)]
        word.extend((op, sign) for op in group)
    require(len(word) <= MAX_WORD, "word capacity")
    return tuple(word)


def labels(groups):
    return tuple(k for k, group in enumerate(groups) for _ in group)


def residual(word, groups, char):
    """Track formal B_j x_j and A_i B_j x_j coefficients exactly."""
    nb = sum(map(len, groups[:3]))
    na = sum(map(len, groups[3:]))
    require(len(word) <= MAX_WORD, "word capacity")
    q, dirt, matrix = [0] * nb, [0] * na, [[0] * nb for _ in range(na)]
    for op, sign in word:
        require(type(op) is int and 0 <= op < nb + na and sign in (-1, 1),
                "invalid query")
        if op < nb:
            q[op] += sign
        else:
            i = op - nb
            dirt[i] += sign
            for j in range(nb):
                matrix[i][j] += sign * q[j]
    lab = labels(groups)
    errors = q + dirt + [matrix[i][j] - C[lab[nb + i] - 3][lab[j]]
                         for i in range(na) for j in range(nb)]
    return tuple(x % char if char else x for x in errors)


def count_profile(word, n):
    counts = [0] * n
    for op, _ in word:
        counts[op] += 1
    return tuple(counts)


def construction_checks(anchors):
    cases = 0
    for sizes in itertools.product(range(1, 4), repeat=6):
        groups = groups_for(sizes)
        n = sum(sizes)
        for char, chosen in itertools.product(CHARS, range(6)):
            word = construct(groups, char, chosen, anchors)
            require(not any(residual(word, groups, char)), "replicated action")
            expected = tuple(2 + premium(char) * (op in groups[chosen])
                             for op in range(n))
            require(count_profile(word, n) == expected, "attaining profile")
            cases += 1
    return cases


def priced_checks(anchors):
    rng, cases = random.Random(84017), 0
    for sizes in itertools.product((1, 2), repeat=6):
        groups = groups_for(sizes)
        n = sum(sizes)
        pricesets = [(Fraction(1),) * n]
        pricesets.extend(tuple(Fraction(rng.randrange(1, 30), rng.randrange(1, 8))
                               for _ in range(n)) for _ in range(4))
        for char, prices in itertools.product(CHARS, pricesets):
            chosen = min(range(6), key=lambda k: sum(prices[o] for o in groups[k]))
            word = construct(groups, char, chosen, anchors)
            bill = sum(prices[op] for op, _ in word)
            require(bill == envelope(groups, prices, char), "priced attainment")
            require(not any(residual(word, groups, char)), "priced action")
            cases += 1
    return cases


def cover_checks():
    """Enumerate subsets directly, independently of the closed cover lemma."""
    masks, transversals, cases = 0, 0, 0
    for sizes in itertools.product((1, 2), repeat=6):
        groups = groups_for(sizes)
        n = sum(sizes)
        edges = tuple(sum(1 << op for op in choice)
                      for choice in itertools.product(*groups))
        group_masks = tuple(sum(1 << op for op in g) for g in groups)
        prices = tuple(Fraction((7 * op + 3) % 19 + 1, op % 4 + 1)
                       for op in range(n))
        best, minimal = None, set()
        for mask in range(1 << n):
            hit = all(mask & edge for edge in edges)
            whole = any(mask & g == g for g in group_masks)
            require(hit == whole, "transversal equivalence")
            if hit:
                cost = sum(prices[o] for o in range(n) if mask & (1 << o))
                best = cost if best is None else min(best, cost)
                if all(not all((mask ^ (1 << o)) & edge for edge in edges)
                       for o in range(n) if mask & (1 << o)):
                    minimal.add(mask)
            masks += 1
        require(minimal == set(group_masks), "minimal cover classification")
        require(best == min(sum(prices[o] for o in g) for g in groups),
                "weighted cover optimum")
        transversals += len(edges)
        cases += 1
    return {"shapes": cases, "subsets": masks, "transversals": transversals}


def mv(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def execute(word, nb, maps, initial, char):
    state = [list(v) for v in initial]
    for op, sign in word:
        src, dst = (op, len(state) - 1) if op < nb else (len(state) - 1, op)
        inc = mv(maps[op], state[src])
        state[dst] = [a + sign * b for a, b in zip(state[dst], inc)]
        if char:
            state[dst] = [a % char for a in state[dst]]
    return state


def dense_checks(anchors):
    rng, cases = random.Random(84321), 0
    shapes = ((1,) * 6, (2,) * 6, (4, 1, 2, 3, 1, 2), (1, 4, 2, 1, 3, 4))
    for sizes in shapes:
        groups = groups_for(sizes)
        n, nb = sum(sizes), sum(sizes[:3])
        lab = labels(groups)
        for char, chosen, _ in itertools.product(CHARS, range(6), range(3)):
            maps = [[[rng.randrange(-3, 4) for _ in range(2)] for _ in range(2)]
                    for _ in range(n)]
            maps[0], maps[nb] = [[0, 1], [0, 0]], [[0, 0], [1, 0]]
            require(mv(maps[0], mv(maps[nb], [1, 0])) !=
                    mv(maps[nb], mv(maps[0], [1, 0])), "noncommuting fixture")
            initial = [[rng.randrange(-5, 6) for _ in range(2)] for _ in range(n + 1)]
            if char:
                initial = [[a % char for a in row] for row in initial]
            expected = [list(v) for v in initial]
            for i in range(nb, n):
                for j in range(nb):
                    inc = mv(maps[i], mv(maps[j], initial[j]))
                    coefficient = C[lab[i] - 3][lab[j]]
                    expected[i] = [a + coefficient * b for a, b in zip(expected[i], inc)]
                if char:
                    expected[i] = [a % char for a in expected[i]]
            word = construct(groups, char, chosen, anchors)
            actual = execute(word, nb, maps, initial, char)
            require(actual == expected, "literal dense dirty action")
            inverse = tuple((op, -sign) for op, sign in reversed(word))
            require(execute(inverse, nb, maps, actual, char) == initial,
                    "literal dirty round trip")
            cases += 1
    return cases


def failure_checks(anchors):
    groups, controls = groups_for((2, 1, 1, 1, 1, 1)), 0
    for char, chosen in itertools.product(CHARS, range(6)):
        word = construct(groups, char, chosen, anchors)
        for position in range(len(word)):
            broken = word[:position] + word[position + 1:]
            require(any(residual(broken, groups, char)), "omitted query accepted")
            controls += 1
    prices = (1, 100, 10, 10, 10, 10, 10)
    require(envelope(groups, prices, 0) == 322, "whole-group example")
    require(2 * sum(prices) + 2 * min(prices) == 304, "incorrect single surcharge")
    word = construct(groups, 0, 1, anchors)
    require(sum(prices[op] for op, _ in word) == 322, "literal example bill")
    edge_avoiding_cheapest = sum(1 << group[-1] for group in groups)
    require(not edge_avoiding_cheapest & 1, "single surcharge misses a transversal")
    controls += 1
    bad_cases = ((0, 1, 1, 1, 1, 1), (5, 1, 1, 1, 1, 1), (1,) * 5)
    for sizes in bad_cases:
        try:
            groups_for(sizes)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid group shape accepted")
    for prices, char in (((0,) * 7, 3), ((1,) * 6, 3), ((1,) * 7, 1)):
        try:
            envelope(groups, prices, char)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid price or characteristic accepted")
    return controls


def receipt(counts):
    paths = sorted(p for p in PACKAGE.iterdir() if p.is_file())
    require(len(paths) <= 16, "package inventory capacity")
    inputs = json.loads(read_bytes(PACKAGE / "VERIFY.json"))["inputs"]
    require(len(inputs) == 2, "receipt input inventory")
    paths.extend(ROOT / path for path in inputs)
    hashes = {str(p.relative_to(ROOT)): digest(read_bytes(p)) for p in paths}
    return {"status": "PASS_SIGNED_DUPLICATION_TARIFF", "counts": counts,
            "sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(ROOT),
                "receipt must stay outside checkout")
    anchors = load_anchors()
    counts = {"construction_cases": construction_checks(anchors),
              "priced_cases": priced_checks(anchors), "cover": cover_checks(),
              "dense_cases": dense_checks(anchors),
              "negative_controls": failure_checks(anchors)}
    result = receipt(counts)
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt:
        written = args.receipt.write_text(payload)
        require(written == len(payload), "incomplete receipt write")
    print("PASS_SIGNED_DUPLICATION_TARIFF", json.dumps(counts, sort_keys=True))
    print("receipt_sha256", digest(payload.encode()))


if __name__ == "__main__":
    main()
