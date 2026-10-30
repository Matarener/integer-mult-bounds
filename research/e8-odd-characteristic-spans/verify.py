#!/usr/bin/env python3
"""Exact all-odd-characteristic certificates; produced by Nick Petalas.

Integer minors certify ranks. Modular elimination only selects minors.
No predecessor program is executed and no file is written.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations, product
from math import gcd
from pathlib import Path
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def power_of_two(value):
    return value > 0 and value & (value - 1) == 0


def dot(left, right):
    return sum(x * y for x, y in zip(left, right, strict=True))


def canonical(row):
    require(any(row), "zero projective vector")
    return tuple(-x for x in row) if next(x for x in row if x) < 0 else row


def roots():
    lines = []
    for i, j in combinations(range(8), 2):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            lines.append(tuple(row))
    for signs in product((1, -1), repeat=7):
        row = (1,) + signs
        if row.count(-1) % 2 == 0:
            lines.append(row)
    require(len(lines) == len(set(lines)) == 120, "root inventory")
    require(all(dot(row, row) == 8 for row in lines), "root norm")
    return tuple(lines)


def determinant(matrix):
    """Bareiss elimination with checked exact divisions; order at most seven."""
    size = len(matrix)
    require(1 <= size <= 7, "minor order")
    require(all(len(row) == size for row in matrix), "nonsquare minor")
    work = [list(row) for row in matrix]
    previous, sign = 1, 1
    for col in range(size - 1):
        pivot = next((i for i in range(col, size) if work[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign = -sign
        current = work[col][col]
        for i in range(col + 1, size):
            for j in range(col + 1, size):
                numerator = current * work[i][j] - work[i][col] * work[col][j]
                require(numerator % previous == 0, "inexact Bareiss division")
                work[i][j] = numerator // previous
            work[i][col] = 0
        previous = current
    return sign * work[-1][-1]


def select_minor(rows, rank, prime):
    """Return original row and column IDs of a nonzero modular minor."""
    require(1 <= len(rows) <= 63 and 1 <= rank <= 7, "matrix bounds")
    require(all(len(row) == 8 for row in rows), "coordinate count")
    work = [[x % prime for x in row] for row in rows]
    indices = list(range(len(rows)))
    columns = []
    for col in range(8):
        height = len(columns)
        pivot = next((i for i in range(height, len(rows)) if work[i][col]), None)
        if pivot is None:
            continue
        work[height], work[pivot] = work[pivot], work[height]
        indices[height], indices[pivot] = indices[pivot], indices[height]
        inverse = pow(work[height][col], -1, prime)
        for i in range(height + 1, len(rows)):
            factor = work[i][col] * inverse % prime
            for j in range(col, 8):
                work[i][j] = (work[i][j] - factor * work[height][j]) % prime
        columns.append(col)
        if len(columns) == rank:
            return indices[:rank], columns
    raise ValueError(f"rank below {rank} in characteristic {prime}")


def rank_certificate(rows, rank):
    """Select and exactly verify one power-of-two minor."""
    row_ids, col_ids = select_minor(rows, rank, 3)
    minor = [[rows[i][j] for j in col_ids] for i in row_ids]
    value = determinant(minor)
    require(power_of_two(abs(value)) and abs(value) <= 2**20, "nonunit minor")
    return [[row_ids, col_ids, value]], abs(value)


def reflection_orbit(lines):
    ids = {row: i for i, row in enumerate(lines)}
    maps = []
    for alpha in lines:
        image = []
        for row in lines:
            pairing = dot(alpha, row)
            require(pairing % 4 == 0, "reflection integrality")
            reflected = tuple(x - pairing // 4 * a for x, a in zip(row, alpha))
            require(canonical(reflected) in ids, "reflection left root set")
            image.append(ids[canonical(reflected)])
        require(len(set(image)) == 120, "reflection is not a permutation")
        maps.append(image)
    orbit, seen = [0], {0}
    for position in range(120):
        if position == len(orbit):
            break
        for image in maps:
            target = image[orbit[position]]
            if target not in seen:
                seen.add(target)
                orbit.append(target)
    require(len(orbit) == 120, "reflection transitivity")
    return len(maps) * len(lines)


def geometry(lines):
    orthogonal = [{j for j, other in enumerate(lines) if dot(row, other) == 0}
                  for row in lines]
    neighbors = [u for u in range(1, 120) if dot(lines[0], lines[u]) != 0]
    directions, projected_ids = [], {}
    for u in neighbors:
        pairing = dot(lines[0], lines[u])
        require(pairing in (-4, 4), "neighbor pairing")
        projected = tuple(2 * x - pairing // 4 * y
                          for x, y in zip(lines[u], lines[0]))
        scale = gcd(*projected)
        require(power_of_two(scale), "nonunit projection rescaling")
        direction = canonical(tuple(x // scale for x in projected))
        require(dot(direction, lines[0]) == 0, "projection is not orthogonal")
        if direction not in directions:
            directions.append(direction)
        projected_ids[u] = directions.index(direction)
    require(len(neighbors) == 56 and len(directions) == 28, "projection inventory")
    require(set(Counter(projected_ids.values()).values()) == {2}, "antipodal fibers")
    return orthogonal, neighbors, directions, projected_ids


def certificates(lines, orthogonal, neighbors, directions, projected_ids):
    yield "S1", [lines[i] for i in sorted(orthogonal[0])], 7
    for u in range(1, 120):
        yield "S2-anchor", [lines[0], lines[u]], 2
        yield "S2", [lines[i] for i in sorted(orthogonal[0] & orthogonal[u])], 6
    for u, v in combinations(neighbors, 2):
        if projected_ids[u] == projected_ids[v]:
            continue
        yield "S3-anchor", [lines[0], lines[u], lines[v]], 3
        common = orthogonal[0] & orthogonal[u] & orthogonal[v]
        yield "S3", [lines[i] for i in sorted(common)], 5
    for indices in combinations(range(28), 3):
        yield "W2", [directions[i] for i in indices], 3


def leibniz(matrix):
    total = 0
    for order in permutations(range(len(matrix))):
        inversions = sum(order[i] > order[j] for i, j in combinations(range(len(order)), 2))
        term = (-1) ** inversions
        for i, j in enumerate(order):
            term *= matrix[i][j]
        total += term
    return total


def controls():
    count = 0
    for values in product(range(-2, 3), repeat=4):
        matrix = [list(values[:2]), list(values[2:])]
        require(determinant(matrix) == leibniz(matrix), "determinant differential")
        count += 1
    for size in (3, 4, 5):
        for offset in range(16):
            matrix = [[((i + 2) * (j + 3) + offset * (i == j)) % 7 - 3
                       for j in range(size)] for i in range(size)]
            require(determinant(matrix) == leibniz(matrix), "larger determinant differential")
            count += 1
    for coefficient in (0, 3, 5):
        try:
            rank_certificate([[coefficient] + [0] * 7], 1)
        except ValueError:
            count += 1
        else:
            raise ValueError("accepted singular or odd-torsion matrix")
    require(rank_certificate([[2] + [0] * 7], 1)[1] == 2, "dyadic unit control")
    require(not power_of_two(0) and not power_of_two(12), "power-of-two control")
    return count + 2


def source_bindings(package):
    manifest = json.loads((package / "SOURCES.json").read_text())
    root, hashes = package.parent.parent, {}
    for item in manifest["files"]:
        if item["usage"] == "input":
            observed = sha256((root / item["path"]).read_bytes()).hexdigest()
            require(observed == item["sha256"], "source byte mismatch: " + item["path"])
            hashes[item["path"]] = observed
    for path in sorted(package.iterdir()):
        if path.is_file() and path.suffix in (".py", ".md", ".json"):
            hashes[path.name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    package = Path(__file__).resolve().parent
    hashes = source_bindings(package)
    lines = roots()
    images = reflection_orbit(lines)
    orthogonal, neighbors, directions, projected_ids = geometry(lines)
    counts, gcds, digest = Counter(), Counter(), sha256()
    minor_count, largest = 0, 0
    for name, rows, rank in certificates(lines, orthogonal, neighbors, directions, projected_ids):
        witnesses, divisor = rank_certificate(rows, rank)
        digest.update(json.dumps([name, rows, rank, witnesses, divisor], separators=(",", ":")).encode())
        counts[name] += 1
        gcds[str(divisor)] += 1
        minor_count += len(witnesses)
        largest = max(largest, *(abs(witness[2]) for witness in witnesses))
    require(dict(counts) == {"S1": 1, "S2-anchor": 119, "S2": 119,
                             "S3-anchor": 1512, "S3": 1512, "W2": 3276}, "case inventory")
    print(json.dumps({"status": "PASS_E8_ODD_CHARACTERISTIC_SPANS",
                      "claim_type": "scoped proof with finite integer-minor certificate",
                      "cases": dict(counts), "minor_count": minor_count,
                      "gcd_histogram": dict(sorted(gcds.items())),
                      "largest_absolute_minor": largest,
                      "certificate_sha256": digest.hexdigest(),
                      "reflection_images": images, "controls": controls(),
                      "source_sha256": hashes, "exceptional_odd_primes": []}, sort_keys=True))


if __name__ == "__main__":
    main()
