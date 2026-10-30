#!/usr/bin/env python3
"""Exact ternary pair law, produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


STATES = tuple(
    (a, b, c, d)
    for a, d in product((0, 2), repeat=2)
    for b, c in product(range(3), repeat=2)
)
QUOTIENT = ((21, 24, 4, 0), (6, 29, 6, 8), (2, 12, 27, 8), (0, 16, 8, 25))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def weight(matrix):
    if matrix == (0, 0, 0, 0):
        return 17
    a, b, c, d = matrix
    return 2 if (a * d - b * c) % 3 == 0 else 0


def category(matrix):
    a, b, c, d = matrix
    if b == c == 0:
        return 0
    if b * c == 0:
        return 1
    return 2 if (b * c - (1 - a) * (1 - d)) % 3 == 0 else 3


def multiply(matrix, vector):
    return tuple(sum(a * b for a, b in zip(row, vector, strict=True)) for row in matrix)


def shifted(matrix, vector, eigenvalue):
    return tuple(
        a - eigenvalue * b
        for a, b in zip(multiply(matrix, vector), vector, strict=True)
    )


def numerator(dimension):
    require(2 <= dimension <= 128, "dimension outside replay bound")
    n = dimension - 1
    value, remainder = divmod(4 * (49**n - 2 * 25**n + 19**n), 9)
    require(remainder == 0, "nonintegral closed form")
    return value


def density(dimension):
    denominator = (3**dimension - 1) * (3**dimension - 3) * 3 ** (2 * dimension - 4)
    return Fraction(numerator(dimension), denominator)


def transfer_checks():
    # Enumerate the 81 coordinate pairs independently of the rank formula.
    increments = {}
    for a, b, c, d in product(range(3), repeat=4):
        increment = (a * c % 3, a * d % 3, b * c % 3, b * d % 3)
        increments[increment] = increments.get(increment, 0) + 1
    for matrix in product(range(3), repeat=4):
        require(increments.get(matrix, 0) == weight(matrix), "factor weight")
    transfer = tuple(
        tuple(
            weight(tuple((x - y) % 3 for x, y in zip(target, source, strict=True)))
            for target in STATES
        )
        for source in STATES
    )
    for state, row in zip(STATES, transfer, strict=True):
        totals = tuple(
            sum(
                v
                for target, v in zip(STATES, row, strict=True)
                if category(target) == group
            )
            for group in range(4)
        )
        require(totals == QUOTIENT[category(state)], "inequitable quotient")
    terminal = tuple(
        weight(((1 - a) % 3, -b % 3, -c % 3, (1 - d) % 3)) for a, b, c, d in STATES
    )
    require(
        terminal == tuple(2 if category(s) == 2 else 0 for s in STATES),
        "terminal class",
    )
    killed = (0, 0, 2, 0)
    for eigenvalue in (19, 25, 49):
        killed = shifted(QUOTIENT, killed, eigenvalue)
    require(killed == (0, 0, 0, 0), "cubic annihilator")
    values = terminal
    short = (0, 0, 2, 0)
    for n in range(128):
        expected = 4 * (49**n - 2 * 25**n + 19**n) // 9
        require(values[0] == short[0] == expected, "closed form versus transfer")
        values = multiply(transfer, values)
        short = multiply(QUOTIENT, short)
    return {
        "coordinate_pairs": 81,
        "increment_matrices": 81,
        "quotient_rows": 36,
        "transfer_dimensions": 127,
        "initial_numerators": [numerator(m) for m in range(2, 8)],
    }


def inverse(matrix):
    n = len(matrix)
    require(2 <= n <= 3, "GL census dimension")
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [value * scale % 3 for value in rows[col]]
        for i in range(n):
            if i != col:
                scale = rows[i][col]
                rows[i] = [
                    (x - scale * y) % 3 for x, y in zip(rows[i], rows[col], strict=True)
                ]
    return tuple(tuple(row[n:]) for row in rows)


def literal_guards(matrix):
    # No row or column exchanges: these are the actual leading-minor guards.
    rows = [list(row) for row in matrix]
    n = len(rows)
    for k in range(n - 1):
        pivot = rows[k][k]
        if pivot == 0:
            return False
        for i in range(k + 1, n):
            scale = rows[i][k] * pivot % 3
            for j in range(k + 1, n):
                rows[i][j] = (rows[i][j] - scale * rows[k][j]) % 3
    return True


def header_census():
    report = []
    for n in (2, 3):
        count = passing = first_only = 0
        for flat in product(range(3), repeat=n * n):
            header = tuple(flat[i * n : (i + 1) * n] for i in range(n))
            inv = inverse(header)
            if inv is None:
                continue
            count += 1
            requests = [
                tuple(
                    tuple(
                        (int(i == j) - header[i][k] * inv[k][j]) % 3 for j in range(n)
                    )
                    for i in range(n)
                )
                for k in (0, 1)
            ]
            passing += all(literal_guards(request) for request in requests)
            first_only += all(request[0][0] != 0 for request in requests)
        require(Fraction(passing, count) == density(n), "literal GL density")
        report.append(
            {
                "m": n,
                "headers": count,
                "passing": passing,
                "first_guard_only": first_only,
            }
        )
    require(
        report[-1]["first_guard_only"] > report[-1]["passing"],
        "first-guard control failed",
    )
    return report


def normalized_pair_census():
    report = []
    for n in (2, 3, 4):
        rows = tuple(product(range(3), repeat=n))
        count = passing = 0
        for u in rows:
            for v in rows:
                # Solve each dual row independently, then enumerate all solutions.
                a_rows = tuple(
                    a
                    for a in rows
                    if sum(x * y for x, y in zip(a, u, strict=True)) % 3 == 1
                    and sum(x * y for x, y in zip(a, v, strict=True)) % 3 == 0
                )
                if not a_rows:
                    continue
                b_rows = tuple(
                    b
                    for b in rows
                    if sum(x * y for x, y in zip(b, u, strict=True)) % 3 == 0
                    and sum(x * y for x, y in zip(b, v, strict=True)) % 3 == 1
                )
                for a in a_rows:
                    for b in b_rows:
                        count += 1
                        sa = sb = 0
                        good = True
                        for i in range(n - 1):
                            sa = (sa + a[i] * u[i]) % 3
                            sb = (sb + b[i] * v[i]) % 3
                            good = good and sa != 1 and sb != 1
                        passing += good
        expected = (3**n - 1) * (3**n - 3) * 3 ** (2 * n - 4)
        require(count == expected, "normalized-pair domain incomplete")
        require(passing == numerator(n), "normalized-pair closed form")
        report.append({"m": n, "pairs": count, "passing": passing})
    return report


def controls():
    require(18 != weight((0, 0, 0, 0)), "zero-factor control")
    wrong = shifted(QUOTIENT, (0, 0, 2, 0), 18)
    for eigenvalue in (25, 49):
        wrong = shifted(QUOTIENT, wrong, eigenvalue)
    require(any(wrong), "wrong-eigenvalue control")
    require(numerator(2) != 4 * (49 - 2 * 25) // 9, "lost-mode control")
    for m in range(2, 129):
        single = Fraction(2 * 7 ** (m - 1), (3**m - 1) * 3 ** (m - 1))
        require(0 < density(m) < single**2, "positivity/correlation")
    return {
        "rejected_controls": [
            "zero weight 18",
            "eigenvalue 18",
            "omitted 19 mode",
            "independent marginals",
            "first guard only",
        ],
        "correlation_dimensions": 127,
    }


def main():
    result = {
        "status": "PASS_TERNARY_CORANKONE_PAIR_LAW",
        "claim_type": "scoped counting proof with finite corroboration",
        "transfer": transfer_checks(),
        "headers": header_census(),
        "normalized_pairs": normalized_pair_census(),
        "controls": controls(),
    }
    package = Path(__file__).resolve().parent
    names = (
        "README.md",
        "PROOF.md",
        "TASK.json",
        "SOURCES.json",
        "VERIFY.json",
        "verify.py",
    )
    result["sha256"] = {
        name: sha256((package / name).read_bytes()).hexdigest() for name in names
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
