#!/usr/bin/env python3
"""Exact corroboration of the binary off-diagonal pool theorem.

Produced by Nick Petalas. Apache-2.0.
No predecessor executable or external scientific input is imported.
"""

import hashlib
import json
from pathlib import Path
import sys


PACKAGE_FILES = (
    "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def bound(d: int) -> int:
    need(type(d) is int and 0 <= d <= 10, "unsupported pattern dimension")
    return (1 << d) + d - 1


def outer(x: int, y: int, n: int) -> tuple[int, ...]:
    need(0 < x < 1 << n and 0 < y < 1 << n, "invalid outer-product vectors")
    return tuple(y if x >> i & 1 else 0 for i in range(n))


def pattern(rows: tuple[int, ...]) -> int:
    n = len(rows)
    need(1 <= n <= 11, "unsupported matrix width")
    return sum((row & ~(1 << i)) << (n * i) for i, row in enumerate(rows))


def projector(rows: tuple[int, ...]) -> bool:
    """Recognize rank one and idempotence from the literal row action."""
    n = len(rows)
    need(1 <= n <= 11, "unsupported matrix width")
    need(all(type(row) is int and 0 <= row < 1 << n for row in rows), "bad row")
    pivot = next((row for row in rows if row), 0)
    if not pivot or any(row not in (0, pivot) for row in rows):
        return False
    image = sum(1 << i for i, row in enumerate(rows) if row)
    return (pivot & image).bit_count() % 2 == 1


def fibers(n: int) -> dict[int, set[tuple[int, ...]]]:
    need(n in (5, 6), "census width must be five or six")
    result: dict[int, set[tuple[int, ...]]] = {}
    for x in range(1, 1 << n):
        for y in range(1, 1 << n):
            if (x & y).bit_count() % 2:
                rows = outer(x, y, n)
                code = pattern(rows)
                if code:
                    result.setdefault(code, set()).add(rows)
    return result


def diagonal_oracle(code: int, n: int) -> set[tuple[int, ...]]:
    """Try every diagonal completion, independently of the outer-product list."""
    need(n in (5, 6), "unsupported exhaustive oracle width")
    mask = (1 << n) - 1
    off = tuple(code >> (n * i) & mask for i in range(n))
    need(all(row >> i & 1 == 0 for i, row in enumerate(off)), "nonzero diagonal")
    result = set()
    for diagonal in range(1 << n):
        rows = tuple(row | ((diagonal >> i & 1) << i) for i, row in enumerate(off))
        if projector(rows):
            result.add(rows)
    return result


def check_fibers(n: int) -> tuple[dict[int, set[tuple[int, ...]]], dict[str, int]]:
    data = fibers(n)
    matrices = sum(len(value) for value in data.values())
    for code, value in data.items():
        need(value == diagonal_oracle(code, n), "diagonal oracle disagrees")
        expected = 2 if code.bit_count() == 1 else 1
        need(len(value) == expected, "nonzero-pattern fiber theorem fails")
        if expected == 2:
            position = code.bit_length() - 1
            i, j = divmod(position, n)
            a = outer(1 << i, (1 << i) | (1 << j), n)
            b = outer((1 << i) | (1 << j), 1 << j, n)
            need(value == {a, b}, "wrong single-edge lifts")
    zeros = diagonal_oracle(0, n)
    need(len(zeros) == n, "zero fiber must contain every coordinate projector")
    return data, {
        "width": n,
        "noncoordinate_projectors": matrices,
        "nonzero_patterns": len(data),
        "diagonal_completions": (len(data) + 1) * (1 << n),
    }


def check_planes(data: dict[int, set[tuple[int, ...]]]) -> dict[str, int]:
    codes = sorted(data)
    need(len(codes) <= 500, "plane enumeration capacity exceeded")
    pairs = 0
    maximum = 0
    for index, p in enumerate(codes):
        for q in codes[index + 1:]:
            vectors = (p, q, p ^ q)
            actual = sum(len(data.get(code, ())) for code in vectors)
            realized = sum(code in data for code in vectors)
            edges = sum(code.bit_count() == 1 for code in vectors)
            need(actual == realized + edges, "exact pool identity fails")
            need(actual <= bound(2), "two-dimensional pool exceeds bound")
            maximum = max(maximum, actual)
            pairs += 1
    need(maximum == bound(2), "sharp two-dimensional witness absent")
    return {"spanning_pairs": pairs, "maximum_pool_size": maximum}


def star(d: int, n: int) -> tuple[tuple[int, ...], ...]:
    need(1 <= d <= 10 and d + 1 <= n <= 11, "invalid star shape")
    primary = tuple(outer(1, 1 | (subset << 1), n) for subset in range(1, 1 << d))
    secondary = tuple(outer(1 | (1 << j), 1 << j, n) for j in range(1, d + 1))
    return primary + secondary


def check_stars() -> dict[str, int]:
    total = 0
    shapes = 0
    for d in range(1, 11):
        for n in range(d + 1, 12):
            pool = star(d, n)
            need(len(set(pool)) == len(pool) == bound(d), "star cardinality fails")
            grouped: dict[int, int] = {}
            for rows in pool:
                need(projector(rows), "star has a nonprojector")
                code = pattern(rows)
                need(code != 0, "coordinate projector entered star")
                grouped[code] = grouped.get(code, 0) + 1
            need(len(grouped) == (1 << d) - 1, "star omits a nonzero pattern")
            need(sum(code.bit_count() == 1 for code in grouped) == d, "bad star edges")
            for code, size in grouped.items():
                need(size == (2 if code.bit_count() == 1 else 1), "bad star fiber")
            total += len(pool)
            shapes += 1
    return {"shapes": shapes, "literal_projectors": total}


def check_controls() -> dict[str, int]:
    rejected = 0
    for invalid in (-1, 11, True, 1.0, "2"):
        try:
            bound(invalid)
        except ValueError:
            rejected += 1
    need(rejected == 5, "dimension validation failed")
    need(bound(0) == 0, "zero-dimensional noncoordinate pool must be empty")
    need(not projector((0, 0)), "zero matrix accepted")
    need(not projector((1, 2)), "rank-two matrix accepted")
    need(not projector((3, 3)), "rank-one nilpotent accepted")
    need(projector((1, 0)) and pattern((1, 0)) == 0, "coordinate control fails")
    # Over F7 two distinct cyclic-pattern projectors have the same off-diagonal.
    odd = (((3, 1), (1, 5)), ((5, 1), (1, 3)))
    for rows in odd:
        square = tuple(tuple(sum(rows[i][k] * rows[k][j] for k in range(2)) % 7
                             for j in range(2)) for i in range(2))
        need(square == rows and (rows[0][0] * rows[1][1] - 1) % 7 == 0,
             "odd-characteristic scope control fails")
    need(odd[0] != odd[1], "odd-field example collapsed")
    return {"invalid_dimensions_rejected": rejected, "semantic_groups": 7}


def main() -> None:
    need(len(sys.argv) == 1, "this fixed-domain verifier takes no arguments")
    first, first_counts = check_fibers(5)
    _, second_counts = check_fibers(6)
    counts = {
        "fibers": [first_counts, second_counts],
        "planes": check_planes(first),
        "attaining_stars": check_stars(),
        "controls": check_controls(),
    }
    root = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
              for name in PACKAGE_FILES}
    print("PASS_PATTERN_POOL_CARDINALITY")
    print(json.dumps({"counts": counts, "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
