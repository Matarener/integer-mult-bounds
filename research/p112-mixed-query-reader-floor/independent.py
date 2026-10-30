#!/usr/bin/env python3
"""Direct multicover replay, without importing the primary checker.

@CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def gf2_rank(matrix):
    rows = [row[:] for row in matrix]
    height = len(rows)
    width = len(rows[0]) if rows else 0
    pivot = 0
    for column in range(width):
        candidate = next((i for i in range(pivot, height) if rows[i][column]), None)
        if candidate is None:
            continue
        rows[pivot], rows[candidate] = rows[candidate], rows[pivot]
        for i in range(pivot+1, height):
            if rows[i][column]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def load():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    live = [row for row in pins["files"] if row["usage"] == "input"]
    require(len(live) == 1, "live source count")
    raw = (ROOT / live[0]["path"]).read_bytes()
    require(sha256(raw).hexdigest() == live[0]["sha256"], "live hash")
    rows = json.loads(raw)["recipes"]
    indexed = {row["port"]: row["q"] for row in rows}
    require(len(rows) == 112 and set(indexed) == set(range(112)), "port IDs")
    vectors = [[(indexed[p] >> j) & 1 for j in range(9)] for p in range(112)]
    gram = [[sum(x*y for x, y in zip(a, b)) % 2 for b in vectors] for a in vectors]
    raw = (HERE / "RETAINED-RANK32.json").read_bytes()
    require(sha256(raw).hexdigest() == pins["retained_rank32"]["sha256"], "retained hash")
    groups = json.loads(raw)["orthonormal_groups"]
    require(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    require(sorted(map(len, groups)) == [4]*3+[6]*2+[8]*11, "sizes")
    for g in groups:
        require([[gram[p][q] for q in g] for p in g]
                == [[int(i == j) for j in range(len(g))] for i in range(len(g))],
                "identity Gram block")
    return gram, groups


def rank_table(gram, source, planes):
    table = []
    for subset in range(2**len(planes)):
        columns = [p for i, plane in enumerate(planes) if subset & 2**i for p in plane]
        table.append(gf2_rank([[gram[p][q] for q in columns] for p in source]))
    return table


def dense_multicover(cost, k):
    """No uncrossing assumption: enumerate every next dense support."""
    weights = [3**i for i in range(k)]
    decrement = [sum(weights[i] for i in range(k) if mask & 2**i) for mask in range(2**k)]
    best = [0]*3**k
    transitions = 0
    for demand in range(1, len(best)):
        remaining = demand
        available = 0
        for i in range(k):
            if remaining % 3:
                available |= 2**i
            remaining //= 3
        subset = available
        choices = []
        while subset:
            choices.append(cost[subset] + best[demand-decrement[subset]])
            transitions += 1
            subset = (subset-1) & available
        best[demand] = min(choices)
    return best, transitions


def field_checks():
    deliveries = 0
    tuples = 0
    for prime in (2, 3, 5):
        directions = [(1, 0), (0, 1)] + [(1, t) for t in range(1, prime)]
        for coefficients in product(range(prime), repeat=len(directions)):
            tuples += 1
            delivered = tuple(sum(c*q[j] for c, q in zip(coefficients, directions)) % prime
                              for j in (0, 1))
            if delivered not in ((1, 0), (0, 1)):
                continue
            axis = delivered.index(1)
            required = 0 if coefficients[axis] else (1 if coefficients[1-axis] else 2)
            require(sum(bool(c) for c in coefficients[2:]) >= required,
                    "pointwise dense demand")
            deliveries += 1
    return tuples, deliveries


def main():
    gram, groups = load()
    result = json.loads((HERE / "RESULT.json").read_text())
    require(len(result["pairs"]) == 120, "receipt pair count")
    total = transitions = layers = 0
    for index, (i, j) in enumerate(combinations(range(16), 2)):
        ga, gb = groups[i], groups[j]
        planes = [list(pair) for g in (ga, gb) for pair in zip(g[::2], g[1::2])]
        k, na = len(planes), len(ga)//2
        tables = [rank_table(gram, source, planes) for source in (ga, gb, ga+gb)]
        ca, cb, cd = tables
        best, count = dense_multicover(cd, k)
        transitions += count
        histogram = Counter()
        equality = 0
        first_mixed = None
        for demand in range(3**k):
            digits = [(demand//3**p) % 3 for p in range(k)]
            sa = sum(2**p for p, digit in enumerate(digits)
                     if (p < na and digit == 0) or (p >= na and digit == 1))
            sb = sum(2**p for p, digit in enumerate(digits)
                     if (p < na and digit == 1) or (p >= na and digit == 0))
            s1 = sum(2**p for p, digit in enumerate(digits) if digit >= 1)
            s2 = sum(2**p for p, digit in enumerate(digits) if digit == 2)
            require(best[demand] == cd[s1]+cd[s2], "multicover versus two layers")
            layers += 1
            bill = ca[sa]+cb[sb]+best[demand]
            require(bill >= len(ga)+len(gb), "independent pair floor")
            histogram[bill-len(ga)-len(gb)] += 1
            if bill == len(ga)+len(gb):
                equality += 1
                if s2 and sa and sb and first_mixed is None:
                    first_mixed = demand
        expected = {"groups": [i, j], "sizes": [len(ga), len(gb)], "states": 3**k,
                    "minimum": len(ga)+len(gb), "equality_states": equality,
                    "first_equal_four_direction_state": first_mixed,
                    "gap_histogram": {str(g): n for g, n in sorted(histogram.items())},
                    "rank_tables_sha256": sha256(json.dumps(tables, separators=(",", ":")).encode()).hexdigest()}
        require(result["pairs"][index] == expected, "complete independent pair receipt")
        total += 3**k
    require(total == result["ternary_states"] == 435456, "complete state coverage")
    require(4*120+16 == result["indicator_pairs_covered"] == 496, "pair reduction")
    require(2*sum(map(len, groups)) == result["literal_total_tariff"] == 224, "total tariff")
    tuples, deliveries = field_checks()
    print(f"PASS_MIXED_QUERY_INDEPENDENT states={total} transitions={transitions} "
          f"layer_equalities={layers} field_tuples={tuples} axis_deliveries={deliveries}")


if __name__ == "__main__":
    main()
