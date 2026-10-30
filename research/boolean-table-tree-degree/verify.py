#!/usr/bin/env python3
"""Exact cut certificates and tree-degree controls.

produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FILES = ("README.md", "PROOF.md", "TABLE.json", "TASK.json", "SOURCES.json",
         "VERIFY.json", "verify.py")
PRIME = 101


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(name, limit):
    with (ROOT / name).open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "package file capacity")
    return data


def decode_table(record):
    require(type(record) is dict, "table must be an object")
    require(set(record) == {"axes", "hex", "encoding"}, "table fields")
    require(type(record["axes"]) is int and record["axes"] == 8, "eight axes")
    require(record["encoding"] == "byte i//8, bit i%8, input i=sum(x_j*2^j)",
            "table encoding")
    word = record["hex"]
    require(type(word) is str and len(word) == 64, "32-byte table")
    require(all(c in "0123456789abcdef" for c in word), "canonical hex")
    raw = bytes.fromhex(word)
    return tuple((raw[i // 8] >> (i % 8)) & 1 for i in range(256))


def flatten(values, axes, mask):
    require(type(axes) is int and 2 <= axes <= 8, "axis bound")
    require(len(values) == 1 << axes, "table size")
    require(type(mask) is int and 0 < mask < (1 << axes) - 1, "proper cut")
    left = tuple(i for i in range(axes) if mask >> i & 1)
    right = tuple(i for i in range(axes) if not mask >> i & 1)
    rows = tuple(sum(((x >> j) & 1) << i for j, i in enumerate(left))
                 for x in range(1 << len(left)))
    cols = tuple(sum(((x >> j) & 1) << i for j, i in enumerate(right))
                 for x in range(1 << len(right)))
    return [[values[x | y] for y in cols] for x in rows]


def modular_pivots(matrix):
    work = [[x % PRIME for x in row] for row in matrix]
    rows, cols = len(work), len(work[0])
    require(1 <= rows <= 16 and rows <= cols <= 128, "matrix capacity")
    pivots = []
    for col in range(cols):
        row = len(pivots)
        found = next((i for i in range(row, rows) if work[i][col]), None)
        if found is None:
            continue
        work[row], work[found] = work[found], work[row]
        inverse = pow(work[row][col], -1, PRIME)
        work[row] = [x * inverse % PRIME for x in work[row]]
        for i in range(row + 1, rows):
            factor = work[i][col]
            work[i] = [(a - factor * b) % PRIME
                       for a, b in zip(work[i], work[row])]
        pivots.append(col)
        if len(pivots) == rows:
            break
    return tuple(pivots)


def exact_determinant(matrix):
    """Fraction-free elimination, separate from the modular rank algorithm."""
    size = len(matrix)
    require(1 <= size <= 16 and all(len(r) == size for r in matrix), "square minor")
    work = [row[:] for row in matrix]
    previous, sign = 1, 1
    for k in range(size - 1):
        found = next((i for i in range(k, size) if work[i][k]), None)
        if found is None:
            return 0
        if found != k:
            work[k], work[found] = work[found], work[k]
            sign = -sign
        pivot = work[k][k]
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                numerator = work[i][j] * pivot - work[i][k] * work[k][j]
                require(numerator % previous == 0, "Bareiss exact division")
                work[i][j] = numerator // previous
            work[i][k] = 0
        previous = pivot
    return sign * work[-1][-1]


def independent_minor(values, axes, mask, columns):
    """Rebuild the selected integer minor by scanning complete input words."""
    left = [i for i in range(axes) if mask & (1 << i)]
    right = [i for i in range(axes) if not mask & (1 << i)]
    require(len(left) <= 4, "minor row capacity")
    cells = [[None] * len(columns) for _ in range(1 << len(left))]
    column_positions = {value: i for i, value in enumerate(columns)}
    for word in range(1 << axes):
        row = sum(((word >> bit) & 1) * 2 ** i for i, bit in enumerate(left))
        col = sum(((word >> bit) & 1) * 2 ** i for i, bit in enumerate(right))
        if col in column_positions:
            cells[row][column_positions[col]] = values[word]
    require(all(x is not None for row in cells for x in row), "complete minor")
    return cells


def cut_certificate(values, axes, cuts):
    require(tuple(cuts) == tuple(range(1, 1 << (axes - 1))), "complete cut domain")
    histogram = {size: 0 for size in range(1, axes // 2 + 1)}
    determinants = []
    full = (1 << axes) - 1
    for original in cuts:
        mask = original if original.bit_count() <= axes // 2 else full ^ original
        matrix = flatten(values, axes, mask)
        pivots = modular_pivots(matrix)
        require(len(pivots) == len(matrix), "rank-deficient cut")
        minor = independent_minor(values, axes, mask, pivots)
        determinant = exact_determinant(minor)
        require(determinant % PRIME != 0, "nonzero integer minor")
        histogram[mask.bit_count()] += 1
        determinants.append((original, pivots, determinant))
    return histogram, determinants


def prufer_tree(vertices, code):
    require(1 <= vertices <= 4, "tree capacity")
    if vertices == 1:
        return ()
    degrees = [1 + code.count(i) for i in range(vertices)]
    edges = []
    for target in code:
        leaf = next(i for i in range(vertices) if degrees[i] == 1)
        edges.append((leaf, target))
        degrees[leaf] -= 1
        degrees[target] -= 1
    ends = tuple(i for i in range(vertices) if degrees[i] == 1)
    require(len(ends) == 2, "two final leaves")
    return tuple(edges) + (ends,)


def component_weight(weights, edges, start, blocked):
    reached, frontier = {start}, {start}
    for _ in range(len(weights)):
        following = set()
        for a, b in edges:
            if a in frontier and b != blocked and b not in reached:
                following.add(b)
            if b in frontier and a != blocked and a not in reached:
                following.add(a)
        reached.update(following)
        frontier = following
    require(not frontier, "bounded traversal exhausted")
    return sum(weights[i] for i in reached)


def centroid_degree(weights, edges):
    vertices, total = len(weights), sum(weights)
    require(1 <= vertices <= 4 and total == 8, "eight external legs")
    require(all(type(x) is int and x >= 0 for x in weights), "external weights")
    require(len(edges) == vertices - 1, "tree edge count")
    for root in range(vertices):
        neighbours = [b if a == root else a for a, b in edges if root in (a, b)]
        branches = [component_weight(weights, edges, v, root) for v in neighbours]
        require(weights[root] + sum(branches) == total, "tree components partition")
        if all(b <= total // 2 for b in branches):
            bound = weights[root] + sum(min(b, total - b) for b in branches)
            require(bound == total, "centroid degree floor")
            return root, bound
    raise ValueError("no weighted centroid")


def check_trees():
    count = 0
    for vertices in range(1, 5):
        codes = itertools.product(range(vertices), repeat=max(0, vertices - 2))
        for code in codes:
            edges = prufer_tree(vertices, code)
            for bars in itertools.combinations(range(8 + vertices - 1), vertices - 1):
                stops = (-1,) + bars + (8 + vertices - 1,)
                weights = tuple(stops[i + 1] - stops[i] - 1 for i in range(vertices))
                _, degree = centroid_degree(weights, edges)
                require(degree == 8, "tree degree")
                count += 1
    require(count == 2785, "complete small-tree domain")
    return count


def cycle_boundary():
    cores = (
        (((1, 1), (1, 2)), ((2, 0), (2, 1))),
        (((1, 2), (1, 0)), ((2, 0), (0, 2))),
        (((1, 2), (2, 2)), ((0, 2), (1, 1))),
        (((0, 2), (1, 2)), ((0, 0), (2, 0))),
    )
    values = []
    for word in range(16):
        state = [[1, 0], [0, 1]]
        for site in range(4):
            gate = cores[site][(word >> site) & 1]
            state = [[sum(state[i][k] * gate[k][j] for k in range(2))
                      for j in range(2)] for i in range(2)]
        values.append(state[0][0] + state[1][1])
    require(values == [42, 62, 52, 48, 26, 36, 30, 32,
                       16, 24, 16, 16, 12, 16, 12, 16], "cycle contraction")
    histogram, _ = cut_certificate(values, 4, range(1, 8))
    require(histogram == {1: 4, 2: 3}, "full-rank cycle boundary")
    return len(values)


def rejected(call, message):
    try:
        call()
    except ValueError as error:
        require(message in str(error), "unexpected rejection cause")
        return 1
    raise ValueError("false certificate accepted")


def controls(record, values):
    count = 0
    for field, value, message in (
        ("axes", True, "eight axes"), ("axes", 9, "eight axes"),
        ("hex", "00", "32-byte table"), ("hex", "g" * 64, "canonical hex"),
        ("encoding", "big endian", "table encoding"),
    ):
        changed = dict(record, **{field: value})
        count += rejected(lambda: decode_table(changed), message)
    for bad in ((0,) * 256, (1,) * 256,
                tuple(i.bit_count() % 2 for i in range(256))):
        count += rejected(lambda: cut_certificate(bad, 8, range(1, 128)),
                          "rank-deficient cut")
    count += rejected(lambda: cut_certificate(values, 8, range(1, 127)),
                      "complete cut domain")
    count += rejected(lambda: flatten(values, 8, 0), "proper cut")
    count += rejected(lambda: exact_determinant([[1, 2]]), "square minor")
    count += rejected(lambda: centroid_degree((2, 2, 2, 2),
                      ((0, 1), (1, 2), (2, 3), (3, 0))), "tree edge count")
    return count


def main():
    raw = read_bounded("TABLE.json", 4096)
    record = json.loads(raw)
    values = decode_table(record)
    require(sum(values) == 121, "membership count")
    histogram, minors = cut_certificate(values, 8, range(1, 128))
    require(histogram == {1: 8, 2: 28, 3: 56, 4: 35}, "bipartition census")
    require(len(minors) == 127, "minor census")
    trees = check_trees()
    cycle_entries = cycle_boundary()
    count = controls(record, values)
    require(count == 12, "control census")
    hashes = {}
    for name in FILES:
        data = read_bounded(name, 262144)
        hashes[name] = hashlib.sha256(data).hexdigest()
    print(json.dumps({"status": "PASS_BOOLEAN_TABLE_TREE_DEGREE", "axes": 8,
                      "members": sum(values), "cuts": len(minors),
                      "cut_sizes": histogram, "exact_integer_minors": len(minors),
                      "degree_minimum": 8, "small_weighted_trees": trees,
                      "cycle_boundary_entries": cycle_entries, "controls": count,
                      "claim_type": "scoped proof with finite exact certificate",
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
