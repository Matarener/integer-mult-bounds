#!/usr/bin/env python3
"""RREF enumeration and quotient-rank replay; imports no primary code. Apache-2.0."""

import itertools
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
PERMS = (
    (1, 0, 2, 3),
    (0, 2, 1, 3),
    (0, 1, 3, 2),
    (1, 0, 3, 2),
    (2, 0, 3, 1),
    (3, 1, 2, 0),
    (1, 0, 3, 2),
)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def bases(n, field):
    check(n in (4, 6) and field in (2, 3, 5), "enumeration domain")
    check(n == 4 or field == 2, "six-space field")
    for dimension in range(n + 1):
        for pivots in itertools.combinations(range(n), dimension):
            free = [
                (i, j)
                for i, pivot in enumerate(pivots)
                for j in range(pivot + 1, n)
                if j not in pivots
            ]
            for values in itertools.product(range(field), repeat=len(free)):
                rows = [[int(j == pivot) for j in range(n)] for pivot in pivots]
                for (i, j), value in zip(free, values, strict=True):
                    rows[i][j] = value
                yield rows


def rank(rows, field):
    if not rows:
        return 0
    matrix = [list(row) for row in rows]
    n = len(matrix[0])
    check(n <= 6 and len(matrix) <= 12, "rank capacity")
    result = 0
    for column in range(n):
        pivot = next((i for i in range(result, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[result], matrix[pivot] = matrix[pivot], matrix[result]
        scale = pow(matrix[result][column], -1, field)
        matrix[result] = [x * scale % field for x in matrix[result]]
        for i in range(result + 1, len(matrix)):
            value = matrix[i][column]
            matrix[i] = [
                (x - value * y) % field
                for x, y in zip(matrix[i], matrix[result], strict=True)
            ]
        result += 1
        if result == len(matrix):
            break
    return result


def transform(rows, p, edge):
    objects = (
        list(itertools.combinations(range(4), 2)) if edge else [(i,) for i in range(4)]
    )
    permutation = [objects.index(tuple(sorted(p[i] for i in obj))) for obj in objects]
    output = []
    for row in rows:
        result = [0] * len(row)
        for i, value in enumerate(row):
            result[permutation[i]] = value
        output.append(result)
    return output


def members(rows, n):
    output = []
    for scalars in itertools.product((0, 1), repeat=len(rows)):
        vector = [
            sum(s * row[j] for s, row in zip(scalars, rows, strict=True)) % 2
            for j in range(n)
        ]
        output.append(sum(value << j for j, value in enumerate(vector)))
    check(len(set(output)) == 1 << len(rows), "basis independence")
    return sum(1 << x for x in output)


def replay(n, field):
    counts = [0] * (n + 1)
    profiles, slacks, encoded = Counter(), Counter(), []
    for rows in bases(n, field):
        dimension = len(rows)
        cuts = tuple(
            rank(rows + transform(rows, p, n == 6), field) - dimension for p in PERMS
        )
        check(
            all(0 <= c <= min(dimension, n - dimension) for c in cuts), "quotient rank"
        )
        slack = 4 * sum(cuts[:3]) - sum(cuts[3:])
        check(slack >= 0, "independent shared inequality")
        check(
            sum(a * b for a, b in zip((4, 2, 4), cuts[:3], strict=True))
            >= sum(cuts[3:]),
            "strong module inequality",
        )
        counts[dimension] += 1
        profiles[cuts] += 1
        slacks[slack] += 1
        if field == 2:
            encoded.append(members(rows, n))
    receipt = {"dimension_counts": counts, "spaces": sum(counts)}
    if field == 2:
        check(len(set(encoded)) == sum(counts), "RREF uniqueness")
        payload = b"".join(x.to_bytes((1 << n) // 8, "little") for x in sorted(encoded))
        receipt.update(
            membership_sha256=sha256(payload).hexdigest(),
            profiles=[
                {"cuts": list(p), "count": c} for p, c in sorted(profiles.items())
            ],
            slack_histogram={str(k): v for k, v in sorted(slacks.items())},
        )
    return receipt


def main():
    with (HERE / "RESULT.json").open("rb") as stream:
        raw = stream.read(131073)
    check(len(raw) <= 131072, "receipt capacity")
    expected = json.loads(raw)
    for n, key in ((4, "natural_binary"), (6, "edge_binary")):
        check(
            json.dumps(replay(n, 2), sort_keys=True)
            == json.dumps(expected[key], sort_keys=True),
            "complete independent inventory",
        )
    finite_fields = {
        3: replay(4, 3)["dimension_counts"],
        5: replay(4, 5)["dimension_counts"],
    }
    check(
        finite_fields == {3: [1, 40, 130, 40, 1], 5: [1, 156, 806, 156, 1]},
        "other-characteristic coverage",
    )
    print(
        json.dumps(
            {
                "status": "PASS_INDEPENDENT_S4_SUBSPACE_CUTS",
                "binary_spaces": 2892,
                "natural_field_counts": {
                    str(p): sum(c) for p, c in finite_fields.items()
                },
            }
        )
    )


if __name__ == "__main__":
    main()
