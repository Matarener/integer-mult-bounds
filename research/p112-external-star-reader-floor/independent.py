"""Binary support domination, implemented separately. Nick Petalas. Apache-2.0."""

import itertools
import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def read_bytes(path, capacity=1_048_576):
    with path.open("rb") as source:
        raw = source.read(capacity + 1)
    require(len(raw) <= capacity, "source capacity")
    return raw


def matrix_rank(matrix):
    rows = [list(row) for row in matrix]
    height = len(rows)
    width = len(rows[0]) if height else 0
    pivot = 0
    for column in range(width):
        candidates = [i for i in range(pivot, height) if rows[i][column]]
        if not candidates:
            continue
        i = candidates[0]
        rows[pivot], rows[i] = rows[i], rows[pivot]
        for j in range(pivot + 1, height):
            if rows[j][column]:
                rows[j] = [x ^ y for x, y in zip(rows[j], rows[pivot])]
        pivot += 1
    return pivot


def parity(x, y):
    return sum(a * b for a, b in zip(x, y)) % 2


def load_geometry():
    meta = json.loads(read_bytes(DIRECTORY / "SOURCES.json", 32768))
    inputs = [x for x in meta["files"] if x["usage"] == "input"]
    require(len(inputs) == 1 and inputs[0]["path"] ==
            "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json", "input inventory")
    pin = inputs[0]
    raw = read_bytes(DIRECTORY.parents[1] / pin["path"])
    require(sha256(raw).hexdigest() == pin["sha256"], "label hash")
    recipes = json.loads(raw)["recipes"]
    recipes = sorted(recipes, key=lambda x: x["port"])
    labels = [[(r["q"] >> i) % 2 for i in range(9)] for r in recipes]
    raw = read_bytes(DIRECTORY / "RETAINED-RANK32.json", 32768)
    require(sha256(raw).hexdigest() == meta["retained_rank32"]["sha256"], "group hash")
    return labels, json.loads(raw)["orthonormal_groups"]


def check_partition(labels, groups):
    n = len(labels)
    require(0 < n <= 112 and all(0 < len(g) <= 8 and len(g) % 2 == 0 for g in groups),
            "even group capacity")
    require(sorted(p for g in groups for p in g) == list(range(n)), "partition")
    for g in groups:
        for p, q in itertools.product(g, repeat=2):
            require(parity(labels[p], labels[q]) == int(p == q), "Gram identity")
    return [g[s::2] for g in groups for s in (0, 1)]


def local_domination():
    checked = 0
    choices = [Fraction(-2), Fraction(-1), Fraction(-1, 2), Fraction(0),
               Fraction(1, 2), Fraction(1), Fraction(2)]
    for alpha in itertools.product(range(-2, 3), repeat=3):
        for target, seed in itertools.product(range(-1, 3), choices):
            bit = int(target >= 0 and alpha[target] != 0 and 1 + alpha[target] * seed == 0)
            require(not bit or seed != 0, "seed domination")
            for j in range(3):
                before = int(j == target) + alpha[j] * seed
                after = int(j == target) ^ (int(alpha[j] != 0) * bit)
                require(not after or before != 0, "query domination")
            checked += 1
    return checked


def close(support, plane):
    return sorted({p for i in support for p in plane[i]})


def tariff(labels, source, reader):
    return matrix_rank([[parity(labels[p], labels[q]) for q in reader] for p in source])


def star_checks(labels, groups, indicators):
    n = len(labels)
    plane = {p: g[j:j + 2] for g in groups for j in range(0, len(g), 2)
             for p in g[j:j + 2]}
    states = 0
    for count in range(3, len(indicators) + 1):
        chosen = indicators[:count]
        owner = {p: j for j, row in enumerate(chosen) for p in row}
        alpha = [(-2, 3, 0, 1)[j % 4] for j in range(count)]
        c = [Fraction(0) if p % 3 == 0 else -Fraction(1, alpha[owner[p]])
             if p in owner and alpha[owner[p]] and p % 3 == 1 else Fraction(2)
             for p in range(n)]
        bits = [int(p in owner and alpha[owner[p]] != 0 and
                    1 + alpha[owner[p]] * c[p] == 0) for p in range(n)]
        old_bill = new_bill = baseline = 0
        for j, support in enumerate(chosen):
            old = [p for p in range(n) if int(owner.get(p) == j) + alpha[j] * c[p]]
            new = [p for p in range(n) if int(owner.get(p) == j) ^
                   (int(alpha[j] != 0) * bits[p])]
            require(set(new) <= set(old), "global query domination")
            reader = close(support, plane)
            old_bill += tariff(labels, close(old, plane), reader)
            new_bill += tariff(labels, close(new, plane), reader)
            baseline += len(reader)
        reader = close([p for p, j in owner.items() if alpha[j]], plane)
        old_bill += tariff(labels, close([p for p in range(n) if c[p]], plane), reader)
        new_bill += tariff(labels, close([p for p in range(n) if bits[p]], plane), reader)
        require(baseline <= new_bill <= old_bill, "binary support bill")
        states += 1
    return states


def main():
    labels, groups = load_geometry()
    indicators = check_partition(labels, groups)
    literal = star_checks(labels, groups, indicators)
    toy = [[int(i == j) for j in range(8)] for i in range(8)]
    toy_groups = [list(range(4)), list(range(4, 8))]
    toy_count = star_checks(toy, toy_groups, check_partition(toy, toy_groups))
    for bad in ([list(range(3)), list(range(3, 8))], [list(range(8))] * 2):
        try:
            check_partition(toy, bad)
        except ValueError:
            continue
        raise ValueError("invalid partition accepted")
    print(json.dumps({"status": "PASS_SEPARATE_BINARY_STAR_DOMINATION", "errors": 0,
                      "rational_local_states": local_domination(),
                      "literal_all_k_fixtures": literal, "non_P112_fixtures": toy_count,
                      "invalid_partition_controls": 2}, sort_keys=True))


if __name__ == "__main__":
    main()
