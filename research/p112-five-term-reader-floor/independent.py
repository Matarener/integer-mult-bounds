"""Pair-disjoint line enumeration and determinant oracle. Nick Petalas. Apache-2.0."""

import itertools as it
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(condition, label):
    if not condition:
        raise ValueError(label)


def load(name):
    with (HERE / name).open("rb") as stream:
        raw = stream.read(131073)
    check(len(raw) <= 131072, "input bound")
    return json.loads(raw)


def multiply(a, b):
    out = 0
    for bit in range(8):
        if b >> bit & 1:
            out ^= a << bit
    for bit in range(14, 7, -1):
        if out >> bit & 1:
            out ^= 283 << (bit - 8)
    return out


def determinant(a, b, c):
    result = 0
    for perm in it.permutations(range(3)):
        result ^= multiply(multiply(a[perm[0]], b[perm[1]]), c[perm[2]])
    return result


def rational_det(a, b, c):
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def ranks(points, binary):
    triple_rank = determinant if binary else rational_det
    check(len(points) == 7 and all(len(p) == 3 for p in points), "oracle shape")
    check(all(any(p) for p in points), "nonzero points")
    for a, b in it.combinations(points, 2):
        minors = [
            multiply(a[i], b[j]) ^ multiply(a[j], b[i])
            if binary
            else a[i] * b[j] - a[j] * b[i]
            for i, j in it.combinations(range(3), 2)
        ]
        check(any(minors), "distinct projective points")
    independent = [
        sum(1 << i for i in t)
        for t in it.combinations(range(7), 3)
        if triple_rank(*(points[i] for i in t))
    ]
    return [
        mask.bit_count()
        if mask.bit_count() < 2
        else 3
        if any(t & mask == t for t in independent)
        else 2
        for mask in range(128)
    ]


def embedding():
    roots = []
    for x in range(256):
        square = multiply(x, x)
        if multiply(square, square) ^ x ^ 1 == 0:
            roots.append(x)
    check(len(roots) == 4, "GF16 embedding roots")
    x = roots[0]
    powers = (1, x, multiply(x, x), multiply(multiply(x, x), x))
    mapping = []
    for value in range(16):
        out = 0
        for bit in range(4):
            if value >> bit & 1:
                out ^= powers[bit]
        mapping.append(out)
    check(len(set(mapping)) == 16, "injective field embedding")
    return mapping


def line_systems(rows):
    check(len(rows) == 23, "independent template count")
    check(
        all(
            len(row["lines"]) <= 7
            and all(type(x) is int and 0 <= x < 128 for x in row["lines"])
            for row in rows
        ),
        "line shape",
    )
    blocks = [
        sum(1 << i for i in points)
        for size in range(3, 8)
        for points in it.combinations(range(7), size)
    ]
    index = {block: j for j, block in enumerate(blocks)}
    pairs = list(it.combinations(range(7), 2))
    consumed = [
        sum(1 << j for j, pair in enumerate(pairs) if all(block >> i & 1 for i in pair))
        for block in blocks
    ]
    expected = set()
    for row in [item["lines"] for item in rows] + [[127]]:
        for perm in it.permutations(range(7)):
            transformed = [
                sum(1 << perm[i] for i in range(7) if line >> i & 1) for line in row
            ]
            expected.add(sum(1 << index[line] for line in transformed))
    stack = [(0, 0, 0)]
    actual = set()
    for _ in range(200000):
        if not stack:
            break
        code, used, start = stack.pop()
        check(code not in actual, "duplicate enumeration state")
        actual.add(code)
        for j in range(start, len(blocks)):
            if used & consumed[j] == 0:
                stack.append((code | (1 << j), used | consumed[j], j + 1))
        check(len(stack) <= 200000, "worklist capacity")
    else:
        raise ValueError("enumeration capacity")
    check(
        actual == expected and len(actual) == 8390,
        "independent classification coverage",
    )
    return len(actual)


def representations(rows, mapping):
    count = 0
    for row in rows:
        if row["kind"] != "GF16":
            continue
        check(
            len(row["points"]) == 7
            and all(
                len(p) == 3 and all(type(x) is int and 0 <= x < 16 for x in p)
                for p in row["points"]
            ),
            "independent field shape",
        )
        points = [[mapping[x] for x in point] for point in row["points"]]
        observed = ranks(points, True)
        for mask, actual in enumerate(observed):
            expected = (
                mask.bit_count()
                if mask.bit_count() < 2
                else 2
                if mask.bit_count() == 2
                or any(mask & line == mask for line in row["lines"])
                else 3
            )
            check(actual == expected, "determinant subset ranks")
            count += 1
    return count


def marked_transfer(mapping):
    points = (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1),
        (1, 1, 1),
    )
    old = ranks(points, False)
    lines = {
        sum(1 << i for i in t)
        for t in it.combinations(range(7), 3)
        if rational_det(*(points[i] for i in t)) == 0
    }
    source = load("PREDECESSOR-TEMPLATES.json")
    automorphisms = [
        p
        for p in it.permutations(range(7))
        if {sum(1 << p[i] for i in range(7) if line >> i & 1) for line in lines}
        == lines
    ]
    check(len(automorphisms) == 24 and len(lines) == 6, "rational quadrangle")
    counts = [0, 0]
    for a, b in it.combinations(range(7), 2):
        j, permutation = next(
            (j, p)
            for j, pair in enumerate(source["representative_pairs"])
            for p in automorphisms
            if sorted(p[i] for i in pair) == [a, b]
        )
        new = [None] * 7
        for i in range(7):
            new[permutation[i]] = [
                mapping[[0, 1, 6, 7][x]] for x in source["points"][j][i]
            ]
        changed = ranks(new, True)
        check(changed[(1 << a) | (1 << b)] == 2, "independent marks")
        for subset in range(128):
            if subset & ((1 << a) | (1 << b)):
                continue
            for t, other in ((a, b), (b, a)):
                base = subset | (1 << other)
                if old[base | (1 << t)] != old[base]:
                    check(
                        changed[base | (1 << t)] != changed[base],
                        "independent source transfer",
                    )
                    counts[0] += 1
                if old[subset | (1 << t)] == old[subset]:
                    check(
                        changed[subset | (1 << t)] == changed[subset],
                        "independent reader transfer",
                    )
                    counts[1] += 1
    check(counts == [288, 672], "independent premise receipt")
    return counts


def main():
    data = load("TEMPLATES.json")
    check(data["polynomial"] == 19, "independent polynomial")
    mapping = embedding()
    systems = line_systems(data["types"])
    subsets = representations(data["types"], mapping)
    premises = marked_transfer(mapping)
    result = {
        "labeled_systems": systems,
        "GF256_subset_ranks": subsets,
        "source_premises": premises[0],
        "reader_premises": premises[1],
    }
    check(result == load("RESULT.json")["independent"], "independent result receipt")
    print("PASS_INDEPENDENT_FIVE_TERM " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
